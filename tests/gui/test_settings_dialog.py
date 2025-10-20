"""설정 대화상자 테스트

src/gui/dialogs/settings_dialog.py의 GUI 테스트입니다.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.gui.dialogs.settings_dialog import SettingsDialog
from src.infrastructure.config.settings import get_default_settings


@pytest.fixture
def app(qapp):
    """QApplication 픽스처 (qapp는 pytest-qt가 제공)"""
    return qapp


@pytest.fixture
def temp_settings_file():
    """임시 설정 파일 픽스처"""
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = Path(tmpdir) / "settings.json"
        yield settings_file


class TestSettingsDialogInit:
    """SettingsDialog 초기화 테스트"""

    def test_dialog_creation(self, app):
        """대화상자가 생성되는지 확인"""
        dialog = SettingsDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "설정"

    def test_widgets_exist(self, app):
        """필수 위젯들이 존재하는지 확인"""
        dialog = SettingsDialog()

        assert hasattr(dialog, "theme_combo")
        assert hasattr(dialog, "log_level_combo")
        assert hasattr(dialog, "language_combo")
        assert hasattr(dialog, "backup_path_edit")
        assert hasattr(dialog, "backup_path_button")

    def test_theme_combo_items(self, app):
        """테마 콤보박스 항목 확인"""
        dialog = SettingsDialog()

        assert dialog.theme_combo.count() == 2
        assert dialog.theme_combo.itemText(0) == "Dark"
        assert dialog.theme_combo.itemText(1) == "Light"

    def test_log_level_combo_items(self, app):
        """로그 레벨 콤보박스 항목 확인"""
        dialog = SettingsDialog()

        assert dialog.log_level_combo.count() == 4
        assert dialog.log_level_combo.itemText(0) == "DEBUG"
        assert dialog.log_level_combo.itemText(1) == "INFO"
        assert dialog.log_level_combo.itemText(2) == "WARNING"
        assert dialog.log_level_combo.itemText(3) == "ERROR"

    def test_language_combo_disabled(self, app):
        """언어 콤보박스가 비활성화 상태인지 확인 (미구현 기능)"""
        dialog = SettingsDialog()

        assert not dialog.language_combo.isEnabled()


class TestSettingsDialogLoadSettings:
    """설정 로드 테스트"""

    @patch("src.gui.dialogs.settings_dialog.load_settings")
    def test_loads_default_settings(self, mock_load, app):
        """기본 설정을 로드하는지 확인"""
        mock_load.return_value = get_default_settings()

        dialog = SettingsDialog()

        # 기본값 확인
        assert dialog.theme_combo.currentText() == "Dark"
        assert dialog.log_level_combo.currentText() == "INFO"
        assert dialog.language_combo.currentText() == "한국어"
        assert dialog.backup_path_edit.text() == "data/backups"

    @patch("src.gui.dialogs.settings_dialog.load_settings")
    def test_loads_custom_settings(self, mock_load, app):
        """커스텀 설정을 로드하는지 확인"""
        custom_settings = {
            "appearance": {"theme": "light"},
            "logging": {"level": "DEBUG"},
            "language": {"locale": "en_US"},
            "backup": {"directory": "/custom/backup"},
        }
        mock_load.return_value = custom_settings

        dialog = SettingsDialog()

        assert dialog.theme_combo.currentText() == "Light"
        assert dialog.log_level_combo.currentText() == "DEBUG"
        assert dialog.language_combo.currentText() == "English"
        assert dialog.backup_path_edit.text() == "/custom/backup"


class TestSettingsDialogBrowseDirectory:
    """디렉토리 찾아보기 테스트"""

    @patch("src.gui.dialogs.settings_dialog.QFileDialog.getExistingDirectory")
    def test_browse_directory_updates_path(self, mock_dialog, app):
        """찾아보기 버튼 클릭 시 경로가 업데이트되는지 확인"""
        mock_dialog.return_value = "/selected/directory"

        dialog = SettingsDialog()
        dialog.backup_path_edit.setText("data/backups")

        # 버튼 클릭
        dialog._on_browse_backup_directory()

        assert dialog.backup_path_edit.text() == "/selected/directory"

    @patch("src.gui.dialogs.settings_dialog.QFileDialog.getExistingDirectory")
    def test_browse_directory_cancel(self, mock_dialog, app):
        """찾아보기 취소 시 경로가 유지되는지 확인"""
        mock_dialog.return_value = ""  # 취소

        dialog = SettingsDialog()
        dialog.backup_path_edit.setText("data/backups")

        # 버튼 클릭
        dialog._on_browse_backup_directory()

        # 경로 유지
        assert dialog.backup_path_edit.text() == "data/backups"


class TestSettingsDialogSave:
    """설정 저장 테스트"""

    @patch("src.gui.dialogs.settings_dialog.save_settings")
    @patch("src.gui.dialogs.settings_dialog.load_settings")
    def test_save_button_saves_settings(self, mock_load, mock_save, app):
        """저장 버튼 클릭 시 설정이 저장되는지 확인"""
        mock_load.return_value = get_default_settings()
        mock_save.return_value = True

        dialog = SettingsDialog()

        # 값 변경
        dialog.theme_combo.setCurrentText("Light")
        dialog.log_level_combo.setCurrentText("DEBUG")
        dialog.backup_path_edit.setText("/custom/backup")

        # 저장 버튼 클릭
        dialog._on_save()

        # save_settings가 호출되었는지 확인
        assert mock_save.called
        saved_settings = mock_save.call_args[0][0]

        assert saved_settings["appearance"]["theme"] == "light"
        assert saved_settings["logging"]["level"] == "DEBUG"
        assert saved_settings["backup"]["directory"] == "/custom/backup"

    @patch("src.gui.dialogs.settings_dialog.save_settings")
    @patch("src.gui.dialogs.settings_dialog.load_settings")
    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_save_validates_backup_path(self, mock_warning, mock_load, mock_save, app):
        """백업 경로가 비어있으면 경고 표시"""
        mock_load.return_value = get_default_settings()

        dialog = SettingsDialog()
        dialog.backup_path_edit.setText("")  # 비어있음

        # 저장 버튼 클릭
        dialog._on_save()

        # 경고 메시지 표시
        assert mock_warning.called

        # save_settings는 호출되지 않음
        assert not mock_save.called

    @patch("src.gui.dialogs.settings_dialog.save_settings")
    @patch("src.gui.dialogs.settings_dialog.load_settings")
    @patch("PySide6.QtWidgets.QMessageBox.critical")
    def test_save_failure_shows_error(self, mock_critical, mock_load, mock_save, app):
        """저장 실패 시 오류 메시지 표시"""
        mock_load.return_value = get_default_settings()
        mock_save.return_value = False  # 저장 실패

        dialog = SettingsDialog()

        # 저장 버튼 클릭
        dialog._on_save()

        # 오류 메시지 표시
        assert mock_critical.called


class TestSettingsDialogGetData:
    """설정 데이터 반환 테스트"""

    @patch("src.gui.dialogs.settings_dialog.load_settings")
    def test_get_settings_returns_dict(self, mock_load, app):
        """get_settings()가 딕셔너리를 반환하는지 확인"""
        mock_load.return_value = get_default_settings()

        dialog = SettingsDialog()
        settings = dialog.get_settings()

        assert isinstance(settings, dict)
        assert "appearance" in settings
        assert "logging" in settings
        assert "language" in settings
        assert "backup" in settings
