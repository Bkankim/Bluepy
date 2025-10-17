# BluePy 2.0 - 프로젝트 계획서

**작성일**: 2025-10-17
**프로젝트 기간**: 12.5주 (예상)
**버전**: 2.0 (2017년 Legacy 재구성)

---

## 📋 목차

1. [Executive Summary](#executive-summary)
2. [프로젝트 비전 및 배경](#프로젝트-비전-및-배경)
3. [핵심 목표 및 차별화](#핵심-목표-및-차별화)
4. [타겟 사용자](#타겟-사용자)
5. [기술 스택](#기술-스택)
6. [시스템 아키텍처 개요](#시스템-아키텍처-개요)
7. [프로젝트 구조](#프로젝트-구조)
8. [개발 로드맵](#개발-로드맵)
9. [리스크 관리](#리스크-관리)
10. [성공 지표](#성공-지표)
11. [다음 단계](#다음-단계)
12. [참조 문서](#참조-문서)

---

## 1. Executive Summary

### 한 문장 요약
**"비전공자도 버튼 클릭만으로 리눅스/맥OS/윈도우 서버의 보안을 진단하고 자동으로 수정할 수 있는 GUI 기반 인프라 보안 관리 플랫폼"**

### 핵심 목표 3가지

1. **멀티플랫폼 지원**: Linux, macOS, Windows 통합 점검 (총 170+ 항목)
2. **원클릭 자동 수정**: 취약점을 자동으로 수정하고 백업/롤백 지원
3. **비전공자 친화**: 쉬운 GUI + 교육 콘텐츠 + 한글 지원

### 개발 기간
- **총 기간**: 12.5주 (약 3개월)
- **MVP**: 4주 (Linux만)
- **완성**: 12.5주 (3-OS + 자동수정 + 고급기능)

### 차별화 포인트

| 항목 | 경쟁 도구 | BluePy 2.0 |
|------|----------|-----------|
| **플랫폼** | Linux/Windows | **Linux + macOS + Windows** |
| **자동 수정** | ❌ 또는 부분 | ✅ **원클릭 + 롤백** |
| **GUI** | CLI 중심 | ✅ **비전공자용 GUI** |
| **교육** | 없음 | ✅ **내장 교육 콘텐츠** |
| **언어** | 영어 | ✅ **한글 지원** |
| **KISA 준수** | 부분 | ✅ **KISA 기준 완전 준수** |

---

## 2. 프로젝트 비전 및 배경

### 2.1 현재 상황 (2017년 Legacy 시스템)

#### 기존 시스템 개요
- **개발 시기**: 2017년 (8년 전)
- **플랫폼**: Linux만 지원
- **아키텍처**: 3계층 파이프라인
  ```
  [점검 명령어 73개] → [Python2 분석] → [Excel 보고서]
  ```
- **통신**: Python2 소켓 통신 (포트 8282)
- **GUI**: Qt 5.7.2 (C++)
- **점검 항목**: KISA 기준 73개 (Linux)

#### 주요 문제점

**기술 부채**:
- ❌ Python 2 사용 (2020년 EOL, 보안 업데이트 없음)
- ❌ 하드코딩된 73개 함수 (`_1SCRIPT` ~ `_73SCRIPT`)
- ❌ 한글 인코딩 깨짐 (cp949/utf-8 혼재)
- ❌ 에러 처리 부재 (try-except으로 무시)

**확장성 한계**:
- ❌ 새 점검 항목 추가 시 전체 코드 수정 필요
- ❌ Windows 지원 미구현 (TODO 상태로 남음)
- ❌ 다중 서버 관리 불가

**사용성 문제**:
- ❌ CLI 전문가만 사용 가능
- ❌ 결과가 숫자 코드 (0=안전, 1=취약, 2=보류)로만 표시
- ❌ 수동 수정 (자동화 없음)
- ❌ 실시간 진행률 표시 없음

**보안 문제**:
- ❌ 인증 없는 소켓 통신
- ❌ 평문 데이터 전송
- ❌ root 권한 필수

### 2.2 목표 상태 (2025년 BluePy 2.0)

#### 비전
**"중소기업과 스타트업도 전문 보안 인력 없이 인프라 보안을 관리할 수 있는 플랫폼"**

#### 핵심 개선 사항

**현대적 기술 스택**:
- ✅ Python 3.12+ (최신 기능 + 성능 + 보안)
- ✅ PySide6 (크로스 플랫폼 GUI)
- ✅ YAML 규칙 시스템 (확장 가능)
- ✅ AsyncIO (비동기 처리)

**확장 가능한 아키텍처**:
- ✅ Clean Architecture (계층 분리)
- ✅ 플러그인 시스템
- ✅ 규칙 기반 엔진 (하드코딩 제거)
- ✅ 멀티플랫폼 지원

**자동화 및 편의성**:
- ✅ 원클릭 자동 수정
- ✅ 백업/롤백 시스템
- ✅ 실시간 진행률 표시
- ✅ 스케줄링 (정기 점검)

**교육 및 접근성**:
- ✅ 각 취약점 설명 (쉬운 용어)
- ✅ 공격 시나리오 제공
- ✅ 수정 가이드 (스크린샷)
- ✅ 한글 UI/문서

---

## 3. 핵심 목표 및 차별화

### 3.1 핵심 기능

#### 1. 멀티플랫폼 보안 점검

**지원 플랫폼**:
- **Linux** (73개 항목)
  - 계정 관리 (15개)
  - 파일/디렉터리 (20개)
  - 서비스 관리 (35개)
  - 패치 관리 (1개)
  - 로그 관리 (2개)

- **macOS** (50개 항목) - 신규
  - Linux 재사용 (40개)
  - macOS 전용 (10개): SIP, FileVault, Gatekeeper 등

- **Windows** (예정, 50~70개 항목)
  - 계정 정책
  - 레지스트리 설정
  - 방화벽/서비스

**점검 방식**:
```yaml
# 규칙 예시: rules/linux/account.yaml
id: U-01
name: root 원격 로그인 제한
category: account_management
severity: high
platforms: [linux]

check:
  commands:
    - cat /etc/pam.d/login | grep pam_securetty
    - cat /etc/securetty | grep pts

remediation:
  auto: true
  backup_files:
    - /etc/pam.d/login
  steps:
    - echo "auth required /lib/security/pam_securetty.so" >> /etc/pam.d/login
```

#### 2. 원클릭 자동 수정

**기능**:
- 취약점 자동 수정
- 수정 전 백업 자동 생성
- 미리보기 (변경 사항 확인)
- 원클릭 롤백
- 배치 수정 (여러 항목 동시)

**안전 장치**:
- Dry-run 모드 (실제 수정 안 함)
- 수정 로그 기록
- 백업 파일 버전 관리
- 롤백 성공 검증

#### 3. 비전공자 친화 GUI

**메인 화면**:
- 대시보드 (전체 점수, 위험 분포)
- 서버 카드 (연결 상태, 최근 점검)
- 빠른 액션 (전체 스캔, 자동 수정)

**점검 결과**:
- 트리 뷰 (카테고리별 정리)
- 색상 코드 (🔴 위험, 🟡 경고, 🟢 안전)
- 상세 설명 (왜 위험한지, 어떻게 고치는지)
- 진행률 표시 (실시간)

**교육 콘텐츠**:
- 각 취약점 설명
- 공격 시나리오
- 수정 가이드 (단계별)
- 관련 CVE 링크

#### 4. 이력 관리 및 분석

**이력 DB**:
- 과거 점검 결과 저장
- 트렌드 분석 (개선/악화)
- 비교 기능 (이전 vs 현재)
- 규정 준수 추적 (KISA, PCI-DSS)

**보고서**:
- PDF (경영진용 요약)
- Excel (기술팀용 상세)
- HTML (웹 공유)
- 이메일 자동 발송

### 3.2 차별화 전략

#### vs Lynis (오픈소스)
- Lynis: CLI 전문가용, 자동 수정 없음
- **BluePy**: GUI + 자동 수정 + 교육

#### vs CIS-CAT (상용)
- CIS-CAT: 비싸고 복잡함, macOS 미지원
- **BluePy**: 무료 + 간단 + 3-OS

#### vs OpenSCAP (오픈소스)
- OpenSCAP: Linux만, 학습 곡선 높음
- **BluePy**: 멀티플랫폼 + 쉬움

---

## 4. 타겟 사용자

### 4.1 Primary Target (주 타겟)

**중소기업 IT 담당자**:
- 인원: 1~3명
- 보안 전문 지식: 중하
- 니즈: 빠르고 쉬운 점검, 자동화
- 예산: 제한적 (무료 도구 선호)

**스타트업 DevOps 엔지니어**:
- 인원: 1~2명
- 플랫폼: Linux + macOS (개발용)
- 니즈: CI/CD 통합, 빠른 스캔
- 예산: 낮음

### 4.2 Secondary Target (부 타겟)

**프리랜서 보안 컨설턴트**:
- 여러 고객 관리
- 니즈: 다중 서버 관리, 보고서 자동화

**개인 개발자**:
- 개인 서버 운영 (블로그, 프로젝트)
- 니즈: 간단한 점검, 무료

### 4.3 Anti-Persona (타겟 아님)

- 대기업 보안팀 (전문 도구 사용)
- 클라우드 네이티브 기업 (다른 솔루션)

---

## 5. 기술 스택

### 5.1 핵심 기술

| 분야 | 기술 | 버전 | 선택 이유 |
|------|------|------|----------|
| **언어** | Python | 3.12+ | 기존 로직 재사용, 풍부한 라이브러리 |
| **GUI** | PySide6 | 6.6+ | Qt 공식, LGPL, 크로스 플랫폼 |
| **DB** | SQLite | 3.40+ | 단일 사용자, 설치 불필요 |
| **SSH** | AsyncSSH | 2.14+ | 비동기 처리, 성능 |
| **Windows** | PyWinRM | 0.4+ | Windows 원격 관리 |
| **패키징** | PyInstaller | 6.0+ | 단일 실행 파일 배포 |

### 5.2 주요 라이브러리

```python
# requirements.txt 주요 항목

# 코어
python>=3.12
pydantic>=2.0          # 데이터 검증
pyyaml>=6.0            # 규칙 파일
rich>=13.0             # CLI 출력

# GUI
PySide6>=6.6           # GUI 프레임워크
qt-material>=2.0       # Material Design 테마

# 네트워크
asyncssh>=2.14         # SSH (비동기)
paramiko>=3.4          # SSH (동기, 백업)
pywinrm>=0.4           # Windows Remote Management

# 데이터베이스
sqlalchemy>=2.0        # ORM
alembic>=1.13          # 마이그레이션

# 보고서
openpyxl>=3.1          # Excel 생성
reportlab>=4.0         # PDF 생성
jinja2>=3.1            # HTML 템플릿

# 보안
cryptography>=42.0     # 암호화
keyring>=25.0          # 크레덴셜 안전 저장

# 테스트
pytest>=8.0
pytest-asyncio>=0.23
pytest-qt>=4.3
pytest-cov>=4.1

# 개발 도구
black>=24.0            # 코드 포맷
ruff>=0.1              # 린터
mypy>=1.8              # 타입 체크
```

### 5.3 아키텍처 패턴

**Clean Architecture (Hexagonal Architecture)**:
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│    (GUI, CLI, API - PySide6/Click)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Application Layer              │
│    (Use Cases, Business Logic)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Domain Layer                 │
│  (Entities: CheckItem, ScanResult)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Infrastructure Layer             │
│  (DB, Network, File System, External)  │
└─────────────────────────────────────────┘
```

**설계 원칙**:
- **의존성 역전**: 외부 → 내부만 의존
- **단일 책임**: 각 모듈은 하나의 책임만
- **개방-폐쇄**: 확장에는 열려있고 수정에는 닫혀있음
- **인터페이스 분리**: 작고 명확한 인터페이스

---

## 6. 시스템 아키텍처 개요

### 6.1 전체 구조도

```
┌──────────────────────────────────────────────────────────┐
│                      BluePy 2.0 GUI                      │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐  │
│  │ Dashboard  │ │  Scan View │ │ Result/History View │  │
│  └────────────┘ └────────────┘ └─────────────────────┘  │
└────────────────────┬─────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │   Application Core    │
         │  ┌─────────────────┐  │
         │  │    Scanner      │  │ ← Linux/macOS/Windows
         │  ├─────────────────┤  │
         │  │    Analyzer     │  │ ← Risk Calculation
         │  ├─────────────────┤  │
         │  │  Remediation    │  │ ← Auto Fix
         │  └─────────────────┘  │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐    ┌─────▼─────┐    ┌────▼────┐
│   DB   │    │  Network  │    │  Report │
│SQLite  │    │SSH/WinRM  │    │PDF/Excel│
└────────┘    └───────────┘    └─────────┘
```

### 6.2 데이터 플로우

```
1. 사용자: "스캔 시작" 버튼 클릭
   ↓
2. GUI → Scanner: 점검 요청
   ↓
3. Scanner → 서버: SSH/WinRM 연결
   ↓
4. Scanner: 규칙 파일(YAML) 읽기
   ↓
5. Scanner: 명령어 실행 (비동기)
   ↓
6. Analyzer: 결과 파싱 및 위험도 계산
   ↓
7. DB: 결과 저장
   ↓
8. GUI: 결과 표시 (트리 뷰)
   ↓
9. 사용자: "자동 수정" 클릭 (선택)
   ↓
10. Remediation: 백업 → 수정 → 검증
   ↓
11. Report: PDF/Excel 생성
```

---

## 7. 프로젝트 구조

### 7.1 전체 폴더 구조

```
bluepy/
├── 📄 README.md                    # 프로젝트 소개
├── 📄 PROJECT_PLAN.md             # 이 문서
├── 📄 CLAUDE.md                    # AI 작업 지침
├── 📄 requirements.txt             # Python 의존성
├── 📄 pyproject.toml               # 최신 Python 프로젝트 표준
├── 📄 .gitignore
│
├── 📂 ai-dev-tasks/               # PRD/Task 관리
│   ├── create-prd.md
│   ├── generate-tasks.md
│   └── process-task-list.md
│
├── 📂 src/                        # 소스 코드
│   ├── __init__.py
│   │
│   ├── 📂 core/                   # 🧠 핵심 비즈니스 로직
│   │   ├── domain/               # 도메인 모델
│   │   ├── scanner/              # 스캔 엔진
│   │   ├── analyzer/             # 분석 엔진
│   │   └── remediation/          # 자동 수정
│   │
│   ├── 📂 gui/                    # 🖥️ PySide6 GUI
│   │   ├── main_window.py
│   │   ├── views/                # 화면
│   │   ├── widgets/              # 재사용 위젯
│   │   └── resources/            # UI 리소스
│   │
│   ├── 📂 infrastructure/         # 인프라 계층
│   │   ├── database/             # SQLite
│   │   ├── network/              # SSH/WinRM
│   │   └── reporting/            # PDF/Excel
│   │
│   └── 📂 utils/                  # 공통 유틸리티
│
├── 📂 config/                     # ⚙️ 설정 파일
│   ├── default.yaml
│   ├── servers.yaml
│   └── rules/                    # 점검 규칙 (YAML)
│       ├── linux/
│       ├── macos/
│       └── windows/
│
├── 📂 data/                       # 데이터 저장소
│   ├── databases/
│   └── reports/
│
├── 📂 tests/                      # 테스트 코드
│   ├── unit/
│   └── integration/
│
├── 📂 scripts/                    # 유틸리티 스크립트
│   ├── migrate_legacy.py
│   └── build.py
│
├── 📂 docs/                       # 문서
│   ├── ARCHITECTURE.md           # 아키텍처 상세
│   ├── ROADMAP.md                # 로드맵 상세
│   ├── LEGACY_ANALYSIS.md        # 기존 시스템 분석
│   └── USER_MANUAL.md            # 사용자 매뉴얼
│
└── 📂 legacy/                     # 기존 코드 (참고용)
    └── infra/
```

### 7.2 핵심 모듈 설명

#### src/core/scanner/
```python
# 스캔 엔진 구조
scanner/
├── base_scanner.py       # 추상 클래스
├── unix_scanner.py       # Linux + macOS 공통
├── linux_scanner.py      # Linux 특화
├── macos_scanner.py      # macOS 특화
└── windows_scanner.py    # Windows 특화

# 사용 예시
from src.core.scanner import LinuxScanner

scanner = LinuxScanner(ssh_client)
results = await scanner.scan_all()
```

#### config/rules/
```yaml
# 규칙 파일 구조 예시
id: U-01
name: root 원격 로그인 제한
category: account_management
severity: high
platforms: [linux]

description: |
  root 계정의 원격 로그인을 허용하면
  무차별 대입 공격에 취약합니다.

check:
  commands:
    - cat /etc/pam.d/login | grep pam_securetty
    - cat /etc/securetty | grep pts
  validator: check_root_remote_login

remediation:
  auto: true
  backup_files:
    - /etc/pam.d/login
    - /etc/securetty
  steps:
    - echo "auth required /lib/security/pam_securetty.so" >> /etc/pam.d/login
  rollback_safe: true

education:
  risk_level: 치명적
  attack_scenario: |
    공격자가 root 계정으로 직접 로그인 시도
  fix_guide: |
    1. /etc/pam.d/login 편집
    2. pam_securetty 모듈 추가

references:
  - kisa: "U-01"
  - cve: []
```

---

## 8. 개발 로드맵

### 8.1 전체 타임라인 (12.5주)

```
Week  1  2  3  4  5  6  7  8  9  10 11 12 13
      [─Phase 1─][P2][──Phase 3─][─Phase 4─][P5]
       Linux MVP  M  Auto-Fix    Windows    Adv
```

### 8.2 Phase별 상세 계획

#### Phase 1: Linux MVP (4주)

**목표**: 기존 기능을 현대적으로 재구현

**주요 작업**:
- [ ] Week 1: 프로젝트 구조 생성 + 기존 코드 마이그레이션 시작
  - Git 초기화
  - 폴더 구조 생성
  - Python 2 → 3 변환 (73개 함수)
  - 규칙 YAML 변환 시작

- [ ] Week 2: Linux 스캐너 구현
  - BaseScanner 추상 클래스
  - LinuxScanner 구현
  - SSH 연결 모듈
  - 규칙 파일 파서

- [ ] Week 3: GUI 기본 구조
  - MainWindow (PySide6)
  - 서버 관리 뷰
  - 스캔 실행 뷰
  - 결과 트리 뷰

- [ ] Week 4: 보고서 + 테스트
  - Excel 보고서 생성
  - 단위 테스트 (커버리지 60%+)
  - 통합 테스트
  - 버그 수정

**결과물**:
- ✅ Linux 73개 규칙 점검 가능
- ✅ GUI로 스캔 실행 및 결과 조회
- ✅ Excel 보고서 생성
- ✅ 기존 BluePy와 동일한 기능

**성공 기준**:
- 기존 73개 규칙 100% 마이그레이션
- 테스트 커버리지 60% 이상
- GUI에서 스캔 실행 가능

---

#### Phase 2: macOS 확장 (1.5주)

**목표**: Unix 공통화 + macOS 지원

**주요 작업**:
- [ ] Day 1-2: UnixScanner 추상화
  - Linux/macOS 공통 로직 추출
  - LinuxScanner 리팩토링

- [ ] Day 3-5: macOS 규칙 작성
  - macOS 전용 10개 (SIP, FileVault 등)
  - Linux 재사용 40개

- [ ] Day 6-7: macOS 스캐너 구현
  - MacOSScanner 클래스
  - macOS 명령어 래퍼

- [ ] Day 8-10: 테스트 + 문서화
  - macOS 환경 테스트
  - 사용자 가이드

**결과물**:
- ✅ macOS 50개 규칙 점검 가능
- ✅ Linux + macOS 통합 GUI
- ✅ UnixScanner 공통 로직

**성공 기준**:
- macOS 50개 규칙 동작
- Linux 기능 유지 (회귀 없음)

---

#### Phase 3: 자동 수정 강화 (2주)

**목표**: 원클릭 자동 수정 + 백업/롤백

**주요 작업**:
- [ ] Week 7: Remediation 엔진
  - BaseRemediator 추상 클래스
  - LinuxRemediator 구현
  - MacOSRemediator 구현
  - 백업 매니저

- [ ] Week 8: 안전 장치 + GUI
  - 롤백 매니저
  - Dry-run 모드
  - 미리보기 UI
  - 배치 수정

**결과물**:
- ✅ 자동 수정 기능 (Linux + macOS)
- ✅ 백업/롤백 시스템
- ✅ GUI 미리보기

**성공 기준**:
- 자동 수정 성공률 90%+
- 롤백 성공률 100%
- 백업 무결성 보장

---

#### Phase 4: Windows 지원 (3주)

**목표**: Windows 플랫폼 추가

**주요 작업**:
- [ ] Week 9: WinRM 연결
  - PyWinRM 통합
  - 인증 매니저
  - PowerShell 래퍼

- [ ] Week 10: Windows 규칙 작성
  - CIS Benchmark 기반 50개
  - 레지스트리 점검
  - 서비스/방화벽 점검

- [ ] Week 11: Windows 스캐너 + 테스트
  - WindowsScanner 구현
  - 통합 테스트
  - GUI 업데이트

**결과물**:
- ✅ Windows 50개 규칙 점검
- ✅ 3-OS 통합 GUI
- ✅ WinRM 연결 안정화

**성공 기준**:
- Windows 환경에서 정상 동작
- 기존 Linux/macOS 기능 유지

---

#### Phase 5: 고급 기능 (2주)

**목표**: 이력 관리 + 트렌드 분석 + UX 개선

**주요 작업**:
- [ ] Week 12: 이력 관리
  - SQLite 스키마 설계
  - ORM 구현 (SQLAlchemy)
  - 이력 뷰어 UI
  - 비교 기능

- [ ] Week 13: 고급 기능 + 마무리
  - 대시보드 (그래프, 차트)
  - 트렌드 분석
  - PDF 보고서
  - 스케줄러
  - 교육 콘텐츠 추가
  - 다크 모드
  - 다국어 (한/영)

**결과물**:
- ✅ 이력 DB + 트렌드 분석
- ✅ 대시보드
- ✅ PDF 보고서
- ✅ 스케줄러

**성공 기준**:
- 과거 이력 조회 가능
- 트렌드 그래프 표시
- 완전한 배포 패키지

---

### 8.3 마일스톤

| 마일스톤 | 주차 | 설명 | 검증 |
|----------|------|------|------|
| **M1: Linux MVP** | Week 4 | Linux 기본 기능 완성 | 사용자 테스트 |
| **M2: macOS 추가** | Week 6 | Unix 통합 완료 | 베타 테스트 |
| **M3: 자동 수정** | Week 8 | 자동 수정 기능 | 안전성 검증 |
| **M4: Windows** | Week 11 | 3-OS 완성 | 통합 테스트 |
| **M5: 출시 준비** | Week 13 | 모든 기능 완성 | UAT |

---

## 9. 리스크 관리

### 9.1 기술적 리스크

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| **Python 2→3 마이그레이션 실패** | 중 | 높음 | 점진적 마이그레이션, 테스트 강화 |
| **macOS SIP 제약** | 높음 | 중 | 수정 불가 항목 명시, 사용자 안내 |
| **Windows 테스트 환경 부족** | 중 | 중 | GitHub Actions, VM 활용 |
| **자동 수정 시 시스템 손상** | 낮음 | 높음 | 백업 강제, Dry-run 기본 |
| **성능 문제 (대규모 서버)** | 중 | 중 | 비동기 처리, 캐싱 |

### 9.2 일정 리스크

| 리스크 | 확률 | 영향 | 대응 방안 |
|--------|------|------|----------|
| **규칙 작성 지연** | 중 | 중 | 우선순위 규칙만 먼저 |
| **GUI 개발 지연** | 중 | 낮음 | MVP는 간단한 UI로 |
| **Windows 기능 미완성** | 중 | 낮음 | Phase 5로 연기 가능 |

### 9.3 리스크 완화 전략

**개발 프로세스**:
- 매주 코드 리뷰
- 단위 테스트 의무화 (커버리지 60%+)
- 통합 테스트 자동화
- Git 브랜치 전략 (feature/develop/main)

**테스트 환경**:
- Linux: Docker, VM
- macOS: GitHub Actions (macos-latest)
- Windows: Azure Pipelines, VM

---

## 10. 성공 지표

### 10.1 개발 목표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **코드 커버리지** | 60% 이상 | pytest-cov |
| **규칙 수** | 170개 이상 | Linux(73) + macOS(50) + Windows(50) |
| **자동 수정 성공률** | 90% 이상 | 테스트 환경에서 검증 |
| **롤백 성공률** | 100% | 모든 수정 항목 검증 |
| **빌드 시간** | 5분 이내 | CI/CD 파이프라인 |

### 10.2 품질 목표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **버그 밀도** | 10개/1000 LOC 이하 | 정적 분석 |
| **린트 에러** | 0개 | ruff, mypy |
| **타입 커버리지** | 80% 이상 | mypy |
| **문서화 커버리지** | 90% 이상 | docstring 검사 |

### 10.3 사용자 목표 (MVP 이후)

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **사용자 만족도** | 4.5/5 이상 | 설문 조사 |
| **첫 스캔 성공률** | 95% 이상 | 사용자 추적 |
| **평균 학습 시간** | 30분 이내 | 온보딩 추적 |

---

## 11. 다음 단계

### 11.1 즉시 시작할 작업 (이번 주)

1. **Git 초기화 및 백업** (30분)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: 2017 legacy project backup"
   ```

2. **프로젝트 구조 생성** (1시간)
   ```bash
   # 새 폴더 구조 생성
   mkdir -p src/{core/{domain,scanner,analyzer,remediation},gui,infrastructure,utils}
   mkdir -p config/rules/{linux,macos,windows}
   mkdir -p data/{databases,reports}
   mkdir -p tests/{unit,integration}
   mkdir -p scripts docs

   # 기존 코드 이동
   mv infra legacy/
   ```

3. **PRD 생성** (2시간)
   - ai-dev-tasks/create-prd.md 사용
   - 기능 명세 상세화

4. **의존성 설치** (30분)
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 11.2 이번 주 목표

- [x] PROJECT_PLAN.md 작성 완료
- [ ] docs/ARCHITECTURE.md 작성
- [ ] docs/ROADMAP.md 작성
- [ ] Git 초기화
- [ ] 프로젝트 구조 생성
- [ ] PRD 생성

### 11.3 의사결정 필요 항목

**프로젝트 이름**:
- [ ] BluePy 2.0 (기존 이름 유지)
- [ ] EasyAudit (새 이름)
- [ ] 다른 이름 제안?

**배포 방식**:
- [ ] 단일 실행 파일 (.exe) - 추천
- [ ] pip install

**라이선스**:
- [ ] MIT (가장 자유로움)
- [ ] GPL v3 (오픈소스 강제)
- [ ] Apache 2.0 (특허 보호)

---

## 12. 참조 문서

### 12.1 프로젝트 문서

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 시스템 아키텍처 상세
- [ROADMAP.md](docs/ROADMAP.md) - 개발 로드맵 상세
- [LEGACY_ANALYSIS.md](docs/LEGACY_ANALYSIS.md) - 기존 시스템 분석
- [USER_MANUAL.md](docs/USER_MANUAL.md) - 사용자 매뉴얼 (예정)

### 12.2 외부 참조

**보안 기준**:
- [KISA 주요정보통신기반시설 취약점 분석평가 상세가이드](https://www.kisa.or.kr)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

**기술 문서**:
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [AsyncSSH Documentation](https://asyncssh.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-10-17 | 1.0 | 초안 작성 | Claude |

---

**문서 끝**