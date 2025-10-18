"""스캔 실행 뷰

보안 점검 스캔을 실행하고 진행 상황을 표시하는 뷰입니다.

주요 기능:
- 스캔 시작/중지
- 진행률 표시
- 상태 메시지 표시
"""

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ScanView(QWidget):
    """스캔 실행 뷰 클래스

    스캔 실행 및 진행 상황을 표시하는 위젯입니다.

    Signals:
        scan_requested: 스캔 시작 요청
        scan_stopped: 스캔 중지 요청
    """

    # 커스텀 시그널
    scan_requested = Signal()
    scan_stopped = Signal()

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)

        self._is_scanning = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 서버 정보 그룹
        server_group = QGroupBox("서버 정보")
        server_layout = QVBoxLayout()

        self.server_label = QLabel("서버: 선택되지 않음")
        self.server_label.setStyleSheet("font-weight: bold;")
        server_layout.addWidget(self.server_label)

        self.platform_label = QLabel("플랫폼: -")
        server_layout.addWidget(self.platform_label)

        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        # 스캔 제어 그룹
        control_group = QGroupBox("스캔 제어")
        control_layout = QVBoxLayout()

        # 스캔 버튼
        self.scan_button = QPushButton("스캔 시작")
        self.scan_button.setMinimumHeight(40)
        self.scan_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        )
        control_layout.addWidget(self.scan_button)

        # 진행률 표시
        self.progress_label = QLabel("진행률: 0 / 0")
        control_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        control_layout.addWidget(self.progress_bar)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 로그 그룹
        log_group = QGroupBox("스캔 로그")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 여백 추가
        layout.addStretch()

    def _connect_signals(self):
        """시그널 연결"""
        self.scan_button.clicked.connect(self._on_scan_button_clicked)

    def _on_scan_button_clicked(self):
        """스캔 버튼 클릭 핸들러"""
        if not self._is_scanning:
            # 스캔 시작
            self._start_scan()
        else:
            # 스캔 중지
            self._stop_scan()

    def _start_scan(self):
        """스캔 시작"""
        self._is_scanning = True

        # UI 업데이트
        self.scan_button.setText("스캔 중지")
        self.scan_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )

        self.log_text.clear()
        self.append_log("스캔을 시작합니다...")

        # 시그널 발생
        self.scan_requested.emit()

        # TODO: 실제 스캔 로직 연결
        # 데모용 시뮬레이션
        self._simulate_scan()

    def _stop_scan(self):
        """스캔 중지"""
        self._is_scanning = False

        # UI 업데이트
        self.scan_button.setText("스캔 시작")
        self.scan_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )

        self.append_log("스캔이 중지되었습니다.")

        # 시그널 발생
        self.scan_stopped.emit()

    def _simulate_scan(self):
        """스캔 시뮬레이션 (데모용)

        TODO: 실제 스캔 로직으로 대체
        """
        self.update_progress(0, 73)

        # 타이머로 진행률 시뮬레이션
        self._progress = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_simulation)
        self._timer.start(100)  # 100ms마다 업데이트

    def _update_simulation(self):
        """시뮬레이션 업데이트"""
        if not self._is_scanning:
            self._timer.stop()
            return

        self._progress += 1
        self.update_progress(self._progress, 73)
        self.append_log(f"U-{self._progress:02d} 점검 중...")

        if self._progress >= 73:
            self._timer.stop()
            self._stop_scan()
            self.append_log("스캔이 완료되었습니다!")

    def set_server(self, server_id: str, server_name: str, platform: str = "linux"):
        """서버 설정

        Args:
            server_id: 서버 ID
            server_name: 서버 이름
            platform: 플랫폼 (linux, macos, windows)
        """
        self.server_label.setText(f"서버: {server_name}")
        self.platform_label.setText(f"플랫폼: {platform}")
        self.scan_button.setEnabled(True)

    def update_progress(self, current: int, total: int):
        """진행률 업데이트

        Args:
            current: 현재 진행 수
            total: 전체 수
        """
        self.progress_label.setText(f"진행률: {current} / {total}")

        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
        else:
            self.progress_bar.setValue(0)

    def append_log(self, message: str):
        """로그 메시지 추가

        Args:
            message: 로그 메시지
        """
        self.log_text.append(message)
        # 스크롤을 맨 아래로
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
