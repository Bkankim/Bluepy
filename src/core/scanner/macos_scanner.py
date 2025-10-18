"""macOS 스캐너

macOS 서버에 SSH로 연결하여 보안 점검을 수행합니다.
UnixScanner를 상속하여 macOS 전용 설정을 제공합니다.
"""

from typing import Optional

from .unix_scanner import UnixScanner


class MacOSScanner(UnixScanner):
    """macOS 서버 스캐너

    UnixScanner를 상속하여 macOS 서버 점검을 수행합니다.
    모든 공통 로직은 UnixScanner에 구현되어 있습니다.

    사용 예시:
        >>> scanner = MacOSScanner(
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
        port: int = 22,
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
        # UnixScanner 초기화 (platform="macos" 고정)
        super().__init__(
            server_id=server_id,
            platform="macos",
            host=host,
            username=username,
            password=password,
            key_filename=key_filename,
            port=port,
        )


__all__ = [
    "MacOSScanner",
]
