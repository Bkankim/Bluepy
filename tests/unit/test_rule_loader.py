"""RuleLoader 단위 테스트

rule_loader 모듈의 함수들을 테스트합니다.
"""

import pytest
from pathlib import Path

from src.core.scanner.rule_loader import (
    load_yaml_file,
    convert_yaml_to_metadata,
    load_rules,
    RuleLoaderError,
)
from src.core.domain.models import Severity


@pytest.mark.unit
class TestLoadYamlFile:
    """load_yaml_file 함수 테스트"""

    def test_load_valid_yaml(self):
        """유효한 YAML 파일 로딩"""
        yaml_path = Path("config/rules/linux/U-01.yaml")
        data = load_yaml_file(yaml_path)

        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data
        assert data["id"] == "U-01"

    def test_load_all_yaml_files(self):
        """모든 YAML 파일 로딩 (73개)"""
        rules_dir = Path("config/rules/linux")
        count = 0

        for i in range(1, 74):
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            if yaml_file.exists():
                data = load_yaml_file(yaml_file)
                assert isinstance(data, dict)
                assert "id" in data
                count += 1

        assert count == 73


@pytest.mark.unit
class TestConvertYamlToMetadata:
    """convert_yaml_to_metadata 함수 테스트"""

    def test_convert_u01(self):
        """U-01 YAML을 RuleMetadata로 변환"""
        yaml_path = Path("config/rules/linux/U-01.yaml")
        yaml_data = load_yaml_file(yaml_path)

        rule = convert_yaml_to_metadata(yaml_data, yaml_path)

        assert rule.id == "U-01"
        assert rule.name == "root 계정 원격 접속 제한"
        assert rule.severity == Severity.HIGH
        assert rule.validator.startswith("validators.linux.check_u")

    def test_convert_multiple_rules(self):
        """여러 YAML 파일 변환"""
        rules_dir = Path("config/rules/linux")
        rules = []

        for i in [1, 4, 10, 18, 27, 36, 44, 50, 60, 70]:
            yaml_file = rules_dir / f"U-{i:02d}.yaml"
            yaml_data = load_yaml_file(yaml_file)
            rule = convert_yaml_to_metadata(yaml_data, yaml_file)
            rules.append(rule)

        assert len(rules) == 10
        assert all(r.id.startswith("U-") for r in rules)


@pytest.mark.unit
class TestLoadRules:
    """load_rules 함수 테스트"""

    def test_load_all_linux_rules(self):
        """Linux 규칙 전체 로딩"""
        rules = load_rules("config/rules", platform="linux")

        assert len(rules) == 73
        assert all(r.id.startswith("U-") for r in rules)
        assert all(r.validator.startswith("validators.linux.check_u") for r in rules)

    def test_rules_have_required_fields(self):
        """로딩된 규칙이 필수 필드를 갖는지 확인"""
        rules = load_rules("config/rules", platform="linux")

        for rule in rules[:10]:  # 처음 10개만 확인
            assert rule.id is not None
            assert rule.name is not None
            assert rule.category is not None
            assert rule.severity is not None
            assert rule.validator is not None

    def test_load_rules_invalid_path(self):
        """유효하지 않은 경로로 로딩 시 에러"""
        with pytest.raises(RuleLoaderError):
            load_rules("/invalid/path/that/does/not/exist", platform="linux")
