# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# ===== 전역 필수 규칙 (GLOBAL MANDATORY RULES) =====

```yaml
global_rules:
  agent_utilization:
    mandate: "반드시 모든 작업에서 적절한 에이전트를 최대한 활용하여 효율을 극대화해야 함"
    priority: "CRITICAL"
    enforcement: "이 규칙 위반 시 작업 재수행 필요"

    core_principles:
      - principle: "에이전트 우선 원칙"
        rule: "직접 실행 가능한 작업도 에이전트 활용 가능 시 에이전트 사용"

      - principle: "병렬 실행 강제"
        rule: "독립적인 작업 2개 이상 시 무조건 병렬 에이전트 실행"

      - principle: "전문성 활용"
        rule: "전문 에이전트가 존재하면 반드시 해당 에이전트 사용"

      - principle: "작업 분할"
        rule: "큰 작업은 여러 독립적 하위 작업으로 분할 후 병렬 실행"

    available_agents:
      - name: "general-purpose"
        priority: "HIGH"
        use_for:
          - "복잡한 다단계 작업"
          - "코드 구현 (여러 파일)"
          - "심층 리서치"
          - "문서 작성"

      - name: "Explore"
        priority: "HIGH"
        thoroughness_levels: ["quick", "medium", "very thorough"]
        use_for:
          - "코드베이스 탐색 (파일 패턴 검색)"
          - "키워드 검색 (Grep)"
          - "구조 분석"
          - "API 엔드포인트 찾기"
        when_to_use: "파일 위치나 코드 패턴을 모를 때 필수"

      - name: "code-analyzer"
        priority: "HIGH"
        use_for:
          - "최근 코드 변경 분석"
          - "버그 추적"
          - "로직 흐름 추적 (다중 파일)"
          - "잠재적 이슈 발견"
        when_to_use: "코드 변경 후 검증, 버그 조사 시 필수"

      - name: "file-analyzer"
        priority: "MEDIUM"
        use_for:
          - "로그 파일 분석 및 요약"
          - "대용량 파일 처리"
          - "핵심 정보 추출"
        when_to_use: "로그/대용량 파일 분석 시 필수"

      - name: "test-runner"
        priority: "HIGH"
        use_for:
          - "테스트 실행 및 분석"
          - "실패 패턴 파악"
          - "커버리지 분석"
          - "테스트 건강도 리포트"
        when_to_use: "코드 변경 후 검증, 테스트 디버깅 시 필수"

      - name: "parallel-worker"
        priority: "CRITICAL"
        use_for:
          - "Git worktree 병렬 작업"
          - "다중 워크스트림 조율"
          - "대규모 이슈 병렬 처리"
        when_to_use: "여러 독립적 작업 스트림 동시 실행 시 필수"

    execution_patterns:
      parallel:
        trigger: "독립적인 작업 2개 이상"
        mandatory: true
        examples:
          - scenario: "여러 파일 조사"
            tasks: ["파일 A 조사", "파일 B 조사", "파일 C 조사"]
            agents: ["Explore", "Explore", "Explore"]

          - scenario: "여러 규칙 구현"
            tasks: ["W-11~W-15 구현", "W-16~W-20 구현"]
            agents: ["general-purpose", "general-purpose"]

          - scenario: "조사 + 구현 병렬"
            tasks: ["레지스트리 조사", "YAML 작성", "문서 업데이트"]
            agents: ["Explore", "general-purpose", "general-purpose"]

        action: "반드시 단일 메시지에서 모든 Task 도구 호출"

      sequential:
        trigger: "의존성이 있는 작업"
        examples:
          - scenario: "설계 기반 구현"
            steps: ["설계 완료", "설계 결과로 구현", "구현 결과로 테스트"]

          - scenario: "조사 결과 활용"
            steps: ["CIS Benchmark 조사", "조사 결과로 규칙 선정", "선정된 규칙 구현"]

        action: "이전 에이전트 결과를 다음 에이전트 프롬프트에 포함"

    decision_tree:
      question_1: "이 작업을 독립적인 하위 작업으로 분할 가능한가?"
      yes_1:
        action: "분할 후 각 하위 작업마다 에이전트 배정"
        next: "question_2"
      no_1:
        next: "question_3"

      question_2: "하위 작업들이 서로 독립적인가? (의존성 없음)"
      yes_2:
        action: "병렬 에이전트 실행 (단일 메시지에서 모든 Task 호출)"
        result: "PARALLEL EXECUTION"
      no_2:
        action: "순차 에이전트 실행 (결과 전달)"
        result: "SEQUENTIAL EXECUTION"

      question_3: "전문 에이전트가 이 작업에 적합한가?"
      yes_3:
        action: "해당 전문 에이전트 사용"
        result: "SPECIALIZED AGENT"
      no_3:
        action: "general-purpose 에이전트 사용"
        result: "GENERAL AGENT"

    anti_patterns:
      forbidden:
        - action: "에이전트 사용 가능한데 직접 실행"
          reason: "효율성 저하, 컨텍스트 낭비"

        - action: "병렬 가능한 작업을 순차 실행"
          reason: "시간 낭비"

        - action: "Explore 에이전트 없이 직접 Grep/Glob"
          reason: "여러 번 시도 시 컨텍스트 낭비"

        - action: "코드 변경 후 code-analyzer 생략"
          reason: "잠재적 버그 미발견"

        - action: "테스트 실행 시 test-runner 생략"
          reason: "실패 원인 분석 부족"

    enforcement_checklist:
      before_every_task:
        - "[ ] 이 작업을 여러 독립적 하위 작업으로 분할 가능한가?"
        - "[ ] 각 하위 작업에 적합한 전문 에이전트가 있는가?"
        - "[ ] 하위 작업들을 병렬로 실행할 수 있는가?"
        - "[ ] 에이전트 활용 시 직접 실행보다 효율적인가?"

      if_yes_to_any:
        action: "반드시 에이전트 사용"
        format: "단일 메시지에서 모든 Task 도구 병렬 호출"
```

