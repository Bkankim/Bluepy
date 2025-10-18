"""데이터베이스 모델

SQLAlchemy ORM 모델을 정의합니다.

주요 모델:
- Server: 서버 정보
- ScanHistory: 스캔 이력
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Server(Base):
    """서버 모델

    점검 대상 서버 정보를 저장합니다.

    Attributes:
        id: Primary Key
        name: 서버 이름
        host: 호스트 주소 (IP 또는 도메인)
        port: SSH 포트
        username: SSH 사용자명
        auth_method: 인증 방법 (password, key)
        key_path: SSH 키 파일 경로 (선택)
        platform: 플랫폼 (linux, macos, windows)
        description: 설명 (선택)
        created_at: 생성 시각
        updated_at: 수정 시각
    """

    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=22, nullable=False)
    username = Column(String(100), nullable=False)
    auth_method = Column(String(20), default="password", nullable=False)  # password or key
    key_path = Column(String(500), nullable=True)
    platform = Column(String(20), default="linux", nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"<Server(id={self.id}, name='{self.name}', host='{self.host}')>"


class ScanHistory(Base):
    """스캔 이력 모델

    과거 스캔 결과를 저장합니다.

    Attributes:
        id: Primary Key
        server_id: 서버 ID (외래 키)
        scan_time: 스캔 수행 시각
        total: 전체 점검 항목 수
        passed: 양호 항목 수
        failed: 취약 항목 수
        manual: 수동 점검 필요 항목 수
        score: 점수 (0~100)
        result_data: 상세 결과 데이터 (JSON)
        created_at: 생성 시각
    """

    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, nullable=False)  # TODO: ForeignKey 추가
    scan_time = Column(DateTime, default=datetime.now, nullable=False)
    total = Column(Integer, default=0, nullable=False)
    passed = Column(Integer, default=0, nullable=False)
    failed = Column(Integer, default=0, nullable=False)
    manual = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)  # 0~100
    result_data = Column(Text, nullable=True)  # JSON 형식
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def __repr__(self) -> str:
        return f"<ScanHistory(id={self.id}, server_id={self.server_id}, score={self.score})>"


# 데이터베이스 엔진 및 세션 생성 함수
def create_db_engine(db_path: str = "data/databases/bluepy.db"):
    """데이터베이스 엔진 생성

    Args:
        db_path: 데이터베이스 파일 경로

    Returns:
        SQLAlchemy Engine
    """
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return engine


def create_db_session(engine):
    """데이터베이스 세션 생성

    Args:
        engine: SQLAlchemy Engine

    Returns:
        SQLAlchemy Session
    """
    Session = sessionmaker(bind=engine)
    return Session()


def init_database(db_path: str = "data/databases/bluepy.db"):
    """데이터베이스 초기화

    테이블을 생성합니다.

    Args:
        db_path: 데이터베이스 파일 경로
    """
    engine = create_db_engine(db_path)
    Base.metadata.create_all(engine)
    return engine


__all__ = [
    "Base",
    "Server",
    "ScanHistory",
    "create_db_engine",
    "create_db_session",
    "init_database",
]
