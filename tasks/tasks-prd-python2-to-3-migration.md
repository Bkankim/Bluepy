# Task List: Phase 1 - Linux MVP (Week 1-4)

**생성일**: 2025-10-17
**PRD**: `prd-python2-to-3-migration.md`
**기간**: 4주 (Week 1-4)
**상태**: Linux MVP 완성!

---

## 전체 진행 상황 (2025-10-20 업데이트)

### Phase 1 완료 요약
- **Week 1**: 73개 Validator 함수 마이그레이션 (100%)
- **Week 2**: Scanner/Analyzer 엔진 구현 (1,050 lines)
- **Week 3**: GUI + Database 구현 (1,490 lines)
- **Week 4**: Integration + Reporting (784 lines)
- **Phase 3 Week 9**: Linux Remediation 완성 (10개 규칙)
- **Phase 5 Week 1**: Quick Wins 완료 (다크 모드 + History View)
- **총 구현**: 3,324 lines + Remediation + Quick Wins (2,427 lines)
- **Linux MVP**: 완성!
- **자동 수정 기능**: 완성! (Linux 10개 + macOS 5개 = 총 15개 규칙)

### 완료된 작업
- Task 1.0-2.0: 완료 (Legacy 분석, 도메인 모델, 마이그레이션 엔진)
- Task 3.0: 완료 (73개 YAML 규칙 파일 생성)
- Task 4.0: 완료 (73개 Validator 스켈레톤 생성)
- **Week 1 Validator 구현**: 완료 (73/73 함수, 100%)
  * Phase 1: log_management.py (U-72, U-73) - 2개
  * Phase 2: patch_management.py (U-71) - 1개
  * Phase 3: account_management.py 나머지 (U-02, U-06, U-11~U-15) - 7개
  * Phase 4: file_management.py 나머지 (U-16, U-17, U-19~U-26, U-28~U-35) - 18개
  * Phase 5: service_management.py (U-36~U-70) - 35개
  * 완료 카테고리: account_management (15/15), file_management (20/20), service_management (35/35), patch_management (1/1), log_management (2/2)

**Git Commits (Week 1)**:
- 8a23c3d: feat: Complete Phase 5 Batch 3+4 - Implement 15 service_management functions (U-56~70)
- 1b6c59b: feat: Complete Phase 5 Batch 2 - Implement 10 service_management functions (U-46~55)
- 76075b6: feat: Complete Phase 5 Batch 1 - Implement 10 service_management functions (U-36~45)
- 4a098bf: feat: Complete Phase 4 - Implement 18 file_management functions (U-16~35)
- b90b9ca: feat: Complete Phase 3 - Implement 7 account_management functions (U-02, U-06, U-11~U-15)
- 19fc939: feat: Complete Phase 2 - Implement check_u71 (patch_management.py)
- 922555d: feat: Complete Phase 1 - Implement check_u72 and check_u73
- 634d85a: feat: Complete Task 5.0 - 10 functions implementation
- 6a1e166: feat: Complete Task 4.0 - Validator skeleton generation

### Week 2-4 구현 내용

**Week 2: Scanner/Analyzer 엔진 (commit a97b9f3)**
- base_scanner.py (210 lines) - BaseScanner 추상 클래스, ScanResult dataclass
- rule_loader.py (209 lines) - YAML 규칙 로딩, RuleMetadata 변환
- ssh_client.py (190 lines) - AsyncSSH 클라이언트 구현
- linux_scanner.py (234 lines) - Linux 스캐너 구현, Validator 호출
- risk_calculator.py (207 lines) - 리스크 통계 계산, RiskStatistics
- 총 1,050 lines

**Week 3: GUI + Database (commit 947261b)**
- main_window.py (188 lines) - QMainWindow 구조, 메뉴바, 탭
- server_view.py (188 lines) - 서버 목록 관리, QListWidget
- scan_view.py (253 lines) - 스캔 실행 UI, 진행률 표시
- result_view.py (277 lines) - 결과 트리뷰, 색상 코딩
- server_dialog.py (198 lines) - 서버 추가/편집 폼
- models.py (137 lines) - SQLAlchemy ORM (Server, ScanHistory)
- server_repository.py (178 lines) - CRUD 기능
- app.py (52 lines) - Entry point
- 총 1,490 lines

