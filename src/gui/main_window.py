"""메인 윈도우

BluePy 2.0의 메인 GUI 윈도우입니다.

주요 구성:
- 메뉴바 (파일, 도움말)
- 도크 위젯 (서버 목록)
- 중앙 탭 위젯 (스캔, 결과)
- 상태바
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from .views.server_view import ServerView
from .views.scan_view import ScanView
from .views.result_view import ResultView
from .views.history_view import HistoryView
from .dialogs.server_dialog import ServerDialog
from .dialogs.remediation_dialog import RemediationDialog
from .dialogs.settings_dialog import SettingsDialog
from .workers.scan_worker import ScanWorker
from ..infrastructure.reporting.excel_reporter import ExcelReporter
from ..infrastructure.database.models import create_db_engine, create_db_session
from ..infrastructure.config.settings import load_settings, get_setting


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

        # 상태 변수
        self.current_server = None  # 현재 선택된 서버 정보
        self.scan_worker = None  # 스캔 Worker
        self.last_scan_result = None  # 마지막 스캔 결과

        # 데이터베이스 세션
        self.db_engine = create_db_engine("data/databases/bluepy.db")
        self.db_session = create_db_session(self.db_engine)

        # 설정 로드
        self.app_settings = load_settings()

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
        self.history_view = HistoryView()

        # DB 세션 설정
        self.history_view.set_database_session(self.db_session)

        # 탭에 추가
        self.tab_widget.addTab(self.scan_view, "스캔")
        self.tab_widget.addTab(self.result_view, "결과")
        self.tab_widget.addTab(self.history_view, "이력")

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
        scan_menu = menubar.addMenu("스캔(&C)")

        # 스캔 시작
        start_scan_action = scan_menu.addAction("스캔 시작(&S)")
        start_scan_action.setShortcut("F5")
        start_scan_action.triggered.connect(self._on_start_scan)

        # 설정 메뉴
        settings_menu = menubar.addMenu("설정(&S)")

        # 설정 열기
        open_settings_action = settings_menu.addAction("설정(&P)")
        open_settings_action.setShortcut("Ctrl+,")
        open_settings_action.triggered.connect(self._on_open_settings)

        # 보기 메뉴
        view_menu = menubar.addMenu("보기(&V)")

        # 테마 전환
        toggle_theme_action = view_menu.addAction("테마 전환(&T)")
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.triggered.connect(self._on_toggle_theme)

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

        # 자동 수정 시그널
        self.result_view.remediate_requested.connect(self._on_remediate_requested)

    def _on_add_server(self):
        """서버 추가 핸들러"""
        dialog = ServerDialog(self)

        if dialog.exec():
            data = dialog.get_data()
            # TODO: DB에 저장
            # 현재는 ServerView에 직접 추가
            self.server_view.add_server(
                server_id=data["name"],  # 임시로 이름을 ID로 사용
                server_name=data["name"],
                host=data["host"],
            )
            self.statusBar().showMessage(f"서버 추가됨: {data['name']}")

    def _on_server_selected(self, server_id: str):
        """서버 선택 핸들러

        Args:
            server_id: 선택된 서버 ID
        """
        self.statusBar().showMessage(f"서버 선택: {server_id}")

        # 서버 정보 저장 (실제로는 DB에서 조회)
        self.current_server = {
            "server_id": server_id,
            "name": server_id,  # 임시
            "host": "192.168.1.100",  # 임시
            "username": "root",  # 임시
            "password": "password",  # 임시 (실제로는 keyring 사용)
            "platform": "linux",
        }

        # ScanView에 서버 정보 설정
        self.scan_view.set_server(server_id=server_id, server_name=server_id, platform="linux")

        # HistoryView에 이력 로드
        # TODO: 실제 server DB ID 사용 (현재는 임시로 hash 사용)
        try:
            # 임시: server_id 문자열을 hash로 정수 변환 (0-999 범위)
            server_db_id = abs(hash(server_id)) % 1000
            self.history_view.load_history(server_db_id)
        except Exception as e:
            print(f"Warning: Failed to load history: {e}")

        self.server_selected.emit(server_id)

    def _on_start_scan(self):
        """스캔 시작 핸들러"""
        if not self.current_server:
            QMessageBox.warning(self, "서버 선택 필요", "먼저 스캔할 서버를 선택하세요.")
            return

        # 이미 스캔 중이면 무시
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, "스캔 진행 중", "이미 스캔이 진행 중입니다.")
            return

        # ScanWorker 생성
        self.scan_worker = ScanWorker(
            server_id=self.current_server["server_id"],
            host=self.current_server["host"],
            username=self.current_server["username"],
            password=self.current_server.get("password"),
            key_filename=self.current_server.get("key_path"),
            port=self.current_server.get("port", 22),
        )

        # 시그널 연결
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.log.connect(self._on_scan_log)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.error.connect(self._on_scan_error)

        # 스캔 시작
        self.scan_worker.start()
        self.scan_started.emit()

        # 스캔 탭으로 전환
        self.tab_widget.setCurrentWidget(self.scan_view)
        self.statusBar().showMessage("스캔 시작...")

    def _on_scan_progress(self, current: int, total: int, message: str):
        """스캔 진행률 업데이트

        Args:
            current: 현재 진행 수
            total: 전체 수
            message: 메시지
        """
        self.scan_view.update_progress(current, total)
        self.statusBar().showMessage(message)

    def _on_scan_log(self, message: str):
        """스캔 로그 메시지

        Args:
            message: 로그 메시지
        """
        self.scan_view.append_log(message)

    def _on_scan_finished(self, result):
        """스캔 완료

        Args:
            result: ScanResult 객체
        """
        self.last_scan_result = result

        self.statusBar().showMessage(f"스캔 완료! 점수: {result.score:.1f}/100")
        self.scan_completed.emit()

        # 결과 표시
        self.result_view.load_result(result)
        self.tab_widget.setCurrentWidget(self.result_view)

        # Excel 보고서 저장 옵션
        reply = QMessageBox.question(
            self,
            "보고서 저장",
            "Excel 보고서를 저장하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self._save_report(result)

    def _on_scan_error(self, error_message: str):
        """스캔 오류

        Args:
            error_message: 오류 메시지
        """
        self.statusBar().showMessage(f"스캔 실패: {error_message}")
        QMessageBox.critical(self, "스캔 오류", f"스캔 중 오류가 발생했습니다:\n\n{error_message}")

    def _save_report(self, result):
        """Excel 보고서 저장

        Args:
            result: ScanResult 객체
        """
        # 기본 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bluepy_report_{result.server_id}_{timestamp}.xlsx"

        # 파일 저장 대화상자
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "보고서 저장",
            str(Path("data/reports") / default_filename),
            "Excel Files (*.xlsx)",
        )

        if filename:
            try:
                reporter = ExcelReporter()
                output_path = reporter.generate(
                    result, filename, server_name=self.current_server.get("name")
                )

                QMessageBox.information(
                    self, "저장 완료", f"보고서가 저장되었습니다:\n{output_path}"
                )
                self.statusBar().showMessage(f"보고서 저장됨: {output_path}")

            except Exception as e:
                QMessageBox.critical(
                    self, "저장 실패", f"보고서 저장 중 오류가 발생했습니다:\n\n{str(e)}"
                )

    def _show_about(self):
        """정보 대화상자 표시"""
        QMessageBox.about(
            self,
            "BluePy 2.0 정보",
            "<h3>BluePy 2.0</h3>"
            "<p>멀티플랫폼 인프라 보안 점검 및 자동 수정 도구</p>"
            "<p>버전: 2.0.0</p>"
            "<p>Copyright 2025</p>",
        )

    def _on_remediate_requested(self, rule_id: str, rule_name: str, status: str):
        """자동 수정 요청 핸들러

        Args:
            rule_id: 규칙 ID (예: M-03)
            rule_name: 규칙 이름
            status: 현재 상태 (FAIL 등)
        """
        # 서버 정보 확인
        if not self.current_server:
            QMessageBox.warning(
                self, "서버 선택 필요", "먼저 자동 수정할 서버를 선택하세요."
            )
            return

        # 플랫폼 확인 (현재 macOS만 지원)
        platform = self.current_server.get("platform", "linux")
        if platform not in ["macos", "linux"]:
            QMessageBox.warning(
                self,
                "지원하지 않는 플랫폼",
                f"현재 {platform} 플랫폼의 자동 수정은 지원되지 않습니다.\n"
                "macOS와 Linux만 지원됩니다.",
            )
            return

        # RemediationDialog 생성 및 실행
        dialog = RemediationDialog(
            parent=self,
            rule_id=rule_id,
            rule_name=rule_name,
            server=self.current_server,
        )

        # 모달 대화상자로 실행
        dialog.exec()

        # 대화상자 종료 후 상태 업데이트
        self.statusBar().showMessage(f"{rule_id} 자동 수정 대화상자 종료")

    def update_status(self, message: str):
        """상태 메시지 업데이트

        Args:
            message: 표시할 메시지
        """
        self.statusBar().showMessage(message)

    def _on_toggle_theme(self):
        """테마 토글 슬롯

        다크 모드와 라이트 모드를 전환합니다.
        """
        from .theme_manager import get_theme_manager

        theme_manager = get_theme_manager()
        theme_manager.toggle_theme()

        # 상태바 메시지 업데이트
        current_theme = theme_manager.get_current_theme()
        theme_name = "다크 모드" if current_theme.value == "dark" else "라이트 모드"
        self.statusBar().showMessage(f"테마 변경: {theme_name}")

    def _on_open_settings(self):
        """설정 대화상자 열기 핸들러

        설정 대화상자를 모달로 열고, 저장 시 즉시 적용합니다.
        """
        dialog = SettingsDialog(self)

        if dialog.exec():
            # 설정이 저장되었으므로 재로드
            self.app_settings = load_settings()

            # 테마 적용
            theme = get_setting(self.app_settings, "appearance.theme", "dark")
            self._apply_theme(theme)

            # 상태바 메시지
            self.statusBar().showMessage("설정이 저장되었습니다.")

    def _apply_theme(self, theme: str):
        """테마 적용

        Args:
            theme: 테마 이름 ("dark" 또는 "light")
        """
        from .theme_manager import get_theme_manager, Theme

        theme_manager = get_theme_manager()
        theme_enum = Theme.DARK if theme == "dark" else Theme.LIGHT

        # 현재 테마와 다르면 변경
        if theme_manager.get_current_theme() != theme_enum:
            theme_manager.set_theme(QApplication.instance(), theme_enum)


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
