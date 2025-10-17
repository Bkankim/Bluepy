# Task List: Python 2→3 마이그레이션 자동화 시스템

**생성일**: 2025-10-17
**PRD**: `prd-python2-to-3-migration.md`
**기간**: 3일 (Day 3-5)

---

## 진행 상황 (2025-10-17 업데이트)

**중요**: 이 Task List는 초기 PRD 기준으로 작성되었습니다. 실제 구현 과정에서 일부 조정이 있었습니다.

**실제 완료 내용** (상세 내용은 `docs/ROADMAP.md` 참조):
- Task 1.0-2.0: 완료 (Legacy 분석, 도메인 모델, 마이그레이션 엔진)
- Task 3.0: 완료 (73개 YAML 규칙 파일 생성, 10개가 아닌 전체 73개 생성)
- Task 4.0: 완료 (73개 Validator 스켈레톤 생성, linux/ 디렉토리 구조로 변경)
- Task 5.0 (ROADMAP 버전): 완료 (10개 함수 시범 구현 - U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10, U-18, U-27)
- Task 5.0 (PRD 버전): 미완료 (테스트 자동화는 향후 진행 예정)
- Task 6.0: 진행 예정 (나머지 63개 함수 마이그레이션)

**Git Commits**:
- 634d85a: feat: Complete Task 5.0 - 10 functions implementation
- 6a1e166: feat: Complete Task 4.0 - Validator skeleton generation
- f624874: docs: Update documentation with Task 3.3 verification results

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

**총 36개 Sub-task | 예상 소요 시간: 3일 (Day 3-5)**