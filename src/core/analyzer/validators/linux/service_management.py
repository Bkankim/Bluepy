"""
Linux 보안 점검 Validator 함수 모음 - 서비스 관리

이 모듈은 KISA 기준 Linux 보안 점검 항목 중 서비스 관리 관련
validator 함수들을 포함합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)
"""

from typing import List
from src.core.domain.models import CheckResult, Status


def check_u36(command_outputs: List[str]) -> CheckResult:
    """U-36: Finger 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _36SCRIPT 로직:
    - /etc/inetd.conf 파일에서 finger 서비스 확인
    - 출력이 없으면 PASS (서비스 비활성화)
    - 출력이 있으면 FAIL (서비스 활성화)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/inetd.conf 파일 내용 또는 ps 출력

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Finger 서비스가 비활성화되어 있습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: Finger 서비스가 활성화되어 있습니다"
        )



def check_u37(command_outputs: List[str]) -> CheckResult:
    """U-37: Anonymous FTP 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _37SCRIPT 로직:
    - /etc/passwd에서 ftp 계정 확인
    - 출력이 없으면 PASS (FTP 계정 없음)
    - 출력이 있으면 FAIL (FTP 계정 존재)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ftp 계정 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Anonymous FTP 계정이 존재하지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: Anonymous FTP 계정이 존재합니다"
        )



