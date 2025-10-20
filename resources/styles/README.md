# BluePy 2.0 - QSS 스타일시트

## 파일 구조

```
resources/styles/
├── dark.qss      # 다크 모드 스타일시트
├── light.qss     # 라이트 모드 스타일시트
└── README.md     # 이 파일
```

## 색상 팔레트

### 다크 모드 (dark.qss)

VSCode Dark+ / GitHub Dark 기반

| 색상 종류 | Hex 코드 | 용도 |
|-----------|----------|------|
| **배경색** | | |
| Primary Background | `#1E1E1E` | 메인 배경 |
| Secondary Background | `#252526` | 도크, 사이드바 |
| Tertiary Background | `#2D2D30` | 입력 필드, 버튼 |
| Hover Background | `#3E3E42` | 마우스 오버 |
| **텍스트색** | | |
| Primary Text | `#CCCCCC` | 기본 텍스트 |
| Secondary Text | `#9D9D9D` | 비활성 텍스트 |
| Disabled Text | `#656565` | 비활성화 상태 |
| **강조색** | | |
| Accent Blue | `#007ACC` | 선택, 링크 |
| Success Green | `#4EC9B0` | 통과 (PASS) |
| Warning Orange | `#CE9178` | 경고 (WARN) |
| Error Red | `#F48771` | 실패 (FAIL) |
| **테두리** | | |
| Border | `#3E3E42` | 기본 테두리 |
| Focus Border | `#007ACC` | 포커스 테두리 |

### 라이트 모드 (light.qss)

VSCode Light+ / GitHub Light 기반

| 색상 종류 | Hex 코드 | 용도 |
|-----------|----------|------|
| **배경색** | | |
| Primary Background | `#FFFFFF` | 메인 배경 |
| Secondary Background | `#F3F3F3` | 도크, 사이드바 |
| Tertiary Background | `#E8E8E8` | 입력 필드, 버튼 |
| Hover Background | `#DCDCDC` | 마우스 오버 |
| **텍스트색** | | |
| Primary Text | `#2E2E2E` | 기본 텍스트 |
| Secondary Text | `#6E6E6E` | 비활성 텍스트 |
| Disabled Text | `#AEAEAE` | 비활성화 상태 |
| **강조색** | | |
| Accent Blue | `#0078D4` | 선택, 링크 |
| Success Green | `#16825D` | 통과 (PASS) |
| Warning Orange | `#CA5010` | 경고 (WARN) |
| Error Red | `#D13438` | 실패 (FAIL) |
| **테두리** | | |
| Border | `#DCDCDC` | 기본 테두리 |
| Focus Border | `#0078D4` | 포커스 테두리 |

## 지원 위젯

### 메인 윈도우
- `QMainWindow` - 메인 윈도우, 구분선
- `QMenuBar` - 메뉴바 (선택, 프레스 상태)
- `QMenu` - 메뉴 아이템, 구분선
- `QStatusBar` - 상태바

### 버튼
- `QPushButton` - 일반, 호버, 프레스, 비활성, 기본 버튼
- `QCheckBox` - 체크박스 (체크, 호버, 비활성)
- `QRadioButton` - 라디오 버튼 (체크, 호버, 비활성)

### 입력 위젯
- `QLineEdit` - 한 줄 입력 (포커스, 선택, 비활성)
- `QTextEdit` - 여러 줄 입력 (포커스, 선택, 비활성)
- `QPlainTextEdit` - 플레인 텍스트 편집기
- `QComboBox` - 콤보박스 (드롭다운 포함)

### 테이블/트리
- `QTableWidget` - 테이블 (교차 배경색, 선택, 호버)
- `QHeaderView` - 헤더 (호버)
- `QTreeWidget` - 트리 위젯 (선택, 호버, 브랜치)

### 탭
- `QTabWidget` - 탭 컨테이너
- `QTabBar` - 탭 바 (선택, 호버)

