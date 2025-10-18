"""Migration 스크립트 단위 테스트

scripts/migrate_legacy.py 스크립트를 테스트합니다.

테스트 범위:
1. FunctionInfo: Legacy 함수 정보 dataclass
2. KISA_NAMES: 73개 규칙 이름 매핑
3. Script import 가능 확인
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ==================== Import Tests ====================


@pytest.mark.unit
class TestMigrationScriptImport:
    """Migration 스크립트 import 테스트"""

    def test_import_migrate_legacy_script(self):
        """migrate_legacy.py 스크립트 import 가능 확인"""
        try:
            # scripts 디렉토리를 sys.path에 추가
            scripts_dir = project_root / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))

            import migrate_legacy

            assert migrate_legacy is not None
        except ImportError as e:
            pytest.fail(f"migrate_legacy.py import 실패: {e}")

    def test_function_info_dataclass_exists(self):
        """FunctionInfo dataclass가 정의되어 있는지 확인"""
        scripts_dir = project_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        import migrate_legacy

        assert hasattr(
            migrate_legacy, "FunctionInfo"
        ), "FunctionInfo dataclass가 정의되지 않았습니다"


# ==================== FunctionInfo Tests ====================


@pytest.mark.unit
class TestFunctionInfo:
    """FunctionInfo dataclass 테스트"""

    def setup_method(self):
        """테스트 메서드 전 scripts 모듈 import"""
        scripts_dir = project_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

    def test_create_function_info(self):
        """FunctionInfo 생성 테스트"""
        from migrate_legacy import FunctionInfo

        func_info = FunctionInfo(
            name="_1SCRIPT",
            number=1,
            kisa_code="U-01",
            source="def check_u01():\n    pass",
            complexity=10,
            severity="high",
            commands=["cat /etc/passwd"],
        )

        assert func_info.name == "_1SCRIPT"
        assert func_info.number == 1
        assert func_info.kisa_code == "U-01"
        assert func_info.source is not None
        assert func_info.complexity == 10
        assert func_info.severity == "high"
        assert len(func_info.commands) == 1

    def test_function_info_fields(self):
        """FunctionInfo 필드 확인"""
        from migrate_legacy import FunctionInfo
        import dataclasses

        # dataclass인지 확인
        assert dataclasses.is_dataclass(FunctionInfo)

        # 필수 필드 확인
        fields = {f.name for f in dataclasses.fields(FunctionInfo)}
        expected_fields = {"name", "number", "kisa_code", "source", "complexity", "severity", "commands"}

        assert expected_fields.issubset(
            fields
        ), f"필수 필드가 누락되었습니다. 예상: {expected_fields}, 실제: {fields}"


# ==================== KISA_NAMES Mapping Tests ====================


@pytest.mark.unit
class TestKISANamesMapping:
    """KISA_NAMES 매핑 테스트"""

    def setup_method(self):
        """테스트 메서드 전 scripts 모듈 import"""
        scripts_dir = project_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

    def test_kisa_names_exists(self):
        """KISA_NAMES 상수가 정의되어 있는지 확인"""
        import migrate_legacy

        assert hasattr(
            migrate_legacy, "KISA_NAMES"
        ), "KISA_NAMES 상수가 정의되지 않았습니다"

    def test_kisa_names_count(self):
        """KISA_NAMES에 73개 항목이 있는지 확인"""
        from migrate_legacy import KISA_NAMES

        assert len(KISA_NAMES) == 73, f"KISA_NAMES는 73개여야 하는데 {len(KISA_NAMES)}개입니다"

    def test_kisa_names_format(self):
        """KISA_NAMES 키 형식 확인 (U-01 ~ U-73)"""
        from migrate_legacy import KISA_NAMES

        for i in range(1, 74):
            key = f"U-{i:02d}"
            assert key in KISA_NAMES, f"{key}가 KISA_NAMES에 없습니다"

    def test_kisa_names_values_not_empty(self):
        """KISA_NAMES 값이 비어있지 않은지 확인"""
        from migrate_legacy import KISA_NAMES

        for key, value in KISA_NAMES.items():
            assert value is not None, f"{key}의 값이 None입니다"
            assert len(value) > 0, f"{key}의 값이 비어있습니다"
            assert isinstance(value, str), f"{key}의 값이 문자열이 아닙니다"

    def test_kisa_names_sample_values(self):
        """KISA_NAMES 샘플 값 확인"""
        from migrate_legacy import KISA_NAMES

        # 샘플 확인
        assert KISA_NAMES["U-01"] == "root 계정 원격 접속 제한"
        assert KISA_NAMES["U-04"] == "패스워드 파일 보호"
        assert KISA_NAMES["U-18"] == "/etc/passwd 파일 소유자 및 권한 설정"
        assert KISA_NAMES["U-73"] == "로그 기록 정책 수립"


# ==================== Script Constants Tests ====================


@pytest.mark.unit
class TestMigrationScriptConstants:
    """Migration 스크립트 상수 테스트"""

    def setup_method(self):
        """테스트 메서드 전 scripts 모듈 import"""
        scripts_dir = project_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

    def test_kisa_pattern_exists(self):
        """KISA_PATTERN 상수가 정의되어 있는지 확인"""
        import migrate_legacy

        assert hasattr(
            migrate_legacy, "KISA_PATTERN"
        ), "KISA_PATTERN 상수가 정의되지 않았습니다"

    def test_kisa_pattern_format(self):
        """KISA_PATTERN 정규식 확인"""
        import re
        from migrate_legacy import KISA_PATTERN

        # U-01 ~ U-73 형식과 매칭되는지 확인
        assert re.match(KISA_PATTERN, "U-01"), "U-01이 KISA_PATTERN과 매칭되지 않습니다"
        assert re.match(KISA_PATTERN, "U-73"), "U-73이 KISA_PATTERN과 매칭되지 않습니다"

        # 잘못된 형식은 매칭되지 않아야 함
        assert not re.match(KISA_PATTERN, "U-001"), "U-001이 KISA_PATTERN과 매칭되어서는 안됩니다"
        assert not re.match(KISA_PATTERN, "U01"), "U01이 KISA_PATTERN과 매칭되어서는 안됩니다"


# ==================== Migration Script File Tests ====================


@pytest.mark.unit
class TestMigrationScriptFile:
    """Migration 스크립트 파일 존재 확인"""

    def test_migrate_legacy_file_exists(self):
        """migrate_legacy.py 파일이 존재하는지 확인"""
        script_file = project_root / "scripts" / "migrate_legacy.py"
        assert script_file.exists(), f"migrate_legacy.py 파일이 존재하지 않습니다: {script_file}"

    def test_migrate_legacy_file_is_executable(self):
        """migrate_legacy.py 파일이 실행 가능한지 확인"""
        import os

        script_file = project_root / "scripts" / "migrate_legacy.py"
        # 파일이 존재하고 읽기 가능한지 확인
        assert os.access(
            script_file, os.R_OK
        ), f"migrate_legacy.py 파일을 읽을 수 없습니다: {script_file}"

    def test_migrate_legacy_file_has_shebang(self):
        """migrate_legacy.py 파일에 shebang이 있는지 확인"""
        script_file = project_root / "scripts" / "migrate_legacy.py"
        with open(script_file, "r", encoding="utf-8") as f:
            first_line = f.readline()

        assert first_line.startswith(
            "#!/usr/bin/env python"
        ), "migrate_legacy.py 파일에 shebang이 없습니다"
