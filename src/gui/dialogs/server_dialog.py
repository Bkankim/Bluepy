"""서버 추가/편집 대화상자

서버 정보를 입력받는 대화상자입니다.

주요 기능:
- 서버 정보 입력 폼
- 유효성 검사
- 연결 테스트 (TODO)
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class ServerDialog(QDialog):
    """서버 추가/편집 대화상자

    서버 정보를 입력받는 폼 대화상자입니다.
    """

    def __init__(self, parent=None, server_data=None):
        """초기화

        Args:
            parent: 부모 위젯
            server_data: 편집할 서버 데이터 (None이면 추가 모드)
        """
        super().__init__(parent)

        self.server_data = server_data
        self.is_edit_mode = server_data is not None

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """UI 구성"""
        # 윈도우 설정
        title = "서버 편집" if self.is_edit_mode else "서버 추가"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        # 레이아웃
        layout = QVBoxLayout(self)

        # 기본 정보 그룹
        basic_group = QGroupBox("기본 정보")
        basic_layout = QFormLayout()

        # 서버 이름
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("예: server-001")
        basic_layout.addRow("서버 이름*:", self.name_edit)

        # 호스트 주소
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("예: 192.168.1.100 또는 example.com")
        basic_layout.addRow("호스트*:", self.host_edit)

        # 플랫폼
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["linux", "macos", "windows"])
        basic_layout.addRow("플랫폼*:", self.platform_combo)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # SSH 설정 그룹
        ssh_group = QGroupBox("SSH 설정")
        ssh_layout = QFormLayout()

        # 사용자명
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("예: root 또는 admin")
        ssh_layout.addRow("사용자명*:", self.username_edit)

        # 포트
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        ssh_layout.addRow("포트:", self.port_spin)

        # 인증 방법
        self.auth_method_combo = QComboBox()
        self.auth_method_combo.addItems(["password", "key"])
        ssh_layout.addRow("인증 방법:", self.auth_method_combo)

        # SSH 키 경로
        self.key_path_edit = QLineEdit()
        self.key_path_edit.setPlaceholderText("예: /home/user/.ssh/id_rsa")
        self.key_path_edit.setEnabled(False)
        ssh_layout.addRow("키 파일 경로:", self.key_path_edit)

        ssh_group.setLayout(ssh_layout)
        layout.addWidget(ssh_group)

        # 인증 방법 변경 시 키 경로 활성화/비활성화
        self.auth_method_combo.currentTextChanged.connect(self._on_auth_method_changed)

        # 추가 정보 그룹
        extra_group = QGroupBox("추가 정보")
        extra_layout = QFormLayout()

        # 설명
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("서버에 대한 간단한 설명 (선택사항)")
        extra_layout.addRow("설명:", self.description_edit)

        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)

        # 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # 안내 문구
        help_label = QLabel("* 필수 항목")
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(help_label)

    def _on_auth_method_changed(self, method: str):
        """인증 방법 변경 핸들러

        Args:
            method: 인증 방법 (password, key)
        """
        self.key_path_edit.setEnabled(method == "key")

    def _load_data(self):
        """기존 데이터 로드 (편집 모드)"""
        if not self.server_data:
            return

        self.name_edit.setText(self.server_data.get("name", ""))
        self.host_edit.setText(self.server_data.get("host", ""))
        self.platform_combo.setCurrentText(self.server_data.get("platform", "linux"))
        self.username_edit.setText(self.server_data.get("username", ""))
        self.port_spin.setValue(self.server_data.get("port", 22))
        self.auth_method_combo.setCurrentText(self.server_data.get("auth_method", "password"))
        self.key_path_edit.setText(self.server_data.get("key_path", ""))
        self.description_edit.setPlainText(self.server_data.get("description", ""))

    def _on_accept(self):
        """확인 버튼 핸들러"""
        # 유효성 검사
        if not self.name_edit.text().strip():
            # TODO: 경고 메시지 표시
            return

        if not self.host_edit.text().strip():
            return

        if not self.username_edit.text().strip():
            return

        # 키 인증 방식일 때 키 경로 확인
        if self.auth_method_combo.currentText() == "key":
            if not self.key_path_edit.text().strip():
                return

        self.accept()

    def get_data(self) -> dict:
        """입력된 데이터 반환

        Returns:
            서버 정보 딕셔너리
        """
        return {
            "name": self.name_edit.text().strip(),
            "host": self.host_edit.text().strip(),
            "platform": self.platform_combo.currentText(),
            "username": self.username_edit.text().strip(),
            "port": self.port_spin.value(),
            "auth_method": self.auth_method_combo.currentText(),
            "key_path": self.key_path_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
        }


__all__ = [
    "ServerDialog",
]
