# Settings UI 구현 가이드

**작성일**: 2025-10-20
**버전**: 1.0.0
**상태**: 완료

## 개요

BluePy 2.0 프로젝트의 설정 UI를 완전히 구현한 문서입니다.

### 주요 기능

1. **테마 선택**: Light/Dark 모드 전환
2. **로그 레벨**: DEBUG/INFO/WARNING/ERROR 선택
3. **언어 선택**: 한국어/English (준비만, 실제 구현은 나중)
4. **백업 디렉토리**: 경로 설정 (기본값: data/backups)

---

## 아키텍처

### 파일 구조

```
src/
├── infrastructure/
│   └── config/
│       ├── __init__.py         # 모듈 export
│       └── settings.py         # 설정 저장/로드 (193줄)
├── gui/
│   ├── dialogs/
│   │   └── settings_dialog.py  # 설정 대화상자 (234줄)
│   └── main_window.py          # 메인 윈도우 통합 (수정)
tests/
├── unit/
│   └── test_settings.py        # 설정 모듈 테스트 (302줄, 26개 테스트)
└── gui/
    └── test_settings_dialog.py # GUI 테스트 (217줄, 13개 테스트)
config/
└── settings.json               # 설정 파일 (자동 생성)
```

### 레이어 분리

```
┌─────────────────────────────────────┐
│    GUI Layer (Presentation)        │
│  - SettingsDialog (PySide6)        │
│  - MainWindow 통합                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Infrastructure Layer (Persistence) │
│  - settings.py (JSON 저장/로드)     │
│  - 기본값 관리                       │
│  - 에러 처리                         │
└─────────────────────────────────────┘
```

---

## 모듈 상세 설명

### 1. Settings 모듈 (src/infrastructure/config/settings.py)

#### 기능

- JSON 기반 설정 저장/로드
- 기본값 관리
- 중첩 딕셔너리 병합
- 점 표기법 키 접근 (예: "appearance.theme")

#### 주요 함수

##### get_default_settings()

기본 설정을 반환합니다 (깊은 복사본).

```python
def get_default_settings() -> Dict[str, Any]:
    """기본 설정 반환

    Returns:
        기본 설정 딕셔너리 (깊은 복사본)
    """
```

**기본값 구조**:

```json
{
  "appearance": {
    "theme": "dark"
  },
  "logging": {
    "level": "INFO"
  },
  "language": {
    "locale": "ko_KR"
  },
  "backup": {
    "directory": "data/backups"
  }
}
```

##### load_settings(settings_file)

JSON 파일에서 설정을 로드합니다.

```python
def load_settings(settings_file: Optional[Path] = None) -> Dict[str, Any]:
    """설정 로드

    Args:
        settings_file: 설정 파일 경로 (기본값: config/settings.json)

    Returns:
        설정 딕셔너리 (기본값과 병합됨)
    """
```

**특징**:
- 파일이 없으면 기본값 반환
- 일부 키만 있으면 기본값과 병합
- 파싱 오류 시 경고 출력 후 기본값 반환

##### save_settings(settings, settings_file)

설정을 JSON 파일로 저장합니다.

```python
def save_settings(settings: Dict[str, Any], settings_file: Optional[Path] = None) -> bool:
    """설정 저장

    Args:
        settings: 저장할 설정 딕셔너리
        settings_file: 설정 파일 경로 (기본값: config/settings.json)

    Returns:
        성공 여부
    """
```

**특징**:
- 디렉토리 자동 생성
- UTF-8 인코딩 (한글 지원)
- 들여쓰기 포함 (indent=2)
- 에러 시 False 반환

##### get_setting(settings, key_path, default)

점 표기법으로 설정 값을 가져옵니다.

```python
def get_setting(settings: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """설정 값 가져오기 (점 표기법)

    Args:
        settings: 설정 딕셔너리
        key_path: 점으로 구분된 키 경로 (예: "appearance.theme")
        default: 키가 없을 때 반환할 기본값

    Returns:
        설정 값 또는 기본값
    """
```

**예제**:
```python
theme = get_setting(settings, "appearance.theme", "dark")
# settings["appearance"]["theme"]와 동일
```

