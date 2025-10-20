# BluePy 2.0 - 테마 사용 가이드

## 개요

BluePy 2.0은 다크 모드와 라이트 모드를 지원합니다.

- **다크 모드**: VSCode Dark+ / GitHub Dark 기반
- **라이트 모드**: VSCode Light+ / GitHub Light 기반

## 색상 팔레트

### 다크 모드
```
배경색:
- Primary Background: #1E1E1E (메인 배경)
- Secondary Background: #252526 (도크, 사이드바)
- Tertiary Background: #2D2D30 (입력 필드, 버튼)
- Hover Background: #3E3E42 (마우스 오버)

텍스트색:
- Primary Text: #CCCCCC (기본 텍스트)
- Secondary Text: #9D9D9D (비활성 텍스트)
- Disabled Text: #656565

강조색:
- Accent Blue: #007ACC (선택, 링크)
- Success Green: #4EC9B0 (통과)
- Warning Orange: #CE9178 (경고)
- Error Red: #F48771 (실패)
```

### 라이트 모드
```
배경색:
- Primary Background: #FFFFFF
- Secondary Background: #F3F3F3
- Tertiary Background: #E8E8E8
- Hover Background: #DCDCDC

텍스트색:
- Primary Text: #2E2E2E
- Secondary Text: #6E6E6E
- Disabled Text: #AEAEAE

강조색:
- Accent Blue: #0078D4 (선택, 링크)
- Success Green: #16825D (통과)
- Warning Orange: #CA5010 (경고)
- Error Red: #D13438 (실패)
```

## MainWindow에 테마 전환 메뉴 추가

`src/gui/main_window.py` 파일을 다음과 같이 수정하세요:

```python
from .theme_manager import get_theme_manager, Theme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... 기존 코드 ...

        # 테마 관리자 초기화
        self.theme_manager = get_theme_manager()

    def _create_menus(self):
        """메뉴바 생성"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")
        # ... 기존 코드 ...

        # 뷰 메뉴 (새로 추가)
        view_menu = menubar.addMenu("보기(&V)")

        # 테마 전환
        theme_menu = view_menu.addMenu("테마(&T)")

        # 다크 모드
        dark_action = theme_menu.addAction("다크 모드(&D)")
        dark_action.triggered.connect(lambda: self._change_theme(Theme.DARK))

        # 라이트 모드
        light_action = theme_menu.addAction("라이트 모드(&L)")
        light_action.triggered.connect(lambda: self._change_theme(Theme.LIGHT))

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말(&H)")
        # ... 기존 코드 ...

    def _change_theme(self, theme: Theme):
        """테마 변경

        Args:
            theme: 적용할 테마
        """
        app = QApplication.instance()
        self.theme_manager.set_theme(app, theme)
        self.statusBar().showMessage(
            f"테마 변경: {'다크 모드' if theme == Theme.DARK else '라이트 모드'}"
        )
```

## app.py에서 초기 테마 설정

`src/gui/app.py` 파일을 다음과 같이 수정하세요:

```python
import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow
from .theme_manager import get_theme_manager, Theme


def main():
    """애플리케이션 진입점"""
    app = QApplication(sys.argv)

    # 애플리케이션 설정
    app.setApplicationName("BluePy 2.0")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("BluePy")

    # 테마 설정 (기본값: 다크 모드)
    theme_manager = get_theme_manager()
    theme_manager.set_theme(app, Theme.DARK)

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

## QSS 파일 위치

- **다크 모드**: `resources/styles/dark.qss`
- **라이트 모드**: `resources/styles/light.qss`

## 커스텀 위젯에서 스타일 클래스 사용

QSS에는 상태별 색상 클래스가 정의되어 있습니다:

```python
# 통과 상태 (녹색)
label.setProperty("class", "status-pass")

# 실패 상태 (빨간색)
label.setProperty("class", "status-fail")

# 경고 상태 (주황색)
label.setProperty("class", "status-warn")

# 정보 상태 (파란색)
label.setProperty("class", "status-info")

# 스타일 업데이트 (property 변경 후 필수)
label.style().unpolish(label)
label.style().polish(label)
```

## QSS 커스터마이징

QSS 파일을 직접 수정하여 색상과 스타일을 변경할 수 있습니다:

```css
/* 버튼 배경색 변경 */
QPushButton {
    background-color: #YOUR_COLOR;
}

/* 호버 효과 변경 */
QPushButton:hover {
    background-color: #YOUR_HOVER_COLOR;
}
```

## 테마 전환 단축키 추가 (선택사항)

`_create_menus()` 메서드에서 단축키를 추가할 수 있습니다:

```python
# 테마 토글 (Ctrl+T)
toggle_theme_action = view_menu.addAction("테마 전환(&T)")
toggle_theme_action.setShortcut("Ctrl+T")
toggle_theme_action.triggered.connect(self._toggle_theme)

def _toggle_theme(self):
    """테마 토글"""
    app = QApplication.instance()
    self.theme_manager.toggle_theme()
    current = self.theme_manager.get_current_theme()
    self.statusBar().showMessage(
        f"테마 전환: {'다크 모드' if current == Theme.DARK else '라이트 모드'}"
    )
```

## 접근성 고려사항

- 명도 대비: WCAG AA 기준 준수 (4.5:1 이상)
- 다크 모드: 배경 #1E1E1E / 텍스트 #CCCCCC (대비 11.0:1)
- 라이트 모드: 배경 #FFFFFF / 텍스트 #2E2E2E (대비 13.6:1)

## 트러블슈팅

### 테마가 적용되지 않는 경우

1. QSS 파일 경로 확인:
   ```python
   print(ThemeManager.STYLES_DIR)
   ```

2. QSS 파일 존재 확인:
   ```bash
   ls resources/styles/
   ```

3. QSS 파일 인코딩 확인 (UTF-8)

### 일부 위젯에 스타일이 적용되지 않는 경우

- `setStyleSheet()`를 위젯별로 호출한 경우 QSS가 무시됩니다.
- 위젯별 스타일시트는 제거하고 전역 QSS를 사용하세요.

## PySide6 QSS Best Practice

1. **QPalette 우선 사용**: 기본 색상은 QPalette로 설정하고 QSS는 세부 스타일에만 사용
2. **파일 분리**: QSS를 외부 파일로 저장하여 유지보수성 향상
3. **캐싱**: 자주 전환하는 경우 QSS를 메모리에 캐싱
4. **선택자 최소화**: 과도한 중첩 선택자는 성능 저하
5. **상태별 스타일링**: `:hover`, `:pressed`, `:disabled` 등 적극 활용

## 참고 자료

- [Qt Style Sheets Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)
- [Qt Style Sheets Examples](https://doc.qt.io/qt-6/stylesheet-examples.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
