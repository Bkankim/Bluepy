"""ServerRepository 단위 테스트

src/infrastructure/database/repositories/server_repository.py의 CRUD 기능을 테스트합니다.

테스트 범위:
1. 초기화 (__init__)
2. create(): 서버 생성
3. get_by_id(): ID로 서버 조회
4. get_by_name(): 이름으로 서버 조회
5. get_all(): 전체 서버 목록
6. update(): 서버 정보 수정
7. delete(): 서버 삭제
8. count(): 서버 개수
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.models import Base, Server
from src.infrastructure.database.repositories.server_repository import ServerRepository


@pytest.fixture
def in_memory_db():
    """인메모리 SQLite 데이터베이스 픽스처"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repo(in_memory_db):
    """ServerRepository 인스턴스 픽스처"""
    return ServerRepository(in_memory_db)


# ==================== Initialization Tests ====================


@pytest.mark.unit
class TestServerRepositoryInit:
    """ServerRepository 초기화 테스트"""

    def test_init(self, in_memory_db):
        """ServerRepository 초기화 테스트"""
        repo = ServerRepository(in_memory_db)
        assert repo.session == in_memory_db


# ==================== Create Tests ====================


@pytest.mark.unit
class TestServerRepositoryCreate:
    """create() 메서드 테스트"""

    def test_create_server_success(self, repo):
        """서버 생성 성공"""
        server = repo.create(
            name="test-server",
            host="192.168.1.1",
            username="admin",
            port=22,
            auth_method="password",
            platform="linux"
        )

        assert server.name == "test-server"
        assert server.host == "192.168.1.1"
        assert server.username == "admin"
        assert server.port == 22
        assert server.auth_method == "password"
        assert server.platform == "linux"
        assert server.id is not None

    def test_create_server_duplicate_name(self, repo):
        """중복된 이름으로 서버 생성 시 예외 발생"""
        repo.create(name="test", host="1.1.1.1", username="user")

        with pytest.raises(ValueError, match="이미 존재"):
            repo.create(name="test", host="2.2.2.2", username="user")

    def test_create_server_with_key_auth(self, repo):
        """SSH 키 인증 서버 생성"""
        server = repo.create(
            name="key-server",
            host="10.0.0.1",
            username="root",
            auth_method="key",
            key_path="/path/to/key"
        )

        assert server.auth_method == "key"
        assert server.key_path == "/path/to/key"

    def test_create_server_with_description(self, repo):
        """설명이 있는 서버 생성"""
        server = repo.create(
            name="prod-server",
            host="prod.example.com",
            username="admin",
            description="Production server"
        )

        assert server.description == "Production server"


# ==================== Get Tests ====================


@pytest.mark.unit
class TestServerRepositoryGet:
    """get_by_id(), get_by_name() 테스트"""

    def test_get_by_id_found(self, repo):
        """ID로 서버 조회 성공"""
        server = repo.create(name="test", host="1.1.1.1", username="user")

        found = repo.get_by_id(server.id)

        assert found is not None
        assert found.id == server.id
        assert found.name == "test"

    def test_get_by_id_not_found(self, repo):
        """존재하지 않는 ID 조회 시 None 반환"""
        found = repo.get_by_id(99999)
        assert found is None

    def test_get_by_name_found(self, repo):
        """이름으로 서버 조회 성공"""
        repo.create(name="unique-name", host="1.1.1.1", username="user")

        found = repo.get_by_name("unique-name")

        assert found is not None
        assert found.name == "unique-name"

    def test_get_by_name_not_found(self, repo):
        """존재하지 않는 이름 조회 시 None 반환"""
        found = repo.get_by_name("non-existent")
        assert found is None


# ==================== Get All Tests ====================


@pytest.mark.unit
class TestServerRepositoryGetAll:
    """get_all() 테스트"""

    def test_get_all_empty(self, repo):
        """서버가 없을 때 빈 리스트 반환"""
        servers = repo.get_all()
        assert servers == []

    def test_get_all_single(self, repo):
        """서버 1개 조회"""
        repo.create(name="server1", host="1.1.1.1", username="user")

        servers = repo.get_all()

        assert len(servers) == 1
        assert servers[0].name == "server1"

    def test_get_all_multiple_ordered_by_created_at(self, repo):
        """여러 서버 조회 시 created_at 역순 정렬"""
        import time

        repo.create(name="server1", host="1.1.1.1", username="user")
        time.sleep(0.01)  # 시간 차이 보장
        repo.create(name="server2", host="2.2.2.2", username="user")

        servers = repo.get_all()

        assert len(servers) == 2
        assert servers[0].name == "server2"  # 최신 서버가 먼저
        assert servers[1].name == "server1"


