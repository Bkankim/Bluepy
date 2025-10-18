"""Risk Calculator

스캔 결과를 분석하여 위험도 통계 및 분포를 계산합니다.

주요 기능:
- 심각도별 통계 (HIGH/MID/LOW)
- 카테고리별 통계
- 위험도 분포 계산
- 점수 평가
"""

from dataclasses import dataclass
from typing import Dict, List

from ..domain.models import Severity, Status
from ..scanner.base_scanner import ScanResult


@dataclass
class RiskStatistics:
    """위험도 통계

    스캔 결과의 통계 정보를 담습니다.

    Attributes:
        total: 전체 점검 항목 수
        passed: 양호 항목 수
        failed: 취약 항목 수
        manual: 수동 점검 필요 항목 수
        score: 전체 점수 (0~100)
        high_risk: HIGH 심각도 취약점 수
        mid_risk: MID 심각도 취약점 수
        low_risk: LOW 심각도 취약점 수
        pass_rate: 양호 비율 (%)
        fail_rate: 취약 비율 (%)
        risk_level: 위험 수준 (critical/high/medium/low/safe)
    """

    total: int
    passed: int
    failed: int
    manual: int
    score: float

    high_risk: int
    mid_risk: int
    low_risk: int

    pass_rate: float
    fail_rate: float
    risk_level: str


def calculate_risk_statistics(
    scan_result: ScanResult, rules_metadata: List = None
) -> RiskStatistics:
    """위험도 통계 계산

    Args:
        scan_result: 스캔 결과
        rules_metadata: 규칙 메타데이터 리스트 (심각도 정보용, 선택)

    Returns:
        RiskStatistics 객체
    """
    total = scan_result.total
    passed = scan_result.passed
    failed = scan_result.failed
    manual = scan_result.manual
    score = scan_result.score

    # 양호/취약 비율
    pass_rate = (passed / total * 100) if total > 0 else 0.0
    fail_rate = (failed / total * 100) if total > 0 else 0.0

    # 심각도별 취약점 수 (rules_metadata에서 계산 또는 기본값)
    high_risk = 0
    mid_risk = 0
    low_risk = 0

    if rules_metadata:
        # TODO: rules_metadata와 scan_result.results를 매칭하여 심각도별 집계
        # 현재는 간단하게 failed 항목을 균등 분배
        high_risk = failed // 3
        mid_risk = failed // 3
        low_risk = failed - high_risk - mid_risk
    else:
        # rules_metadata 없이 단순 추정
        high_risk = failed // 3
        mid_risk = failed // 3
        low_risk = failed - high_risk - mid_risk

    # 위험 수준 평가
    risk_level = evaluate_risk_level(score, high_risk)

    return RiskStatistics(
        total=total,
        passed=passed,
        failed=failed,
        manual=manual,
        score=score,
        high_risk=high_risk,
        mid_risk=mid_risk,
        low_risk=low_risk,
        pass_rate=pass_rate,
        fail_rate=fail_rate,
        risk_level=risk_level,
    )


def evaluate_risk_level(score: float, high_risk_count: int) -> str:
    """위험 수준 평가

    점수와 HIGH 심각도 취약점 개수를 기반으로 위험 수준을 결정합니다.

    Args:
        score: 전체 점수 (0~100)
        high_risk_count: HIGH 심각도 취약점 개수

    Returns:
        위험 수준 문자열:
        - "critical": 치명적 (점수 < 40 또는 HIGH 취약점 >= 10)
        - "high": 높음 (점수 < 60 또는 HIGH 취약점 >= 5)
        - "medium": 중간 (점수 < 80)
        - "low": 낮음 (점수 < 90)
        - "safe": 안전 (점수 >= 90)
    """
    if score < 40 or high_risk_count >= 10:
        return "critical"
    elif score < 60 or high_risk_count >= 5:
        return "high"
    elif score < 80:
        return "medium"
    elif score < 90:
        return "low"
    else:
        return "safe"


def get_category_distribution(
    scan_result: ScanResult, rules_metadata: List = None
) -> Dict[str, Dict[str, int]]:
    """카테고리별 분포 계산

    각 카테고리별로 양호/취약/수동 점검 항목 수를 집계합니다.

    Args:
        scan_result: 스캔 결과
        rules_metadata: 규칙 메타데이터 리스트 (카테고리 정보용)

    Returns:
        카테고리별 통계 딕셔너리
        {
            "계정관리": {"passed": 10, "failed": 3, "manual": 2},
            "파일 및 디렉터리 관리": {"passed": 15, "failed": 5, "manual": 0},
            ...
        }
    """
    # TODO: rules_metadata를 사용하여 실제 카테고리별 집계
    # 현재는 샘플 데이터 반환
    return {
        "계정관리": {
            "passed": scan_result.passed // 3,
            "failed": scan_result.failed // 3,
            "manual": scan_result.manual // 3,
        },
        "파일 및 디렉터리 관리": {
            "passed": scan_result.passed // 3,
            "failed": scan_result.failed // 3,
            "manual": scan_result.manual // 3,
        },
        "서비스 관리": {
            "passed": scan_result.passed - (scan_result.passed // 3) * 2,
            "failed": scan_result.failed - (scan_result.failed // 3) * 2,
            "manual": scan_result.manual - (scan_result.manual // 3) * 2,
        },
    }


def get_severity_distribution(
    scan_result: ScanResult, rules_metadata: List = None
) -> Dict[str, int]:
    """심각도별 분포 계산

    실패한 항목들을 심각도별로 집계합니다.

    Args:
        scan_result: 스캔 결과
        rules_metadata: 규칙 메타데이터 리스트 (심각도 정보용)

    Returns:
        심각도별 취약점 수
        {
            "high": 5,
            "mid": 3,
            "low": 2
        }
    """
    stats = calculate_risk_statistics(scan_result, rules_metadata)

    return {"high": stats.high_risk, "mid": stats.mid_risk, "low": stats.low_risk}


__all__ = [
    "RiskStatistics",
    "calculate_risk_statistics",
    "evaluate_risk_level",
    "get_category_distribution",
    "get_severity_distribution",
]
