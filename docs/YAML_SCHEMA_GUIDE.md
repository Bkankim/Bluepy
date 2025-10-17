# YAML 규칙 스키마 가이드

**작성일**: 2025-10-17
**목적**: BluePy 2.0 YAML 규칙 파일 작성 가이드

---

## 1. 개요

BluePy 2.0은 YAML 형식의 규칙 파일로 보안 점검 항목을 정의합니다.
각 YAML 파일은 하나의 점검 항목을 나타내며, `RuleMetadata` 모델과 1:1 매핑됩니다.

**장점:**
- 선언적 설정: 코드 수정 없이 규칙 추가/변경 가능
- 가독성: 비개발자도 이해 가능한 형식
- 검증: pydantic을 통한 자동 스키마 검증
- 확장성: 새로운 플랫폼/규칙 쉽게 추가

---

## 2. 파일 위치 및 명명 규칙

### 디렉토리 구조

```
config/rules/
├── linux/
│   ├── U-01.yaml  # Unix/Linux 규칙
│   ├── U-02.yaml
│   └── ...
├── windows/
│   ├── W-01.yaml  # Windows 규칙
│   ├── W-02.yaml
│   └── ...
└── macos/
    ├── M-01.yaml  # macOS 규칙
    ├── M-02.yaml
    └── ...
```

### 명명 규칙

- **Linux**: `U-{번호:02d}.yaml` (예: U-01, U-02, ..., U-73)
- **Windows**: `W-{번호:02d}.yaml` (예: W-01, W-02, ..., W-50)
- **macOS**: `M-{번호:02d}.yaml` (예: M-01, M-02, ..., M-50)

---

## 3. 스키마 정의

### 필수 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `id` | string | 규칙 ID (패턴: `^[UWM]-\d{2}$`) | `"U-01"` |
| `name` | string | 규칙 이름 (1~200자) | `"root 계정 원격 로그인 제한"` |
| `category` | string | 카테고리 | `"계정관리"` |
| `severity` | string | 심각도 (`"high"`, `"mid"`, `"low"`) | `"high"` |
| `kisa_standard` | string | KISA 기준 코드 | `"U-01"` |
| `description` | string | 상세 설명 (multi-line 권장) | `"root 계정의 원격 로그인을 제한..."` |
| `commands` | list[string] | 실행할 bash 명령어 (최소 1개) | `["cat /etc/passwd"]` |
| `validator` | string | validator 함수 경로 | `"validators.linux.check_u01_root_remote_login"` |

### 선택 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `expected_result` | string | 기대 결과 설명 | `"pam_securetty.so가 설정되어 있어야 함"` |
| `remediation` | object | 자동 수정 정보 (아래 참조) | - |

### remediation 객체 (선택)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `auto` | boolean | 자동 수정 가능 여부 | `false` |
| `backup_files` | list[string] | 백업할 파일 목록 | `["/etc/pam.d/login"]` |
| `commands` | list[string] | 실행할 수정 명령어 | `["chown root:root /tmp/file"]` |
| `manual_steps` | list[string] | 수동 수정 단계 | `["파일 편집", "재부팅"]` |

---

## 4. 카테고리 분류

KISA 기준에 따른 카테고리:

| 카테고리 | KISA 코드 범위 | 설명 |
|---------|---------------|------|
| 계정관리 | U-01 ~ U-15 | 계정, 패스워드, 세션 관리 |
| 파일 및 디렉토리 관리 | U-16 ~ U-26 | 파일 권한, 소유자 설정 |
| 서비스 관리 | U-27 ~ U-43 | 불필요한 서비스 제거, 설정 |
| 패치 관리 | U-44 ~ U-51 | 보안 패치, 버전 관리 |
| 로그 관리 | U-52 ~ U-73 | 로그 설정, 검토 정책 |

---

## 5. validator 함수 경로 규칙

validator 필드는 다음 패턴을 따라야 합니다:

**패턴**: `validators.(linux|macos|windows).check_[a-z]\d{2}_\w+`

**예시:**
- `validators.linux.check_u01_root_remote_login`
- `validators.linux.check_u04_shadow_password`
- `validators.windows.check_w01_password_policy`
- `validators.macos.check_m01_firewall_enabled`

**매핑 규칙:**
- `check_u{번호:02d}_{snake_case_name}`
- KISA 코드 U-01 → `check_u01_`
- 이름은 snake_case (소문자, 언더스코어)

---

## 6. YAML 작성 예시

### 예시 1: 간단한 규칙 (U-04)

```yaml
# U-04: 패스워드 파일 보호
id: "U-04"
name: "패스워드 파일 보호"
category: "계정관리"
severity: "high"
kisa_standard: "U-04"

description: |
  Shadow 패스워드를 사용하여 /etc/passwd 파일에
  암호화된 패스워드가 저장되지 않도록 합니다.

commands:
  - "grep '^root:' /etc/shadow"

validator: "validators.linux.check_u04_shadow_password"

expected_result: |
  root 계정의 두 번째 필드가 'x'여야 함
```