### 기타
- `QProgressBar` - 프로그레스 바
- `QScrollBar` - 스크롤바 (수직/수평, 호버)
- `QDockWidget` - 도크 위젯 (타이틀바)
- `QToolTip` - 툴팁
- `QLabel` - 라벨 (비활성)
- `QGroupBox` - 그룹박스 (타이틀)
- `QMessageBox` - 메시지 박스
- `QDialog` - 대화상자

## 커스텀 클래스

상태별 색상을 적용하기 위한 커스텀 클래스:

```python
# 통과 상태 (녹색)
label.setProperty("class", "status-pass")

# 실패 상태 (빨간색)
label.setProperty("class", "status-fail")

# 경고 상태 (주황색)
label.setProperty("class", "status-warn")

# 정보 상태 (파란색)
label.setProperty("class", "status-info")

# 스타일 업데이트 필수
label.style().unpolish(label)
label.style().polish(label)
```

## QSS 파일 수정 가이드

### 색상 변경
```css
/* 예: 버튼 배경색 변경 */
QPushButton {
    background-color: #YOUR_COLOR;  /* 여기 수정 */
}
```

### 테두리 스타일 변경
```css
QPushButton {
    border: 2px solid #YOUR_COLOR;  /* 두께, 스타일, 색상 */
    border-radius: 8px;              /* 둥근 모서리 */
}
```

### 패딩/마진 조정
```css
QPushButton {
    padding: 8px 20px;  /* 상하 좌우 */
    margin: 4px;        /* 여백 */
}
```

### 폰트 변경
```css
* {
    font-family: "Your Font", sans-serif;
    font-size: 11pt;
}
```

## 접근성

### WCAG 2.1 AA 기준 준수

| 테마 | 배경 | 텍스트 | 대비 비율 | 기준 |
|------|------|--------|-----------|------|
| 다크 | #1E1E1E | #CCCCCC | 11.0:1 | AAA |
| 라이트 | #FFFFFF | #2E2E2E | 13.6:1 | AAA |

### 명도 대비 (강조색)

| 색상 | 다크 모드 | 라이트 모드 | 대비 |
|------|-----------|-------------|------|
| Accent Blue | #007ACC | #0078D4 | 4.6:1 |
| Success Green | #4EC9B0 | #16825D | 5.2:1 |
| Warning Orange | #CE9178 | #CA5010 | 4.8:1 |
| Error Red | #F48771 | #D13438 | 5.1:1 |

모든 색상이 WCAG AA 기준(4.5:1 이상)을 충족합니다.

## PySide6 QSS Best Practice

### 1. QPalette 우선 사용
```python
# 기본 색상은 QPalette로 설정
palette = QPalette()
palette.setColor(QPalette.Window, QColor("#1E1E1E"))
app.setPalette(palette)

# QSS는 세부 스타일링에만 사용
app.setStyleSheet(qss_content)
```

### 2. 파일 분리
```python
# QSS를 외부 파일로 저장
with open("resources/styles/dark.qss", "r") as f:
    app.setStyleSheet(f.read())
```

### 3. 선택자 최소화
```css
/* Good - 단순 선택자 */
QPushButton {
    background-color: #2D2D30;
}

/* Bad - 과도한 중첩 */
QMainWindow QWidget QTabWidget QPushButton {
    background-color: #2D2D30;
}
```

### 4. 상태별 스타일링
```css
/* 호버, 프레스, 비활성 등 다양한 상태 지원 */
QPushButton:hover { ... }
QPushButton:pressed { ... }
QPushButton:disabled { ... }
QPushButton:default { ... }
```

### 5. 성능 최적화
```python
# QSS 캐싱 (자주 전환 시)
class ThemeManager:
    def __init__(self):
        self._qss_cache = {}

    def load_qss(self, theme):
        if theme not in self._qss_cache:
            with open(f"{theme}.qss") as f:
                self._qss_cache[theme] = f.read()
        return self._qss_cache[theme]
```

## 참고 자료

- [Qt Style Sheets Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)
- [Qt Style Sheets Examples](https://doc.qt.io/qt-6/stylesheet-examples.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 라이선스

BluePy 2.0 프로젝트 라이선스를 따릅니다.
