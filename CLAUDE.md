# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# agents 사용 지침
- **반드시** 병렬 수행에 유리한 작업을 스스로 판단하고 적절한 agents를 배정해서 사용.

# 철칙
- **반드시** 이모티콘 사용 금지 (📋 ❌ ✅ 🔴 📂 등)

# AI Dev Tasks
Use these files when I request structured feature development using PRDs:
/ai-dev-tasks/create-prd.md
/ai-dev-tasks/generate-tasks.md
/ai-dev-tasks/process-task-list.md

# agents 사용 지침
- **반드시** 병렬 수행에 유리한 작업을 스스로 판단하고 적절한 agents를 배정해서 사용.

## AI Dev Tasks 사용법
1. **PRD 생성**: `Use @create-prd.md` + 기능 설명
   - 결과: `tasks/prd-[feature-name].md`
2. **Task List 생성**: `@prd-[feature-name].md와 @generate-tasks.md 사용`
   - 결과: `tasks/tasks-prd-[feature-name].md`
3. **구현 진행**: `@process-task-list.md 사용`
   - Task 단위로 단계별 구현 및 검증

## BluePy 2.0 프로젝트

### 프로젝트 개요
멀티플랫폼(Linux, macOS, Windows) 인프라 보안 점검 및 자동 수정 도구.
2017년 Legacy 시스템을 Python 3.12, Clean Architecture로 재구성.

**참고 문서:**
- `PROJECT_PLAN.md` - 전체 프로젝트 계획 및 로드맵
- `docs/ARCHITECTURE.md` - Clean Architecture 설계
- `docs/ROADMAP.md` - Phase별 상세 개발 일정
- `docs/LEGACY_ANALYSIS.md` - 2017년 시스템 분석

### 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 테스트 실행
```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/unit

# 통합 테스트만
pytest tests/integration

# 커버리지 리포트 (목표 60%+)
pytest --cov=src --cov-report=html
# 결과: htmlcov/index.html

# 특정 테스트만 실행
pytest tests/unit/test_scanner.py::test_connect
```

### GUI 실행
```bash
# GUI 애플리케이션 실행
python -m src.gui.app

# 테마 데모 실행
python examples/theme_demo.py

# CLI 모드 (고급 사용자)
python -m src.cli.commands scan --server myserver.com
```

### 프로젝트 아키텍처

**Clean Architecture (Hexagonal) 레이어:**
- `src/core/domain/` - 도메인 모델 (Entity, Value Object)
- `src/core/scanner/` - 스캔 엔진 (Linux/macOS/Windows Scanner)
- `src/core/analyzer/` - 분석 엔진 (결과 파싱, 평가)
- `src/core/remediation/` - 자동 수정 엔진 (백업, 실행, 롤백)
- `src/application/` - 유스케이스 (비즈니스 로직 조율)
- `src/infrastructure/` - 외부 어댑터 (DB, Network, Reporting)
- `src/gui/` - PySide6 GUI (Presentation Layer)
  * `theme_manager.py` - 테마 관리자 (다크/라이트 모드)
  * `resources/styles/` - QSS 스타일시트 (dark.qss, light.qss)

**핵심 패턴:**
- Factory Pattern: Scanner 생성 (플랫폼별 분기)
- Repository Pattern: DB 접근 추상화
- YAML 기반 규칙 시스템: 확장 가능한 점검 항목

**규칙 파일 구조:**
```yaml
# config/rules/linux/U-01.yaml
id: U-01
name: root 원격 로그인 제한
severity: high
check:
  commands:
    - cat /etc/pam.d/login | grep pam_securetty
validator: validators.linux.check_pam_securetty
remediation:
  auto: true
  backup_files:
    - /etc/pam.d/login
  commands:
    - echo "auth required pam_securetty.so" >> /etc/pam.d/login
```

### Legacy 코드 참고
- `legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py` - 73개 점검 함수 (`_1SCRIPT` ~ `_73SCRIPT`)
- Python 2 코드이므로 직접 실행 불가, 로직만 참고

### 스크립트

#### scripts/migrate_legacy.py (완성)
Legacy Python 2 코드를 Python 3로 마이그레이션하고 YAML 규칙 파일 생성

