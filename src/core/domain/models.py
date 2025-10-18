"""도메인 모델 정의

BluePy 2.0의 핵심 도메인 모델.
Clean Architecture의 Domain Layer에 해당하며,
외부 의존성 없는 순수한 비즈니스 로직을 포함합니다.

설계 원칙:
- 외부 의존성 없음 (표준 라이브러리 + pydantic만)
- 불변성 지향 (immutable)
- Type Safety (완전한 type hints)
- Validation (pydantic 활용)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Status(str, Enum):
    """점검 결과 상태

    Legacy 매핑:
    - _SETOK() → PASS
    - _SETBAD() → FAIL
    - _SETHOLD() → MANUAL
    """

    PASS = "PASS"  # 양호: 취약점 없음
    FAIL = "FAIL"  # 취약: 조치 필요
    MANUAL = "MANUAL"  # 수동 점검: 자동 판단 불가


class Severity(str, Enum):
    """취약점 심각도

    Legacy 매핑:
    - _SETHIGH() → HIGH
    - _SETMID() → MID
    - _SETLOW() → LOW
    """

    HIGH = "high"  # 상: 즉시 조치 필요
    MID = "mid"  # 중: 조치 권장
    LOW = "low"  # 하: 참고


@dataclass
class CheckResult:
    """점검 결과

    단일 점검 항목의 검증 결과를 나타냅니다.

    Attributes:
        status: 검증 결과 상태 (PASS/FAIL/MANUAL)
        message: 결과 설명 메시지
        details: 추가 정보 (파일 경로, 권한 등)
        timestamp: 검증 수행 시각 (자동 생성)

    Examples:
        >>> # 양호
        >>> result = CheckResult(
        ...     status=Status.PASS,
        ...     message="Shadow 패스워드를 사용하고 있습니다"
        ... )

        >>> # 취약
        >>> result = CheckResult(
        ...     status=Status.FAIL,
        ...     message="패스워드 최소 길이가 8자 미만입니다",
        ...     details={"current_length": 6, "required_length": 8}
        ... )

        >>> # 수동 점검
        >>> result = CheckResult(
        ...     status=Status.MANUAL,
        ...     message="불필요한 계정 존재 여부를 수동으로 확인하세요",
        ...     details={"accounts": ["user1", "user2", "user3"]}
        ... )
    """

    status: Status
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def is_passed(self) -> bool:
        """양호 여부 반환"""
        return self.status == Status.PASS

    def is_failed(self) -> bool:
        """취약 여부 반환"""
        return self.status == Status.FAIL

    def is_manual(self) -> bool:
        """수동 점검 필요 여부 반환"""
        return self.status == Status.MANUAL


class RemediationInfo(BaseModel):
    """자동 수정 정보

    취약점에 대한 자동/수동 수정 방법을 정의합니다.
    Phase 3에서 자동 수정 기능 구현 시 사용됩니다.

    Attributes:
        auto: 자동 수정 가능 여부
        backup_files: 수정 전 백업할 파일 목록
        commands: 실행할 bash 명령어 목록
        manual_steps: 수동 수정 단계 설명

    Examples:
        >>> # 자동 수정 가능
        >>> remediation = RemediationInfo(
        ...     auto=True,
        ...     backup_files=["/etc/pam.d/login"],
        ...     commands=["echo 'auth required pam_securetty.so' >> /etc/pam.d/login"]
        ... )

        >>> # 수동 수정만 가능
        >>> remediation = RemediationInfo(
        ...     auto=False,
        ...     manual_steps=[
        ...         "/etc/pam.d/login 파일 편집",
        ...         "auth required pam_securetty.so 추가"
        ...     ]
        ... )
    """

    model_config = ConfigDict(frozen=True)

    auto: bool = False
    backup_files: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    manual_steps: Optional[List[str]] = None


class RuleMetadata(BaseModel):
    """점검 규칙 메타데이터

    YAML 규칙 파일의 스키마를 정의합니다.
    각 점검 항목의 메타정보와 실행 방법을 포함합니다.

    Attributes:
        id: 규칙 ID (U-01, W-01, M-01 형식)
        name: 규칙 이름
        category: 카테고리 (계정관리, 파일/디렉토리 관리 등)
        severity: 취약점 심각도
        kisa_standard: KISA 기준 코드
        description: 상세 설명
        commands: 실행할 bash 명령어 목록
        validator: validator 함수 경로
        expected_result: 기대 결과 설명
        remediation: 자동 수정 정보 (Optional)

    Validation:
        - id: U-01 ~ U-73, W-01 ~ W-50, M-01 ~ M-50 형식
        - name: 1~200자
        - commands: 최소 1개 이상
        - validator: validators.(linux|macos|windows).check_[a-z]\\d{2}_\\w+ 형식

    Examples:
        >>> rule = RuleMetadata(
        ...     id="U-01",
        ...     name="root 계정 원격 로그인 제한",
        ...     category="계정관리",
        ...     severity=Severity.HIGH,
        ...     kisa_standard="U-01",
        ...     description="root 계정의 원격 로그인을 제한하여 시스템 보안을 강화합니다.",
        ...     commands=["cat /etc/pam.d/login", "cat /etc/securetty"],
        ...     validator="validators.linux.check_u01_root_remote_login",
        ...     expected_result="pam_securetty.so가 설정되어 있어야 함",
        ...     remediation=RemediationInfo(
        ...         auto=False,
        ...         manual_steps=[
        ...             "/etc/pam.d/login 파일 편집",
        ...             "auth required pam_securetty.so 추가"
        ...         ]
        ...     )
        ... )
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., pattern=r"^[UWM]-\d{2}$")
    name: str = Field(..., min_length=1, max_length=200)
    category: str
    severity: Severity
    kisa_standard: str
    description: str
    commands: List[str] = Field(default_factory=list)
    validator: str = Field(
        ..., pattern=r"^validators\.(linux|macos|windows)\.check_[a-z]\d{2}(_\w+)?$"
    )
    expected_result: Optional[str] = None
    remediation: Optional[RemediationInfo] = None


@dataclass
class RemediationResult:
    """자동 수정 실행 결과

    자동 수정 시도 후 성공/실패 여부와 상세 정보를 담습니다.

    Attributes:
        success: 수정 성공 여부
        message: 결과 메시지
        backup_id: 백업 세션 ID (롤백 시 사용)
        executed_commands: 실행한 명령어 목록
        dry_run: Dry-run 모드 여부 (실제 실행 안 함)
        timestamp: 실행 시각
        rollback_performed: 롤백 수행 여부 (실패 시 자동 롤백)
        error: 에러 정보 (실패 시)
    """

    success: bool
    message: str
    backup_id: Optional[str] = None
    executed_commands: List[str] = field(default_factory=list)
    dry_run: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    rollback_performed: bool = False
    error: Optional[str] = None


__all__ = [
    "Status",
    "Severity",
    "CheckResult",
    "RemediationInfo",
    "RuleMetadata",
    "RemediationResult",
]