##### set_setting(settings, key_path, value)

점 표기법으로 설정 값을 설정합니다.

```python
def set_setting(settings: Dict[str, Any], key_path: str, value: Any) -> None:
    """설정 값 설정 (점 표기법)

    Args:
        settings: 설정 딕셔너리 (변경됨)
        key_path: 점으로 구분된 키 경로 (예: "appearance.theme")
        value: 설정할 값
    """
```

**예제**:
```python
set_setting(settings, "appearance.theme", "light")
# settings["appearance"]["theme"] = "light"와 동일
# 중간 키가 없으면 자동 생성
```

#### 테스트 커버리지

- **26개 테스트**: 모두 통과
- **커버리지**: 93% (57줄 중 53줄)
- **미커버 라인**: import copy, print 구문, 예외 처리 내부

---

### 2. SettingsDialog 클래스 (src/gui/dialogs/settings_dialog.py)

#### 구조

```python
class SettingsDialog(QDialog):
    """설정 대화상자

    애플리케이션 설정을 변경하는 폼 대화상자입니다.
    """
```

#### 위젯 구성

```
┌─────────────────────────────────────────┐
│           설정 대화상자                  │
├─────────────────────────────────────────┤
│ [외관]                                   │
│   테마:        [Dark ▼]                  │
│                                          │
│ [로깅]                                   │
│   로그 레벨:   [INFO ▼]                  │
│                                          │
│ [언어]                                   │
│   언어:        [한국어 ▼] (비활성화)     │
│   (언어 전환 기능은 향후 업데이트 예정)  │
│                                          │
│ [백업]                                   │
│   백업 디렉토리: [data/backups] [찾아보기]│
│                                          │
├─────────────────────────────────────────┤
│               [저장] [취소]              │
│ (설정 변경 후 '저장'을 눌러야 적용)      │
└─────────────────────────────────────────┘
```

#### 주요 메서드

##### __init__(parent)

대화상자를 초기화하고 현재 설정을 로드합니다.

```python
def __init__(self, parent=None):
    """초기화

    Args:
        parent: 부모 위젯
    """
```

##### _setup_ui()

UI 구성 요소를 생성합니다.

- 4개 그룹박스 (외관, 로깅, 언어, 백업)
- QFormLayout 사용
- 저장/취소 버튼

##### _load_current_settings()

저장된 설정을 UI에 로드합니다.

```python
def _load_current_settings(self):
    """현재 설정 로드

    저장된 설정 파일에서 값을 읽어 UI에 표시합니다.
    """
```

##### _on_browse_backup_directory()

"찾아보기" 버튼 핸들러입니다.

```python
def _on_browse_backup_directory(self):
    """백업 디렉토리 찾아보기 핸들러

    파일 선택 대화상자를 열어 디렉토리를 선택합니다.
    """
```

##### _on_save()

"저장" 버튼 핸들러입니다.

```python
def _on_save(self):
    """저장 버튼 핸들러

    UI의 값을 읽어 설정 파일로 저장합니다.
    """
```

**유효성 검사**:
- 백업 디렉토리가 비어있으면 경고 표시
- 저장 실패 시 오류 메시지 표시

**값 매핑**:
```python
# 테마: UI 표시값 → 내부 값
"Dark" → "dark"
"Light" → "light"

# 언어: UI 표시값 → 내부 값
"한국어" → "ko_KR"
"English" → "en_US"
```

##### get_settings()

저장된 설정을 반환합니다.

```python
def get_settings(self) -> dict:
    """저장된 설정 반환

    Returns:
        설정 딕셔너리
    """
```

#### 테스트 커버리지

- **13개 테스트**: 모두 통과
- **커버리지**: 100% (104줄 중 104줄)

---

### 3. MainWindow 통합 (src/gui/main_window.py)

#### 추가된 코드

##### import 추가

```python
from .dialogs.settings_dialog import SettingsDialog
from ..infrastructure.config.settings import load_settings, get_setting
```

##### __init__() 수정

```python
# 설정 로드
self.app_settings = load_settings()
```

##### _create_menus() 수정

