"""Dialogs 모듈

GUI 대화상자 컴포넌트를 제공합니다.

주요 대화상자:
- server_dialog: 서버 추가/편집 대화상자
- remediation_dialog: 자동 수정 대화상자
"""

from .server_dialog import ServerDialog
from .remediation_dialog import RemediationDialog

__all__ = [
    "ServerDialog",
    "RemediationDialog",
]
