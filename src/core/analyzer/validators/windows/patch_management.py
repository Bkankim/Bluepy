"""
Windows 패치 관리 validator 함수

Windows Update 설정 점검 함수들을 포함합니다.
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_w41(command_outputs: List[str]) -> CheckResult:
    """
    W-41: Windows Update 자동 업데이트 활성화

    NoAutoUpdate 레지스트리 값이 0인지 확인합니다.
    값 0은 자동 업데이트가 활성화되어 있음을 의미합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Update 자동 업데이트 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        no_auto_update = int(output)
        if no_auto_update == 0:
            return CheckResult(
                status=Status.PASS,
                message="Windows Update 자동 업데이트가 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"Windows Update 자동 업데이트가 비활성화되어 있습니다: {no_auto_update} (권장: 0)",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Windows Update 자동 업데이트 설정 파싱 실패: {output}",
        )


def check_w42(command_outputs: List[str]) -> CheckResult:
    """
    W-42: Windows Update 자동 설치 설정

    AUOptions 레지스트리 값이 4인지 확인합니다.
    값 4는 자동 다운로드 및 설치를 의미합니다.
    (2=다운로드만, 3=다운로드 후 알림, 4=자동 설치)
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Update 자동 설치 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        au_options = int(output)
        if au_options == 4:
            return CheckResult(
                status=Status.PASS,
                message="Windows Update 자동 설치가 활성화되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"Windows Update 자동 설치가 비활성화되어 있습니다: {au_options} (권장: 4)",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Windows Update 자동 설치 설정 파싱 실패: {output}",
        )


def check_w43(command_outputs: List[str]) -> CheckResult:
    """
    W-43: Windows Update 예정 설치 시간

    ScheduledInstallDay 레지스트리 값이 0~7 범위인지 확인합니다.
    0=매일, 1=일요일, 2=월요일, ..., 7=토요일
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="Windows Update 예정 설치 시간 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        scheduled_install_day = int(output)
        day_names = [
            "매일",
            "일요일",
            "월요일",
            "화요일",
            "수요일",
            "목요일",
            "금요일",
            "토요일",
        ]

        if scheduled_install_day == 0:
            return CheckResult(
                status=Status.PASS,
                message="Windows Update 예정 설치 시간이 매일로 설정되어 있습니다.",
            )
        elif 1 <= scheduled_install_day <= 7:
            return CheckResult(
                status=Status.FAIL,
                message=f"Windows Update 예정 설치 시간이 주 1회로 설정되어 있습니다: {day_names[scheduled_install_day]} (권장: 매일)",
            )
        else:
            return CheckResult(
                status=Status.MANUAL,
                message=f"Windows Update 예정 설치 시간 값이 유효하지 않습니다: {scheduled_install_day} (유효 범위: 0~7)",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Windows Update 예정 설치 시간 설정 파싱 실패: {output}",
        )


def check_w44(command_outputs: List[str]) -> CheckResult:
    """
    W-44: 드라이버 업데이트 제외 설정

    ExcludeWUDriversInQualityUpdate 레지스트리 값이 1인지 확인합니다.
    값 1은 품질 업데이트에서 Windows Update 드라이버를 제외함을 의미합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="드라이버 업데이트 제외 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        exclude_drivers = int(output)
        if exclude_drivers == 1:
            return CheckResult(
                status=Status.PASS,
                message="품질 업데이트에서 드라이버가 제외되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"품질 업데이트에서 드라이버가 포함되어 있습니다: {exclude_drivers} (권장: 1)",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"드라이버 업데이트 제외 설정 파싱 실패: {output}",
        )


def check_w45(command_outputs: List[str]) -> CheckResult:
    """
    W-45: 자동 재부팅 금지 설정

    NoAutoRebootWithLoggedOnUsers 레지스트리 값이 1인지 확인합니다.
    값 1은 사용자 로그온 중 자동 재부팅을 금지함을 의미합니다.
    """
    if not command_outputs or not command_outputs[0].strip():
        return CheckResult(
            status=Status.MANUAL,
            message="자동 재부팅 금지 설정을 확인할 수 없습니다. 수동 점검이 필요합니다.",
        )

    output = command_outputs[0].strip()

    try:
        no_auto_reboot = int(output)
        if no_auto_reboot == 1:
            return CheckResult(
                status=Status.PASS,
                message="사용자 로그온 중 자동 재부팅이 금지되어 있습니다.",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"사용자 로그온 중 자동 재부팅이 허용되어 있습니다: {no_auto_reboot} (권장: 1)",
            )
    except ValueError:
        return CheckResult(
            status=Status.MANUAL,
            message=f"자동 재부팅 금지 설정 파싱 실패: {output}",
        )
