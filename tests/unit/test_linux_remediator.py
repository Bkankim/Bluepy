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


class TestLinuxRemediatorTier2:
    """통합 테스트 (Tier 2 규칙 - PAM/sed)"""

    @pytest.mark.asyncio
    async def test_u01_pam_securetty(self, linux_remediator, mock_scanner):
        """U-01: root 원격 접속 제한 (PAM + sed)"""
        commands = [
            'grep -q "pam_securetty.so" /etc/pam.d/login || echo "auth required /lib/security/pam_securetty.so" >> /etc/pam.d/login',
            "sed -i '/^pts/d' /etc/securetty",
        ]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 2
        assert "pam_securetty.so" in result[0]
        assert "sed" in result[1]
        assert mock_scanner.execute_command.await_count == 2

    @pytest.mark.asyncio
    async def test_u03_pam_tally(self, linux_remediator, mock_scanner):
        """U-03: 계정 잠금 임계값 (PAM 2줄)"""
        commands = [
            'grep -q "pam_tally.so.*deny=5" /etc/pam.d/system-auth || echo "auth required /lib/security/pam_tally.so deny=5 unlock_time=120 no_magic_root" >> /etc/pam.d/system-auth',
            'grep -q "pam_tally.so.*reset" /etc/pam.d/system-auth || echo "account required /lib/security/pam_tally.so no_magic_root reset" >> /etc/pam.d/system-auth',
        ]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 2
        assert "deny=5" in result[0]
        assert "reset" in result[1]

    @pytest.mark.asyncio
    async def test_u06_pam_wheel(self, linux_remediator, mock_scanner):
        """U-06: root su 제한 (PAM)"""
        commands = [
            'grep -q "pam_wheel.so" /etc/pam.d/su || echo "auth required /lib/security/pam_wheel.so debug group=wheel" >> /etc/pam.d/su'
        ]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert "pam_wheel.so" in result[0]

    @pytest.mark.asyncio
    async def test_u21_chmod_inetd(self, linux_remediator, mock_scanner):
        """U-21: /etc/inetd.conf 권한 설정 (600)"""
        commands = ["chmod 600 /etc/inetd.conf"]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 1
        assert result[0] == "chmod 600 /etc/inetd.conf"

    @pytest.mark.asyncio
    async def test_u38_sed_rservices(self, linux_remediator, mock_scanner):
        """U-38: r계열 서비스 비활성화 (sed 3줄)"""
        commands = [
            "sed -i 's/^rsh/#rsh/' /etc/inetd.conf 2>/dev/null || true",
            "sed -i 's/^rlogin/#rlogin/' /etc/inetd.conf 2>/dev/null || true",
            "sed -i 's/^rexec/#rexec/' /etc/inetd.conf 2>/dev/null || true",
        ]

        result = await linux_remediator._execute_commands(commands)

        assert len(result) == 3
        assert "rsh" in result[0]
        assert "rlogin" in result[1]
        assert "rexec" in result[2]
        assert mock_scanner.execute_command.await_count == 3
