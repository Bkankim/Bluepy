"""Scanner 모듈 단위 테스트

src/core/scanner/base_scanner.py와 linux_scanner.py를 테스트합니다.

테스트 범위:
1. ScanResult: 스캔 결과 dataclass
2. BaseScanner: 추상 클래스 (메서드 존재 확인)
3. LinuxScanner: Linux 스캐너 구현 (mock 사용)
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.domain.models import CheckResult, Status, Severity, RuleMetadata
from src.core.scanner.base_scanner import ScanResult, BaseScanner
from src.core.scanner.linux_scanner import LinuxScanner


# ==================== ScanResult Tests ====================


@pytest.mark.unit
class TestScanResult:
    """ScanResult 테스트"""

    def test_create_scan_result(self):
        """ScanResult 생성 테스트"""
        result = ScanResult(server_id="server-001", platform="linux")
        assert result.server_id == "server-001"
        assert result.platform == "linux"
        assert isinstance(result.scan_time, datetime)
        assert result.results == {}

    def test_scan_result_total_property(self):
        """total property 테스트"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.MANUAL, message="Test"),
        }
        assert result.total == 3

    def test_scan_result_passed_property(self):
        """passed property 테스트"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test 1"),
            "U-02": CheckResult(status=Status.PASS, message="Test 2"),
            "U-03": CheckResult(status=Status.FAIL, message="Test 3"),
        }
        assert result.passed == 2

    def test_scan_result_failed_property(self):
        """failed property 테스트"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.FAIL, message="Test"),
        }
        assert result.failed == 2

    def test_scan_result_manual_property(self):
        """manual property 테스트"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.MANUAL, message="Test 1"),
            "U-02": CheckResult(status=Status.MANUAL, message="Test 2"),
            "U-03": CheckResult(status=Status.PASS, message="Test 3"),
        }
        assert result.manual == 2

    def test_scan_result_score_all_pass(self):
        """score property 테스트 (모두 PASS)"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.PASS, message="Test"),
        }
        # 2 PASS / 2 total = 100점
        assert result.score == 100.0

    def test_scan_result_score_all_fail(self):
        """score property 테스트 (모두 FAIL)"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.FAIL, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
        }
        # 0 PASS / 2 total = 0점
        assert result.score == 0.0

    def test_scan_result_score_mixed(self):
        """score property 테스트 (혼합)"""
        result = ScanResult(server_id="server-001", platform="linux")
        result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),  # 1.0점
            "U-02": CheckResult(status=Status.FAIL, message="Test"),  # 0점
            "U-03": CheckResult(status=Status.MANUAL, message="Test"),  # 0.5점
            "U-04": CheckResult(status=Status.MANUAL, message="Test"),  # 0.5점
        }
        # (1.0 + 0 + 0.5 + 0.5) / 4 * 100 = 50점
        assert result.score == 50.0

    def test_scan_result_score_empty(self):
        """score property 테스트 (결과 없음)"""
        result = ScanResult(server_id="server-001", platform="linux")
        # 결과가 없으면 0점
        assert result.score == 0.0


# ==================== BaseScanner Tests ====================


@pytest.mark.unit
class TestBaseScanner:
    """BaseScanner 추상 클래스 테스트"""

    def test_base_scanner_is_abstract(self):
        """BaseScanner는 직접 인스턴스화할 수 없음"""
        with pytest.raises(TypeError):
            BaseScanner(server_id="test", platform="linux")

    def test_base_scanner_has_abstract_methods(self):
        """BaseScanner에 필수 추상 메서드가 정의되어 있는지 확인"""
        abstract_methods = BaseScanner.__abstractmethods__
        expected_methods = {"connect", "disconnect", "execute_command", "load_rules", "scan_one"}

        assert expected_methods.issubset(
            abstract_methods
        ), f"필수 추상 메서드가 누락되었습니다. 예상: {expected_methods}, 실제: {abstract_methods}"


# ==================== LinuxScanner Tests ====================


@pytest.mark.unit
class TestLinuxScannerInit:
    """LinuxScanner 초기화 테스트"""

    def test_linux_scanner_init_with_password(self):
        """LinuxScanner 초기화 (패스워드)"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )
        assert scanner.server_id == "server-001"
        assert scanner.platform == "linux"
        assert scanner.is_connected() is False

    def test_linux_scanner_init_with_key(self):
        """LinuxScanner 초기화 (SSH 키)"""
        scanner = LinuxScanner(
            server_id="server-002",
            host="192.168.1.101",
            username="admin",
            key_filename="/path/to/key.pem",
        )
        assert scanner.server_id == "server-002"
        assert scanner.platform == "linux"

    def test_linux_scanner_init_custom_port(self):
        """LinuxScanner 초기화 (커스텀 포트)"""
        scanner = LinuxScanner(
            server_id="server-003",
            host="192.168.1.102",
            username="admin",
            password="secret",
            port=2222,
        )
        assert scanner.server_id == "server-003"


