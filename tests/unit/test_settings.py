"""설정 모듈 테스트

src/infrastructure/config/settings.py 모듈의 단위 테스트입니다.
"""

import json
import tempfile
from pathlib import Path


from src.infrastructure.config.settings import (
    get_default_settings,
    load_settings,
    save_settings,
    get_setting,
    set_setting,
)


class TestGetDefaultSettings:
    """기본 설정 반환 테스트"""

    def test_returns_dict(self):
        """딕셔너리를 반환하는지 확인"""
        settings = get_default_settings()
        assert isinstance(settings, dict)

    def test_has_required_keys(self):
        """필수 키가 있는지 확인"""
        settings = get_default_settings()
        assert "appearance" in settings
        assert "logging" in settings
        assert "language" in settings
        assert "backup" in settings

    def test_appearance_has_theme(self):
        """appearance.theme 키가 있는지 확인"""
        settings = get_default_settings()
        assert "theme" in settings["appearance"]
        assert settings["appearance"]["theme"] in ["dark", "light"]

    def test_logging_has_level(self):
        """logging.level 키가 있는지 확인"""
        settings = get_default_settings()
        assert "level" in settings["logging"]
        assert settings["logging"]["level"] in ["DEBUG", "INFO", "WARNING", "ERROR"]

    def test_returns_copy(self):
        """복사본을 반환하는지 확인 (원본 보호)"""
        settings1 = get_default_settings()
        settings2 = get_default_settings()

        settings1["appearance"]["theme"] = "modified"

        # settings2는 영향받지 않아야 함
        assert settings2["appearance"]["theme"] != "modified"


