"""도메인 모델 단위 테스트

src/core/domain/models.py의 모든 도메인 모델을 테스트합니다.

테스트 대상:
- CheckResult: 점검 결과 dataclass
- Status: 점검 결과 상태 enum
- Severity: 취약점 심각도 enum
- RemediationInfo: 자동 수정 정보 BaseModel
- RuleMetadata: 점검 규칙 메타데이터 BaseModel
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.core.domain.models import (
    CheckResult,
    Status,
    Severity,
    RemediationInfo,
    RuleMetadata,
)


# ==================== CheckResult Tests ====================


@pytest.mark.unit
class TestCheckResult:
    """CheckResult 테스트"""

    def test_create_pass_result(self, sample_check_result):
        """PASS 상태 CheckResult 생성 테스트"""
        assert sample_check_result.status == Status.PASS
        assert sample_check_result.message == "Shadow 패스워드를 사용하고 있습니다"
        assert sample_check_result.details == {"file": "/etc/shadow", "exists": True}
        assert isinstance(sample_check_result.timestamp, datetime)

    def test_create_fail_result(self, sample_check_result_fail):
        """FAIL 상태 CheckResult 생성 테스트"""
        assert sample_check_result_fail.status == Status.FAIL
        assert "패스워드 최소 길이" in sample_check_result_fail.message
        assert sample_check_result_fail.details["current_length"] == 6

    def test_create_manual_result(self, sample_check_result_manual):
        """MANUAL 상태 CheckResult 생성 테스트"""
        assert sample_check_result_manual.status == Status.MANUAL
        assert "수동으로 확인" in sample_check_result_manual.message
        assert len(sample_check_result_manual.details["accounts"]) == 3

    def test_is_passed_method(self, sample_check_result):
        """is_passed() 메서드 테스트"""
        assert sample_check_result.is_passed() is True
        assert sample_check_result.is_failed() is False
        assert sample_check_result.is_manual() is False

    def test_is_failed_method(self, sample_check_result_fail):
        """is_failed() 메서드 테스트"""
        assert sample_check_result_fail.is_passed() is False
        assert sample_check_result_fail.is_failed() is True
        assert sample_check_result_fail.is_manual() is False

    def test_is_manual_method(self, sample_check_result_manual):
        """is_manual() 메서드 테스트"""
        assert sample_check_result_manual.is_passed() is False
        assert sample_check_result_manual.is_failed() is False
        assert sample_check_result_manual.is_manual() is True

    def test_timestamp_auto_generation(self):
        """timestamp 자동 생성 테스트"""
        result1 = CheckResult(status=Status.PASS, message="Test")
        result2 = CheckResult(status=Status.PASS, message="Test")

        # 두 객체의 timestamp는 거의 동시에 생성되지만 다를 수 있음
        assert isinstance(result1.timestamp, datetime)
        assert isinstance(result2.timestamp, datetime)

    def test_details_optional(self):
        """details 필드 optional 테스트"""
        result = CheckResult(status=Status.PASS, message="Test")
        assert result.details is None

    def test_details_with_various_types(self):
        """details 필드 다양한 타입 테스트"""
        # dict with various value types
        result = CheckResult(
            status=Status.FAIL,
            message="Test",
            details={
                "string": "value",
                "int": 123,
                "list": [1, 2, 3],
                "nested_dict": {"key": "value"},
                "bool": True,
            },
        )
        assert result.details["string"] == "value"
        assert result.details["int"] == 123
        assert result.details["list"] == [1, 2, 3]
        assert result.details["nested_dict"]["key"] == "value"
        assert result.details["bool"] is True


# ==================== Status Enum Tests ====================


@pytest.mark.unit
class TestStatus:
    """Status enum 테스트"""

    def test_all_status_values_exist(self, sample_status_list):
        """모든 Status 값 존재 확인"""
        assert Status.PASS in sample_status_list
        assert Status.FAIL in sample_status_list
        assert Status.MANUAL in sample_status_list
        assert len(sample_status_list) == 3

    def test_status_string_values(self):
        """Status enum의 문자열 값 테스트"""
        assert Status.PASS.value == "PASS"
        assert Status.FAIL.value == "FAIL"
        assert Status.MANUAL.value == "MANUAL"

    def test_status_equality(self):
        """Status enum 동등성 테스트"""
        assert Status.PASS == Status.PASS
        assert Status.PASS != Status.FAIL
        assert Status.FAIL != Status.MANUAL

    def test_status_from_string(self):
        """문자열로부터 Status enum 생성 테스트"""
        assert Status("PASS") == Status.PASS
        assert Status("FAIL") == Status.FAIL
        assert Status("MANUAL") == Status.MANUAL


# ==================== Severity Enum Tests ====================


@pytest.mark.unit
class TestSeverity:
    """Severity enum 테스트"""

    def test_all_severity_values_exist(self, sample_severity_list):
        """모든 Severity 값 존재 확인"""
        assert Severity.HIGH in sample_severity_list
        assert Severity.MID in sample_severity_list
        assert Severity.LOW in sample_severity_list
        assert len(sample_severity_list) == 3

    def test_severity_string_values(self):
        """Severity enum의 문자열 값 테스트"""
        assert Severity.HIGH.value == "high"
        assert Severity.MID.value == "mid"
        assert Severity.LOW.value == "low"

    def test_severity_equality(self):
        """Severity enum 동등성 테스트"""
        assert Severity.HIGH == Severity.HIGH
        assert Severity.HIGH != Severity.MID
        assert Severity.MID != Severity.LOW

    def test_severity_from_string(self):
        """문자열로부터 Severity enum 생성 테스트"""
        assert Severity("high") == Severity.HIGH
        assert Severity("mid") == Severity.MID
        assert Severity("low") == Severity.LOW


# ==================== RemediationInfo Tests ====================


@pytest.mark.unit
class TestRemediationInfo:
    """RemediationInfo 테스트"""

    def test_create_manual_remediation(self, sample_remediation_info):
        """수동 수정 정보 생성 테스트"""
        assert sample_remediation_info.auto is False
        assert sample_remediation_info.backup_files is None
        assert sample_remediation_info.commands is None
        assert len(sample_remediation_info.manual_steps) == 2

    def test_create_auto_remediation(self, sample_remediation_info_auto):
        """자동 수정 정보 생성 테스트"""
        assert sample_remediation_info_auto.auto is True
        assert len(sample_remediation_info_auto.backup_files) == 1
        assert len(sample_remediation_info_auto.commands) == 1
        assert sample_remediation_info_auto.manual_steps is None

    def test_remediation_info_frozen(self, sample_remediation_info):
        """RemediationInfo immutable 테스트 (frozen=True)"""
        with pytest.raises((ValidationError, AttributeError)):
            sample_remediation_info.auto = True

    def test_remediation_info_default_values(self):
        """RemediationInfo 기본값 테스트"""
        remediation = RemediationInfo()
        assert remediation.auto is False
        assert remediation.backup_files is None
        assert remediation.commands is None
        assert remediation.manual_steps is None


# ==================== RuleMetadata Tests ====================


@pytest.mark.unit
class TestRuleMetadata:
    """RuleMetadata 테스트"""

    def test_create_rule_metadata(self, sample_rule_metadata):
        """RuleMetadata 정상 생성 테스트"""
        assert sample_rule_metadata.id == "U-01"
        assert sample_rule_metadata.name == "root 계정 원격 로그인 제한"
        assert sample_rule_metadata.category == "계정관리"
        assert sample_rule_metadata.severity == Severity.HIGH
        assert sample_rule_metadata.kisa_standard == "U-01"
        assert len(sample_rule_metadata.commands) == 2
        assert sample_rule_metadata.validator == "validators.linux.check_u01_root_remote_login"
        assert sample_rule_metadata.remediation is not None

    def test_rule_metadata_id_pattern_validation(self):
        """RuleMetadata id 패턴 validation 테스트"""
        # 정상 패턴: U-01, W-01, M-01
        valid_ids = ["U-01", "U-73", "W-01", "W-50", "M-01", "M-50"]
        for rule_id in valid_ids:
            rule = RuleMetadata(
                id=rule_id,
                name="Test Rule",
                category="테스트",
                severity=Severity.HIGH,
                kisa_standard="U-01",
                description="Test",
                commands=["echo test"],
                validator="validators.linux.check_u01_test",
            )
            assert rule.id == rule_id

        # 비정상 패턴
        invalid_ids = ["U-001", "U01", "X-01", "U-1", "u-01"]
        for rule_id in invalid_ids:
            with pytest.raises(ValidationError):
                RuleMetadata(
                    id=rule_id,
                    name="Test Rule",
                    category="테스트",
                    severity=Severity.HIGH,
                    kisa_standard="U-01",
                    description="Test",
                    commands=["echo test"],
                    validator="validators.linux.check_u01_test",
                )

    def test_rule_metadata_validator_pattern_validation(self):
        """RuleMetadata validator 패턴 validation 테스트"""
        # 정상 패턴: validators.(linux|macos|windows).check_[a-z]\d{2}_\w+
        valid_validators = [
            "validators.linux.check_u01_test",
            "validators.macos.check_m01_test",
            "validators.windows.check_w01_test",
            "validators.linux.check_u73_long_name_with_underscores",
        ]
        for validator in valid_validators:
            rule = RuleMetadata(
                id="U-01",
                name="Test Rule",
                category="테스트",
                severity=Severity.HIGH,
                kisa_standard="U-01",
                description="Test",
                commands=["echo test"],
                validator=validator,
            )
            assert rule.validator == validator

        # 비정상 패턴
        invalid_validators = [
            "validators.invalid.check_u01_test",  # invalid platform
            "check_u01_test",  # missing prefix
            "validators.linux.u01_test",  # missing check_ prefix
            "validators.linux.check_U01_test",  # uppercase U (should be lowercase)
        ]
        for validator in invalid_validators:
            with pytest.raises(ValidationError):
                RuleMetadata(
                    id="U-01",
                    name="Test Rule",
                    category="테스트",
                    severity=Severity.HIGH,
                    kisa_standard="U-01",
                    description="Test",
                    commands=["echo test"],
                    validator=validator,
                )

    def test_rule_metadata_name_length_validation(self):
        """RuleMetadata name 길이 validation 테스트"""
        # 빈 문자열 불가
        with pytest.raises(ValidationError):
            RuleMetadata(
                id="U-01",
                name="",
                category="테스트",
                severity=Severity.HIGH,
                kisa_standard="U-01",
                description="Test",
                commands=["echo test"],
                validator="validators.linux.check_u01_test",
            )

        # 200자 초과 불가
        with pytest.raises(ValidationError):
            RuleMetadata(
                id="U-01",
                name="a" * 201,
                category="테스트",
                severity=Severity.HIGH,
                kisa_standard="U-01",
                description="Test",
                commands=["echo test"],
                validator="validators.linux.check_u01_test",
            )

        # 1-200자는 정상
        rule = RuleMetadata(
            id="U-01",
            name="a" * 200,
            category="테스트",
            severity=Severity.HIGH,
            kisa_standard="U-01",
            description="Test",
            commands=["echo test"],
            validator="validators.linux.check_u01_test",
        )
        assert len(rule.name) == 200

    def test_rule_metadata_commands_not_empty(self):
        """RuleMetadata commands 비어있지 않음 검증"""
        # 빈 리스트 불가
        with pytest.raises(ValidationError):
            RuleMetadata(
                id="U-01",
                name="Test Rule",
                category="테스트",
                severity=Severity.HIGH,
                kisa_standard="U-01",
                description="Test",
                commands=[],
                validator="validators.linux.check_u01_test",
            )

        # 최소 1개 이상
        rule = RuleMetadata(
            id="U-01",
            name="Test Rule",
            category="테스트",
            severity=Severity.HIGH,
            kisa_standard="U-01",
            description="Test",
            commands=["echo test"],
            validator="validators.linux.check_u01_test",
        )
        assert len(rule.commands) == 1

    def test_rule_metadata_frozen(self, sample_rule_metadata):
        """RuleMetadata immutable 테스트 (frozen=True)"""
        with pytest.raises((ValidationError, AttributeError)):
            sample_rule_metadata.name = "Modified Name"

    def test_rule_metadata_optional_fields(self):
        """RuleMetadata optional 필드 테스트"""
        # expected_result, remediation은 optional
        rule = RuleMetadata(
            id="U-01",
            name="Test Rule",
            category="테스트",
            severity=Severity.HIGH,
            kisa_standard="U-01",
            description="Test",
            commands=["echo test"],
            validator="validators.linux.check_u01_test",
        )
        assert rule.expected_result is None
        assert rule.remediation is None