---

# 철칙
- **반드시** 이모티콘 사용 금지 (📋 ❌ ✅ 🔴 📂 등)

# AI Dev Tasks
Use these files when I request structured feature development using PRDs:
/ai-dev-tasks/create-prd.md
/ai-dev-tasks/generate-tasks.md
/ai-dev-tasks/process-task-list.md

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

- **Settings UI 구현** (2025-10-20)
  * Settings 모듈 (193줄)
    - JSON 기반 설정 저장/로드 (config/settings.json)
    - 기본값 관리 (테마, 로그 레벨, 언어, 백업 디렉토리)
    - 점 표기법 키 접근 (get_setting, set_setting)
    - 중첩 딕셔너리 병합 (_deep_update)
    - UTF-8 인코딩 (한글 지원)
  * SettingsDialog 클래스 (234줄)
    - 4개 그룹박스 (외관, 로깅, 언어, 백업)
    - 테마 선택 (Dark/Light)
    - 로그 레벨 선택 (DEBUG/INFO/WARNING/ERROR)
    - 언어 선택 (한국어/English, 현재 비활성화)
    - 백업 디렉토리 경로 설정 (찾아보기 버튼)
    - 유효성 검사 및 에러 처리
  * MainWindow 통합
    - "설정" 메뉴 추가 (Ctrl+,)
    - 설정 변경 시 즉시 적용 (테마 자동 전환)
    - 상태바 메시지 표시
  * 테스트 완료
    - 단위 테스트 26개 (test_settings.py, 302줄)
    - GUI 테스트 13개 (test_settings_dialog.py, 217줄)
    - 총 39개 테스트 모두 통과
    - 커버리지: settings.py 93%, settings_dialog.py 100%
  * 문서화
    - docs/SETTINGS_UI_IMPLEMENTATION.md (완전한 구현 가이드)

- **Phase 4 Windows 지원** (2025-10-20, commit 3735972)
  * WinRMClient 클래스 (310줄)
    - pywinrm 기반 비동기 Windows 원격 관리
    - execute_powershell() - PowerShell 스크립트 실행
    - get_registry_value() - Windows 레지스트리 조회
    - check_service() - Windows 서비스 상태 확인
    - 에러 처리 3종: WinRMConnectionError, WinRMCommandError, WinRMTimeoutError
    - asyncio 래핑 (run_in_executor 사용)
    - Context Manager 지원
  * WindowsScanner 클래스 (247줄)
    - BaseScanner 상속, UnixScanner 패턴 유지
    - WinRMClient 통합
    - Validator 동적 import 및 호출
    - 에러 발생 시 MANUAL 상태 반환
  * Windows 규칙 10개 (YAML 283줄 + Validator 343줄)
    - 계정 관리 7개: W-01~W-07 (Administrator 이름, Guest, 패스워드 정책)
    - 서비스 관리 3개: W-08~W-10 (Firewall, Defender, 원격 데스크톱 NLA)
    - CIS Benchmark 기반 선정
    - 모든 Validator 함수 완전 구현 (PASS/FAIL 판단 로직)
  * 테스트 스켈레톤 (194줄)
    - tests/unit/test_winrm_client.py
    - 27개 테스트 메서드 (TODO 마커)
  * 코드 품질
    - Black 포맷팅 완료 (2개 파일)
    - Ruff 린팅 통과 (0개 에러)
    - Python 구문 검증 100%