def check_u38(command_outputs: List[str]) -> CheckResult:
    """U-38: r계열 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _38SCRIPT 로직:
    - rsh, rlogin, rexec 서비스 확인
    - 출력이 없으면 PASS (서비스 비활성화)
    - 출력이 있으면 FAIL (서비스 활성화)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: r계열 서비스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: r계열 서비스(rsh, rlogin, rexec)가 비활성화되어 있습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: r계열 서비스가 활성화되어 있습니다"
        )



def check_u39(command_outputs: List[str]) -> CheckResult:
    """U-39: cron 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _39SCRIPT 로직:
    - ls -al /var/spool/cron/crontabs/* 출력 파싱
    - 파일이 없거나 권한이 rw-r----- root이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: ls -al 출력

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(
            status=Status.PASS,
            message="안전: cron 파일이 없습니다"
        )

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: cron 파일이 없습니다"
        )

    # ls -l 출력 형식: -rw-r----- 1 root root 1234 Jan 1 12:00 filename
    parts = lines[0].split()
    if len(parts) < 3:
        return CheckResult(
            status=Status.MANUAL,
            message="ls 출력 형식이 올바르지 않습니다"
        )

    permissions = parts[0]
    owner = parts[2]

    # 권한 체크: rw-r----- (1:10 = rw-r-----)
    if len(permissions) >= 10:
        if permissions[1:10] == 'rw-r-----' and owner == 'root':
            return CheckResult(
                status=Status.PASS,
                message=f"안전: cron 파일 권한이 {permissions}이고 소유자가 root입니다"
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: cron 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다 (rw-r----- root 권장)"
            )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="권한 문자열 형식이 올바르지 않습니다"
        )



def check_u40(command_outputs: List[str]) -> CheckResult:
    """U-40: DOS 공격에 취약한 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _40SCRIPT 로직:
    - _SPLIT(data) → 4개 명령어 (echo, discard, daytime, chargen)
    - 모든 출력이 비어있으면 PASS
    - 하나라도 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0~3]: echo, discard, daytime, chargen 서비스 설정 파일

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

    # 모든 명령어 결과 확인
    for idx, output in enumerate(command_outputs):
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if lines:
            # 하나라도 서비스가 활성화되어 있음
            service_names = ["echo", "discard", "daytime", "chargen"]
            service_name = service_names[idx] if idx < len(service_names) else f"서비스 {idx+1}"
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: DOS 취약 서비스({service_name})가 활성화되어 있습니다"
            )

    # 모든 서비스가 비활성화
    return CheckResult(
        status=Status.PASS,
        message="안전: DOS 취약 서비스(echo, discard, daytime, chargen)가 모두 비활성화되어 있습니다"
    )



def check_u41(command_outputs: List[str]) -> CheckResult:
    """U-41: NFS 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _41SCRIPT 로직:
    - ps -ef | grep nfsd 출력 확인
    - 출력이 없으면 PASS (NFS 서비스 비활성화)
    - 출력이 있으면 FAIL (NFS 서비스 활성화)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: nfsd 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: NFS 서비스가 비활성화되어 있습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: NFS 서비스가 활성화되어 있습니다"
        )



def check_u42(command_outputs: List[str]) -> CheckResult:
    """U-42: NFS 접근 통제

    점검 항목을 자동으로 검증합니다.

    Legacy _42SCRIPT 로직:
    - /etc/exports 파일 내용 확인
    - _DELGREP (grep 라인 제외) 후 출력이 없으면 PASS
    - 출력이 있으면 FAIL (NFS export 설정 존재)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/exports 파일 내용

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

    output = command_outputs[0].strip()
    # grep이 포함된 라인 제외 (_DELGREP)
    lines = [line for line in output.split('\n') if line.strip() and 'grep' not in line]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: NFS export 설정이 없습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: NFS export 설정이 존재합니다"
        )



def check_u43(command_outputs: List[str]) -> CheckResult:
    """U-43: automountd 제거

    점검 항목을 자동으로 검증합니다.

    Legacy _43SCRIPT 로직:
    - ps -ef | grep automount 출력 확인
    - 출력이 없으면 PASS (automountd 제거됨)
    - 출력이 있으면 FAIL (automountd 실행 중)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: automount 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: automountd가 제거되었습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: automountd가 실행 중입니다"
        )



def check_u44(command_outputs: List[str]) -> CheckResult:
    """U-44: RPC 서비스 확인

    점검 항목을 자동으로 검증합니다.

    Legacy _44SCRIPT 로직:
    - ps -ef | egrep "rpc.*|sadmind|..." 출력 확인
    - grep이 포함된 라인 제외
    - 빈 출력이면 PASS, 출력이 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: RPC 관련 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    # grep이 포함된 라인 제외
    lines = [line for line in output.split('\n') if line.strip() and 'grep' not in line]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: RPC 관련 서비스가 실행되지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: RPC 관련 서비스가 실행 중입니다"
        )



def check_u45(command_outputs: List[str]) -> CheckResult:
    """U-45: NIS, NIS+ 점검

    점검 항목을 자동으로 검증합니다.

    Legacy _45SCRIPT 로직:
    - ps -ef | egrep "ypserv|ypbind|..." 출력 확인
    - grep이 포함된 라인 제외
    - 빈 출력이면 PASS, 출력이 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: NIS/NIS+ 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    # grep이 포함된 라인 제외
    lines = [line for line in output.split('\n') if line.strip() and 'grep' not in line]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: NIS/NIS+ 서비스가 실행되지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: NIS/NIS+ 서비스가 실행 중입니다"
        )



def check_u46(command_outputs: List[str]) -> CheckResult:
    """U-46: tftp, talk 서비스 비활성화

    점검 항목을 자동으로 검증합니다.

    Legacy _46SCRIPT 로직:
    - ps -ef | egrep "tftp|talk" 출력 확인
    - grep이 포함된 라인 제외
    - 빈 출력이면 PASS, 출력이 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: tftp, talk 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    # grep이 포함된 라인 제외
    lines = [line for line in output.split('\n') if line.strip() and 'grep' not in line]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: tftp, talk 서비스가 비활성화되어 있습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: tftp 또는 talk 서비스가 실행 중입니다"
        )



def check_u47(command_outputs: List[str]) -> CheckResult:
    """U-47: Sendmail 버전 점검

    점검 항목을 자동으로 검증합니다.

    Legacy _47SCRIPT 로직:
    - ps -ef | grep sendmail 출력 확인
    - 빈 출력이면 PASS (Sendmail 없음)
    - 출력이 있으면 MANUAL (버전 확인 필요)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: sendmail 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Sendmail이 실행되지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="수동 점검: Sendmail 버전을 확인하세요"
        )



def check_u48(command_outputs: List[str]) -> CheckResult:
    """U-48: 스팸 메일 릴레이 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _48SCRIPT 로직:
    - 2개 명령어: sendmail 실행 여부 + 설정 파일
    - sendmail이 없으면 PASS
    - 설정 파일에서 "Relaying denied" 확인
    - 주석(#)이면 FAIL, 아니면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: sendmail 프로세스 조회 결과
            - [1]: sendmail.cf 설정 파일 (Relaying denied)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 부족합니다"
        )

    sendmail_output = command_outputs[0].strip()
    lines = [line for line in sendmail_output.split('\n') if line.strip()]

    # sendmail이 실행되지 않으면 PASS
    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Sendmail이 실행되지 않습니다"
        )

    # 설정 파일 확인
    config_output = command_outputs[1].strip()
    config_lines = [line for line in config_output.split('\n') if line.strip()]

    if not config_lines:
        return CheckResult(
            status=Status.FAIL,
            message="취약: Relaying denied 설정이 없습니다"
        )

    # 주석이 아닌 라인 확인
    for line in config_lines:
        if line.strip() and line.strip()[0] != '#':
            return CheckResult(
                status=Status.PASS,
                message="안전: Relaying denied 설정이 활성화되어 있습니다"
            )

    return CheckResult(
        status=Status.FAIL,
        message="취약: Relaying denied 설정이 주석 처리되어 있습니다"
    )



def check_u49(command_outputs: List[str]) -> CheckResult:
    """U-49: 스팸 메일 릴레이 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _49SCRIPT 로직:
    - 2개 명령어: sendmail 실행 여부 + 설정 파일
    - sendmail이 없으면 PASS
    - 설정 파일 확인 (PrivacyOptions)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: sendmail 프로세스 조회 결과
            - [1]: sendmail.cf 설정 파일 (PrivacyOptions)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 부족합니다"
        )

    sendmail_output = command_outputs[0].strip()
    lines = [line for line in sendmail_output.split('\n') if line.strip()]

    # sendmail이 실행되지 않으면 PASS
    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Sendmail이 실행되지 않습니다"
        )

    # 설정 파일 확인 (PrivacyOptions)
    config_output = command_outputs[1].strip()
    config_lines = [line for line in config_output.split('\n') if line.strip()]

    if not config_lines:
        return CheckResult(
            status=Status.FAIL,
            message="취약: PrivacyOptions 설정이 없습니다"
        )

    return CheckResult(
        status=Status.PASS,
        message="안전: PrivacyOptions 설정이 존재합니다"
    )



def check_u50(command_outputs: List[str]) -> CheckResult:
    """U-50: DNS 보안 버전 패치

    점검 항목을 자동으로 검증합니다.

    Legacy _50SCRIPT 로직:
    - ps -ef | grep named 출력 확인
    - 빈 출력이면 PASS (DNS 없음)
    - 출력이 있으면 MANUAL (버전 확인 필요)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: named 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: DNS(named) 서비스가 실행되지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="수동 점검: DNS 버전을 확인하고 최신 보안 패치를 적용하세요"
        )



def check_u51(command_outputs: List[str]) -> CheckResult:
    """U-51: DNS Zone Transfer 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _51SCRIPT 로직:
    - 3개 명령어: named 실행 여부 + 설정 파일 2개
    - named가 없으면 PASS
    - 설정 파일 확인 (MANUAL)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: named 프로세스 조회 결과
            - [1]: named.conf 설정 파일 (allow-transfer)
            - [2]: named.boot 설정 파일 (xfrnets)

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

    named_output = command_outputs[0].strip()
    lines = [line for line in named_output.split('\n') if line.strip()]

    # named가 실행되지 않으면 PASS
    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: DNS(named) 서비스가 실행되지 않습니다"
        )

    # named가 실행 중이면 MANUAL (설정 확인 필요)
    return CheckResult(
        status=Status.MANUAL,
        message="수동 점검: DNS Zone Transfer 설정을 확인하세요 (allow-transfer, xfrnets)"
    )



def check_u52(command_outputs: List[str]) -> CheckResult:
    """U-52: Apache 디렉터리 리스팅 제거

    점검 항목을 자동으로 검증합니다.

    Legacy _52SCRIPT 로직:
    - httpd.conf 파일에서 "Indexes" 검색
    - 빈 출력이면 PASS
    - "Indexes"가 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf 파일에서 Indexes 검색 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 디렉터리 리스팅이 비활성화되어 있습니다"
        )

    # "Indexes"가 있으면 FAIL
    for line in lines:
        if 'Indexes' in line:
            return CheckResult(
                status=Status.FAIL,
                message="취약: Apache 디렉터리 리스팅이 활성화되어 있습니다 (Indexes 옵션)"
            )

    return CheckResult(
        status=Status.PASS,
        message="안전: Apache 디렉터리 리스팅이 비활성화되어 있습니다"
    )



def check_u53(command_outputs: List[str]) -> CheckResult:
    """U-53: Apache 웹 프로세스 권한 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _53SCRIPT 로직:
    - httpd.conf 파일에서 User/Group 검색
    - 빈 출력이면 PASS
    - "User root" 또는 "Group root"가 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf 파일에서 User/Group 검색 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없거나 User/Group 설정이 없습니다"
        )

    # "User root" 또는 "Group root" 체크
    for line in lines:
        if ('User' in line and 'root' in line) or ('Group' in line and 'root' in line):
            return CheckResult(
                status=Status.FAIL,
                message="취약: Apache가 root 권한으로 실행되고 있습니다"
            )

    return CheckResult(
        status=Status.PASS,
        message="안전: Apache가 root 권한으로 실행되지 않습니다"
    )



def check_u54(command_outputs: List[str]) -> CheckResult:
    """U-54: Apache 상위 디렉터리 접근 금지

    점검 항목을 자동으로 검증합니다.

    Legacy _54SCRIPT 로직:
    - httpd.conf 파일에서 AllowOverride 검색
    - 빈 출력이면 PASS
    - "AllowOverride None"이 있으면 PASS, 아니면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf 파일에서 AllowOverride 검색 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없거나 AllowOverride 설정이 없습니다"
        )

    # "AllowOverride None" 체크
    for line in lines:
        if 'AllowOverride' in line and 'None' in line:
            return CheckResult(
                status=Status.PASS,
                message="안전: AllowOverride가 None으로 설정되어 있습니다"
            )

    return CheckResult(
        status=Status.FAIL,
        message="취약: AllowOverride가 None이 아닙니다"
    )



def check_u55(command_outputs: List[str]) -> CheckResult:
    """U-55: Apache 불필요한 파일 제거

    점검 항목을 자동으로 검증합니다.

    Legacy _55SCRIPT 로직:
    - 2개 명령어: htdocs/manual, manual 디렉터리 확인
    - 모두 빈 출력이면 PASS (불필요한 파일 없음)
    - 하나라도 있으면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: htdocs/manual 디렉터리 ls 결과
            - [1]: manual 디렉터리 ls 결과

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

    # 모든 명령어 결과 확인
    for output in command_outputs:
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if lines:
            return CheckResult(
                status=Status.FAIL,
                message="취약: Apache 불필요한 파일(manual 디렉터리)이 존재합니다"
            )

    return CheckResult(
        status=Status.PASS,
        message="안전: Apache 불필요한 파일이 제거되었습니다"
    )



def check_u56(command_outputs: List[str]) -> CheckResult:
    """U-56: Apache 링크 사용금지

    점검 항목을 자동으로 검증합니다.

    Legacy _56SCRIPT 로직:
    - httpd.conf에서 FollowSymLinks 검색
    - 빈 출력이면 PASS
    - "Options Indexes FollowSymLinks"가 있으면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf에서 FollowSymLinks 검색 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없거나 FollowSymLinks 설정이 없습니다"
        )

    # "Options ... FollowSymLinks" 체크
    for line in lines:
        if 'Options' in line and 'Indexes' in line and 'FollowSymLinks' in line:
            return CheckResult(
                status=Status.PASS,
                message="안전: FollowSymLinks가 적절히 설정되어 있습니다"
            )

    return CheckResult(
        status=Status.FAIL,
        message="취약: FollowSymLinks 설정이 올바르지 않습니다"
    )



def check_u57(command_outputs: List[str]) -> CheckResult:
    """U-57: Apache 파일 업로드 및 다운로드 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _57SCRIPT 로직:
    - httpd.conf에서 LimitRequestBody 검색
    - 빈 출력이면 PASS
    - LimitRequestBody 값이 5000000 미만이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf에서 LimitRequestBody 검색 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없거나 LimitRequestBody 설정이 없습니다"
        )

    # LimitRequestBody 값 파싱
    for line in lines:
        if 'LimitRequestBody' in line:
            parts = line.split()
            for part in parts:
                try:
                    limit = int(part)
                    if limit < 5000000:
                        return CheckResult(
                            status=Status.PASS,
                            message=f"안전: 파일 업로드 크기가 제한되어 있습니다 (LimitRequestBody {limit})"
                        )
                    else:
                        return CheckResult(
                            status=Status.FAIL,
                            message=f"취약: 파일 업로드 크기 제한이 너무 큽니다 (LimitRequestBody {limit}, 권장 5MB 미만)"
                        )
                except ValueError:
                    pass

    return CheckResult(
        status=Status.PASS,
        message="안전: LimitRequestBody 설정이 없습니다"
    )



def check_u58(command_outputs: List[str]) -> CheckResult:
    """U-58: Apache 웹 서비스 영역의 분리

    점검 항목을 자동으로 검증합니다.

    Legacy _58SCRIPT 로직:
    - DocumentRoot 확인
    - 출력이 없으면 PASS (Apache 없음)
    - 출력이 있으면 FAIL (수동 점검 필요)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: DocumentRoot 설정 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없습니다"
        )
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: Apache DocumentRoot가 기본 위치에 있습니다 (웹 서비스 영역 분리 필요)"
        )



def check_u59(command_outputs: List[str]) -> CheckResult:
    """U-59: ssh 원격접속 허용

    점검 항목을 자동으로 검증합니다.

    Legacy _59SCRIPT 로직:
    - /etc/xinetd.d/telnet, /etc/services에서 telnet/ftp 검색
    - telnet 또는 ftp가 있으면 FAIL
    - 없으면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/services에서 telnet/ftp 검색 결과

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

    output = command_outputs[0].strip()
    lines = output.split('\n')

    for line in lines:
        if line.strip():
            if 'telnet' in line or 'ftp' in line:
                return CheckResult(
                    status=Status.FAIL,
                    message="취약: telnet 또는 ftp 서비스가 활성화되어 있습니다 (SSH 사용 권장)"
                )

    return CheckResult(
        status=Status.PASS,
        message="안전: telnet 및 ftp 서비스가 비활성화되어 있습니다"
    )



def check_u60(command_outputs: List[str]) -> CheckResult:
    """U-60: ftp 서비스 확인

    점검 항목을 자동으로 검증합니다.

    Legacy _60SCRIPT 로직:
    - 2개 명령어: /etc/xinetd.d/ftp, ps -ef | grep ftp
    - 모두 빈 출력이면 PASS
    - 첫번째에 출력이 있으면 PASS (xinetd 설정 있음)
    - 두번째에 ftp가 있지만 grep이 아니면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/xinetd.d/ftp 파일 조회 결과
            - [1]: ps -ef | grep ftp 프로세스 조회 결과

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 부족합니다"
        )

    xinetd_output = command_outputs[0].strip()
    ps_output = command_outputs[1].strip()

    xinetd_lines = [line for line in xinetd_output.split('\n') if line.strip()]
    ps_lines = [line for line in ps_output.split('\n') if line.strip()]

    # 모두 빈 출력이면 PASS
    if not xinetd_lines and not ps_lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: FTP 서비스가 비활성화되어 있습니다"
        )

    # xinetd 설정이 있으면 PASS
    if xinetd_lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: FTP 서비스가 xinetd로 관리되고 있습니다"
        )

    # ps 출력 확인 (grep 라인 제외)
    if ps_lines:
        for line in ps_lines:
            if 'ftp' in line:
                if 'grep' in line:
                    pass  # grep 라인은 무시
                else:
                    return CheckResult(
                        status=Status.FAIL,
                        message="취약: FTP 서비스가 실행 중입니다"
                    )

    return CheckResult(
        status=Status.PASS,
        message="안전: FTP 서비스가 비활성화되어 있습니다"
    )



def check_u61(command_outputs: List[str]) -> CheckResult:
    """U-61: ftp 계정 shell 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _61SCRIPT 로직:
    - /etc/passwd에서 ftp 계정 확인
    - ftp 계정의 shell이 /sbin/nologin 또는 /sbin/false이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd에서 ftp 계정 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: ftp 계정이 존재하지 않습니다"
        )

    # ftp 계정의 shell 확인
    for line in lines:
        if 'ftp' in line:
            parts = line.split(':')
            if len(parts) >= 7:
                shell = parts[-1].strip()
                if shell == '/sbin/nologin' or shell == '/sbin/false':
                    pass  # 정상
                else:
                    return CheckResult(
                        status=Status.FAIL,
                        message=f"취약: ftp 계정의 shell이 {shell}입니다 (/sbin/nologin 또는 /sbin/false 권장)"
                    )

    return CheckResult(
        status=Status.PASS,
        message="안전: ftp 계정의 shell이 적절히 설정되어 있습니다"
    )



def check_u62(command_outputs: List[str]) -> CheckResult:
    """U-62: ftpusers 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _62SCRIPT 로직:
    - 2개 명령어: /etc/ftpusers, /etc/ftpd/ftpusers 파일 권한 확인
    - 모두 빈 출력이면 PASS (파일 없음)
    - 권한이 rw-r----- root이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/ftpusers ls -l 결과
            - [1]: /etc/ftpd/ftpusers ls -l 결과

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

    # 모든 출력 확인
    all_empty = True
    for output in command_outputs:
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if lines:
            all_empty = False
            # ls -l 출력 파싱
            parts = lines[0].split()
            if len(parts) >= 3:
                permissions = parts[0]
                owner = parts[2]
                # 권한 체크: rw-r----- root
                if len(permissions) >= 10:
                    if permissions[1:10] == 'rw-r-----' and owner == 'root':
                        pass  # 정상
                    else:
                        return CheckResult(
                            status=Status.FAIL,
                            message=f"취약: ftpusers 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다"
                        )

    if all_empty:
        return CheckResult(
            status=Status.PASS,
            message="안전: ftpusers 파일이 존재하지 않습니다"
        )

    return CheckResult(
        status=Status.PASS,
        message="안전: ftpusers 파일 권한이 적절히 설정되어 있습니다"
    )



def check_u63(command_outputs: List[str]) -> CheckResult:
    """U-63: ftpusers 파일 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _63SCRIPT 로직:
    - 3개 명령어: /etc/ftpusers, /etc/ftpd/ftpusers, proftpd.conf 확인
    - 모두 빈 출력이면 PASS
    - 출력이 있으면 MANUAL (수동 점검 필요)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/ftpusers 파일 내용
            - [1]: /etc/ftpd/ftpusers 파일 내용
            - [2]: proftpd.conf 파일 내용

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

    # 모든 출력 확인
    all_empty = True
    for output in command_outputs:
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if lines:
            all_empty = False
            break

    if all_empty:
        return CheckResult(
            status=Status.PASS,
            message="안전: FTP 설정 파일이 존재하지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="수동 점검: FTP root 계정 접속 차단 확인이 필요합니다"
        )



def check_u64(command_outputs: List[str]) -> CheckResult:
    """U-64: at 파일 소유자 및 권한 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _64SCRIPT 로직:
    - 2개 명령어: /etc/at.allow, /etc/at.deny 파일 권한 확인
    - 모두 빈 출력이면 PASS
    - 권한이 rw-r----- root이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/at.allow ls -l 결과
            - [1]: /etc/at.deny ls -l 결과

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

    # 모든 출력 확인
    all_empty = True
    for output in command_outputs:
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if lines:
            all_empty = False
            # ls -l 출력 파싱
            parts = lines[0].split()
            if len(parts) >= 3:
                permissions = parts[0]
                owner = parts[2]
                # 권한 체크: rw-r----- root
                if len(permissions) >= 10:
                    if permissions[1:10] == 'rw-r-----' and owner == 'root':
                        pass  # 정상
                    else:
                        return CheckResult(
                            status=Status.FAIL,
                            message=f"취약: at 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다"
                        )

    if all_empty:
        return CheckResult(
            status=Status.PASS,
            message="안전: at 파일이 존재하지 않습니다"
        )

    return CheckResult(
        status=Status.PASS,
        message="안전: at 파일 권한이 적절히 설정되어 있습니다"
    )



def check_u65(command_outputs: List[str]) -> CheckResult:
    """U-65: SNMP 서비스 구동 점검

    점검 항목을 자동으로 검증합니다.

    Legacy _65SCRIPT 로직:
    - ps -ef | grep snmp 출력 확인
    - grep이 포함된 라인 제외
    - snmp가 있으면 FAIL
    - 없으면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: snmp 프로세스 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    # grep이 포함된 라인 제외
    for line in lines:
        if 'snmp' in line and 'grep' not in line:
            return CheckResult(
                status=Status.FAIL,
                message="취약: SNMP 서비스가 실행 중입니다"
            )

    return CheckResult(
        status=Status.PASS,
        message="안전: SNMP 서비스가 비활성화되어 있습니다"
    )



def check_u66(command_outputs: List[str]) -> CheckResult:
    """U-66: SNMP 서비스 Community String의 복잡성

    점검 항목을 자동으로 검증합니다.

    Legacy _66SCRIPT 로직:
    - /etc/snmp/snmpd.conf 파일 확인
    - 빈 출력이면 PASS (SNMP 설정 없음)
    - "public" 또는 "private"가 있으면 FAIL
    - 그 외는 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: snmpd.conf 파일 내용

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: SNMP 설정 파일이 없습니다"
        )

    # "public" 또는 "private" 체크
    for line in lines:
        if 'public' in line or 'private' in line:
            return CheckResult(
                status=Status.FAIL,
                message="취약: SNMP Community String이 기본값(public/private)입니다"
            )

    return CheckResult(
        status=Status.PASS,
        message="안전: SNMP Community String이 복잡하게 설정되어 있습니다"
    )



def check_u67(command_outputs: List[str]) -> CheckResult:
    """U-67: 로그온 시 경고 메세지 제공

    점검 항목을 자동으로 검증합니다.

    Legacy _67SCRIPT 로직:
    - /etc/motd 파일 확인
    - 빈 출력이면 FAIL (경고 메시지 없음)
    - 출력이 있으면 PASS (경고 메시지 존재)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/motd 파일 내용

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.FAIL,
            message="취약: 로그온 시 경고 메시지가 설정되어 있지 않습니다"
        )
    else:
        return CheckResult(
            status=Status.PASS,
            message="안전: 로그온 시 경고 메시지가 설정되어 있습니다"
        )



def check_u68(command_outputs: List[str]) -> CheckResult:
    """U-68: NFS 설정파일 접근 권한

    점검 항목을 자동으로 검증합니다.

    Legacy _68SCRIPT 로직:
    - /etc/exports 파일 권한 확인
    - 빈 출력이면 PASS (파일 없음)
    - 권한이 rw-r--r-- root이면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/exports ls -l 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: NFS 설정 파일이 존재하지 않습니다"
        )

    # ls -l 출력 파싱
    parts = lines[0].split()
    if len(parts) >= 3:
        permissions = parts[0]
        owner = parts[2]
        # 권한 체크: rw-r--r-- root
        if len(permissions) >= 10:
            if permissions[1:10] == 'rw-r--r--' and owner == 'root':
                return CheckResult(
                    status=Status.PASS,
                    message=f"안전: NFS 설정 파일 권한이 {permissions}이고 소유자가 root입니다"
                )
            else:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"취약: NFS 설정 파일 권한({permissions}) 또는 소유자({owner})가 올바르지 않습니다"
                )

    return CheckResult(
        status=Status.MANUAL,
        message="ls 출력 형식이 올바르지 않습니다"
    )



def check_u69(command_outputs: List[str]) -> CheckResult:
    """U-69: expn, vrfy 명령어 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _69SCRIPT 로직:
    - sendmail.cf에서 expn, vrfy 설정 확인
    - 빈 출력이면 PASS (sendmail 없음)
    - 출력이 있으면 MANUAL (수동 점검 필요)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: sendmail.cf에서 expn/vrfy 설정 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Sendmail 설정 파일이 없습니다"
        )
    else:
        return CheckResult(
            status=Status.MANUAL,
            message="수동 점검: Sendmail expn/vrfy 명령어 제한 설정을 확인하세요"
        )



def check_u70(command_outputs: List[str]) -> CheckResult:
    """U-70: Apache 웹서비스 정보 숨김

    점검 항목을 자동으로 검증합니다.

    Legacy _70SCRIPT 로직:
    - httpd.conf에서 ServerTokens 설정 확인
    - 빈 출력이면 PASS (Apache 없음)
    - "ServerTokens Prod"가 있으면 PASS
    - 그 외는 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: httpd.conf에서 ServerTokens 설정 조회 결과

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

    output = command_outputs[0].strip()
    lines = [line for line in output.split('\n') if line.strip()]

    if not lines:
        return CheckResult(
            status=Status.PASS,
            message="안전: Apache 설정 파일이 없습니다"
        )

    # "ServerTokens Prod" 체크
    for line in lines:
        if 'ServerTokens' in line and 'Prod' in line:
            return CheckResult(
                status=Status.PASS,
                message="안전: Apache 서버 정보가 숨겨져 있습니다 (ServerTokens Prod)"
            )

    return CheckResult(
        status=Status.FAIL,
        message="취약: Apache 서버 정보가 노출됩니다 (ServerTokens Prod 설정 권장)"
    )


