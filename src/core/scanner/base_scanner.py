"""BaseScanner 추상 클래스

모든 플랫폼 스캐너의 기본 인터페이스를 정의합니다.
Clean Architecture의 Domain Layer에 해당하며,
구체적인 구현(SSH, WinRM 등)은 하위 클래스에서 담당합니다.

설계 원칙:
- ABC (Abstract Base Class) 사용
- AsyncIO 기반 비동기 처리
- 플랫폼 독립적 인터페이스
- 의존성 역전 원칙 (DIP)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.models import CheckResult, RuleMetadata


@dataclass
class ScanResult:
    """스캔 결과 컨테이너

    단일 서버의 전체 점검 결과를 담습니다.

    Attributes:
        server_id: 서버 식별자
        platform: 플랫폼 (linux, macos, windows)
        scan_time: 스캔 수행 시각
        results: 점검 항목별 결과 (rule_id -> CheckResult)
        total: 전체 점검 항목 수
        passed: 양호 항목 수
        failed: 취약 항목 수
        manual: 수동 점검 필요 항목 수
        score: 전체 점수 (0~100)
    """

    server_id: str
    platform: str
    scan_time: datetime = field(default_factory=datetime.now)
    results: Dict[str, CheckResult] = field(default_factory=dict)

    @property
    def total(self) -> int:
        """전체 점검 항목 수"""
        return len(self.results)

    @property
    def passed(self) -> int:
        """양호 항목 수"""
        return sum(1 for r in self.results.values() if r.is_passed())

    @property
    def failed(self) -> int:
        """취약 항목 수"""
        return sum(1 for r in self.results.values() if r.is_failed())

    @property
    def manual(self) -> int:
        """수동 점검 필요 항목 수"""
        return sum(1 for r in self.results.values() if r.is_manual())

    @property
    def score(self) -> float:
        """전체 점수 (0~100)

        계산 방식:
        - PASS: 1점
        - FAIL: 0점
        - MANUAL: 0.5점 (절반만 인정)
        """
        if self.total == 0:
            return 0.0

        weighted_score = self.passed * 1.0 + self.manual * 0.5
        return (weighted_score / self.total) * 100


class BaseScanner(ABC):
    """스캐너 기본 클래스

    모든 플랫폼 스캐너가 상속해야 하는 추상 클래스입니다.

    하위 클래스:
    - LinuxScanner: Linux 서버 스캔 (SSH)
    - MacOSScanner: macOS 서버 스캔 (SSH)
    - WindowsScanner: Windows 서버 스캔 (WinRM)

    사용 예시:
        >>> scanner = LinuxScanner(host="192.168.1.100", username="admin")
        >>> await scanner.connect()
        >>> result = await scanner.scan_all()
        >>> print(f"점수: {result.score}/100")
        >>> await scanner.disconnect()
    """

    def __init__(self, server_id: str, platform: str):
        """초기화

        Args:
            server_id: 서버 식별자
            platform: 플랫폼 (linux, macos, windows)
        """
        self.server_id = server_id
        self.platform = platform
        self._connected = False
        self._rules: List[RuleMetadata] = []

    @abstractmethod
    async def connect(self) -> None:
        """서버에 연결

        Raises:
            ConnectionError: 연결 실패 시
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """서버 연결 해제"""
        pass

    @abstractmethod
    async def execute_command(self, command: str) -> str:
        """명령어 실행

        Args:
            command: 실행할 명령어

        Returns:
            명령어 출력 결과 (stdout)

        Raises:
            RuntimeError: 명령어 실행 실패 시
        """
        pass

    @abstractmethod
    async def load_rules(self, rules_dir: str) -> None:
        """규칙 파일 로드

        Args:
            rules_dir: 규칙 파일 디렉토리 경로

        Raises:
            FileNotFoundError: 규칙 파일이 없는 경우
            ValueError: 규칙 파일 파싱 실패
        """
        pass

    async def scan_all(self) -> ScanResult:
        """전체 점검 실행

        모든 규칙을 순차적으로 실행합니다.

        Returns:
            전체 스캔 결과

        Raises:
            RuntimeError: 연결되지 않은 상태에서 호출 시
        """
        if not self._connected:
            raise RuntimeError("서버에 연결되지 않았습니다. connect()를 먼저 호출하세요.")

        if not self._rules:
            raise RuntimeError("규칙이 로드되지 않았습니다. load_rules()를 먼저 호출하세요.")

        result = ScanResult(server_id=self.server_id, platform=self.platform)

        for rule in self._rules:
            check_result = await self.scan_one(rule)
            result.results[rule.id] = check_result

        return result

    @abstractmethod
    async def scan_one(self, rule: RuleMetadata) -> CheckResult:
        """단일 규칙 점검

        Args:
            rule: 점검 규칙

        Returns:
            점검 결과

        Raises:
            RuntimeError: 명령어 실행 실패 시
        """
        pass

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected

    def get_rules_count(self) -> int:
        """로드된 규칙 수 반환"""
        return len(self._rules)


__all__ = [
    "ScanResult",
    "BaseScanner",
]