- **Phase 4 Week 2 Day 1 완료**: 레지스트리 규칙 10개 (commit 1bcef01)
  * W-11~W-20 구현 (YAML 10개 + Validator 10개)
  * registry.py 파일 생성 (304줄)
  * 총 601줄 신규 코드
  * 에이전트 활용: Explore + 2개 병렬 general-purpose + code-analyzer
  * 버그 1개 발견 및 수정 (category 일관성)
  * 코드 품질: Black, Ruff, py_compile 모두 PASS

- **Phase 4 Week 2 Day 2 완료**: 레지스트리 규칙 10개 (commit dff93ae)
  * W-21~W-30 구현 (YAML 10개 + Validator 10개)
  * registry.py 확장 (+313줄, 총 606줄)
  * 총 603줄 신규 코드
  * 에이전트 활용: sequential-thinking + Explore + 2개 병렬 + code-analyzer (5개)
  * 버그 0개 (완전 PASS)
  * 코드 품질: Black, Ruff, py_compile 모두 PASS
  * Windows 규칙 30/50 완성 (60%)

- **Phase 4 Week 2 Day 3 완료**: 서비스 관리 규칙 10개
  * W-31~W-40 구현 (YAML 10개 + Validator 10개)
  * service_management.py 확장 (+252줄, 총 331줄)
  * 총 654줄 신규 코드 (YAML 323줄 + Validator 331줄)
  * 에이전트 활용: sequential-thinking + Explore + 2개 병렬 general-purpose + code-analyzer (5개)
  * 버그 1개 발견 및 수정 (__init__.py export 누락)
  * 코드 품질: Black, Ruff, py_compile 모두 PASS
  * Import 테스트: 10개 validator 모두 성공
  * Windows 규칙 40/50 완성 (80%)

- **Phase 4 Week 2 Day 4 완료**: 패치/로깅 규칙 10개 (Windows 50/50 완성!)
  * W-41~W-50 구현 (YAML 10개 + Validator 10개)
  * patch_management.py 신규 생성 (195줄, check_w41~w45)
  * logging_auditing.py 신규 생성 (177줄, check_w46~w50)
  * 총 700줄 신규 코드 (YAML 328줄 + Validator 372줄)
  * 에이전트 활용: sequential-thinking + Explore + 4개 병렬 general-purpose + code-analyzer (6개)
  * 버그 1개 발견 및 수정 (W-43 로직 버그 - PASS 조건 수정)
  * 코드 품질: Black, Ruff, py_compile 모두 PASS
  * Import 테스트: 10개 validator 모두 성공
  * Windows 규칙 50/50 완성 (100%)!

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

---

## YAML 구조화된 작업 템플릿

아래 YAML 템플릿을 참고하여 일관된 방식으로 작업을 진행합니다.

### Phase 작업 템플릿

```yaml
phase:
  name: "Phase 4 Windows 지원"
  id: "phase-4"
  duration: "3주"
  status: "진행 중"  # 준비 중 / 진행 중 / 완료
  progress: 30%

  objectives:
    - "WinRM 연결 시스템 구현"
    - "Windows 50개 규칙 작성"
    - "WindowsRemediator 구현"
    - "3-OS 통합 완성"

  deliverables:
    - type: "코드"
      files:
        - "src/infrastructure/network/winrm_client.py"
        - "src/core/scanner/windows_scanner.py"
        - "src/core/remediation/windows_remediator.py"
      lines: 1500
    - type: "규칙"
      count: 50
      files: "config/rules/windows/*.yaml"
    - type: "테스트"
      count: 100
      files: "tests/unit/test_winrm*.py"
    - type: "문서"
      files:
        - "docs/WINDOWS_SETUP.md"
        - "PROJECT_PLAN.md"

  success_criteria:
    - name: "Windows 50개 규칙 동작"
      status: "partial"  # pass / fail / partial / pending
      progress: 20%  # 10/50
    - name: "코드 품질 검증"
      checks:
        - "Black 포맷팅 통과"
        - "Ruff 린팅 0개 에러"
        - "Python 구문 검증 100%"
    - name: "테스트 커버리지"
      target: "60%"
      current: "61%"
```

### 코드 작성 체크리스트