**주요 기능**:
- Legacy Python 2 코드 파싱 및 변환
- FunctionInfo 데이터 구조 추출 (73개 함수)
- bash 명령어 추출 및 분석
- YAML 템플릿 자동 생성 (KISA 규칙 73개)
- UTF-8 인코딩으로 파일 저장

**사용 방법**:
```bash
# 전체 마이그레이션 (73개 파일 생성)
python3.12 scripts/migrate_legacy.py \
  --input "legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py" \
  --output-dir config/rules/linux/ \
  --all

# 특정 함수만 마이그레이션
python3.12 scripts/migrate_legacy.py \
  --input "legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py" \
  --output-dir config/rules/linux/ \
  --functions _1SCRIPT _4SCRIPT _18SCRIPT

# Dry-run 모드 (파일 생성 안함)
python3.12 scripts/migrate_legacy.py \
  --input "..." \
  --output-dir config/rules/linux/ \
  --all --dry-run
```

**완료 상태** (2025-10-18 업데이트):
- **Week 1 완료**: 73개 Validator 함수 마이그레이션 (100%)
  * Task 1.0-4.0 완료: 73개 YAML 파일 생성, Validator 스켈레톤 생성
  * Task 5.0 완료: 10개 함수 시범 마이그레이션 (U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10, U-18, U-27)
  * Task 6.0 완료: 나머지 63개 함수 마이그레이션 (73/73 완료)
  * 완료 카테고리: account_management (15/15), file_management (20/20), service_management (35/35), log_management (2/2), patch_management (1/1)

- **Week 2 완료**: Scanner/Analyzer 엔진 (1,050 lines, commit a97b9f3)
  * base_scanner.py (210 lines) - BaseScanner, ScanResult
  * rule_loader.py (209 lines) - YAML 규칙 로딩
  * ssh_client.py (190 lines) - AsyncSSH 클라이언트
  * linux_scanner.py (234 lines) - Linux 스캐너 구현
  * risk_calculator.py (207 lines) - 리스크 통계 계산

- **Week 3 완료**: GUI + Database (1,490 lines, commit 947261b)
  * main_window.py (188 lines) - QMainWindow 구조
  * server_view.py (188 lines) - 서버 목록 관리
  * scan_view.py (253 lines) - 스캔 실행 UI
  * result_view.py (277 lines) - 결과 트리뷰
  * server_dialog.py (198 lines) - 서버 추가/편집
  * models.py (137 lines) - SQLAlchemy ORM
  * server_repository.py (178 lines) - CRUD 기능
  * app.py (52 lines) - Entry point

- **Week 4 완료**: Integration + Reporting (784 lines, commit b2cd6cc)
  * excel_reporter.py (242 lines) - Excel 보고서 (3 sheets)
  * scan_worker.py (186 lines) - QThread + asyncio
  * main_window.py 통합 업데이트 (+168 lines) - Scanner 연동

- **Linux MVP 완성!** (총 3,324 lines)

- **Phase 1.5 완료**: Testing Infrastructure (커버리지 65%, commits 01f4833, bd217ca, 6210cd7)
  * Day 1-2: pytest 설정, 기본 unit 테스트 (36%)
  * Day 3: 통합 테스트 + 커버리지 향상 (65%, +102개 테스트)
  * 테스트 272개 (251 passed, 20 failed, 1 skipped)
  * Black 코드 포매팅 (32 files reformatted)

- **Phase 2 완료**: macOS 확장 (commits 4b8e0bf, 8ae7670, f21d18b)
  * Day 1-2: UnixScanner 추상화 + macOS 규칙 10개 (15 files, +634/-181)
  * Day 3-5: macOS validator 10개 + Linux 규칙 40개 공유 (48 files, +782/-8)
  * macOS 50개 규칙 지원 (전용 10 + 공유 40)
  * LinuxScanner 리팩토링 (227줄 → 65줄)

- **Phase 3 Week 7 완료**: Remediation 엔진 (commits 0614cb3, 758f76d)
  * RemediationResult 모델 추가
  * BackupManager 클래스 (백업/롤백, SHA256 체크섬, ~150줄)
  * BaseRemediator 추상 클래스 (dry-run 지원, ~150줄)
  * MacOSRemediator 구현 (5개 auto: true 규칙, ~50줄)
  * 총 ~400줄 추가

