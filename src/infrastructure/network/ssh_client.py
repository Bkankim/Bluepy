"""SSH 클라이언트

AsyncSSH 기반 비동기 SSH 클라이언트 구현.
Linux 및 macOS 서버에 연결하여 명령어를 실행합니다.

주요 기능:
- 비동기 SSH 연결
- 명령어 실행 및 결과 수집
- 에러 처리
- 연결 풀 관리 (향후 확장)
"""

import logging
from typing import Optional

import asyncssh

logger = logging.getLogger(__name__)


class SSHClientError(Exception):
    """SSH 클라이언트 예외"""
    pass


class SSHClient:
    """AsyncSSH 기반 SSH 클라이언트

    사용 예시:
        >>> client = SSHClient(
        ...     host="192.168.1.100",
        ...     username="admin",
        ...     password="password"
        ... )
        >>> await client.connect()
        >>> result = await client.execute("ls -la /etc")
        >>> print(result)
        >>> await client.disconnect()
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        timeout: int = 30
    ):
        """초기화

        Args:
            host: 서버 호스트명 또는 IP
            username: SSH 사용자명
            password: SSH 패스워드 (선택)
            key_filename: SSH 키 파일 경로 (선택)
            port: SSH 포트 (기본: 22)
            timeout: 연결 타임아웃 (초, 기본: 30)
        """
        self.host = host
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout

        self._conn: Optional[asyncssh.SSHClientConnection] = None
        self._connected = False

    async def connect(self) -> None:
        """SSH 서버에 연결

        Raises:
            SSHClientError: 연결 실패 시
        """
        if self._connected:
            logger.warning(f"이미 연결되어 있습니다: {self.host}")
            return

        try:
            logger.info(f"SSH 연결 시도: {self.username}@{self.host}:{self.port}")

            # AsyncSSH 연결 옵션
            connect_kwargs = {
                'host': self.host,
                'port': self.port,
                'username': self.username,
                'connect_timeout': self.timeout,
                'known_hosts': None,  # 보안: 프로덕션에서는 known_hosts 사용 권장
            }

            # 인증 방법 선택
            if self.key_filename:
                connect_kwargs['client_keys'] = [self.key_filename]
                logger.debug(f"SSH 키 사용: {self.key_filename}")
            elif self.password:
                connect_kwargs['password'] = self.password
                logger.debug("패스워드 인증 사용")
            else:
                raise SSHClientError("패스워드 또는 SSH 키가 필요합니다")

            self._conn = await asyncssh.connect(**connect_kwargs)
            self._connected = True

            logger.info(f"SSH 연결 성공: {self.username}@{self.host}")

        except asyncssh.Error as e:
            raise SSHClientError(f"SSH 연결 실패: {self.host}, 오류: {e}")
        except OSError as e:
            raise SSHClientError(f"네트워크 오류: {self.host}, 오류: {e}")
        except Exception as e:
            raise SSHClientError(f"예상치 못한 오류: {e}")

    async def disconnect(self) -> None:
        """SSH 연결 해제"""
        if not self._connected or not self._conn:
            logger.debug(f"연결되어 있지 않습니다: {self.host}")
            return

        try:
            self._conn.close()
            await self._conn.wait_closed()
            self._connected = False
            logger.info(f"SSH 연결 해제: {self.username}@{self.host}")
        except Exception as e:
            logger.error(f"연결 해제 중 오류: {e}")

    async def execute(self, command: str, timeout: int = 60) -> str:
        """명령어 실행

        Args:
            command: 실행할 bash 명령어
            timeout: 명령어 실행 타임아웃 (초, 기본: 60)

        Returns:
            명령어 출력 (stdout)

        Raises:
            SSHClientError: 연결되지 않았거나 명령어 실행 실패
        """
        if not self._connected or not self._conn:
            raise SSHClientError("SSH에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        try:
            logger.debug(f"명령어 실행: {command[:100]}...")

            # AsyncSSH run() 메서드 사용
            result = await self._conn.run(command, timeout=timeout, check=False)

            # stdout 반환
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            exit_status = result.exit_status

            if exit_status != 0:
                logger.warning(
                    f"명령어 실행 실패 (exit: {exit_status}): {command[:50]}...\n"
                    f"stderr: {stderr[:200]}"
                )
                # 일부 점검 명령어는 오류 코드를 반환할 수 있으므로
                # 예외를 발생시키지 않고 결과를 반환
                # (validator가 결과를 판단)

            logger.debug(f"명령어 실행 완료 (exit: {exit_status}): {len(stdout)} 바이트 출력")
            return stdout

        except asyncssh.TimeoutError:
            raise SSHClientError(f"명령어 실행 타임아웃: {command[:100]}...")
        except asyncssh.Error as e:
            raise SSHClientError(f"명령어 실행 실패: {command[:100]}..., 오류: {e}")
        except Exception as e:
            raise SSHClientError(f"예상치 못한 오류: {e}")

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected

    async def __aenter__(self):
        """비동기 context manager 진입"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 context manager 종료"""
        await self.disconnect()


__all__ = [
    "SSHClientError",
    "SSHClient",
]