"""Analyzer 모듈 단위 테스트

src/core/analyzer/risk_calculator.py를 테스트합니다.

테스트 범위:
1. RiskStatistics: 위험도 통계 dataclass
2. calculate_risk_statistics: 위험도 통계 계산
3. evaluate_risk_level: 위험 수준 평가
4. get_category_distribution: 카테고리별 분포
5. get_severity_distribution: 심각도별 분포
"""

import pytest
from datetime import datetime

from src.core.domain.models import CheckResult, Status
from src.core.scanner.base_scanner import ScanResult
from src.core.analyzer.risk_calculator import (
    RiskStatistics,
    calculate_risk_statistics,
    evaluate_risk_level,
    get_category_distribution,
    get_severity_distribution,
)


# ==================== Helper Functions ====================


def create_test_scan_result(
    results: list,
    server_id: str = "test-server",
    platform: str = "linux"
) -> ScanResult:
    """테스트용 ScanResult 생성 헬퍼

    CheckResult 리스트를 ScanResult로 래핑합니다.

    Args:
        results: CheckResult 리스트
        server_id: 서버 ID
        platform: 플랫폼

    Returns:
        results가 담긴 ScanResult 객체
    """
    return ScanResult(
        server_id=server_id,
        platform=platform,
        scan_time=datetime.now(),
        results={f"U-{i:02d}": r for i, r in enumerate(results, 1)}
    )


# ==================== RiskStatistics Tests ====================


@pytest.mark.unit
class TestRiskStatistics:
    """RiskStatistics dataclass 테스트"""

    def test_create_risk_statistics(self):
        """RiskStatistics 생성 테스트"""
        stats = RiskStatistics(
            total=10,
            passed=6,
            failed=3,
            manual=1,
            score=65.0,
            high_risk=1,
            mid_risk=1,
            low_risk=1,
            pass_rate=60.0,
            fail_rate=30.0,
            risk_level="medium",
        )

        assert stats.total == 10
        assert stats.passed == 6
        assert stats.failed == 3
        assert stats.manual == 1
        assert stats.score == 65.0
        assert stats.high_risk == 1
        assert stats.mid_risk == 1
        assert stats.low_risk == 1
        assert stats.pass_rate == 60.0
        assert stats.fail_rate == 30.0
        assert stats.risk_level == "medium"


# ==================== calculate_risk_statistics Tests ====================


@pytest.mark.unit
class TestCalculateRiskStatistics:
    """calculate_risk_statistics 함수 테스트"""

    def test_calculate_all_passed(self):
        """모두 양호한 경우"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.PASS, message="Test"),
            "U-03": CheckResult(status=Status.PASS, message="Test"),
        }

        stats = calculate_risk_statistics(scan_result)

        assert stats.total == 3
        assert stats.passed == 3
        assert stats.failed == 0
        assert stats.manual == 0
        assert stats.score == 100.0
        assert stats.pass_rate == 100.0
        assert stats.fail_rate == 0.0
        assert stats.risk_level == "safe"

    def test_calculate_all_failed(self):
        """모두 취약한 경우"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.FAIL, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.FAIL, message="Test"),
        }

        stats = calculate_risk_statistics(scan_result)

        assert stats.total == 3
        assert stats.passed == 0
        assert stats.failed == 3
        assert stats.manual == 0
        assert stats.score == 0.0
        assert stats.pass_rate == 0.0
        assert stats.fail_rate == 100.0
        assert stats.risk_level == "critical"

    def test_calculate_mixed_results(self):
        """혼합된 결과"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.PASS, message="Test"),
            "U-03": CheckResult(status=Status.FAIL, message="Test"),
            "U-04": CheckResult(status=Status.FAIL, message="Test"),
            "U-05": CheckResult(status=Status.MANUAL, message="Test"),
        }

        stats = calculate_risk_statistics(scan_result)

        assert stats.total == 5
        assert stats.passed == 2
        assert stats.failed == 2
        assert stats.manual == 1
        # (2 PASS + 0.5 MANUAL) / 5 * 100 = 50.0
        assert stats.score == 50.0
        assert stats.pass_rate == 40.0  # 2/5 * 100
        assert stats.fail_rate == 40.0  # 2/5 * 100

    def test_calculate_empty_results(self):
        """결과가 없는 경우"""
        scan_result = ScanResult(server_id="server-001", platform="linux")

        stats = calculate_risk_statistics(scan_result)

        assert stats.total == 0
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.manual == 0
        assert stats.score == 0.0
        assert stats.pass_rate == 0.0
        assert stats.fail_rate == 0.0

    def test_calculate_high_risk_distribution(self):
        """HIGH 심각도 취약점 분포 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        # 9개 실패 항목
        for i in range(1, 10):
            scan_result.results[f"U-{i:02d}"] = CheckResult(status=Status.FAIL, message="Test")

        stats = calculate_risk_statistics(scan_result)

        # 9개를 3개씩 분배
        assert stats.high_risk == 3
        assert stats.mid_risk == 3
        assert stats.low_risk == 3