- **Phase 3 Week 8 완료**: GUI 통합 (commit 78bb83d)
  * RemediationWorker 클래스 (QThread + asyncio, 244줄)
  * RemediationDialog 대화상자 (Dry-run 미리보기 + 실행, 364줄)
  * ResultView 자동 수정 버튼 추가 (+79줄)
  * MainWindow 시그널 연결 및 통합 (+49줄)
  * 2단계 워크플로우 (Dry-run → 확인 → 실행)
  * 총 ~700줄 추가 (신규 2개, 수정 4개)

- **Phase 1 기술 부채 완전 해결** (commit c7080a1)
  * GUI 한글 폰트 문제 해결 (commit 1a65b7a) - Noto Sans CJK 폰트 설치 및 설정
  * 테스트 271 passed, 1 skipped (10개 실패 → 0개 실패)
  * 커버리지 56% (15% → 56%, +41% 향상)
  * RuleLoader 경로 중복 문제 해결 (config/rules/linux/linux)
  * Integration 테스트 API 불일치 수정 (ScanResult wrapper, 한글→영어)
  * Unit 테스트 헬퍼 함수 추가 및 API 표준화

- **테스트 인프라 강화** (commits eaf7a7d, 6a14415)
  * Remediation 엔진 단위 테스트 완성 (commit eaf7a7d)
    - test_backup_manager.py (278줄, 13개 테스트) - 100% 커버리지
    - test_base_remediator.py (336줄, 10개 테스트) - 98% 커버리지
    - test_macos_remediator.py (206줄, 9개 테스트) - 100% 커버리지
    - 테스트 303개 (271 → 303, +32개)
    - Remediation 모듈 완전 테스트 완료

  * 핵심 모듈 테스트 확장 (commit 6a14415)
    - test_database_models.py (8개 테스트, 신규) - Server/ScanHistory 모델, DB 헬퍼 100% 커버리지
    - test_server_repository.py (22개 테스트, 신규) - CRUD 전체 100% 커버리지
    - test_analyzer.py 확장 (+1개) - rules_metadata 분기 테스트
    - test_scanner.py 확장 (+1개) - scan_all 성공 경로 테스트
    - test_rule_loader.py 확장 (+4개) - 예외 처리 테스트
    - 테스트 340개 (303 → 340, +37개)
    - 커버리지 63% (56% → 61% → 63%)

  * 100% 커버리지 달성 모듈
    - risk_calculator.py (94% → 100%)
    - database/models.py (80% → 100%)
    - server_repository.py (31% → 100%)
    - backup_manager.py (100%)
    - macos_remediator.py (100%)
    - domain/models.py (100%)
    - excel_reporter.py (100%)

  * 90%+ 커버리지 달성 모듈
    - base_scanner.py (85% → 92%)
    - base_remediator.py (98%)
    - file_management.py (91%)
    - service_management.py (93%)

- **Linux Remediation 구현** (commits 38d104c, ebaaa0f, d24f898)
  * Tier 1: 단순 chmod 명령어 (commit 38d104c)
    - LinuxRemediator 클래스 구현 (61줄, 100% 커버리지)
    - U-18: /etc/passwd 권한 600
    - U-19: /etc/shadow 권한 400
    - U-22: /etc/syslog.conf 권한 644
    - U-23: /etc/services 권한 644
    - U-39: cron 파일 권한 640
    - 테스트 10개 추가
    - 중요 버그 수정: 4개 YAML check.commands 수정

  * Tier 2: PAM/sed 파일 수정 (commit ebaaa0f)
    - U-01: root 원격 접속 제한 (PAM + sed)
    - U-03: 계정 잠금 임계값 (PAM 2줄)
    - U-06: root su 제한 (PAM)
    - U-21: /etc/inetd.conf 권한 600
    - U-38: r계열 서비스 비활성화 (sed 3줄)
    - 테스트 5개 추가
    - 전체 테스트 354개 (340 → 355, +15개)
    - 커버리지 63% 유지

  * Linux Remediation 완성 (10개 규칙, commit d24f898)
    - chmod 명령어: 6개
    - PAM 설정: 3개
    - sed 파일 수정: 1개
    - Idempotent 설계 (grep -q || echo 패턴)

