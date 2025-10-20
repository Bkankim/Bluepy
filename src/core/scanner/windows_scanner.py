"""Windows 스캐너

Windows 서버에 WinRM으로 연결하여 보안 점검을 수행합니다.
BaseScanner를 상속하여 Windows 전용 스캔 로직을 구현합니다.
"""

import importlib
import logging
from typing import List

from ...infrastructure.network.winrm_client import (
    WinRMClient,
    WinRMConnectionError,
)
from ..domain.models import CheckResult, RuleMetadata, Status
from .base_scanner import BaseScanner
from .rule_loader import load_rules

logger = logging.getLogger(__name__)


class WindowsScanner(BaseScanner):
    """Windows 서버 스캐너

    WinRM을 통해 Windows 서버에 연결하고 PowerShell 명령어를 실행하여
    보안 점검을 수행합니다.

    사용 예시:
        >>> scanner = WindowsScanner(
        ...     server_id="server-001",
        ...     host="192.168.1.100",
        ...     username="Administrator",
        ...     password="password"
        ... )
        >>> await scanner.connect()
        >>> await scanner.load_rules("config/rules")
        >>> result = await scanner.scan_all()
        >>> print(f"점수: {result.score}/100")
        >>> await scanner.disconnect()
    """

    def __init__(
        self,
        server_id: str,
        host: str,
        username: str,
        password: str,
        port: int = 5986,
        transport: str = "ntlm",
        use_ssl: bool = True,
    ):
        """초기화

        Args:
            server_id: 서버 식별자
            host: 서버 호스트명 또는 IP
            username: Windows 사용자명
            password: Windows 패스워드
            port: WinRM 포트 (기본: 5986 HTTPS)
            transport: 인증 방식 (ntlm, kerberos, basic, credssp)
            use_ssl: SSL/TLS 사용 여부 (기본: True)
        """
        # BaseScanner 초기화 (platform="windows" 고정)
        super().__init__(server_id=server_id, platform="windows")

        # WinRM 클라이언트 생성
        self._client = WinRMClient(
            host=host,
            username=username,
            password=password,
            port=port,
            transport=transport,
            use_ssl=use_ssl,
        )

        logger.debug(f"WindowsScanner 초기화: {server_id} ({host})")

    async def connect(self) -> None:
        """WinRM 서버에 연결

        Raises:
            WinRMConnectionError: 연결 실패 시
        """
        if self._connected:
            logger.warning(f"이미 연결되어 있습니다: {self.server_id}")
            return

        try:
            await self._client.connect()
            self._connected = True
            logger.info(f"WindowsScanner 연결 성공: {self.server_id}")

        except WinRMConnectionError as e:
            logger.error(f"WindowsScanner 연결 실패: {self.server_id}, 오류: {e}")
            raise

    async def disconnect(self) -> None:
        """WinRM 연결 해제"""
        if not self._connected:
            logger.debug(f"연결되어 있지 않습니다: {self.server_id}")
            return

        try:
            await self._client.disconnect()
            self._connected = False
            logger.info(f"WindowsScanner 연결 해제: {self.server_id}")

        except Exception as e:
            logger.error(f"연결 해제 중 오류: {e}")

    async def execute_command(self, command: str) -> str:
        """PowerShell 명령어 실행

        Args:
            command: 실행할 PowerShell 명령어

        Returns:
            명령어 출력 결과 (stdout)

        Raises:
            RuntimeError: 연결되지 않았거나 명령어 실행 실패
        """
        if not self._connected:
            raise RuntimeError("서버에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            return await self._client.execute_powershell(command)

        except Exception as e:
            raise RuntimeError(f"명령어 실행 실패: {e}")

    async def load_rules(self, rules_dir: str) -> None:
        """Windows 규칙 파일 로드

        Args:
            rules_dir: 규칙 파일 디렉토리 경로 (예: config/rules)

        Raises:
            FileNotFoundError: 규칙 파일이 없는 경우
            ValueError: 규칙 파일 파싱 실패
        """
        try:
            self._rules = load_rules(rules_dir, platform="windows")
            logger.info(f"Windows 규칙 {len(self._rules)}개 로드 완료")
        except Exception as e:
            raise ValueError(f"규칙 로드 실패: {e}")

    async def scan_one(self, rule: RuleMetadata) -> CheckResult:
        """단일 규칙 점검

        Args:
            rule: 점검 규칙 (RuleMetadata)

        Returns:
            점검 결과 (CheckResult)

        Raises:
            RuntimeError: 명령어 실행 실패 시
        """
        if not self._connected:
            raise RuntimeError("서버에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            # 1. 명령어 실행
            command_outputs: List[str] = []

            for command in rule.commands:
                # 수동 점검 명령어는 skip
                if not command.strip() or command.strip().startswith("echo 'No commands"):
                    logger.debug(f"수동 점검 규칙: {rule.id}, 명령어 실행 skip")
                    command_outputs.append("")
                    continue

                try:
                    output = await self.execute_command(command)
                    command_outputs.append(output)
                    logger.debug(f"{rule.id}: 명령어 실행 완료, {len(output)} 바이트")
                except Exception as e:
                    logger.error(f"{rule.id}: 명령어 실행 실패: {command[:50]}..., {e}")
                    command_outputs.append("")  # 빈 출력

            # 2. Validator 함수 동적 import 및 호출
            validator_result = self._call_validator(rule, command_outputs)

            logger.info(
                f"{rule.id} 점검 완료: {validator_result.status.value}, "
                f"{validator_result.message[:50]}..."
            )

            return validator_result

        except Exception as e:
            logger.error(f"{rule.id} 점검 중 오류: {e}")
            return CheckResult(status=Status.MANUAL, message=f"점검 중 오류 발생: {str(e)[:200]}")

    def _call_validator(self, rule: RuleMetadata, outputs: List[str]) -> CheckResult:
        """Validator 함수 동적 호출

        Args:
            rule: 점검 규칙
            outputs: 명령어 출력 리스트

        Returns:
            CheckResult

        Raises:
            RuntimeError: validator 함수 import 또는 호출 실패
        """
        try:
            # validator 경로 파싱: validators.windows.check_w01
            parts = rule.validator.split(".")
            if len(parts) < 3:
                raise ValueError(f"올바르지 않은 validator 경로: {rule.validator}")

            # 모듈 경로: src.core.analyzer.validators.windows
            module_path = f"src.core.analyzer.{'.'.join(parts[:-1])}"
            function_name = parts[-1]  # check_w01

            # 동적 import
            try:
                module = importlib.import_module(module_path)
            except ModuleNotFoundError:
                raise RuntimeError(f"Validator 모듈을 찾을 수 없습니다: {module_path}")

            # 함수 가져오기
            if not hasattr(module, function_name):
                raise RuntimeError(f"Validator 함수를 찾을 수 없습니다: {function_name}")

            validator_func = getattr(module, function_name)

            # 함수 호출
            result = validator_func(outputs)

            # CheckResult 타입 확인
            if not isinstance(result, CheckResult):
                raise RuntimeError(f"Validator가 CheckResult를 반환하지 않았습니다: {type(result)}")

            return result

        except Exception as e:
            logger.error(f"Validator 호출 실패 ({rule.id}): {e}")
            raise RuntimeError(f"Validator 호출 실패: {e}")


__all__ = [
    "WindowsScanner",
]
