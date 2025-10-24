# Python 2→3 마이그레이션 전략

**작성일**: 2025-10-17
**목적**: Legacy Python 2 코드를 Python 3.12로 안전하게 마이그레이션

---

## 1. 개요

### 목표

2017년 개발된 Legacy Python 2 보안 점검 코드를 Python 3.12 기반의 BluePy 2.0 시스템으로 마이그레이션합니다.

**Legacy 시스템:**
- 언어: Python 2.7
- 파일: `legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py` (957줄)
- 함수: 73개 점검 함수 (_1SCRIPT ~ _73SCRIPT)
- 인코딩: BOM-UTF8, cp949 혼재
- 패턴: 하드코딩, 전역 변수, 절차적 프로그래밍

**목표 시스템:**
- 언어: Python 3.12
- 아키텍처: Clean Architecture
- 패턴: YAML 기반 규칙 시스템, 함수형 프로그래밍
- 인코딩: UTF-8 통일

### 마이그레이션 범위

**Phase 1 (Week 1, Day 3-5):**
- 10개 대표 함수 마이그레이션
- 자동화 스크립트 개발
- 검증 시스템 구축

**Phase 2 (Week 2+):**
- 나머지 63개 함수 마이그레이션
- 전체 시스템 통합
- 프로덕션 배포

---

## 2. 마이그레이션 프로세스

### 전체 워크플로우

```
Legacy Python 2 코드 (Linux_Check_2.py)
    ↓
[1] 인코딩 변환 (BOM-UTF8/cp949 → UTF-8)
    ↓
[2] Python 2→3 구문 변환 (lib2to3)
    ↓
[3] AST 기반 함수 추출
    ↓
[4] bash 명령어 추출
    ↓
[5] YAML 규칙 생성
    ↓
[6] Validator 함수 스켈레톤 생성
    ↓
[7] 마이그레이션 보고서 생성
    ↓
[수동] Validator 함수 구현
    ↓
[수동] 테스트 작성 및 실행
    ↓
완료
```

---

## 3. 단계별 세부 전략

### Step 1: 인코딩 변환

**문제:**
- Legacy 코드는 BOM-UTF8, cp949, euc-kr 혼재
- Python 3는 기본적으로 UTF-8 인코딩 요구

**전략:**
```python
def read_legacy_file(filepath: str) -> str:
    """다중 인코딩 시도로 Legacy 파일 읽기"""
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'latin-1']

    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            logger.info(f"파일을 {encoding}으로 성공적으로 읽었습니다")
            return content
        except (UnicodeDecodeError, LookupError):
            continue

    raise ValueError(f"파일을 읽을 수 없습니다: {filepath}")
```

**검증:**
- 변환 후 한글 깨짐 확인
- 주석, 문자열 리터럴 확인

**출력:**
- UTF-8로 저장
- 파일 첫 줄에 `# -*- coding: utf-8 -*-` 추가

---

### Step 2: Python 2→3 구문 변환

**도구: lib2to3**

lib2to3는 Python 공식 변환 도구로, AST 기반 자동 변환을 수행합니다.

**주요 변환 항목:**

| Python 2 | Python 3 | fixer |
|----------|----------|-------|
| `print "hello"` | `print("hello")` | fix_print |
| `except E, e:` | `except E as e:` | fix_except |
| `unicode()` | `str()` | fix_unicode |
| `d.has_key(k)` | `k in d` | fix_has_key |
| `raw_input()` | `input()` | fix_raw_input |
| `xrange()` | `range()` | fix_xrange |

**구현:**
```python
from lib2to3.refactor import RefactoringTool

fixers = [
    'lib2to3.fixes.fix_print',
    'lib2to3.fixes.fix_except',
    'lib2to3.fixes.fix_unicode',
    'lib2to3.fixes.fix_has_key',
    'lib2to3.fixes.fix_raw_input',
    'lib2to3.fixes.fix_xrange',
]

tool = RefactoringTool(fixers)
refactored = tool.refactor_string(python2_code, '<stdin>')
python3_code = str(refactored)
```

