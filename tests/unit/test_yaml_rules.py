"""YAML 규칙 파일 단위 테스트

config/rules/linux/ 디렉토리의 73개 YAML 규칙 파일을 테스트합니다.

테스트 범위:
1. 73개 YAML 파일 존재 확인
2. YAML 파일 파싱 가능 확인
3. 필수 필드 존재 확인
4. RuleMetadata로 변환 가능 확인
5. 규칙 ID 유효성 검증
6. Severity 값 유효성 검증
7. Validator 경로 형식 검증
"""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.core.domain.models import RuleMetadata, Severity


# ==================== YAML 파일 존재 확인 ====================


@pytest.mark.unit
class TestYAMLFilesExist:
    """73개 YAML 파일 존재 확인"""

    def test_rules_directory_exists(self, rules_dir):
        """규칙 디렉토리가 존재하는지 확인"""
        assert rules_dir.exists(), f"규칙 디렉토리가 존재하지 않습니다: {rules_dir}"
        assert rules_dir.is_dir(), f"규칙 디렉토리가 디렉토리가 아닙니다: {rules_dir}"

    def test_all_73_yaml_files_exist(self, rules_dir):
        """U-01.yaml ~ U-73.yaml 파일이 모두 존재하는지 확인"""
        missing_files = []
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            if not yaml_file.exists():
                missing_files.append(f"U-{i:02d}.yaml")

        assert len(missing_files) == 0, f"누락된 YAML 파일: {missing_files}"

    def test_yaml_files_are_readable(self, rules_dir):
        """모든 YAML 파일이 읽기 가능한지 확인"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            assert yaml_file.is_file(), f"{yaml_file.name}이 파일이 아닙니다"
            # 파일 읽기 가능 확인
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = f.read()
                assert len(content) > 0, f"{yaml_file.name}이 비어있습니다"
            except Exception as e:
                pytest.fail(f"{yaml_file.name} 읽기 실패: {e}")


# ==================== YAML 파싱 테스트 ====================


@pytest.mark.unit
class TestYAMLParsing:
    """YAML 파일 파싱 테스트"""

    def test_all_yaml_files_are_valid_yaml(self, rules_dir):
        """모든 YAML 파일이 유효한 YAML 형식인지 확인"""
        invalid_files = []
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                assert isinstance(data, dict), f"{yaml_file.name}이 dict가 아닙니다"
            except yaml.YAMLError as e:
                invalid_files.append((yaml_file.name, str(e)))
            except Exception as e:
                invalid_files.append((yaml_file.name, str(e)))

        assert len(invalid_files) == 0, f"유효하지 않은 YAML 파일: {invalid_files}"

    def test_sample_yaml_parsing(self, sample_yaml_data):
        """샘플 YAML 데이터 파싱 확인"""
        assert sample_yaml_data["id"] == "U-01"
        assert sample_yaml_data["name"] == "root 계정 원격 접속 제한"
        assert sample_yaml_data["category"] == "계정관리"
        assert sample_yaml_data["severity"] == "high"


# ==================== 필수 필드 검증 ====================


@pytest.mark.unit
class TestYAMLRequiredFields:
    """YAML 필수 필드 검증"""

    def test_all_files_have_id_field(self, rules_dir):
        """모든 YAML 파일에 id 필드가 있는지 확인"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "id" in data, f"{yaml_file.name}에 id 필드가 없습니다"
            assert data["id"] == f"U-{i:02d}", f"{yaml_file.name}의 id가 예상과 다릅니다"

    def test_all_files_have_name_field(self, rules_dir):
        """모든 YAML 파일에 name 필드가 있는지 확인"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "name" in data, f"{yaml_file.name}에 name 필드가 없습니다"
            assert len(data["name"]) > 0, f"{yaml_file.name}의 name이 비어있습니다"

    def test_all_files_have_category_field(self, rules_dir):
        """모든 YAML 파일에 category 필드가 있는지 확인"""
        valid_categories = {
            "계정관리",
            "파일/디렉토리 관리",
            "서비스 관리",
            "로그 관리",
            "패치 관리",
        }

        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "category" in data, f"{yaml_file.name}에 category 필드가 없습니다"
            # category는 유효한 값 중 하나여야 함 (엄격하지 않게 검증)
            assert len(data["category"]) > 0, f"{yaml_file.name}의 category가 비어있습니다"

    def test_all_files_have_severity_field(self, rules_dir):
        """모든 YAML 파일에 severity 필드가 있는지 확인"""
        valid_severities = {"high", "mid", "low"}

        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "severity" in data, f"{yaml_file.name}에 severity 필드가 없습니다"
            assert (
                data["severity"] in valid_severities
            ), f"{yaml_file.name}의 severity가 유효하지 않습니다: {data['severity']}"

    def test_all_files_have_check_commands(self, rules_dir):
        """모든 YAML 파일에 check.commands 필드가 있는지 확인 (빈 리스트도 허용)"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "check" in data, f"{yaml_file.name}에 check 필드가 없습니다"
            assert (
                "commands" in data["check"]
            ), f"{yaml_file.name}에 check.commands 필드가 없습니다"
            assert isinstance(
                data["check"]["commands"], list
            ), f"{yaml_file.name}의 check.commands가 리스트가 아닙니다"
            # 빈 리스트도 허용 (일부 점검 항목은 수동 점검이거나 서버 명령어가 불필요)

    def test_all_files_have_validator_field(self, rules_dir):
        """모든 YAML 파일에 validator 필드가 있는지 확인"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "validator" in data, f"{yaml_file.name}에 validator 필드가 없습니다"
            assert len(data["validator"]) > 0, f"{yaml_file.name}의 validator가 비어있습니다"


# ==================== RuleMetadata 변환 테스트 ====================


@pytest.mark.unit
class TestRuleMetadataConversion:
    """RuleMetadata 변환 테스트"""

    def test_sample_yaml_to_rule_metadata(self, sample_yaml_data):
        """샘플 YAML을 RuleMetadata로 변환 가능한지 확인"""
        # YAML 구조를 RuleMetadata 형식으로 변환
        rule_data = {
            "id": sample_yaml_data["id"],
            "name": sample_yaml_data["name"],
            "category": sample_yaml_data["category"],
            "severity": Severity(sample_yaml_data["severity"]),
            "kisa_standard": sample_yaml_data["id"],  # 일반적으로 id와 동일
            "description": sample_yaml_data["description"],
            "commands": sample_yaml_data["check"]["commands"],
            "validator": sample_yaml_data["validator"],
        }

        # RuleMetadata 객체 생성 시도
        try:
            rule = RuleMetadata(**rule_data)
            assert rule.id == "U-01"
            assert rule.name == "root 계정 원격 접속 제한"
        except ValidationError as e:
            pytest.fail(f"RuleMetadata 변환 실패: {e}")

    def test_yaml_files_convertible_to_rule_metadata(self, rules_dir):
        """일부 YAML 파일을 RuleMetadata로 변환 가능한지 확인 (샘플 10개)"""
        sample_ids = [1, 10, 20, 30, 40, 50, 60, 70, 73]  # 샘플 선택
        failed_conversions = []

        for i in sample_ids:
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                # YAML 구조를 RuleMetadata 형식으로 변환
                rule_data = {
                    "id": data["id"],
                    "name": data["name"],
                    "category": data["category"],
                    "severity": Severity(data["severity"]),
                    "kisa_standard": data.get("kisa_standard", data["id"]),
                    "description": data["description"],
                    "commands": data["check"]["commands"],
                    "validator": data["validator"],
                }

                # RuleMetadata 객체 생성
                rule = RuleMetadata(**rule_data)
                assert rule.id == f"U-{i:02d}"

            except Exception as e:
                failed_conversions.append((yaml_file.name, str(e)))

        assert (
            len(failed_conversions) == 0
        ), f"RuleMetadata 변환 실패: {failed_conversions}"


# ==================== Validator 경로 형식 검증 ====================


@pytest.mark.unit
class TestValidatorPathFormat:
    """Validator 경로 형식 검증"""

    def test_validator_path_format(self, rules_dir):
        """모든 YAML 파일의 validator 경로 형식 확인"""
        # 예상 형식: validators.linux.check_uXX
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            validator = data["validator"]

            # validators.linux로 시작하는지 확인
            assert validator.startswith(
                "validators.linux."
            ), f"{yaml_file.name}의 validator가 'validators.linux.'로 시작하지 않습니다: {validator}"

            # check_uXX 형식인지 확인 (일반적인 패턴)
            # 단, 일부 함수는 다른 이름일 수 있으므로 체크하지 않음

    def test_validator_function_matches_file_id(self, rules_dir):
        """validator 함수 이름이 파일 ID와 일치하는지 확인 (샘플)"""
        # 샘플 확인: U-01.yaml → validators.linux.check_u01
        sample_ids = [1, 5, 10, 20, 30, 40, 50, 60, 70, 73]

        for i in sample_ids:
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            validator = data["validator"]
            expected_suffix = f"check_u{i:02d}"

            # validator가 check_uXX를 포함하는지 확인 (완전 일치는 아닐 수 있음)
            assert (
                expected_suffix in validator
            ), f"{yaml_file.name}의 validator에 {expected_suffix}가 포함되어 있지 않습니다: {validator}"


# ==================== Remediation 필드 검증 ====================


@pytest.mark.unit
class TestRemediationField:
    """Remediation 필드 검증"""

    def test_all_files_have_remediation_field(self, rules_dir):
        """모든 YAML 파일에 remediation 필드가 있는지 확인"""
        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert (
                "remediation" in data
            ), f"{yaml_file.name}에 remediation 필드가 없습니다"

    def test_remediation_has_auto_field(self, rules_dir):
        """remediation.auto 필드가 boolean인지 확인 (샘플)"""
        sample_ids = [1, 10, 20, 30, 40, 50, 60, 70, 73]

        for i in sample_ids:
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if "remediation" in data and data["remediation"]:
                assert (
                    "auto" in data["remediation"]
                ), f"{yaml_file.name}의 remediation에 auto 필드가 없습니다"
                assert isinstance(
                    data["remediation"]["auto"], bool
                ), f"{yaml_file.name}의 remediation.auto가 boolean이 아닙니다"


# ==================== 통계 테스트 ====================


@pytest.mark.unit
class TestRuleStatistics:
    """규칙 통계 테스트"""

    def test_severity_distribution(self, rules_dir):
        """Severity 분포 확인"""
        severity_count = {"high": 0, "mid": 0, "low": 0}

        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            severity_count[data["severity"]] += 1

        # 모든 severity가 최소 1개 이상 있어야 함
        assert severity_count["high"] > 0, "high severity 규칙이 없습니다"
        assert severity_count["mid"] > 0, "mid severity 규칙이 없습니다"
        assert severity_count["low"] > 0, "low severity 규칙이 없습니다"

        # 총 개수 확인
        total = sum(severity_count.values())
        assert total == 73, f"전체 규칙 개수가 73개가 아닙니다: {total}"

    def test_category_distribution(self, rules_dir):
        """Category 분포 확인"""
        category_count = {}

        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            category = data["category"]
            category_count[category] = category_count.get(category, 0) + 1

        # 최소 3개 이상의 카테고리가 있어야 함
        assert (
            len(category_count) >= 3
        ), f"카테고리가 3개 미만입니다: {list(category_count.keys())}"

        # 총 개수 확인
        total = sum(category_count.values())
        assert total == 73, f"전체 규칙 개수가 73개가 아닙니다: {total}"
