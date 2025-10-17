"""서버 목록 뷰

서버 관리 기능을 제공하는 뷰입니다.

주요 기능:
- 서버 목록 표시
- 서버 추가/편집/삭제
- 서버 선택
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
)


class ServerView(QWidget):
    """서버 목록 뷰 클래스

    서버 목록을 표시하고 관리하는 위젯입니다.

    Signals:
        server_selected: 서버가 선택되었을 때 발생 (server_id: str)
        add_requested: 서버 추가 요청
        edit_requested: 서버 편집 요청 (server_id: str)
        delete_requested: 서버 삭제 요청 (server_id: str)
    """

    # 커스텀 시그널
    server_selected = Signal(str)
    add_requested = Signal()
    edit_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()
        self._load_sample_data()

    def _setup_ui(self):
        """UI 구성"""
        # 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 서버 목록
        self.server_list = QListWidget()
        self.server_list.setAlternatingRowColors(True)
        layout.addWidget(self.server_list)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 추가 버튼
        self.add_button = QPushButton("추가")
        self.add_button.setToolTip("새 서버 추가")
        button_layout.addWidget(self.add_button)

        # 편집 버튼
        self.edit_button = QPushButton("편집")
        self.edit_button.setToolTip("선택한 서버 편집")
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)

        # 삭제 버튼
        self.delete_button = QPushButton("삭제")
        self.delete_button.setToolTip("선택한 서버 삭제")
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """시그널 연결"""
        # 서버 선택
        self.server_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.server_list.itemDoubleClicked.connect(self._on_item_double_clicked)

        # 버튼
        self.add_button.clicked.connect(self._on_add_clicked)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

    def _load_sample_data(self):
        """샘플 데이터 로드

        TODO: DB에서 실제 데이터 로드
        """
        sample_servers = [
            "server-001 (192.168.1.100)",
            "server-002 (192.168.1.101)",
            "server-003 (192.168.1.102)",
        ]

        for server in sample_servers:
            item = QListWidgetItem(server)
            # 서버 ID를 data로 저장 (실제로는 DB ID 사용)
            item.setData(Qt.UserRole, server.split()[0])
            self.server_list.addItem(item)

    def _on_selection_changed(self):
        """선택 변경 핸들러"""
        has_selection = len(self.server_list.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            item = self.server_list.selectedItems()[0]
            server_id = item.data(Qt.UserRole)
            self.server_selected.emit(server_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """아이템 더블 클릭 핸들러

        Args:
            item: 클릭된 아이템
        """
        server_id = item.data(Qt.UserRole)
        self.edit_requested.emit(server_id)

    def _on_add_clicked(self):
        """추가 버튼 핸들러"""
        self.add_requested.emit()

    def _on_edit_clicked(self):
        """편집 버튼 핸들러"""
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        server_id = item.data(Qt.UserRole)
        self.edit_requested.emit(server_id)

    def _on_delete_clicked(self):
        """삭제 버튼 핸들러"""
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        server_id = item.data(Qt.UserRole)

        # 확인 대화상자
        reply = QMessageBox.question(
            self,
            "서버 삭제",
            f"'{item.text()}' 서버를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.delete_requested.emit(server_id)
            # TODO: DB에서 삭제 후 목록 갱신
            self.server_list.takeItem(self.server_list.row(item))

    def add_server(self, server_id: str, server_name: str, host: str):
        """서버 추가

        Args:
            server_id: 서버 ID
            server_name: 서버 이름
            host: 호스트 주소
        """
        item = QListWidgetItem(f"{server_name} ({host})")
        item.setData(Qt.UserRole, server_id)
        self.server_list.addItem(item)

    def refresh(self):
        """목록 새로고침

        TODO: DB에서 서버 목록 다시 로드
        """
        self.server_list.clear()
        self._load_sample_data()