# ==================== evaluate_risk_level Tests ====================


@pytest.mark.unit
class TestEvaluateRiskLevel:
    """evaluate_risk_level 함수 테스트"""

    def test_critical_level_low_score(self):
        """치명적 수준 (낮은 점수)"""
        risk_level = evaluate_risk_level(score=30.0, high_risk_count=0)
        assert risk_level == "critical"

    def test_critical_level_high_risk_count(self):
        """치명적 수준 (HIGH 취약점 많음)"""
        risk_level = evaluate_risk_level(score=80.0, high_risk_count=10)
        assert risk_level == "critical"

    def test_high_level_low_score(self):
        """높음 수준 (낮은 점수)"""
        risk_level = evaluate_risk_level(score=50.0, high_risk_count=0)
        assert risk_level == "high"

    def test_high_level_high_risk_count(self):
        """높음 수준 (HIGH 취약점 일부)"""
        risk_level = evaluate_risk_level(score=70.0, high_risk_count=5)
        assert risk_level == "high"

    def test_medium_level(self):
        """중간 수준"""
        risk_level = evaluate_risk_level(score=70.0, high_risk_count=0)
        assert risk_level == "medium"

    def test_low_level(self):
        """낮음 수준"""
        risk_level = evaluate_risk_level(score=85.0, high_risk_count=0)
        assert risk_level == "low"

    def test_safe_level(self):
        """안전 수준"""
        risk_level = evaluate_risk_level(score=95.0, high_risk_count=0)
        assert risk_level == "safe"

    def test_boundary_critical_high(self):
        """경계값 테스트: critical/high (score=40)"""
        risk_level_39 = evaluate_risk_level(score=39.9, high_risk_count=0)
        risk_level_40 = evaluate_risk_level(score=40.0, high_risk_count=0)

        assert risk_level_39 == "critical"
        assert risk_level_40 == "high"

    def test_boundary_high_medium(self):
        """경계값 테스트: high/medium (score=60)"""
        risk_level_59 = evaluate_risk_level(score=59.9, high_risk_count=0)
        risk_level_60 = evaluate_risk_level(score=60.0, high_risk_count=0)

        assert risk_level_59 == "high"
        assert risk_level_60 == "medium"

    def test_boundary_medium_low(self):
        """경계값 테스트: medium/low (score=80)"""
        risk_level_79 = evaluate_risk_level(score=79.9, high_risk_count=0)
        risk_level_80 = evaluate_risk_level(score=80.0, high_risk_count=0)

        assert risk_level_79 == "medium"
        assert risk_level_80 == "low"

    def test_boundary_low_safe(self):
        """경계값 테스트: low/safe (score=90)"""
        risk_level_89 = evaluate_risk_level(score=89.9, high_risk_count=0)
        risk_level_90 = evaluate_risk_level(score=90.0, high_risk_count=0)

        assert risk_level_89 == "low"
        assert risk_level_90 == "safe"


# ==================== get_category_distribution Tests ====================


@pytest.mark.unit
class TestGetCategoryDistribution:
    """get_category_distribution 함수 테스트"""

    def test_category_distribution_returns_dict(self):
        """카테고리 분포가 dict를 반환하는지 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.MANUAL, message="Test"),
        }

        distribution = get_category_distribution(scan_result)

        assert isinstance(distribution, dict)
        assert len(distribution) > 0

    def test_category_distribution_structure(self):
        """카테고리 분포 구조 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.MANUAL, message="Test"),
        }

        distribution = get_category_distribution(scan_result)

        # 각 카테고리는 passed, failed, manual 키를 가져야 함
        for category, stats in distribution.items():
            assert "passed" in stats
            assert "failed" in stats
            assert "manual" in stats
            assert isinstance(stats["passed"], int)
            assert isinstance(stats["failed"], int)
            assert isinstance(stats["manual"], int)


# ==================== get_severity_distribution Tests ====================


@pytest.mark.unit
class TestGetSeverityDistribution:
    """get_severity_distribution 함수 테스트"""

    def test_severity_distribution_returns_dict(self):
        """심각도 분포가 dict를 반환하는지 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.FAIL, message="Test"),
            "U-02": CheckResult(status=Status.FAIL, message="Test"),
            "U-03": CheckResult(status=Status.FAIL, message="Test"),
        }

        distribution = get_severity_distribution(scan_result)

        assert isinstance(distribution, dict)
        assert "high" in distribution
        assert "mid" in distribution
        assert "low" in distribution

    def test_severity_distribution_values(self):
        """심각도 분포 값 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        # 9개 실패 항목
        for i in range(1, 10):
            scan_result.results[f"U-{i:02d}"] = CheckResult(status=Status.FAIL, message="Test")

        distribution = get_severity_distribution(scan_result)

        # 9개를 3개씩 분배
        assert distribution["high"] == 3
        assert distribution["mid"] == 3
        assert distribution["low"] == 3

    def test_severity_distribution_all_integers(self):
        """심각도 분포가 모두 정수인지 확인"""
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.FAIL, message="Test"),
        }

        distribution = get_severity_distribution(scan_result)

        assert isinstance(distribution["high"], int)
        assert isinstance(distribution["mid"], int)
        assert isinstance(distribution["low"], int)


