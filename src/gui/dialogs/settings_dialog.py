"""설정 대화상자

애플리케이션 설정을 변경하는 대화상자입니다.

주요 기능:
- 테마 선택 (Light/Dark)
- 로그 레벨 선택
- 언어 선택
- 백업 디렉토리 경로 설정
"""


from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ...infrastructure.config.settings import (
    load_settings,
    save_settings,
    get_setting,
    set_setting,
)


class SettingsDialog(QDialog):
    """설정 대화상자

    애플리케이션 설정을 변경하는 폼 대화상자입니다.

    설정 항목:
    - 테마: Light/Dark 모드
    - 로그 레벨: DEBUG/INFO/WARNING/ERROR
    - 언어: 한국어/English (현재는 UI만 제공)
    - 백업 디렉토리: 경로 설정
    """

    def __init__(self, parent=None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)

        # 현재 설정 로드
        self.settings = load_settings()

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """UI 구성"""
        # 윈도우 설정
        self.setWindowTitle("설정")
        self.setMinimumWidth(500)

        # 메인 레이아웃
        layout = QVBoxLayout(self)

        # 외관 설정 그룹
        appearance_group = QGroupBox("외관")
        appearance_layout = QFormLayout()

        # 테마 선택
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setToolTip("애플리케이션 색상 테마를 선택합니다")
        appearance_layout.addRow("테마:", self.theme_combo)

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # 로깅 설정 그룹
        logging_group = QGroupBox("로깅")
        logging_layout = QFormLayout()

        # 로그 레벨 선택
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setToolTip(
            "로그 출력 레벨을 선택합니다\n"
            "DEBUG: 모든 로그\n"
            "INFO: 일반 정보 이상\n"
            "WARNING: 경고 이상\n"
            "ERROR: 오류만"
        )
        logging_layout.addRow("로그 레벨:", self.log_level_combo)

        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

        # 언어 설정 그룹
        language_group = QGroupBox("언어")
        language_layout = QFormLayout()

        # 언어 선택
        self.language_combo = QComboBox()
        self.language_combo.addItems(["한국어", "English"])
        self.language_combo.setToolTip(
            "애플리케이션 언어를 선택합니다\n" "(현재는 준비 단계입니다)"
        )
        self.language_combo.setEnabled(False)  # 아직 미구현
        language_layout.addRow("언어:", self.language_combo)

        # 안내 레이블
        language_note = QLabel("언어 전환 기능은 향후 업데이트 예정입니다.")
        language_note.setStyleSheet("color: gray; font-size: 10px;")
        language_layout.addRow("", language_note)

        language_group.setLayout(language_layout)
        layout.addWidget(language_group)

        # 백업 설정 그룹
        backup_group = QGroupBox("백업")
        backup_layout = QFormLayout()

        # 백업 디렉토리 경로
        backup_path_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setPlaceholderText("예: data/backups")
        self.backup_path_edit.setToolTip("자동 수정 시 원본 파일을 백업할 디렉토리 경로")

        self.backup_path_button = QPushButton("찾아보기...")
        self.backup_path_button.clicked.connect(self._on_browse_backup_directory)
        self.backup_path_button.setToolTip("디렉토리 선택 대화상자 열기")

        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(self.backup_path_button)

        backup_layout.addRow("백업 디렉토리:", backup_path_layout)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Save).setText("저장")
        button_box.button(QDialogButtonBox.Cancel).setText("취소")

        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # 안내 문구
        help_label = QLabel("설정 변경 후 '저장'을 눌러야 적용됩니다.")
        help_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(help_label)

    def _load_current_settings(self):
        """현재 설정 로드

        저장된 설정 파일에서 값을 읽어 UI에 표시합니다.
        """
        # 테마 설정
        theme = get_setting(self.settings, "appearance.theme", "dark")
        theme_display = "Dark" if theme == "dark" else "Light"
        self.theme_combo.setCurrentText(theme_display)

        # 로그 레벨 설정
        log_level = get_setting(self.settings, "logging.level", "INFO")
        self.log_level_combo.setCurrentText(log_level)

        # 언어 설정
        locale = get_setting(self.settings, "language.locale", "ko_KR")
        language_display = "한국어" if locale == "ko_KR" else "English"
        self.language_combo.setCurrentText(language_display)

        # 백업 디렉토리 설정
        backup_dir = get_setting(self.settings, "backup.directory", "data/backups")
        self.backup_path_edit.setText(backup_dir)

    def _on_browse_backup_directory(self):
        """백업 디렉토리 찾아보기 핸들러

        파일 선택 대화상자를 열어 디렉토리를 선택합니다.
        """
        current_path = self.backup_path_edit.text() or "data/backups"

        directory = QFileDialog.getExistingDirectory(
            self,
            "백업 디렉토리 선택",
            current_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if directory:
            self.backup_path_edit.setText(directory)

    def _on_save(self):
        """저장 버튼 핸들러

        UI의 값을 읽어 설정 파일로 저장합니다.
        """
        # 유효성 검사: 백업 디렉토리
        backup_path = self.backup_path_edit.text().strip()
        if not backup_path:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "입력 오류", "백업 디렉토리를 입력하세요.")
            return

        # 설정 값 업데이트
        # 테마
        theme_display = self.theme_combo.currentText()
        theme_value = "dark" if theme_display == "Dark" else "light"
        set_setting(self.settings, "appearance.theme", theme_value)

        # 로그 레벨
        log_level = self.log_level_combo.currentText()
        set_setting(self.settings, "logging.level", log_level)

        # 언어
        language_display = self.language_combo.currentText()
        locale_value = "ko_KR" if language_display == "한국어" else "en_US"
        set_setting(self.settings, "language.locale", locale_value)

        # 백업 디렉토리
        set_setting(self.settings, "backup.directory", backup_path)

        # 설정 파일 저장
        success = save_settings(self.settings)

        if success:
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "저장 실패", "설정 파일 저장 중 오류가 발생했습니다.")

    def get_settings(self) -> dict:
        """저장된 설정 반환

        Returns:
            설정 딕셔너리
        """
        return self.settings


__all__ = [
    "SettingsDialog",
]