**Week 4: Integration + Reporting (commit b2cd6cc)**
- excel_reporter.py (242 lines) - Excel 보고서 (요약/상세/통계 3개 시트)
- scan_worker.py (186 lines) - QThread + asyncio 통합
- main_window.py 업데이트 (+168 lines) - Scanner 연동, Excel 저장
- 총 784 lines

**Git Commits (Week 2-4)**:
- b2cd6cc: feat: Implement Week 4 - Integration and Excel Reporting
- 947261b: feat: Implement Week 3 - GUI Basic Structure and Database
- a97b9f3: feat: Implement Week 2 - Core Scanner and Analyzer modules

**Git Commits (Phase 3 - Remediation)**:
- 38d104c: feat: Linux Remediation Tier 1 구현 (5개 규칙)
- ebaaa0f: feat: Linux Remediation Tier 2 구현 (5개 규칙)
- d24f898: docs: Linux Remediation 완성 문서화 (10개 규칙)

**Git Commits (Phase 5 - Quick Wins)**:
- ca08e0c: feat: 다크 모드 기능 구현 (ThemeManager, QSS, 총 1,883 insertions)
- 4ceb74c: feat: History View 구현 (HistoryRepository, HistoryView, PyQtGraph, 총 544 insertions)

---

## 미진한 부분 (중요!)

### Critical (즉시 필요)
**Task 5.0: 테스트 자동화 (0% 완료)**
- [ ] 5.1: test_migration.py 생성 - 마이그레이션 스크립트 테스트
- [ ] 5.2: test_yaml_rules.py 생성 - YAML 파일 검증
- [ ] 5.3: test_validators.py 완성 - 73개 Validator 함수 테스트
- [ ] 5.4: test_domain_models.py 생성 - 도메인 모델 테스트
- [ ] 5.5: pytest 설정 및 fixture - conftest.py
- [ ] 5.6: 커버리지 측정 - 목표 60%+ (현재 0%)

**리스크**: 테스트 없이 코드가 3,324 lines 작성됨. 버그 발견 및 수정 비용 증가, 리팩토링 불가, 회귀 버그 위험

### Important (곧 필요)
**Task 6.0: 문서화 및 검증 (50% 완료)**
- [ ] 6.1-6.2: MIGRATION_REPORT.md 자동 생성 - 통계, 함수 목록
- [ ] 6.4: 코드 품질 검사 (black/ruff/mypy) - 포맷팅, 린팅, 타입 체킹
- [ ] 6.5: 최종 통합 테스트 - 전체 워크플로우 검증
- [x] 6.3: README.md 업데이트 - 완료
- [x] 6.6: Git 커밋 및 문서 정리 - 완료 (commit 27d87f1)

**리스크**: 코드 품질 미검증, 잠재적 버그 존재 가능성

### Nice to Have (선택사항)
- [ ] 사용자 매뉴얼 작성 (docs/USER_MANUAL.md)
- [ ] PyInstaller 빌드 스크립트 (scripts/build.py)
- [ ] 배포 패키지 생성 (.exe, .app, .deb)
- [ ] 실제 서버 테스트 (Docker 환경)

---

## Relevant Files

### 생성할 파일
- `scripts/migrate_legacy.py` - 메인 마이그레이션 스크립트 (Python 2→3 변환, YAML 생성, Validator 생성)
- `src/core/domain/models.py` - CheckResult, RuleMetadata 등 도메인 모델 정의
- `src/core/analyzer/validators/__init__.py` - Validators 패키지 초기화
- `src/core/analyzer/validators/linux.py` - Linux 10개 validator 함수 스켈레톤
- `config/rules/linux/U-01.yaml` ~ `U-10.yaml` - 10개 YAML 규칙 파일
- `tests/unit/test_migration.py` - 마이그레이션 테스트
- `tests/unit/test_validators.py` - Validator 함수 테스트
- `tests/unit/test_yaml_rules.py` - YAML 규칙 검증 테스트
- `docs/MIGRATION_REPORT.md` - 마이그레이션 결과 보고서 (자동 생성)
- `docs/LEGACY_ANALYSIS_DETAIL.md` - Legacy 코드 상세 분석 (73개 함수, 복잡도, 패턴, 10개 선정)
- `docs/DOMAIN_MODEL_DESIGN.md` - 도메인 모델 설계 (Status, Severity, CheckResult, RuleMetadata, RemediationInfo)