class TestLoadSettings:
    """설정 로드 테스트"""

    def test_load_nonexistent_file_returns_default(self):
        """존재하지 않는 파일을 로드하면 기본값 반환"""
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_file = Path(tmpdir) / "nonexistent.json"
            settings = load_settings(nonexistent_file)

            assert settings == get_default_settings()

    def test_load_valid_file(self):
        """유효한 JSON 파일 로드"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            # 테스트 데이터 작성
            test_settings = {
                "appearance": {"theme": "light"},
                "logging": {"level": "DEBUG"},
                "language": {"locale": "en_US"},
                "backup": {"directory": "/custom/backup"},
            }

            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(test_settings, f)

            # 로드
            loaded = load_settings(settings_file)

            assert loaded["appearance"]["theme"] == "light"
            assert loaded["logging"]["level"] == "DEBUG"
            assert loaded["language"]["locale"] == "en_US"
            assert loaded["backup"]["directory"] == "/custom/backup"

    def test_load_partial_settings_merges_with_default(self):
        """일부 키만 있는 설정 파일은 기본값과 병합"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            # theme만 있는 부분 설정
            partial_settings = {"appearance": {"theme": "light"}}

            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(partial_settings, f)

            # 로드
            loaded = load_settings(settings_file)

            # theme는 로드된 값
            assert loaded["appearance"]["theme"] == "light"

            # 나머지는 기본값
            assert "logging" in loaded
            assert "language" in loaded
            assert "backup" in loaded

    def test_load_invalid_json_returns_default(self):
        """잘못된 JSON 파일은 기본값 반환"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            # 잘못된 JSON 작성
            with open(settings_file, "w", encoding="utf-8") as f:
                f.write("{invalid json")

            # 로드 (경고 메시지 출력하지만 예외는 발생하지 않음)
            loaded = load_settings(settings_file)

            assert loaded == get_default_settings()


class TestSaveSettings:
    """설정 저장 테스트"""

    def test_save_creates_file(self):
        """파일이 생성되는지 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            settings = get_default_settings()
            success = save_settings(settings, settings_file)

            assert success
            assert settings_file.exists()

    def test_save_creates_directory(self):
        """디렉토리가 없으면 생성하는지 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "subdir" / "settings.json"

            settings = get_default_settings()
            success = save_settings(settings, settings_file)

            assert success
            assert settings_file.exists()
            assert settings_file.parent.exists()

    def test_save_and_load_roundtrip(self):
        """저장 후 로드 시 동일한 값인지 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            # 저장
            original = {
                "appearance": {"theme": "light"},
                "logging": {"level": "DEBUG"},
                "language": {"locale": "en_US"},
                "backup": {"directory": "/test/backup"},
            }
            save_settings(original, settings_file)

            # 로드
            loaded = load_settings(settings_file)

            assert loaded["appearance"]["theme"] == "light"
            assert loaded["logging"]["level"] == "DEBUG"
            assert loaded["language"]["locale"] == "en_US"
            assert loaded["backup"]["directory"] == "/test/backup"

    def test_save_utf8_encoding(self):
        """한글 등 UTF-8 문자를 올바르게 저장하는지 확인"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"

            settings = get_default_settings()
            settings["backup"]["directory"] = "한글/경로/테스트"

            save_settings(settings, settings_file)

            # 직접 파일 읽어서 확인
            with open(settings_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "한글" in content


class TestGetSetting:
    """설정 값 가져오기 테스트"""

    def test_get_existing_key(self):
        """존재하는 키 가져오기"""
        settings = get_default_settings()
        theme = get_setting(settings, "appearance.theme")

        assert theme in ["dark", "light"]

    def test_get_nested_key(self):
        """중첩된 키 가져오기"""
        settings = {"level1": {"level2": {"level3": "value"}}}

        value = get_setting(settings, "level1.level2.level3")
        assert value == "value"

    def test_get_nonexistent_key_returns_default(self):
        """존재하지 않는 키는 기본값 반환"""
        settings = get_default_settings()
        value = get_setting(settings, "nonexistent.key", "fallback")

        assert value == "fallback"

    def test_get_partial_path_returns_dict(self):
        """일부 경로만 지정하면 딕셔너리 반환"""
        settings = get_default_settings()
        appearance = get_setting(settings, "appearance")

        assert isinstance(appearance, dict)
        assert "theme" in appearance


class TestSetSetting:
    """설정 값 설정 테스트"""

    def test_set_existing_key(self):
        """존재하는 키 수정"""
        settings = get_default_settings()
        set_setting(settings, "appearance.theme", "light")

        assert settings["appearance"]["theme"] == "light"

    def test_set_new_key(self):
        """새로운 키 추가"""
        settings = {}
        set_setting(settings, "new.nested.key", "value")

        assert settings["new"]["nested"]["key"] == "value"

    def test_set_overwrites_existing(self):
        """기존 값 덮어쓰기"""
        settings = {"appearance": {"theme": "dark"}}
        set_setting(settings, "appearance.theme", "light")

        assert settings["appearance"]["theme"] == "light"

    def test_set_creates_nested_dicts(self):
        """중첩 딕셔너리 자동 생성"""
        settings = {}
        set_setting(settings, "a.b.c.d", "value")

        assert settings == {"a": {"b": {"c": {"d": "value"}}}}


class TestDefaultSettings:
    """DEFAULT_SETTINGS 상수 테스트"""

    def test_default_settings_structure(self):
        """DEFAULT_SETTINGS가 올바른 구조인지 확인"""
        # 독립적인 복사본 사용
        settings = get_default_settings()
        assert isinstance(settings, dict)
        assert "appearance" in settings
        assert "logging" in settings
        assert "language" in settings
        assert "backup" in settings

    def test_default_theme_is_dark(self):
        """기본 테마가 dark인지 확인"""
        settings = get_default_settings()
        assert settings["appearance"]["theme"] == "dark"

    def test_default_log_level_is_info(self):
        """기본 로그 레벨이 INFO인지 확인"""
        settings = get_default_settings()
        assert settings["logging"]["level"] == "INFO"

    def test_default_locale_is_korean(self):
        """기본 언어가 한국어인지 확인"""
        settings = get_default_settings()
        assert settings["language"]["locale"] == "ko_KR"

    def test_default_backup_directory(self):
        """기본 백업 디렉토리 확인"""
        settings = get_default_settings()
        assert settings["backup"]["directory"] == "data/backups"
