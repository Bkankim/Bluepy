"""Scanner Worker

QThread를 사용하여 백그라운드에서 스캔을 실행하는 Worker입니다.

주요 기능:
- 비동기 Scanner 실행
- 진행률 시그널 emit
- 결과 반환
"""

import asyncio
import logging
from typing import Optional

from PySide6.QtCore import QThread, Signal

from ...core.scanner import LinuxScanner, ScanResult

logger = logging.getLogger(__name__)


class ScanWorker(QThread):
    """스캔 Worker 클래스

    QThread를 사용하여 백그라운드에서 Scanner를 실행합니다.

    Signals:
        progress: 진행률 업데이트 (current: int, total: int, message: str)
        log: 로그 메시지 (message: str)
        finished: 스캔 완료 (result: ScanResult)
        error: 오류 발생 (error_message: str)
    """

    # 커스텀 시그널
    progress = Signal(int, int, str)  # current, total, message
    log = Signal(str)
    finished = Signal(object)  # ScanResult
    error = Signal(str)

    def __init__(
        self,
        server_id: str,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        rules_dir: str = "config/rules",
    ):
        """초기화

        Args:
            server_id: 서버 ID
            host: 호스트 주소
            username: SSH 사용자명
            password: SSH 패스워드 (선택)
            key_filename: SSH 키 파일 경로 (선택)
            port: SSH 포트
            rules_dir: 규칙 디렉토리
        """
        super().__init__()

        self.server_id = server_id
        self.host = host
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.rules_dir = rules_dir

        self._is_cancelled = False

    def run(self):
        """스레드 실행 (오버라이드)"""
        try:
            # asyncio 이벤트 루프 생성 및 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(self._run_scan())

            loop.close()

            # 결과 시그널 emit
            if not self._is_cancelled:
                self.finished.emit(result)

        except Exception as e:
            logger.error(f"스캔 중 오류: {e}")
            self.error.emit(f"스캔 실패: {str(e)}")

    async def _run_scan(self) -> ScanResult:
        """실제 스캔 실행

        Returns:
            ScanResult
        """
        self.log.emit(f"서버 연결 중: {self.host}...")

        # Scanner 생성
        scanner = LinuxScanner(
            server_id=self.server_id,
            host=self.host,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename,
            port=self.port,
        )

        try:
            # 연결
            await scanner.connect()
            self.log.emit("서버 연결 성공")

            # 규칙 로드
            await scanner.load_rules(self.rules_dir)
            total_rules = scanner.get_rules_count()
            self.log.emit(f"규칙 {total_rules}개 로드 완료")

            # 스캔 실행
            self.log.emit("스캔 시작...")
            self.progress.emit(0, total_rules, "스캔 준비 중...")

            result = await self._scan_with_progress(scanner, total_rules)

            # 연결 해제
            await scanner.disconnect()
            self.log.emit("서버 연결 해제")

            return result

        except Exception as e:
            # 오류 시에도 연결 해제 시도
            try:
                await scanner.disconnect()
            except:
                pass

            raise e

    async def _scan_with_progress(self, scanner: LinuxScanner, total: int) -> ScanResult:
        """진행률 업데이트와 함께 스캔 실행

        Args:
            scanner: LinuxScanner 인스턴스
            total: 전체 규칙 수

        Returns:
            ScanResult
        """
        # Scanner의 scan_all()을 호출하되, 각 규칙마다 진행률 업데이트
        # 현재 BaseScanner.scan_all()은 순차 실행이므로, 여기서 직접 구현

        result = ScanResult(server_id=scanner.server_id, platform=scanner.platform)

        current = 0
        for rule in scanner._rules:
            if self._is_cancelled:
                break

            current += 1
            self.progress.emit(current, total, f"{rule.id} 점검 중...")
            self.log.emit(f"[{current}/{total}] {rule.id}: {rule.name}")

            try:
                check_result = await scanner.scan_one(rule)
                result.results[rule.id] = check_result
            except Exception as e:
                logger.error(f"{rule.id} 점검 실패: {e}")
                self.log.emit(f"[오류] {rule.id}: {str(e)}")

        self.progress.emit(total, total, "스캔 완료!")
        return result

    def cancel(self):
        """스캔 취소"""
        self._is_cancelled = True
        self.log.emit("스캔 취소 중...")


__all__ = [
    "ScanWorker",
]
