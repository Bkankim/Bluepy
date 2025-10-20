"""
Windows 계정 관리 validator 함수

Windows 계정 정책 및 보안 설정 점검 함수들을 포함합니다.
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_w01(command_outputs: List[str]) -> CheckResult:
    """
    W-01: Administrator 계정 이름 변경

    SID *-500을 가진 계정 이름이 "Administrator"가 아닌지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Administrator 계정 이름을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    admin_name = command_outputs[0].strip()

    if admin_name == "Administrator":
        return CheckResult(
            status=Status.FAIL,
            message=f"기본 Administrator 계정 이름을 사용 중입니다: {admin_name}",
        )

    return CheckResult(
        status=Status.PASS, message=f"Administrator 계정 이름이 변경되었습니다: {admin_name}"
    )


def check_w02(command_outputs: List[str]) -> CheckResult:
    """
    W-02: Guest 계정 비활성화

    Guest 계정의 Enabled 속성이 False인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Guest 계정 상태를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    enabled_str = command_outputs[0].strip()

    if enabled_str.lower() == "false":
        return CheckResult(status=Status.PASS, message="Guest 계정이 비활성화되어 있습니다.")

    return CheckResult(status=Status.FAIL, message="Guest 계정이 활성화되어 있습니다.")


def check_w03(command_outputs: List[str]) -> CheckResult:
    """
    W-03: 패스워드 복잡성 정책 설정

    패스워드 복잡성 정책이 활성화되어 있는지 확인합니다.
    레지스트리 값이 1이면 활성화, 0이면 비활성화입니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="패스워드 복잡성 정책을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    complexity_value = command_outputs[0].strip()

    if "1" in complexity_value or complexity_value == "1":
        return CheckResult(
            status=Status.PASS, message="패스워드 복잡성 정책이 활성화되어 있습니다."
        )

    return CheckResult(status=Status.FAIL, message="패스워드 복잡성 정책이 비활성화되어 있습니다.")


def check_w04(command_outputs: List[str]) -> CheckResult:
    """
    W-04: 패스워드 최소 길이 설정

    패스워드 최소 길이가 8자 이상인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="패스워드 최소 길이를 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    # "Minimum password length                      8" 형식에서 숫자 추출
    try:
        # 숫자만 추출
        import re

        match = re.search(r"(\d+)", output)
        if match:
            min_length = int(match.group(1))

            if min_length >= 8:
                return CheckResult(
                    status=Status.PASS,
                    message=f"패스워드 최소 길이가 설정되어 있습니다: {min_length}자",
                )
            else:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"패스워드 최소 길이가 부족합니다: {min_length}자 (권장: 8자 이상)",
                )
    except (ValueError, AttributeError):
        pass

    return CheckResult(
        status=Status.MANUAL,
        message=f"패스워드 최소 길이를 파싱할 수 없습니다: {output}",
    )


def check_w05(command_outputs: List[str]) -> CheckResult:
    """
    W-05: 패스워드 최대 사용 기간 설정

    패스워드 최대 사용 기간이 90일 이하인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="패스워드 최대 사용 기간을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    # "Maximum password age (days):              90" 형식에서 숫자 추출
    try:
        import re

        match = re.search(r"(\d+)", output)
        if match:
            max_age = int(match.group(1))

            if 1 <= max_age <= 90:
                return CheckResult(
                    status=Status.PASS,
                    message=f"패스워드 최대 사용 기간이 적절합니다: {max_age}일",
                )
            elif max_age == 0 or max_age > 90:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"패스워드 최대 사용 기간이 부적절합니다: {max_age}일 (권장: 1~90일)",
                )
    except (ValueError, AttributeError):
        pass

    return CheckResult(
        status=Status.MANUAL,
        message=f"패스워드 최대 사용 기간을 파싱할 수 없습니다: {output}",
    )


def check_w06(command_outputs: List[str]) -> CheckResult:
    """
    W-06: 계정 잠금 임계값 설정

    계정 잠금 임계값이 5회 이하인지 확인합니다.
    0은 잠금 기능 비활성화를 의미합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="계정 잠금 임계값을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    # "Lockout threshold:                    5" 형식에서 숫자 추출
    try:
        import re

        match = re.search(r"(\d+)", output)
        if match:
            threshold = int(match.group(1))

            if threshold == 0:
                return CheckResult(
                    status=Status.FAIL, message="계정 잠금 기능이 비활성화되어 있습니다."
                )
            elif 1 <= threshold <= 5:
                return CheckResult(
                    status=Status.PASS,
                    message=f"계정 잠금 임계값이 적절합니다: {threshold}회",
                )
            else:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"계정 잠금 임계값이 너무 높습니다: {threshold}회 (권장: 1~5회)",
                )
    except (ValueError, AttributeError):
        pass

    return CheckResult(
        status=Status.MANUAL, message=f"계정 잠금 임계값을 파싱할 수 없습니다: {output}"
    )


def check_w07(command_outputs: List[str]) -> CheckResult:
    """
    W-07: 계정 잠금 기간 설정

    계정 잠금 기간이 30분 이상인지 확인합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="계정 잠금 기간을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    # "Lockout duration (minutes):          30" 형식에서 숫자 추출
    try:
        import re

        match = re.search(r"(\d+)", output)
        if match:
            duration = int(match.group(1))

            if duration >= 30:
                return CheckResult(
                    status=Status.PASS, message=f"계정 잠금 기간이 적절합니다: {duration}분"
                )
            else:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"계정 잠금 기간이 부족합니다: {duration}분 (권장: 30분 이상)",
                )
    except (ValueError, AttributeError):
        pass

    return CheckResult(
        status=Status.MANUAL, message=f"계정 잠금 기간을 파싱할 수 없습니다: {output}"
    )
