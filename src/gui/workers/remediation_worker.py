"""Remediation Worker

QThread를 사용하여 백그라운드에서 자동 수정을 실행하는 Worker입니다.
ScanWorker 패턴을 따라 asyncio + QThread를 통합합니다.
"""

import asyncio
import logging
from typing import Optional, List

from PySide6.QtCore import QThread, Signal

from ...core.domain.models import RemediationResult, RuleMetadata

logger = logging.getLogger(__name__)


class RemediationWorker(QThread):
    """자동 수정 Worker 클래스

    QThread를 사용하여 백그라운드에서 Remediator를 실행합니다.

    Signals:
        progress: 진행률 업데이트 (current: int, total: int, message: str)
        log: 로그 메시지 (message: str)
        finished: 수정 완료 (result: RemediationResult)
        error: 오류 발생 (error_message: str)

    Attributes:
        server_id: 서버 ID
        host: 서버 호스트 주소
        username: SSH 사용자명
        platform: OS 플랫폼 (linux, macos, windows)
        rule_id: 수정할 규칙 ID
        dry_run: Dry-run 모드 여부
    """

    # 커스텀 시그널
    progress = Signal(int, int, str)  # current, total, message
    log = Signal(str)
    finished = Signal(object)  # RemediationResult
    error = Signal(str)

    def __init__(
        self,
        server_id: str,
        host: str,
        username: str,
        platform: str,
        rule_id: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        dry_run: bool = True,
    ):
        """초기화

        Args:
            server_id: 서버 ID
            host: 호스트 주소
            username: SSH 사용자명
            platform: OS 플랫폼 (linux/macos/windows)
            rule_id: 수정할 규칙 ID (예: M-03)
            password: SSH 패스워드 (선택)
            key_filename: SSH 키 파일 경로 (선택)
            port: SSH 포트 (기본 22)
            dry_run: Dry-run 모드 (기본 True)
        """
        super().__init__()

        self.server_id = server_id
        self.host = host
        self.username = username
        self.platform = platform
        self.rule_id = rule_id
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.dry_run = dry_run

        self._is_cancelled = False

    def run(self):
        """스레드 실행 (QThread 오버라이드)

        asyncio 이벤트 루프를 생성하여 _run_remediation()을 실행합니다.
        ScanWorker 패턴을 따라 loop.run_until_complete() 사용.
        """
        try:
            # 새 이벤트 루프 생성 (스레드마다 독립적)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 비동기 메서드 실행 및 완료 대기
            result = loop.run_until_complete(self._run_remediation())

            # 루프 정리
            loop.close()

            # 결과 emit (취소되지 않은 경우)
            if not self._is_cancelled:
                self.finished.emit(result)

        except Exception as e:
            logger.error(f"자동 수정 중 오류: {e}", exc_info=True)
            self.error.emit(f"자동 수정 실패: {str(e)}")

    async def _run_remediation(self) -> RemediationResult:
        """실제 자동 수정 실행 (비동기)

        Scanner 생성 → 연결 → 규칙 로드 → Remediator 생성 → 수정 실행

        Returns:
            RemediationResult: 수정 결과
        """
        self.log.emit(f"서버 연결 중: {self.host}...")

        # 플랫폼별 Scanner 생성
        scanner = self._create_scanner()

        try:
            # 1. 연결
            await scanner.connect()
            self.log.emit("서버 연결 성공")

            # 2. 규칙 로드
            await scanner.load_rules()
            self.log.emit(f"규칙 로드 완료 (총 {len(scanner._rules)}개)")

            # 3. 대상 규칙 찾기
            target_rule = None
            for rule in scanner._rules:
                if rule.id == self.rule_id:
                    target_rule = rule
                    break

            if not target_rule:
                raise ValueError(f"규칙을 찾을 수 없습니다: {self.rule_id}")

            if not target_rule.remediation or not target_rule.remediation.auto:
                raise ValueError(f"자동 수정이 지원되지 않는 규칙입니다: {self.rule_id}")

            self.log.emit(f"규칙 확인: {target_rule.name}")

            # 4. Remediator 생성
            remediator = self._create_remediator(scanner)

            # 5. 자동 수정 실행
            mode = "Dry-run" if self.dry_run else "실제 수정"
            self.log.emit(f"[{mode}] {self.rule_id} 실행 중...")
            self.progress.emit(0, 1, f"{self.rule_id} 수정 중...")

            result = await remediator.remediate(target_rule, dry_run=self.dry_run)

            self.progress.emit(1, 1, "완료!")

            status = "성공" if result.success else "실패"
            self.log.emit(f"[{status}] {result.message}")

            return result

        except Exception as e:
            # 오류 시에도 연결 해제 시도
            try:
                await scanner.disconnect()
            except:
                pass
            raise e

        finally:
            # 정상 종료 시 연결 해제
            try:
                await scanner.disconnect()
                self.log.emit("서버 연결 해제")
            except:
                pass

    def _create_scanner(self):
        """플랫폼별 Scanner 생성

        Returns:
            BaseScanner: 플랫폼에 맞는 Scanner 인스턴스

        Raises:
            ValueError: 지원하지 않는 플랫폼
        """
        if self.platform == "linux":
            from ...core.scanner import LinuxScanner
            return LinuxScanner(
                server_id=self.server_id,
                host=self.host,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
                port=self.port,
            )
        elif self.platform == "macos":
            from ...core.scanner import MacOSScanner
            return MacOSScanner(
                server_id=self.server_id,
                host=self.host,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
                port=self.port,
            )
        elif self.platform == "windows":
            # TODO: Windows Scanner 구현
            raise ValueError(f"Windows는 아직 지원되지 않습니다")
        else:
            raise ValueError(f"지원하지 않는 플랫폼: {self.platform}")

    def _create_remediator(self, scanner):
        """플랫폼별 Remediator 생성

        Args:
            scanner: Scanner 인스턴스 (SSHClient 재사용)

        Returns:
            BaseRemediator: 플랫폼에 맞는 Remediator 인스턴스

        Raises:
            ValueError: 지원하지 않는 플랫폼
        """
        if self.platform == "macos":
            from ...core.remediation import MacOSRemediator
            return MacOSRemediator(scanner)
        elif self.platform == "linux":
            # TODO: Linux Remediator 구현
            from ...core.remediation import MacOSRemediator
            return MacOSRemediator(scanner)  # 임시로 MacOS 사용
        elif self.platform == "windows":
            # TODO: Windows Remediator 구현
            raise ValueError(f"Windows Remediator는 아직 구현되지 않았습니다")
        else:
            raise ValueError(f"지원하지 않는 플랫폼: {self.platform}")

    def cancel(self):
        """자동 수정 취소"""
        self._is_cancelled = True
        self.log.emit("자동 수정 취소 중...")


__all__ = ["RemediationWorker"]
