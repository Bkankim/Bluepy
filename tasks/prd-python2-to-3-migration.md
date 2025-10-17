# PRD: Python 2→3 마이그레이션 자동화 시스템

**작성일**: 2025-10-17
**대상 기간**: Phase 1, Week 1, Day 3-5 (3일)
**상태**: Draft

---

## 1. Introduction/Overview

2017년에 작성된 Linux 보안 점검 Legacy 시스템(Python 2)을 Python 3.12 기반의 현대적인 시스템으로 마이그레이션하기 위한 자동화 도구를 개발합니다.

**문제:**
- Legacy 시스템은 Python 2(EOL 2020)로 작성되어 보안 업데이트 불가
- 73개 점검 함수가 하드코딩되어 확장성 제로
- cp949/utf-8 인코딩 혼재로 한글 깨짐 문제

**해결책:**
- Python 2→3 자동 변환 스크립트 개발
- 73개 함수 중 10개를 시범으로 YAML 규칙 시스템으로 분리
- 나머지 63개는 Week 4에 동일한 스크립트로 자동 처리

**범위:**
- Legacy 파일: `legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py`
- 목표: 10개 함수(`_1SCRIPT` ~ `_10SCRIPT`) 마이그레이션
- 기간: 3일 (Day 3-5)

---

## 2. Goals

1. **자동화 스크립트 완성**: `scripts/migrate_legacy.py`를 개발하여 Python 2 코드를 Python 3로 자동 변환
2. **YAML 규칙 시스템 구축**: 10개 점검 항목을 `config/rules/linux/U-01.yaml` ~ `U-10.yaml`로 변환
3. **Validator 함수 생성**: 10개 validator 함수 스켈레톤을 `src/core/analyzer/validators/linux.py`에 자동 생성
4. **재사용 가능한 패턴 확립**: 나머지 63개 함수에 적용 가능한 범용 스크립트 완성

---

## 3. User Stories

### US-1: 개발자로서 Legacy 코드를 자동 변환하고 싶다
**As a** 개발자
**I want to** Legacy Python 2 코드를 Python 3로 자동 변환하는 스크립트를 실행
**So that** 수동 변환 시간을 절약하고 실수를 방지할 수 있다

**Acceptance Criteria:**
- `python scripts/migrate_legacy.py --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py --output src/core/legacy_migrated.py --count 10` 실행
- 10개 함수가 Python 3 구문으로 변환됨
- print문 → print(), except: → except Exception: 등 자동 처리

### US-2: 개발자로서 YAML 규칙을 자동 생성하고 싶다
**As a** 개발자
**I want to** Legacy 함수에서 bash 명령어와 검증 로직을 추출하여 YAML로 생성
**So that** YAML 규칙 시스템을 빠르게 구축할 수 있다

**Acceptance Criteria:**
- `config/rules/linux/U-01.yaml` ~ `U-10.yaml` 파일 자동 생성
- 각 YAML은 id, name, commands, validator 필드 포함
- KISA 기준 코드(U-01 ~ U-73) 자동 매핑

### US-3: 개발자로서 validator 함수 스켈레톤을 생성하고 싶다
**As a** 개발자
**I want to** 각 점검 항목에 대한 validator 함수 템플릿이 자동 생성
**So that** 나중에 실제 검증 로직만 채워 넣으면 된다

**Acceptance Criteria:**
- `src/core/analyzer/validators/linux.py`에 10개 함수 생성
- 각 함수는 docstring, type hint, TODO 주석 포함
- CheckResult 객체 반환 구조

### US-4: 개발자로서 변환 결과를 검증하고 싶다
**As a** 개발자
**I want to** 변환된 코드가 원본과 동일하게 동작하는지 테스트
**So that** 마이그레이션의 정확성을 보장할 수 있다

**Acceptance Criteria:**
- `tests/unit/test_migration.py`에 10개 함수 테스트 작성
- Legacy 결과와 100% 일치 확인
- 테스트 커버리지 60% 이상

---

## 4. Functional Requirements