**한계:**
- 의미론적 변환 불가 (str/bytes 구분 등)
- Legacy 특수 함수 (_SETOK, _SETBAD 등)는 그대로 유지
- 수동 검토 필요

**검증:**
- `ast.parse()` 성공 여부
- `python -m py_compile` 구문 오류 확인

---

### Step 3: AST 기반 함수 추출

**목표:**
- _1SCRIPT ~ _73SCRIPT 함수를 AST로 파싱
- 소스 코드, 복잡도, KISA 코드 추출

**구현:**
```python
import ast

def extract_functions(python3_code: str) -> Dict[str, FunctionInfo]:
    """AST로 함수 추출"""
    tree = ast.parse(python3_code)
    functions = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_') and node.name.endswith('SCRIPT'):
                # 함수 번호 추출: _4SCRIPT → 4
                func_number = int(
                    node.name.replace('_', '').replace('SCRIPT', '')
                )

                # KISA 코드 매핑
                kisa_code = f'U-{func_number:02d}'

                # 소스 코드 추출 (Python 3.9+)
                source = ast.unparse(node)

                # 복잡도 계산 (AST 노드 수)
                complexity = len(list(ast.walk(node)))

                # 심각도 추출 (함수 내에서 _SETHIGH/_SETMID/_SETLOW 찾기)
                severity = extract_severity(node)

                functions[node.name] = FunctionInfo(
                    name=node.name,
                    number=func_number,
                    kisa_code=kisa_code,
                    source=source,
                    complexity=complexity,
                    severity=severity,
                    ast_node=node
                )

    return functions
```

**복잡도 기준:**
- 매우 낮음: < 20 노드
- 낮음: 20-50 노드
- 중: 51-100 노드
- 높음: > 100 노드

---

### Step 4: bash 명령어 추출

**목표:**
- Legacy 함수에서 실행하는 bash 명령어 추출
- YAML의 commands 필드 생성

**패턴:**
1. `os.popen('command')`
2. `subprocess.call(['command'])`
3. `_SPLIT(data)` - 여러 명령어를 `;`로 구분

**구현:**
```python
def extract_commands(func_ast: ast.FunctionDef) -> List[str]:
    """함수 내 bash 명령어 추출"""
    commands = []

    for node in ast.walk(func_ast):
        # os.popen('command') 패턴
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr') and node.func.attr == 'popen':
                if node.args:
                    cmd = ast.unparse(node.args[0])
                    # 문자열 리터럴의 따옴표 제거
                    cmd = cmd.strip('"\'')
                    commands.append(cmd)

        # _SPLIT 패턴 인식
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'id') and node.func.id == '_SPLIT':
                # _SPLIT은 여러 명령어를 ; 로 구분
                # 주석으로 표시
                commands.append("# TODO: _SPLIT 패턴 - 여러 명령어 확인 필요")

    return commands
```

**폴백:**
- 추출 실패 시 TODO 주석으로 표시
- 수동 검토 필요 로그 남김

---

### Step 5: YAML 규칙 생성

**목표:**
- RuleMetadata 스키마에 맞는 YAML 파일 생성
- 자동 추론 + 수동 검토용 TODO

**템플릿:**
```python
def generate_yaml(func_info: FunctionInfo, commands: List[str]) -> str:
    """YAML 규칙 생성"""

    # category 자동 매핑 (KISA 코드 범위 기반)
    category = map_category(func_info.kisa_code)

    # validator 함수명 생성
    validator_name = f"check_{func_info.kisa_code.lower().replace('-', '')}_TODO"
    validator = f"validators.linux.{validator_name}"

    yaml_data = {
        'id': func_info.kisa_code,
        'name': f'TODO: {func_info.kisa_code} 규칙 이름',
        'category': category,
        'severity': func_info.severity.value,
        'kisa_standard': func_info.kisa_code,
        'description': f'TODO: {func_info.kisa_code} 상세 설명',
        'commands': commands or ['# TODO: 명령어 추가 필요'],
        'validator': validator,
        'expected_result': f'TODO: {func_info.kisa_code} 기대 결과',
        'remediation': {
            'auto': False,
            'manual_steps': ['TODO: 수동 수정 단계']
        }
    }

    return yaml.dump(yaml_data, allow_unicode=True, sort_keys=False)
```

