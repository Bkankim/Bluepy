# BluePy 2.0 - 시스템 아키텍처 문서

**작성일**: 2025-10-17
**버전**: 1.0
**상태**: Draft

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [설계 원칙](#2-설계-원칙)
3. [전체 시스템 구조](#3-전체-시스템-구조)
4. [프로젝트 폴더 구조](#4-프로젝트-폴더-구조)
5. [핵심 모듈 설계](#5-핵심-모듈-설계)
6. [데이터 모델](#6-데이터-모델)
7. [규칙 시스템](#7-규칙-시스템)
8. [통신 및 네트워크](#8-통신-및-네트워크)
9. [데이터베이스 설계](#9-데이터베이스-설계)
10. [보안 설계](#10-보안-설계)
11. [확장성 전략](#11-확장성-전략)
12. [성능 최적화](#12-성능-최적화)

---

## 1. 아키텍처 개요

### 1.1 아키텍처 패턴

BluePy 2.0은 **Clean Architecture** (Hexagonal Architecture)를 기반으로 설계되었습니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   GUI        │  │     CLI      │  │    REST API      │  │
│  │  (PySide6)   │  │   (Click)    │  │   (FastAPI)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Use Cases (Business Logic)                │   │
│  │  • ScanServer    • AnalyzeResults   • AutoRemediate │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Domain Layer                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             Domain Entities & Logic                  │   │
│  │  • CheckItem  • ScanResult  • RemediationAction     │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │  Database   │ │   Network    │ │    Reporting       │   │
│  │  (SQLite)   │ │ (SSH/WinRM)  │ │  (PDF/Excel/HTML)  │   │
│  └─────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 주요 특징

**계층 분리**:
- 각 계층은 명확한 책임을 가짐
- 의존성은 외부 → 내부만 가능 (Dependency Inversion)
- Infrastructure 계층은 Domain을 의존하지만, Domain은 Infrastructure를 모름

**확장성**:
- 새로운 플랫폼 추가 용이 (Linux, macOS, Windows, Docker 등)
- 규칙 기반 시스템 (YAML 파일로 점검 항목 정의)
- 플러그인 시스템 (커스텀 점검 규칙 추가)

**테스트 가능성**:
- 각 계층을 독립적으로 테스트 가능
- Mock 객체로 외부 의존성 제거
- 단위 테스트, 통합 테스트 분리

---

## 2. 설계 원칙

### 2.1 SOLID 원칙

#### Single Responsibility Principle (단일 책임)
각 클래스는 하나의 책임만 가짐

```python
# Good: 책임 분리
class Scanner:
    """점검 실행만 담당"""
    def scan(self): pass

class Analyzer:
    """결과 분석만 담당"""
    def analyze(self, scan_result): pass

class Reporter:
    """보고서 생성만 담당"""
    def generate_report(self, analyzed_data): pass
```

#### Open-Closed Principle (개방-폐쇄)
확장에는 열려있고 수정에는 닫혀있음

```python
# Good: 확장 가능
class BaseScanner(ABC):
    @abstractmethod
    def scan(self): pass

class LinuxScanner(BaseScanner):
    def scan(self): pass  # Linux 구현

class MacOSScanner(BaseScanner):
    def scan(self): pass  # macOS 구현 - 기존 코드 수정 없음
```

#### Liskov Substitution Principle (리스코프 치환)
하위 타입은 상위 타입을 대체 가능

```python
def run_scan(scanner: BaseScanner):
    """어떤 Scanner든 동작 가능"""
    result = scanner.scan()
    return result

# LinuxScanner, MacOSScanner 모두 가능
```

#### Interface Segregation Principle (인터페이스 분리)
클라이언트는 사용하지 않는 인터페이스에 의존하지 않음

```python
# Good: 작고 명확한 인터페이스
class Scannable(Protocol):
    def scan(self) -> ScanResult: ...

class Remediable(Protocol):
    def remediate(self, item: CheckItem) -> bool: ...

# Bad: 거대한 인터페이스
class AllInOne(Protocol):
    def scan(self): ...
    def remediate(self): ...
    def report(self): ...  # 점검만 필요한 클라이언트에게 불필요
```

#### Dependency Inversion Principle (의존성 역전)
고수준 모듈은 저수준 모듈에 의존하지 않고, 둘 다 추상화에 의존

```python
# Good: 추상화에 의존
class ScanUseCase:
    def __init__(self, scanner: BaseScanner, reporter: BaseReporter):
        self.scanner = scanner  # 구체적 클래스가 아닌 추상 클래스
        self.reporter = reporter

# Bad: 구체적 클래스에 의존
class ScanUseCase:
    def __init__(self):
        self.scanner = LinuxScanner()  # 하드코딩
```

### 2.2 추가 설계 원칙

**DRY (Don't Repeat Yourself)**:
- Unix 공통 로직은 `UnixScanner`에 추상화
- 반복되는 패턴은 유틸리티 함수로 추출

**KISS (Keep It Simple, Stupid)**:
- 과도한 추상화 지양
- 명확하고 읽기 쉬운 코드

**YAGNI (You Aren't Gonna Need It)**:
- 현재 필요한 기능만 구현
- 미래를 위한 과도한 설계 지양

---

## 3. 전체 시스템 구조

### 3.1 컴포넌트 다이어그램

```
┌────────────────────────────────────────────────────────────────┐
│                      BluePy 2.0 Application                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                     GUI Layer (PySide6)                   │ │
│  │  ┌────────────┐ ┌────────────┐ ┌───────────────────────┐ │ │
│  │  │ Dashboard  │ │ Scan View  │ │ Result/History View   │ │ │
│  │  │ - 점수     │ │ - 서버선택 │ │ - 트리뷰              │ │ │
│  │  │ - 차트     │ │ - 실행     │ │ - 상세정보            │ │ │
│  │  └────────────┘ └────────────┘ └───────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                 │
│  ┌───────────────────────────▼────────────────────────────┐   │
│  │               Application Services                     │   │
│  │  ┌──────────────────┐ ┌────────────────────────────┐  │   │
│  │  │ ScanService      │ │ RemediationService         │  │   │
│  │  │ - scan_server()  │ │ - auto_fix()              │  │   │
│  │  │ - get_results()  │ │ - rollback()              │  │   │
│  │  └──────────────────┘ └────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌───────────────────────────▼────────────────────────────┐   │
│  │                  Core Domain                           │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │   │
│  │  │ Scanner  │  │ Analyzer  │  │ Remediator       │   │   │
│  │  │ - Base   │  │ - Parser  │  │ - Backup         │   │   │
│  │  │ - Unix   │  │ - Risk    │  │ - Execute        │   │   │
│  │  │ - Linux  │  │ - Trend   │  │ - Rollback       │   │   │
│  │  │ - macOS  │  │           │  │                  │   │   │
│  │  │ - Win    │  │           │  │                  │   │   │
│  │  └──────────┘  └───────────┘  └──────────────────┘   │   │
│  └────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌───────────────────────────▼────────────────────────────┐   │
│  │                Infrastructure                          │   │
│  │  ┌───────────┐  ┌───────────┐  ┌──────────────────┐  │   │
│  │  │  DB       │  │ Network   │  │  Reporting       │  │   │
│  │  │  Repo     │  │ SSH       │  │  PDF/Excel/HTML  │  │   │
│  │  │  SQLite   │  │ WinRM     │  │                  │  │   │
│  │  └───────────┘  └───────────┘  └──────────────────┘  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘

              External Resources
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Rules   │  │ Servers  │  │  Reports │
    │  YAML    │  │ SSH/WinRM│  │  Files   │
    └──────────┘  └──────────┘  └──────────┘
```

### 3.2 데이터 플로우

```
사용자 액션
    │
    ▼
┌───────────────────────────────────────────────────────────┐
│ 1. GUI: 스캔 시작 버튼 클릭                                │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 2. ScanService: scan_server(server_id, platform)         │
│    - 서버 정보 조회 (DB)                                  │
│    - Scanner 팩토리로 적절한 Scanner 생성                 │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 3. Scanner: 점검 실행                                     │
│    - SSH/WinRM 연결                                       │
│    - 규칙 파일(YAML) 로드                                │
│    - 점검 명령어 실행 (비동기)                           │
│    - 원시 결과 수집                                       │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 4. Analyzer: 결과 분석                                    │
│    - 명령어 결과 파싱                                     │
│    - 규칙 기반 검증 (YAML validator)                     │
│    - 위험도 계산 (high/medium/low)                       │
│    - ScanResult 객체 생성                                │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 5. Repository: 결과 저장                                  │
│    - ScanResult → DB (SQLite)                            │
│    - 이력 기록                                            │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 6. GUI: 결과 표시                                         │
│    - 트리 뷰 업데이트                                     │
│    - 색상 코드 표시                                       │
│    - 통계 업데이트                                        │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
           (사용자가 자동 수정 선택 시)
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 7. RemediationService: 자동 수정                          │
│    - 백업 생성 (BackupManager)                           │
│    - Dry-run 시뮬레이션                                  │
│    - 미리보기 표시                                        │
│    - 사용자 확인                                          │
│    - 실제 수정 실행                                       │
│    - 검증                                                 │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ 8. Reporter: 보고서 생성                                  │
│    - PDF/Excel/HTML 생성                                 │
│    - 이메일 발송 (선택)                                  │
└───────────────────────────────────────────────────────────┘
```

---

## 4. 프로젝트 폴더 구조

### 4.1 전체 구조

```
bluepy/
│
├──  README.md                       # 프로젝트 소개
├──  PROJECT_PLAN.md                 # 프로젝트 계획서
├──  CLAUDE.md                       # AI 작업 지침
├──  requirements.txt                # Python 의존성
├──  pyproject.toml                  # 프로젝트 메타데이터
├──  setup.py                        # 패키지 설정
├──  .gitignore
├──  .env.example                    # 환경 변수 템플릿
│
├──  src/                            # 소스 코드
│   ├── __init__.py
│   ├── __main__.py                    # 진입점 (python -m src)
│   │
│   ├──  core/                       #  핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   │
│   │   ├──  domain/                 # 도메인 모델
│   │   │   ├── __init__.py
│   │   │   ├── check_item.py         # 점검 항목 엔티티
│   │   │   ├── scan_result.py        # 스캔 결과 엔티티
│   │   │   ├── remediation_action.py # 수정 조치 엔티티
│   │   │   ├── server.py              # 서버 엔티티
│   │   │   └── enums.py               # Severity, Status 등 Enum
│   │   │
│   │   ├──  scanner/                # 스캔 엔진
│   │   │   ├── __init__.py
│   │   │   ├── base_scanner.py       # 추상 클래스
│   │   │   ├── unix_scanner.py       # Unix 공통 (Linux + macOS)
│   │   │   ├── linux_scanner.py      # Linux 특화
│   │   │   ├── macos_scanner.py      # macOS 특화
│   │   │   ├── windows_scanner.py    # Windows 특화
│   │   │   ├── scanner_factory.py    # 팩토리 패턴
│   │   │   └── rule_loader.py        # YAML 규칙 로더
│   │   │
│   │   ├──  analyzer/               # 분석 엔진
│   │   │   ├── __init__.py
│   │   │   ├── result_parser.py      # 명령어 결과 파싱
│   │   │   ├── validator.py          # 규칙 기반 검증
│   │   │   ├── risk_calculator.py    # 위험도 계산
│   │   │   └── trend_analyzer.py     # 트렌드 분석
│   │   │
│   │   └──  remediation/            # 자동 수정 엔진
│   │       ├── __init__.py
│   │       ├── base_remediator.py    # 추상 클래스
│   │       ├── unix_remediator.py    # Unix 공통
│   │       ├── linux_remediator.py   # Linux 특화
│   │       ├── macos_remediator.py   # macOS 특화
│   │       ├── windows_remediator.py # Windows 특화
│   │       ├── backup_manager.py     # 백업 관리
│   │       └── rollback_manager.py   # 롤백 관리
│   │
│   ├──  application/                # 애플리케이션 서비스 (Use Cases)
│   │   ├── __init__.py
│   │   ├── scan_service.py           # 스캔 관련 Use Case
│   │   ├── remediation_service.py    # 수정 관련 Use Case
│   │   ├── report_service.py         # 보고서 관련 Use Case
│   │   └── server_service.py         # 서버 관리 Use Case
│   │
│   ├──  gui/                        # ️ PySide6 GUI
│   │   ├── __init__.py
│   │   ├── app.py                    # QApplication 진입점
│   │   ├── main_window.py            # 메인 윈도우
│   │   │
│   │   ├──  views/                 # 화면 (QWidget)
│   │   │   ├── __init__.py
│   │   │   ├── dashboard_view.py    # 대시보드
│   │   │   ├── server_view.py       # 서버 관리
│   │   │   ├── scan_view.py         # 스캔 실행
│   │   │   ├── result_view.py       # 결과 조회
│   │   │   ├── history_view.py      # 이력 관리
│   │   │   └── settings_view.py     # 설정
│   │   │
│   │   ├──  widgets/               # 재사용 위젯
│   │   │   ├── __init__.py
│   │   │   ├── server_card.py       # 서버 카드
│   │   │   ├── check_item_tree.py   # 점검 항목 트리
│   │   │   ├── progress_widget.py   # 진행률 표시
│   │   │   ├── chart_widget.py      # 차트
│   │   │   └── log_viewer.py        # 로그 뷰어
│   │   │
│   │   ├──  dialogs/               # 대화상자
│   │   │   ├── __init__.py
│   │   │   ├── server_dialog.py     # 서버 추가/편집
│   │   │   ├── remediation_dialog.py # 수정 미리보기
│   │   │   └── about_dialog.py      # 정보
│   │   │
│   │   └──  resources/             # UI 리소스
│   │       ├── icons/                # 아이콘 파일
│   │       ├── styles.qss            # Qt 스타일시트
│   │       └── ui_files/             # Qt Designer 파일 (선택)
│   │
│   ├──  cli/                       # CLI 인터페이스 (선택)
│   │   ├── __init__.py
│   │   └── commands.py               # Click 명령어
│   │
│   ├──  infrastructure/            # 인프라 계층
│   │   ├── __init__.py
│   │   │
│   │   ├──  database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py        # DB 연결 관리
│   │   │   ├── models.py             # SQLAlchemy ORM 모델
│   │   │   ├── repositories/         # Repository 패턴
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scan_repository.py
│   │   │   │   └── server_repository.py
│   │   │   └── migrations/           # Alembic 마이그레이션
│   │   │
│   │   ├──  network/
│   │   │   ├── __init__.py
│   │   │   ├── ssh_client.py        # AsyncSSH 래퍼
│   │   │   ├── winrm_client.py      # PyWinRM 래퍼
│   │   │   └── connection_pool.py   # 연결 풀 관리
│   │   │
│   │   └──  reporting/
│   │       ├── __init__.py
│   │       ├── base_reporter.py     # 추상 클래스
│   │       ├── pdf_reporter.py      # PDF 생성 (ReportLab)
│   │       ├── excel_reporter.py    # Excel 생성 (openpyxl)
│   │       ├── html_reporter.py     # HTML 생성 (Jinja2)
│   │       └── email_sender.py      # 이메일 발송
│   │
│   └──  utils/                     # 공통 유틸리티
│       ├── __init__.py
│       ├── logger.py                 # 로깅 설정
│       ├── config.py                 # 설정 관리
│       ├── validators.py             # 입력 검증
│       ├── crypto.py                 # 암호화 (크레덴셜)
│       └── exceptions.py             # 커스텀 예외
│
├──  config/                        # ️ 설정 파일
│   ├── default.yaml                  # 기본 설정
│   ├── servers.yaml                  # 서버 목록
│   ├── logging.yaml                  # 로깅 설정
│   │
│   └──  rules/                     # 점검 규칙 (YAML)
│       ├──  linux/
│       │   ├── account.yaml          # 계정 관리 (15개)
│       │   ├── filesystem.yaml       # 파일/디렉터리 (20개)
│       │   ├── service.yaml          # 서비스 (35개)
│       │   ├── patch.yaml            # 패치 (1개)
│       │   └── log.yaml              # 로그 (2개)
│       │
│       ├──  macos/
│       │   ├── account.yaml
│       │   ├── filesystem.yaml
│       │   ├── system.yaml           # SIP, Gatekeeper 등
│       │   └── network.yaml
│       │
│       └──  windows/
│           ├── account.yaml
│           ├── registry.yaml
│           ├── service.yaml
│           └── firewall.yaml
│
├──  data/                          # 데이터 저장소 (Git 제외)
│   ├──  databases/
│   │   └── bluepy.db                 # SQLite 파일
│   ├──  reports/                   # 생성된 보고서
│   └──  backups/                   # 백업 파일
│
├──  tests/                         # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py                   # pytest 설정
│   │
│   ├──  unit/                      # 단위 테스트
│   │   ├── test_scanner.py
│   │   ├── test_analyzer.py
│   │   ├── test_remediation.py
│   │   └── ...
│   │
│   ├──  integration/               # 통합 테스트
│   │   ├── test_scan_workflow.py
│   │   ├── test_remediation_workflow.py
│   │   └── ...
│   │
│   └──  fixtures/                  # 테스트 데이터
│       ├── sample_rules.yaml
│       └── mock_responses.json
│
├──  scripts/                       # 유틸리티 스크립트
│   ├── migrate_legacy.py             # 기존 코드 마이그레이션
│   ├── import_rules.py               # 규칙 가져오기
│   ├── build.py                      # PyInstaller 빌드
│   └── setup_dev.sh                  # 개발 환경 설정
│
├──  docs/                          # 문서
│   ├── ARCHITECTURE.md               # 이 문서
│   ├── ROADMAP.md                    # 개발 로드맵
│   ├── LEGACY_ANALYSIS.md            # 기존 시스템 분석
│   ├── PLATFORM_DETAILS.md           # 플랫폼별 상세
│   ├── USER_MANUAL.md                # 사용자 매뉴얼
│   └── API_REFERENCE.md              # API 문서
│
└──  legacy/                        # 기존 코드 (참고용, Git 제외)
    └── infra/                        # 2017년 프로젝트
```

### 4.2 주요 파일 설명

| 파일 | 설명 |
|------|------|
| `src/__main__.py` | 진입점, `python -m src` 실행 |
| `src/gui/app.py` | GUI 애플리케이션 시작 |
| `src/core/scanner/base_scanner.py` | 모든 Scanner의 기본 클래스 |
| `src/application/scan_service.py` | 스캔 관련 비즈니스 로직 |
| `config/rules/linux/account.yaml` | Linux 계정 관리 규칙 |
| `tests/conftest.py` | pytest 공통 픽스처 |

---

## 5. 핵심 모듈 설계

### 5.1 Scanner 모듈

#### 클래스 다이어그램

```
┌──────────────────────────────────┐
│      BaseScanner (ABC)           │
├──────────────────────────────────┤
│ + connect()                      │
│ + disconnect()                   │
│ + scan() -> ScanResult           │
│ + execute_command(cmd) -> str    │
│ # _load_rules() -> List[Rule]    │
│ # _parse_result(raw) -> Result   │
└──────────────────────────────────┘
                 △
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────────┐ ┌───▼──────────────┐
│ UnixScanner      │ │WindowsScanner    │
├──────────────────┤ ├──────────────────┤
│ # check_file_    │ │ # check_registry │
│   permission()   │ │ # check_service  │
│ # check_process  │ │ # check_firewall │
└──────────────────┘ └──────────────────┘
         △
         │
    ┌────┴─────┐
    │          │
┌───▼────┐ ┌──▼──────┐
│Linux   │ │macOS    │
│Scanner │ │Scanner  │
└────────┘ └─────────┘
```

#### 코드 예시

```python
# src/core/scanner/base_scanner.py
from abc import ABC, abstractmethod
from typing import List
from ..domain.scan_result import ScanResult
from ..domain.check_item import CheckItem

class BaseScanner(ABC):
    """모든 Scanner의 기본 클래스"""

    def __init__(self, server_info: dict):
        self.server_info = server_info
        self.rules: List[CheckItem] = []
        self.connection = None

    @abstractmethod
    async def connect(self) -> bool:
        """서버 연결 (SSH/WinRM)"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """연결 종료"""
        pass

    @abstractmethod
    async def execute_command(self, command: str) -> str:
        """명령어 실행"""
        pass

    async def scan(self) -> ScanResult:
        """전체 점검 실행"""
        await self.connect()
        self._load_rules()

        results = []
        for rule in self.rules:
            result = await self._check_item(rule)
            results.append(result)

        await self.disconnect()
        return ScanResult(results=results)

    @abstractmethod
    def _load_rules(self) -> None:
        """플랫폼별 규칙 로드"""
        pass

    async def _check_item(self, item: CheckItem) -> dict:
        """개별 점검 항목 실행"""
        raw_output = await self.execute_command(item.command)
        is_compliant = self._validate(raw_output, item.validator)

        return {
            "item_id": item.id,
            "status": "pass" if is_compliant else "fail",
            "raw_output": raw_output
        }

    @abstractmethod
    def _validate(self, output: str, validator: str) -> bool:
        """결과 검증"""
        pass
```

```python
# src/core/scanner/unix_scanner.py
import asyncio
from .base_scanner import BaseScanner

class UnixScanner(BaseScanner):
    """Linux와 macOS 공통 로직"""

    async def execute_command(self, command: str) -> str:
        """SSH로 명령어 실행"""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode()

    def check_file_permission(self, file_path: str, expected_perm: str) -> bool:
        """파일 권한 확인 (Unix 공통)"""
        output = await self.execute_command(f"ls -l {file_path}")
        # 권한 파싱 로직
        return actual_perm == expected_perm
```

```python
# src/core/scanner/linux_scanner.py
from .unix_scanner import UnixScanner
from ..scanner.rule_loader import RuleLoader

class LinuxScanner(UnixScanner):
    """Linux 특화 Scanner"""

    def _load_rules(self) -> None:
        """Linux 규칙 로드"""
        loader = RuleLoader(platform="linux")
        self.rules = loader.load_all()

    async def check_systemd_service(self, service_name: str) -> bool:
        """systemd 서비스 확인 (Linux 전용)"""
        output = await self.execute_command(f"systemctl status {service_name}")
        return "active" in output
```

```python
# src/core/scanner/macos_scanner.py
from .unix_scanner import UnixScanner

class MacOSScanner(UnixScanner):
    """macOS 특화 Scanner"""

    def _load_rules(self) -> None:
        """macOS 규칙 로드"""
        loader = RuleLoader(platform="macos")
        self.rules = loader.load_all()

    async def check_sip_status(self) -> bool:
        """SIP 상태 확인 (macOS 전용)"""
        output = await self.execute_command("csrutil status")
        return "enabled" in output.lower()

    async def check_gatekeeper(self) -> bool:
        """Gatekeeper 확인 (macOS 전용)"""
        output = await self.execute_command("spctl --status")
        return "assessments enabled" in output.lower()
```

#### Scanner Factory

```python
# src/core/scanner/scanner_factory.py
from .linux_scanner import LinuxScanner
from .macos_scanner import MacOSScanner
from .windows_scanner import WindowsScanner

class ScannerFactory:
    """Scanner 팩토리"""

    @staticmethod
    def create(platform: str, server_info: dict):
        """플랫폼에 맞는 Scanner 생성"""
        scanners = {
            "linux": LinuxScanner,
            "macos": MacOSScanner,
            "windows": WindowsScanner
        }

        scanner_class = scanners.get(platform.lower())
        if not scanner_class:
            raise ValueError(f"Unsupported platform: {platform}")

        return scanner_class(server_info)
```

### 5.2 Analyzer 모듈

```python
# src/core/analyzer/risk_calculator.py
from ..domain.enums import Severity

class RiskCalculator:
    """위험도 계산"""

    def calculate_score(self, scan_result) -> float:
        """전체 점수 계산 (0~100)"""
        total_items = len(scan_result.items)
        passed_items = sum(1 for item in scan_result.items if item.status == "pass")

        return (passed_items / total_items) * 100

    def get_severity_distribution(self, scan_result) -> dict:
        """위험도 분포"""
        distribution = {
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0
        }

        for item in scan_result.items:
            if item.status == "fail":
                distribution[item.severity] += 1

        return distribution
```

### 5.3 Remediation 모듈

```python
# src/core/remediation/base_remediator.py
from abc import ABC, abstractmethod
from typing import List
from ..domain.check_item import CheckItem
from .backup_manager import BackupManager

class BaseRemediator(ABC):
    """자동 수정 기본 클래스"""

    def __init__(self, scanner, dry_run=True):
        self.scanner = scanner
        self.dry_run = dry_run
        self.backup_manager = BackupManager()

    async def remediate(self, items: List[CheckItem]) -> dict:
        """자동 수정 실행"""
        results = {
            "total": len(items),
            "success": 0,
            "failed": 0,
            "skipped": 0
        }

        for item in items:
            if not item.auto_remediable:
                results["skipped"] += 1
                continue

            # 백업
            if item.backup_files:
                await self.backup_manager.backup(item.backup_files)

            # 수정 실행
            try:
                if self.dry_run:
                    # Dry-run: 시뮬레이션만
                    success = self._simulate_fix(item)
                else:
                    success = await self._execute_fix(item)

                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    # 롤백
                    if item.backup_files:
                        await self.backup_manager.rollback(item.backup_files)

            except Exception as e:
                results["failed"] += 1
                # 롤백
                if item.backup_files:
                    await self.backup_manager.rollback(item.backup_files)

        return results

    @abstractmethod
    async def _execute_fix(self, item: CheckItem) -> bool:
        """실제 수정 실행"""
        pass

    def _simulate_fix(self, item: CheckItem) -> bool:
        """수정 시뮬레이션 (Dry-run)"""
        # 명령어 실행하지 않고 검증만
        return True
```

```python
# src/core/remediation/backup_manager.py
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    """백업 관리"""

    def __init__(self, backup_dir="/var/bluepy/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def backup(self, files: List[str]) -> str:
        """파일 백업"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir()

        for file_path in files:
            src = Path(file_path)
            dst = backup_path / src.name
            shutil.copy2(src, dst)

        return backup_id

    async def rollback(self, backup_id: str) -> bool:
        """백업에서 복원"""
        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            return False

        for file_path in backup_path.iterdir():
            # 원래 위치로 복원
            # (실제 구현 시 원본 경로 메타데이터 필요)
            shutil.copy2(file_path, original_location)

        return True
```

---

## 6. 데이터 모델

### 6.1 Domain Entities

```python
# src/core/domain/check_item.py
from dataclasses import dataclass
from typing import List, Optional
from .enums import Severity, Platform

@dataclass
class CheckItem:
    """점검 항목 엔티티"""
    id: str                           # 예: "U-01", "M-01"
    name: str                         # 예: "root 원격 로그인 제한"
    category: str                     # 예: "account_management"
    severity: Severity                # HIGH, MEDIUM, LOW
    platforms: List[Platform]         # [LINUX], [MACOS], etc.
    description: str                  # 설명
    commands: List[str]               # 실행할 명령어
    validator: str                    # 검증 함수명
    auto_remediable: bool             # 자동 수정 가능 여부
    remediation_steps: List[str]      # 수정 단계
    backup_files: List[str]           # 백업할 파일
    references: dict                  # KISA, CVE 등 참조
    education: dict                   # 교육 콘텐츠
```

```python
# src/core/domain/scan_result.py
from dataclasses import dataclass
from datetime import datetime
from typing import List
from .enums import Status

@dataclass
class CheckResult:
    """개별 점검 결과"""
    item_id: str
    status: Status                    # PASS, FAIL, HOLD
    raw_output: str                   # 명령어 실행 결과
    message: str                      # 사용자 메시지
    timestamp: datetime

@dataclass
class ScanResult:
    """전체 스캔 결과"""
    scan_id: str
    server_id: str
    platform: Platform
    start_time: datetime
    end_time: datetime
    results: List[CheckResult]
    score: float                      # 0~100
    summary: dict                     # 통계
```

```python
# src/core/domain/enums.py
from enum import Enum

class Severity(str, Enum):
    """위험도"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(str, Enum):
    """점검 상태"""
    PASS = "pass"        # 안전
    FAIL = "fail"        # 취약
    HOLD = "hold"        # 수동 확인 필요

class Platform(str, Enum):
    """플랫폼"""
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
```

### 6.2 Infrastructure Models (ORM)

```python
# src/infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    platform = Column(String(20), nullable=False)  # linux, macos, windows
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=22)
    username = Column(String(100))
    # 비밀번호는 keyring에 저장
    group = Column(String(50))  # 예: dev, prod, test
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    scans = relationship("Scan", back_populates="server")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    scan_id = Column(String(50), unique=True)  # UUID
    server_id = Column(Integer, ForeignKey("servers.id"))
    platform = Column(String(20))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    score = Column(Float)  # 0~100
    total_items = Column(Integer)
    passed_items = Column(Integer)
    failed_items = Column(Integer)
    hold_items = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    server = relationship("Server", back_populates="scans")
    results = relationship("CheckResultModel", back_populates="scan")

class CheckResultModel(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    item_id = Column(String(20))  # U-01, M-01 등
    status = Column(String(20))  # pass, fail, hold
    raw_output = Column(Text)
    message = Column(Text)
    severity = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 관계
    scan = relationship("Scan", back_populates="results")
```

---

## 7. 규칙 시스템

### 7.1 YAML 규칙 구조

```yaml
# config/rules/linux/account.yaml

# U-01: root 원격 로그인 제한
- id: U-01
  name: root 원격 로그인 제한
  category: account_management
  severity: high
  platforms:
    - linux

  description: |
    root 계정의 원격 로그인을 허용하면
    무차별 대입 공격(Brute Force Attack)에 취약합니다.

    공격자가 root 비밀번호만 알아내면
    시스템 전체를 장악할 수 있습니다.

  check:
    commands:
      - cat /etc/pam.d/login | grep pam_securetty
      - cat /etc/securetty | grep pts
    validator: check_root_remote_login
    # validator 함수가 True를 반환하면 PASS

  remediation:
    auto: true
    backup_files:
      - /etc/pam.d/login
      - /etc/securetty
    steps:
      - |
        # /etc/pam.d/login에 pam_securetty 모듈 추가
        if ! grep -q "pam_securetty" /etc/pam.d/login; then
          echo "auth required /lib/security/pam_securetty.so" >> /etc/pam.d/login
        fi
      - |
        # /etc/securetty에서 pts 제거
        sed -i '/^pts/d' /etc/securetty
    rollback_safe: true

  education:
    risk_level: 치명적
    attack_scenario: |
      1. 공격자가 인터넷에서 서버 IP 탐색
      2. SSH로 root 로그인 시도 (무차별 대입)
      3. 비밀번호 획득 시 전체 시스템 장악
      4. 백도어 설치, 데이터 탈취

    fix_guide: |
      ### 수동 수정 방법

      1. /etc/pam.d/login 파일 편집
         ```bash
         sudo vi /etc/pam.d/login
         ```

      2. 다음 라인 추가
         ```
         auth required /lib/security/pam_securetty.so
         ```

      3. /etc/securetty에서 pts 제거
         ```bash
         sudo sed -i '/^pts/d' /etc/securetty
         ```

      4. 검증
         ```bash
         grep pam_securetty /etc/pam.d/login
         ```

    related_cves: []

  references:
    kisa: U-01
    cis: "5.2.8 Ensure SSH root login is disabled"
    nist: "IA-2"

# U-02: 패스워드 복잡도 설정
- id: U-02
  name: 패스워드 복잡도 설정
  category: account_management
  severity: high
  platforms:
    - linux

  # ... (유사한 구조)
```

### 7.2 Rule Loader

```python
# src/core/scanner/rule_loader.py
import yaml
from pathlib import Path
from typing import List
from ..domain.check_item import CheckItem
from ..domain.enums import Severity, Platform

class RuleLoader:
    """YAML 규칙 파일 로더"""

    def __init__(self, platform: str, rules_dir: str = "config/rules"):
        self.platform = platform
        self.rules_dir = Path(rules_dir) / platform

    def load_all(self) -> List[CheckItem]:
        """모든 규칙 로드"""
        rules = []

        for yaml_file in self.rules_dir.glob("*.yaml"):
            rules.extend(self._load_file(yaml_file))

        return rules

    def _load_file(self, file_path: Path) -> List[CheckItem]:
        """개별 YAML 파일 로드"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return [self._parse_rule(rule_dict) for rule_dict in data]

    def _parse_rule(self, rule_dict: dict) -> CheckItem:
        """YAML 딕셔너리를 CheckItem으로 변환"""
        return CheckItem(
            id=rule_dict['id'],
            name=rule_dict['name'],
            category=rule_dict['category'],
            severity=Severity(rule_dict['severity']),
            platforms=[Platform(p) for p in rule_dict['platforms']],
            description=rule_dict['description'],
            commands=rule_dict['check']['commands'],
            validator=rule_dict['check']['validator'],
            auto_remediable=rule_dict['remediation']['auto'],
            remediation_steps=rule_dict['remediation']['steps'],
            backup_files=rule_dict['remediation'].get('backup_files', []),
            references=rule_dict['references'],
            education=rule_dict['education']
        )
```

### 7.3 Validator 시스템

```python
# src/core/analyzer/validator.py
import re

class Validator:
    """규칙 검증 함수 모음"""

    @staticmethod
    def check_root_remote_login(outputs: List[str]) -> bool:
        """U-01: root 원격 로그인 검증"""
        pam_output, securetty_output = outputs

        # pam_securetty가 있어야 함
        has_pam = "pam_securetty" in pam_output

        # pts가 없어야 함
        has_pts = "pts" in securetty_output

        return has_pam and not has_pts

    @staticmethod
    def check_password_complexity(outputs: List[str]) -> bool:
        """U-02: 패스워드 복잡도 검증"""
        output = outputs[0]

        # pam_cracklib 또는 pam_pwquality가 있어야 함
        return "pam_cracklib" in output or "pam_pwquality" in output

    @staticmethod
    def check_file_permission(outputs: List[str], expected: str) -> bool:
        """파일 권한 검증 (범용)"""
        output = outputs[0]

        # ls -l 출력 파싱
        # 예: -rw-r--r--. 1 root root 1320 3월 13 2017 /etc/passwd
        match = re.search(r'^([rwx-]{10})', output)
        if not match:
            return False

        actual_perm = match.group(1)
        return actual_perm == expected

    # macOS 전용
    @staticmethod
    def check_sip_enabled(outputs: List[str]) -> bool:
        """M-01: SIP 활성화 검증"""
        output = outputs[0].lower()
        return "enabled" in output

    @staticmethod
    def check_gatekeeper(outputs: List[str]) -> bool:
        """M-02: Gatekeeper 검증"""
        output = outputs[0].lower()
        return "assessments enabled" in output
```

---

## 8. 통신 및 네트워크

### 8.1 SSH 클라이언트

```python
# src/infrastructure/network/ssh_client.py
import asyncssh
from typing import Optional

class SSHClient:
    """AsyncSSH 래퍼"""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn: Optional[asyncssh.SSHClientConnection] = None

    async def connect(self) -> bool:
        """SSH 연결"""
        try:
            self.conn = await asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                known_hosts=None  # 프로덕션에서는 검증 필요
            )
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def execute(self, command: str, sudo: bool = False) -> tuple[str, str]:
        """명령어 실행"""
        if sudo:
            command = f"echo {self.password} | sudo -S {command}"

        result = await self.conn.run(command)
        return result.stdout, result.stderr

    async def disconnect(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
            await self.conn.wait_closed()
```

### 8.2 WinRM 클라이언트

```python
# src/infrastructure/network/winrm_client.py
import winrm

class WinRMClient:
    """PyWinRM 래퍼"""

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.session = None

    def connect(self) -> bool:
        """WinRM 연결"""
        try:
            self.session = winrm.Session(
                f'https://{self.host}:5986/wsman',
                auth=(self.username, self.password),
                server_cert_validation='ignore'  # 프로덕션에서는 검증 필요
            )
            # 연결 테스트
            result = self.session.run_cmd('echo test')
            return result.status_code == 0
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def execute_powershell(self, script: str) -> tuple[str, str]:
        """PowerShell 스크립트 실행"""
        result = self.session.run_ps(script)
        return result.std_out.decode(), result.std_err.decode()

    def disconnect(self):
        """연결 종료"""
        # WinRM 세션은 자동으로 정리됨
        self.session = None
```

---

## 9. 데이터베이스 설계

### 9.1 ERD

```
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│     Server      │       │      Scan       │       │  CheckResult     │
├─────────────────┤       ├─────────────────┤       ├──────────────────┤
│ id (PK)         │1    ∞│ id (PK)         │1    ∞│ id (PK)          │
│ name            │───────│ scan_id (UK)    │───────│ scan_id (FK)     │
│ platform        │       │ server_id (FK)  │       │ item_id          │
│ host            │       │ platform        │       │ status           │
│ port            │       │ start_time      │       │ raw_output       │
│ username        │       │ end_time        │       │ message          │
│ group           │       │ score           │       │ severity         │
│ created_at      │       │ total_items     │       │ timestamp        │
│ updated_at      │       │ passed_items    │       └──────────────────┘
└─────────────────┘       │ failed_items    │
                          │ hold_items      │
                          │ created_at      │
                          └─────────────────┘
```

### 9.2 스키마 생성 (SQLite)

```sql
-- servers 테이블
CREATE TABLE servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,  -- linux, macos, windows
    host VARCHAR(255) NOT NULL,
    port INTEGER DEFAULT 22,
    username VARCHAR(100),
    group_name VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- scans 테이블
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id VARCHAR(50) UNIQUE NOT NULL,  -- UUID
    server_id INTEGER NOT NULL,
    platform VARCHAR(20),
    start_time DATETIME,
    end_time DATETIME,
    score REAL,  -- 0~100
    total_items INTEGER,
    passed_items INTEGER,
    failed_items INTEGER,
    hold_items INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);

-- check_results 테이블
CREATE TABLE check_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    item_id VARCHAR(20),  -- U-01, M-01 등
    status VARCHAR(20),  -- pass, fail, hold
    raw_output TEXT,
    message TEXT,
    severity VARCHAR(20),  -- high, medium, low
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- 인덱스
CREATE INDEX idx_scans_server_id ON scans(server_id);
CREATE INDEX idx_scans_created_at ON scans(created_at);
CREATE INDEX idx_check_results_scan_id ON check_results(scan_id);
CREATE INDEX idx_check_results_status ON check_results(status);
```

### 9.3 Repository 패턴

```python
# src/infrastructure/database/repositories/scan_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Scan, CheckResultModel
from ...core.domain.scan_result import ScanResult

class ScanRepository:
    """Scan 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, scan_result: ScanResult) -> int:
        """ScanResult 저장"""
        # Domain Entity → ORM Model 변환
        scan = Scan(
            scan_id=scan_result.scan_id,
            server_id=scan_result.server_id,
            platform=scan_result.platform.value,
            start_time=scan_result.start_time,
            end_time=scan_result.end_time,
            score=scan_result.score,
            total_items=len(scan_result.results),
            passed_items=sum(1 for r in scan_result.results if r.status == "pass"),
            failed_items=sum(1 for r in scan_result.results if r.status == "fail"),
            hold_items=sum(1 for r in scan_result.results if r.status == "hold")
        )

        self.session.add(scan)
        self.session.flush()  # ID 생성

        # CheckResult 저장
        for result in scan_result.results:
            check_result = CheckResultModel(
                scan_id=scan.id,
                item_id=result.item_id,
                status=result.status.value,
                raw_output=result.raw_output,
                message=result.message,
                severity=result.severity.value,
                timestamp=result.timestamp
            )
            self.session.add(check_result)

        self.session.commit()
        return scan.id

    def find_by_id(self, scan_id: int) -> Optional[ScanResult]:
        """ID로 Scan 조회"""
        scan = self.session.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return None

        # ORM Model → Domain Entity 변환
        return self._to_domain(scan)

    def find_by_server(self, server_id: int, limit: int = 10) -> List[ScanResult]:
        """서버별 Scan 조회 (최근순)"""
        scans = self.session.query(Scan)\
            .filter(Scan.server_id == server_id)\
            .order_by(Scan.created_at.desc())\
            .limit(limit)\
            .all()

        return [self._to_domain(scan) for scan in scans]

    def _to_domain(self, scan: Scan) -> ScanResult:
        """ORM Model을 Domain Entity로 변환"""
        # ... 변환 로직
        pass
```

---

## 10. 보안 설계

### 10.1 크레덴셜 관리

```python
# src/utils/crypto.py
import keyring
from cryptography.fernet import Fernet

class CredentialManager:
    """크레덴셜 안전 저장"""

    SERVICE_NAME = "bluepy"

    @staticmethod
    def save_password(server_id: str, password: str):
        """비밀번호 저장 (OS Keyring 사용)"""
        keyring.set_password(
            CredentialManager.SERVICE_NAME,
            server_id,
            password
        )

    @staticmethod
    def get_password(server_id: str) -> str:
        """비밀번호 조회"""
        return keyring.get_password(
            CredentialManager.SERVICE_NAME,
            server_id
        )

    @staticmethod
    def delete_password(server_id: str):
        """비밀번호 삭제"""
        keyring.delete_password(
            CredentialManager.SERVICE_NAME,
            server_id
        )
```

### 10.2 감사 로그

```python
# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_audit_logger():
    """감사 로그 설정"""
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        'logs/audit.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)

    return audit_logger

# 사용 예시
audit = setup_audit_logger()
audit.info(f"User {user_id} started scan on server {server_id}")
audit.info(f"User {user_id} executed remediation on {item_id}")
```

---

## 11. 확장성 전략

### 11.1 플러그인 시스템

```python
# src/core/scanner/plugin_manager.py
import importlib
from pathlib import Path

class PluginManager:
    """플러그인 관리"""

    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = {}

    def load_plugins(self):
        """플러그인 로드"""
        for py_file in self.plugin_dir.glob("*.py"):
            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Scanner 클래스 찾기
            if hasattr(module, 'Scanner'):
                self.plugins[module_name] = module.Scanner

    def get_plugin(self, name: str):
        """플러그인 조회"""
        return self.plugins.get(name)
```

### 11.2 커스텀 규칙

사용자가 `config/rules/custom/` 폴더에 자신만의 YAML 규칙을 추가 가능:

```yaml
# config/rules/custom/my_custom_check.yaml
- id: C-01
  name: 내부 보안 정책 확인
  category: custom
  severity: medium
  platforms:
    - linux

  check:
    commands:
      - cat /etc/company_policy.conf
    validator: check_company_policy

  # ...
```

---

## 12. 성능 최적화

### 12.1 비동기 스캔

```python
# 병렬 스캔
async def scan_multiple_items(items: List[CheckItem]):
    """여러 항목을 동시에 점검"""
    tasks = [scan_single_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

### 12.2 캐싱

```python
# src/core/scanner/cache.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_os_version(host: str) -> str:
    """OS 버전 캐싱 (점검 중 여러 번 호출되므로)"""
    # ... SSH로 uname -a 실행
    pass
```

### 12.3 연결 풀

```python
# src/infrastructure/network/connection_pool.py
class ConnectionPool:
    """SSH 연결 풀 관리"""

    def __init__(self, max_connections=5):
        self.pool = {}
        self.max_connections = max_connections

    async def get_connection(self, server_id: str):
        """연결 가져오기 (재사용)"""
        if server_id in self.pool:
            return self.pool[server_id]

        # 새 연결 생성
        conn = await create_ssh_connection(server_id)
        self.pool[server_id] = conn
        return conn
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-10-17 | 1.0 | 초안 작성 | Claude |

---

**문서 끝**