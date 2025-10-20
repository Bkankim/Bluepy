"""테마 관리자

애플리케이션의 색상 테마를 관리하는 모듈입니다.

주요 기능:
- QSS 파일 로딩
- 테마 전환 (다크/라이트)
- QPalette 설정
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QFile, QTextStream, Qt, QSettings
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


class Theme(Enum):
    """테마 종류"""

    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    """테마 관리자 클래스

    QSS 스타일시트와 QPalette를 조합하여 애플리케이션 테마를 설정합니다.
    """

    # QSS 파일 경로
    STYLES_DIR = Path(__file__).parent.parent.parent / "resources" / "styles"

    def __init__(self):
        """초기화"""
        self._current_theme: Theme = Theme.DARK
        self._app: Optional[QApplication] = None

    def set_theme(self, app: QApplication, theme: Theme):
        """테마 설정

        Args:
            app: QApplication 인스턴스
            theme: 적용할 테마
        """
        self._app = app
        self._current_theme = theme

        # 1. QPalette 먼저 설정 (기본 색상)
        self._apply_palette(theme)

        # 2. QSS 스타일시트 적용 (세부 스타일)
        self._apply_stylesheet(theme)

        # 3. 설정 저장
        self.save_theme()

    def _apply_palette(self, theme: Theme):
        """QPalette 설정

        Args:
            theme: 적용할 테마
        """
        if not self._app:
            return

        palette = QPalette()

        if theme == Theme.DARK:
            # Dark Theme Colors
            palette.setColor(QPalette.Window, QColor("#1E1E1E"))
            palette.setColor(QPalette.WindowText, QColor("#CCCCCC"))
            palette.setColor(QPalette.Base, QColor("#2D2D30"))
            palette.setColor(QPalette.AlternateBase, QColor("#252526"))
            palette.setColor(QPalette.ToolTipBase, QColor("#252526"))
            palette.setColor(QPalette.ToolTipText, QColor("#CCCCCC"))
            palette.setColor(QPalette.Text, QColor("#CCCCCC"))
            palette.setColor(QPalette.Button, QColor("#2D2D30"))
            palette.setColor(QPalette.ButtonText, QColor("#CCCCCC"))
            palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Link, QColor("#007ACC"))
            palette.setColor(QPalette.Highlight, QColor("#264F78"))
            palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

            # Disabled colors
            palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#656565"))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#656565"))
            palette.setColor(
                QPalette.Disabled, QPalette.ButtonText, QColor("#656565")
            )

        else:  # LIGHT
            # Light Theme Colors
            palette.setColor(QPalette.Window, QColor("#FFFFFF"))
            palette.setColor(QPalette.WindowText, QColor("#2E2E2E"))
            palette.setColor(QPalette.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.AlternateBase, QColor("#F3F3F3"))
            palette.setColor(QPalette.ToolTipBase, QColor("#F3F3F3"))
            palette.setColor(QPalette.ToolTipText, QColor("#2E2E2E"))
            palette.setColor(QPalette.Text, QColor("#2E2E2E"))
            palette.setColor(QPalette.Button, QColor("#E8E8E8"))
            palette.setColor(QPalette.ButtonText, QColor("#2E2E2E"))
            palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Link, QColor("#0078D4"))
            palette.setColor(QPalette.Highlight, QColor("#CCE4F7"))
            palette.setColor(QPalette.HighlightedText, QColor("#2E2E2E"))

            # Disabled colors
            palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#AEAEAE"))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#AEAEAE"))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#AEAEAE"))

        self._app.setPalette(palette)

    def _apply_stylesheet(self, theme: Theme):
        """QSS 스타일시트 적용

        Args:
            theme: 적용할 테마
        """
        if not self._app:
            return

        # QSS 파일 경로
        qss_file = self.STYLES_DIR / f"{theme.value}.qss"

        if not qss_file.exists():
            print(f"Warning: QSS file not found: {qss_file}")
            return

        # QSS 파일 읽기
        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self._app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def toggle_theme(self):
        """테마 토글 (다크 <-> 라이트)"""
        if not self._app:
            return

        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.set_theme(self._app, new_theme)

    def get_current_theme(self) -> Theme:
        """현재 테마 반환

        Returns:
            현재 적용된 테마
        """
        return self._current_theme

    def save_theme(self):
        """현재 테마 설정을 QSettings에 저장"""
        settings = QSettings()
        settings.setValue("appearance/theme", self._current_theme.value)

    def load_theme(self) -> Theme:
        """QSettings에서 테마 설정 로드

        Returns:
            저장된 테마 (기본값: DARK)
        """
        settings = QSettings()
        theme_str = settings.value("appearance/theme", Theme.DARK.value)
        return Theme.DARK if theme_str == "dark" else Theme.LIGHT


# 전역 인스턴스 (싱글톤 패턴)
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """ThemeManager 싱글톤 인스턴스 반환

    Returns:
        ThemeManager 인스턴스
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
