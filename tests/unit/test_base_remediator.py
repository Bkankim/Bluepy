"""BaseRemediator 단위 테스트

자동 수정 추상 클래스의 핵심 기능을 테스트합니다.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.core.remediation.base_remediator import BaseRemediator
from src.core.remediation.backup_manager import BackupManager, BackupFile
from src.core.domain.models import (
    RemediationResult,
    RuleMetadata,
    RemediationInfo,
    Severity,
)
from src.core.scanner.base_scanner import BaseScanner


# ==================== 테스트용 Concrete Remediator ====================


class TestRemediator(BaseRemediator):
    """테스트용 Concrete Remediator"""

    def __init__(self, scanner, backup_manager=None, command_results=None):
        super().__init__(scanner, backup_manager)
        self.command_results = command_results or []

    async def _execute_commands(self, commands: list[str]) -> list[str]:
        """명령어 실행 Mock"""
        if self.command_results and isinstance(self.command_results[0], Exception):
            raise self.command_results[0]
        return commands  # 정상적으로 실행된 명령어 목록 반환


# ==================== Helper Functions ====================


def create_test_rule(
    rule_id="U-01",
    auto=True,
    commands=None,
    backup_files=None,
):
    """테스트용 RuleMetadata 생성"""
    if commands is None:
        commands = ["sudo systemctl restart sshd"]

    remediation_info = RemediationInfo(
        auto=auto,
        commands=commands,
        backup_files=backup_files or [],
    ) if auto else None

    return RuleMetadata(
        id=rule_id,
        name=f"Test Rule {rule_id}",
        category="account_management",
        description="Test rule description",
        severity=Severity.HIGH,
        kisa_standard=rule_id,
        commands=["cat /etc/ssh/sshd_config"],
        validator="validators.linux.check_u01_test",
        remediation=remediation_info,
    )


# ==================== BaseRemediator 핵심 기능 테스트 ====================


@pytest.mark.unit
@pytest.mark.asyncio
class TestBaseRemediatorCore:
    """BaseRemediator 핵심 기능 테스트"""

    async def test_remediate_auto_false_rule(self):
        """remediation.auto=False인 규칙 처리"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        remediator = TestRemediator(mock_scanner)
        
        rule = create_test_rule(auto=False)

        # Act
        result = await remediator.remediate(rule, dry_run=True)

        # Assert
        assert result.success is False
        assert "불가능한 규칙" in result.message

    async def test_remediate_no_remediation_info(self):
        """remediation이 None인 규칙 처리"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        remediator = TestRemediator(mock_scanner)
        
        rule = RuleMetadata(
            id="U-04",
            name="No Remediation Rule",
            category="account_management",
            description="Test",
            severity=Severity.HIGH,
            kisa_standard="U-04",
            commands=["test"],
            validator="validators.linux.check_u04_test",
            remediation=None,
        )

        # Act
        result = await remediator.remediate(rule, dry_run=True)

        # Assert
        assert result.success is False
        assert "불가능한 규칙" in result.message

    async def test_remediate_dry_run_calls_simulate(self):
        """dry_run=True일 때 _simulate() 호출"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        remediator = TestRemediator(mock_scanner)
        
        rule = create_test_rule(commands=["cmd1", "cmd2", "cmd3"])

        # Act
        result = await remediator.remediate(rule, dry_run=True)

        # Assert
        assert result.success is True
        assert result.dry_run is True
        assert "[Dry-run]" in result.message
        assert "명령어 3개" in result.message
        assert result.executed_commands == ["cmd1", "cmd2", "cmd3"]

    async def test_remediate_execute_calls_execute_remediation(self):
        """dry_run=False일 때 _execute_remediation() 호출"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        mock_backup_manager.save_metadata = MagicMock()
        
        remediator = TestRemediator(mock_scanner, backup_manager=mock_backup_manager)
        rule = create_test_rule(commands=["cmd1"])

        # Act
        result = await remediator.remediate(rule, dry_run=False)

        # Assert
        assert result.success is True
        assert result.dry_run is False
        assert "자동 수정 완료" in result.message
        assert result.backup_id == "session_20251019_120000"
        assert result.executed_commands == ["cmd1"]

    async def test_simulate_returns_commands_preview(self):
        """_simulate()가 명령어 미리보기 반환"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        remediator = TestRemediator(mock_scanner)
        
        rule = create_test_rule(commands=["cmd1", "cmd2", "cmd3", "cmd4"])

        # Act
        result = await remediator._simulate(rule)

        # Assert
        assert result.success is True
        assert result.dry_run is True
        assert "[Dry-run]" in result.message
        assert "cmd1" in result.message
        assert "cmd2" in result.message
        assert "cmd3" in result.message
        # 최대 3개만 표시
        assert result.executed_commands == ["cmd1", "cmd2", "cmd3", "cmd4"]


