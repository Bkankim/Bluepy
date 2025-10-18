"""
Linux 보안 점검 Validator 함수 모음 - 계정관리

이 모듈은 KISA 기준 Linux 보안 점검 항목 중 계정관리 관련
validator 함수들을 포함합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)
"""

from typing import List
from src.core.domain.models import CheckResult, Status


def check_u01(command_outputs: List[str]) -> CheckResult:
    """U-01: root 계정 원격 접속 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _1SCRIPT 로직:
    - /etc/pam.d/login에서 pam_securetty.so 설정 확인
    - /etc/securetty에서 pts 존재 여부 확인
    - pts가 없으면 PASS (원격 로그인 제한됨)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/pam.d/login 내용
            - [1]: /etc/securetty 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 부족합니다 (2개 필요: pam.d/login, securetty)",
        )

    pam_login = command_outputs[0]
    securetty = command_outputs[1]

    # pam_securetty.so 설정 확인
    pam_securetty_found = False
    for line in pam_login.split("\n"):
        # NOSPACE: 빈 문자열 제거
        words = [w for w in line.split(" ") if w]
        if words == ["auth", "required", "/lib/security/pam_securetty.so"]:
            pam_securetty_found = True
            break

    if not pam_securetty_found:
        return CheckResult(status=Status.FAIL, message="취약: pam_securetty.so 설정이 없습니다")

    # pts 확인 (pts가 있으면 원격 로그인 가능 = 취약)
    for line in securetty.split("\n"):
        if line.strip().startswith("pts"):
            return CheckResult(
                status=Status.FAIL,
                message="취약: /etc/securetty에 pts가 존재합니다 (원격 로그인 가능)",
            )

    return CheckResult(
        status=Status.PASS, message="안전: pam_securetty.so 설정되어 있고 pts가 없습니다"
    )


def check_u02(command_outputs: List[str]) -> CheckResult:
    """U-02: 패스워드 복잡성 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _2SCRIPT 로직:
    - LINUX의 SHADOW 파일은 해시화되어 저장되기 때문에 비교 불가능
    - 항상 PASS 반환

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트 (사용 안 함)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전)
            - message: 결과 설명 메시지
    """
    return CheckResult(
        status=Status.PASS, message="안전: LINUX shadow 파일은 해시화되어 저장됩니다"
    )


def check_u03(command_outputs: List[str]) -> CheckResult:
    """U-03: 계정잠금 임계값 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _3SCRIPT 로직:
    - pam_tally.so 2개 설정 확인
    - auth required /lib/security/pam_tally.so deny=5 unlock_time=120 no_magic_root
    - account required /lib/security/pam_tally.so no_magic_root reset

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: PAM 설정 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    pam_config = command_outputs[0]

    r1 = [
        "auth",
        "required",
        "/lib/security/pam_tally.so",
        "deny=5",
        "unlock_time=120",
        "no_magic_root",
    ]
    r2 = ["account", "required", "/lib/security/pam_tally.so", "no_magic_root", "reset"]

    found = [False, False]
    for line in pam_config.split("\n"):
        words = [w for w in line.split(" ") if w]
        if words == r1:
            found[0] = True
        if words == r2:
            found[1] = True

    if found == [True, True]:
        return CheckResult(
            status=Status.PASS, message="안전: 계정잠금 임계값이 올바르게 설정되어 있습니다"
        )
    else:
        missing = []
        if not found[0]:
            missing.append("auth pam_tally.so")
        if not found[1]:
            missing.append("account pam_tally.so")
        return CheckResult(
            status=Status.FAIL,
            message=f"취약: 계정잠금 설정이 누락되었습니다 ({', '.join(missing)})",
        )


