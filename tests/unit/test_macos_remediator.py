"""MacOSRemediator 단위 테스트"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.remediation.macos_remediator import MacOSRemediator
from src.core.remediation.backup_manager import BackupManager
from src.core.scanner.base_scanner import BaseScanner


@pytest.fixture
def mock_scanner():
    """Mock Scanner 픽스처"""
    scanner = MagicMock(spec=BaseScanner)
    scanner.server_id = "test-macos-server"
    scanner.platform = "macos"
    scanner.execute_command = AsyncMock(return_value="success")
    return scanner


@pytest.fixture
def mock_backup_manager(tmp_path):
    """Mock BackupManager 픽스처"""
    return BackupManager(backup_root=str(tmp_path / "backups"))


@pytest.fixture
def macos_remediator(mock_scanner, mock_backup_manager):
    """MacOSRemediator 인스턴스"""
    return MacOSRemediator(
        scanner=mock_scanner,
        backup_manager=mock_backup_manager
    )


class TestMacOSRemediatorExecuteCommands:
    """_execute_commands() 메서드 테스트"""

    @pytest.mark.asyncio
    async def test_execute_commands_success_single(self, macos_remediator, mock_scanner):
        """단일 명령어 정상 실행"""
        commands = ["sudo spctl --master-enable"]

        result = await macos_remediator._execute_commands(commands)

        assert result == commands
        mock_scanner.execute_command.assert_awaited_once_with(commands[0])

    @pytest.mark.asyncio
    async def test_execute_commands_success_multiple(self, macos_remediator, mock_scanner):
        """여러 명령어 순차 실행"""
        commands = [
            "sudo spctl --master-enable",
            "sudo defaults write /Library/Preferences/com.apple.alf globalstate -int 1",
            "sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool true"
        ]

        result = await macos_remediator._execute_commands(commands)

        assert result == commands
        assert mock_scanner.execute_command.await_count == 3
        for cmd in commands:
            mock_scanner.execute_command.assert_any_await(cmd)

    @pytest.mark.asyncio
    async def test_execute_commands_empty_list(self, macos_remediator, mock_scanner):
        """빈 명령어 목록 처리"""
        commands = []

        result = await macos_remediator._execute_commands(commands)

        assert result == []
        mock_scanner.execute_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_execute_commands_failure_first(self, macos_remediator, mock_scanner):
        """첫 번째 명령어 실패 시 중단"""
        commands = [
            "sudo spctl --master-enable",
            "sudo defaults write test"
        ]
        mock_scanner.execute_command.side_effect = Exception("Permission denied")

        with pytest.raises(Exception) as exc_info:
            await macos_remediator._execute_commands(commands)

        assert "명령어 실행 실패" in str(exc_info.value)
        assert "sudo spctl" in str(exc_info.value)
        # 첫 번째 명령어 실행 후 중단
        mock_scanner.execute_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_commands_failure_middle(self, macos_remediator, mock_scanner):
        """중간 명령어 실패 시 중단"""
        commands = [
            "sudo spctl --master-enable",
            "sudo failing-command",
            "sudo defaults write test"
        ]

        # 첫 번째는 성공, 두 번째는 실패
        async def side_effect(cmd):
            if "failing" in cmd:
                raise Exception("Command not found")
            return "success"

        mock_scanner.execute_command.side_effect = side_effect

        with pytest.raises(Exception) as exc_info:
            await macos_remediator._execute_commands(commands)

        assert "명령어 실행 실패" in str(exc_info.value)
        assert "failing-command" in str(exc_info.value)
        # 두 번째 명령어까지만 실행
        assert mock_scanner.execute_command.await_count == 2

    @pytest.mark.asyncio
    async def test_execute_commands_long_command(self, macos_remediator, mock_scanner):
        """긴 명령어 로깅 테스트 (잘림 확인)"""
        # 50자 초과 명령어
        long_command = "sudo defaults write /Library/Preferences/com.apple.test.very.long.path.that.exceeds.fifty.characters TestKey -bool true"
        commands = [long_command]

        result = await macos_remediator._execute_commands(commands)

        assert result == commands
        mock_scanner.execute_command.assert_awaited_once_with(long_command)

    @pytest.mark.asyncio
    async def test_execute_commands_ssh_connection_error(self, macos_remediator, mock_scanner):
        """SSH 연결 오류 처리"""
        commands = ["sudo spctl --master-enable"]
        mock_scanner.execute_command.side_effect = Exception("SSH connection lost")

        with pytest.raises(Exception) as exc_info:
            await macos_remediator._execute_commands(commands)

        assert "명령어 실행 실패" in str(exc_info.value)
        assert "SSH connection lost" in str(exc_info.value)


class TestMacOSRemediatorIntegration:
    """통합 테스트 (remediate 전체 플로우)"""

    @pytest.mark.asyncio
    async def test_remediate_macos_gatekeeper(self, macos_remediator, mock_scanner):
        """M-03 Gatekeeper 자동 수정 시나리오"""
        from src.core.domain.models import RuleMetadata, RemediationInfo, Severity

        rule = RuleMetadata(
            id="M-03",
            name="Gatekeeper 활성화",
            category="application_security",
            description="Gatekeeper는 macOS의 앱 보안 기능입니다.",
            severity=Severity.HIGH,
            kisa_standard="M-03",
            commands=["spctl --status"],
            validator="validators.macos.check_m03",
            remediation=RemediationInfo(
                auto=True,
                description="Gatekeeper 활성화",
                backup_files=[],
                commands=["sudo spctl --master-enable"],
                manual_steps=[]
            )
        )

        # Dry-run 모드
        result = await macos_remediator.remediate(rule, dry_run=True)

        assert result.success is True
        assert result.dry_run is True
        assert "sudo spctl --master-enable" in result.message
        mock_scanner.execute_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_remediate_macos_firewall(self, macos_remediator, mock_scanner):
        """M-04 Firewall 자동 수정 시나리오"""
        from src.core.domain.models import RuleMetadata, RemediationInfo, Severity

        rule = RuleMetadata(
            id="M-04",
            name="방화벽 활성화",
            category="network_security",
            description="macOS 방화벽을 활성화하여 네트워크 보안을 강화합니다.",
            severity=Severity.HIGH,
            kisa_standard="M-04",
            commands=["sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"],
            validator="validators.macos.check_m04",
            remediation=RemediationInfo(
                auto=True,
                description="방화벽 활성화",
                backup_files=[],
                commands=["sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on"],
                manual_steps=[]
            )
        )

        # 실제 실행 모드
        result = await macos_remediator.remediate(rule, dry_run=False)

        assert result.success is True
        assert result.dry_run is False
        assert len(result.executed_commands) == 1
        assert "socketfilterfw" in result.executed_commands[0]
        mock_scanner.execute_command.assert_awaited_once()