@pytest.mark.unit
@pytest.mark.asyncio
class TestLinuxScannerConnection:
    """LinuxScanner 연결 테스트"""

    async def test_connect_success(self):
        """연결 성공 테스트"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # SSH 클라이언트 connect mock
        with patch.object(scanner._ssh_client, "connect", new_callable=AsyncMock) as mock_connect:
            await scanner.connect()
            mock_connect.assert_called_once()
            assert scanner.is_connected() is True

    async def test_connect_failure(self):
        """연결 실패 테스트"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # SSH 클라이언트 connect가 예외 발생
        with patch.object(scanner._ssh_client, "connect", new_callable=AsyncMock) as mock_connect:
            from src.infrastructure.network.ssh_client import SSHClientError

            mock_connect.side_effect = SSHClientError("Connection refused")

            with pytest.raises(ConnectionError):
                await scanner.connect()

            assert scanner.is_connected() is False

    async def test_disconnect(self):
        """연결 해제 테스트"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # 먼저 연결
        with patch.object(scanner._ssh_client, "connect", new_callable=AsyncMock):
            await scanner.connect()

        # 연결 해제
        with patch.object(
            scanner._ssh_client, "disconnect", new_callable=AsyncMock
        ) as mock_disconnect:
            await scanner.disconnect()
            mock_disconnect.assert_called_once()
            assert scanner.is_connected() is False


@pytest.mark.unit
@pytest.mark.asyncio
class TestLinuxScannerCommandExecution:
    """LinuxScanner 명령어 실행 테스트"""

    async def test_execute_command_success(self):
        """명령어 실행 성공 테스트"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # 연결 상태로 만들기
        scanner._connected = True

        # execute 메서드 mock
        with patch.object(scanner._ssh_client, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = "command output"

            result = await scanner.execute_command("ls -la")
            assert result == "command output"
            mock_execute.assert_called_once_with("ls -la")

    async def test_execute_command_without_connection(self):
        """연결 없이 명령어 실행 시도 (에러)"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # 연결하지 않은 상태
        with pytest.raises(RuntimeError, match="연결되지 않았습니다"):
            await scanner.execute_command("ls -la")


@pytest.mark.unit
@pytest.mark.asyncio
class TestLinuxScannerRuleLoading:
    """LinuxScanner 규칙 로드 테스트"""

    async def test_load_rules_success(self, tmp_path, sample_yaml_data):
        """규칙 로드 성공 테스트"""
        import yaml

        # 임시 규칙 디렉토리 생성
        rules_dir = tmp_path / "rules" / "linux"
        rules_dir.mkdir(parents=True)

        # 샘플 YAML 파일 생성
        yaml_file = rules_dir / "U-01.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_yaml_data, f)

        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # 규칙 로드
        await scanner.load_rules(str(tmp_path / "rules"))
        assert scanner.get_rules_count() == 1

    async def test_get_rules_count_empty(self):
        """규칙 로드 전 개수 확인"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )
        assert scanner.get_rules_count() == 0


@pytest.mark.unit
@pytest.mark.asyncio
class TestLinuxScannerScanning:
    """LinuxScanner 스캔 테스트"""

    async def test_scan_all_without_connection(self):
        """연결 없이 scan_all 호출 (에러)"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        with pytest.raises(RuntimeError, match="연결되지 않았습니다"):
            await scanner.scan_all()

    async def test_scan_all_without_rules(self):
        """규칙 로드 없이 scan_all 호출 (에러)"""
        scanner = LinuxScanner(
            server_id="server-001",
            host="192.168.1.100",
            username="admin",
            password="secret",
        )

        # 연결 상태로 만들기
        scanner._connected = True

        with pytest.raises(RuntimeError, match="규칙이 로드되지 않았습니다"):
            await scanner.scan_all()


@pytest.mark.unit
class TestScanResultAdditional:
    """ScanResult 추가 테스트 (커버리지 증가)"""

    def test_scan_result_with_dict_results(self):
        """Dict 형태의 results 테스트"""
        results = {
            "U-01": CheckResult(status=Status.PASS, message="통과", timestamp=datetime.now()),
            "U-02": CheckResult(status=Status.FAIL, message="실패", timestamp=datetime.now()),
            "U-03": CheckResult(status=Status.MANUAL, message="수동", timestamp=datetime.now()),
        }

        scan_result = ScanResult(server_id="test-server", platform="linux", results=results)

        assert scan_result.total == 3
        assert scan_result.passed == 1
        assert scan_result.failed == 1
        assert scan_result.manual == 1

    def test_scan_result_empty(self):
        """빈 결과 테스트"""
        scan_result = ScanResult(
            server_id="empty-server",
            platform="linux",
        )

        assert scan_result.total == 0
        assert scan_result.passed == 0
        assert scan_result.failed == 0
        assert scan_result.manual == 0
        assert scan_result.score == 0.0

    def test_scan_result_score_calculation(self):
        """점수 계산 테스트"""
        # 50% PASS
        results = {
            f"U-{i:02d}": CheckResult(
                status=Status.PASS if i <= 5 else Status.FAIL,
                message="test",
                timestamp=datetime.now(),
            )
            for i in range(1, 11)
        }

        scan_result = ScanResult(server_id="test", platform="linux", results=results)

        assert scan_result.total == 10
        assert scan_result.score == pytest.approx(50.0, rel=0.1)


@pytest.mark.unit
class TestBaseScannerAdditional:
    """BaseScanner 추가 테스트"""

    def test_base_scanner_rules_property(self):
        """규칙 리스트 확인"""
        scanner = LinuxScanner(server_id="test", platform="linux")

        assert hasattr(scanner, "rules")
        assert isinstance(scanner.rules, list)
        assert len(scanner.rules) == 0  # 초기에는 비어있음

    def test_base_scanner_connection_state(self):
        """연결 상태 확인"""
        scanner = LinuxScanner(server_id="test", platform="linux")

        assert hasattr(scanner, "is_connected")
        # 초기에는 연결되지 않음