def check_u04(command_outputs: List[str]) -> CheckResult:
    """U-04: 패스워드 파일 보호

    점검 항목을 자동으로 검증합니다.

    Legacy _4SCRIPT 로직:
    - /etc/passwd의 두 번째 필드가 'x'인지 확인 (shadow 파일 사용)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용 (한 줄)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    passwd_line = command_outputs[0].strip()
    fields = passwd_line.split(":")

    if len(fields) < 2:
        return CheckResult(status=Status.MANUAL, message="passwd 파일 형식이 올바르지 않습니다")

    if fields[1] == "x":
        return CheckResult(status=Status.PASS, message="안전: shadow 패스워드를 사용하고 있습니다")
    else:
        return CheckResult(
            status=Status.FAIL,
            message="취약: shadow 패스워드를 사용하지 않습니다 (패스워드가 /etc/passwd에 노출됨)",
        )


def check_u05(command_outputs: List[str]) -> CheckResult:
    """U-05: root 이외의 UID가 '0' 금지

    점검 항목을 자동으로 검증합니다.

    Legacy _5SCRIPT 로직:
    - /etc/passwd의 첫 3개 계정 UID가 0, 1, 2인지 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용 (여러 줄)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    passwd_content = command_outputs[0]
    lines = [line for line in passwd_content.split("\n") if line.strip()]

    if len(lines) < 3:
        return CheckResult(status=Status.MANUAL, message="/etc/passwd에 계정이 3개 미만입니다")

    try:
        uid0 = int(lines[0].split(":")[2])
        uid1 = int(lines[1].split(":")[2])
        uid2 = int(lines[2].split(":")[2])

        if uid0 == 0 and uid1 == 1 and uid2 == 2:
            return CheckResult(
                status=Status.PASS, message="안전: UID가 올바르게 설정되어 있습니다 (0, 1, 2)"
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: UID가 올바르지 않습니다 (실제: {uid0}, {uid1}, {uid2})",
            )
    except (IndexError, ValueError) as e:
        return CheckResult(status=Status.MANUAL, message=f"passwd 파일 파싱 오류: {str(e)}")


def check_u06(command_outputs: List[str]) -> CheckResult:
    """U-06: root 계정 su 제한

    점검 항목을 자동으로 검증합니다.

    Legacy _6SCRIPT 로직:
    - data[0]에서 wheel 그룹 정보 추출
    - data[1]에서 pam_wheel.so 설정 확인
    - 2가지 패턴 중 하나라도 매칭되면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: wheel 그룹 정보 (예: /etc/group 내용)
            - [1]: PAM 설정 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs or len(command_outputs) < 2:
        return CheckResult(
            status=Status.MANUAL,
            message="명령어 출력이 부족합니다 (2개 필요: wheel 그룹, PAM 설정)",
        )

    try:
        wheel_info = command_outputs[0]
        pam_config = command_outputs[1]

        # wheel 그룹 정보 추출 (split(':')[3])
        wheel_group = wheel_info.split(":")[3] if ":" in wheel_info else ""

        # pam_wheel.so 설정 2가지 패턴
        pattern1 = ["auth", "required", "/lib/security/pam_wheel_so", "debug", "group=wheel"]
        pattern2 = ["auth", "required", "/lib/security/$ISA/pam_wheel_so", "use_uid"]

        for line in pam_config.split("\n"):
            words = [w for w in line.split(" ") if w]
            if words == pattern1 or words == pattern2:
                return CheckResult(
                    status=Status.PASS,
                    message=f"안전: pam_wheel.so가 설정되어 있습니다 (wheel 그룹: {wheel_group})",
                )

        return CheckResult(status=Status.FAIL, message="취약: pam_wheel.so 설정이 없습니다")

    except Exception as e:
        return CheckResult(status=Status.FAIL, message=f"취약: 설정 파일 파싱 오류 ({str(e)})")


def check_u07(command_outputs: List[str]) -> CheckResult:
    """U-07: 패스워드 최소 길이 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _7SCRIPT 로직:
    - data[1].split('\t')[1] > 8 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 패스워드 정책 파일 내용 (탭 구분)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    policy_content = command_outputs[0]
    lines = [line for line in policy_content.split("\n") if line.strip()]

    if len(lines) < 2:
        return CheckResult(
            status=Status.MANUAL, message="패스워드 정책 파일 형식이 올바르지 않습니다"
        )

    try:
        min_len = int(lines[1].split("\t")[1])
        if min_len > 8:
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 패스워드 최소 길이가 {min_len}자로 설정되어 있습니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 패스워드 최소 길이가 {min_len}자입니다 (8자 초과 권장)",
            )
    except (IndexError, ValueError) as e:
        return CheckResult(status=Status.MANUAL, message=f"정책 파일 파싱 오류: {str(e)}")