# ==================== Update Tests ====================


@pytest.mark.unit
class TestServerRepositoryUpdate:
    """update() 메서드 테스트"""

    def test_update_server_success(self, repo):
        """서버 정보 수정 성공"""
        server = repo.create(name="test", host="1.1.1.1", username="user", port=22)

        updated = repo.update(server.id, host="2.2.2.2", port=2222)

        assert updated.host == "2.2.2.2"
        assert updated.port == 2222
        assert updated.name == "test"  # 변경 안한 필드는 유지

    def test_update_server_not_found(self, repo):
        """존재하지 않는 서버 수정 시 예외 발생"""
        with pytest.raises(ValueError, match="찾을 수 없습니다"):
            repo.update(99999, host="1.1.1.1")

    def test_update_server_all_allowed_fields(self, repo):
        """모든 허용된 필드 수정"""
        server = repo.create(name="old", host="1.1.1.1", username="user")

        updated = repo.update(
            server.id,
            name="new",
            host="2.2.2.2",
            port=2222,
            username="admin",
            auth_method="key",
            key_path="/new/key",
            platform="macos",
            description="Updated"
        )

        assert updated.name == "new"
        assert updated.host == "2.2.2.2"
        assert updated.port == 2222
        assert updated.username == "admin"
        assert updated.auth_method == "key"
        assert updated.key_path == "/new/key"
        assert updated.platform == "macos"
        assert updated.description == "Updated"

    def test_update_server_unknown_field_ignored(self, repo):
        """허용되지 않은 필드는 무시됨"""
        server = repo.create(name="test", host="1.1.1.1", username="user")

        # 허용되지 않은 필드 전달 (예외 발생하지 않음)
        updated = repo.update(server.id, unknown_field="value", host="2.2.2.2")

        assert updated.host == "2.2.2.2"
        assert not hasattr(updated, "unknown_field")


# ==================== Delete Tests ====================


@pytest.mark.unit
class TestServerRepositoryDelete:
    """delete() 메서드 테스트"""

    def test_delete_server_success(self, repo):
        """서버 삭제 성공"""
        server = repo.create(name="test", host="1.1.1.1", username="user")

        result = repo.delete(server.id)

        assert result is True
        assert repo.get_by_id(server.id) is None

    def test_delete_server_not_found(self, repo):
        """존재하지 않는 서버 삭제 시 False 반환"""
        result = repo.delete(99999)
        assert result is False


# ==================== Count Tests ====================


@pytest.mark.unit
class TestServerRepositoryCount:
    """count() 메서드 테스트"""

    def test_count_empty(self, repo):
        """서버가 없을 때 0 반환"""
        assert repo.count() == 0

    def test_count_single(self, repo):
        """서버 1개 생성 후 개수 확인"""
        repo.create(name="s1", host="1.1.1.1", username="user")
        assert repo.count() == 1

    def test_count_multiple(self, repo):
        """여러 서버 생성 후 개수 확인"""
        repo.create(name="s1", host="1.1.1.1", username="user")
        repo.create(name="s2", host="2.2.2.2", username="user")
        repo.create(name="s3", host="3.3.3.3", username="user")
        assert repo.count() == 3


# ==================== Integration Tests ====================


@pytest.mark.unit
class TestServerRepositoryIntegration:
    """ServerRepository 통합 테스트"""

    def test_full_crud_workflow(self, repo):
        """전체 CRUD 워크플로우 테스트"""
        # 1. Create
        server = repo.create(
            name="workflow-test",
            host="10.0.0.1",
            username="admin",
            description="Test server"
        )
        assert server.id is not None

        # 2. Read
        retrieved = repo.get_by_id(server.id)
        assert retrieved.name == "workflow-test"

        # 3. Update
        updated = repo.update(server.id, host="10.0.0.2", description="Updated server")
        assert updated.host == "10.0.0.2"
        assert updated.description == "Updated server"

        # 4. Delete
        result = repo.delete(server.id)
        assert result is True

        # 5. Verify deletion
        assert repo.get_by_id(server.id) is None
        assert repo.count() == 0
