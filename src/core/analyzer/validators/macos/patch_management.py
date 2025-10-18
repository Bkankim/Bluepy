"""Patch Management Validators

패치 관리 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m05(outputs: List[str]) -> CheckResult:
    """M-05: Automatic Updates 활성화

    Args:
        outputs:
            - defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled
            - defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload

    Returns:
        CheckResult: 자동 업데이트 활성화 여부

    출력 예시:
        - 양호: "1" 또는 "true"
        - 취약: "0" 또는 "false"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Automatic Updates 설정을 확인할 수 없습니다. 수동으로 확인하세요.",
        )

    # AutomaticCheckEnabled 확인 (outputs[0])
    check_enabled = outputs[0].strip().lower()
    download_enabled = ""

    # AutomaticDownload 확인 (outputs[1] 있으면)
    if len(outputs) > 1 and outputs[1]:
        download_enabled = outputs[1].strip().lower()

    # 둘 다 활성화되어 있어야 양호
    check_ok = check_enabled in ["1", "true", "yes"]
    download_ok = download_enabled in ["1", "true", "yes"] if download_enabled else True

    if check_ok and download_ok:
        return CheckResult(
            status=Status.PASS,
            message="자동 업데이트가 활성화되어 있습니다. (양호)",
        )
    elif not check_ok:
        return CheckResult(
            status=Status.FAIL,
            message="자동 업데이트 확인이 비활성화되어 있습니다. System Preferences에서 활성화하세요. (취약)",
        )
    elif not download_ok:
        return CheckResult(
            status=Status.FAIL,
            message="자동 다운로드가 비활성화되어 있습니다. System Preferences에서 활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"자동 업데이트 상태를 판단할 수 없습니다: Check={check_enabled}, Download={download_enabled}",
        )


__all__ = ["check_m05"]
