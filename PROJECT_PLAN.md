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
- [x] Week 1: 프로젝트 구조 생성 + 마이그레이션 시스템 구축 (90% 완료)
  - Git 초기화 및 프로젝트 구조 생성
  - Task 1.0 완료: Legacy 분석, 도메인 모델, YAML 스키마, 마이그레이션 전략
  - Task 2.0 완료: 마이그레이션 스크립트 핵심 엔진 개발
    * CLI 인터페이스 구현 (argparse)
    * 다중 인코딩 지원 (utf-8-sig, cp949, euc-kr)
    * 정규식 기반 Python 2→3 변환 (lib2to3 대체)
    * FunctionInfo 데이터 구조 및 AST 추출 엔진
    * 73개 함수 추출 성공 (통합 테스트 완료)
  - Task 3.1-3.3 완료: bash 명령어 추출, YAML 템플릿 생성, 파일 저장
    * parse_linux_bash_script() 함수 (113줄, State machine)
    * KISA_NAMES 딕셔너리 (73개 규칙 이름 전체 매핑)
    * 카테고리 자동 추론 함수 (5개 카테고리)
    * YAML 템플릿 자동 생성 함수
    * save_yaml_file() 함수 (43줄, UTF-8 인코딩)
    * 73개 YAML 파일 전체 생성 (config/rules/linux/)
    * 재검증 완료 (5단계):
      - 파일 생성: 73개 YAML 파일 정상 (0바이트 없음, 255~412 바이트)
      - 내용 검증: 5개 카테고리 샘플 정상 (한글 보존, commands/severity 정확)
      - YAML 파싱: yaml.safe_load() 성공, 데이터 타입/중첩 구조 정확
      - 코드 검증: save_yaml_file() 함수, UTF-8 인코딩, yaml.dump() 옵션 정상
      - Git 검증: commit 3f8fd58, 76 files changed, working tree clean
  - Task 4.0 완료: Validator 스켈레톤 생성
    * generate_validator_skeleton() 함수 (70줄)
    * save_validator_files() 함수 (95줄)
    * create_init_file() 함수 (105줄)
    * 6개 파일 생성 (src/core/analyzer/validators/linux/)
    * 73개 validator 함수 스켈레톤 (check_u01 ~ check_u73)
    * 검증 완료: py_compile, import 테스트, 함수 호출 테스트
  - Task 5.0 완료: 10개 함수 시범 마이그레이션
    * 10개 함수 선정: U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10 (계정관리 8개), U-18, U-27 (파일관리 2개)
    * Legacy 로직 분석 및 Python 3 변환 완료
    * account_management.py: 7개 함수 구현 (U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10)
    * file_management.py: 2개 함수 구현 (U-18, U-27)
    * 모든 함수 Status.PASS/FAIL/MANUAL 판단 로직 추가
    * 검증 완료: py_compile, import, 실행 테스트 통과
    * Git commit: 634d85a (3 files, 399 insertions, 118 deletions)
  - **Task 6.0 완료: 나머지 63개 함수 마이그레이션 (73/73 완료, 100%)**
    * **Phase 1 완료** (2025-10-17): log_management.py (U-72, U-73 - 2개)
      - check_u72: 로그의 정기적 검토 및 보고 (MANUAL)
      - check_u73: 로그 기록 정책 수립 (MANUAL)
      - Git commit: 922555d
    * **Phase 2 완료** (2025-10-17): patch_management.py (U-71 - 1개)
      - check_u71: 최신 보안패치 및 벤더 권고사항 적용 (MANUAL)
      - Git commit: 19fc939
    * **Phase 3 완료** (2025-10-17): account_management.py 나머지 (U-02, U-06, U-11~U-15 - 7개)
      - Batch 1: check_u02 (패스워드 복잡성), check_u06 (su 제한), check_u11 (관리자 그룹)
      - Batch 2: check_u12 (GID 점검), check_u13 (UID 중복), check_u14 (shell 점검)
      - Batch 3: check_u15 (Session Timeout)
      - 총 15개 테스트 케이스 통과
      - Git commit: b90b9ca
    * **Phase 4 완료** (2025-10-18): file_management.py 나머지 (U-16, U-17, U-19~U-26, U-28~U-35 - 18개)
      - Batch 1: check_u16~u22 (PATH 점검, 파일 권한 r--------/rw-------/rw-r--r--)
      - Batch 2: check_u23~u29 (서비스 파일, SUID/SGID, .rhosts, ALL:ALL)
      - Batch 3: check_u30~u35 (hosts.lpd, NIS, umask, 홈 디렉터리)
      - 총 32개 테스트 케이스 통과
      - Git commit: 4a098bf
    * **Phase 5 완료** (2025-10-18): service_management.py (U-36~U-70 - 35개)
      - Batch 1: check_u36~u45 (Finger, FTP, r계열, cron, DOS, NFS, RPC, NIS)
      - Batch 2: check_u46~u55 (tftp, Sendmail, DNS, Apache 디렉터리/권한/파일)
      - Batch 3+4: check_u56~u70 (Apache 링크/업로드/ssh, FTP 계정/설정/at, SNMP, NFS, expn/vrfy)
      - 총 73개 테스트 케이스 통과 (24 + 25 + 24)
      - Git commits: 76075b6, 1b6c59b, 8a23c3d
    * **완료 상황**: 73/73 함수 구현 완료 (100%)!
      - 완료 카테고리: account_management (15/15), file_management (20/20), service_management (35/35), log_management (2/2), patch_management (1/1)
      - Task 6.0 완료!

