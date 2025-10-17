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

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _16SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-16 root 홈, 패스 디렉터리 권한 및 패스 설정"
    )



def check_u17(command_outputs: List[str]) -> CheckResult:
    """U-17: 파일 및 디렉터리 소유자 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _17SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-17 파일 및 디렉터리 소유자 설정"
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
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 없습니다"
        )

    ls_output = command_outputs[0].strip()
    lines = [line for line in ls_output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.MANUAL,
            message="파일 정보가 없습니다"
        )

    # ls -l 출력 형식: -rw------- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(
            status=Status.MANUAL,
            message="ls 출력 형식이 올바르지 않습니다"
        )

    permissions = parts[0]
    owner = parts[2] if len(parts) >= 3 else ""

    # 권한 체크: rw-------  (1:3 = rw, 4:6 = ---, 7:9 = ---)
    if len(permissions) >= 10:
        read_write = permissions[1:3] == 'rw'
        group_none = permissions[4:7] == '---'
        other_none = permissions[7:10] == '---'

        if read_write and group_none and other_none and owner == 'root':
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 파일 권한이 {permissions}이고 소유자가 root입니다"
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw------- root 권장)"
            )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="권한 문자열 형식이 올바르지 않습니다"
        )



def check_u19(command_outputs: List[str]) -> CheckResult:
    """U-19: /etc/shadow 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _19SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-19 /etc/shadow 파일 소유자 및 권한 설정"
    )



def check_u20(command_outputs: List[str]) -> CheckResult:
    """U-20: /etc/hosts 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _20SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-20 /etc/hosts 파일 소유자 및 권한 설정"
    )



def check_u21(command_outputs: List[str]) -> CheckResult:
    """U-21: /etc/(x)inetd.conf 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _21SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-21 /etc/(x)inetd.conf 파일 소유자 및 권한 설정"
    )



def check_u22(command_outputs: List[str]) -> CheckResult:
    """U-22: /etc/syslog.conf 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _22SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-22 /etc/syslog.conf 파일 소유자 및 권한 설정"
    )



def check_u23(command_outputs: List[str]) -> CheckResult:
    """U-23: /etc/services 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _23SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-23 /etc/services 파일 소유자 및 권한 설정"
    )



def check_u24(command_outputs: List[str]) -> CheckResult:
    """U-24: SUID, SGID, Sticky bit 설정파일 점검

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _24SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-24 SUID, SGID, Sticky bit 설정파일 점검"
    )



def check_u25(command_outputs: List[str]) -> CheckResult:
    """U-25: 사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _25SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-25 사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정"
    )



def check_u26(command_outputs: List[str]) -> CheckResult:
    """U-26: world writable 파일 점검

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _26SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-26 world writable 파일 점검"
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
        return CheckResult(
            status=Status.PASS,
            message="안전: 불필요한 device 파일이 없습니다"
        )

    device_files = command_outputs[0].strip()
    lines = [line for line in device_files.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: 불필요한 device 파일이 없습니다"
        )
    else:
        file_list = ', '.join(lines[:5])  # 처음 5개만 표시
        if len(lines) > 5:
            file_list += f', ... (총 {len(lines)}개)'
        return CheckResult(
            status=Status.FAIL,
            message=f"취약: 불필요한 device 파일이 존재합니다 - {file_list}"
        )



def check_u28(command_outputs: List[str]) -> CheckResult:
    """U-28: $HOME/.rhosts, hosts.equiv 사용 금지

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _28SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-28 $HOME/.rhosts, hosts.equiv 사용 금지"
    )



def check_u29(command_outputs: List[str]) -> CheckResult:
    """U-29: 접속 IP 및 포트 제한

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _29SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: high
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-29 접속 IP 및 포트 제한"
    )



def check_u30(command_outputs: List[str]) -> CheckResult:
    """U-30: hosts.lpd 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _30SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: low
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-30 hosts.lpd 파일 소유자 및 권한 설정"
    )



def check_u31(command_outputs: List[str]) -> CheckResult:
    """U-31: NIS 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _31SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: mid
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-31 NIS 서비스 비활성화"
    )



def check_u32(command_outputs: List[str]) -> CheckResult:
    """U-32: UMASK 설정 관리

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _32SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: mid
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-32 UMASK 설정 관리"
    )



def check_u33(command_outputs: List[str]) -> CheckResult:
    """U-33: 홈 디렉토리 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _33SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: mid
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-33 홈 디렉토리 소유자 및 권한 설정"
    )



def check_u34(command_outputs: List[str]) -> CheckResult:
    """U-34: 홈 디렉토리로 지정한 디렉터리의 존재 관리

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _34SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: mid
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-34 홈 디렉토리로 지정한 디렉터리의 존재 관리"
    )



def check_u35(command_outputs: List[str]) -> CheckResult:
    """U-35: 숨겨진 파일 및 디렉터리 검색 및 제거

    점검 항목을 자동으로 검증합니다.

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - 각 문자열은 하나의 명령어 실행 결과
            - 빈 리스트는 명령어가 없거나 수동 점검 항목

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지

    TODO: 구현 필요
        - Legacy 코드 _35SCRIPT의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: low
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - U-35 숨겨진 파일 및 디렉터리 검색 및 제거"
    )