### 예시 2: 복잡한 규칙 (U-01)

```yaml
# U-01: root 계정 원격 로그인 제한
id: "U-01"
name: "root 계정 원격 로그인 제한"
category: "계정관리"
severity: "high"
kisa_standard: "U-01"

description: |
  root 계정의 원격 로그인을 제한하여 시스템 보안을 강화합니다.
  PAM(Pluggable Authentication Modules) 설정을 통해 제어합니다.

commands:
  - "cat /etc/pam.d/login"
  - "cat /etc/securetty"

validator: "validators.linux.check_u01_root_remote_login"

expected_result: |
  /etc/pam.d/login에 pam_securetty.so가 설정되어 있고,
  /etc/securetty에 pts 터미널이 포함되지 않아야 함

remediation:
  auto: false
  manual_steps:
    - "/etc/pam.d/login 파일에 'auth required pam_securetty.so' 추가"
    - "/etc/securetty 파일에서 pts/* 항목 제거"
    - "설정 후 SSH 접속 테스트"
```

### 예시 3: 자동 수정 가능 (U-18)

```yaml
# U-18: 소유자 없는 파일 관리
id: "U-18"
name: "소유자 없는 파일 및 디렉토리 관리"
category: "파일 및 디렉토리 관리"
severity: "high"
kisa_standard: "U-18"

description: |
  소유자가 없는 파일이나 디렉토리가 존재하는지 점검합니다.

commands:
  - "find / -nouser -o -nogroup 2>/dev/null | head -20"

validator: "validators.linux.check_u18_orphan_files"

expected_result: |
  소유자 없는 파일이 없어야 함

remediation:
  auto: true
  backup_files: []
  commands:
    - "chown root:root <file>"
  manual_steps:
    - "소유자 없는 파일 목록 확인"
    - "적절한 소유자 할당"
```

---

## 7. YAML 작성 팁

### Multi-line 문자열

긴 설명은 `|` (literal block scalar) 사용:

```yaml
description: |
  이것은 여러 줄에 걸친
  긴 설명입니다.
  줄바꿈이 보존됩니다.
```

### 주석

```yaml
# 한 줄 주석
id: "U-01"  # 인라인 주석도 가능
```

### 리스트

```yaml
commands:
  - "command 1"
  - "command 2"
  - "command 3"
```

### 인코딩

- **반드시 UTF-8 인코딩** 사용
- 한글 주석/설명 사용 가능

---

## 8. 검증 방법

### Python으로 검증

```python
import yaml
from src.core.domain.models import RuleMetadata

# YAML 파일 읽기
with open('config/rules/linux/U-01.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# pydantic으로 검증
rule = RuleMetadata(**data)
print(f"검증 성공: {rule.id} - {rule.name}")
```

### 명령줄 검증 스크립트 (개발 예정)

```bash
# 전체 규칙 검증
python scripts/validate_rules.py

# 특정 규칙 검증
python scripts/validate_rules.py config/rules/linux/U-01.yaml
```

---

## 9. 새 규칙 추가 워크플로우

1. **KISA 코드 확인**: 추가할 항목의 KISA 코드 확인 (예: U-05)
2. **YAML 파일 생성**: `config/rules/linux/U-05.yaml` 생성
3. **스키마 작성**: 위 예시를 참고하여 모든 필수 필드 작성
4. **Validator 함수 작성**: `src/core/analyzer/validators/linux.py`에 함수 추가
5. **검증**: Python으로 YAML 파싱 및 pydantic 검증
6. **테스트**: 실제 시스템에서 점검 명령어 실행 및 결과 확인

---

## 10. 문제 해결

### ValidationError: Field required

필수 필드가 누락되었습니다. 위 "필수 필드" 섹션 참조.

### ValidationError: String should match pattern

- `id`: U-01, W-01, M-01 형식 확인
- `validator`: 패턴 확인 (예: `validators.linux.check_u01_name`)

### YAMLError: mapping values are not allowed

들여쓰기 오류입니다. YAML은 공백(space)을 사용하며, 탭(tab) 사용 금지.

### UnicodeDecodeError

파일 인코딩을 UTF-8로 저장하세요.

---

## 11. 참고 자료

- **RuleMetadata 모델**: `src/core/domain/models.py`
- **도메인 모델 설계**: `docs/DOMAIN_MODEL_DESIGN.md`
- **예시 YAML 파일**: `config/rules/linux/U-{01,04,18}.yaml`
- **YAML 공식 문서**: https://yaml.org/spec/

---

**문서 끝**
