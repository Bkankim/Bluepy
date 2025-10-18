"""
Linux 보안 점검 Validator 함수 모음 - 파일 및 디렉터리 관리

이 모듈은 KISA 기준 Linux 보안 점검 항목 중 파일 및 디렉터리 관리 관련
validator 함수들을 포함합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)
"""

from typing import List
from src.core.domain.models import CheckResult, Status


def check_u16(command_outputs: List[str]) -> CheckResult:
    """U-16: root 홈, 패스 디렉터리 권한 및 패스 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _16SCRIPT 로직:
    - 각 줄에 '.' 문자가 있는지 체크
    - '.' 있으면 FAIL, 없으면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: PATH 환경변수 또는 디렉터리 목록

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    path_content = command_outputs[0]
    lines = [line for line in path_content.split("\n") if line.strip()]

    for line in lines:
        if "." in line:
            return CheckResult(
                status=Status.FAIL, message=f"취약: PATH에 '.'이 포함되어 있습니다 - {line}"
            )

    return CheckResult(status=Status.PASS, message="안전: PATH에 '.'이 포함되어 있지 않습니다")


def check_u17(command_outputs: List[str]) -> CheckResult:
    """U-17: 파일 및 디렉터리 소유자 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _17SCRIPT 로직:
    - _SPLIT 사용 (2개 명령어 결과 분리)
    - data[0], data[1] 둘 다 비어있으면 PASS
    - 하나라도 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 첫 번째 명령어 결과
            - [1]: 두 번째 명령어 결과

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 부족합니다 (2개 필요)")

    data0 = command_outputs[0]
    data1 = command_outputs[1]

    lines0 = [line for line in data0.split("\n") if line.strip()]
    lines1 = [line for line in data1.split("\n") if line.strip()]

    if not lines0 and not lines1:
        return CheckResult(
            status=Status.PASS, message="안전: 소유자가 존재하지 않는 파일이 없습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL, message="취약: 소유자가 존재하지 않는 파일이 발견되었습니다"
        )


def check_u18(command_outputs: List[str]) -> CheckResult:
    """U-18: /etc/passwd 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _18SCRIPT 로직:
    - ls -l 출력에서 권한이 rw------- (644) 이고 소유자가 root인지 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력 (예: -rw------- 1 root root 1234 ...)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.MANUAL, message="파일 정보가 없습니다")

    # ls -l 출력 형식: -rw------- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw-------  (1:3 = rw, 4:6 = ---, 7:9 = ---)
    if len(permissions) >= 10:
        read_write = permissions[1:3] == "rw"
        group_none = permissions[4:7] == "---"
        other_none = permissions[7:10] == "---"

        if read_write and group_none and other_none and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw------- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u19(command_outputs: List[str]) -> CheckResult:
    """U-19: /etc/shadow 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _19SCRIPT 로직:
    - ls -l 출력 파싱
    - 권한 r-------- 및 소유자 root 체크

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.MANUAL, message="파일 정보가 없습니다")

    # ls -l 출력 형식: -r-------- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: r-------- (1:10 = r--------)
    if len(permissions) >= 10:
        if permissions[1:10] == "r--------" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (r-------- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u20(command_outputs: List[str]) -> CheckResult:
    """U-20: /etc/hosts 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _20SCRIPT 로직:
    - ls -l 출력 파싱
    - 권한 rw------- 및 소유자 root 체크

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.MANUAL, message="파일 정보가 없습니다")

    # ls -l 출력 형식: -rw------- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw------- (1:10 = rw-------)
    if len(permissions) >= 10:
        if permissions[1:10] == "rw-------" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw------- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u21(command_outputs: List[str]) -> CheckResult:
    """U-21: /etc/(x)inetd.conf 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _21SCRIPT 로직:
    - ls -l 출력 파싱
    - 권한 rw------- 및 소유자 root 체크
    - 파일이 없어도 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    # ls -l 출력 형식: -rw------- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw------- (1:10 = rw-------)
    if len(permissions) >= 10:
        if permissions[1:10] == "rw-------" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw------- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u22(command_outputs: List[str]) -> CheckResult:
    """U-22: /etc/syslog.conf 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _22SCRIPT 로직:
    - ls -l 출력 파싱
    - 권한 rw-r--r-- 및 소유자 root 체크
    - 파일이 없어도 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    # ls -l 출력 형식: -rw-r--r-- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw-r--r-- (1:10 = rw-r--r--)
    if len(permissions) >= 10:
        if permissions[1:10] == "rw-r--r--" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw-r--r-- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u23(command_outputs: List[str]) -> CheckResult:
    """U-23: /etc/services 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _23SCRIPT 로직:
    - ls -l 출력 파싱
    - 권한 rw-r--r-- 및 소유자 root 체크
    - 파일이 없어도 PASS
    - (_22SCRIPT와 동일한 로직)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    # ls -l 출력 형식: -rw-r--r-- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw-r--r-- (1:10 = rw-r--r--)
    if len(permissions) >= 10:
        if permissions[1:10] == "rw-r--r--" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw-r--r-- root 권장)",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u24(command_outputs: List[str]) -> CheckResult:
    """U-24: SUID, SGID, Sticky bit 설정파일 점검

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _24SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - SUID/SGID/Sticky bit 파일 목록을 추출하여 관리자가 확인 필요

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: find 명령어 결과 (SUID/SGID 파일 목록)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: SUID, SGID, Sticky bit 설정 파일 목록을 확인하고 불필요한 설정이 있는지 검토하세요",
    )


def check_u25(command_outputs: List[str]) -> CheckResult:
    """U-25: 사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _25SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - 주석: "추가 요망" (구현 미완성)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트 (사용 안 함, 수동 점검 항목)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: 사용자 및 시스템 시작파일(.profile, .bashrc 등)의 소유자 및 권한 설정을 확인하세요",
    )


