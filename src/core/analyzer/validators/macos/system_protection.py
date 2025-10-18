"""System Protection Validators

시스템 보호 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m01(outputs: List[str]) -> CheckResult:
    """M-01: System Integrity Protection (SIP) 활성화

    Args:
        outputs: csrutil status 명령어 출력

    Returns:
        CheckResult: SIP 활성화 여부

    출력 예시:
        - 양호: "System Integrity Protection status: enabled."
        - 취약: "System Integrity Protection status: disabled."
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="SIP 상태를 확인할 수 없습니다. csrutil status 명령어를 수동으로 실행하세요.",
        )

    output = outputs[0].lower()

    if "enabled" in output:
        return CheckResult(
            status=Status.PASS, message="SIP가 활성화되어 있습니다. (양호)"
        )
    elif "disabled" in output:
        return CheckResult(
            status=Status.FAIL,
            message="SIP가 비활성화되어 있습니다. Recovery Mode에서 csrutil enable을 실행하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"SIP 상태를 판단할 수 없습니다: {output[:100]}",
        )


def check_m10(outputs: List[str]) -> CheckResult:
    """M-10: Firmware Password 설정

    Args:
        outputs: firmwarepasswd -check 명령어 출력

    Returns:
        CheckResult: Firmware Password 설정 여부

    출력 예시:
        - 양호: "Password Enabled: Yes"
        - 취약: "Password Enabled: No"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Firmware Password 상태를 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    output = outputs[0].lower()

    if "yes" in output or "enabled" in output:
        return CheckResult(
            status=Status.PASS,
            message="Firmware Password가 설정되어 있습니다. (양호)",
        )
    elif "no" in output or "disabled" in output:
        return CheckResult(
            status=Status.FAIL,
            message="Firmware Password가 설정되지 않았습니다. Recovery Mode에서 설정하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Firmware Password 상태를 판단할 수 없습니다: {output[:100]}",
        )


__all__ = ["check_m01", "check_m10"]
