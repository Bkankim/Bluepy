"""테마 데모 애플리케이션

다크 모드와 라이트 모드를 전환하는 간단한 데모입니다.

실행 방법:
    python examples/theme_demo.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QGroupBox,
    QCheckBox,
    QRadioButton,
    QComboBox,
    QProgressBar,
)
from PySide6.QtCore import Qt

from src.gui.theme_manager import get_theme_manager, Theme


class ThemeDemoWindow(QMainWindow):
    """테마 데모 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BluePy 2.0 - 테마 데모")
        self.setMinimumSize(800, 600)

        # 테마 관리자
        self.theme_manager = get_theme_manager()

        # UI 설정
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 테마 전환 버튼
        theme_layout = QHBoxLayout()
        layout.addLayout(theme_layout)

        dark_btn = QPushButton("다크 모드")
        dark_btn.clicked.connect(lambda: self._change_theme(Theme.DARK))
        theme_layout.addWidget(dark_btn)

        light_btn = QPushButton("라이트 모드")
        light_btn.clicked.connect(lambda: self._change_theme(Theme.LIGHT))
        theme_layout.addWidget(light_btn)

        toggle_btn = QPushButton("테마 토글")
        toggle_btn.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(toggle_btn)

        theme_layout.addStretch()

        # 탭 위젯
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 탭 1: 입력 위젯
        tab_widget.addTab(self._create_input_tab(), "입력 위젯")

        # 탭 2: 테이블
        tab_widget.addTab(self._create_table_tab(), "테이블")

        # 탭 3: 기타
        tab_widget.addTab(self._create_misc_tab(), "기타")

    def _create_input_tab(self) -> QWidget:
        """입력 위젯 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 그룹 1: 텍스트 입력
        group1 = QGroupBox("텍스트 입력")
        group1_layout = QVBoxLayout(group1)

        group1_layout.addWidget(QLabel("QLineEdit:"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("여기에 입력하세요...")
        group1_layout.addWidget(line_edit)

        group1_layout.addWidget(QLabel("QTextEdit:"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("여러 줄 입력...")
        text_edit.setMaximumHeight(100)
        group1_layout.addWidget(text_edit)

        layout.addWidget(group1)

        # 그룹 2: 버튼
        group2 = QGroupBox("버튼")
        group2_layout = QHBoxLayout(group2)

        normal_btn = QPushButton("일반 버튼")
        group2_layout.addWidget(normal_btn)

        default_btn = QPushButton("기본 버튼")
        default_btn.setDefault(True)
        group2_layout.addWidget(default_btn)

        disabled_btn = QPushButton("비활성 버튼")
        disabled_btn.setEnabled(False)
        group2_layout.addWidget(disabled_btn)

        layout.addWidget(group2)

        # 그룹 3: 선택
        group3 = QGroupBox("선택 위젯")
        group3_layout = QVBoxLayout(group3)

        check1 = QCheckBox("체크박스 1")
        check1.setChecked(True)
        group3_layout.addWidget(check1)

        check2 = QCheckBox("체크박스 2 (비활성)")
        check2.setEnabled(False)
        group3_layout.addWidget(check2)

        radio1 = QRadioButton("라디오 버튼 1")
        radio1.setChecked(True)
        group3_layout.addWidget(radio1)

        radio2 = QRadioButton("라디오 버튼 2")
        group3_layout.addWidget(radio2)

        combo = QComboBox()
        combo.addItems(["옵션 1", "옵션 2", "옵션 3"])
        group3_layout.addWidget(combo)

        layout.addWidget(group3)

        layout.addStretch()

        return widget

    def _create_table_tab(self) -> QWidget:
        """테이블 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["규칙 ID", "규칙 이름", "상태", "점수"])
        table.setAlternatingRowColors(True)

        # 샘플 데이터
        data = [
            ("U-01", "root 계정 원격 접속 제한", "PASS", "100"),
            ("U-03", "계정 잠금 임계값 설정", "FAIL", "0"),
            ("U-04", "패스워드 파일 보호", "PASS", "100"),
            ("U-18", "/etc/passwd 파일 권한 설정", "WARN", "50"),
            ("U-22", "/etc/syslog.conf 파일 권한 설정", "PASS", "100"),
        ]

        for row, (rule_id, rule_name, status, score) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(rule_id))
            table.setItem(row, 1, QTableWidgetItem(rule_name))

            # 상태 아이템 (색상 적용)
            status_item = QTableWidgetItem(status)
            if status == "PASS":
                status_item.setForeground(Qt.green)
            elif status == "FAIL":
                status_item.setForeground(Qt.red)
            else:
                status_item.setForeground(Qt.yellow)
            table.setItem(row, 2, status_item)

            table.setItem(row, 3, QTableWidgetItem(score))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        return widget

    def _create_misc_tab(self) -> QWidget:
        """기타 위젯 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 프로그레스 바
        layout.addWidget(QLabel("QProgressBar:"))
        progress = QProgressBar()
        progress.setValue(65)
        layout.addWidget(progress)

        # 상태 라벨
        layout.addWidget(QLabel("\n커스텀 상태 색상:"))

        pass_label = QLabel("PASS - 통과")
        pass_label.setProperty("class", "status-pass")
        layout.addWidget(pass_label)

        fail_label = QLabel("FAIL - 실패")
        fail_label.setProperty("class", "status-fail")
        layout.addWidget(fail_label)

        warn_label = QLabel("WARN - 경고")
        warn_label.setProperty("class", "status-warn")
        layout.addWidget(warn_label)

        info_label = QLabel("INFO - 정보")
        info_label.setProperty("class", "status-info")
        layout.addWidget(info_label)

        layout.addStretch()

        return widget

    def _change_theme(self, theme: Theme):
        """테마 변경"""
        app = QApplication.instance()
        self.theme_manager.set_theme(app, theme)
        self.statusBar().showMessage(
            f"테마 변경: {'다크 모드' if theme == Theme.DARK else '라이트 모드'}"
        )

    def _toggle_theme(self):
        """테마 토글"""
        app = QApplication.instance()
        self.theme_manager.toggle_theme()
        current = self.theme_manager.get_current_theme()
        self.statusBar().showMessage(
            f"테마 전환: {'다크 모드' if current == Theme.DARK else '라이트 모드'}"
        )


def main():
    """메인 함수"""
    app = QApplication(sys.argv)

    # 애플리케이션 설정
    app.setApplicationName("BluePy 2.0 Theme Demo")
    app.setApplicationVersion("2.0.0")

    # 초기 테마 설정 (다크 모드)
    theme_manager = get_theme_manager()
    theme_manager.set_theme(app, Theme.DARK)

    # 윈도우 생성 및 표시
    window = ThemeDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