```python
# 설정 메뉴
settings_menu = menubar.addMenu("설정(&S)")

# 설정 열기
open_settings_action = settings_menu.addAction("설정(&P)")
open_settings_action.setShortcut("Ctrl+,")
open_settings_action.triggered.connect(self._on_open_settings)
```

##### _on_open_settings() 추가

설정 대화상자를 열고 저장 시 즉시 적용합니다.

```python
def _on_open_settings(self):
    """설정 대화상자 열기 핸들러

    설정 대화상자를 모달로 열고, 저장 시 즉시 적용합니다.
    """
    dialog = SettingsDialog(self)

    if dialog.exec():
        # 설정이 저장되었으므로 재로드
        self.app_settings = load_settings()

        # 테마 적용
        theme = get_setting(self.app_settings, "appearance.theme", "dark")
        self._apply_theme(theme)

        # 상태바 메시지
        self.statusBar().showMessage("설정이 저장되었습니다.")
```

##### _apply_theme(theme) 추가

테마를 즉시 적용합니다.

```python
def _apply_theme(self, theme: str):
    """테마 적용

    Args:
        theme: 테마 이름 ("dark" 또는 "light")
    """
    from .theme_manager import get_theme_manager, Theme

    theme_manager = get_theme_manager()
    theme_enum = Theme.DARK if theme == "dark" else Theme.LIGHT

    # 현재 테마와 다르면 변경
    if theme_manager.get_current_theme() != theme_enum:
        theme_manager.set_theme(QApplication.instance(), theme_enum)
```

---

## 사용 방법

### 사용자 관점

#### 1. 설정 대화상자 열기

메뉴: **설정 > 설정**
단축키: **Ctrl+,**

#### 2. 설정 변경

1. **테마 선택**: Dark 또는 Light 선택
2. **로그 레벨**: DEBUG/INFO/WARNING/ERROR 선택
3. **언어**: 한국어 또는 English 선택 (현재 비활성화)
4. **백업 디렉토리**: 경로 입력 또는 "찾아보기" 클릭

#### 3. 저장

"저장" 버튼 클릭 → 즉시 적용

### 개발자 관점

#### 설정 읽기

```python
from src.infrastructure.config.settings import load_settings, get_setting

# 전체 설정 로드
settings = load_settings()

# 특정 값 가져오기
theme = get_setting(settings, "appearance.theme", "dark")
log_level = get_setting(settings, "logging.level", "INFO")
backup_dir = get_setting(settings, "backup.directory", "data/backups")
```

#### 설정 쓰기

```python
from src.infrastructure.config.settings import load_settings, set_setting, save_settings

# 설정 로드
settings = load_settings()

# 값 변경
set_setting(settings, "appearance.theme", "light")
set_setting(settings, "logging.level", "DEBUG")

# 저장
success = save_settings(settings)
```

#### 새 설정 항목 추가

1. **settings.py의 DEFAULT_SETTINGS에 추가**:

```python
DEFAULT_SETTINGS = {
    "appearance": {
        "theme": "dark",
        "font_size": 12,  # 새 항목
    },
    # ...
}
```

2. **SettingsDialog에 위젯 추가**:

```python
# _setup_ui()에서
self.font_size_spin = QSpinBox()
self.font_size_spin.setRange(8, 24)
appearance_layout.addRow("글꼴 크기:", self.font_size_spin)

# _load_current_settings()에서
font_size = get_setting(self.settings, "appearance.font_size", 12)
self.font_size_spin.setValue(font_size)

# _on_save()에서
font_size = self.font_size_spin.value()
set_setting(self.settings, "appearance.font_size", font_size)
```

3. **테스트 추가**:

```python
def test_loads_font_size(self):
    """글꼴 크기를 로드하는지 확인"""
    settings = {"appearance": {"font_size": 14}}
    # ...
```

---

## 테스트 가이드

### 실행 방법

#### 단위 테스트만 실행

```bash
pytest tests/unit/test_settings.py -v
```

#### GUI 테스트만 실행

```bash
pytest tests/gui/test_settings_dialog.py -v
```

#### 전체 테스트 (커버리지 포함)

```bash
pytest tests/unit/test_settings.py tests/gui/test_settings_dialog.py \
  --cov=src/infrastructure/config \
  --cov=src/gui/dialogs/settings_dialog \
  -v
```

