"""BluePy 2.0 GUI 애플리케이션

PySide6 기반 GUI 애플리케이션의 메인 엔트리 포인트입니다.

사용법:
    python -m src.gui.app
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from .main_window import MainWindow
from ..infrastructure.database.models import init_database


def setup_database():
    """데이터베이스 초기화"""
    # 데이터베이스 디렉토리 생성
    db_dir = Path("data/databases")
    db_dir.mkdir(parents=True, exist_ok=True)

    # 데이터베이스 초기화
    db_path = db_dir / "bluepy.db"
    init_database(str(db_path))

    print(f"데이터베이스 초기화 완료: {db_path}")


def main():
    """애플리케이션 메인 함수"""
    # 데이터베이스 초기화
    setup_database()

    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)

    # 한글 폰트 설정 (fallback 체인)
    font = QFont()
    font.setFamilies([
        "Noto Sans CJK KR",
        "Noto Sans KR",
        "NanumGothic",
        "DejaVu Sans",
        "Sans Serif"
    ])
    font.setPointSize(10)
    app.setFont(font)

    # 애플리케이션 정보 설정
    app.setApplicationName("BluePy 2.0")
    app.setOrganizationName("BluePy")
    app.setApplicationVersion("2.0.0")

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
