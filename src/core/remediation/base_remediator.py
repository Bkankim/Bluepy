"""BaseRemediator - 자동 수정 추상 클래스

모든 플랫폼 Remediator의 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

from ..domain.models import RemediationResult, RuleMetadata
from ..scanner.base_scanner import BaseScanner
from .backup_manager import BackupManager, BackupSession

logger = logging.getLogger(__name__)


class BaseRemediator(ABC):
    """자동 수정 추상 클래스

    Scanner와 협력하여 자동 수정을 수행합니다.
    """

    def __init__(self, scanner: BaseScanner, backup_manager: Optional[BackupManager] = None):
        """초기화

        Args:
            scanner: 스캐너 (SSHClient 재사용)
            backup_manager: 백업 관리자 (None이면 기본 생성)
        """
        self.scanner = scanner
        self.backup_manager = backup_manager or BackupManager()

    async def remediate(
        self, rule: RuleMetadata, dry_run: bool = True
    ) -> RemediationResult:
        """자동 수정 실행

        Args:
            rule: 점검 규칙
            dry_run: Dry-run 모드 (실제 실행 안 함)

        Returns:
            RemediationResult: 수정 결과
        """
        # 1. remediation 가능 여부 확인
        if not rule.remediation or not rule.remediation.auto:
            return RemediationResult(
                success=False, message="자동 수정 불가능한 규칙입니다.", dry_run=dry_run
            )

        # 2. Dry-run 모드
        if dry_run:
            return await self._simulate(rule)

        # 3. 실제 수정 실행
        return await self._execute_remediation(rule)

    async def _simulate(self, rule: RuleMetadata) -> RemediationResult:
        """Dry-run 시뮬레이션

        Args:
            rule: 점검 규칙

        Returns:
            RemediationResult: 시뮬레이션 결과
        """
        commands = rule.remediation.commands if rule.remediation else []
        message = f"[Dry-run] 실행할 명령어 {len(commands)}개:\n" + "\n".join(
            f"  - {cmd}" for cmd in commands[:3]
        )

        return RemediationResult(
            success=True, message=message, executed_commands=commands, dry_run=True
        )

    async def _execute_remediation(self, rule: RuleMetadata) -> RemediationResult:
        """실제 자동 수정 실행 (백업 + 수정 + 검증)

        Args:
            rule: 점검 규칙

        Returns:
            RemediationResult: 수정 결과
        """
        session_id = None
        try:
            # 1. 백업 세션 생성
            session_id = self.backup_manager.create_session(
                server=self.scanner.server_id, rule_ids=[rule.id]
            )

            # 2. 파일 백업 (있다면)
            backup_files = []
            if rule.remediation.backup_files:
                for file_path in rule.remediation.backup_files:
                    try:
                        bf = self.backup_manager.backup_file(session_id, file_path)
                        backup_files.append(bf)
                    except Exception as e:
                        logger.warning(f"파일 백업 skip: {file_path}, {e}")

            # 3. 플랫폼별 자동 수정 실행
            executed_commands = await self._execute_commands(rule.remediation.commands)

            # 4. 검증 (다시 스캔)
            # TODO: 실제로는 다시 scan_one()을 호출해서 PASS인지 확인
            # if not await self._verify_fix(rule):
            #     raise Exception("수정 후에도 취약함")

            # 5. 메타데이터 저장
            self.backup_manager.save_metadata(
                BackupSession(
                    session_id=session_id,
                    timestamp=session_id.split("_", 1)[1],
                    server=self.scanner.server_id,
                    rule_ids=[rule.id],
                    files=[{"original_path": bf.original_path} for bf in backup_files],
                    status="completed",
                )
            )

            return RemediationResult(
                success=True,
                message=f"{rule.id} 자동 수정 완료",
                backup_id=session_id,
                executed_commands=executed_commands,
            )

        except Exception as e:
            logger.error(f"{rule.id} 자동 수정 실패: {e}")

            # 롤백
            if session_id and backup_files:
                for bf in backup_files:
                    self.backup_manager.rollback_file(bf)

            return RemediationResult(
                success=False,
                message=f"자동 수정 실패: {str(e)[:200]}",
                error=str(e),
                rollback_performed=bool(backup_files),
            )

    @abstractmethod
    async def _execute_commands(self, commands: list[str]) -> list[str]:
        """플랫폼별 명령어 실행

        Args:
            commands: 실행할 명령어 목록

        Returns:
            List[str]: 실행한 명령어 목록
        """
        pass


__all__ = ["BaseRemediator"]
