"""Remediation 모듈

자동 수정 기능을 제공합니다.

주요 클래스:
- BaseRemediator: 자동 수정 추상 클래스
- LinuxRemediator: Linux 자동 수정 (10개 규칙 지원)
- MacOSRemediator: macOS 자동 수정 (5개 규칙 지원)
- WindowsRemediator: Windows 자동 수정 (30개 규칙 지원)
- BackupManager: 백업/롤백 관리자
"""

from .backup_manager import BackupManager
from .base_remediator import BaseRemediator
from .linux_remediator import LinuxRemediator
from .macos_remediator import MacOSRemediator
from .windows_remediator import WindowsRemediator

__all__ = [
    "BackupManager",
    "BaseRemediator",
    "LinuxRemediator",
    "MacOSRemediator",
    "WindowsRemediator",
]