### FR-1: Python 2→3 구문 변환
스크립트는 다음 변환을 자동으로 수행해야 함:
- FR-1.1: `print "text"` → `print("text")`
- FR-1.2: `except:` → `except Exception:`
- FR-1.3: `unicode()` → `str()`
- FR-1.4: `.decode('cp949')` → `.decode('utf-8')`
- FR-1.5: `#!/usr/bin/python` → `#!/usr/bin/python3.12`

### FR-2: 함수 추출
- FR-2.1: 정규식 또는 AST로 `_1SCRIPT` ~ `_10SCRIPT` 함수 추출
- FR-2.2: 각 함수의 bash 명령어 부분과 검증 로직 부분 분리
- FR-2.3: 함수명에서 KISA 코드 자동 추출 (예: `_1SCRIPT` → `U-01`)

### FR-3: YAML 규칙 생성
각 함수마다 다음 구조의 YAML 생성:
```yaml
id: U-01
name: root 계정 원격 로그인 제한
category: 계정관리
severity: high
kisa_standard: U-01
description: |
  설명 자동 생성 또는 TODO
check:
  commands:
    - cat /etc/pam.d/login
    - cat /etc/securetty
  validator: validators.linux.check_u01_root_remote_login
expected_result: |
  기대 결과 (주석에서 추출 또는 TODO)
remediation:
  auto: false  # Phase 3에서 구현
  manual_steps:
    - 수동 수정 방법 (추후 추가)
```

- FR-3.1: YAML 파일은 `config/rules/linux/U-{번호:02d}.yaml` 형식으로 저장
- FR-3.2: commands 필드는 함수에서 `os.popen()` 또는 `subprocess` 호출 부분 추출
- FR-3.3: validator 필드는 자동 생성된 함수명 매핑

### FR-4: Validator 함수 스켈레톤 생성
`src/core/analyzer/validators/linux.py`에 다음 형식으로 함수 생성:
```python
def check_u01_root_remote_login(command_outputs: Dict[str, str]) -> CheckResult:
    """
    U-01: root 계정 원격 로그인 제한 검증

    Legacy 함수: _1SCRIPT

    Args:
        command_outputs: 명령어 실행 결과 딕셔너리
            키: 명령어 문자열
            값: 실행 결과 (stdout)

    Returns:
        CheckResult: PASS/FAIL/MANUAL 상태와 메시지
    """
    # TODO: Legacy 함수의 검증 로직을 Python 3로 변환하여 구현
    # Legacy 코드 참조: legacy/infra/linux/.../Linux_Check_2.py::_1SCRIPT

    return CheckResult(
        status="MANUAL",
        message="검증 로직 미구현 - Week 2에 구현 예정"
    )
```

- FR-4.1: 각 함수는 type hint 포함
- FR-4.2: docstring에 Legacy 함수명 참조 포함
- FR-4.3: TODO 주석으로 구현 필요 부분 명시

### FR-5: 인코딩 변환
- FR-5.1: 모든 소스 파일을 UTF-8로 저장
- FR-5.2: cp949로 인코딩된 한글 주석/문자열을 UTF-8로 변환
- FR-5.3: 변환 로그에 인코딩 변경 사항 기록

### FR-6: 마이그레이션 보고서 생성
`docs/MIGRATION_REPORT.md`에 다음 내용 자동 생성:
- FR-6.1: 변환된 함수 목록 (10개)
- FR-6.2: 각 함수의 KISA 코드 매핑
- FR-6.3: 생성된 YAML 파일 경로
- FR-6.4: 생성된 validator 함수명
- FR-6.5: 변환 중 발생한 경고/에러 목록

### FR-7: 테스트 자동 생성
`tests/unit/test_migration.py`에 다음 테스트 생성:
- FR-7.1: 각 validator 함수가 존재하는지 테스트
- FR-7.2: YAML 파일이 올바른 형식인지 검증
- FR-7.3: (선택) Legacy 결과와 비교 테스트

### FR-8: 스크립트 재사용성
- FR-8.1: `--count` 옵션으로 변환할 함수 개수 지정 (기본값: 10)
- FR-8.2: Week 4에 `--count 73`으로 실행 시 나머지 63개도 자동 변환 가능
- FR-8.3: 로깅 기능 (`--verbose` 옵션)

---