```yaml
code_checklist:
  before_writing:
    - "[ ] 기존 코드 패턴 확인 (BaseScanner, UnixScanner 등)"
    - "[ ] 필요한 import 문 확인"
    - "[ ] 타입 힌트 정의 (from typing import List, Optional)"
    - "[ ] 에러 처리 전략 수립"

  during_writing:
    - "[ ] 모든 클래스/함수에 docstring 추가"
    - "[ ] Type hints 완전 작성"
    - "[ ] 에러 처리 구현 (try-except, 로깅)"
    - "[ ] 일관된 네이밍 (snake_case 함수, PascalCase 클래스)"

  after_writing:
    - "[ ] Black 포맷팅 실행"
    - "[ ] Ruff 린팅 실행 및 수정"
    - "[ ] Python 구문 검증 (py_compile)"
    - "[ ] Import 테스트"
    - "[ ] 단위 테스트 작성"
```

### 테스트 작성 체크리스트

```yaml
test_checklist:
  unit_tests:
    - "[ ] 정상 동작 테스트 (happy path)"
    - "[ ] 에러 케이스 테스트 (edge cases)"
    - "[ ] 빈 입력 테스트 (empty input)"
    - "[ ] None 입력 테스트"
    - "[ ] Mock 사용 (외부 의존성 제거)"

  integration_tests:
    - "[ ] 실제 데이터 흐름 테스트"
    - "[ ] Scanner → Analyzer → Result 전체 플로우"
    - "[ ] 에러 발생 시 복구 테스트"

  coverage_goals:
    target: "60%"
    priorities:
      - "Core 모듈: 80%+"
      - "GUI 모듈: 30%+"
      - "Infrastructure: 60%+"
```

### 문서화 체크리스트

```yaml
documentation_checklist:
  code_level:
    - "[ ] 모든 public 클래스에 docstring"
    - "[ ] 모든 public 함수에 docstring"
    - "[ ] 복잡한 로직에 inline 주석"
    - "[ ] Type hints 완전 작성"

  project_level:
    - "[ ] PROJECT_PLAN.md 업데이트"
    - "[ ] ROADMAP.md 업데이트"
    - "[ ] CLAUDE.md 업데이트 (완료 작업 반영)"
    - "[ ] README.md 업데이트 (주요 기능 변경 시)"

  phase_completion:
    - "[ ] Phase별 완료 문서 작성"
    - "[ ] 구현 가이드 문서 (필요 시)"
    - "[ ] 사용자 매뉴얼 업데이트 (GUI 변경 시)"
```

### Git 커밋 템플릿

```yaml
commit_template:
  format: |
    feat/fix/docs: [간결한 제목] (50자 이내)

    [상세 설명]
    - 신규 파일: X개, Y줄
    - 수정 파일: Z개
    - 주요 변경사항 나열

    [테스트]
    - 테스트 N개 통과
    - 커버리지 X%

    [Phase 진행률]
    - Phase X: Y% → Z%

    Generated with Claude Code (https://claude.com/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>

  types:
    feat: "새로운 기능 추가"
    fix: "버그 수정"
    docs: "문서 수정"
    test: "테스트 추가/수정"
    refactor: "코드 리팩토링"
    style: "코드 포맷팅"

  examples:
    - "feat: Phase 4 Week 1 - Windows 지원 기본 구조 완성"
    - "docs: 전체 문서 최신화 (Phase 5 Quick Wins 반영)"
    - "test: Remediation 엔진 단위 테스트 완성"
```

### 에이전트 사용 템플릿

```yaml
agent_usage:
  parallel_execution:
    when:
      - "독립적인 조사 작업 (WinRM 조사, CIS Benchmark 분석)"
      - "독립적인 구현 작업 (여러 Validator 함수)"
      - "독립적인 테스트 작업"

    example: |
      Task 1: WinRM 연결 방법 조사 (Explore agent)
      Task 2: Windows CIS Benchmark 분석 (Explore agent)
      Task 3: WinRMClient 클래스 구현 (general-purpose agent)
      → 3개 에이전트 병렬 실행

  sequential_execution:
    when:
      - "의존성이 있는 작업 (설계 → 구현 → 테스트)"
      - "이전 결과가 필요한 작업"

    example: |
      Step 1: 설계 완료
      Step 2: 구현 시작 (Step 1 결과 필요)
      Step 3: 테스트 (Step 2 결과 필요)
```

---

위 YAML 템플릿을 참고하여 일관된 방식으로 작업을 진행하면, Claude가 더 명확하게 이해하고 효율적으로 작동합니다.