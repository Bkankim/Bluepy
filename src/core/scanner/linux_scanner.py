"""Linux 스캐너

Linux 서버에 SSH로 연결하여 보안 점검을 수행합니다.

주요 기능:
- SSH 연결 및 명령어 실행
- YAML 규칙 파일 로드
- Validator 함수 동적 호출
- 점검 결과 수집
"""

import importlib
import logging
from typing import List, Optional

from .base_scanner import BaseScanner
from .rule_loader import load_rules
from ..domain.models import CheckResult, RuleMetadata, Status
from ...infrastructure.network.ssh_client import SSHClient, SSHClientError

logger = logging.getLogger(__name__)


class LinuxScanner(BaseScanner):
    """Linux 서버 스캐너

    SSH를 사용하여 Linux 서버에 연결하고 보안 점검을 수행합니다.

    사용 예시:
        >>> scanner = LinuxScanner(
        ...     server_id="server-001",
        ...     host="192.168.1.100",
        ...     username="admin",
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
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22
    ):
        """초기화

        Args:
            server_id: 서버 식별자
            host: 서버 호스트명 또는 IP
            username: SSH 사용자명
            password: SSH 패스워드 (선택)
            key_filename: SSH 키 파일 경로 (선택)
            port: SSH 포트 (기본: 22)
        """
        super().__init__(server_id=server_id, platform="linux")

        # SSH 클라이언트 초기화
        self._ssh_client = SSHClient(
            host=host,
            username=username,
            password=password,
            key_filename=key_filename,
            port=port
        )

    async def connect(self) -> None:
        """서버에 연결

        SSH 연결을 수행합니다.

        Raises:
            ConnectionError: 연결 실패 시
        """
        try:
            await self._ssh_client.connect()
            self._connected = True
            logger.info(f"Linux 서버 연결 성공: {self.server_id}")
        except SSHClientError as e:
            raise ConnectionError(f"서버 연결 실패: {e}")

    async def disconnect(self) -> None:
        """서버 연결 해제"""
        await self._ssh_client.disconnect()
        self._connected = False
        logger.info(f"Linux 서버 연결 해제: {self.server_id}")

    async def execute_command(self, command: str) -> str:
        """명령어 실행

        Args:
            command: 실행할 bash 명령어

        Returns:
            명령어 출력 (stdout)

        Raises:
            RuntimeError: 명령어 실행 실패 시
        """
        if not self._connected:
            raise RuntimeError("서버에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            result = await self._ssh_client.execute(command)
            return result
        except SSHClientError as e:
            raise RuntimeError(f"명령어 실행 실패: {command[:50]}..., 오류: {e}")

    async def load_rules(self, rules_dir: str) -> None:
        """규칙 파일 로드

        Args:
            rules_dir: 규칙 파일 디렉토리 경로 (예: config/rules)

        Raises:
            FileNotFoundError: 규칙 파일이 없는 경우
            ValueError: 규칙 파일 파싱 실패
        """
        try:
            self._rules = load_rules(rules_dir, platform="linux")
            logger.info(f"Linux 규칙 {len(self._rules)}개 로드 완료")
        except Exception as e:
            raise ValueError(f"규칙 로드 실패: {e}")

    async def scan_one(self, rule: RuleMetadata) -> CheckResult:
        """단일 규칙 점검

        Args:
            rule: 점검 규칙

        Returns:
            점검 결과

        Raises:
            RuntimeError: 명령어 실행 실패 또는 validator 호출 실패
        """
        if not self._connected:
            raise RuntimeError("서버에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            # 1. 명령어 실행
            command_outputs: List[str] = []

            for command in rule.commands:
                # 수동 점검 명령어는 skip (명령어가 빈 문자열이거나 "echo" 같은 경우)
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
            return CheckResult(
                status=Status.MANUAL,
                message=f"점검 중 오류 발생: {str(e)[:200]}"
            )

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
            # validator 경로 파싱: validators.linux.check_u01
            parts = rule.validator.split('.')
            if len(parts) < 3:
                raise ValueError(f"올바르지 않은 validator 경로: {rule.validator}")

            # 모듈 경로: src.core.analyzer.validators.linux
            module_path = f"src.core.analyzer.{'.'.join(parts[:-1])}"
            function_name = parts[-1]  # check_u01

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
                raise RuntimeError(
                    f"Validator가 CheckResult를 반환하지 않았습니다: {type(result)}"
                )

            return result

        except Exception as e:
            logger.error(f"Validator 호출 실패 ({rule.id}): {e}")
            raise RuntimeError(f"Validator 호출 실패: {e}")


__all__ = [
    "LinuxScanner",
]