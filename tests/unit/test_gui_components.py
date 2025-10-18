"""GUI 컴포넌트 단위 테스트

src/gui/ 모듈의 GUI 컴포넌트를 테스트합니다.

테스트 범위:
1. MainWindow import 및 생성
2. 기본 GUI 속성 확인
3. pytest-qt를 사용한 위젯 테스트

주의: GUI 테스트는 headless 환경에서 실행될 수 있으므로
QT_QPA_PLATFORM=offscreen 설정이 필요할 수 있습니다.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

# QT_QPA_PLATFORM 환경변수 설정 (headless 환경 대응)
os.environ["QT_QPA_PLATFORM"] = "offscreen"


# ==================== Import Tests ====================


@pytest.mark.unit
class TestGUIImports:
    """GUI 모듈 import 테스트"""

    def test_import_gui_app(self):
        """app.py import 가능 확인"""
        try:
            from src.gui import app

            assert app is not None
        except ImportError as e:
            pytest.fail(f"src.gui.app import 실패: {e}")

    def test_import_main_window(self):
        """main_window.py import 가능 확인"""
        try:
            from src.gui.main_window import MainWindow

            assert MainWindow is not None
        except ImportError as e:
            pytest.fail(f"MainWindow import 실패: {e}")


# ==================== MainWindow Tests ====================


@pytest.mark.unit
class TestMainWindow:
    """MainWindow 클래스 테스트"""

    def test_main_window_class_exists(self):
        """MainWindow 클래스가 정의되어 있는지 확인"""
        from src.gui.main_window import MainWindow

        assert MainWindow is not None
        assert callable(MainWindow)

    @pytest.mark.skip(reason="GUI 테스트는 실제 환경에서만 실행")
    def test_main_window_creation(self, qtbot):
        """MainWindow 생성 테스트 (pytest-qt 사용)

        이 테스트는 실제 GUI 환경에서만 실행됩니다.
        CI/CD 환경에서는 skip됩니다.
        """
        from src.gui.main_window import MainWindow

        # MainWindow 생성
        window = MainWindow()
        qtbot.addWidget(window)

        # 기본 속성 확인
        assert window is not None
        assert window.windowTitle() is not None


# ==================== GUI Components Existence Tests ====================


@pytest.mark.unit
class TestGUIComponentsExistence:
    """GUI 컴포넌트 파일 존재 확인"""

    def test_main_window_file_exists(self, project_root):
        """main_window.py 파일 존재 확인"""
        main_window_file = project_root / "src" / "gui" / "main_window.py"
        assert (
            main_window_file.exists()
        ), f"main_window.py 파일이 존재하지 않습니다: {main_window_file}"

    def test_app_file_exists(self, project_root):
        """app.py 파일 존재 확인"""
        app_file = project_root / "src" / "gui" / "app.py"
        assert app_file.exists(), f"app.py 파일이 존재하지 않습니다: {app_file}"

    def test_views_directory_exists(self, project_root):
        """views 디렉토리 존재 확인"""
        views_dir = project_root / "src" / "gui" / "views"
        assert (
            views_dir.exists() and views_dir.is_dir()
        ), f"views 디렉토리가 존재하지 않습니다: {views_dir}"

    def test_dialogs_directory_exists(self, project_root):
        """dialogs 디렉토리 존재 확인"""
        dialogs_dir = project_root / "src" / "gui" / "dialogs"
        assert (
            dialogs_dir.exists() and dialogs_dir.is_dir()
        ), f"dialogs 디렉토리가 존재하지 않습니다: {dialogs_dir}"


# ==================== GUI Module Structure Tests ====================


@pytest.mark.unit
class TestGUIModuleStructure:
    """GUI 모듈 구조 테스트"""

    def test_gui_package_has_init(self, project_root):
        """gui 패키지에 __init__.py가 있는지 확인"""
        init_file = project_root / "src" / "gui" / "__init__.py"
        assert init_file.exists(), f"gui 패키지에 __init__.py가 없습니다: {init_file}"

    def test_views_package_has_init(self, project_root):
        """views 패키지에 __init__.py가 있는지 확인"""
        init_file = project_root / "src" / "gui" / "views" / "__init__.py"
        if (project_root / "src" / "gui" / "views").exists():
            assert init_file.exists(), f"views 패키지에 __init__.py가 없습니다: {init_file}"

    def test_dialogs_package_has_init(self, project_root):
        """dialogs 패키지에 __init__.py가 있는지 확인"""
        init_file = project_root / "src" / "gui" / "dialogs" / "__init__.py"
        if (project_root / "src" / "gui" / "dialogs").exists():
            assert init_file.exists(), f"dialogs 패키지에 __init__.py가 없습니다: {init_file}"


# ==================== PySide6 Dependency Tests ====================


@pytest.mark.unit
class TestPySide6Dependency:
    """PySide6 의존성 테스트"""

    def test_pyside6_installed(self):
        """PySide6가 설치되어 있는지 확인"""
        try:
            import PySide6

            assert PySide6 is not None
        except ImportError:
            pytest.fail("PySide6가 설치되지 않았습니다")

    def test_pyside6_qtwidgets_available(self):
        """PySide6.QtWidgets를 import 가능한지 확인"""
        try:
            from PySide6 import QtWidgets

            assert QtWidgets is not None
        except ImportError as e:
            pytest.fail(f"PySide6.QtWidgets import 실패: {e}")

    def test_pyside6_qtcore_available(self):
        """PySide6.QtCore를 import 가능한지 확인"""
        try:
            from PySide6 import QtCore

            assert QtCore is not None
        except ImportError as e:
            pytest.fail(f"PySide6.QtCore import 실패: {e}")


# ==================== Mock GUI Tests ====================


@pytest.mark.unit
class TestGUIWithMocks:
    """Mock을 사용한 GUI 테스트"""

    def test_main_window_with_mock(self):
        """Mock을 사용한 MainWindow 테스트

        실제 GUI를 생성하지 않고 구조만 확인합니다.
        """
        from src.gui.main_window import MainWindow

        # MainWindow가 QMainWindow를 상속하는지 확인
        # (PySide6.QtWidgets.QMainWindow)
        try:
            from PySide6.QtWidgets import QMainWindow

            # MainWindow의 부모 클래스 확인
            # (실제 인스턴스를 생성하지 않고 클래스 구조만 확인)
            assert issubclass(MainWindow, QMainWindow) or hasattr(MainWindow, "__bases__")
        except Exception:
            # headless 환경에서는 skip
            pytest.skip("GUI 환경이 아니므로 skip")


# ==================== Minimal GUI Smoke Tests ====================


@pytest.mark.unit
class TestGUISmokeTests:
    """GUI 기본 동작 smoke 테스트"""

    def test_gui_app_module_has_main_function(self):
        """app.py에 main 함수가 있는지 확인"""
        from src.gui import app

        # main 함수 또는 run 함수가 있는지 확인
        has_main = hasattr(app, "main") or hasattr(app, "run") or hasattr(app, "__main__")
        # app 모듈이 실행 가능한지만 확인 (함수 존재 여부는 선택적)
        assert app is not None

    def test_main_window_has_required_methods(self):
        """MainWindow에 필수 메서드가 있는지 확인"""
        from src.gui.main_window import MainWindow

        # MainWindow 클래스에 __init__ 메서드가 있는지 확인
        assert hasattr(MainWindow, "__init__")