def check_u08(command_outputs: List[str]) -> CheckResult:
    """U-08: 패스워드 최대 사용기간 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _8SCRIPT 로직:
    - data[1].split('\t')[1] > 90 and != '99999' 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 패스워드 정책 파일 내용 (탭 구분)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    policy_content = command_outputs[0]
    lines = [line for line in policy_content.split("\n") if line.strip()]

    if len(lines) < 2:
        return CheckResult(
            status=Status.MANUAL, message="패스워드 정책 파일 형식이 올바르지 않습니다"
        )

    try:
        max_days_str = lines[1].split("\t")[1]
        max_days = int(max_days_str)

        if max_days > 90 and max_days_str != "99999":
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 패스워드 최대 사용기간이 {max_days}일로 설정되어 있습니다",
            )
        else:
            if max_days_str == "99999":
                return CheckResult(
                    status=Status.FAIL, message="취약: 패스워드 최대 사용기간이 무제한(99999)입니다"
                )
            else:
                return CheckResult(
                    status=Status.FAIL,
                    message=f"취약: 패스워드 최대 사용기간이 {max_days}일입니다 (90일 초과 권장)",
                )
    except (IndexError, ValueError) as e:
        return CheckResult(status=Status.MANUAL, message=f"정책 파일 파싱 오류: {str(e)}")


def check_u09(command_outputs: List[str]) -> CheckResult:
    """U-09: 패스워드 최소 사용기간 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _9SCRIPT 로직:
    - data[1].split('\t')[1] >= 1 확인

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 패스워드 정책 파일 내용 (탭 구분)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    policy_content = command_outputs[0]
    lines = [line for line in policy_content.split("\n") if line.strip()]

    if len(lines) < 2:
        return CheckResult(
            status=Status.MANUAL, message="패스워드 정책 파일 형식이 올바르지 않습니다"
        )

    try:
        min_days = int(lines[1].split("\t")[1])
        if min_days >= 1:
            return CheckResult(
                status=Status.PASS,
                message=f"안전: 패스워드 최소 사용기간이 {min_days}일로 설정되어 있습니다",
            )
        else:
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: 패스워드 최소 사용기간이 {min_days}일입니다 (1일 이상 권장)",
            )
    except (IndexError, ValueError) as e:
        return CheckResult(status=Status.MANUAL, message=f"정책 파일 파싱 오류: {str(e)}")


def check_u10(command_outputs: List[str]) -> CheckResult:
    """U-10: 불필요한 계정 제거

    점검 항목을 자동으로 검증합니다.

    Legacy _10SCRIPT 로직:
    - 계정 목록 추출 후 수동 점검 (MANUAL)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    passwd_content = command_outputs[0]
    lines = [line for line in passwd_content.split("\n") if line.strip()]

    account_names = []
    for line in lines:
        fields = line.split(":")
        if fields:
            account_names.append(fields[0])

    accounts_str = ", ".join(account_names[:10])  # 처음 10개만 표시
    if len(account_names) > 10:
        accounts_str += f", ... (총 {len(account_names)}개)"

    return CheckResult(
        status=Status.MANUAL,
        message=f"수동 점검 필요: 다음 계정들이 모두 필요한지 확인하세요 - {accounts_str}",
    )


def check_u11(command_outputs: List[str]) -> CheckResult:
    """U-11: 관리자 그룹에 최소한의 계정 포함

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _11SCRIPT 로직:
    - 그룹 파일에서 계정 목록 추출
    - 수동 점검 (MANUAL)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 그룹 파일 내용 (예: /etc/group)

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="수동 점검: 명령어 출력이 없습니다")

    try:
        group_content = command_outputs[0]
        lines = [line for line in group_content.split("\n") if line.strip()]

        if not lines:
            return CheckResult(status=Status.MANUAL, message="수동 점검: 그룹 정보가 비어있습니다")

        # 첫 줄에서 그룹 멤버 추출 (split(':')[3])
        first_line = lines[0]
        fields = first_line.split(":")
        if len(fields) >= 4:
            members = fields[3]
            return CheckResult(
                status=Status.MANUAL,
                message=f"수동 점검: 관리자 그룹 계정 확인 필요 - {members if members else '(없음)'}",
            )
        else:
            return CheckResult(
                status=Status.MANUAL, message="수동 점검: 그룹 파일 형식이 올바르지 않습니다"
            )

    except Exception as e:
        return CheckResult(status=Status.FAIL, message=f"취약: 그룹 파일 파싱 오류 ({str(e)})")


