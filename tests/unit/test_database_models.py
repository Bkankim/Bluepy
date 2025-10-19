"""Database Models 단위 테스트

src/infrastructure/database/models.py의 ORM 모델과 헬퍼 함수를 테스트합니다.

테스트 범위:
1. Server 모델 (__repr__, 필드)
2. ScanHistory 모델 (__repr__, 필드)
3. create_db_engine(): SQLite 엔진 생성
4. create_db_session(): Session 생성
5. init_database(): 데이터베이스 초기화
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.infrastructure.database.models import (
    Server,
    ScanHistory,
    create_db_engine,
    create_db_session,
    init_database,
)


# ==================== Server Model Tests ====================


@pytest.mark.unit
class TestServerModel:
    """Server ORM 모델 테스트"""

    def test_server_repr(self):
        """Server __repr__ 메서드 테스트"""
        server = Server(
            id=1,
            name="test-server",
            host="192.168.1.100",
            username="admin",
        )

        repr_str = repr(server)
        assert "<Server(id=1" in repr_str
        assert "name='test-server'" in repr_str
        assert "host='192.168.1.100'" in repr_str

    def test_server_creation(self):
        """Server 객체 생성 테스트"""
        server = Server(
            name="prod-server",
            host="10.0.0.1",
            port=22,
            username="root",
            auth_method="password",
            platform="linux",
            description="Production server",
        )

        assert server.name == "prod-server"
        assert server.host == "10.0.0.1"
        assert server.port == 22
        assert server.username == "root"
        assert server.auth_method == "password"
        assert server.platform == "linux"
        assert server.description == "Production server"


# ==================== ScanHistory Model Tests ====================


@pytest.mark.unit
class TestScanHistoryModel:
    """ScanHistory ORM 모델 테스트"""

    def test_scan_history_repr(self):
        """ScanHistory __repr__ 메서드 테스트"""
        history = ScanHistory(
            id=1,
            server_id=5,
            total=10,
            passed=7,
            failed=2,
            manual=1,
            score=75,
        )

        repr_str = repr(history)
        assert "<ScanHistory(id=1" in repr_str
        assert "server_id=5" in repr_str
        assert "score=75" in repr_str

    def test_scan_history_creation(self):
        """ScanHistory 객체 생성 테스트"""
        scan_time = datetime(2025, 1, 1, 12, 0, 0)
        history = ScanHistory(
            server_id=10,
            scan_time=scan_time,
            total=20,
            passed=15,
            failed=3,
            manual=2,
            score=80,
            result_data='{"risk_level": "low"}',
        )

        assert history.server_id == 10
        assert history.scan_time == scan_time
        assert history.total == 20
        assert history.passed == 15
        assert history.failed == 3
        assert history.manual == 2
        assert history.score == 80
        assert history.result_data == '{"risk_level": "low"}'


# ==================== Database Helper Functions Tests ====================


@pytest.mark.unit
class TestDatabaseHelpers:
    """데이터베이스 헬퍼 함수 테스트"""

    def test_create_db_engine(self, tmp_path):
        """create_db_engine 함수 테스트"""
        db_path = tmp_path / "test.db"

        engine = create_db_engine(str(db_path))

        assert engine is not None
        assert "sqlite" in str(engine.url)
        assert str(db_path) in str(engine.url)

    def test_create_db_session(self, tmp_path):
        """create_db_session 함수 테스트"""
        db_path = tmp_path / "test.db"
        engine = create_db_engine(str(db_path))

        session = create_db_session(engine)

        assert session is not None
        assert hasattr(session, "query")
        assert hasattr(session, "add")
        assert hasattr(session, "commit")

        session.close()

    def test_init_database(self, tmp_path):
        """init_database 함수 테스트"""
        db_path = tmp_path / "bluepy_test.db"

        engine = init_database(str(db_path))

        assert engine is not None
        assert db_path.exists()

        # 테이블이 생성되었는지 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "servers" in tables
        assert "scan_history" in tables


# ==================== Integration Tests ====================


@pytest.mark.unit
class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""

    def test_full_workflow(self, tmp_path):
        """전체 워크플로우: 초기화 → Session 생성 → 모델 사용"""
        db_path = tmp_path / "workflow_test.db"

        # 1. 데이터베이스 초기화
        engine = init_database(str(db_path))

        # 2. Session 생성
        session = create_db_session(engine)

        # 3. Server 추가
        server = Server(
            name="test-server",
            host="192.168.1.1",
            username="admin",
            auth_method="password",
        )
        session.add(server)
        session.commit()
        session.refresh(server)

        # 4. 조회 확인
        retrieved = session.query(Server).filter(Server.name == "test-server").first()
        assert retrieved is not None
        assert retrieved.name == "test-server"
        assert retrieved.host == "192.168.1.1"

        # 5. ScanHistory 추가
        history = ScanHistory(
            server_id=server.id,
            scan_time=datetime.now(),
            total=10,
            passed=8,
            failed=1,
            manual=1,
            score=85.0,
        )
        session.add(history)
        session.commit()

        # 6. 관계 조회 확인
        histories = session.query(ScanHistory).filter(ScanHistory.server_id == server.id).all()
        assert len(histories) == 1
        assert histories[0].server_id == server.id

        session.close()