**카테고리 매핑:**
```python
def map_category(kisa_code: str) -> str:
    """KISA 코드 → 카테고리"""
    number = int(kisa_code.split('-')[1])

    if 1 <= number <= 15:
        return '계정관리'
    elif 16 <= number <= 26:
        return '파일 및 디렉토리 관리'
    elif 27 <= number <= 43:
        return '서비스 관리'
    elif 44 <= number <= 51:
        return '패치 관리'
    elif 52 <= number <= 73:
        return '로그 관리'
    else:
        return 'TODO: 카테고리'
```

---

### Step 6: Validator 함수 스켈레톤 생성

**목표:**
- CheckResult를 반환하는 함수 템플릿 생성
- Legacy 로직을 주석으로 포함
- TODO 주석으로 구현 힌트 제공

**템플릿:**
```python
def generate_validator_skeleton(func_info: FunctionInfo) -> str:
    """Validator 함수 스켈레톤 생성"""

    func_name = f"check_{func_info.kisa_code.lower().replace('-', '')}_TODO"

    # Legacy 로직을 주석으로
    legacy_code_comment = '\n'.join(
        f'    # {line}' for line in func_info.source.split('\n')
    )

    skeleton = f'''
def {func_name}(command_outputs: Dict[str, str]) -> CheckResult:
    """
    {func_info.kisa_code}: TODO 규칙 이름

    점검 내용:
    - TODO: 점검 내용 설명

    Legacy 로직:
    ```python
{legacy_code_comment}
    ```

    Args:
        command_outputs: 명령어 실행 결과 딕셔너리
            Key: 명령어 문자열
            Value: 실행 결과 (stdout)

    Returns:
        CheckResult: 점검 결과
    """
    # TODO: Implement validation logic
    # 힌트: command_outputs에서 필요한 데이터를 가져와 검증

    return CheckResult(
        status=Status.MANUAL,
        message=f"구현 필요: {func_info.kisa_code} 점검 로직"
    )
'''

    return skeleton
```

---

### Step 7: 마이그레이션 보고서 생성

**목표:**
- 마이그레이션 결과 요약
- 수동 작업 필요 항목 목록
- 다음 단계 가이드

**포함 내용:**
1. 처리된 함수 목록 (10개)
2. 각 함수별:
   - KISA 코드
   - 복잡도
   - 추출된 명령어 수
   - 생성된 파일 (YAML, validator)
3. 경고/에러 목록
4. 수동 작업 체크리스트
5. 다음 단계

**예시:**
```markdown
# 마이그레이션 보고서

**일시**: 2025-10-17
**처리 함수**: 10개

## 요약

- 성공: 10개
- 경고: 2개
- 에러: 0개

## 함수 목록

| KISA | 함수명 | 복잡도 | 명령어 | YAML | Validator |
|------|--------|--------|--------|------|-----------|
| U-01 | _1SCRIPT | 높음 | 2개 |  |  |
| U-04 | _4SCRIPT | 매우낮음 | 1개 |  |  |
...

## 경고

1. U-01: _SPLIT 패턴 - 명령어 수동 확인 필요
2. U-18: 복잡한 문자열 조작 - 로직 검토 필요

## 다음 단계

- [ ] YAML 파일의 TODO 항목 수정
- [ ] Validator 함수 구현
- [ ] 테스트 작성 및 실행
- [ ] 코드 리뷰
```

---

## 4. 자동화 범위