# ==================== 통합 테스트 ====================


@pytest.mark.unit
class TestRiskCalculatorIntegration:
    """Risk Calculator 통합 테스트"""

    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        # ScanResult 생성
        scan_result = ScanResult(server_id="server-001", platform="linux")
        scan_result.results = {
            "U-01": CheckResult(status=Status.PASS, message="Test"),
            "U-02": CheckResult(status=Status.PASS, message="Test"),
            "U-03": CheckResult(status=Status.PASS, message="Test"),
            "U-04": CheckResult(status=Status.FAIL, message="Test"),
            "U-05": CheckResult(status=Status.FAIL, message="Test"),
            "U-06": CheckResult(status=Status.FAIL, message="Test"),
            "U-07": CheckResult(status=Status.FAIL, message="Test"),
            "U-08": CheckResult(status=Status.FAIL, message="Test"),
            "U-09": CheckResult(status=Status.MANUAL, message="Test"),
            "U-10": CheckResult(status=Status.MANUAL, message="Test"),
        }

        # 통계 계산
        stats = calculate_risk_statistics(scan_result)

        # 검증
        assert stats.total == 10
        assert stats.passed == 3
        assert stats.failed == 5
        assert stats.manual == 2
        # (3 PASS + 2 * 0.5 MANUAL) / 10 * 100 = 40.0
        assert stats.score == 40.0

        # 심각도 분포
        severity_dist = get_severity_distribution(scan_result)
        assert severity_dist["high"] + severity_dist["mid"] + severity_dist["low"] == 5

        # 카테고리 분포
        category_dist = get_category_distribution(scan_result)
        assert isinstance(category_dist, dict)


@pytest.mark.unit
class TestRiskCalculatorAdditional:
    """RiskCalculator 추가 테스트 (커버리지 증가)"""

    def test_calculate_with_only_manual(self):
        """MANUAL만 있는 경우"""
        results = [
            CheckResult(status=Status.MANUAL, message=f"수동 {i}", timestamp=datetime.now())
            for i in range(10)
        ]

        scan_result = create_test_scan_result(results)
        stats = calculate_risk_statistics(scan_result)

        assert stats.total == 10
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.manual == 10
        assert stats.pass_rate == 0.0

    def test_evaluate_risk_level_edge_cases(self):
        """위험도 평가 경계값 테스트"""
        # 정확히 80% - low
        assert evaluate_risk_level(80.0, 0) == "low"

        # 정확히 60% - medium
        level_60 = evaluate_risk_level(60.0, 0)
        assert level_60 == "medium"

        # 정확히 40% - high
        level_40 = evaluate_risk_level(40.0, 0)
        assert level_40 == "high"

        # 정확히 20% - critical
        level_20 = evaluate_risk_level(20.0, 0)
        assert level_20 == "critical"

    def test_category_distribution_coverage(self):
        """카테고리 분포 커버리지 테스트"""
        results = [
            CheckResult(status=Status.PASS, message="test", timestamp=datetime.now())
            for _ in range(5)
        ]

        scan_result = create_test_scan_result(results)
        dist = get_category_distribution(scan_result)

        assert isinstance(dist, dict)
        # 빈 카테고리도 0으로 표시되어야 함

    def test_severity_distribution_all_types(self):
        """모든 심각도 타입 테스트"""
        results = [
            CheckResult(status=Status.FAIL, message="test", timestamp=datetime.now())
            for _ in range(9)
        ]

        scan_result = create_test_scan_result(results)
        dist = get_severity_distribution(scan_result)

        assert "high" in dist
        assert "mid" in dist
        assert "low" in dist
        assert all(isinstance(v, int) for v in dist.values())

    def test_risk_statistics_with_high_risk_counts(self):
        """고위험 항목 수 테스트"""
        results = [
            CheckResult(status=Status.FAIL, message="critical", timestamp=datetime.now())
            for _ in range(20)
        ]

        scan_result = create_test_scan_result(results)
        stats = calculate_risk_statistics(scan_result)

        assert stats.failed == 20
        assert stats.total == 20
        assert stats.score == 0.0
        # score=0.0 → critical
        assert stats.risk_level == "critical"