## 5. Non-Goals (Out of Scope)

이 PRD의 범위에 포함되지 않으며, 향후 별도로 진행할 항목:

### NG-1: Scanner 엔진 구현
- **범위**: YAML 규칙을 읽고 SSH로 원격 서버에 명령어를 실행하는 엔진
- **예정**: Phase 1, Week 2 (Day 6-8), 별도 PRD 작성
- **이유**: 마이그레이션이 먼저 완료되어야 Scanner가 사용할 YAML이 생성됨

### NG-2: Analyzer 엔진 구현
- **범위**: validator 함수를 실제로 호출하고 결과를 집계하는 엔진
- **예정**: Phase 1, Week 2 (Day 9-10), 별도 PRD 작성
- **이유**: 이번 PRD에서는 validator 스켈레톤만 생성, 실제 로직은 Week 2에 구현

### NG-3: GUI 구현
- **범위**: PySide6 메인 윈도우, 서버 관리, 스캔 실행, 결과 표시
- **예정**: Phase 1, Week 3 (Day 11-15), 별도 PRD 작성
- **이유**: 백엔드 로직(Scanner/Analyzer)이 먼저 완성되어야 GUI 연결 가능

### NG-4: 나머지 63개 함수 마이그레이션
- **범위**: `_11SCRIPT` ~ `_73SCRIPT` 변환
- **예정**: Phase 1, Week 4 (Day 18-19), 같은 스크립트 재사용
- **이유**: 10개 시범 마이그레이션이 성공하면 동일한 패턴 적용

### NG-5: 보고서 생성 시스템
- **범위**: Excel 보고서 생성 (Linux_Check_3.py 참고)
- **예정**: Phase 1, Week 4 (Day 16-17), 별도 PRD 작성
- **이유**: 스캔 결과가 있어야 보고서 생성 가능

### NG-6: macOS/Windows 플랫폼 지원
- **범위**: 다른 플랫폼 점검 규칙 및 스캐너
- **예정**: Phase 2 (macOS, Week 5-6), Phase 4 (Windows, Week 9-11)
- **이유**: Linux MVP를 먼저 완성하는 것이 우선

### NG-7: 자동 수정(Remediation) 기능
- **범위**: 취약점을 자동으로 수정하는 엔진, 백업/롤백 시스템
- **예정**: Phase 3 (Week 7-8), 별도 PRD 작성
- **이유**: 점검 기능이 먼저 안정화되어야 안전한 자동 수정 가능

---

## 6. Design Considerations

### 6.1 스크립트 구조
```
scripts/migrate_legacy.py
├── main()
├── parse_arguments()
├── extract_functions()      # AST로 함수 추출
├── convert_python2_to_3()   # 2to3 + 커스텀 변환
├── generate_yaml_rules()    # YAML 생성
├── generate_validators()    # validator 함수 생성
├── generate_tests()         # 테스트 생성
└── generate_report()        # 보고서 생성
```

### 6.2 YAML 규칙 파일 위치
```
config/rules/linux/
├── U-01.yaml  # root 원격 로그인 제한
├── U-02.yaml  # 패스워드 복잡도 설정
├── ...
└── U-10.yaml
```

### 6.3 Validator 함수 위치
```
src/core/analyzer/validators/
├── __init__.py
└── linux.py
    ├── check_u01_root_remote_login()
    ├── check_u02_password_complexity()
    └── ...
```

---

## 7. Technical Considerations

### 7.1 Python 2→3 변환 도구
- **도구**: 표준 라이브러리 `lib2to3` + 커스텀 정규식
- **이유**: 2to3는 기본 구문만 변환, 프로젝트별 커스터마이징 필요
- **대안**: AST(Abstract Syntax Tree)를 직접 파싱하여 완전한 제어 (복잡도 증가)

### 7.2 함수 추출 방법
- **방법**: Python AST 모듈 사용
- **코드 예시**:
```python
import ast

with open('Linux_Check_2.py', 'r', encoding='utf-8', errors='ignore') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name.startswith('_') and node.name.endswith('SCRIPT'):
            # 함수 추출 로직
```

