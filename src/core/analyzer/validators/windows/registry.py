"""
Windows 레지스트리 validator 함수

Windows 레지스트리 기반 보안 설정 점검 함수들을 포함합니다.
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_w11(command_outputs: List[str]) -> CheckResult:
    """
    W-11: UAC 관리자 승인 모드 활성화

    EnableLUA 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="UAC 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        enable_lua = int(output)
        if enable_lua == 1:
            return CheckResult(status=Status.PASS, message="UAC가 활성화되어 있습니다.")
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"UAC가 비활성화되어 있습니다: {enable_lua}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"UAC 설정 파싱 실패: {output}")


def check_w12(command_outputs: List[str]) -> CheckResult:
    """
    W-12: LM 해시 저장 금지

    NoLMHash 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.FAIL,
            message="NoLMHash 설정이 존재하지 않습니다. LM 해시가 저장될 수 있습니다.",
        )

    output = command_outputs[0].strip()

    try:
        no_lm_hash = int(output)
        if no_lm_hash == 1:
            return CheckResult(status=Status.PASS, message="LM 해시 저장이 금지되어 있습니다.")
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"LM 해시 저장이 허용되어 있습니다: {no_lm_hash}",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"NoLMHash 설정 파싱 실패: {output}")


def check_w13(command_outputs: List[str]) -> CheckResult:
    """
    W-13: 익명 SAM 계정 열거 차단

    RestrictAnonymousSAM 레지스트리 값이 1인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="익명 SAM 계정 열거 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        restrict_anonymous_sam = int(output)
        if restrict_anonymous_sam == 1:
            return CheckResult(
                status=Status.PASS, message="익명 SAM 계정 열거가 차단되어 있습니다."
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"익명 SAM 계정 열거가 허용되어 있습니다: {restrict_anonymous_sam}",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"RestrictAnonymousSAM 설정 파싱 실패: {output}",
        )


def check_w14(command_outputs: List[str]) -> CheckResult:
    """
    W-14: 자동 로그온 비활성화

    AutoAdminLogon 레지스트리 값이 0인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.PASS,
            message="AutoAdminLogon 설정이 존재하지 않습니다. 자동 로그온이 비활성화되어 있습니다.",
        )

    output = command_outputs[0].strip()

    try:
        auto_admin_logon = int(output)
        if auto_admin_logon == 0:
            return CheckResult(status=Status.PASS, message="자동 로그온이 비활성화되어 있습니다.")
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"자동 로그온이 활성화되어 있습니다: {auto_admin_logon}",
            )
    except ValueError:
        # 문자열 "0" 처리
        if output == "0":
            return CheckResult(status=Status.PASS, message="자동 로그온이 비활성화되어 있습니다.")
        else:
            return CheckResult(
                status=Status.MANUAL,
                message=f"AutoAdminLogon 설정 파싱 실패: {output}",
            )


def check_w15(command_outputs: List[str]) -> CheckResult:
    """
    W-15: 원격 레지스트리 서비스 비활성화

    RemoteRegistry 서비스의 Start 값이 4(Disabled)인지 확인합니다.
    Start 값: 2=Automatic, 3=Manual, 4=Disabled
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="원격 레지스트리 서비스 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        start_value = int(output)
        if start_value == 4:
            return CheckResult(
                status=Status.PASS,
                message="원격 레지스트리 서비스가 비활성화되어 있습니다.",
            )
        elif start_value == 3:
            return CheckResult(
                status=Status.FAIL,
                message="원격 레지스트리 서비스가 수동 시작으로 설정되어 있습니다.",
            )
        elif start_value == 2:
            return CheckResult(
                status=Status.FAIL,
                message="원격 레지스트리 서비스가 자동 시작으로 설정되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"원격 레지스트리 서비스가 비활성화되어 있지 않습니다: Start={start_value}",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"원격 레지스트리 서비스 설정 파싱 실패: {output}",
        )


def check_w16(command_outputs: List[str]) -> CheckResult:
    """W-16: NTLM SSP 기반 서버 세션 보안"""
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="NTLM 세션 보안 설정을 확인할 수 없습니다.",
        )

    output = command_outputs[0].strip()
    try:
        ntlm_min_server_sec = int(output)
        if ntlm_min_server_sec >= 537395200:
            return CheckResult(
                status=Status.PASS,
                message=f"NTLM 세션 보안이 적절히 설정되어 있습니다: {ntlm_min_server_sec}",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"NTLM 세션 보안이 약하게 설정되어 있습니다: {ntlm_min_server_sec} (권장: 537395200 이상)",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"NTLM 설정 파싱 실패: {output}")


def check_w17(command_outputs: List[str]) -> CheckResult:
    """W-17: 빈 패스워드로 콘솔 로그온 제한"""
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="빈 패스워드 제한 설정을 확인할 수 없습니다.",
        )

    output = command_outputs[0].strip()
    try:
        limit_blank_password = int(output)
        if limit_blank_password == 1:
            return CheckResult(
                status=Status.PASS,
                message="빈 패스워드 계정의 콘솔 로그온이 제한되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"빈 패스워드 계정의 콘솔 로그온이 허용되어 있습니다: {limit_blank_password} (권장: 1)",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"빈 패스워드 설정 파싱 실패: {output}")


def check_w18(command_outputs: List[str]) -> CheckResult:
    """W-18: SMB v1 프로토콜 비활성화"""
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(status=Status.MANUAL, message="SMB v1 설정을 확인할 수 없습니다.")

    output = command_outputs[0].strip()
    try:
        smb1_status = int(output)
        if smb1_status == 0:
            return CheckResult(
                status=Status.PASS, message="SMB v1 프로토콜이 비활성화되어 있습니다."
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"SMB v1 프로토콜이 활성화되어 있습니다: {smb1_status} (권장: 0)",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"SMB v1 설정 파싱 실패: {output}")


def check_w19(command_outputs: List[str]) -> CheckResult:
    """W-19: 익명 공유 및 파이프 열거 차단"""
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="익명 공유 제한 설정을 확인할 수 없습니다.",
        )

    output = command_outputs[0].strip()
    try:
        restrict_null_sess = int(output)
        if restrict_null_sess == 1:
            return CheckResult(
                status=Status.PASS,
                message="익명 공유 및 파이프 열거가 차단되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"익명 공유 및 파이프 열거가 허용되어 있습니다: {restrict_null_sess} (권장: 1)",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"익명 공유 설정 파싱 실패: {output}")


def check_w20(command_outputs: List[str]) -> CheckResult:
    """W-20: LSA 보호 활성화"""
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(status=Status.MANUAL, message="LSA 보호 설정을 확인할 수 없습니다.")

    output = command_outputs[0].strip()
    try:
        run_as_ppl = int(output)
        if run_as_ppl == 1:
            return CheckResult(status=Status.PASS, message="LSA 보호 모드가 활성화되어 있습니다.")
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"LSA 보호 모드가 비활성화되어 있습니다: {run_as_ppl} (권장: 1)",
            )
    except ValueError:
        return CheckResult(status=Status.MANUAL, message=f"LSA 보호 설정 파싱 실패: {output}")