### 테스트 결과

```
tests/unit/test_settings.py::TestGetDefaultSettings (5개 테스트)
tests/unit/test_settings.py::TestLoadSettings (4개 테스트)
tests/unit/test_settings.py::TestSaveSettings (4개 테스트)
tests/unit/test_settings.py::TestGetSetting (4개 테스트)
tests/unit/test_settings.py::TestSetSetting (4개 테스트)
tests/unit/test_settings.py::TestDefaultSettings (5개 테스트)
tests/gui/test_settings_dialog.py::TestSettingsDialogInit (5개 테스트)
tests/gui/test_settings_dialog.py::TestSettingsDialogLoadSettings (2개 테스트)
tests/gui/test_settings_dialog.py::TestSettingsDialogBrowseDirectory (2개 테스트)
tests/gui/test_settings_dialog.py::TestSettingsDialogSave (3개 테스트)
tests/gui/test_settings_dialog.py::TestSettingsDialogGetData (1개 테스트)

총 39개 테스트: 모두 통과
커버리지:
- settings.py: 93% (57줄 중 53줄)
- settings_dialog.py: 100% (104줄 중 104줄)
```

---

## 통계 및 요약

### 코드 라인 수

| 파일 | 라인 수 | 설명 |
|------|---------|------|
| `src/infrastructure/config/settings.py` | 193줄 | 설정 모듈 (함수 6개) |
| `src/gui/dialogs/settings_dialog.py` | 234줄 | GUI 대화상자 (클래스 1개) |
| `tests/unit/test_settings.py` | 302줄 | 단위 테스트 (26개) |
| `tests/gui/test_settings_dialog.py` | 217줄 | GUI 테스트 (13개) |
| **총계** | **946줄** | **39개 테스트** |

### 기능 완성도

- [x] Settings 모듈 설계 및 구현
- [x] SettingsDialog 클래스 구현
- [x] MainWindow에 설정 메뉴 통합
- [x] 테스트 케이스 작성 (39개, 100% 통과)
- [x] 테마 즉시 적용
- [x] 유효성 검사
- [x] 에러 처리
- [x] 한글 지원 (UTF-8)
- [ ] 언어 전환 기능 (향후 구현)

### 테스트 커버리지

| 모듈 | 커버리지 |
|------|----------|
| `settings.py` | 93% |
| `settings_dialog.py` | 100% |

---

## 향후 개선 사항

### 1. 언어 전환 기능 구현

현재는 UI만 준비되어 있고 실제 기능은 비활성화되어 있습니다.

**구현 계획**:
- Qt Translator 사용
- .ts/.qm 파일로 번역 관리
- 런타임 언어 전환

### 2. 추가 설정 항목

**제안**:
- 글꼴 크기
- 자동 스캔 간격
- 알림 설정
- SSH 타임아웃 설정
- 최대 동시 스캔 수

### 3. 설정 검증

**제안**:
- 백업 디렉토리 쓰기 권한 확인
- 경로 유효성 검사
- 범위 제한 (예: 로그 레벨)

### 4. 설정 마이그레이션

**제안**:
- 버전 정보 추가
- 설정 스키마 변경 시 자동 마이그레이션
- 호환성 검사

---

## 참조

### 관련 문서

- `PROJECT_PLAN.md` - 전체 프로젝트 계획
- `docs/ARCHITECTURE.md` - Clean Architecture 설계
- `docs/THEME_USAGE.md` - 테마 사용 가이드

### 관련 코드

- `src/gui/theme_manager.py` - 테마 관리자 (연동됨)
- `src/gui/main_window.py` - 메인 윈도우 (통합됨)

### 외부 라이브러리

- **PySide6**: Qt 6 GUI 프레임워크
- **pytest**: 테스트 프레임워크
- **pytest-qt**: Qt 테스트 유틸리티
- **pytest-mock**: Mock 지원

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2025-10-20 | 1.0.0 | 최초 구현 완료 |

---

**작성자**: Claude (Anthropic)
**검토자**: sweetbkan
**상태**: 완료 및 테스트 통과
