"""MacOSRemediator - macOS 자동 수정

macOS 5개 자동 수정 가능 규칙을 지원합니다.
- M-03: Gatekeeper (spctl)
- M-04: Firewall (socketfilterfw)
- M-05: Automatic Updates (defaults)
- M-06: Screen Saver Password (defaults)
- M-07: Guest Account (defaults)
- M-08: Remote Login (systemsetup)
"""

from typing import List
import logging

from .base_remediator import BaseRemediator

logger = logging.getLogger(__name__)


class MacOSRemediator(BaseRemediator):
    """macOS 자동 수정

    macOS의 자동 수정 가능한 5개 규칙을 지원합니다.
    """

    async def _execute_commands(self, commands: List[str]) -> List[str]:
        """macOS 명령어 실행

        Args:
            commands: 실행할 명령어 목록

        Returns:
            List[str]: 실행한 명령어 목록
        """
        executed = []

        for cmd in commands:
            try:
                # Scanner의 execute_command() 재사용
                result = await self.scanner.execute_command(cmd)
                executed.append(cmd)
                logger.info(f"명령어 실행 완료: {cmd[:50]}...")
            except Exception as e:
                logger.error(f"명령어 실행 실패: {cmd[:50]}..., {e}")
                raise Exception(f"명령어 실행 실패: {cmd[:30]}... ({e})")

        return executed


__all__ = ["MacOSRemediator"]
