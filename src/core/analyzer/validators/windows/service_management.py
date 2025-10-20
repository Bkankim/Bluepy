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


def check_w31(command_outputs: List[str]) -> CheckResult:
    """
    W-31: Telnet 서비스 비활성화

    Telnet 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Telnet 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(status=Status.PASS, message="Telnet 서비스가 비활성화되어 있습니다.")

    return CheckResult(
        status=Status.FAIL, message=f"Telnet 서비스가 활성화되어 있습니다 (Start={value})."
    )


def check_w32(command_outputs: List[str]) -> CheckResult:
    """
    W-32: FTP 서비스 비활성화

    FTP 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="FTP 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(status=Status.PASS, message="FTP 서비스가 비활성화되어 있습니다.")

    return CheckResult(
        status=Status.FAIL, message=f"FTP 서비스가 활성화되어 있습니다 (Start={value})."
    )


def check_w33(command_outputs: List[str]) -> CheckResult:
    """
    W-33: SNMP 서비스 비활성화

    SNMP 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="SNMP 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(status=Status.PASS, message="SNMP 서비스가 비활성화되어 있습니다.")

    return CheckResult(
        status=Status.FAIL, message=f"SNMP 서비스가 활성화되어 있습니다 (Start={value})."
    )


def check_w34(command_outputs: List[str]) -> CheckResult:
    """
    W-34: RDP 유휴 세션 시간 제한

    RDP 유휴 세션 시간 제한이 15분 이하로 설정되어 있는지 확인합니다.
    MaxIdleTime 값이 900000 (밀리초) 이하여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="RDP 유휴 세션 시간 제한을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    try:
        max_idle_time = int(value)
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"RDP 유휴 세션 시간 제한 값이 올바르지 않습니다 (MaxIdleTime={value}).",
        )

    if max_idle_time == 0:
        return CheckResult(
            status=Status.FAIL, message="RDP 유휴 세션 시간 제한이 설정되어 있지 않습니다."
        )

    if max_idle_time <= 900000:
        return CheckResult(
            status=Status.PASS,
            message=f"RDP 유휴 세션 시간 제한이 15분 이하로 설정되어 있습니다 (MaxIdleTime={max_idle_time}).",
        )

    return CheckResult(
        status=Status.FAIL,
        message=f"RDP 유휴 세션 시간 제한이 15분을 초과합니다 (MaxIdleTime={max_idle_time}).",
    )


def check_w35(command_outputs: List[str]) -> CheckResult:
    """
    W-35: SMB Server Signing 강제

    SMB 서버 서명이 강제되어 있는지 확인합니다.
    RequireSecuritySignature 레지스트리 값이 1이어야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="SMB Server Signing 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "1":
        return CheckResult(status=Status.PASS, message="SMB Server Signing이 강제되어 있습니다.")

    return CheckResult(status=Status.FAIL, message="SMB Server Signing이 강제되어 있지 않습니다.")


def check_w36(command_outputs: List[str]) -> CheckResult:
    """
    W-36: NetBIOS over TCP/IP 비활성화

    NetBIOS over TCP/IP가 비활성화되어 있는지 확인합니다.
    NodeType 레지스트리 값이 2 (P-node)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="NetBIOS over TCP/IP 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "2":
        return CheckResult(
            status=Status.PASS, message="NetBIOS over TCP/IP가 비활성화되어 있습니다 (P-node)."
        )

    return CheckResult(
        status=Status.FAIL,
        message=f"NetBIOS over TCP/IP가 활성화되어 있습니다 (NodeType={value}).",
    )


def check_w37(command_outputs: List[str]) -> CheckResult:
    """
    W-37: LLMNR 비활성화

    LLMNR (Link-Local Multicast Name Resolution)이 비활성화되어 있는지 확인합니다.
    EnableMulticast 레지스트리 값이 0이어야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="LLMNR 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "0":
        return CheckResult(status=Status.PASS, message="LLMNR이 비활성화되어 있습니다.")

    return CheckResult(status=Status.FAIL, message="LLMNR이 활성화되어 있습니다.")


def check_w38(command_outputs: List[str]) -> CheckResult:
    """
    W-38: Print Spooler 서비스 비활성화

    Print Spooler 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Print Spooler 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(
            status=Status.PASS, message="Print Spooler 서비스가 비활성화되어 있습니다."
        )

    return CheckResult(
        status=Status.FAIL,
        message=f"Print Spooler 서비스가 활성화되어 있습니다 (Start={value}).",
    )


def check_w39(command_outputs: List[str]) -> CheckResult:
    """
    W-39: Windows Search 서비스 비활성화

    Windows Search 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Search 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(
            status=Status.PASS, message="Windows Search 서비스가 비활성화되어 있습니다."
        )

    return CheckResult(
        status=Status.FAIL,
        message=f"Windows Search 서비스가 활성화되어 있습니다 (Start={value}).",
    )


def check_w40(command_outputs: List[str]) -> CheckResult:
    """
    W-40: IIS Admin 서비스 비활성화

    IIS Admin 서비스가 비활성화되어 있는지 확인합니다.
    Start 레지스트리 값이 4 (Disabled)여야 합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="IIS Admin 서비스 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    value = command_outputs[0].strip()

    if value == "4":
        return CheckResult(status=Status.PASS, message="IIS Admin 서비스가 비활성화되어 있습니다.")

    return CheckResult(
        status=Status.FAIL,
        message=f"IIS Admin 서비스가 활성화되어 있습니다 (Start={value}).",
    )
