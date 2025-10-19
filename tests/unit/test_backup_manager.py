"""BackupManager 단위 테스트

백업/롤백 관리자의 핵심 기능을 테스트합니다.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from src.core.remediation.backup_manager import (
    BackupManager,
    BackupFile,
    BackupSession,
)


# ==================== BackupManager 핵심 기능 테스트 ====================


@pytest.mark.unit
class TestBackupManagerCore:
    """BackupManager 핵심 기능 테스트"""

    def test_create_session_creates_directory(self, tmp_path):
        """백업 세션 생성 시 디렉토리 생성 확인"""
        # Arrange
        backup_root = tmp_path / "backups"
        manager = BackupManager(backup_root=str(backup_root))

        # Act
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # Assert
        assert session_id.startswith("session_")
        session_dir = backup_root / "sessions" / session_id
        assert session_dir.exists()
        assert (session_dir / "files").exists()

    def test_create_session_returns_unique_id(self, tmp_path):
        """백업 세션 ID가 타임스탬프 기반으로 생성되는지 확인"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))

        # Act
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # Assert
        # 형식: session_YYYYMMDD_HHMMSS
        parts = session_id.split("_")
        assert len(parts) == 3
        assert parts[0] == "session"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS

    def test_backup_file_success(self, tmp_path):
        """파일 백업 정상 동작 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 테스트 파일 생성
        test_file = tmp_path / "test.conf"
        test_content = "original content"
        test_file.write_text(test_content)

        # Act
        backup_file = manager.backup_file(session_id=session_id, file_path=str(test_file))

        # Assert
        assert backup_file.original_path == str(test_file)
        assert Path(backup_file.backup_path).exists()
        assert backup_file.checksum.startswith("sha256:")
        assert backup_file.mode in ("0644", "0666")  # OS dependent

        # 백업된 내용 확인
        backup_path = Path(backup_file.backup_path)
        assert backup_path.read_text() == test_content

    def test_backup_file_not_found(self, tmp_path):
        """존재하지 않는 파일 백업 시 FileNotFoundError 발생"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])
        non_existent_file = tmp_path / "non_existent.conf"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="원본 파일 없음"):
            manager.backup_file(session_id=session_id, file_path=str(non_existent_file))

    def test_rollback_file_success(self, tmp_path):
        """파일 롤백 정상 동작 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 원본 파일 생성 및 백업
        original_file = tmp_path / "original.conf"
        original_content = "original content"
        original_file.write_text(original_content)
        backup_file = manager.backup_file(session_id=session_id, file_path=str(original_file))

        # 원본 파일 수정
        original_file.write_text("modified content")

        # Act
        result = manager.rollback_file(backup_file)

        # Assert
        assert result is True
        assert original_file.read_text() == original_content

    def test_rollback_file_checksum_mismatch(self, tmp_path):
        """백업 파일 체크섬 불일치 시 ValueError 발생"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 원본 파일 생성 및 백업
        original_file = tmp_path / "original.conf"
        original_file.write_text("original content")
        backup_file = manager.backup_file(session_id=session_id, file_path=str(original_file))

        # 백업 파일 손상 (내용 변경)
        backup_path = Path(backup_file.backup_path)
        backup_path.write_text("corrupted content")

        # Act
        result = manager.rollback_file(backup_file)

        # Assert
        assert result is False  # 롤백 실패

    def test_calculate_checksum_sha256(self, tmp_path):
        """SHA256 체크섬 계산 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        test_file = tmp_path / "test.txt"
        test_content = "test content for checksum"
        test_file.write_text(test_content)

        # Act
        checksum1 = manager._calculate_checksum(test_file)
        checksum2 = manager._calculate_checksum(test_file)

        # Assert
        assert checksum1.startswith("sha256:")
        assert checksum1 == checksum2  # 동일 파일은 동일 체크섬
        assert len(checksum1) == 71  # "sha256:" (7) + hex digest (64)

    def test_save_metadata_writes_json(self, tmp_path):
        """백업 메타데이터 JSON 저장 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 백업 세션 객체 생성
        session = BackupSession(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            server="test-server",
            rule_ids=["U-01", "U-04"],
            files=[{"original_path": "/etc/test.conf", "backup_path": "/tmp/backup.bak"}],
            status="completed",
        )

        # Act
        manager.save_metadata(session)

        # Assert
        metadata_path = tmp_path / "sessions" / session_id / "metadata.json"
        assert metadata_path.exists()

        # JSON 내용 확인
        with metadata_path.open("r") as f:
            data = json.load(f)
        assert data["session_id"] == session_id
        assert data["server"] == "test-server"
        assert data["rule_ids"] == ["U-01", "U-04"]
        assert data["status"] == "completed"


# ==================== BackupManager 엣지 케이스 테스트 ====================


@pytest.mark.unit
class TestBackupManagerEdgeCases:
    """BackupManager 엣지 케이스 테스트"""

    def test_backup_file_empty_file(self, tmp_path):
        """빈 파일 백업 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 빈 파일 생성
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        # Act
        backup_file = manager.backup_file(session_id=session_id, file_path=str(empty_file))

        # Assert
        assert Path(backup_file.backup_path).exists()
        assert Path(backup_file.backup_path).read_text() == ""
        assert backup_file.checksum.startswith("sha256:")

    def test_backup_file_large_file(self, tmp_path):
        """대용량 파일 백업 테스트 (청크 처리 검증)"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 5KB 파일 생성 (4096 바이트 청크 크기보다 큼)
        large_file = tmp_path / "large.txt"
        large_content = "x" * 5000
        large_file.write_text(large_content)

        # Act
        backup_file = manager.backup_file(session_id=session_id, file_path=str(large_file))

        # Assert
        assert Path(backup_file.backup_path).exists()
        assert Path(backup_file.backup_path).read_text() == large_content
        assert backup_file.checksum.startswith("sha256:")

    def test_backup_file_special_characters_in_path(self, tmp_path):
        """경로에 특수문자 포함 시 백업 파일명 생성 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        session_id = manager.create_session(server="test-server", rule_ids=["U-01"])

        # 특수문자 포함 경로
        test_file = tmp_path / "test-file.conf"
        test_file.write_text("content")

        # Act
        backup_file = manager.backup_file(session_id=session_id, file_path=str(test_file))

        # Assert
        backup_name = Path(backup_file.backup_path).name
        assert "_" in backup_name  # "/" -> "_" 변환 확인
        assert backup_name.endswith(".bak")

    def test_rollback_file_backup_not_exist(self, tmp_path):
        """백업 파일이 존재하지 않을 때 롤백 실패"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))

        # 존재하지 않는 백업 파일 정보
        backup_file = BackupFile(
            original_path=str(tmp_path / "original.txt"),
            backup_path=str(tmp_path / "non_existent_backup.bak"),
            mode="0644",
            checksum="sha256:abc123",
        )

        # Act
        result = manager.rollback_file(backup_file)

        # Assert
        assert result is False  # 롤백 실패

    def test_calculate_checksum_binary_file(self, tmp_path):
        """바이너리 파일 체크섬 계산 테스트"""
        # Arrange
        manager = BackupManager(backup_root=str(tmp_path))
        binary_file = tmp_path / "binary.dat"
        binary_content = b"\x00\x01\x02\x03\x04\x05\xff\xfe\xfd"
        binary_file.write_bytes(binary_content)

        # Act
        checksum = manager._calculate_checksum(binary_file)

        # Assert
        assert checksum.startswith("sha256:")
        assert len(checksum) == 71