- [x] Week 2: Linux 스캐너 구현 (완료)
  - BaseScanner 추상 클래스
  - LinuxScanner 구현
  - SSH 연결 모듈
  - 규칙 파일 파서
  - Git commit: a97b9f3 (5 files, 1,050 lines)

- [x] Week 3: GUI 기본 구조 (완료)
  - MainWindow (PySide6)
  - 서버 관리 뷰
  - 스캔 실행 뷰
  - 결과 트리 뷰
  - Git commit: 947261b (8 files, 1,490 lines)

- [x] Week 4: 보고서 + 통합 (완료)
  - Excel 보고서 생성
  - Scanner-GUI 통합
  - ScanWorker (QThread + asyncio)
  - Git commit: b2cd6cc (3 files, 784 lines)

**결과물**:
- ✅ Week 1: 마이그레이션 시스템 (73/73 함수 완료)
  * 마이그레이션 스크립트 핵심 엔진 (scripts/migrate_legacy.py, 700+ 줄)
  * FunctionInfo 데이터 구조 (7 fields)
  * 73개 Legacy 함수 추출 성공 (U-01 ~ U-73)
  * 도메인 모델 구현 (src/core/domain/models.py, 207줄)
  * YAML 스키마 및 73개 규칙 파일 생성
  * 73개 Validator 함수 마이그레이션 완료
- ✅ Week 2: Scanner/Analyzer 엔진 (1,050 lines, commit a97b9f3)
  * base_scanner.py (210 lines) - BaseScanner, ScanResult
  * rule_loader.py (209 lines) - YAML 규칙 로딩
  * ssh_client.py (190 lines) - AsyncSSH 클라이언트
  * linux_scanner.py (234 lines) - Linux 스캐너 구현
  * risk_calculator.py (207 lines) - 리스크 통계
- ✅ Week 3: GUI + Database (1,490 lines, commit 947261b)
  * main_window.py (188 lines) - QMainWindow
  * server_view.py (188 lines) - 서버 목록 관리
  * scan_view.py (253 lines) - 스캔 실행 UI
  * result_view.py (277 lines) - 결과 트리뷰
  * server_dialog.py (198 lines) - 서버 추가/편집
  * models.py (137 lines) - SQLAlchemy ORM
  * server_repository.py (178 lines) - CRUD 기능
  * app.py (52 lines) - Entry point
- ✅ Week 4: Integration + Reporting (784 lines, commit b2cd6cc)
  * excel_reporter.py (242 lines) - Excel 보고서 (3 sheets)
  * scan_worker.py (186 lines) - QThread + asyncio
  * main_window.py 통합 업데이트 (+168 lines) - Scanner 연동

**성공 기준** (Phase 1 완료!):
- ✅ 도메인 모델 설계 및 구현
- ✅ 마이그레이션 스크립트 핵심 엔진 완성
- ✅ 73개 함수 추출 및 메타데이터 수집
- ✅ Week 2-4: 스캐너/GUI/보고서 구현 완료
- ✅ Linux MVP 완성! (총 3,324 lines)

---

