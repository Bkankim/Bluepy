"""서버 Repository

Server 모델에 대한 CRUD 기능을 제공합니다.

주요 기능:
- Create: 서버 추가
- Read: 서버 조회
- Update: 서버 수정
- Delete: 서버 삭제
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Server


class ServerRepository:
    """서버 Repository 클래스

    Server 모델에 대한 데이터베이스 작업을 제공합니다.
    """

    def __init__(self, session: Session):
        """초기화

        Args:
            session: SQLAlchemy Session
        """
        self.session = session

    def create(
        self,
        name: str,
        host: str,
        username: str,
        port: int = 22,
        auth_method: str = "password",
        key_path: Optional[str] = None,
        platform: str = "linux",
        description: Optional[str] = None
    ) -> Server:
        """서버 추가

        Args:
            name: 서버 이름
            host: 호스트 주소
            username: SSH 사용자명
            port: SSH 포트
            auth_method: 인증 방법 (password, key)
            key_path: SSH 키 파일 경로
            platform: 플랫폼 (linux, macos, windows)
            description: 설명

        Returns:
            생성된 Server 객체

        Raises:
            ValueError: 중복된 이름
        """
        # 중복 확인
        existing = self.get_by_name(name)
        if existing:
            raise ValueError(f"서버 이름이 이미 존재합니다: {name}")

        server = Server(
            name=name,
            host=host,
            port=port,
            username=username,
            auth_method=auth_method,
            key_path=key_path,
            platform=platform,
            description=description
        )

        self.session.add(server)
        self.session.commit()
        self.session.refresh(server)

        return server

    def get_by_id(self, server_id: int) -> Optional[Server]:
        """ID로 서버 조회

        Args:
            server_id: 서버 ID

        Returns:
            Server 객체 또는 None
        """
        return self.session.query(Server).filter(Server.id == server_id).first()

    def get_by_name(self, name: str) -> Optional[Server]:
        """이름으로 서버 조회

        Args:
            name: 서버 이름

        Returns:
            Server 객체 또는 None
        """
        return self.session.query(Server).filter(Server.name == name).first()

    def get_all(self) -> List[Server]:
        """전체 서버 목록 조회

        Returns:
            Server 객체 리스트
        """
        return self.session.query(Server).order_by(Server.created_at.desc()).all()

    def update(
        self,
        server_id: int,
        **kwargs
    ) -> Optional[Server]:
        """서버 정보 수정

        Args:
            server_id: 서버 ID
            **kwargs: 수정할 필드들

        Returns:
            수정된 Server 객체 또는 None

        Raises:
            ValueError: 서버를 찾을 수 없음
        """
        server = self.get_by_id(server_id)
        if not server:
            raise ValueError(f"서버를 찾을 수 없습니다: ID {server_id}")

        # 허용된 필드만 업데이트
        allowed_fields = [
            'name', 'host', 'port', 'username',
            'auth_method', 'key_path', 'platform', 'description'
        ]

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(server, key, value)

        self.session.commit()
        self.session.refresh(server)

        return server

    def delete(self, server_id: int) -> bool:
        """서버 삭제

        Args:
            server_id: 서버 ID

        Returns:
            삭제 성공 여부
        """
        server = self.get_by_id(server_id)
        if not server:
            return False

        self.session.delete(server)
        self.session.commit()

        return True

    def count(self) -> int:
        """전체 서버 수 반환

        Returns:
            서버 수
        """
        return self.session.query(Server).count()


__all__ = [
    "ServerRepository",
]