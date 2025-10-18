"""Application Security Validators

애플리케이션 보안 관련 macOS validator 함수들
"""

from typing import List
from ....domain.models import CheckResult, Status


def check_m03(outputs: List[str]) -> CheckResult:
    """M-03: Gatekeeper 설정

    Args:
        outputs:
            - spctl --status 명령어 출력
            - spctl --assess --type execute --verbose /Applications/Safari.app 출력

    Returns:
        CheckResult: Gatekeeper 활성화 여부

    출력 예시:
        - 양호: "assessments enabled"
        - 취약: "assessments disabled"
    """
    if not outputs or not outputs[0]:
        return CheckResult(
            status=Status.MANUAL,
            message="Gatekeeper 상태를 확인할 수 없습니다. spctl --status 명령어를 수동으로 실행하세요.",
        )

    output = outputs[0].lower()

    if "enabled" in output:
        return CheckResult(
            status=Status.PASS,
            message="Gatekeeper가 활성화되어 있습니다. 서명되지 않은 앱 실행이 차단됩니다. (양호)",
        )
    elif "disabled" in output:
        return CheckResult(
            status=Status.FAIL,
            message="Gatekeeper가 비활성화되어 있습니다. spctl --master-enable 명령으로 활성화하세요. (취약)",
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message=f"Gatekeeper 상태를 판단할 수 없습니다: {output[:100]}",
        )


__all__ = ["check_m03"]
