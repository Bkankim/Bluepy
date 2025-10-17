# BluePy 2.0 - 개발 로드맵

**작성일**: 2025-10-17
**총 기간**: 12.5주 (약 3개월)
**시작일**: TBD
**상태**: Planning

---

## 목차

1. [로드맵 개요](#1-로드맵-개요)
2. [Timeline](#2-timeline)
3. [Phase 1: Linux MVP](#3-phase-1-linux-mvp-4주)
4. [Phase 2: macOS 확장](#4-phase-2-macos-확장-15주)
5. [Phase 3: 자동 수정 강화](#5-phase-3-자동-수정-강화-2주)
6. [Phase 4: Windows 지원](#6-phase-4-windows-지원-3주)
7. [Phase 5: 고급 기능](#7-phase-5-고급-기능-2주)
8. [마일스톤](#8-마일스톤)
9. [리스크 관리](#9-리스크-관리)
10. [품질 보증](#10-품질-보증)

---

## 1. 로드맵 개요

### 1.1 전체 목표

**BluePy 2.0**: 2017년 Legacy 시스템을 현대적인 멀티플랫폼 보안 관리 도구로 재구성

**주요 마일스톤**:
- **M1 (Week 4)**: Linux MVP - 기존 기능 재구현
- **M2 (Week 6)**: macOS 지원 - Unix 통합
- **M3 (Week 8)**: 자동 수정 - 핵심 차별화 기능
- **M4 (Week 11)**: Windows 지원 - 3-OS 완성
- **M5 (Week 13)**: 출시 준비 - 완전한 제품

### 1.2 개발 원칙

1. **점진적 개발**: 각 Phase는 독립적으로 동작 가능
2. **테스트 우선**: 커버리지 60% 이상 유지
3. **문서화 동시 작성**: 코드와 문서를 함께 업데이트
4. **사용자 피드백**: 각 Phase 후 베타 테스트
5. **기술 부채 관리**: 매 Phase 후 리팩토링

---

## 2. Timeline

### 2.1 Gantt Chart (ASCII)

```
Week    1    2    3    4    5    6    7    8    9   10   11   12   13
       ─────────────────────────────────────────────────────────────────
Phase 1 ████████████████
        Linux MVP

Phase 2                 ██████
                        macOS

Phase 3                       ████████
                              Auto-Fix

Phase 4                               ████████████
                                      Windows

Phase 5                                           ████████
                                                  Advanced

Tests   ────▲───▲───▲───▲──▲──▲──▲──▲──▲──▲──▲──▲──▲───▲
Docs    ────────▲───────▲──▲─────▲────────▲─────────▲
Review  ────────────────▲─────▲─────▲───────────▲────────▲

Legend:
█ 개발 중
▲ 마일스톤/리뷰
```

### 2.2 Phase별 시간 배분

| Phase | 기간 | 비율 | 주요 작업 |
|-------|------|------|----------|
| Phase 1 | 4주 | 32% | Linux 마이그레이션, GUI 기본 |
| Phase 2 | 1.5주 | 12% | macOS 규칙, Unix 추상화 |
| Phase 3 | 2주 | 16% | 자동 수정, 백업/롤백 |
| Phase 4 | 3주 | 24% | Windows 지원 |
| Phase 5 | 2주 | 16% | 이력 관리, UX 개선 |
| **Total** | **12.5주** | **100%** | |

---

## 3. Phase 1: Linux MVP (4주)

### 3.1 목표

**"기존 2017년 시스템과 동일한 기능을 현대적으로 재구현"**

- Linux 73개 점검 항목 마이그레이션
- Python 3.12+ 기반 재작성
- PySide6 GUI 기본 구조
- Excel 보고서 생성

### 3.2 Week 1: 프로젝트 초기화 + 마이그레이션 시작

#### Day 1-2: 프로젝트 설정

**작업 항목**:
- [ ] Git 저장소 초기화
  ```bash
  git init
  git add .
  git commit -m "Initial commit: 2017 legacy backup"
  ```
- [ ] 프로젝트 구조 생성
  ```bash
  mkdir -p src/{core,gui,infrastructure,utils}
  mkdir -p config/rules/{linux,macos,windows}
  mkdir -p data/{databases,reports}
  mkdir -p tests/{unit,integration}
  ```
- [ ] 기존 코드를 legacy/infra/ 로 이동
- [ ] Python 가상환경 설정
  ```bash
  python3.12 -m venv venv
  source venv/bin/activate
  ```
- [ ] requirements.txt 작성 및 설치
- [ ] .gitignore 업데이트

**결과물**:
- ✅ 프로젝트 구조 완성
- ✅ 의존성 설치 완료
- ✅ Git 저장소 설정

#### Day 3-5: Python 2 → 3 마이그레이션

**작업 항목**:
- [x] Linux_Check_2.py 분석
  - 73개 `_1SCRIPT` ~ `_73SCRIPT` 함수 파악
  - 각 함수의 로직 이해
  - 11개 헬퍼 함수 파악
  - 결과: `docs/LEGACY_ANALYSIS_DETAIL.md` (957줄 분석 완료)
- [x] 10개 함수 선정 및 문서화
  - 복잡도 평가 완료
  - KISA 코드 매핑 완료 (U-04, U-07, U-08, U-09, U-05, U-18, U-27, U-01, U-03, U-10)
  - 선정 근거 문서화 완료
- [x] 도메인 모델 설계 및 구현
  - Status, Severity Enum 설계 및 구현
  - CheckResult dataclass 구현
  - RuleMetadata, RemediationInfo pydantic BaseModel 구현
  - 결과: `docs/DOMAIN_MODEL_DESIGN.md`, `src/core/domain/models.py`
- [x] YAML 스키마 설계 및 예시 작성
  - RuleMetadata 기반 YAML 스키마 정의
  - 필수/선택 필드 확정
  - 3개 예시 YAML 작성 (U-01, U-04, U-18)
  - 결과: `docs/YAML_SCHEMA_GUIDE.md`, `config/rules/linux/U-{01,04,18}.yaml`
- [x] 마이그레이션 전략 문서 작성
  - 인코딩 변환 전략 (BOM-UTF8/cp949 → UTF-8)
  - lib2to3 기반 Python 2→3 구문 변환
  - AST 기반 함수 추출 전략
  - YAML 및 Validator 자동 생성 전략
  - 3단계 검증 프로세스 (구문/스키마/통합)
  - 리스크 및 대응 방안
  - 결과: `docs/MIGRATION_STRATEGY.md`
- [x] 마이그레이션 스크립트 핵심 엔진 개발 (scripts/migrate_legacy.py) - Task 2.0 완료
  - CLI 인터페이스 (argparse, --input, --output-dir, --all, --functions)
  - 듀얼 로깅 시스템 (console + file)
  - 입력 검증 (파일 존재, 출력 디렉토리, KISA 코드 형식)
  - 다중 인코딩 fallback (utf-8-sig → utf-8 → cp949 → euc-kr → latin-1)
  - 정규식 기반 Python 2→3 변환 (lib2to3 대체, Python 3.12 호환)
  - FunctionInfo dataclass (name, number, kisa_code, source, complexity, severity, ast_node)
  - AST 기반 함수 추출 (extract_severity, extract_function_info, extract_functions)
  - 73개 함수 추출 성공 (U-01 ~ U-73)
  - 결과: `scripts/migrate_legacy.py` (700+ 줄)
- [x] bash 명령어 추출 로직 구현 (Task 3.1 완료)
  - parse_linux_bash_script() 함수 (113줄, State machine 방식)
    * KISA 코드 인식: echo "X-X ..." 패턴
    * 명령어 수집: cat, ls, ps, grep, egrep, find, pwconv
    * 리다이렉션 자동 제거 (>>report.txt)
    * 변수 유지 ($APACHE_DIRECTORY)
  - FunctionInfo에 commands 필드 추가 (List[str])
  - extract_function_info() 수정: commands_by_kisa 연결
  - 결과: 35개 KISA 코드에서 35개 명령어 추출 성공
- [x] YAML 템플릿 생성 함수 구현 (Task 3.2 완료)
  - KISA_NAMES 딕셔너리 (73개 규칙 이름 전체 매핑)
  - infer_category(kisa_code) 함수
    * U-01~15: 계정관리
    * U-16~35: 파일 및 디렉터리 관리
    * U-36~70: 서비스 관리
    * U-71: 패치 관리
    * U-72~73: 로그 관리
  - generate_validator_name(kisa_code) 함수
    * U-01 → validators.linux.check_u01 형식 자동 생성
  - generate_yaml_template(func_info) 함수
    * FunctionInfo → YAML dict 완전 자동 변환
    * 모든 필드 생성: id, name, category, severity, commands, validator, remediation
  - 결과: U-01 샘플 YAML 생성 성공 (완전한 구조)
- [x] YAML 파일 저장 및 검증 (Task 3.3 완료)
  - save_yaml_file() 함수 구현 (43줄)
    * UTF-8 인코딩 (allow_unicode=True)
    * 한글 보존 (ensure_ascii=False)
    * YAML 블록 스타일 (default_flow_style=False)
    * 키 순서 유지 (sort_keys=False)
  - main() 함수 수정
    * 출력 디렉토리 Path 객체 생성
    * results 루프에서 save_yaml_file() 호출
    * 에러 처리 및 로깅
  - 결과: 73개 YAML 파일 전체 생성 성공
- [ ] Validator 함수 스켈레톤 생성 - 진행 예정 (Task 4.0)
- [ ] 10개 함수 시범 마이그레이션 완료 및 보고서 생성 - 진행 예정 (Task 5.0-6.0)

**결과물** (Task 1.0 완료):
- ✅ Legacy 코드 분석 문서 (LEGACY_ANALYSIS_DETAIL.md, 530+ 줄)
- ✅ 도메인 모델 설계 문서 (DOMAIN_MODEL_DESIGN.md)
- ✅ 도메인 모델 구현 (src/core/domain/models.py, 207줄)
  - Status, Severity Enum
  - CheckResult dataclass (is_passed/is_failed/is_manual 헬퍼)
  - RemediationInfo, RuleMetadata (pydantic v2, frozen=True)
  - 완전한 type hints 및 validation
- ✅ YAML 스키마 가이드 (YAML_SCHEMA_GUIDE.md, 400+ 줄)
- ✅ 3개 YAML 규칙 예시 (U-01, U-04, U-18)
- ✅ 마이그레이션 전략 문서 (MIGRATION_STRATEGY.md, 850+ 줄)
- ✅ Task List 생성 및 추적 (tasks/tasks-prd-python2-to-3-migration.md, Task 1.0 완료)

**결과물** (Task 2.0 완료):
- ✅ 마이그레이션 스크립트 핵심 엔진 (scripts/migrate_legacy.py, 700+ 줄)
  - CLI 인터페이스: argparse, --input, --output-dir, --all, --functions, --dry-run, --verbose
  - 듀얼 로깅: console (INFO/DEBUG) + file (모든 레벨, migration.log)
  - 다중 인코딩 지원: utf-8-sig → utf-8 → cp949 → euc-kr → latin-1 fallback
  - 정규식 기반 Python 2→3 변환 (lib2to3 대체, Python 3.12 호환)
  - FunctionInfo dataclass (7 fields)
  - AST 기반 함수 추출 엔진 (extract_severity, extract_function_info, extract_functions)
- ✅ tasks-prd 파일 업데이트 (Task 2.0-2.6 완료 표시)

**검증 완료** (Task 1.0):
- ✅ Python 구문 검증 (py_compile)
- ✅ 도메인 모델 동작 테스트 (Status, Severity, CheckResult, RemediationInfo)
- ✅ pydantic validation 테스트 (RuleMetadata, 패턴 매칭, 필드 제약)
- ✅ YAML 파싱 및 검증 (3개 파일 pydantic 통과)

**검증 완료** (Task 2.0):
- ✅ 인코딩 변환 테스트: Legacy 파일 18,421 문자, utf-8-sig 성공
- ✅ Python 2→3 변환 테스트: 6개 bare except 변환, 구문 검증 통과
- ✅ 통합 테스트: 73개 함수 추출 성공 (U-01 ~ U-73)
- ✅ 복잡도 측정: 21 ~ 128 AST 노드
- ✅ 심각도 분류: 44 HIGH, 17 MID, 12 LOW (1개 경고: _42SCRIPT)

**검증 완료** (Task 3.1-3.2):
- ✅ bash 스크립트 파싱: Linux_Check_1.txt (684줄) 파싱 성공
- ✅ 명령어 추출: 35개 KISA 코드에서 총 35개 명령어 추출 (평균 1.0개/규칙)
- ✅ KISA_NAMES 매핑: 73개 전체 규칙 이름 매핑 완료
- ✅ 카테고리 자동 추론: 5개 카테고리 정확 분류
  - 계정관리 (U-01~15), 파일 및 디렉터리 관리 (U-16~35)
  - 서비스 관리 (U-36~70), 패치 관리 (U-71), 로그 관리 (U-72~73)
- ✅ YAML 템플릿 생성: U-01 샘플 성공 (완전한 YAML 구조)
- ✅ validator 함수명: validators.linux.check_u01 형식 자동 생성

**검증 완료** (Task 3.3):
- ✅ YAML 파일 저장: 73개 파일 전체 생성 성공 (config/rules/linux/)
- ✅ UTF-8 인코딩: 한글 정상 출력 (U-01: root 계정 원격 접속 제한)
- ✅ YAML 구조 검증: U-01, U-18, U-72 샘플 확인
  - U-01: commands 정상 (cat /etc/inetd.conf), category: 계정관리
  - U-18: 변수 유지 ($APACHE_DIRECTORY), category: 파일 및 디렉터리 관리
  - U-72: commands 빈 리스트 (수동 점검 규칙), category: 로그 관리
- ✅ YAML 파싱 테스트: yaml.safe_load() 성공, 데이터 무결성 확인
- ✅ 파일 개수 확인: ls config/rules/linux/*.yaml | wc -l = 73

**재검증 완료** (Task 3.3 - 5단계):
1. ✅ **파일 생성 재검증**:
   - 73개 파일 확인 (0바이트 파일 없음)
   - 파일 크기: 255~412 바이트 (YAML 구조에 따라 정상 범위)
   - 파일명 패턴: U-01.yaml ~ U-73.yaml 정확

2. ✅ **내용 재검증 (5개 카테고리 샘플)**:
   - 계정관리 (U-08): commands 1개, severity mid, 한글 정상
   - 파일 관리 (U-27): commands 1개, severity high, 한글 정상
   - 서비스 관리 (U-42, U-59): commands 빈 리스트 (수동 점검), severity high/mid
   - 패치 관리 (U-71): commands 빈 리스트, severity high
   - 로그 관리 (U-73): commands 빈 리스트, severity low

3. ✅ **파싱 재검증**:
   - 3개 샘플 (U-01, U-42, U-73) yaml.safe_load() 성공
   - 데이터 타입 검증: str, dict, list, bool 모두 정확
   - 중첩 구조: check.commands, remediation.auto 접근 정상
   - 8개 필드 전체 존재 및 순서 일치

4. ✅ **코드 재검증**:
   - import yaml 존재 (Line 37)
   - save_yaml_file() 함수: UTF-8 인코딩, yaml.dump() 옵션, 에러 처리 정확
   - main() 함수: 출력 디렉토리 생성, results 루프, 에러 처리 정확

5. ✅ **문서/Git 재검증**:
   - commit 3f8fd58: "feat: Complete Task 3.3 - YAML file saving and generation"
   - 76 files changed, 1359 insertions(+), 154 deletions(-)
   - working tree clean (추가 변경사항 없음)

**Task 4.0 완료**: Validator 스켈레톤 생성 (2025-10-17)

**구현 내용**:
1. generate_validator_skeleton() 함수 (70줄)
   - FunctionInfo → Python 함수 코드 생성
   - Docstring 자동 생성 (KISA 코드, 규칙 이름, TODO)
   - 파라미터: List[str], 리턴: CheckResult
   - f-string 템플릿 기반 코드 생성

2. save_validator_files() 함수 (95줄)
   - 카테고리별 그룹화 (5개 파일)
   - UTF-8 인코딩 (allow_unicode=True)
   - import 문 자동 추가 (typing, models)
   - 파일 헤더 (docstring, 생성일) 추가

3. create_init_file() 함수 (105줄)
   - __init__.py 생성
   - 73개 함수 export
   - __all__ 리스트 자동 생성
   - import 문 카테고리별 정리

**생성 결과**:
- 6개 파일 생성 (src/core/analyzer/validators/linux/)
  * __init__.py (2.8K)
  * account_management.py (14K, 15개 함수)
  * file_management.py (19K, 20개 함수)
  * service_management.py (31K, 35개 함수)
  * patch_management.py (1.3K, 1개 함수)
  * log_management.py (2.1K, 2개 함수)
- 73개 validator 함수 스켈레톤 (check_u01 ~ check_u73)
- 모든 함수: List[str] 파라미터, CheckResult 리턴, Status.MANUAL 기본값

**검증 완료**:
- 구문 검증: py_compile 성공 (6개 파일 모두)
- Import 테스트: check_u01, check_u42, check_u73 import 성공
- 함수 호출 테스트: CheckResult 리턴 확인 (status=Status.MANUAL)
- 함수 개수: grep으로 73개 확인

**Task 5.0 완료**: 10개 함수 시범 마이그레이션 (2025-10-17)

**구현 내용**:
1. 10개 함수 선정 (KISA 코드 기준)
   - U-01: root 계정 원격 접속 제한 (high)
   - U-03: 계정잠금 임계값 설정 (high)
   - U-04: 패스워드 파일 보호 (high)
   - U-05: root 이외의 UID가 '0' 금지 (mid)
   - U-07: 패스워드 최소 길이 설정 (mid)
   - U-08: 패스워드 최대 사용기간 설정 (mid)
   - U-09: 패스워드 최소 사용기간 설정 (mid)
   - U-10: 불필요한 계정 제거 (low)
   - U-18: /etc/passwd 파일 소유자 및 권한 설정 (high)
   - U-27: /dev에 존재하지 않는 device 파일 점검 (high)

2. Legacy 로직 분석 및 Python 3 변환
   - Legacy _1SCRIPT ~ _10SCRIPT, _18SCRIPT, _27SCRIPT 로직 분석
   - Python 2 → Python 3 문법 변환 (리스트 컴프리헨션, 예외 처리 등)
   - command_outputs 파싱 로직 구현
   - Status.PASS / Status.FAIL / Status.MANUAL 판단 로직 추가

3. 파일 수정
   - account_management.py: 7개 함수 구현 (U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10)
   - file_management.py: 2개 함수 구현 (U-18, U-27)

**검증 완료**:
- py_compile 성공: 문법 오류 없음
- import 테스트: 10개 함수 정상 import
- 실행 테스트: CheckResult 반환 확인 (Status 올바르게 설정)
- 패턴 확립: 나머지 63개 함수 구현 가능

**다음 단계**: 나머지 63개 함수 마이그레이션

**Phase 1 완료**: log_management.py (U-72, U-73 - 2개 함수) (2025-10-17)

**구현 내용**:
1. check_u72: 로그의 정기적 검토 및 보고
   - Legacy _72SCRIPT 로직 변환 (수동 점검 항목)
   - 항상 Status.MANUAL 반환
   - 한글 메시지: "로그 기록의 검토, 분석, 리포트 작성 및 보고 등이 정기적으로 이루어지는지 확인"
   - Severity: HIGH

2. check_u73: 로그 기록 정책 수립
   - Legacy _73SCRIPT 로직 변환 (수동 점검 항목)
   - 항상 Status.MANUAL 반환
   - 한글 메시지: "로그 기록 정책이 정책에 따라 설정되어 수립되어 있는지 확인"
   - Severity: LOW

**검증 완료**:
- py_compile 성공: 문법 오류 없음
- import 테스트: check_u72, check_u73 정상 import
- 실행 테스트: Status.MANUAL 반환 확인 (빈 입력, 샘플 입력)
- Git commit: 379e73f (1 file, 16 insertions, 24 deletions)

**진행 상황**: 12/73 함수 구현 완료 (16.4%)
- 완료: U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10 (계정관리 8개), U-18, U-27 (파일관리 2개), U-72, U-73 (로그관리 2개)
- 미완료: 61개

**다음 Phase**: patch_management.py (U-71 - 1개 함수)

**Phase 2 완료**: patch_management.py (U-71 - 1개 함수) (2025-10-17)

**구현 내용**:
1. check_u71: 최신 보안패치 및 벤더 권고사항 적용
   - Legacy _71SCRIPT 로직 변환 (수동 점검 항목)
   - 항상 Status.MANUAL 반환
   - 한글 메시지: "패치 적용 정책을 수립하여 주기적으로 패치를 관리하고 있는지 확인"
   - Severity: HIGH

**검증 완료**:
- py_compile 성공: 문법 오류 없음
- import 테스트: check_u71 정상 import
- 실행 테스트: Status.MANUAL 반환 확인 (빈 입력, 샘플 입력)
- Git commit: 19fc939 (1 file, 8 insertions, 12 deletions)

**진행 상황**: 13/73 함수 구현 완료 (17.8%)
- 완료: U-01, U-03, U-04, U-05, U-07, U-08, U-09, U-10 (계정관리 8개), U-18, U-27 (파일관리 2개), U-71 (패치관리 1개), U-72, U-73 (로그관리 2개)
- 미완료: 60개

**다음 Phase**: account_management.py 나머지 (U-02, U-06, U-11~U-15 - 7개 함수)

**Phase 3 완료**: account_management.py 나머지 (U-02, U-06, U-11~U-15 - 7개 함수) (2025-10-17)

**구현 내용**:
Batch 1 (3개):
1. check_u02: 패스워드 복잡성 설정
   - Legacy _2SCRIPT 로직: shadow 파일 해시화로 항상 PASS
   - Severity: HIGH

2. check_u06: root 계정 su 제한
   - Legacy _6SCRIPT 로직: wheel 그룹 + pam_wheel.so 2가지 패턴 체크
   - Severity: LOW

3. check_u11: 관리자 그룹에 최소한의 계정 포함
   - Legacy _11SCRIPT 로직: 그룹 멤버 추출 후 수동 점검 (MANUAL)
   - Severity: LOW

Batch 2 (3개):
4. check_u12: 계정이 존재하지 않는 GID 금지
   - Legacy _12SCRIPT 로직: 계정별 GID 목록 추출 후 수동 점검 (MANUAL)
   - Severity: LOW

5. check_u13: 동일한 UID 금지
   - Legacy _13SCRIPT 로직: UID 중복 체크, 중복 시 FAIL
   - Severity: MID

6. check_u14: 사용자 shell 점검
   - Legacy _14SCRIPT 로직: shell이 /sbin/nologin 아니면 FAIL
   - Severity: LOW

Batch 3 (1개):
7. check_u15: Session Timeout 설정
   - Legacy _15SCRIPT 로직: TIMEOUT >= 600 and TMOUT 존재 체크
   - Severity: LOW

**검증 완료**:
- py_compile 성공: 문법 오류 없음
- Batch 1-3 각각 import 및 실행 테스트 통과
- 총 15개 테스트 케이스 모두 통과
- Git commit: b90b9ca (1 file, 259 insertions, 88 deletions)

**진행 상황**: 20/73 함수 구현 완료 (27.4%)
- 완료 카테고리:
  * account_management.py: 15/15 (100%) ← 완료!
  * log_management.py: 2/2 (100%)
  * patch_management.py: 1/1 (100%)
- 진행 중 카테고리:
  * file_management.py: 2/20 (10%)
  * service_management.py: 0/35 (0%)

**다음 Phase**: file_management.py 나머지 (U-16, U-17, U-19~U-26, U-28~U-35 - 18개 함수)

---

### 3.3 Week 2: Core 모듈 구현

#### Day 6-8: Scanner 엔진

**작업 항목**:
- [ ] `src/core/scanner/base_scanner.py` 작성
  ```python
  class BaseScanner(ABC):
      @abstractmethod
      async def connect(self): pass
      @abstractmethod
      async def scan(self) -> ScanResult: pass
  ```
- [ ] `src/core/scanner/linux_scanner.py` 구현
  - SSH 연결 (AsyncSSH)
  - 명령어 실행
  - 결과 수집
- [ ] `src/core/scanner/rule_loader.py` 구현
  - YAML 파서
  - CheckItem 생성
- [ ] 첫 10개 규칙을 YAML로 변환
  ```yaml
  # config/rules/linux/account.yaml
  - id: U-01
    name: root 원격 로그인 제한
    # ...
  ```

**결과물**:
- ✅ BaseScanner, LinuxScanner 클래스
- ✅ 10개 규칙 YAML
- ✅ 단위 테스트 (test_scanner.py)

#### Day 9-10: Analyzer 엔진

**작업 항목**:
- [ ] `src/core/analyzer/result_parser.py` 구현
  - 명령어 결과 파싱
  - 정규식 기반 검증
- [ ] `src/core/analyzer/validator.py` 구현
  - 10개 규칙 validator 함수
  ```python
  def check_root_remote_login(outputs):
      # 검증 로직
  ```
- [ ] `src/core/analyzer/risk_calculator.py` 구현
  - 점수 계산 (0~100)
  - 위험도 분포

**결과물**:
- ✅ Analyzer 모듈 완성
- ✅ 10개 validator 함수

---

### 3.4 Week 3: GUI 기본 구조

#### Day 11-13: 메인 윈도우 + 뷰

**작업 항목**:
- [ ] `src/gui/main_window.py` 작성
  ```python
  class MainWindow(QMainWindow):
      def __init__(self):
          super().__init__()
          self.setup_ui()
  ```
- [ ] `src/gui/views/server_view.py` 구현
  - 서버 목록 (QListWidget)
  - 추가/편집/삭제 버튼
- [ ] `src/gui/views/scan_view.py` 구현
  - 스캔 시작 버튼
  - 진행률 표시 (QProgressBar)
- [ ] `src/gui/views/result_view.py` 구현
  - 트리 뷰 (QTreeWidget)
  - 점검 항목 계층 구조
  - 색상 코드 (Red/Yellow/Green)

**결과물**:
- ✅ 기본 GUI 레이아웃
- ✅ 3개 주요 뷰 완성

#### Day 14-15: 서버 관리 + DB

**작업 항목**:
- [ ] `src/infrastructure/database/models.py` 작성
  ```python
  class Server(Base):
      __tablename__ = "servers"
      id = Column(Integer, primary_key=True)
      # ...
  ```
- [ ] `src/infrastructure/database/repositories/server_repository.py`
  - CRUD 기능
- [ ] `src/gui/dialogs/server_dialog.py` 구현
  - 서버 추가/편집 폼
  - 연결 테스트 버튼
- [ ] 크레덴셜 저장 (keyring)

**결과물**:
- ✅ Server 모델 + Repository
- ✅ 서버 관리 UI

---

### 3.5 Week 4: 보고서 + 테스트 + 통합

#### Day 16-17: 보고서 생성

**작업 항목**:
- [ ] `src/infrastructure/reporting/excel_reporter.py` 구현
  - openpyxl로 Excel 생성
  - 기존 Linux_Check_3.py 로직 재사용
  - 차트 추가 (선택)
- [ ] 보고서 템플릿 설계
  - 요약 시트
  - 상세 시트 (73개 항목)
  - 통계 시트

**결과물**:
- ✅ Excel 보고서 생성 기능

#### Day 18-19: 통합 + 나머지 규칙

**작업 항목**:
- [ ] 나머지 63개 규칙 YAML 변환
  - 스크립트로 자동화 가능한 부분
  - 수동 검토 필요 항목
- [ ] 전체 워크플로우 통합 테스트
  - GUI에서 스캔 시작 → 보고서 생성까지
- [ ] 버그 수정 및 리팩토링

**결과물**:
- ✅ 73개 규칙 전부 마이그레이션
- ✅ End-to-End 동작 확인

#### Day 20: 테스트 + 문서화

**작업 항목**:
- [ ] 단위 테스트 작성
  - Scanner, Analyzer, Reporter
  - 목표: 커버리지 60%+
- [ ] 통합 테스트
  - 실제 서버 연결 테스트 (Docker)
- [ ] 사용자 매뉴얼 초안 (docs/USER_MANUAL.md)
- [ ] README.md 업데이트

**결과물**:
- ✅ 테스트 커버리지 60%+
- ✅ 문서화 완료

---

### 3.6 Phase 1 성공 기준

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **기능** | Linux 73개 규칙 100% 동작 | 실제 서버 점검 |
| **성능** | 73개 항목 스캔 5분 이내 | 타이머 측정 |
| **GUI** | 서버 관리, 스캔, 결과 조회 | 수동 테스트 |
| **보고서** | Excel 생성 정상 | 파일 확인 |
| **테스트** | 커버리지 60% 이상 | pytest-cov |
| **문서** | 사용자 매뉴얼 작성 | 검토 |

### 3.7 Phase 1 결과물

```
✅ 완성된 파일 목록:

src/
├── core/
│   ├── domain/ (엔티티)
│   ├── scanner/ (Linux 스캐너)
│   ├── analyzer/ (분석 엔진)
│   └── remediation/ (준비만)
├── gui/
│   ├── main_window.py
│   └── views/ (3개 뷰)
├── infrastructure/
│   ├── database/ (SQLite)
│   ├── network/ (SSH)
│   └── reporting/ (Excel)

config/rules/linux/ (73개 YAML)
tests/ (60%+ 커버리지)
docs/USER_MANUAL.md
```

---

## 4. Phase 2: macOS 확장 (1.5주)

### 4.1 목표

**"Unix 공통화 + macOS 50개 규칙 추가"**

- UnixScanner 추상 클래스 생성
- macOS 전용 10개 + Linux 재사용 40개
- macOS 환경에서 테스트

### 4.2 Week 5: Unix 추상화 + macOS 규칙

#### Day 21-22: UnixScanner 리팩토링

**작업 항목**:
- [ ] `src/core/scanner/unix_scanner.py` 생성
  ```python
  class UnixScanner(BaseScanner):
      """Linux + macOS 공통 로직"""
      def check_file_permission(self, path): pass
      def check_process(self, name): pass
  ```
- [ ] LinuxScanner 리팩토링
  - UnixScanner 상속
  - Linux 전용 로직만 남김
- [ ] 회귀 테스트 (Linux 기능 유지 확인)

**결과물**:
- ✅ UnixScanner 추상 클래스
- ✅ Linux 기능 유지

#### Day 23-25: macOS 규칙 작성

**작업 항목**:
- [ ] macOS 전용 10개 규칙 YAML 작성
  ```yaml
  # config/rules/macos/system.yaml
  - id: M-01
    name: System Integrity Protection
    # ...
  ```
  - M-01: SIP
  - M-02: Gatekeeper
  - M-03: FileVault
  - M-04: Firewall
  - M-05: 자동 업데이트
  - M-06~M-10: 네트워크, 공유 서비스

- [ ] Linux 재사용 40개 선택 및 수정
  - 계정 관리 (대부분 재사용 가능)
  - 파일 권한 (경로만 다름)
  - SSH 설정 (동일)

**결과물**:
- ✅ macOS 50개 규칙 YAML

---

### 4.3 Week 6 (절반): macOS Scanner + 테스트

#### Day 26-27: MacOSScanner 구현

**작업 항목**:
- [ ] `src/core/scanner/macos_scanner.py` 구현
  ```python
  class MacOSScanner(UnixScanner):
      async def check_sip_status(self): pass
      async def check_gatekeeper(self): pass
  ```
- [ ] macOS 전용 validator 함수 10개

**결과물**:
- ✅ MacOSScanner 클래스
- ✅ macOS validator

#### Day 28-30: 테스트 + 통합

**작업 항목**:
- [ ] macOS 환경 테스트
  - GitHub Actions (macos-latest)
  - 또는 로컬 Mac
- [ ] GUI 업데이트
  - 플랫폼 선택 (Linux/macOS)
  - macOS 규칙 표시
- [ ] 통합 테스트
- [ ] 문서 업데이트

**결과물**:
- ✅ macOS 50개 규칙 동작
- ✅ Linux + macOS 통합 GUI

---

### 4.4 Phase 2 성공 기준

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **macOS 규칙** | 50개 동작 | 실제 Mac 점검 |
| **Linux 유지** | 73개 유지 | 회귀 테스트 |
| **코드 재사용** | 70% 이상 | 코드 리뷰 |
| **테스트** | 커버리지 60%+ 유지 | pytest-cov |

---

## 5. Phase 3: 자동 수정 강화 (2주)

### 5.1 목표

**"원클릭 자동 수정 + 백업/롤백 시스템"**

- Remediation 엔진 구현
- 백업 매니저
- 롤백 매니저
- Dry-run 모드
- GUI 미리보기

### 5.2 Week 7: Remediation 엔진

#### Day 31-33: 기본 구조

**작업 항목**:
- [ ] `src/core/remediation/base_remediator.py` 구현
  ```python
  class BaseRemediator(ABC):
      async def remediate(self, items): pass
      async def _execute_fix(self, item): pass
  ```
- [ ] `src/core/remediation/unix_remediator.py`
  - Linux + macOS 공통
  - 파일 수정, 권한 변경 등
- [ ] `src/core/remediation/linux_remediator.py`
  - systemd 서비스 관리
- [ ] `src/core/remediation/macos_remediator.py`
  - defaults 명령어
  - launchd

**결과물**:
- ✅ Remediation 엔진 기본 구조

#### Day 34-35: 백업 시스템

**작업 항목**:
- [ ] `src/core/remediation/backup_manager.py` 구현
  ```python
  class BackupManager:
      async def backup(self, files): pass
      async def rollback(self, backup_id): pass
  ```
- [ ] 백업 저장 위치: `data/backups/`
- [ ] 백업 메타데이터 (JSON)
  ```json
  {
    "backup_id": "backup_20250117_153000",
    "timestamp": "2025-01-17T15:30:00",
    "files": [
      {"original": "/etc/passwd", "backup": "passwd.bak"}
    ]
  }
  ```

**결과물**:
- ✅ 백업/롤백 시스템

---

### 5.3 Week 8: 안전 장치 + GUI

#### Day 36-37: Dry-run + 검증

**작업 항목**:
- [ ] Dry-run 모드 구현
  - 실제 수정 안 함
  - 시뮬레이션만
  - 로그 기록
- [ ] 수정 후 검증
  ```python
  async def verify_fix(self, item):
      # 다시 점검해서 PASS인지 확인
  ```
- [ ] 실패 시 자동 롤백

**결과물**:
- ✅ Dry-run 모드
- ✅ 자동 롤백

#### Day 38-40: GUI 미리보기

**작업 항목**:
- [ ] `src/gui/dialogs/remediation_dialog.py` 구현
  - 수정할 항목 목록
  - 변경 사항 미리보기
  ```
  ┌─────────────────────────────────┐
  │ 자동 수정 미리보기               │
  ├─────────────────────────────────┤
  │ ☑ U-01: root 원격 로그인 제한   │
  │   변경: /etc/pam.d/login 수정   │
  │   백업: Yes                     │
  │                                 │
  │ ☑ U-02: 패스워드 복잡도         │
  │   변경: /etc/pam.d/system-auth  │
  │                                 │
  │ [Dry-run] [실제 수정]  [취소]   │
  └─────────────────────────────────┘
  ```
- [ ] 배치 수정 기능
- [ ] 진행률 표시

**결과물**:
- ✅ 미리보기 UI
- ✅ 배치 수정

---

### 5.4 Phase 3 성공 기준

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **자동 수정** | 90% 성공률 | 테스트 서버에서 검증 |
| **롤백** | 100% 성공 | 모든 항목 롤백 테스트 |
| **백업** | 무결성 보장 | 체크섬 검증 |
| **GUI** | 직관적 미리보기 | 사용자 테스트 |

---

## 6. Phase 4: Windows 지원 (3주)

### 6.1 목표

**"Windows 플랫폼 추가 (50~70개 규칙)"**

- WinRM 연결
- PowerShell 명령어
- 레지스트리 점검
- Windows Remediation

### 6.2 Week 9: WinRM 연결

#### Day 41-43: 네트워크 모듈

**작업 항목**:
- [ ] `src/infrastructure/network/winrm_client.py` 구현
  ```python
  class WinRMClient:
      def connect(self): pass
      def execute_powershell(self, script): pass
  ```
- [ ] 인증 테스트 (NTLM, Kerberos)
- [ ] PowerShell 래퍼 함수
  ```python
  def get_registry_value(self, key, name):
      script = f"Get-ItemProperty -Path {key} -Name {name}"
      return self.execute_powershell(script)
  ```

**결과물**:
- ✅ WinRM 연결 모듈

#### Day 44-45: WindowsScanner 기본

**작업 항목**:
- [ ] `src/core/scanner/windows_scanner.py` 구현
  ```python
  class WindowsScanner(BaseScanner):
      async def check_registry(self, key, value): pass
      async def check_service(self, name): pass
  ```
- [ ] 첫 10개 Windows 규칙 YAML
  - W-01: Administrator 원격 로그인
  - W-02: 패스워드 정책
  - W-03: 방화벽 상태
  - 등등

**결과물**:
- ✅ WindowsScanner 기본 구조
- ✅ 10개 규칙 동작

---

### 6.3 Week 10: Windows 규칙 작성

#### Day 46-50: 규칙 작성 집중

**작업 항목**:
- [ ] CIS Benchmark for Windows 참조
- [ ] 50개 규칙 YAML 작성
  - 계정 정책 (15개)
  - 레지스트리 (20개)
  - 서비스/방화벽 (10개)
  - 패치 관리 (5개)
- [ ] Validator 함수 작성
  ```python
  def check_windows_firewall(outputs):
      # PowerShell 결과 파싱
  ```

**결과물**:
- ✅ Windows 50개 규칙

---

### 6.4 Week 11: Windows Remediation + 통합

#### Day 51-53: WindowsRemediator

**작업 항목**:
- [ ] `src/core/remediation/windows_remediator.py` 구현
  - 레지스트리 수정
  - 그룹 정책 변경
  - 서비스 관리
- [ ] 백업/롤백 (Windows 레지스트리)
- [ ] Dry-run 모드

**결과물**:
- ✅ Windows 자동 수정

#### Day 54-55: GUI 통합 + 테스트

**작업 항목**:
- [ ] GUI에서 Windows 플랫폼 선택
- [ ] Windows 환경 테스트
  - Azure Pipelines 또는 로컬 VM
- [ ] 통합 테스트 (3-OS)
- [ ] 문서 업데이트

**결과물**:
- ✅ 3-OS 완전 통합

---

### 6.5 Phase 4 성공 기준

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **Windows 규칙** | 50개 동작 | 실제 Windows 점검 |
| **3-OS 통합** | GUI에서 모두 선택 가능 | 수동 테스트 |
| **Windows 자동 수정** | 80% 성공률 | 테스트 VM |

---

## 7. Phase 5: 고급 기능 (2주)

### 7.1 목표

**"이력 관리 + 트렌드 분석 + UX 개선"**

- SQLite 이력 DB
- 대시보드 (그래프, 차트)
- PDF 보고서
- 스케줄러
- 교육 콘텐츠
- 다크 모드
- 다국어 (한/영)

### 7.2 Week 12: 이력 관리 + 대시보드

#### Day 56-58: 이력 DB

**작업 항목**:
- [ ] `src/infrastructure/database/models.py` 확장
  - Scan, CheckResult 모델 (이미 있음)
  - 이력 조회 쿼리 최적화
- [ ] `src/gui/views/history_view.py` 구현
  - 과거 스캔 목록 (QTableView)
  - 날짜 필터
  - 상세 조회
- [ ] 비교 기능
  ```python
  def compare_scans(scan_id_1, scan_id_2):
      # 두 스캔 결과 비교
      # 개선/악화 항목 표시
  ```

**결과물**:
- ✅ 이력 관리 기능

#### Day 59-60: 대시보드

**작업 항목**:
- [ ] `src/gui/views/dashboard_view.py` 구현
  - 전체 점수 (큰 숫자)
  - 위험도 분포 (파이 차트)
    ```python
    from PySide6.QtCharts import QChart, QPieSeries
    ```
  - 트렌드 그래프 (라인 차트)
  - 최근 스캔 목록
- [ ] `src/core/analyzer/trend_analyzer.py` 구현
  ```python
  def analyze_trend(server_id, days=30):
      # 30일간 점수 변화
  ```

**결과물**:
- ✅ 대시보드 (그래프, 통계)

---

### 7.3 Week 13: UX 개선 + 마무리

#### Day 61-63: 고급 기능

**작업 항목**:
- [ ] PDF 보고서 생성
  ```python
  # src/infrastructure/reporting/pdf_reporter.py
  from reportlab.lib.pagesizes import letter
  ```
- [ ] 스케줄러 (정기 점검)
  ```python
  from apscheduler.schedulers.background import BackgroundScheduler

  scheduler = BackgroundScheduler()
  scheduler.add_job(scan_server, 'cron', hour=2)  # 매일 새벽 2시
  ```
- [ ] 교육 콘텐츠 UI
  - 각 취약점 클릭 시 설명 표시
  - 공격 시나리오
  - 수정 가이드

**결과물**:
- ✅ PDF 보고서
- ✅ 스케줄러
- ✅ 교육 콘텐츠

#### Day 64-65: UX 개선

**작업 항목**:
- [ ] 다크 모드 (Qt 스타일시트)
  ```python
  app.setStyleSheet(load_stylesheet("dark.qss"))
  ```
- [ ] 다국어 지원 (Qt Linguist)
  - 한국어 (기본)
  - 영어
- [ ] 온보딩 튜토리얼
  - 첫 실행 시 가이드
- [ ] 설정 UI
  - 테마 선택
  - 언어 선택
  - 로그 레벨

**결과물**:
- ✅ 다크 모드
- ✅ 다국어

#### Day 66: 최종 테스트 + 빌드

**작업 항목**:
- [ ] 전체 통합 테스트
- [ ] UAT (User Acceptance Test)
- [ ] PyInstaller로 빌드
  ```bash
  pyinstaller --onefile --windowed src/gui/app.py
  ```
- [ ] 실행 파일 테스트 (Windows, macOS, Linux)
- [ ] 문서 최종 검토
- [ ] 릴리스 노트 작성

**결과물**:
- ✅ 배포 패키지 (.exe, .app, .deb)

---

### 7.4 Phase 5 성공 기준

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **이력** | 과거 조회 가능 | 30일 데이터 테스트 |
| **대시보드** | 그래프 표시 | 수동 확인 |
| **PDF** | 보고서 생성 | 샘플 확인 |
| **빌드** | 3-OS 실행 파일 | 각 OS 테스트 |

---

## 8. 마일스톤

### 8.1 마일스톤 정의

| ID | 이름 | 주차 | 목표 | 결과물 | 검증 |
|----|------|------|------|--------|------|
| **M1** | Linux MVP | Week 4 | Linux 기본 기능 완성 | - 73개 규칙 동작<br>- GUI 기본<br>- Excel 보고서 | - 실제 서버 점검<br>- 사용자 테스트 |
| **M2** | macOS 통합 | Week 6 | Unix 플랫폼 통합 | - macOS 50개 규칙<br>- UnixScanner | - Mac 환경 테스트<br>- 베타 테스트 |
| **M3** | 자동 수정 | Week 8 | 핵심 기능 완성 | - Remediation 엔진<br>- 백업/롤백 | - 안전성 검증<br>- Dry-run 테스트 |
| **M4** | Windows 통합 | Week 11 | 3-OS 완성 | - Windows 50개 규칙<br>- 3-OS GUI | - Windows 테스트<br>- 통합 테스트 |
| **M5** | 출시 준비 | Week 13 | 완전한 제품 | - 모든 기능 완성<br>- 배포 패키지 | - UAT<br>- 릴리스 |

### 8.2 마일스톤 체크리스트

#### M1: Linux MVP (Week 4)

**기능**:
- [ ] Linux 73개 규칙 100% 동작
- [ ] GUI 서버 관리
- [ ] GUI 스캔 실행
- [ ] GUI 결과 조회
- [ ] Excel 보고서 생성

**품질**:
- [ ] 단위 테스트 커버리지 60%+
- [ ] 통합 테스트 통과
- [ ] 문서화 완료 (사용자 매뉴얼)

**검증**:
- [ ] 실제 Linux 서버에서 점검 성공
- [ ] 3명 베타 테스터 피드백

#### M2: macOS 통합 (Week 6)

**기능**:
- [ ] macOS 50개 규칙 동작
- [ ] Linux 기능 유지 (회귀 없음)
- [ ] GUI에서 플랫폼 선택

**품질**:
- [ ] 테스트 커버리지 60%+ 유지
- [ ] macOS 환경 CI/CD (GitHub Actions)

**검증**:
- [ ] 실제 Mac에서 점검 성공

#### M3: 자동 수정 (Week 8)

**기능**:
- [ ] Linux + macOS 자동 수정
- [ ] 백업 자동 생성
- [ ] 롤백 기능
- [ ] Dry-run 모드
- [ ] GUI 미리보기

**품질**:
- [ ] 자동 수정 성공률 90%+
- [ ] 롤백 성공률 100%
- [ ] 안전성 테스트 통과

**검증**:
- [ ] 테스트 서버에서 100회 수정 테스트

#### M4: Windows 통합 (Week 11)

**기능**:
- [ ] Windows 50개 규칙 동작
- [ ] Windows 자동 수정 (기본)
- [ ] 3-OS 통합 GUI

**품질**:
- [ ] Windows 테스트 환경 구축
- [ ] 3-OS 통합 테스트 통과

**검증**:
- [ ] Windows 10/11에서 점검 성공

#### M5: 출시 준비 (Week 13)

**기능**:
- [ ] 이력 관리
- [ ] 대시보드
- [ ] PDF 보고서
- [ ] 스케줄러
- [ ] 교육 콘텐츠
- [ ] 다크 모드
- [ ] 다국어

**품질**:
- [ ] UAT 통과
- [ ] 성능 테스트 (100개 서버)
- [ ] 보안 감사

**검증**:
- [ ] 배포 패키지 3-OS 테스트
- [ ] 10명 사용자 테스트

---

## 9. 리스크 관리

### 9.1 리스크 목록

| ID | 리스크 | 확률 | 영향 | 완화 전략 | 비상 계획 |
|----|--------|------|------|----------|----------|
| **R1** | Python 2→3 마이그레이션 실패 | 중 | 높음 | - 점진적 마이그레이션<br>- 10개씩 테스트 | - 외부 도움 요청<br>- 일정 연장 (1주) |
| **R2** | macOS SIP 제약 | 높음 | 중 | - 수정 불가 항목 명시<br>- 사용자 안내 | - 수동 수정 가이드 제공 |
| **R3** | Windows 테스트 환경 부족 | 중 | 중 | - Azure Pipelines 활용<br>- GitHub Actions | - Windows VM 구매 |
| **R4** | 자동 수정 시 시스템 손상 | 낮음 | 높음 | - 백업 강제<br>- Dry-run 기본 | - 롤백 기능 강화<br>- 보험 정책 |
| **R5** | GUI 개발 지연 | 중 | 낮음 | - MVP는 간단한 UI<br>- 점진적 개선 | - CLI 먼저 완성 |
| **R6** | 규칙 작성 지연 | 중 | 중 | - 우선순위 규칙만<br>- 자동화 스크립트 | - 50개만 먼저 |
| **R7** | 성능 문제 (대규모) | 중 | 중 | - 비동기 처리<br>- 캐싱 | - 연결 풀<br>- 병렬 처리 |

### 9.2 리스크 모니터링

**주간 리뷰**:
- 매주 금요일 리스크 상태 점검
- 새로운 리스크 식별
- 완화 전략 효과 평가

**에스컬레이션**:
- 확률 또는 영향이 "높음"으로 증가 시 즉시 보고
- 비상 계획 활성화 기준 명확화

---

## 10. 품질 보증

### 10.1 테스트 전략

**단위 테스트**:
- 목표: 커버리지 60% 이상
- 도구: pytest, pytest-cov
- 주기: 매일 (CI/CD)

**통합 테스트**:
- 목표: 주요 워크플로우 100% 커버
- 도구: pytest, pytest-asyncio
- 주기: 매 PR

**E2E 테스트**:
- 목표: 실제 환경 점검 성공
- 환경: Docker (Linux), VM (Windows), GitHub Actions (macOS)
- 주기: 주간

**성능 테스트**:
- 목표: 100개 서버 동시 점검
- 도구: locust (선택)
- 주기: Phase 5

### 10.2 코드 품질

**린팅**:
- 도구: ruff, black
- 주기: 커밋 전 (pre-commit hook)

**타입 체킹**:
- 도구: mypy
- 목표: 타입 커버리지 80%+

**코드 리뷰**:
- 모든 PR은 리뷰 필수
- 체크리스트:
  - [ ] 테스트 추가
  - [ ] 문서 업데이트
  - [ ] 린트 통과
  - [ ] 타입 체킹 통과

### 10.3 문서화

**항상 업데이트**:
- README.md
- API 문서 (docstring)
- 사용자 매뉴얼
- 아키텍처 문서

**문서 리뷰**:
- 매 Phase 종료 시 전체 문서 검토

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-10-17 | 1.0 | 초안 작성 | Claude |

---

**문서 끝**