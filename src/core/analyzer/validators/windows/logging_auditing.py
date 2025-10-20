"""
Windows 로깅/감사 정책 validator 함수

PowerShell 로깅, 프로세스 감사, 이벤트 로그 설정 점검 함수들을 포함합니다.
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_w46(command_outputs: List[str]) -> CheckResult:
    """
    W-46: PowerShell Script Block Logging 활성화

    PowerShell Script Block Logging이 활성화되어 있는지 확인합니다.
    EnableScriptBlockLogging 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="PowerShell Script Block Logging 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        enable_logging = int(output)
        if enable_logging == 1:
            return CheckResult(
                status=Status.PASS,
                message="PowerShell Script Block Logging이 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"PowerShell Script Block Logging이 비활성화되어 있습니다: {enable_logging}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"설정 파싱 실패: {output}")


def check_w47(command_outputs: List[str]) -> CheckResult:
    """
    W-47: PowerShell Module Logging 활성화

    PowerShell Module Logging이 활성화되어 있는지 확인합니다.
    EnableModuleLogging 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="PowerShell Module Logging 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        enable_logging = int(output)
        if enable_logging == 1:
            return CheckResult(
                status=Status.PASS,
                message="PowerShell Module Logging이 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"PowerShell Module Logging이 비활성화되어 있습니다: {enable_logging}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"설정 파싱 실패: {output}")


def check_w48(command_outputs: List[str]) -> CheckResult:
    """
    W-48: Command Line Process Auditing 활성화

    Command Line Process Auditing이 활성화되어 있는지 확인합니다.
    ProcessCreationIncludeCmdLine_Enabled 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Command Line Process Auditing 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        enable_auditing = int(output)
        if enable_auditing == 1:
            return CheckResult(
                status=Status.PASS,
                message="Command Line Process Auditing이 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"Command Line Process Auditing이 비활성화되어 있습니다: {enable_auditing}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"설정 파싱 실패: {output}")


def check_w49(command_outputs: List[str]) -> CheckResult:
    """
    W-49: Windows Defender 로그 활성화

    Windows Defender 로그가 활성화되어 있는지 확인합니다.
    DisableGenericRePorts 레지스트리 값이 0인지 확인합니다.
    (0 = 로그 활성화, 1 = 로그 비활성화)
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Defender 로그 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        disable_reports = int(output)
        if disable_reports == 0:
            return CheckResult(
                status=Status.PASS,
                message="Windows Defender 로그가 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"Windows Defender 로그가 비활성화되어 있습니다: DisableGenericRePorts={disable_reports}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"설정 파싱 실패: {output}")


def check_w50(command_outputs: List[str]) -> CheckResult:
    """
    W-50: 보안 이벤트 로그 보존 정책

    보안 이벤트 로그 보존 정책이 적절하게 설정되어 있는지 확인합니다.
    Retention 레지스트리 값이 설정되어 있는지 확인합니다.
    0 = 필요 시 덮어쓰기 (로그 크기 제한 필요)
    1 = 로그 보존 (수동 삭제 필요)
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="보안 이벤트 로그 보존 정책을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    # Retention 값은 문자열일 수 있으므로 먼저 정수 변환 시도
    try:
        retention_value = output
        # 문자열 "0" 또는 "1"을 정수로 변환
        if retention_value in ["0", "1"]:
            retention_int = int(retention_value)
            if retention_int == 0:
                return CheckResult(
                    status=Status.PASS,
                    message="보안 이벤트 로그 보존 정책이 설정되어 있습니다 (필요 시 덮어쓰기). "
                    "로그 크기 제한이 적절하게 설정되어 있는지 확인하세요.",
                )
            elif retention_int == 1:
                return CheckResult(
                    status=Status.PASS,
                    message="보안 이벤트 로그 보존 정책이 설정되어 있습니다 (로그 보존). "
                    "주기적으로 로그를 백업하고 삭제해야 합니다.",
                )
        else:
            return CheckResult(
                status=Status.MANUAL,
                message=f"알 수 없는 보존 정책 값입니다: {retention_value}. 수동 점검이 필요합니다.",
            )
    except (ValueError, AttributeError):
        return CheckResult(status=Status.MANUAL, message=f"설정 파싱 실패: {output}")
