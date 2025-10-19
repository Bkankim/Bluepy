"""LinuxRemediator 단위 테스트"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.remediation.linux_remediator import LinuxRemediator
from src.core.remediation.backup_manager import BackupManager
from src.core.scanner.base_scanner import BaseScanner


@pytest.fixture
def mock_scanner():
    """Mock Scanner 픽스처"""
    scanner = MagicMock(spec=BaseScanner)
    scanner.server_id = "test-linux-server"
    scanner.platform = "linux"
    scanner.execute_command = AsyncMock(return_value="success")
    return scanner


@pytest.fixture
def mock_backup_manager(tmp_path):
    """Mock BackupManager 픽스처"""
    return BackupManager(backup_root=str(tmp_path / "backups"))


@pytest.fixture
def linux_remediator(mock_scanner, mock_backup_manager):
    """LinuxRemediator 인스턴스"""
    return LinuxRemediator(scanner=mock_scanner, backup_manager=mock_backup_manager)


class TestLinuxRemediatorExecuteCommands:
    """_execute_commands() 메서드 테스트"""

    @pytest.mark.asyncio
    async def test_execute_commands_success_single(
        self, linux_remediator, mock_scanner
    ):
        """단일 명령어 정상 실행"""
        commands = ["chmod 600 /etc/passwd"]

        result = await linux_remediator._execute_commands(commands)

        assert result == commands
        mock_scanner.execute_command.assert_awaited_once_with(commands[0])

    @pytest.mark.asyncio
    async def test_execute_commands_success_multiple(
        self, linux_remediator, mock_scanner
    ):
        """여러 명령어 순차 실행"""
        commands = [
            "chmod 600 /etc/passwd",
            "chmod 400 /etc/shadow",
            "chmod 644 /etc/services",
        ]

        result = await linux_remediator._execute_commands(commands)

        assert result == commands
        assert mock_scanner.execute_command.await_count == 3
        for cmd in commands:
            mock_scanner.execute_command.assert_any_await(cmd)

    @pytest.mark.asyncio
    async def test_execute_commands_empty_list(self, linux_remediator, mock_scanner):
        """빈 명령어 목록 처리"""
        commands = []

        result = await linux_remediator._execute_commands(commands)

        assert result == []
        mock_scanner.execute_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_execute_commands_failure_first(
        self, linux_remediator, mock_scanner
    ):
        """첫 번째 명령어 실패 시 중단"""
        commands = ["chmod 600 /etc/passwd", "chmod 400 /etc/shadow"]
        mock_scanner.execute_command.side_effect = Exception("Permission denied")

        with pytest.raises(Exception) as exc_info:
            await linux_remediator._execute_commands(commands)

        assert "명령어 실행 실패" in str(exc_info.value)
        assert "chmod 600" in str(exc_info.value)
        # 첫 번째 명령어 실행 후 중단
        mock_scanner.execute_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_commands_failure_middle(
        self, linux_remediator, mock_scanner
    ):
        """중간 명령어 실패 시 중단"""
        commands = [
            "chmod 600 /etc/passwd",
            "chmod 000 /nonexistent",
            "chmod 644 /etc/services",
        ]

        # 첫 번째는 성공, 두 번째는 실패
        mock_scanner.execute_command.side_effect = [
            "success",
            Exception("No such file"),
            "success",
        ]

        with pytest.raises(Exception) as exc_info:
            await linux_remediator._execute_commands(commands)

        assert "명령어 실행 실패" in str(exc_info.value)
        # 첫 번째 성공, 두 번째 실패 후 중단
        assert mock_scanner.execute_command.await_count == 2


class TestLinuxRemediatorIntegration:
    """통합 테스트 (Tier 1 규칙)"""

    @pytest.mark.asyncio
    async def test_u18_chmod_passwd(self, linux_remediator, mock_scanner):
        """U-18: /etc/passwd 권한 설정 (600)"""
        commands = ["chmod 600 /etc/passwd"]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert result[0] == "chmod 600 /etc/passwd"
        mock_scanner.execute_command.assert_awaited_once_with("chmod 600 /etc/passwd")

    @pytest.mark.asyncio
    async def test_u19_chmod_shadow(self, linux_remediator, mock_scanner):
        """U-19: /etc/shadow 권한 설정 (400)"""
        commands = ["chmod 400 /etc/shadow"]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert result[0] == "chmod 400 /etc/shadow"
        mock_scanner.execute_command.assert_awaited_once_with("chmod 400 /etc/shadow")

    @pytest.mark.asyncio
    async def test_u22_chmod_syslog(self, linux_remediator, mock_scanner):
        """U-22: /etc/syslog.conf 권한 설정 (644)"""
        commands = ["chmod 644 /etc/syslog.conf"]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert result[0] == "chmod 644 /etc/syslog.conf"

    @pytest.mark.asyncio
    async def test_u23_chmod_services(self, linux_remediator, mock_scanner):
        """U-23: /etc/services 권한 설정 (644)"""
        commands = ["chmod 644 /etc/services"]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert result[0] == "chmod 644 /etc/services"

    @pytest.mark.asyncio
    async def test_u39_chmod_cron_multiple(self, linux_remediator, mock_scanner):
        """U-39: cron 파일 권한 설정 (640, 여러 파일)"""
        commands = [
            "chmod 640 /etc/crontab",
            "chmod 640 /var/spool/cron/crontabs/* 2>/dev/null || true",
        ]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 2
        assert result[0] == "chmod 640 /etc/crontab"
        assert mock_scanner.execute_command.await_count == 2
