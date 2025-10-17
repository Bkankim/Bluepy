"""메인 윈도우

BluePy 2.0의 메인 GUI 윈도우입니다.

주요 구성:
- 메뉴바 (파일, 도움말)
- 도크 위젯 (서버 목록)
- 중앙 탭 위젯 (스캔, 결과)
- 상태바
"""

import sys
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from .views.server_view import ServerView
from .views.scan_view import ScanView
from .views.result_view import ResultView


class MainWindow(QMainWindow):
    """메인 윈도우 클래스

    BluePy 2.0 애플리케이션의 최상위 윈도우입니다.

    Signals:
        server_selected: 서버가 선택되었을 때 발생 (server_id: str)
        scan_started: 스캔이 시작되었을 때 발생
        scan_completed: 스캔이 완료되었을 때 발생
    """

    # 커스텀 시그널 정의
    server_selected = Signal(str)  # server_id
    scan_started = Signal()
    scan_completed = Signal()

    def __init__(self):
        """초기화"""
        super().__init__()

        # 윈도우 설정
        self.setWindowTitle("BluePy 2.0 - 인프라 보안 점검 도구")
        self.setMinimumSize(1200, 800)

        # UI 초기화
        self._setup_ui()
        self._create_menus()
        self._create_status_bar()
        self._connect_signals()

    def _setup_ui(self):
        """UI 구성 요소 생성"""
        # 중앙 탭 위젯
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 뷰 생성
        self.scan_view = ScanView()
        self.result_view = ResultView()

        # 탭에 추가
        self.tab_widget.addTab(self.scan_view, "스캔")
        self.tab_widget.addTab(self.result_view, "결과")

        # 서버 목록 도크 위젯
        self.server_view = ServerView()
        self.server_dock = QDockWidget("서버 목록", self)
        self.server_dock.setWidget(self.server_view)
        self.server_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # 왼쪽에 도크 추가
        self.addDockWidget(Qt.LeftDockWidgetArea, self.server_dock)

    def _create_menus(self):
        """메뉴바 생성"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")

        # 서버 추가
        add_server_action = file_menu.addAction("서버 추가(&A)")
        add_server_action.setShortcut("Ctrl+N")
        add_server_action.triggered.connect(self._on_add_server)

        file_menu.addSeparator()

        # 종료
        exit_action = file_menu.addAction("종료(&X)")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # 스캔 메뉴
        scan_menu = menubar.addMenu("스캔(&S)")

        # 스캔 시작
        start_scan_action = scan_menu.addAction("스캔 시작(&S)")
        start_scan_action.setShortcut("F5")
        start_scan_action.triggered.connect(self._on_start_scan)

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말(&H)")

        # 정보
        about_action = help_menu.addAction("정보(&A)")
        about_action.triggered.connect(self._show_about)

    def _create_status_bar(self):
        """상태바 생성"""
        self.statusBar().showMessage("준비")

    def _connect_signals(self):
        """시그널 연결"""
        # 서버 선택 시그널
        self.server_view.server_selected.connect(self._on_server_selected)

        # 스캔 버튼 시그널
        self.scan_view.scan_requested.connect(self._on_start_scan)

    def _on_add_server(self):
        """서버 추가 핸들러"""
        # TODO: ServerDialog 구현 후 연결
        self.statusBar().showMessage("서버 추가 (구현 예정)")
        QMessageBox.information(
            self,
            "서버 추가",
            "서버 추가 기능은 구현 중입니다."
        )

    def _on_server_selected(self, server_id: str):
        """서버 선택 핸들러

        Args:
            server_id: 선택된 서버 ID
        """
        self.statusBar().showMessage(f"서버 선택: {server_id}")
        self.server_selected.emit(server_id)

    def _on_start_scan(self):
        """스캔 시작 핸들러"""
        # TODO: 실제 스캔 로직 연결
        self.statusBar().showMessage("스캔 시작 (구현 예정)")
        self.scan_started.emit()

        # 결과 탭으로 전환
        self.tab_widget.setCurrentWidget(self.result_view)

    def _show_about(self):
        """정보 대화상자 표시"""
        QMessageBox.about(
            self,
            "BluePy 2.0 정보",
            "<h3>BluePy 2.0</h3>"
            "<p>멀티플랫폼 인프라 보안 점검 및 자동 수정 도구</p>"
            "<p>버전: 2.0.0</p>"
            "<p>Copyright 2025</p>"
        )

    def update_status(self, message: str):
        """상태 메시지 업데이트

        Args:
            message: 표시할 메시지
        """
        self.statusBar().showMessage(message)


def main():
    """애플리케이션 실행"""
    app = QApplication(sys.argv)

    # 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()