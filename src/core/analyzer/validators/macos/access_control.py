"""Access Control Validators

접근 제어 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m06(outputs: List[str]) -> CheckResult:
    """M-06: Screen Saver Password 설정

    Args:
        outputs:
            - defaults read com.apple.screensaver askForPassword
            - defaults read com.apple.screensaver askForPasswordDelay

    Returns:
        CheckResult: 화면 보호기 패스워드 설정 여부

    출력 예시:
        - 양호: "1" (askForPassword), "5" 이하 (askForPasswordDelay)
        - 취약: "0" 또는 설정 없음
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Screen Saver Password 설정을 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    # askForPassword 확인 (outputs[0])
    ask_password = outputs[0].strip().lower()

    # askForPasswordDelay 확인 (outputs[1] 있으면)
    delay = ""
    if len(outputs) > 1 and outputs[1]:
        delay = outputs[1].strip()

    # askForPassword가 1이어야 함
    if ask_password not in ["1", "true", "yes"]:
        return CheckResult(
            status=Status.FAIL,
            message="화면 보호기 패스워드가 비활성화되어 있습니다. System Preferences에서 활성화하세요. (취약)",
        )

    # delay가 5초 이하면 양호
    try:
        delay_seconds = int(delay) if delay else 0
        if delay_seconds <= 5:
            return CheckResult(
                status=Status.PASS,
                message=f"화면 보호기 패스워드가 활성화되어 있습니다. (지연시간: {delay_seconds}초) (양호)",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"화면 보호기 패스워드 지연시간이 너무 깁니다. ({delay_seconds}초) 5초 이하로 설정하세요. (취약)",
            )
    except (ValueError, TypeError):
        return CheckResult(
            status=Status.PASS,
            message="화면 보호기 패스워드가 활성화되어 있습니다. (양호)",
        )


def check_m07(outputs: List[str]) -> CheckResult:
    """M-07: Guest Account 비활성화

    Args:
        outputs:
            - dscl . -read /Users/Guest 출력
            - defaults read /Library/Preferences/com.apple.loginwindow GuestEnabled 출력

    Returns:
        CheckResult: Guest 계정 비활성화 여부

    출력 예시:
        - 양호: "0" 또는 "false" 또는 에러 (계정 없음)
        - 취약: "1" 또는 "true"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Guest Account 상태를 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    # GuestEnabled 확인 (outputs[1] 있으면 우선 확인)
    if len(outputs) > 1 and outputs[1]:
        guest_enabled = outputs[1].strip().lower()
        if guest_enabled in ["0", "false", "no"]:
            return CheckResult(
                status=Status.PASS,
                message="Guest 계정이 비활성화되어 있습니다. (양호)",
            )
        elif guest_enabled in ["1", "true", "yes"]:
            return CheckResult(
                status=Status.FAIL,
                message="Guest 계정이 활성화되어 있습니다. System Preferences에서 비활성화하세요. (취약)",
            )

    # dscl 출력 확인 (outputs[0])
    output = outputs[0].lower()

    # Guest 사용자가 존재하지 않으면 양호
    if "no such key" in output or "not found" in output or "error" in output:
        return CheckResult(
            status=Status.PASS,
            message="Guest 계정이 존재하지 않습니다. (양호)",
        )
    # Guest 사용자 정보가 있으면 취약 가능성
    elif "recordname" in output or "username" in output:
        return CheckResult(
            status=Status.FAIL,
            message="Guest 계정이 존재합니다. System Preferences에서 비활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="Guest 계정 상태를 판단할 수 없습니다. 수동으로 확인하세요.",
        )


__all__ = ["check_m06", "check_m07"]
