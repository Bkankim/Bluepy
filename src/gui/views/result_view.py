"""결과 표시 뷰

보안 점검 결과를 트리 구조로 표시하는 뷰입니다.

주요 기능:
- 카테고리별 결과 트리
- 상태별 색상 표시 (PASS/FAIL/MANUAL)
- 상세 정보 표시
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QIcon
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QStyle,
    QApplication,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ResultView(QWidget):
    """결과 표시 뷰 클래스

    스캔 결과를 트리 형태로 표시하는 위젯입니다.

    Signals:
        item_selected: 항목이 선택되었을 때 발생 (rule_id: str)
        remediate_requested: 자동 수정 요청 (rule_id: str, rule_name: str, status: str)
    """

    # 커스텀 시그널
    item_selected = Signal(str)
    remediate_requested = Signal(str, str, str)  # rule_id, rule_name, status

    # 상태별 색상
    COLOR_PASS = QColor(76, 175, 80)  # 녹색
    COLOR_FAIL = QColor(244, 67, 54)  # 빨간색
    COLOR_MANUAL = QColor(255, 152, 0)  # 주황색

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 통계 그룹
        stats_group = QGroupBox("스캔 통계")
        stats_layout = QHBoxLayout()

        self.total_label = QLabel("전체: 0")
        stats_layout.addWidget(self.total_label)

        self.pass_label = QLabel("양호: 0")
        self.pass_label.setStyleSheet(f"color: {self.COLOR_PASS.name()};")
        stats_layout.addWidget(self.pass_label)

        self.fail_label = QLabel("취약: 0")
        self.fail_label.setStyleSheet(f"color: {self.COLOR_FAIL.name()};")
        stats_layout.addWidget(self.fail_label)

        self.manual_label = QLabel("수동: 0")
        self.manual_label.setStyleSheet(f"color: {self.COLOR_MANUAL.name()};")
        stats_layout.addWidget(self.manual_label)

        self.score_label = QLabel("점수: 0")
        self.score_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(self.score_label)

        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # 분할기
        splitter = QSplitter(Qt.Horizontal)

        # 결과 트리
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["항목", "상태", "메시지"])
        self.result_tree.setColumnWidth(0, 300)
        self.result_tree.setColumnWidth(1, 80)
        self.result_tree.setAlternatingRowColors(True)
        splitter.addWidget(self.result_tree)

        # 상세 정보
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)

        detail_label = QLabel("상세 정보")
        detail_label.setStyleSheet("font-weight: bold;")
        detail_layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)

        # 자동 수정 버튼
        button_layout = QHBoxLayout()

        self.remediate_btn = QPushButton("자동 수정")
        self.remediate_btn.setEnabled(False)
        self.remediate_btn.setToolTip("선택된 규칙을 자동으로 수정합니다 (지원되는 규칙만)")

        # 아이콘 추가 (표준 아이콘 사용)
        icon = QApplication.style().standardIcon(QStyle.SP_DialogApplyButton)
        self.remediate_btn.setIcon(icon)

        self.remediate_btn.clicked.connect(self._on_remediate_clicked)
        button_layout.addWidget(self.remediate_btn)

        button_layout.addStretch()
        detail_layout.addLayout(button_layout)

        splitter.addWidget(detail_widget)

        # 분할기 비율 설정 (2:1)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def _connect_signals(self):
        """시그널 연결"""
        self.result_tree.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_sample_data(self):
        """샘플 데이터 로드

        TODO: 실제 스캔 결과로 대체
        """
        # 카테고리별 샘플 데이터
        categories = {
            "계정관리": [
                ("U-01", "root 계정 원격 접속 제한", "PASS", "안전: pam_securetty 설정됨"),
                ("U-03", "계정잠금 임계값 설정", "FAIL", "취약: 임계값 미설정"),
                ("U-04", "패스워드 파일 보호", "PASS", "안전: Shadow 패스워드 사용"),
            ],
            "파일 및 디렉터리 관리": [
                ("U-18", "/etc/passwd 파일 소유자", "PASS", "안전: root 소유, 권한 정상"),
                ("U-27", "/dev 파일 점검", "MANUAL", "수동: device 파일 확인 필요"),
            ],
            "서비스 관리": [
                ("U-36", "Finger 서비스 비활성화", "PASS", "안전: 서비스 비활성화됨"),
                ("U-40", "DOS 취약 서비스", "FAIL", "취약: echo 서비스 활성화됨"),
            ],
        }

        for category, items in categories.items():
            # 카테고리 노드
            category_item = QTreeWidgetItem(self.result_tree)
            category_item.setText(0, category)
            category_item.setExpanded(True)
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsSelectable)

            # 항목 노드
            for rule_id, name, status, message in items:
                item = QTreeWidgetItem(category_item)
                item.setText(0, f"{rule_id}: {name}")
                item.setText(1, status)
                item.setText(2, message)
                item.setData(0, Qt.UserRole, rule_id)

                # 상태별 색상
                color = self._get_status_color(status)
                item.setForeground(1, QBrush(color))

        # 통계 업데이트
        self._update_statistics()

    def _get_status_color(self, status: str) -> QColor:
        """상태별 색상 반환

        Args:
            status: 상태 (PASS, FAIL, MANUAL)

        Returns:
            색상
        """
        if status == "PASS":
            return self.COLOR_PASS
        elif status == "FAIL":
            return self.COLOR_FAIL
        else:
            return self.COLOR_MANUAL

    def _on_selection_changed(self):
        """선택 변경 핸들러"""
        selected_items = self.result_tree.selectedItems()
        if not selected_items:
            self.detail_text.clear()
            self._update_remediate_button(None)
            return

        item = selected_items[0]
        rule_id = item.data(0, Qt.UserRole)

        if not rule_id:
            # 카테고리 선택
            self.detail_text.clear()
            self._update_remediate_button(None)
            return

        # 상세 정보 표시
        self._show_detail(item)

        # 자동 수정 버튼 상태 업데이트
        self._update_remediate_button(item)

        # 시그널 발생
        self.item_selected.emit(rule_id)

    def _show_detail(self, item: QTreeWidgetItem):
        """상세 정보 표시

        Args:
            item: 트리 아이템
        """
        rule_id = item.data(0, Qt.UserRole)
        name = item.text(0).split(": ", 1)[1] if ": " in item.text(0) else item.text(0)
        status = item.text(1)
        message = item.text(2)

        detail_html = f"""
        <h3>{rule_id}: {name}</h3>
        <p><b>상태:</b> <span style='color: {self._get_status_color(status).name()};'>{status}</span></p>
        <p><b>메시지:</b> {message}</p>
        <hr>
        <p><i>※ 상세 정보는 실제 스캔 결과 연동 시 표시됩니다.</i></p>
        """

        self.detail_text.setHtml(detail_html)

    def _update_statistics(self):
        """통계 업데이트"""
        total = 0
        pass_count = 0
        fail_count = 0
        manual_count = 0

        # 전체 항목 순회
        root = self.result_tree.invisibleRootItem()
        for i in range(root.childCount()):
            category = root.child(i)
            for j in range(category.childCount()):
                item = category.child(j)
                status = item.text(1)

                total += 1
                if status == "PASS":
                    pass_count += 1
                elif status == "FAIL":
                    fail_count += 1
                else:
                    manual_count += 1

        # 점수 계산
        if total > 0:
            score = ((pass_count + manual_count * 0.5) / total) * 100
        else:
            score = 0.0

        # 레이블 업데이트
        self.total_label.setText(f"전체: {total}")
        self.pass_label.setText(f"양호: {pass_count}")
        self.fail_label.setText(f"취약: {fail_count}")
        self.manual_label.setText(f"수동: {manual_count}")
        self.score_label.setText(f"점수: {score:.1f}")

    def clear(self):
        """결과 지우기"""
        self.result_tree.clear()
        self.detail_text.clear()
        self._update_statistics()

    def load_result(self, scan_result):
        """스캔 결과 로드

        Args:
            scan_result: ScanResult 객체

        TODO: 실제 ScanResult 객체 연동
        """
        self.clear()
        # TODO: scan_result에서 데이터 추출하여 트리 구성
        self._load_sample_data()

    def _update_remediate_button(self, item: QTreeWidgetItem):
        """자동 수정 버튼 상태 업데이트

        Args:
            item: 트리 아이템 (None이면 버튼 비활성화)
        """
        if not item:
            self.remediate_btn.setEnabled(False)
            return

        status = item.text(1)
        rule_id = item.data(0, Qt.UserRole)

        # TODO: 실제 규칙 메타데이터에서 remediation.auto 확인
        # 현재는 샘플로 FAIL 상태이면서 특정 규칙만 자동 수정 가능으로 설정
        auto_fixable_rules = ["U-03", "U-40", "M-03", "M-04", "M-05", "M-06", "M-07", "M-08"]

        can_remediate = status == "FAIL" and rule_id in auto_fixable_rules

        self.remediate_btn.setEnabled(can_remediate)

        if can_remediate:
            self.remediate_btn.setToolTip(f"{rule_id}를 자동으로 수정합니다")
        else:
            if status != "FAIL":
                self.remediate_btn.setToolTip("FAIL 상태인 규칙만 자동 수정 가능합니다")
            else:
                self.remediate_btn.setToolTip("이 규칙은 자동 수정이 지원되지 않습니다")

    def _on_remediate_clicked(self):
        """자동 수정 버튼 클릭 핸들러"""
        selected_items = self.result_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        rule_id = item.data(0, Qt.UserRole)
        status = item.text(1)

        if not rule_id:
            return

        # 규칙 이름 추출 (형식: "U-03: 계정잠금 임계값 설정")
        full_text = item.text(0)
        if ": " in full_text:
            rule_name = full_text.split(": ", 1)[1]
        else:
            rule_name = full_text

        # 시그널 발생
        self.remediate_requested.emit(rule_id, rule_name, status)
