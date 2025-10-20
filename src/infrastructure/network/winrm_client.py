"""WinRM 클라이언트

pywinrm 기반 비동기 WinRM 클라이언트 구현.
Windows 서버에 연결하여 PowerShell 명령어를 실행합니다.

주요 기능:
- WinRM 연결 (HTTP/HTTPS)
- PowerShell 명령어 실행
- 레지스트리 조회
- 서비스 상태 확인
- 에러 처리 및 로깅
"""

import asyncio
import logging
from typing import Optional

from winrm.exceptions import WinRMError, WinRMTransportError
from winrm.protocol import Protocol

logger = logging.getLogger(__name__)


class WinRMConnectionError(Exception):
    """WinRM 연결 예외"""

    pass


class WinRMCommandError(Exception):
    """WinRM 명령어 실행 예외"""

    pass


class WinRMTimeoutError(Exception):
    """WinRM 타임아웃 예외"""

    pass


class WinRMClient:
    """pywinrm 기반 WinRM 클라이언트

    Windows 서버에 WinRM으로 연결하여 PowerShell 명령어를 실행합니다.
    asyncio를 사용하여 비동기 처리를 지원합니다.

    사용 예시:
        >>> client = WinRMClient(
        ...     host="192.168.1.100",
        ...     username="Administrator",
        ...     password="password"
        ... )
        >>> await client.connect()
        >>> result = await client.execute_powershell("Get-Service")
        >>> print(result)
        >>> await client.disconnect()
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 5986,
        transport: str = "ntlm",
        use_ssl: bool = True,
        timeout: int = 30,
    ):
        """초기화

        Args:
            host: 서버 호스트명 또는 IP
            username: Windows 사용자명 (도메인\사용자 또는 사용자@도메인)
            password: Windows 패스워드
            port: WinRM 포트 (기본: 5986 HTTPS, 5985 HTTP)
            transport: 인증 방식 (ntlm, kerberos, basic, credssp)
            use_ssl: SSL/TLS 사용 여부 (기본: True)
            timeout: 연결 타임아웃 (초, 기본: 30)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.transport = transport
        self.use_ssl = use_ssl
        self.timeout = timeout

        self._protocol: Optional[Protocol] = None
        self._connected = False

        # WinRM 엔드포인트 URL 생성
        protocol_scheme = "https" if use_ssl else "http"
        self._endpoint = f"{protocol_scheme}://{host}:{port}/wsman"

    async def connect(self) -> bool:
        """WinRM 서버에 연결

        Returns:
            연결 성공 여부

        Raises:
            WinRMConnectionError: 연결 실패 시
        """
        if self._connected:
            logger.warning(f"이미 연결되어 있습니다: {self.host}")
            return True

        try:
            logger.info(f"WinRM 연결 시도: {self.username}@{self.host}:{self.port}")

            # Protocol 객체 생성 (동기 작업을 비동기로 래핑)
            await asyncio.get_event_loop().run_in_executor(None, self._create_protocol)

            # 연결 테스트 (간단한 명령어 실행)
            test_result = await self.execute_powershell("echo 'test'", timeout=10)

            if "test" not in test_result:
                raise WinRMConnectionError("연결 테스트 실패: 응답 없음")

            self._connected = True
            logger.info(f"WinRM 연결 성공: {self.username}@{self.host}")
            return True

        except WinRMTransportError as e:
            raise WinRMConnectionError(f"WinRM 전송 오류: {self.host}, 오류: {e}")
        except WinRMError as e:
            raise WinRMConnectionError(f"WinRM 연결 실패: {self.host}, 오류: {e}")
        except Exception as e:
            raise WinRMConnectionError(f"예상치 못한 오류: {e}")

    def _create_protocol(self) -> None:
        """Protocol 객체 생성 (동기 메서드)

        pywinrm은 동기 라이브러리이므로 별도 메서드로 분리.
        run_in_executor로 비동기 실행.
        """
        self._protocol = Protocol(
            endpoint=self._endpoint,
            transport=self.transport,
            username=self.username,
            password=self.password,
            server_cert_validation="ignore" if self.use_ssl else "validate",
            read_timeout_sec=self.timeout,
            operation_timeout_sec=self.timeout,
        )

    async def disconnect(self) -> None:
        """WinRM 연결 해제

        pywinrm은 명시적인 disconnect가 없으므로
        객체 참조만 해제합니다.
        """
        if not self._connected:
            logger.debug(f"연결되어 있지 않습니다: {self.host}")
            return

        try:
            self._protocol = None
            self._connected = False
            logger.info(f"WinRM 연결 해제: {self.username}@{self.host}")
        except Exception as e:
            logger.error(f"연결 해제 중 오류: {e}")

    async def execute_powershell(self, script: str, timeout: int = 60) -> str:
        """PowerShell 스크립트 실행

        Args:
            script: 실행할 PowerShell 스크립트
            timeout: 명령어 실행 타임아웃 (초, 기본: 60)

        Returns:
            명령어 출력 (stdout)

        Raises:
            WinRMConnectionError: 연결되지 않은 경우
            WinRMCommandError: 명령어 실행 실패
            WinRMTimeoutError: 타임아웃 발생
        """
        if not self._connected or not self._protocol:
            raise WinRMConnectionError("WinRM에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            logger.debug(f"PowerShell 실행: {script[:100]}...")

            # PowerShell 명령어 실행 (동기 -> 비동기 래핑)
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._protocol.run_ps(script),
                ),
                timeout=timeout,
            )

            # 결과 파싱
            stdout = result.std_out.decode("utf-8", errors="ignore") if result.std_out else ""
            stderr = result.std_err.decode("utf-8", errors="ignore") if result.std_err else ""
            exit_code = result.status_code

            if exit_code != 0:
                logger.warning(
                    f"PowerShell 실행 실패 (exit: {exit_code}): {script[:50]}...\n"
                    f"stderr: {stderr[:200]}"
                )
                # 일부 점검 명령어는 오류 코드를 반환할 수 있으므로
                # 예외를 발생시키지 않고 결과를 반환
                # (validator가 결과를 판단)

            logger.debug(f"PowerShell 실행 완료 (exit: {exit_code}): {len(stdout)} 바이트 출력")
            return stdout

        except asyncio.TimeoutError:
            raise WinRMTimeoutError(f"PowerShell 실행 타임아웃: {script[:100]}...")
        except WinRMError as e:
            raise WinRMCommandError(f"PowerShell 실행 실패: {script[:100]}..., 오류: {e}")
        except Exception as e:
            raise WinRMCommandError(f"예상치 못한 오류: {e}")

    async def get_registry_value(self, path: str, name: str) -> str:
        r"""레지스트리 값 조회

        Args:
            path: 레지스트리 경로 (예: HKLM:\Software\Microsoft)
            name: 레지스트리 값 이름

        Returns:
            레지스트리 값 (문자열)

        Raises:
            WinRMCommandError: 레지스트리 조회 실패
        """
        if not self._connected:
            raise WinRMConnectionError("WinRM에 연결되지 않았습니다.")

        try:
            # PowerShell Get-ItemProperty 사용
            script = f"""
                $value = Get-ItemProperty -Path '{path}' -Name '{name}' -ErrorAction SilentlyContinue
                if ($value) {{
                    $value.{name}
                }} else {{
                    Write-Output ""
                }}
            """

            result = await self.execute_powershell(script)
            return result.strip()

        except Exception as e:
            raise WinRMCommandError(f"레지스트리 조회 실패: {path}\\{name}, 오류: {e}")

    async def check_service(self, name: str) -> bool:
        """서비스 상태 확인

        Args:
            name: 서비스 이름

        Returns:
            서비스 실행 중 여부 (Running = True)

        Raises:
            WinRMCommandError: 서비스 조회 실패
        """
        if not self._connected:
            raise WinRMConnectionError("WinRM에 연결되지 않았습니다.")

        try:
            # PowerShell Get-Service 사용
            script = f"""
                $service = Get-Service -Name '{name}' -ErrorAction SilentlyContinue
                if ($service) {{
                    $service.Status
                }} else {{
                    Write-Output "NotFound"
                }}
            """

            result = await self.execute_powershell(script)
            status = result.strip()

            logger.debug(f"서비스 상태 조회: {name} = {status}")
            return status == "Running"

        except Exception as e:
            raise WinRMCommandError(f"서비스 조회 실패: {name}, 오류: {e}")

    def is_connected(self) -> bool:
        """연결 상태 확인

        Returns:
            연결 여부
        """
        return self._connected

    async def __aenter__(self):
        """비동기 context manager 진입"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 context manager 종료"""
        await self.disconnect()


__all__ = [
    "WinRMConnectionError",
    "WinRMCommandError",
    "WinRMTimeoutError",
    "WinRMClient",
]
