"""macOS Validators

macOS 보안 점검 validator 함수들을 제공합니다.

각 함수는 명령어 출력을 받아 CheckResult를 반환합니다.
- check_m01 ~ check_m10: macOS 전용 점검 항목
"""

from .system_protection import check_m01, check_m10
from .data_protection import check_m02, check_m09
from .application_security import check_m03
from .network_security import check_m04, check_m08
from .patch_management import check_m05
from .access_control import check_m06, check_m07

__all__ = [
    # System Protection
    "check_m01",  # SIP
    "check_m10",  # Firmware Password
    # Data Protection
    "check_m02",  # FileVault
    "check_m09",  # Time Machine Encryption
    # Application Security
    "check_m03",  # Gatekeeper
    # Network Security
    "check_m04",  # Firewall
    "check_m08",  # Remote Login/Management
    # Patch Management
    "check_m05",  # Automatic Updates
    # Access Control
    "check_m06",  # Screen Saver Password
    "check_m07",  # Guest Account
]
