"""
Linux 보안 점검 Validator 함수 모음 - 패치 관리

이 모듈은 KISA 기준 Linux 보안 점검 항목 중 패치 관리 관련
validator 함수들을 포함합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)
"""

from typing import List
from src.core.domain.models import CheckResult, Status


def check_u71(command_outputs: List[str]) -> CheckResult:
    """U-71: 최신 보안패치 및 벤더 권고사항 적용

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _71SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - 패치 적용 정책을 수립하여 주기적으로 패치를 관리하고 있는지 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트 (사용 안 함, 수동 점검 항목)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: 패치 적용 정책을 수립하여 주기적으로 패치를 관리하고 있는지 확인하세요",
    )