### 자동화 가능 (scripts/migrate_legacy.py)

1. 인코딩 변환 (BOM-UTF8/cp949 → UTF-8)
2. Python 2→3 구문 변환 (lib2to3)
3. 함수 추출 및 분석 (AST)
4. bash 명령어 추출 (AST 패턴 매칭)
5. YAML 규칙 생성 (템플릿 기반)
6. Validator 함수 스켈레톤 생성
7. 마이그레이션 보고서 생성

### 수동 작업 필요

1. YAML 규칙 검토 및 TODO 수정
   - name, description, expected_result
   - 명령어 정확성 확인
   - remediation 상세화
2. Validator 함수 구현
   - Legacy 로직을 Python 3로 재작성
   - CheckResult 생성 로직
   - 예외 처리
3. 테스트 작성
   - 단위 테스트 (각 validator)
   - 통합 테스트 (YAML + validator)
4. 문서 업데이트
   - README.md
   - ROADMAP.md

---

## 5. 검증 방법

### 3단계 검증 프로세스

**1단계: 구문 검증 (Syntax Validation)**
```bash
# Python 구문 오류 확인
python -m py_compile src/core/analyzer/validators/linux.py

# AST 파싱 성공 확인
python -c "import ast; ast.parse(open('src/core/analyzer/validators/linux.py').read())"
```

**2단계: 스키마 검증 (Schema Validation)**
```python
# YAML 파싱 및 pydantic 검증
import yaml
from src.core.domain.models import RuleMetadata

for yaml_file in glob.glob('config/rules/linux/*.yaml'):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    # ValidationError 발생 시 실패
    rule = RuleMetadata(**data)
    print(f" {rule.id}: {rule.name}")
```

**3단계: 통합 검증 (Integration Validation)**
```python
# Validator 함수 존재 및 호출 가능 확인
import importlib

for yaml_file in glob.glob('config/rules/linux/*.yaml'):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    # validator 함수 import
    module_path, func_name = data['validator'].rsplit('.', 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)

    # CheckResult 반환 확인
    result = func({})
    assert isinstance(result, CheckResult)
    print(f" {data['id']}: {func_name} 호출 성공")
```

**자동 테스트:**
```bash
# pytest로 전체 검증
pytest tests/unit/test_migration.py
pytest tests/unit/test_yaml_rules.py
pytest tests/unit/test_validators.py
```

---

## 6. 리스크 및 대응 방안

### 리스크 1: 인코딩 문제

**리스크:**
- Legacy 파일의 인코딩을 잘못 읽어 한글 깨짐
- 특수 문자 손실

**대응:**
- 다중 인코딩 시도 (utf-8-sig → cp949 → euc-kr → latin-1)
- 변환 후 한글 포함 문자열 육안 확인
- 로그에 사용된 인코딩 기록

**검증:**
- 주석, 문자열 리터럴의 한글 확인
- diff 도구로 변환 전후 비교

---

### 리스크 2: lib2to3 변환 실패

**리스크:**
- Python 2 구문이 완전히 변환되지 않음
- 의미론적 오류 (str/bytes 등)

**대응:**
- ast.parse()로 구문 오류 확인
- TODO 주석으로 수동 검토 항목 표시
- 변환 실패 시 에러 로그 상세히 기록

**검증:**
- `python -m py_compile` 실행
- 구문 오류 0개 확인

---

### 리스크 3: bash 명령어 추출 실패

**리스크:**
- 복잡한 문자열 조작으로 명령어 추출 실패
- _SPLIT 패턴 인식 실패

**대응:**
- 패턴 매칭 + 로그 남김
- 추출 실패 시 "# TODO: 명령어 확인 필요" 추가
- Legacy 코드 주석으로 포함하여 수동 확인 가능하게

**검증:**
- 추출된 명령어 수 확인 (보고서)
- 수동으로 Legacy 코드와 비교

---

### 리스크 4: KISA 코드 매핑 오류

