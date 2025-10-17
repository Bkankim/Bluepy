# 도메인 모델 설계

**작성일**: 2025-10-17
**목적**: BluePy 2.0의 핵심 도메인 모델 정의

---

## 1. 개요

Clean Architecture의 Domain Layer에 해당하는 순수한 비즈니스 로직 모델을 정의합니다.

**설계 원칙:**
- 외부 의존성 없음 (표준 라이브러리 + pydantic만 사용)
- 불변성 지향 (immutable)
- Type Safety (완전한 type hints)
- Validation (pydantic 활용)

---

## 2. Status Enum

검증 결과 상태를 나타냅니다.

```python
from enum import Enum

class Status(str, Enum):
    """점검 결과 상태"""
    PASS = "PASS"      # 양호: 취약점 없음
    FAIL = "FAIL"      # 취약: 조치 필요
    MANUAL = "MANUAL"  # 수동 점검: 자동 판단 불가
```

**Legacy 매핑:**
- `_SETOK()` → `Status.PASS`
- `_SETBAD()` → `Status.FAIL`
- `_SETHOLD()` → `Status.MANUAL`

---

## 3. Severity Enum

취약점 심각도를 나타냅니다.

```python
from enum import Enum

class Severity(str, Enum):
    """취약점 심각도"""
    HIGH = "high"  # 상: 즉시 조치 필요
    MID = "mid"    # 중: 조치 권장
    LOW = "low"    # 하: 참고
```

**Legacy 매핑:**
- `_SETHIGH()` → `Severity.HIGH`
- `_SETMID()` → `Severity.MID`
- `_SETLOW()` → `Severity.LOW`

---

## 4. CheckResult

단일 점검 항목의 검증 결과를 나타냅니다.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class CheckResult:
    """점검 결과"""
    status: Status
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def is_passed(self) -> bool:
        """양호 여부"""
        return self.status == Status.PASS

    def is_failed(self) -> bool:
        """취약 여부"""
        return self.status == Status.FAIL

    def is_manual(self) -> bool:
        """수동 점검 필요 여부"""
        return self.status == Status.MANUAL
```

**필드 설명:**
- `status`: 검증 결과 (PASS/FAIL/MANUAL)
- `message`: 결과 설명 (예: "root 원격 로그인이 제한되어 있습니다")
- `details`: 추가 정보 (예: {"found_files": ["/etc/passwd"], "permission": "rw-r--r--"})
- `timestamp`: 검증 시간 (자동 생성)

**사용 예시:**
```python
# 양호
result = CheckResult(
    status=Status.PASS,
    message="Shadow 패스워드를 사용하고 있습니다"
)

# 취약
result = CheckResult(
    status=Status.FAIL,
    message="패스워드 최소 길이가 8자 미만입니다",
    details={"current_length": 6, "required_length": 8}
)

# 수동 점검
result = CheckResult(
    status=Status.MANUAL,
    message="불필요한 계정 존재 여부를 수동으로 확인하세요",
    details={"accounts": ["user1", "user2", "user3"]}
)
```

---

## 5. RemediationInfo

자동 수정 정보를 나타냅니다. (Phase 3에서 구현)

```python
from pydantic import BaseModel
from typing import List, Optional

class RemediationInfo(BaseModel):
    """자동 수정 정보"""
    auto: bool = False
    backup_files: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    manual_steps: Optional[List[str]] = None

    class Config:
        frozen = True  # immutable
```

**필드 설명:**
- `auto`: 자동 수정 가능 여부
- `backup_files`: 백업할 파일 목록
- `commands`: 실행할 bash 명령어
- `manual_steps`: 수동 수정 단계

---

## 6. RuleMetadata

점검 규칙의 메타데이터를 나타냅니다.

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class RuleMetadata(BaseModel):
    """점검 규칙 메타데이터"""
    id: str = Field(..., pattern=r"^[UWM]-\d{2}$")
    name: str = Field(..., min_length=1, max_length=200)
    category: str
    severity: Severity
    kisa_standard: str
    description: str
    commands: List[str] = Field(..., min_items=1)
    validator: str = Field(..., pattern=r"^validators\.(linux|macos|windows)\.check_[a-z]\d{2}_\w+$")
    expected_result: Optional[str] = None
    remediation: Optional[RemediationInfo] = None

    class Config:
        frozen = True  # immutable
```

**필드 설명:**
- `id`: 규칙 ID (예: "U-01" for Unix/Linux, "W-01" for Windows, "M-01" for macOS)
- `name`: 규칙 이름 (예: "root 원격 로그인 제한")
- `category`: 카테고리 (예: "계정관리", "파일/디렉토리 관리", "서비스 관리")
- `severity`: 심각도
- `kisa_standard`: KISA 기준 코드 (예: "U-01")
- `description`: 상세 설명
- `commands`: 실행할 bash 명령어 목록
- `validator`: validator 함수 경로 (예: "validators.linux.check_u01_root_remote_login")
- `expected_result`: 기대 결과 설명
- `remediation`: 자동 수정 정보 (Optional, Phase 3)

**Validation:**
- `id`: 정규식 패턴 매칭 (U-01 ~ U-73, W-01 ~ W-50, M-01 ~ M-50)
- `name`: 1~200자
- `commands`: 최소 1개 이상
- `validator`: 함수명 패턴 검증

**사용 예시:**
```python
rule = RuleMetadata(
    id="U-01",
    name="root 계정 원격 로그인 제한",
    category="계정관리",
    severity=Severity.HIGH,
    kisa_standard="U-01",
    description="root 계정의 원격 로그인을 제한하여 시스템 보안을 강화합니다.",
    commands=[
        "cat /etc/pam.d/login",
        "cat /etc/securetty"
    ],
    validator="validators.linux.check_u01_root_remote_login",
    expected_result="pam_securetty.so가 설정되어 있어야 함",
    remediation=RemediationInfo(
        auto=False,
        manual_steps=[
            "/etc/pam.d/login 파일 편집",
            "auth required pam_securetty.so 추가"
        ]
    )
)
```

---

## 7. 카테고리 분류

KISA 기준에 따른 카테고리:

| 카테고리 | KISA 코드 범위 | 설명 |
|---------|---------------|------|
| 계정관리 | U-01 ~ U-15 | 계정, 패스워드, 세션 관리 |
| 파일/디렉토리 관리 | U-16 ~ U-26 | 파일 권한, 소유자 설정 |
| 서비스 관리 | U-27 ~ U-43 | 불필요한 서비스 제거, 설정 |
| 패치 관리 | U-44 ~ U-51 | 보안 패치, 버전 관리 |
| 로그 관리 | U-52 ~ U-73 | 로그 설정, 검토 정책 |

---

## 8. 데이터 흐름

```
YAML 규칙 파일 (config/rules/linux/U-01.yaml)
    ↓
RuleMetadata 파싱
    ↓
Scanner: commands 실행 → 결과 수집
    ↓
Analyzer: validator 함수 호출
    ↓
CheckResult 반환
    ↓
Reporter: 보고서 생성
```

---

## 9. 타입 안전성

모든 모델은 완전한 type hints를 제공합니다:

```python
from typing import List, Optional, Dict, Any

def validate_rule(rule: RuleMetadata, outputs: Dict[str, str]) -> CheckResult:
    """타입 안전한 검증 함수"""
    pass
```

---

## 10. 다음 단계

- **Task 1.4**: `src/core/domain/models.py` 구현
- **Task 1.5**: YAML 스키마 설계 (RuleMetadata 기반)
- **Task 2.0**: 마이그레이션 스크립트에서 RuleMetadata 활용

---

**문서 끝**
