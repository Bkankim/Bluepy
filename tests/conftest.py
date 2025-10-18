"""pytest 설정 및 공통 fixtures

BluePy 2.0 테스트를 위한 pytest 설정 파일.
모든 테스트에서 사용 가능한 공통 fixtures를 정의합니다.

주요 fixtures:
- sample_check_result: CheckResult 샘플 객체
- sample_rule_metadata: RuleMetadata 샘플 객체
- sample_yaml_data: YAML 규칙 샘플 데이터 (dict)
- temp_yaml_file: 임시 YAML 파일 생성
- sample_severity_list: Severity enum 전체 목록
- sample_status_list: Status enum 전체 목록
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from src.core.domain.models import (
    CheckResult,
    Status,
    Severity,
    RuleMetadata,
    RemediationInfo,
)


# pytest 설정
def pytest_configure(config):
    """pytest 실행 전 설정"""
    config.addinivalue_line(
        "markers", "unit: 단위 테스트 (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트 (slower, may use external dependencies)"
    )
    config.addinivalue_line(
        "markers", "slow: 느린 테스트 (skip with -m 'not slow')"
    )


# ==================== Domain Model Fixtures ====================


@pytest.fixture
def sample_check_result() -> CheckResult:
    """CheckResult 샘플 객체 (PASS)"""
    return CheckResult(
        status=Status.PASS,
        message="Shadow 패스워드를 사용하고 있습니다",
        details={"file": "/etc/shadow", "exists": True},
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_check_result_fail() -> CheckResult:
    """CheckResult 샘플 객체 (FAIL)"""
    return CheckResult(
        status=Status.FAIL,
        message="패스워드 최소 길이가 8자 미만입니다",
        details={"current_length": 6, "required_length": 8},
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_check_result_manual() -> CheckResult:
    """CheckResult 샘플 객체 (MANUAL)"""
    return CheckResult(
        status=Status.MANUAL,
        message="불필요한 계정 존재 여부를 수동으로 확인하세요",
        details={"accounts": ["user1", "user2", "user3"]},
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_status_list() -> list[Status]:
    """Status enum 전체 목록"""
    return [Status.PASS, Status.FAIL, Status.MANUAL]


@pytest.fixture
def sample_severity_list() -> list[Severity]:
    """Severity enum 전체 목록"""
    return [Severity.HIGH, Severity.MID, Severity.LOW]


# ==================== RuleMetadata Fixtures ====================


@pytest.fixture
def sample_remediation_info() -> RemediationInfo:
    """RemediationInfo 샘플 객체 (auto=False)"""
    return RemediationInfo(
        auto=False,
        backup_files=None,
        commands=None,
        manual_steps=[
            "/etc/pam.d/login 파일 편집",
            "auth required pam_securetty.so 추가",
        ],
    )


@pytest.fixture
def sample_remediation_info_auto() -> RemediationInfo:
    """RemediationInfo 샘플 객체 (auto=True)"""
    return RemediationInfo(
        auto=True,
        backup_files=["/etc/pam.d/login"],
        commands=["echo 'auth required pam_securetty.so' >> /etc/pam.d/login"],
        manual_steps=None,
    )


@pytest.fixture
def sample_rule_metadata(sample_remediation_info) -> RuleMetadata:
    """RuleMetadata 샘플 객체 (U-01)"""
    return RuleMetadata(
        id="U-01",
        name="root 계정 원격 로그인 제한",
        category="계정관리",
        severity=Severity.HIGH,
        kisa_standard="U-01",
        description="root 계정의 원격 로그인을 제한하여 시스템 보안을 강화합니다.",
        commands=["cat /etc/pam.d/login", "cat /etc/securetty"],
        validator="validators.linux.check_u01_root_remote_login",
        expected_result="pam_securetty.so가 설정되어 있어야 함",
        remediation=sample_remediation_info,
    )


# ==================== YAML Data Fixtures ====================


@pytest.fixture
def sample_yaml_data() -> Dict[str, Any]:
    """YAML 규칙 샘플 데이터 (dict)

    U-01 규칙의 실제 YAML 구조를 반영한 샘플 데이터입니다.
    """
    return {
        "id": "U-01",
        "name": "root 계정 원격 접속 제한",
        "category": "계정관리",
        "severity": "high",
        "description": "root 계정 원격 접속 제한 취약점을 점검합니다.",
        "check": {"commands": ["cat /etc/inetd.conf"]},
        "validator": "validators.linux.check_u01",
        "remediation": {
            "auto": False,
            "backup_files": [],
            "commands": [],
        },
    }


@pytest.fixture
def sample_yaml_data_with_auto_remediation() -> Dict[str, Any]:
    """자동 수정 가능한 YAML 규칙 샘플 데이터"""
    return {
        "id": "U-18",
        "name": "패스워드 파일 보호",
        "category": "파일/디렉토리 관리",
        "severity": "high",
        "description": "/etc/passwd, /etc/shadow 파일의 권한을 점검합니다.",
        "check": {
            "commands": [
                "ls -l /etc/passwd",
                "ls -l /etc/shadow",
            ]
        },
        "validator": "validators.linux.check_u18",
        "remediation": {
            "auto": True,
            "backup_files": ["/etc/passwd", "/etc/shadow"],
            "commands": [
                "chmod 644 /etc/passwd",
                "chmod 400 /etc/shadow",
            ],
        },
    }


@pytest.fixture
def temp_yaml_file(tmp_path, sample_yaml_data) -> Path:
    """임시 YAML 파일 생성

    Args:
        tmp_path: pytest의 임시 디렉토리
        sample_yaml_data: YAML 샘플 데이터

    Returns:
        Path: 생성된 임시 YAML 파일 경로
    """
    yaml_file = tmp_path / "U-01.yaml"
    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_yaml_data, f, allow_unicode=True)
    return yaml_file


# ==================== Path Fixtures ====================


@pytest.fixture
def project_root() -> Path:
    """프로젝트 루트 디렉토리"""
    return Path(__file__).parent.parent


@pytest.fixture
def rules_dir(project_root) -> Path:
    """규칙 파일 디렉토리 (config/rules/linux)"""
    return project_root / "config" / "rules" / "linux"


@pytest.fixture
def test_fixtures_dir() -> Path:
    """테스트 fixtures 디렉토리"""
    return Path(__file__).parent / "fixtures"


# ==================== Validator Fixtures ====================


@pytest.fixture
def validator_function_names() -> list[str]:
    """73개 validator 함수 이름 목록

    validators.linux 모듈에 정의된 73개 check_u* 함수 이름.
    test_validators.py에서 함수 존재 확인에 사용됩니다.
    """
    return [f"check_u{i:02d}" for i in range(1, 74)]


@pytest.fixture
def validator_categories() -> Dict[str, list[int]]:
    """카테고리별 validator 함수 번호 매핑

    Returns:
        Dict[str, list[int]]: 카테고리명 -> U-번호 리스트

    Examples:
        >>> categories = validator_categories()
        >>> categories["account_management"]
        [1, 2, 3, 4, 5, 44, 45, 46, 47, 48, 49, 50, 51, 52, 73]
    """
    return {
        "account_management": [1, 2, 3, 4, 5, 44, 45, 46, 47, 48, 49, 50, 51, 52, 73],
        "file_management": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        "service_management": [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
        "log_management": [72],
        "patch_management": [72],
    }