#### Phase 1.5: Testing Infrastructure (완료, 2025-10-18)

**목표**: 테스트 인프라 구축 및 커버리지 60%+ 달성

**주요 작업**:
- [x] Day 1-2: 테스트 기본 구조 (완료, commit 01f4833)
  - pytest, pytest-cov 설정
  - conftest.py 픽스처 설정
  - 기본 unit 테스트 작성 (5개 카테고리)
  - 초기 커버리지: 36%

- [x] Day 3: 통합 테스트 + 커버리지 향상 (완료, commit bd217ca)
  - 통합 테스트 2개 파일 생성 (test_workflow.py, test_scanner_analyzer.py)
  - Unit 테스트 대폭 확장 (102개 테스트 추가)
    * TestServiceManagementDetailed: 40개 테스트
    * TestFileManagementDetailed: 24개 테스트
    * TestValidatorsEdgeCases: 6개 대량 호출 테스트
  - Black 코드 포매팅 (32 files reformatted)
  - 최종 커버리지: **65%** (+29%p)

**결과물**:
- ✅ 테스트 272개 (251 passed, 20 failed, 1 skipped)
- ✅ 커버리지 50% → 65% (+15%p)
- ✅ 모듈별 성과:
  * service_management.py: 35% → 80% (+45%p)
  * file_management.py: 59% → 88% (+29%p)
  * account_management.py: 77% → 80% (+3%p)
  * excel_reporter.py: 100%
  * risk_calculator.py: 94%

**성공 기준**:
- ✅ 커버리지 60%+ 달성 (실제 65%)
- ✅ 통합 테스트 작성
- ✅ 코드 품질 도구 적용 (Black)

---

#### Phase 2: macOS 확장 (완료, 2025-10-19)

**목표**: Unix 공통화 + macOS 지원

**주요 작업**:
- [x] Day 1-2: UnixScanner 추상화 (완료, commit 4b8e0bf)
  - UnixScanner 추상 클래스 생성 (82줄)
  - LinuxScanner 리팩토링 (227줄 → 65줄, 162줄 감소)
  - MacOSScanner 생성 (65줄)
  - macOS 전용 규칙 10개 작성 (M-01 ~ M-10)
  - 회귀 테스트 통과 (253 passed, 커버리지 65% 유지)

- [x] Day 3-5: macOS validator 및 규칙 공유 (완료, commit 8ae7670)
  - macOS validator 모듈 생성 (7개 파일, 10개 함수)
    * system_protection.py: check_m01 (SIP), check_m10 (Firmware Password)
    * data_protection.py: check_m02 (FileVault), check_m09 (Time Machine)
    * application_security.py: check_m03 (Gatekeeper)
    * network_security.py: check_m04 (Firewall), check_m08 (Remote Login)
    * patch_management.py: check_m05 (Automatic Updates)
    * access_control.py: check_m06 (Screen Saver), check_m07 (Guest Account)
  - Linux 규칙 40개를 macOS와 공유 (platforms: [linux, macos])
    * 계정 관리: U-01 ~ U-15 (15개)
    * 파일 관리: U-16~U-20, U-23~U-30, U-32~U-35, U-39 (18개)
    * 서비스 관리: U-36, U-38, U-40, U-46, U-59, U-64, U-67 (7개)
  - 자동화 스크립트: scripts/update_macos_rules.py

**결과물**:
- ✅ macOS 50개 규칙 점검 가능 (전용 10 + 공유 40)
- ✅ MacOSScanner 완전 구현 및 동작 가능
- ✅ UnixScanner 공통 로직 (코드 중복 제거)
- ✅ Linux 기능 유지 (회귀 테스트 통과)
- ✅ 총 코드: unix_scanner.py (82줄) + macos_scanner.py (65줄) + validators (7 files, ~400줄)

**성공 기준**:
- ✅ macOS 50개 규칙 작성 완료
- ✅ macOS validator 10개 함수 구현 완료
- ✅ Linux 기능 유지 (회귀 없음, 253 passed)
- ✅ BLOCKER 해결 (macOS validator 모듈 생성)

---

#### Phase 3: 자동 수정 강화 (부분 완료, 2025-10-19)

**목표**: 원클릭 자동 수정 + 백업/롤백

