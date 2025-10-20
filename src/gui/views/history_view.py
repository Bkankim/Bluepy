"""스캔 이력 뷰

스캔 이력을 표시하고 트렌드 차트를 제공하는 뷰입니다.

주요 기능:
- 스캔 이력 목록 표시 (QTableWidget)
- 트렌드 차트 표시 (PyQtGraph)
- 서버별 이력 조회
- 날짜/점수 포맷팅
"""

from datetime import datetime
from typing import Optional

import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
)
from PySide6.QtGui import QColor

from ...infrastructure.database.repositories import HistoryRepository


class HistoryView(QWidget):
    """스캔 이력 뷰 클래스

    스캔 이력 목록과 트렌드 차트를 표시하는 위젯입니다.

    Signals:
        history_selected: 이력이 선택되었을 때 발생 (history_id: int)
    """

    # 커스텀 시그널
    history_selected = Signal(int)  # history_id

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)

        # 상태 변수
        self.db_session = None
        self.history_repository = None
        self.current_server_id = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """UI 구성"""
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 제목 라벨
        title_label = QLabel("스캔 이력 및 트렌드")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # QSplitter (좌우 분할)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # === 왼쪽 패널: 이력 목록 ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 이력 목록 라벨
        history_label = QLabel("스캔 이력")
        history_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(history_label)

        # 이력 테이블
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["날짜/시간", "점수", "통과", "실패", "수동", "전체"]
        )
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 컬럼 너비 설정
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 날짜/시간
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 점수
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 통과
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 실패
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 수동
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 전체

        self.history_table.setColumnWidth(1, 60)  # 점수
        self.history_table.setColumnWidth(2, 60)  # 통과
        self.history_table.setColumnWidth(3, 60)  # 실패
        self.history_table.setColumnWidth(4, 60)  # 수동
        self.history_table.setColumnWidth(5, 60)  # 전체

        left_layout.addWidget(self.history_table)
        splitter.addWidget(left_widget)

        # === 오른쪽 패널: 트렌드 차트 ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 차트 라벨
        chart_label = QLabel("점수 트렌드 (최근 30일)")
        chart_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(chart_label)

        # PyQtGraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")  # 흰색 배경
        self.plot_widget.setLabel("left", "점수", units="점")
        self.plot_widget.setLabel("bottom", "날짜")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.addLegend()

        right_layout.addWidget(self.plot_widget)
        splitter.addWidget(right_widget)

        # Splitter 비율 설정 (50:50)
        splitter.setSizes([400, 400])

    def _connect_signals(self):
        """시그널 연결"""
        # 테이블 선택 시그널
        self.history_table.itemSelectionChanged.connect(self._on_selection_changed)

    def set_database_session(self, session):
        """데이터베이스 세션 설정

        Args:
            session: SQLAlchemy Session
        """
        self.db_session = session
        self.history_repository = HistoryRepository(session)

    def load_history(self, server_id: int):
        """서버의 스캔 이력 로드

        Args:
            server_id: 서버 ID
        """
        if not self.history_repository:
            print("Warning: HistoryRepository not initialized")
            return

        self.current_server_id = server_id

        # 이력 목록 로드
        histories = self.history_repository.get_history_by_server(server_id, limit=30)
        self._populate_table(histories)

        # 트렌드 데이터 로드
        trend_data = self.history_repository.get_trend_data(server_id, days=30)
        self._plot_trend_data(trend_data)

    def _populate_table(self, histories):
        """이력 테이블 채우기

        Args:
            histories: ScanHistory 객체 리스트
        """
        self.history_table.setRowCount(0)

        for history in histories:
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)

            # 날짜/시간
            date_item = QTableWidgetItem(
                history.scan_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            self.history_table.setItem(row_position, 0, date_item)

            # 점수 (색상 코딩)
            score_item = QTableWidgetItem(str(history.score))
            score_item.setTextAlignment(Qt.AlignCenter)
            score_color = self._get_score_color(history.score)
            score_item.setForeground(score_color)
            self.history_table.setItem(row_position, 1, score_item)

            # 통과
            passed_item = QTableWidgetItem(str(history.passed))
            passed_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_position, 2, passed_item)

            # 실패
            failed_item = QTableWidgetItem(str(history.failed))
            failed_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_position, 3, failed_item)

            # 수동
            manual_item = QTableWidgetItem(str(history.manual))
            manual_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_position, 4, manual_item)

            # 전체
            total_item = QTableWidgetItem(str(history.total))
            total_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_position, 5, total_item)

            # ID를 데이터로 저장 (숨김)
            date_item.setData(Qt.UserRole, history.id)

    def _plot_trend_data(self, trend_data):
        """트렌드 차트 그리기

        Args:
            trend_data: 트렌드 데이터 리스트 (dict)
        """
        self.plot_widget.clear()

        if not trend_data:
            return

        # 데이터 추출
        timestamps = [
            int(d["scan_time"].timestamp()) for d in trend_data
        ]  # Unix timestamp
        scores = [d["score"] for d in trend_data]
        passed = [d["passed"] for d in trend_data]
        failed = [d["failed"] for d in trend_data]

        # 점수 그래프 (파란색)
        score_plot = self.plot_widget.plot(
            timestamps,
            scores,
            pen=pg.mkPen(color="b", width=2),
            symbol="o",
            symbolSize=6,
            symbolBrush="b",
            name="점수",
        )

        # X축 날짜 포맷팅
        if timestamps:
            axis = self.plot_widget.getAxis("bottom")
            axis.setTicks([self._create_date_ticks(timestamps)])

    def _create_date_ticks(self, timestamps):
        """날짜 눈금 생성

        Args:
            timestamps: Unix timestamp 리스트

        Returns:
            (timestamp, label) 튜플 리스트
        """
        ticks = []
        for ts in timestamps[::max(1, len(timestamps) // 5)]:  # 최대 5개 눈금
            date_str = datetime.fromtimestamp(ts).strftime("%m/%d")
            ticks.append((ts, date_str))
        return ticks

    def _get_score_color(self, score: int) -> QColor:
        """점수에 따른 색상 반환

        Args:
            score: 점수 (0-100)

        Returns:
            QColor 객체
        """
        if score >= 80:
            return QColor("#4CAF50")  # 녹색 (양호)
        elif score >= 60:
            return QColor("#FF9800")  # 주황색 (경고)
        else:
            return QColor("#F44336")  # 빨간색 (취약)

    def _on_selection_changed(self):
        """테이블 선택 변경 슬롯"""
        selected_items = self.history_table.selectedItems()

        if selected_items:
            # 첫 번째 컬럼의 아이템에서 ID 가져오기
            row = selected_items[0].row()
            date_item = self.history_table.item(row, 0)
            history_id = date_item.data(Qt.UserRole)

            # 시그널 발생
            self.history_selected.emit(history_id)

    def clear(self):
        """뷰 초기화"""
        self.history_table.setRowCount(0)
        self.plot_widget.clear()
        self.current_server_id = None