### 참조할 파일
- `legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py` - 73개 Legacy 점검 함수 (Python 2)

### Notes
- Python 3.12 가상환경에서 작업 (`source venv/bin/activate`)
- 모든 코드는 UTF-8 인코딩 사용
- pytest로 테스트 실행: `pytest tests/unit/`
- 커버리지 확인: `pytest --cov=src --cov-report=html`

---

## Tasks

- [x] 1.0 Legacy 코드 분석 및 도메인 모델 정의
  - [x] 1.1 Legacy 코드 전체 읽기 및 구조 파악 (`Linux_Check_2.py` 전체 분석, 73개 함수 목록 작성, 헬퍼 함수 파악)
  - [x] 1.2 10개 함수 선정 및 문서화 (복잡도 평가, KISA 코드 매핑, 선정 근거 문서화)
  - [x] 1.3 도메인 모델 설계 (CheckResult, RuleMetadata, Severity/Status Enum 설계)
  - [x] 1.4 `src/core/domain/models.py` 구현 (데이터클래스, type hints, pydantic 검증)
  - [x] 1.5 YAML 스키마 설계 (필수/선택 필드 확정, 예시 YAML 작성)
  - [x] 1.6 마이그레이션 전략 문서 작성 (변환 순서, 자동화 범위, 검증 방법)

- [x] 2.0 마이그레이션 스크립트 핵심 엔진 개발 (Python 2→3 변환 + 함수 추출)
  - [x] 2.1 스크립트 기본 구조 생성 (`scripts/migrate_legacy.py`, argparse CLI, logging 설정)
  - [x] 2.2 인코딩 변환 함수 구현 (BOM-UTF8 읽기, cp949→UTF-8 변환, 에러 로깅)
  - [x] 2.3 Python 2→3 구문 변환 함수 구현 (정규식 기반, print/except/unicode 변환)
  - [x] 2.4 AST 기반 함수 추출 구현 (`ast.parse()`, `_XSCRIPT` 패턴 매칭, 소스 코드 추출)
  - [x] 2.5 FunctionInfo 데이터 구조 정의 (name, kisa_code, source_code, commands, complexity 필드)
  - [x] 2.6 통합 테스트 (73개 함수 추출 확인, Python 3 실행 가능 검증)

- [x] 3.0 YAML 규칙 생성 시스템 구현
  - [x] 3.1 bash 명령어 추출 로직 구현 (AST에서 os.popen/subprocess 찾기, `_SPLIT()` 패턴 인식)
  - [x] 3.2 YAML 템플릿 생성 함수 구현 (KISA 코드 매핑, name/category/severity 자동 추론)
  - [x] 3.3 YAML 파일 저장 (pyyaml, UTF-8 인코딩, `config/rules/linux/U-{번호:02d}.yaml` 형식)
  - [x] 3.4 YAML 검증 함수 구현 (필수 필드 체크, validator 함수명 형식 검증)
  - [x] 3.5 10개 YAML 파일 생성 (선정된 10개 함수에 대해 생성 및 검증) - 실제로는 73개 모두 생성
  - [x] 3.6 YAML 규칙 매뉴얼 작성 (`docs/YAML_RULES_GUIDE.md`, 필드 설명, 예시, 추가 방법)

- [x] 4.0 Validator 함수 생성 시스템 구현
  - [x] 4.1 validator 함수 템플릿 설계 (함수 시그니처, docstring 구조, TODO 주석)
  - [x] 4.2 함수명 자동 생성 로직 (KISA 코드→snake_case 변환, `check_u{번호:02d}_{이름}` 형식)
  - [x] 4.3 Legacy 로직 주석 삽입 (주요 로직을 주석으로 변환, 구현 힌트 제공)
  - [x] 4.4 `src/core/analyzer/validators/linux.py` 생성 (모듈 docstring, CheckResult import, 10개 함수, `__all__`) - 실제로는 linux/ 디렉토리 생성 후 category별 분리
  - [x] 4.5 `src/core/analyzer/validators/__init__.py` 생성 (linux 모듈 import, 향후 macos/windows 대비)
  - [x] 4.6 validator 함수 테스트 스켈레톤 생성 (`tests/unit/test_validators.py`, 존재/반환타입 테스트)