- **GUI 테마 시스템 구축** (2025-10-20)
  * PySide6 QSS 기반 다크/라이트 모드 지원
  * ThemeManager 클래스 (168줄, 싱글톤 패턴)
    - QPalette + QSS 조합 (Best Practice)
    - 테마 전환 API (set_theme, toggle_theme)
  * QSS 스타일시트 (총 913줄)
    - dark.qss (455줄) - VSCode Dark+ 기반
    - light.qss (458줄) - VSCode Light+ 기반
    - 42개 위젯 스타일링 (버튼, 입력, 테이블, 탭 등)
  * 색상 팔레트 (WCAG AA 준수)
    - 명도 대비 11.0:1 (다크), 13.6:1 (라이트)
    - 강조색 4종 (Accent, Success, Warning, Error)
  * 문서화
    - docs/THEME_USAGE.md - 사용 가이드
    - resources/styles/README.md - QSS 참조 문서
    - examples/theme_demo.py - 데모 애플리케이션

- **History View 구현** (2025-10-20)
  * HistoryRepository 클래스 (226줄)
    - create() - 스캔 이력 추가
    - get_history_by_server() - 서버별 이력 조회
    - get_trend_data() - 트렌드 데이터 (30일)
    - get_latest_scan(), delete_old_scans()
  * HistoryView 클래스 (305줄)
    - QSplitter (좌우 분할 레이아웃)
    - 왼쪽: QTableWidget (6개 컬럼 - 날짜/시간, 점수, 통과, 실패, 수동, 전체)
    - 오른쪽: PyQtGraph PlotWidget (점수 트렌드 차트)
    - 점수 색상 코딩 (녹색/주황/빨강)
    - Signal/Slot 패턴 (history_selected)
  * MainWindow 통합
    - "이력" 탭 추가 (3번째 탭)
    - DB 세션 연동
    - 서버 선택 시 자동 로드
  * PyQtGraph 의존성
    - requirements.txt에 pyqtgraph>=0.13 추가
    - MIT 라이센스, 고성능 차트 (75-150배 빠름)

#### scripts/import_rules.py (개발 예정)
- YAML 규칙 검증/가져오기

#### scripts/build.py (개발 예정)
- PyInstaller 빌드 자동화

#### scripts/setup_dev.sh (개발 예정)
- 개발 환경 자동 설정

### 코드 품질 도구
```bash
# 코드 포맷팅 (black)
black src/ tests/
black --check src/  # 포맷 검증만

# 린팅 (ruff)
ruff check src/ tests/
ruff check --fix src/  # 자동 수정

# 타입 체킹 (mypy)
mypy src/
mypy --strict src/core/  # 엄격 모드

# 전체 품질 체크
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest
```

### 빌드 및 패키징
```bash
# PyInstaller로 실행 파일 빌드 (개발 예정)
python scripts/build.py

# 플랫폼별 빌드
python scripts/build.py --platform linux
python scripts/build.py --platform macos
python scripts/build.py --platform windows

# 결과물
# - dist/bluepy (Linux/macOS)
# - dist/bluepy.exe (Windows)
```

### 데이터베이스 마이그레이션 (개발 예정)
```bash
# Alembic을 사용한 DB 마이그레이션
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
alembic downgrade -1
```

## 프로젝트 필수 지침

### .md 수정 지침
- 작업을 마칠 때마다, **우선적으로 모든 문서 최신화**를 고려해야 함.

### git 규칙
- 모든 작업을 마칠 때마다, @.gitignore 를 최신화하고, 항상 해당 github를 최신화 해야함 (백업 개념에서)
- 모든 git 내용에 너(Claude)의 흔적이 존재하면 안됨.

### MCP 사용 기준
- sequential-thinking : 깊은 사고력이 요구되는 작업이나, 복잡한 과정을 수행할 때 본인 판단하에 자유롭게 사용.
- context7 : 의존성 문제나, 새로운 패키지의 다운로드가 필요할 시 반드시 사용해서 해결.

### 프롬프트 언어
- 항상 한글로 대답하고, 생각하는 부분도 한글로 표기할 것.

### 코드 작성 지침
- 모든 Class, def 위에는 간단하게 기능을 설명하는 주석을 달아줄 것.
- **모듈 사용을 기본**으로 하여 호환성 / 재사용성 / 유지보수성 의 원칙을 꼭 지킬 것.