def check_u12(command_outputs: List[str]) -> CheckResult:
    """U-12: 계정이 존재하지 않는 GID 금지

    점검 항목을 수동으로 검증해야 합니다.

    Legacy _12SCRIPT 로직:
    - passwd 파일에서 계정명과 GID 추출
    - 수동 점검 (MANUAL)

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="수동 점검: 명령어 출력이 없습니다")

    try:
        passwd_content = command_outputs[0]
        lines = [line for line in passwd_content.split("\n") if line.strip()]

        account_info = []
        for line in lines[:5]:  # 처음 5개만 표시
            fields = line.split(":")
            if len(fields) >= 4:
                account_info.append(f"{fields[0]}(GID:{fields[3]})")

        info_str = ", ".join(account_info)
        if len(lines) > 5:
            info_str += f", ... (총 {len(lines)}개)"

        return CheckResult(
            status=Status.MANUAL, message=f"수동 점검: 계정별 GID 확인 필요 - {info_str}"
        )

    except Exception as e:
        return CheckResult(
            status=Status.MANUAL, message=f"수동 점검: passwd 파일 파싱 오류 ({str(e)})"
        )


def check_u13(command_outputs: List[str]) -> CheckResult:
    """U-13: 동일한 UID 금지

    점검 항목을 자동으로 검증합니다.

    Legacy _13SCRIPT 로직:
    - 각 줄에서 UID 추출
    - UID 중복 여부 확인
    - 중복 있으면 FAIL, 없으면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    try:
        passwd_content = command_outputs[0]
        lines = [line for line in passwd_content.split("\n") if line.strip()]

        uid_list = []
        for line in lines:
            fields = line.split(":")
            if len(fields) >= 3:
                uid = fields[2]
                if uid in uid_list:
                    return CheckResult(
                        status=Status.FAIL, message=f"취약: UID {uid}가 중복되었습니다"
                    )
                uid_list.append(uid)

        return CheckResult(status=Status.PASS, message="안전: 중복된 UID가 없습니다")

    except Exception as e:
        return CheckResult(status=Status.MANUAL, message=f"passwd 파일 파싱 오류: {str(e)}")


def check_u14(command_outputs: List[str]) -> CheckResult:
    """U-14: 사용자 shell 점검

    점검 항목을 자동으로 검증합니다.

    Legacy _14SCRIPT 로직:
    - 각 줄에서 shell 확인
    - shell이 /sbin/nologin이 아니면 FAIL
    - 모두 /sbin/nologin이면 PASS

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: /etc/passwd 파일 내용 (시스템 계정들)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    try:
        passwd_content = command_outputs[0]
        lines = [line for line in passwd_content.split("\n") if line.strip()]

        for line in lines:
            fields = line.split(":")
            if len(fields) >= 7:
                shell = fields[6]
                if shell != "/sbin/nologin":
                    account = fields[0] if fields else "(알 수 없음)"
                    return CheckResult(
                        status=Status.FAIL,
                        message=f"취약: {account} 계정의 shell이 {shell}입니다 (/sbin/nologin 권장)",
                    )

        return CheckResult(
            status=Status.PASS, message="안전: 모든 시스템 계정의 shell이 /sbin/nologin입니다"
        )

    except Exception as e:
        return CheckResult(status=Status.MANUAL, message=f"passwd 파일 파싱 오류: {str(e)}")


def check_u15(command_outputs: List[str]) -> CheckResult:
    """U-15: Session Timeout 설정

    점검 항목을 자동으로 검증합니다.

    Legacy _15SCRIPT 로직:
    - TIMEOUT이 있고 값 >= 600인지 확인
    - TMOUT이 있는지 확인
    - 둘 다 만족하면 PASS, 아니면 FAIL

    Args:
        command_outputs: 점검 명령어 실행 결과 리스트
            - [0]: 환경 설정 파일 내용 (예: /etc/profile)

    Returns:
        CheckResult: 점검 결과
            - status: PASS (안전) / FAIL (취약) / MANUAL (수동 점검 필요)
            - message: 결과 설명 메시지
    """
    if not command_outputs:
        return CheckResult(status=Status.MANUAL, message="명령어 출력이 없습니다")

    try:
        config_content = command_outputs[0]
        lines = [line for line in config_content.split("\n") if line.strip()]

        has_timeout = False
        has_tmout = False

        for line in lines:
            if "TIMEOUT" in line:
                try:
                    # TIMEOUT=값 형식에서 값 추출
                    if "=" in line:
                        value = int(line.split("=")[1].strip())
                        if value >= 600:
                            has_timeout = True
                except (ValueError, IndexError):
                    pass

            if "TMOUT" in line:
                has_tmout = True

        if has_timeout and has_tmout:
            return CheckResult(
                status=Status.PASS,
                message="안전: Session Timeout이 올바르게 설정되어 있습니다 (TIMEOUT >= 600, TMOUT 존재)",
            )
        else:
            missing = []
            if not has_timeout:
                missing.append("TIMEOUT >= 600")
            if not has_tmout:
                missing.append("TMOUT")
            return CheckResult(
                status=Status.FAIL,
                message=f"취약: Session Timeout 설정 누락 ({', '.join(missing)})",
            )

    except Exception as e:
        return CheckResult(status=Status.MANUAL, message=f"설정 파일 파싱 오류: {str(e)}")