- [ ] 5.0 테스트 자동화 구현
  - [ ] 5.1 `tests/unit/test_migration.py` 생성 (마이그레이션 스크립트 기능 테스트, Python 2→3 변환, 함수 추출, 인코딩)
  - [ ] 5.2 `tests/unit/test_yaml_rules.py` 생성 (YAML 파일 존재 확인, 형식 검증, 필수 필드, validator 매칭)
  - [ ] 5.3 `tests/unit/test_validators.py` 완성 (10개 함수 존재, 시그니처 검증, 기본 호출, CheckResult 반환)
  - [ ] 5.4 `tests/unit/test_domain_models.py` 생성 (CheckResult/RuleMetadata 테스트, Enum 테스트, pydantic 검증)
  - [ ] 5.5 pytest 설정 및 fixture 작성 (`tests/conftest.py`, Legacy 코드/YAML 데이터 fixture, 임시 파일 fixture)
  - [ ] 5.6 커버리지 측정 및 리포트 (`pytest --cov=src --cov-report=html`, 60% 이상 확인, 추가 테스트)

- [ ] 6.0 문서화 및 최종 검증
  - [ ] 6.1 마이그레이션 보고서 생성 함수 구현 (`generate_report()`, 통계, 함수 목록, KISA 매핑, 경고/에러)
  - [ ] 6.2 `docs/MIGRATION_REPORT.md` 자동 생성 (Markdown 테이블, 각 함수 상세 정보, 다음 단계)
  - [ ] 6.3 README.md 업데이트 (마이그레이션 스크립트 사용법, 명령어 예시, 옵션 설명, 문제 해결)
  - [ ] 6.4 코드 품질 검사 (black 포맷팅, ruff 린팅, mypy 타입 체킹, 모든 경고/에러 해결)
  - [ ] 6.5 최종 통합 테스트 (전체 워크플로우 실행, 10개 YAML/validator 생성 확인, 모든 테스트 통과, 보고서 생성)
  - [ ] 6.6 Git 커밋 및 문서 정리 (변경사항 커밋, ROADMAP.md 업데이트, Week 2 준비)

---

## 다음 단계 옵션

Linux MVP가 완성되었습니다! 다음으로 진행할 수 있는 옵션:

### 옵션 1: 테스트 코드 작성 (권장)
**기간**: 2-3일
**내용**:
- Task 5.0 완료 (단위 테스트, 통합 테스트)
- Task 6.0 완료 (코드 품질 검사, MIGRATION_REPORT.md)
- 커버리지 60% 달성

**장점**:
- 버그 조기 발견 및 수정
- 안전한 리팩토링 가능
- 향후 Phase에서 회귀 버그 방지

**단점**:
- 추가 시간 소요
- 기능 개발 지연

### 옵션 2: macOS 지원 추가 (Phase 2)
**기간**: 1.5주
**내용**:
- UnixScanner 추상화
- macOS 전용 규칙 10개 + Linux 재사용 40개
- MacOSScanner 구현
- GUI에서 플랫폼 선택

**장점**:
- 멀티플랫폼 지원 확대
- Unix 공통 로직 재사용

### 옵션 3: Windows 지원 추가 (Phase 4)
**기간**: 3주
**내용**:
- WinRM 연결 모듈
- Windows 규칙 50개 (CIS Benchmark)
- WindowsScanner 구현
- 3-OS 통합

**장점**:
- 완전한 3-OS 지원
- 차별화 포인트

### 옵션 4: 고급 기능 강화 (Phase 3 또는 5)
**기간**: 2주
**내용**:
- Remediation 엔진 (자동 수정)
- 백업/롤백 시스템
- 이력 관리 및 트렌드 분석
- 대시보드 (그래프, 차트)

**장점**:
- 핵심 차별화 기능
- 사용자 편의성 향상

### 권장 순서
1. **옵션 1 (테스트)** - 안정성 확보
2. **옵션 2 (macOS)** 또는 **옵션 4 (고급 기능)** - 기능 확장
3. **옵션 3 (Windows)** - 완전성

---

**총 36개 Sub-task | Week 1-4 완료: 3,324 lines | 다음: 테스트 또는 Phase 2**