def check_u26(command_outputs: List[str]) -> CheckResult:
    """U-26: world writable 파일 점검

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _26SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - world writable 파일 목록을 추출하여 관리자가 확인 필요
    - 심볼릭 링크(->) 처리 포함

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: find 명령어 결과 (world writable 파일 목록)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: world writable 파일 목록을 확인하고 불필요한 권한이 있는지 검토하세요",
    )


def check_u27(command_outputs: List[str]) -> CheckResult:
    """U-27: /dev에 존재하지 않는 device 파일 점검

    점검 항목을 자동으로 검증합니다.

    Legacy _27SCRIPT 로직:
    - 출력이 비어있으면 PASS (불필요한 device 파일 없음)
    - 출력이 있으면 FAIL (불필요한 device 파일 존재)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: find 명령어 결과 (존재하지 않아야 할 device 파일 목록)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.PASS, message="안전: 불필요한 device 파일이 없습니다")

    device_files = command_outputs[0].strip()
    lines = [line for line in device_files.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.PASS, message="안전: 불필요한 device 파일이 없습니다")
    else:
        file_list = ", ".join(lines[:5])  # 처음 5개만 표시
        if len(lines) > 5:
            file_list += f", ... (총 {len(lines)}개)"
        return CheckResult(
            status=Status.FAIL, message=f"취약: 불필요한 device 파일이 존재합니다 - {file_list}"
        )


def check_u28(command_outputs: List[str]) -> CheckResult:
    """U-28: $HOME/.rhosts, hosts.equiv 사용 금지

    점검 항목을 자동으로 검증합니다.

    Legacy _28SCRIPT 로직:
    - 3개 명령어 결과 모두 빈 출력이면 PASS (파일 없음)
    - 하나라도 있으면 각 파일이 rw------- root 권한인지 체크

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 첫 번째 파일 ls -l 출력
            - [1]: 두 번째 파일 ls -l 출력
            - [2]: 세 번째 파일 ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 3:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 부족합니다 (3개 필요)")

    # 모든 출력을 파싱
    all_empty = True
    for output in command_outputs:
        lines = [line for line in output.split("\n") if line.strip()]
        if lines:
            all_empty = False
            break

    # 모두 비어있으면 PASS (파일이 없음)
    if all_empty:
        return CheckResult(
            status=Status.PASS, message="안전: .rhosts 또는 hosts.equiv 파일이 없습니다"
        )

    # 하나라도 있으면 권한 체크
    for idx, output in enumerate(command_outputs):
        lines = [line for line in output.strip().split("\n") if line.strip()]
        if not lines:
            continue  # 빈 출력은 허용

        # ls -l 출력 형식: -rw------- 1 root root 1234 Jan 1 12:00 filename
        parts = lines[0].split()
        if len(parts) < 3:
            continue

        permissions = parts[0]
        owner = parts[2]

        # 권한 체크: rw------- root가 아니면 FAIL
        if len(permissions) >= 10:
            if not (permissions[1:10] == "rw-------" and owner == "root"):
                return CheckResult(
                    status=Status.FAIL,
                    message=f"취약: 파일 {idx+1}의 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw------- root 권장)",
                )

    # 모든 파일이 올바른 권한
    return CheckResult(
        status=Status.PASS,
        message="안전: 모든 파일이 올바른 권한(rw------- root)으로 설정되어 있습니다",
    )


def check_u29(command_outputs: List[str]) -> CheckResult:
    """U-29: 접속 IP 및 포트 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _29SCRIPT 로직:
    - 2개 명령어 결과 분리
    - 첫 번째 결과에서 'ALL:ALL' 찾기 (주석 제외)
    - 'ALL:ALL'이 있으면 PASS, 없으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: hosts.deny 또는 유사 파일 내용
            - [1]: (선택적) 추가 설정 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    # 첫 번째 명령어 결과 파싱
    first_output = command_outputs[0]
    lines = [line for line in first_output.split("\n") if line.strip()]

    # 주석이 아닌 라인에서 'ALL:ALL' 찾기
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped[0] == "#":
            continue
        if stripped == "ALL:ALL":
            return CheckResult(status=Status.PASS, message="안전: 'ALL:ALL' 설정이 존재합니다")

    return CheckResult(
        status=Status.FAIL,
        message="취약: 'ALL:ALL' 설정이 없습니다. 접속 IP 및 포트 제한이 설정되지 않았습니다",
    )