### 7.3 의존성
- **필수 패키지**: pyyaml, pytest (이미 설치됨)
- **추가 패키지 없음**: 표준 라이브러리만 사용

### 7.4 인코딩 전략
- **문제**: Legacy 코드는 cp949와 utf-8이 혼재
- **해결**: `errors='ignore'`로 읽고 UTF-8로 쓰기, 깨진 부분은 로그에 기록

### 7.5 기존 아키텍처와의 통합
- **Clean Architecture 준수**: validator 함수는 `src/core/analyzer/` 레이어에 배치
- **YAML 규칙**: `config/rules/` 디렉토리 (인프라 계층과 분리)
- **테스트**: `tests/unit/` 디렉토리

---

## 8. Success Metrics

### 8.1 기능적 성공 지표
- 10개 함수가 Python 3.12에서 정상 실행 (에러 없음)
- 10개 YAML 규칙 파일 생성 완료
- 10개 validator 함수 스켈레톤 생성 완료
- 마이그레이션 보고서 자동 생성

### 8.2 품질 지표
- 테스트 커버리지 60% 이상 (`pytest --cov`)
- Legacy 결과와 100% 일치 (가능한 경우)
- black, ruff 린트 통과

### 8.3 재사용성 지표
- Week 4에 `--count 73` 실행 시 나머지 63개 함수도 자동 변환 성공
- 마이그레이션 시간: 73개 전체 30분 이내 (수동 검토 제외)

### 8.4 문서화 지표
- `docs/MIGRATION_REPORT.md` 자동 생성
- 각 함수에 docstring 포함
- README.md에 스크립트 사용법 추가

---

## 9. Open Questions

### Q1: KISA 기준 코드 매핑
- 73개 함수가 정확히 어떤 KISA 취약점 코드(U-01 ~ U-73)에 매핑되는지?
- Legacy 코드에 주석이나 문서가 있는지 확인 필요
- **해결 방안**: Day 3에 Legacy 코드 분석하며 수동 매핑

### Q2: 10개 함수 선택 기준
- 어떤 10개 함수를 먼저 마이그레이션할지?
- **제안**: 가장 간단한 것부터 (파일 권한 체크, 디렉토리 존재 확인 등)
- **해결 방안**: Day 3에 73개 함수 복잡도 분석 후 결정

### Q3: 검증 방법
- Legacy 시스템과 동일한 결과를 어떻게 확인?
- 테스트 서버가 필요한가?
- **해결 방안**: Docker로 Ubuntu 18.04 테스트 환경 구축 (선택)

### Q4: 인코딩 문제 해결 범위
- cp949로 저장된 주석/문자열을 모두 UTF-8로 변환하면 Legacy와 비교 불가?
- 한글 깨짐이 치명적인 부분이 있는가?
- **해결 방안**: 깨진 부분은 로그에 기록하고 수동 수정, Week 2에 보완

### Q5: Validator 함수 실제 구현 시점
- 이번 PRD에서는 스켈레톤만 생성하는 것이 맞는가?
- 아니면 10개는 완전히 구현?
- **제안**: 스켈레톤만 생성, Week 2 Analyzer PRD에서 구현

---

## 10. Dependencies

### 10.1 선행 작업
- Phase 1, Week 1, Day 1-2 완료 (프로젝트 구조, venv, requirements.txt)

### 10.2 후속 작업
- Week 2 (Day 6-8): Scanner 엔진 PRD 및 구현
- Week 2 (Day 9-10): Analyzer 엔진 PRD 및 구현 (validator 실제 로직 작성)
- Week 4 (Day 18-19): 나머지 63개 함수 마이그레이션 (이 스크립트 재사용)

---

## 11. Timeline

| Day | 작업 내용 | 결과물 |
|-----|----------|--------|
| **Day 3** | Legacy 코드 분석, 10개 함수 선정, 스크립트 설계 | 설계 문서 |
| **Day 4** | `migrate_legacy.py` 구현 (Python 2→3, 함수 추출) | 작동하는 스크립트 |
| **Day 5** | YAML 생성, validator 생성, 테스트 작성, 문서화 | 10개 규칙 완성 |

**총 소요 시간**: 3일 (24시간)

---

**문서 끝**