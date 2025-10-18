"""Data Protection Validators

데이터 보호 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m02(outputs: List[str]) -> CheckResult:
    """M-02: FileVault 전체 디스크 암호화

    Args:
        outputs: fdesetup status 명령어 출력

    Returns:
        CheckResult: FileVault 활성화 여부

    출력 예시:
        - 양호: "FileVault is On."
        - 취약: "FileVault is Off."
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="FileVault 상태를 확인할 수 없습니다. fdesetup status 명령어를 수동으로 실행하세요.",
        )

    output = outputs[0].lower()

    if "on" in output or "enabled" in output:
        return CheckResult(
            status=Status.PASS,
            message="FileVault가 활성화되어 있습니다. 디스크가 암호화되었습니다. (양호)",
        )
    elif "off" in output or "disabled" in output:
        return CheckResult(
            status=Status.FAIL,
            message="FileVault가 비활성화되어 있습니다. System Preferences에서 활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"FileVault 상태를 판단할 수 없습니다: {output[:100]}",
        )


def check_m09(outputs: List[str]) -> CheckResult:
    """M-09: Time Machine 암호화

    Args:
        outputs: tmutil destinationinfo | grep -i encryption 명령어 출력

    Returns:
        CheckResult: Time Machine 암호화 여부

    출력 예시:
        - 양호: "Encrypted: 1" 또는 "Encryption: Enabled"
        - 취약: "Encrypted: 0" 또는 출력 없음
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Time Machine 백업 정보를 확인할 수 없습니다. 백업이 설정되지 않았거나 수동 확인이 필요합니다.",
        )

    output = outputs[0].lower()

    # 암호화 활성화 패턴
    if (
        "encrypted: 1" in output
        or "encryption: enabled" in output
        or "encryption: yes" in output
    ):
        return CheckResult(
            status=Status.PASS,
            message="Time Machine 백업이 암호화되어 있습니다. (양호)",
        )
    # 암호화 비활성화 패턴
    elif (
        "encrypted: 0" in output
        or "encryption: disabled" in output
        or "encryption: no" in output
    ):
        return CheckResult(
            status=Status.FAIL,
            message="Time Machine 백업이 암호화되지 않았습니다. System Preferences에서 암호화를 활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="Time Machine 암호화 상태를 판단할 수 없습니다. 수동으로 확인하세요.",
        )


__all__ = ["check_m02", "check_m09"]
