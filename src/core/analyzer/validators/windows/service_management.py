"""
Windows 서비스 관리 validator 함수

Windows 방화벽, 보안 서비스 점검 함수들을 포함합니다.
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_w08(command_outputs: List[str]) -> CheckResult:
    """
    W-08: Windows Firewall 활성화 (도메인 프로필)

    Windows Firewall의 도메인 프로필이 활성화되어 있는지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Firewall 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    enabled_str = command_outputs[0].strip()

    if enabled_str.lower() == "true":
        return CheckResult(
            status=Status.PASS, message="Windows Firewall (도메인 프로필)이 활성화되어 있습니다."
        )

    return CheckResult(
        status=Status.FAIL, message="Windows Firewall (도메인 프로필)이 비활성화되어 있습니다."
    )


def check_w09(command_outputs: List[str]) -> CheckResult:
    """
    W-09: Windows Defender 실시간 보호 활성화

    Windows Defender 실시간 보호가 활성화되어 있는지 확인합니다.
    DisableRealtimeMonitoring 값이 False여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Defender 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    disabled_str = command_outputs[0].strip()

    if disabled_str.lower() == "false":
        return CheckResult(
            status=Status.PASS, message="Windows Defender 실시간 보호가 활성화되어 있습니다."
        )

    return CheckResult(
        status=Status.FAIL, message="Windows Defender 실시간 보호가 비활성화되어 있습니다."
    )


def check_w10(command_outputs: List[str]) -> CheckResult:
    """
    W-10: 원격 데스크톱 NLA 요구 설정

    원격 데스크톱 연결 시 Network Level Authentication (NLA)이 요구되는지 확인합니다.
    UserAuthentication 레지스트리 값이 1이어야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="원격 데스크톱 NLA 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    user_auth_value = command_outputs[0].strip()

    if "1" in user_auth_value or user_auth_value == "1":
        return CheckResult(status=Status.PASS, message="원격 데스크톱 NLA가 활성화되어 있습니다.")

    return CheckResult(status=Status.FAIL, message="원격 데스크톱 NLA가 비활성화되어 있습니다.")
