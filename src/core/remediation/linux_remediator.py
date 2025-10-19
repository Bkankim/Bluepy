"""LinuxRemediator - Linux 자동 수정

Linux 자동 수정 가능 규칙을 지원합니다.
지원 규칙:
- U-18: /etc/passwd 파일 권한 설정
- U-19: /etc/shadow 파일 권한 설정
- U-22: /etc/syslog.conf 파일 권한 설정
- U-23: /etc/services 파일 권한 설정
- U-39: cron 파일 권한 설정
"""

from typing import List
import logging

from .base_remediator import BaseRemediator

logger = logging.getLogger(__name__)


class LinuxRemediator(BaseRemediator):
    """Linux 자동 수정

    Linux의 자동 수정 가능한 규칙들을 지원합니다.
    BaseRemediator가 백업/롤백/dry-run을 자동 처리하므로,
    명령어 실행 로직만 구현합니다.
    """

    async def _execute_commands(self, commands: List[str]) -> List[str]:
        """Linux 명령어 실행

        Args:
            commands: 실행할 명령어 목록 (YAML remediation.commands)

        Returns:
            List[str]: 실행 성공한 명령어 목록

        Raises:
            Exception: 명령어 실행 실패 시 (BaseRemediator가 롤백 처리)
        """
        executed = []

        for cmd in commands:
            try:
                # Scanner의 SSH 연결 재사용
                result = await self.scanner.execute_command(cmd)
                executed.append(cmd)
                logger.info(f"명령어 실행 완료: {cmd[:50]}...")
            except Exception as e:
                logger.error(f"명령어 실행 실패: {cmd[:50]}..., {e}")
                # Exception 발생 -> BaseRemediator가 자동 롤백
                raise Exception(f"명령어 실행 실패: {cmd[:30]}... ({e})")

        return executed


__all__ = ["LinuxRemediator"]