# ==================== BaseRemediator 실행 로직 테스트 ====================


@pytest.mark.unit
@pytest.mark.asyncio
class TestBaseRemediatorExecution:
    """BaseRemediator 실행 로직 테스트"""

    async def test_execute_remediation_success(self):
        """정상 자동 수정 실행"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        mock_backup_manager.save_metadata = MagicMock()
        
        remediator = TestRemediator(mock_scanner, backup_manager=mock_backup_manager)
        rule = create_test_rule(commands=["systemctl restart sshd"])

        # Act
        result = await remediator._execute_remediation(rule)

        # Assert
        assert result.success is True
        assert result.backup_id == "session_20251019_120000"
        assert result.executed_commands == ["systemctl restart sshd"]
        assert "자동 수정 완료" in result.message
        mock_backup_manager.create_session.assert_called_once()
        mock_backup_manager.save_metadata.assert_called_once()

    async def test_execute_remediation_with_backup_files(self):
        """백업 파일 포함한 자동 수정"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        mock_backup_manager.backup_file = MagicMock(return_value=BackupFile(
            original_path="/etc/ssh/sshd_config",
            backup_path="/var/backups/bluepy/sessions/session_20251019_120000/files/sshd_config.bak",
            mode="0644",
            checksum="sha256:abc123",
        ))
        mock_backup_manager.save_metadata = MagicMock()
        
        remediator = TestRemediator(mock_scanner, backup_manager=mock_backup_manager)
        rule = create_test_rule(
            commands=["echo 'test' >> /etc/ssh/sshd_config"],
            backup_files=["/etc/ssh/sshd_config"],
        )

        # Act
        result = await remediator._execute_remediation(rule)

        # Assert
        assert result.success is True
        mock_backup_manager.backup_file.assert_called_once_with(
            "session_20251019_120000", "/etc/ssh/sshd_config"
        )

    async def test_execute_remediation_failure_rollback(self):
        """실행 실패 시 롤백 수행"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        mock_backup_manager.backup_file = MagicMock(return_value=BackupFile(
            original_path="/etc/test.conf",
            backup_path="/tmp/backup.bak",
            mode="0644",
            checksum="sha256:abc123",
        ))
        mock_backup_manager.rollback_file = MagicMock(return_value=True)
        
        # 명령어 실행 실패 시뮬레이션
        remediator = TestRemediator(
            mock_scanner,
            backup_manager=mock_backup_manager,
            command_results=[Exception("Command failed")],
        )
        rule = create_test_rule(
            commands=["failing command"],
            backup_files=["/etc/test.conf"],
        )

        # Act
        result = await remediator._execute_remediation(rule)

        # Assert
        assert result.success is False
        assert "자동 수정 실패" in result.message
        assert result.error == "Command failed"
        assert result.rollback_performed is True
        mock_backup_manager.rollback_file.assert_called_once()

    async def test_execute_remediation_no_backup_files(self):
        """backup_files가 없을 때 정상 처리"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        mock_backup_manager.save_metadata = MagicMock()
        
        remediator = TestRemediator(mock_scanner, backup_manager=mock_backup_manager)
        rule = create_test_rule(
            commands=["systemctl disable telnet"],
            backup_files=None,  # backup_files 없음
        )

        # Act
        result = await remediator._execute_remediation(rule)

        # Assert
        assert result.success is True
        mock_backup_manager.backup_file.assert_not_called()

    async def test_execute_remediation_partial_backup_failure(self):
        """일부 백업 실패 시 경고 후 계속 진행"""
        # Arrange
        mock_scanner = MagicMock(spec=BaseScanner)
        mock_scanner.server_id = "test-server"
        mock_backup_manager = MagicMock(spec=BackupManager)
        mock_backup_manager.create_session = MagicMock(return_value="session_20251019_120000")
        
        # 첫 번째 파일은 성공, 두 번째 파일은 실패
        backup_file_success = BackupFile(
            original_path="/etc/file1.conf",
            backup_path="/tmp/file1.bak",
            mode="0644",
            checksum="sha256:abc123",
        )
        mock_backup_manager.backup_file = MagicMock(side_effect=[
            backup_file_success,
            FileNotFoundError("File not found"),
        ])
        mock_backup_manager.save_metadata = MagicMock()
        
        remediator = TestRemediator(mock_scanner, backup_manager=mock_backup_manager)
        rule = create_test_rule(
            commands=["test command"],
            backup_files=["/etc/file1.conf", "/etc/non_existent.conf"],
        )

        # Act
        result = await remediator._execute_remediation(rule)

        # Assert
        assert result.success is True  # 일부 백업 실패해도 계속 진행
        assert mock_backup_manager.backup_file.call_count == 2