**리스크:**
- 함수 번호와 KISA 코드가 1:1 매핑이 아닐 수 있음
- 일부 함수는 여러 KISA 코드를 처리할 수 있음

**대응:**
- LEGACY_ANALYSIS_DETAIL.md 문서 참조
- 함수 번호 → KISA 코드 매핑 테이블 작성
- 불일치 시 경고 로그

**검증:**
- 문서와 cross-check
- 전문가 리뷰

---

### 리스크 5: 심각도 추론 오류

**리스크:**
- _SETHIGH/_SETMID/_SETLOW를 찾지 못함
- 복잡한 조건문 내에 있을 경우

**대응:**
- 기본값 "high" 설정 (안전 우선)
- 로그에 심각도 추론 실패 기록
- 수동 검토 항목으로 표시

**검증:**
- KISA 기준 문서와 비교
- 보고서에 심각도 목록 포함

---

## 7. 실행 가이드

### 스크립트 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 10개 함수 마이그레이션
python scripts/migrate_legacy.py \
    --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \
    --output-dir output/ \
    --functions U-01,U-04,U-07,U-08,U-09,U-05,U-18,U-27,U-03,U-10 \
    --verbose

# 결과 확인
tree output/
```

### 출력 구조

```
output/
├── yaml/
│   ├── U-01.yaml
│   ├── U-04.yaml
│   ├── U-07.yaml
│   ├── U-08.yaml
│   ├── U-09.yaml
│   ├── U-05.yaml
│   ├── U-18.yaml
│   ├── U-27.yaml
│   ├── U-03.yaml
│   └── U-10.yaml
├── validators/
│   └── linux.py  (10개 함수 스켈레톤)
└── MIGRATION_REPORT.md
```

### 통합

```bash
# YAML 파일 복사
cp output/yaml/*.yaml config/rules/linux/

# Validator 함수 복사 (기존 파일에 추가)
cat output/validators/linux.py >> src/core/analyzer/validators/linux.py

# 검증
pytest tests/unit/
```

---

## 8. 수동 작업 체크리스트

마이그레이션 스크립트 실행 후 다음 작업을 수행하세요:

### YAML 규칙 수정

- [ ] 각 YAML 파일의 TODO 항목 수정
  - [ ] name: 규칙 이름 명확히
  - [ ] description: 상세 설명 (취약점, 조치 방법)
  - [ ] expected_result: 기대 결과 구체화
  - [ ] commands: 명령어 정확성 확인
  - [ ] remediation: 수정 단계 상세화

### Validator 함수 구현

- [ ] 각 validator 함수 구현
  - [ ] Legacy 로직을 Python 3로 재작성
  - [ ] command_outputs에서 데이터 추출
  - [ ] 검증 로직 구현
  - [ ] CheckResult 반환 (status, message, details)
  - [ ] 예외 처리 (try-except)
  - [ ] Docstring 업데이트

### 테스트 작성

- [ ] tests/unit/test_validators.py
  - [ ] 각 validator 함수 테스트
  - [ ] 정상 케이스 (PASS)
  - [ ] 취약 케이스 (FAIL)
  - [ ] 예외 케이스 (MANUAL)

- [ ] tests/unit/test_yaml_rules.py
  - [ ] YAML 파싱 테스트
  - [ ] pydantic 검증 테스트
  - [ ] validator 매칭 테스트

### 문서 업데이트

- [ ] README.md: 사용법 추가
- [ ] ROADMAP.md: 진행 상황 업데이트
- [ ] MIGRATION_REPORT.md: 검토

---

## 9. 다음 단계 (Week 2)

1. **Validator 함수 구현** (Day 6-8)
   - 10개 함수 구현
   - 테스트 작성 및 실행
   - 코드 리뷰

2. **통합 테스트** (Day 9)
   - Scanner + Analyzer + Validator 통합
   - 실제 Linux 시스템에서 테스트

3. **나머지 63개 함수 마이그레이션** (Week 3-4)
   - 스크립트 재실행
   - 동일한 프로세스 반복

---

## 10. 참고 자료

- **Legacy 분석**: `docs/LEGACY_ANALYSIS_DETAIL.md`
- **도메인 모델**: `docs/DOMAIN_MODEL_DESIGN.md`
- **YAML 스키마**: `docs/YAML_SCHEMA_GUIDE.md`
- **Task List**: `tasks/tasks-prd-python2-to-3-migration.md`
- **Python 2to3**: https://docs.python.org/3/library/2to3.html
- **lib2to3**: https://docs.python.org/3/library/lib2to3.html
- **AST module**: https://docs.python.org/3/library/ast.html

---

## 11. 최종 상태 (2025-10-18 완료)

### 11.1 마이그레이션 완료 요약

**Phase 1 (Week 1): Python 2→3 마이그레이션 완료**
-  73개 함수 추출 성공 (FunctionInfo 데이터 구조)
-  73개 YAML 규칙 파일 생성 (UTF-8 인코딩, 한글 보존)
-  73개 Validator 함수 구현 (Python 3.12, Status 판단 로직)
-  5개 카테고리 완성 (account_management, file_management, service_management, patch_management, log_management)
-  마이그레이션 스크립트 완성 (scripts/migrate_legacy.py, 700+ 줄)

**완료 비율**: 100% (73/73 함수)

### 11.2 검증 결과

**구문 검증 (Syntax Validation)**:
-  모든 Python 파일 py_compile 통과
-  AST 파싱 성공 (구문 오류 0개)

**스키마 검증 (Schema Validation)**:
-  73개 YAML 파일 yaml.safe_load() 성공
-  RuleMetadata pydantic 검증 통과
-  필수 필드 (id, name, commands, validator) 모두 존재

**통합 검증 (Integration Validation)**:
-  Validator 함수 import 성공 (73/73)
-  CheckResult 반환 타입 일치
-  테스트 354개 통과 (100% 통과율)

### 11.3 최종 통계

| 항목 | 수량 | 비고 |
|------|------|------|
| **마이그레이션 함수** | 73개 | 100% 완료 |
| **YAML 규칙 파일** | 73개 | UTF-8, 255-412 바이트 |
| **Validator 함수** | 73개 | Python 3.12, 완전 구현 |
| **테스트 케이스** | 354개 | 100% 통과 |
| **코드 커버리지** | 63% | 목표 60% 초과 달성 |
| **Git 커밋** | 18개 | Phase 1-3 완료, Phase 5 진행 중 |
| **코드 라인** | ~5,000줄 | 마이그레이션 + Validator + YAML |

### 11.4 달성한 목표

**기술적 목표**:
1.  Python 2 → Python 3.12 완전 변환
2.  하드코딩 제거 (YAML 규칙 시스템 구축)
3.  UTF-8 인코딩 통일 (한글 깨짐 해결)
4.  확장 가능한 아키텍처 (Clean Architecture)
5.  테스트 자동화 (pytest, 354개 테스트)

**비즈니스 목표**:
1.  개발 시간 단축 (70% 로직 재사용)
2.  검증된 규칙 활용 (KISA 73개 항목)
3.  빠른 MVP 출시 (4주 만에 Linux MVP 완성)

### 11.5 다음 단계

**완료된 Phase**:
-  Phase 1: Linux MVP (Week 1-4)
-  Phase 1.5: Testing Infrastructure (커버리지 63%)
-  Phase 2: macOS 확장 (50개 규칙)
-  Phase 3: Remediation 엔진 + Linux Remediation (15개 자동 수정 규칙)

**진행 중**:
- Phase 5: Quick Wins (History View, 다크 모드, 설정 UI)

**계획**:
- Phase 4: Windows 지원 (WinRM, 50개 규칙)
- Phase 5: 고급 기능 (대시보드, PDF 보고서, 스케줄러)

---

**문서 끝**
