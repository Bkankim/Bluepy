"""Scanner와 Analyzer 통합 테스트

Scanner와 Analyzer 컴포넌트의 통합 테스트입니다.
실제 validator 함수 호출 및 결과 분석을 검증합니다.

테스트 범위:
1. Scanner + Validator 통합
2. Validator + Analyzer 통합
3. 실제 validator 함수 호출 검증
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.core.scanner.rule_loader import load_rules
from src.core.scanner.base_scanner import ScanResult
from src.core.analyzer.risk_calculator import (
    calculate_risk_statistics,
    evaluate_risk_level,
    get_category_distribution,
    get_severity_distribution,
)
from src.core.analyzer.validators import linux
from src.core.domain.models import CheckResult, Status, Severity


@pytest.mark.integration
class TestScannerValidatorIntegration:
    """Scanner와 Validator 통합 테스트"""

    @pytest.fixture
    def rules_dir(self):
        """YAML 규칙 디렉토리"""
        return Path("config/rules/linux")

    def test_load_rules_and_call_validators(self, rules_dir):
        """규칙 로딩 및 validator 함수 호출 통합 테스트"""
        # 1. 규칙 로딩
        rules = load_rules(str(rules_dir), platform="linux")

        assert len(rules) > 0

        # 2. 첫 번째 규칙의 validator 함수 호출
        first_rule = rules[0]  # U-01
        assert first_rule.id == "U-01"

        # 3. Validator 함수 동적 호출
        validator_path = first_rule.validator  # "validators.linux.check_u01"
        function_name = validator_path.split(".")[-1]  # "check_u01"

        # 4. 함수 존재 확인
        assert hasattr(linux, function_name)
        validator_func = getattr(linux, function_name)
        assert callable(validator_func)

        # 5. 실제 함수 호출 (테스트 데이터)
        test_outputs = ["auth required /lib/security/pam_securetty.so\n", "console\ntty1\n"]
        result = validator_func(test_outputs)

        # 6. 결과 검증
        assert isinstance(result, CheckResult)
        assert result.status in [Status.PASS, Status.FAIL, Status.MANUAL]

    def test_multiple_validators_execution(self, rules_dir):
        """여러 validator 함수 순차 실행"""
        rules = load_rules(str(rules_dir), platform="linux")[:10]  # 처음 10개 규칙

        results = []

        for rule in rules:
            function_name = rule.validator.split(".")[-1]
            if hasattr(linux, function_name):
                validator_func = getattr(linux, function_name)

                # 빈 출력으로 테스트 (대부분 MANUAL 반환 예상)
                result = validator_func([])
                results.append(result)

        # 모든 결과가 CheckResult 타입인지 확인
        assert len(results) == 10
        assert all(isinstance(r, CheckResult) for r in results)

    def test_validator_with_pass_case(self):
        """PASS 케이스 validator 실행"""
        # check_u04: Shadow 패스워드 사용 확인
        result = linux.check_u04(["root:x:0:0:root:/root:/bin/bash"])

        assert result.status == Status.PASS
        assert "shadow" in result.message.lower() or "안전" in result.message

    def test_validator_with_fail_case(self):
        """FAIL 케이스 validator 실행"""
        # check_u04: Shadow 패스워드 미사용
        result = linux.check_u04(["root:encrypted_password:0:0:root:/root:/bin/bash"])

        assert result.status == Status.FAIL
        assert "취약" in result.message or "shadow" in result.message.lower()

    def test_validator_with_manual_case(self):
        """MANUAL 케이스 validator 실행"""
        # check_u10: 불필요한 계정 제거 (항상 MANUAL)
        result = linux.check_u10(
            ["root:x:0:0:root:/root:/bin/bash\nbin:x:1:1:bin:/bin:/sbin/nologin"]
        )

        assert result.status == Status.MANUAL
        assert "수동" in result.message


@pytest.mark.integration
class TestValidatorAnalyzerIntegration:
    """Validator와 Analyzer 통합 테스트"""

    def test_analyze_validator_results(self):
        """Validator 결과 분석 통합 테스트"""
        # 1. 여러 validator 실행
        results = [
            linux.check_u04(["root:x:0:0:root:/root:/bin/bash"]),  # PASS
            linux.check_u04(["root:pwd:0:0:root:/root:/bin/bash"]),  # FAIL
            linux.check_u10(["root:x:0:0:..."]),  # MANUAL
        ]

        # 2. RiskCalculator로 분석
        risk_stats = calculate_risk_statistics(results)

        # 3. 결과 검증
        assert risk_stats.total_checks == 3
        assert risk_stats.passed >= 1
        assert risk_stats.failed >= 1
        assert risk_stats.manual >= 1

    def test_risk_level_evaluation_from_validators(self):
        """Validator 결과로부터 위험도 평가"""
        # 모두 PASS 시나리오
        all_pass = [linux.check_u04(["root:x:0:0:root:/root:/bin/bash"]) for _ in range(5)]
        risk_stats_safe = calculate_risk_statistics(all_pass)
        assert risk_stats_safe.risk_level == "안전"

        # 모두 FAIL 시나리오
        all_fail = [linux.check_u04(["root:pwd:0:0:root:/root:/bin/bash"]) for _ in range(5)]
        risk_stats_danger = calculate_risk_statistics(all_fail)
        assert risk_stats_danger.risk_level in ["위험", "높음", "중간"]

    def test_category_distribution_from_validators(self):
        """Validator 결과로부터 카테고리 분포 분석"""
        results = [
            linux.check_u01([]),  # account_management
            linux.check_u18([]),  # file_management
            linux.check_u36([]),  # service_management
        ]

        risk_stats = calculate_risk_statistics(results)
        category_dist = get_category_distribution(results)

        assert isinstance(category_dist, dict)
        # 카테고리 키가 존재하는지만 확인
        assert len(category_dist) > 0

    def test_severity_distribution_from_validators(self):
        """Validator 결과로부터 심각도 분포 분석"""
        results = [
            linux.check_u01([]),  # HIGH severity
            linux.check_u04([]),  # HIGH severity
            linux.check_u10([]),  # MEDIUM severity
        ]

        severity_dist = get_severity_distribution(results)

        assert isinstance(severity_dist, dict)
        assert all(k in severity_dist for k in ["high", "medium", "low", "info"])
        assert all(isinstance(v, int) for v in severity_dist.values())


@pytest.mark.integration
class TestScanResultAnalyzerIntegration:
    """ScanResult와 Analyzer 통합 테스트"""

    def test_scan_result_to_risk_statistics(self):
        """ScanResult에서 RiskStatistics로 변환"""
        # 1. CheckResult 생성
        results = [
            CheckResult(status=Status.PASS, message="통과", timestamp=datetime.now()),
            CheckResult(status=Status.PASS, message="통과", timestamp=datetime.now()),
            CheckResult(status=Status.FAIL, message="실패", timestamp=datetime.now()),
            CheckResult(status=Status.MANUAL, message="수동", timestamp=datetime.now()),
        ]

        # 2. ScanResult 생성
        scan_result = ScanResult(
            server="test.example.com", scan_date=datetime.now(), results=results
        )

        # 3. RiskStatistics 계산
        risk_stats = calculate_risk_statistics(results)

        # 4. 통계 일치 확인
        assert risk_stats.total_checks == scan_result.total
        assert risk_stats.passed == scan_result.passed
        assert risk_stats.failed == scan_result.failed
        assert risk_stats.manual == scan_result.manual

    def test_complete_scan_to_report_workflow(self):
        """완전한 스캔 → 분석 → 보고서 워크플로우"""
        # 1. 실제 validator 실행
        validator_results = [
            linux.check_u04(["root:x:0:0:root:/root:/bin/bash"]),  # PASS
            linux.check_u04(["user:x:1000:1000::/home/user:/bin/bash"]),  # PASS
            linux.check_u04(["admin:pwd:0:0::/root:/bin/bash"]),  # FAIL
        ]

        # 2. ScanResult 생성
        scan_result = ScanResult(
            server="integration-test.example.com",
            scan_date=datetime.now(),
            results=validator_results,
        )

        # 3. 통계 계산
        risk_stats = calculate_risk_statistics(validator_results)

        # 4. 검증
        assert scan_result.total == risk_stats.total_checks
        assert scan_result.score == risk_stats.pass_rate
        assert len(validator_results) == 3

        # 5. 위험도 평가
        risk_level = evaluate_risk_level(
            risk_stats.pass_rate, risk_stats.high_risk_count, risk_stats.medium_risk_count
        )
        assert risk_level in ["안전", "낮음", "중간", "높음", "위험"]
