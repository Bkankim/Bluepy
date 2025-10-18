"""Network Security Validators

네트워크 보안 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m04(outputs: List[str]) -> CheckResult:
    """M-04: Firewall 활성화

    Args:
        outputs: /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 출력

    Returns:
        CheckResult: Firewall 활성화 여부

    출력 예시:
        - 양호: "Firewall is enabled"
        - 취약: "Firewall is disabled"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Firewall 상태를 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    output = outputs[0].lower()

    if "enabled" in output or "on" in output:
        return CheckResult(
            status=Status.PASS,
            message="Application Firewall가 활성화되어 있습니다. (양호)",
        )
    elif "disabled" in output or "off" in output:
        return CheckResult(
            status=Status.FAIL,
            message="Application Firewall가 비활성화되어 있습니다. socketfilterfw --setglobalstate on 명령으로 활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Firewall 상태를 판단할 수 없습니다: {output[:100]}",
        )


def check_m08(outputs: List[str]) -> CheckResult:
    """M-08: Remote Login 및 Remote Management 제한

    Args:
        outputs:
            - systemsetup -getremotelogin 출력
            - ARDAgent kickstart -query 출력

    Returns:
        CheckResult: Remote 접근 제한 여부

    출력 예시:
        - 양호: "Remote Login: Off"
        - 취약: "Remote Login: On"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Remote Login 상태를 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    output = outputs[0].lower()

    # Remote Login 상태 확인
    if "off" in output or "disabled" in output:
        return CheckResult(
            status=Status.PASS,
            message="Remote Login이 비활성화되어 있습니다. (양호)",
        )
    elif "on" in output or "enabled" in output:
        # Remote Management (ARD) 상태도 확인 (outputs[1] 있으면)
        ard_status = ""
        if len(outputs) > 1 and outputs[1]:
            ard_status = f" ARD 상태: {outputs[1][:50]}"

        return CheckResult(
            status=Status.FAIL,
            message=f"Remote Login이 활성화되어 있습니다. 불필요하면 비활성화하세요.{ard_status} (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Remote Login 상태를 판단할 수 없습니다: {output[:100]}",
        )


__all__ = ["check_m04", "check_m08"]