def check_u30(command_outputs: List[str]) -> CheckResult:
    """U-30: hosts.lpd 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _30SCRIPT 로직:
    - 빈 출력이면 PASS (파일 없음)
    - 권한[8]이 '-'이고 소유자가 root이면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -l 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split("\n") if line.strip()]

    if not lines:
        return CheckResult(status=Status.PASS, message="안전: 파일이 없습니다")

    # ls -l 출력 형식: -rw-r--r-- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(status=Status.MANUAL, message="ls 출력 형식이 올바르지 않습니다")

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한[8] (other 실행 권한)이 '-'이고 소유자가 root인지 체크
    if len(permissions) >= 10:
        if permissions[9] == "-" and owner == "root":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다",
            )
    else:
        return CheckResult(status=Status.MANUAL, message="권한 문자열 형식이 올바르지 않습니다")


def check_u31(command_outputs: List[str]) -> CheckResult:
    """U-31: NIS 서비스 비활성화

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _31SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - NIS 관련 프로세스 목록을 추출하여 관리자가 확인 필요

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ps 명령어 결과 (NIS 프로세스 목록)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: NIS 서비스(ypbind, ypserv 등) 실행 여부를 확인하고 불필요시 비활성화하세요",
    )


def check_u32(command_outputs: List[str]) -> CheckResult:
    """U-32: UMASK 설정 관리

    점검 항목을 자동으로 검증합니다.

    Legacy _32SCRIPT 로직:
    - umask 설정 파일에서 'umask 022' 찾기 (주석 제외)
    - 'umask 022'가 있으면 PASS, 없으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 설정 파일 내용 (예: /etc/profile)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    config_content = command_outputs[0]
    lines = [line for line in config_content.split("\n")]

    # 주석이 아닌 라인에서 'umask' 찾기
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped[0] == "#":
            continue
        if "umask" in stripped:
            parts = [p for p in stripped.split(" ") if p]
            # 'umask 022' 형태 찾기
            if len(parts) >= 2 and parts[0] == "umask" and parts[1] == "022":
                return CheckResult(status=Status.PASS, message="안전: umask 022 설정이 존재합니다")

    return CheckResult(status=Status.FAIL, message="취약: umask 022 설정이 없습니다")


def check_u33(command_outputs: List[str]) -> CheckResult:
    """U-33: 홈 디렉토리 소유자 및 권한 설정

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _33SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - 주석: "추가 요망" (구현 미완성)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트 (사용 안 함, 수동 점검 항목)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: 각 사용자의 홈 디렉토리 소유자 및 권한 설정이 올바른지 확인하세요",
    )


def check_u34(command_outputs: List[str]) -> CheckResult:
    """U-34: 홈 디렉토리로 지정한 디렉터리의 존재 관리

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _34SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - 사용자와 홈 디렉터리 목록을 추출하여 관리자가 확인 필요

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: passwd 파일 내용 (사용자 및 홈 디렉터리 정보)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: 각 사용자의 홈 디렉터리가 실제로 존재하는지 확인하세요",
    )


def check_u35(command_outputs: List[str]) -> CheckResult:
    """U-35: 숨겨진 파일 및 디렉터리 검색 및 제거

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _35SCRIPT 로직:
    - 항상 수동 점검 (MANUAL)
    - 주석: "추가 요망" (구현 미완성)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트 (사용 안 함, 수동 점검 항목)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: 시스템 내 숨겨진 파일 및 디렉터리(. 시작)를 검색하고 불필요한 파일이 있는지 확인하세요",
    )
