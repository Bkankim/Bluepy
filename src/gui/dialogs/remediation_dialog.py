"""Remediation Dialog

자동 수정 미리보기 및 실행 대화상자입니다.
Dry-run으로 실행 계획을 확인한 후 실제 수정을 진행합니다.
"""

from typing import Optional, Dict

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QTextEdit,
    QPushButton,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import Qt

from ...core.domain.models import RemediationResult
from ..workers.remediation_worker import RemediationWorker


class RemediationDialog(QDialog):
    """자동 수정 대화상자

    특정 규칙에 대한 자동 수정을 Dry-run으로 미리보고 실행합니다.

    Attributes:
        rule_id: 규칙 ID (예: M-03)
        rule_name: 규칙 이름
        server: 서버 정보 딕셔너리
        preview_result: Dry-run 결과 (RemediationResult)
        worker: RemediationWorker 인스턴스
    """

    def __init__(
        self,
        parent=None,
        rule_id: str = "",
        rule_name: str = "",
        server: Optional[Dict] = None,
    ):
        """초기화

        Args:
            parent: 부모 위젯
            rule_id: 규칙 ID
            rule_name: 규칙 이름
            server: 서버 정보 딕셔너리 (server_id, host, username, platform 등)
        """
        super().__init__(parent)

        self.rule_id = rule_id
        self.rule_name = rule_name
        self.server = server or {}

        self.preview_result: Optional[RemediationResult] = None
        self.worker: Optional[RemediationWorker] = None

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.setWindowTitle(f"자동 수정 - {self.rule_id}")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # 1. 규칙 정보 그룹
        info_group = self._create_info_group()
        layout.addWidget(info_group)

        # 2. 로그 영역
        log_label = QLabel("실행 로그:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        layout.addWidget(self.log_text)

        # 3. 진행 상황
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 4. 버튼 영역
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)

    def _create_info_group(self) -> QGroupBox:
        """규칙 정보 그룹 생성

        Returns:
            QGroupBox: 규칙 정보 그룹박스
        """
        group = QGroupBox("규칙 정보")
        layout = QVBoxLayout()

        # 규칙 ID 및 이름
        rule_label = QLabel(f"<b>{self.rule_id}</b>: {self.rule_name}")
        layout.addWidget(rule_label)

        # 서버 정보
        server_name = self.server.get("name", self.server.get("server_id", "알 수 없음"))
        server_host = self.server.get("host", "")
        platform = self.server.get("platform", "").upper()

        server_label = QLabel(f"서버: {server_name} ({server_host}) [{platform}]")
        layout.addWidget(server_label)

        group.setLayout(layout)
        return group

    def _create_button_layout(self) -> QHBoxLayout:
        """버튼 레이아웃 생성

        Returns:
            QHBoxLayout: 버튼 레이아웃
        """
        button_layout = QHBoxLayout()

        # 미리보기 버튼
        self.preview_btn = QPushButton("미리보기 (Dry-run)")
        self.preview_btn.setToolTip("실제 실행 없이 수정 계획을 확인합니다")
        self.preview_btn.clicked.connect(self._on_preview)
        button_layout.addWidget(self.preview_btn)

        # 실행 버튼
        self.execute_btn = QPushButton("실행")
        self.execute_btn.setToolTip("자동 수정을 실제로 실행합니다")
        self.execute_btn.setEnabled(False)  # 미리보기 후 활성화
        self.execute_btn.clicked.connect(self._on_execute)
        button_layout.addWidget(self.execute_btn)

        button_layout.addStretch()

        # 닫기 버튼
        self.close_btn = QPushButton("닫기")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        return button_layout

    def _on_preview(self):
        """미리보기 (Dry-run) 실행"""
        if not self.server:
            QMessageBox.warning(self, "오류", "서버 정보가 없습니다.")
            return

        # 로그 초기화
        self.log_text.clear()
        self._append_log("=== Dry-run 시작 ===")

        # Worker 생성 (Dry-run 모드)
        self.worker = RemediationWorker(
            server_id=self.server.get("server_id", ""),
            host=self.server["host"],
            username=self.server["username"],
            platform=self.server["platform"],
            rule_id=self.rule_id,
            password=self.server.get("password"),
            key_filename=self.server.get("key_path"),
            port=self.server.get("port", 22),
            dry_run=True,  # Dry-run 모드
        )

        # 시그널 연결
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_preview_finished)
        self.worker.error.connect(self._on_error)

        # UI 상태 업데이트
        self.preview_btn.setEnabled(False)
        self.execute_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Worker 시작
        self.worker.start()

    def _on_execute(self):
        """실제 자동 수정 실행"""
        # 확인 대화상자
        reply = QMessageBox.question(
            self,
            "확인",
            f"정말로 {self.rule_id}을(를) 자동 수정하시겠습니까?\n\n"
            f"백업이 자동으로 생성되지만, 신중하게 진행하세요.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # 로그 초기화
        self.log_text.clear()
        self._append_log("=== 자동 수정 실행 시작 ===")

        # Worker 생성 (실제 실행 모드)
        self.worker = RemediationWorker(
            server_id=self.server.get("server_id", ""),
            host=self.server["host"],
            username=self.server["username"],
            platform=self.server["platform"],
            rule_id=self.rule_id,
            password=self.server.get("password"),
            key_filename=self.server.get("key_path"),
            port=self.server.get("port", 22),
            dry_run=False,  # 실제 실행 모드
        )

        # 시그널 연결
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_execute_finished)
        self.worker.error.connect(self._on_error)

        # UI 상태 업데이트
        self.preview_btn.setEnabled(False)
        self.execute_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Worker 시작
        self.worker.start()

    def _on_preview_finished(self, result: RemediationResult):
        """Dry-run 완료 처리

        Args:
            result: Dry-run 결과
        """
        self.preview_result = result

        # 진행바 숨김
        self.progress_bar.setVisible(False)

        # 결과 표시
        self._append_log("=== Dry-run 완료 ===")
        self._append_log("")

        if result.success:
            self._append_log("[미리보기 결과]")
            self._append_log(result.message)

            if result.executed_commands:
                self._append_log("")
                self._append_log("실행될 명령어:")
                for cmd in result.executed_commands:
                    self._append_log(f"  - {cmd}")

            # 실행 버튼 활성화
            self.execute_btn.setEnabled(True)
            self._append_log("")
            self._append_log("[안내] '실행' 버튼을 클릭하면 위 명령어가 실제로 실행됩니다.")

        else:
            self._append_log(f"[오류] {result.message}")
            if result.error:
                self._append_log(f"상세: {result.error}")

        # 미리보기 버튼 재활성화
        self.preview_btn.setEnabled(True)

    def _on_execute_finished(self, result: RemediationResult):
        """실제 실행 완료 처리

        Args:
            result: 실행 결과
        """
        # 진행바 숨김
        self.progress_bar.setVisible(False)

        # 결과 표시
        self._append_log("=== 자동 수정 완료 ===")
        self._append_log("")

        if result.success:
            self._append_log("[성공] " + result.message)

            if result.backup_id:
                self._append_log(f"백업 ID: {result.backup_id}")
                self._append_log("(향후 롤백 기능에서 사용 가능)")

            QMessageBox.information(
                self,
                "성공",
                f"자동 수정이 완료되었습니다!\n\n{result.message}",
            )

        else:
            self._append_log("[실패] " + result.message)

            if result.error:
                self._append_log(f"오류: {result.error}")

            if result.rollback_performed:
                self._append_log("[롤백] 변경사항이 자동으로 롤백되었습니다.")

            QMessageBox.critical(
                self,
                "실패",
                f"자동 수정 실패:\n\n{result.message}\n\n"
                + (f"오류: {result.error}" if result.error else ""),
            )

        # 버튼 상태 복원
        self.preview_btn.setEnabled(True)
        self.execute_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def _on_progress(self, current: int, total: int, message: str):
        """진행률 업데이트

        Args:
            current: 현재 진행
            total: 전체 작업
            message: 진행 메시지
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)

        self._append_log(f"[진행] {message}")

    def _on_error(self, error_message: str):
        """오류 처리

        Args:
            error_message: 오류 메시지
        """
        self.progress_bar.setVisible(False)

        self._append_log("=== 오류 발생 ===")
        self._append_log(error_message)

        QMessageBox.critical(self, "오류", error_message)

        # 버튼 상태 복원
        self.preview_btn.setEnabled(True)
        self.execute_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def _append_log(self, message: str):
        """로그 메시지 추가

        Args:
            message: 로그 메시지
        """
        self.log_text.append(message)

        # 자동 스크롤 (맨 아래로)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


__all__ = ["RemediationDialog"]