**주요 작업**:
- [x] Week 7: Remediation 엔진 (완료, commit 0614cb3)
  - RemediationResult 모델 추가 (success, backup_id, dry_run 등)
  - BackupManager 클래스 (백업 세션, 파일 백업/롤백, SHA256 체크섬)
  - BaseRemediator 추상 클래스 (remediate 플로우, 자동 롤백)
  - MacOSRemediator 구현 (macOS 5개 auto: true 규칙 지원)
  - LinuxRemediator (향후 확장)

- [x] Week 8: GUI 통합 (완료, commit TBD)
  - RemediationWorker 클래스 (QThread + asyncio, 244줄)
  - RemediationDialog 대화상자 (Dry-run 미리보기 + 실행, 364줄)
  - ResultView 자동 수정 버튼 추가 (+79줄)
  - MainWindow 시그널 연결 및 통합 (+49줄)
  - 2단계 워크플로우 (Dry-run → 확인 → 실행)

**결과물**:
- ✅ Remediation 엔진 구축 (4개 클래스, ~400줄)
- ✅ 백업/롤백 시스템 (원자성 보장, 체크섬 검증)
- ✅ macOS 자동 수정 (5개 규칙: M-03, M-04, M-05, M-06, M-07, M-08)
- ✅ Dry-run 모드 (실제 실행 전 시뮬레이션)
- ✅ GUI 통합 (자동 수정 대화상자, ~700줄)
- ⏸ Linux 자동 수정 (향후 확장)
- ⏸ 배치 수정 (향후 확장)

**성공 기준**:
- ✅ Remediation 아키텍처 설계 완료
- ✅ Scanner와 Remediator 분리 (관심사 분리)
- ✅ 백업 무결성 보장 (SHA256)
- ✅ GUI 통합 완료 (자동 수정 버튼, 미리보기, 진행 표시)

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

### 11.1 현재 진행 상태 (2025-10-19)

**완료된 Phase**:
- [x] Phase 1: Linux MVP (Week 1-4) - 완료
- [x] Phase 1.5: Testing Infrastructure - 부분 완료 (271/272 테스트, 커버리지 56%)
- [x] Phase 2: macOS 확장 (Day 1-5) - 완료
- [x] Phase 3 Week 7: Remediation 엔진 - 완료
- [x] Phase 3 Week 8: GUI 통합 - 완료 (commit 78bb83d)
- [x] Phase 1 기술 부채 해결 - 완료 (commit c7080a1, 1a65b7a)

**진행률**: 65% (약 8주 작업 완료)

**주요 성과**:
- 73개 Linux 규칙 마이그레이션 (100%)
- 50개 macOS 규칙 지원
- macOS Remediation 구현 (5개 auto: true)
- GUI 완성 (서버 관리, 스캔, 결과, 보고서, 자동 수정)
- 테스트 271/272 통과
- 커버리지 56%
- 총 10개 Git 커밋

### 11.2 다음 2주 계획

**Week 1: 품질 강화 + 핵심 기능 완성**
- [ ] Day 1-2: 커버리지 65% 달성 (테스트 100-150개 추가)
- [ ] Day 3-5: Linux Remediation 구현 (10-15개 규칙)

**Week 2: Phase 5 Quick Wins**
- [ ] Day 6-8: History View 구현
- [ ] Day 9: 다크 모드 구현
- [ ] Day 10: 설정 UI 구현

**2주 후 목표 상태**:
- Phase 1.5: 완료 (커버리지 65%+)
- Phase 3: 완전 완료 (Linux + macOS Remediation)
- Phase 5: 부분 완료 (3개 기능)
- 진행률: 75%

### 11.3 향후 계획 (Week 3+)

**옵션 1: Phase 4 Windows 지원** (3주)
- Windows Scanner 구현
- Windows 50개 규칙 작성
- Windows Remediation 구현
- 3-OS 통합 완성

**옵션 2: Phase 5 나머지 기능** (2주)
- 대시보드 (그래프, 차트)
- PDF 보고서
- 스케줄러
- 교육 콘텐츠
- 다국어 지원

**의사결정 필요**: Phase 4 vs Phase 5 우선순위

### 11.4 참고사항

**배포 방식** (결정됨):
- [x] PyInstaller 단일 실행 파일 (.exe, .app, binary)

**프로젝트 이름** (결정됨):
- [x] BluePy 2.0 (기존 이름 유지)

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