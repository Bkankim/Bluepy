#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 2 → 3 마이그레이션 스크립트

Legacy Python 2 코드를 Python 3.12로 변환하고,
YAML 규칙 파일과 Validator 함수 스켈레톤을 자동 생성합니다.

사용법:
    python scripts/migrate_legacy.py --input <legacy_file> --output-dir <output> --functions <U-01,U-04,...>

예시:
    # 10개 함수 마이그레이션
    python scripts/migrate_legacy.py \\
        --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
        --output-dir output/ \\
        --functions U-01,U-04,U-07,U-08,U-09,U-05,U-18,U-27,U-03,U-10

    # 전체 73개 함수
    python scripts/migrate_legacy.py \\
        --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
        --output-dir output/ \\
        --all

    # Dry-run (시뮬레이션)
    python scripts/migrate_legacy.py \\
        --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
        --output-dir output/ \\
        --functions U-01 \\
        --dry-run
"""

import argparse
import ast
import logging
import re
import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

# 프로젝트 루트를 sys.path에 추가 (src 모듈 import를 위해)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.domain.models import Severity

# 상수
DEFAULT_LOG_FILE = 'migration.log'
KISA_PATTERN = r'^U-\d{2}$'

# KISA 코드별 규칙 이름 매핑 (73개)
KISA_NAMES = {
    "U-01": "root 계정 원격 접속 제한",
    "U-02": "패스워드 복잡성 설정",
    "U-03": "계정잠금 임계값 설정",
    "U-04": "패스워드 파일 보호",
    "U-05": "root 이외의 UID가 '0' 금지",
    "U-06": "root 계정 su 제한",
    "U-07": "패스워드 최소 길이 설정",
    "U-08": "패스워드 최대 사용기간 설정",
    "U-09": "패스워드 최소 사용기간 설정",
    "U-10": "불필요한 계정 제거",
    "U-11": "관리자 그룹에 최소한의 계정 포함",
    "U-12": "계정이 존재하지 않는 GID 금지",
    "U-13": "동일한 UID 금지",
    "U-14": "사용자 shell 점검",
    "U-15": "Session Timeout 설정",
    "U-16": "root 홈, 패스 디렉터리 권한 및 패스 설정",
    "U-17": "파일 및 디렉터리 소유자 설정",
    "U-18": "/etc/passwd 파일 소유자 및 권한 설정",
    "U-19": "/etc/shadow 파일 소유자 및 권한 설정",
    "U-20": "/etc/hosts 파일 소유자 및 권한 설정",
    "U-21": "/etc/(x)inetd.conf 파일 소유자 및 권한 설정",
    "U-22": "/etc/syslog.conf 파일 소유자 및 권한 설정",
    "U-23": "/etc/services 파일 소유자 및 권한 설정",
    "U-24": "SUID, SGID, Sticky bit 설정파일 점검",
    "U-25": "사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정",
    "U-26": "world writable 파일 점검",
    "U-27": "/dev에 존재하지 않는 device 파일 점검",
    "U-28": "$HOME/.rhosts, hosts.equiv 사용 금지",
    "U-29": "접속 IP 및 포트 제한",
    "U-30": "hosts.lpd 파일 소유자 및 권한 설정",
    "U-31": "NIS 서비스 비활성화",
    "U-32": "UMASK 설정 관리",
    "U-33": "홈 디렉토리 소유자 및 권한 설정",
    "U-34": "홈 디렉토리로 지정한 디렉터리의 존재 관리",
    "U-35": "숨겨진 파일 및 디렉터리 검색 및 제거",
    "U-36": "Finger 서비스 비활성화",
    "U-37": "Anonymous FTP 비활성화",
    "U-38": "r계열 서비스 비활성화",
    "U-39": "cron 파일 소유자 및 권한 설정",
    "U-40": "DOS 공격에 취약한 서비스 비활성화",
    "U-41": "NFS 서비스 비활성화",
    "U-42": "NFS 접근 통제",
    "U-43": "automountd 제거",
    "U-44": "RPC 서비스 확인",
    "U-45": "NIS, NIS+ 점검",
    "U-46": "tftp, talk 서비스 비활성화",
    "U-47": "Sendmail 버전 점검",
    "U-48": "스팸 메일 릴레이 제한",
    "U-49": "스팸 메일 릴레이 제한",
    "U-50": "DNS 보안 버전 패치",
    "U-51": "DNS Zone Transfer 설정",
    "U-52": "Apache 디렉터리 리스팅 제거",
    "U-53": "Apache 웹 프로세스 권한 제한",
    "U-54": "Apache 상위 디렉터리 접근 금지",
    "U-55": "Apache 불필요한 파일 제거",
    "U-56": "Apache 링크 사용금지",
    "U-57": "Apache 파일 업로드 및 다운로드 제한",
    "U-58": "Apache 웹 서비스 영역의 분리",
    "U-59": "ssh 원격접속 허용",
    "U-60": "ftp 서비스 확인",
    "U-61": "ftp 계정 shell 제한",
    "U-62": "ftpusers 파일 소유자 및 권한 설정",
    "U-63": "ftpusers 파일 설정",
    "U-64": "at 파일 소유자 및 권한 설정",
    "U-65": "SNMP 서비스 구동 점검",
    "U-66": "SNMP 서비스 Community String의 복잡성",
    "U-67": "로그온 시 경고 메세지 제공",
    "U-68": "NFS 설정파일 접근 권한",
    "U-69": "expn, vrfy 명령어 제한",
    "U-70": "Apache 웹서비스 정보 숨김",
    "U-71": "최신 보안패치 및 벤더 권고사항 적용",
    "U-72": "로그의 정기적 검토 및 보고",
    "U-73": "로그 기록 정책 수립",
}


@dataclass
class FunctionInfo:
    """Legacy 함수 정보

    AST에서 추출한 Legacy 함수의 메타데이터를 저장합니다.

    Attributes:
        name: 함수명 (_1SCRIPT, _4SCRIPT 등)
        number: 함수 번호 (1, 4, ...)
        kisa_code: KISA 표준 코드 (U-01, U-04, ...)
        source: 함수 소스 코드 (Python 3 변환 후)
        complexity: 복잡도 (AST 노드 수)
        severity: 심각도 (HIGH/MID/LOW)
        commands: bash 명령어 리스트 (Linux_Check_1.txt에서 추출)
        ast_node: AST FunctionDef 노드 (Optional, 추가 분석용)
    """
    name: str
    number: int
    kisa_code: str
    source: str
    complexity: int
    severity: Severity
    commands: List[str] = field(default_factory=list)
    ast_node: Optional[ast.FunctionDef] = None


def parse_arguments() -> argparse.Namespace:
    """CLI 인자 파싱"""
    parser = argparse.ArgumentParser(
        prog='migrate_legacy',
        description='Python 2 → 3 마이그레이션 및 YAML/Validator 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예시:
  # 10개 함수 마이그레이션
  python scripts/migrate_legacy.py \\
      --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
      --output-dir output/ \\
      --functions U-01,U-04,U-07,U-08,U-09,U-05,U-18,U-27,U-03,U-10

  # 전체 73개 함수
  python scripts/migrate_legacy.py \\
      --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
      --output-dir output/ \\
      --all

  # Dry-run (시뮬레이션)
  python scripts/migrate_legacy.py \\
      --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py \\
      --output-dir output/ \\
      --functions U-01 \\
      --dry-run
        '''
    )

    # 필수 인자
    parser.add_argument(
        '--input',
        required=True,
        help='Legacy Python 2 파일 경로'
    )

    parser.add_argument(
        '--output-dir',
        required=True,
        help='출력 디렉토리 (yaml/, validators/, MIGRATION_REPORT.md)'
    )

    # 함수 선택 (상호 배타적)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--functions',
        help='마이그레이션할 함수 (KISA 코드, 쉼표 구분): U-01,U-04,U-18'
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='모든 함수 마이그레이션 (73개)'
    )

    # 선택 인자
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 로그 출력'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='시뮬레이션 (파일 생성 안 함)'
    )

    parser.add_argument(
        '--log-file',
        default=DEFAULT_LOG_FILE,
        help=f'로그 파일 경로 (기본: {DEFAULT_LOG_FILE})'
    )

    return parser.parse_args()


def setup_logging(verbose: bool, log_file: str) -> logging.Logger:
    """로깅 시스템 초기화

    Args:
        verbose: 상세 로그 출력 여부
        log_file: 로그 파일 경로

    Returns:
        설정된 Logger 인스턴스
    """
    # 루트 로거
    logger = logging.getLogger('migrate_legacy')
    logger.setLevel(logging.DEBUG)

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 간단한 포맷 (콘솔용)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)

    # 파일 핸들러 (상세 정보)
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        file_handler.setLevel(logging.DEBUG)

        # 상세 포맷 (파일용)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        logger.addHandler(file_handler)
    except PermissionError:
        # 로그 파일 쓰기 실패 시 경고만 (콘솔은 계속)
        print(f"경고: 로그 파일 쓰기 권한 없음: {log_file}", file=sys.stderr)

    # 핸들러 추가
    logger.addHandler(console_handler)

    return logger


def validate_inputs(args: argparse.Namespace, logger: logging.Logger) -> None:
    """입력 인자 검증

    Args:
        args: CLI 인자
        logger: Logger 인스턴스

    Raises:
        FileNotFoundError: Legacy 파일 없음
        ValueError: 잘못된 인자 형식
        PermissionError: 디렉토리 생성 권한 없음
    """
    # 1. Legacy 파일 존재 확인
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Legacy 파일을 찾을 수 없습니다: {args.input}")

    if not input_path.is_file():
        raise ValueError(f"파일이 아닙니다: {args.input}")

    logger.debug(f"입력 파일 확인: {input_path.absolute()}")

    # 2. 출력 디렉토리 생성 가능 확인
    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # 하위 디렉토리 생성
        (output_dir / 'yaml').mkdir(exist_ok=True)
        (output_dir / 'validators').mkdir(exist_ok=True)

        logger.debug(f"출력 디렉토리 생성: {output_dir.absolute()}")
    except PermissionError as e:
        raise PermissionError(
            f"출력 디렉토리 생성 권한 없음: {args.output_dir}"
        ) from e

    # 3. --functions 형식 검증
    if args.functions:
        kisa_pattern = re.compile(KISA_PATTERN)
        functions = [f.strip() for f in args.functions.split(',')]

        invalid = [f for f in functions if not kisa_pattern.match(f)]
        if invalid:
            raise ValueError(
                f"잘못된 KISA 코드 형식: {invalid}\n"
                "형식: U-01, U-04, ... (U-로 시작, 2자리 숫자)"
            )

        logger.debug(f"선택된 함수: {functions}")


def read_legacy_file(filepath: str, logger: logging.Logger) -> str:
    """Legacy Python 2 파일 읽기 (다중 인코딩 시도)

    다양한 인코딩을 순서대로 시도하여 Legacy 파일을 읽습니다.
    2017년 Python 2 코드는 BOM-UTF8, cp949, euc-kr 등 다양한 인코딩을 사용할 수 있습니다.

    Args:
        filepath: Legacy 파일 경로
        logger: Logger 인스턴스

    Returns:
        읽은 파일 내용 (UTF-8 문자열)

    Raises:
        ValueError: 모든 인코딩 시도 실패
    """
    # 시도할 인코딩 목록 (우선순위 순)
    encodings = [
        'utf-8-sig',  # UTF-8 with BOM (EF BB BF)
        'utf-8',      # UTF-8 without BOM
        'cp949',      # Windows 한글
        'euc-kr',     # Unix/Linux 한글
        'latin-1'     # 최후의 수단 (항상 성공하지만 깨질 수 있음)
    ]

    last_error = None

    for encoding in encodings:
        try:
            logger.debug(f"인코딩 시도: {encoding}")
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            # 성공
            logger.info(f"파일 읽기 성공: {encoding}")
            logger.info(
                f"파일 크기: {len(content):,} 문자 "
                f"({len(content.encode('utf-8')):,} UTF-8 bytes)"
            )

            # 한글 포함 확인
            korean_pattern = re.compile('[가-힣]+')
            if korean_pattern.search(content):
                logger.debug("한글 포함 확인")

            # latin-1로 읽은 경우 경고
            if encoding == 'latin-1':
                logger.warning(
                    "latin-1 인코딩으로 읽었습니다. "
                    "한글이 깨졌을 수 있으니 결과를 확인하세요."
                )

            return content

        except (UnicodeDecodeError, LookupError) as e:
            logger.debug(f"인코딩 실패 ({encoding}): {type(e).__name__}")
            last_error = e
            continue

    # 모든 인코딩 실패
    raise ValueError(
        f"파일을 읽을 수 없습니다: {filepath}\n"
        f"마지막 오류: {last_error}"
    )


def convert_to_python3(python2_code: str, logger: logging.Logger) -> str:
    """Python 2 → 3 구문 변환 (정규식 기반)

    정규식을 사용하여 Python 2 코드를 Python 3로 변환합니다.
    주요 변환: print 문, except 구문, unicode() 등

    Note: Python 3.12에서 lib2to3가 제거되어 정규식 기반으로 구현했습니다.

    Args:
        python2_code: Python 2 소스 코드
        logger: Logger 인스턴스

    Returns:
        Python 3 소스 코드

    Raises:
        SyntaxError: Python 3 구문 검증 실패
    """
    import ast

    logger.info("Python 2 → 3 변환 시작 (정규식 기반)")
    lines_before = python2_code.count('\n') + 1
    logger.debug(f"변환 전 줄 수: {lines_before:,}")

    python3_code = python2_code
    conversions = []

    # 1. print 문 → print() 함수
    # print "text" → print("text")
    # print >> file, "text" → print("text", file=file)
    print_pattern = re.compile(r'(\s+)print\s+(["\'].*?["\'])', re.MULTILINE)
    matches = print_pattern.findall(python3_code)
    if matches:
        python3_code = print_pattern.sub(r'\1print(\2)', python3_code)
        conversions.append(f"print 문: {len(matches)}개")
        logger.debug(f"print 문 변환: {len(matches)}개")

    # 2. except E, e → except E as e
    except_pattern = re.compile(r'except\s+(\w+)\s*,\s*(\w+)\s*:', re.MULTILINE)
    matches = except_pattern.findall(python3_code)
    if matches:
        python3_code = except_pattern.sub(r'except \1 as \2:', python3_code)
        conversions.append(f"except 구문: {len(matches)}개")
        logger.debug(f"except 구문 변환: {len(matches)}개")

    # 3. bare except → except Exception
    bare_except_pattern = re.compile(r'except\s*:\s*$', re.MULTILINE)
    matches = bare_except_pattern.findall(python3_code)
    if matches:
        python3_code = bare_except_pattern.sub(r'except Exception:', python3_code)
        conversions.append(f"bare except: {len(matches)}개")
        logger.debug(f"bare except 변환: {len(matches)}개")

    # 4. unicode() → str()
    unicode_pattern = re.compile(r'\bunicode\s*\(')
    matches = unicode_pattern.findall(python3_code)
    if matches:
        python3_code = unicode_pattern.sub(r'str(', python3_code)
        conversions.append(f"unicode(): {len(matches)}개")
        logger.debug(f"unicode() 변환: {len(matches)}개")

    # 5. .has_key() → in
    has_key_pattern = re.compile(r'\.has_key\s*\(\s*([^)]+)\s*\)')
    matches = has_key_pattern.findall(python3_code)
    if matches:
        # 주의: 완벽한 변환은 어려우므로 주석으로 TODO 추가
        python3_code = has_key_pattern.sub(r' # TODO: .has_key(\1) -> (\1 in dict)', python3_code)
        conversions.append(f"has_key(): {len(matches)}개 (TODO)")
        logger.warning(f"has_key() 변환: {len(matches)}개 (수동 검토 필요)")

    lines_after = python3_code.count('\n') + 1
    logger.debug(f"변환 후 줄 수: {lines_after:,}")

    if conversions:
        logger.info(f"변환 항목: {', '.join(conversions)}")
    else:
        logger.info("변환 필요 없음 (이미 Python 3 코드)")

    # Python 3 구문 검증
    logger.debug("Python 3 구문 검증 중...")
    try:
        ast.parse(python3_code)
        logger.debug("Python 3 구문 검증 통과")
    except SyntaxError as e:
        logger.error(f"Python 3 구문 오류: {e}")
        if e.lineno:
            logger.error(f"위치: {e.lineno}:{e.offset}")
            # 해당 줄 주변 출력
            lines = python3_code.split('\n')
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            logger.debug("문제가 있는 코드:")
            for i in range(start, end):
                marker = ">>>" if i + 1 == e.lineno else "   "
                logger.debug(f"{marker} {i+1:4d}: {lines[i]}")
        raise

    logger.info("Python 2 → 3 변환 완료")
    return python3_code


def parse_linux_bash_script(bash_file: str, logger: logging.Logger) -> Dict[str, List[str]]:
    """Linux bash 스크립트에서 명령어 추출 (Linux 전용)

    Linux_Check_1.txt 파일을 파싱하여 각 KISA 코드별 bash 명령어를 추출합니다.

    Args:
        bash_file: Linux_Check_1.txt 파일 경로
        logger: Logger 인스턴스

    Returns:
        KISA 코드별 명령어 딕셔너리
        예: {"U-01": ["cat /etc/pam.d/login", "cat /etc/securetty"], ...}

    Note:
        - Linux 전용 (macOS, Windows는 별도 구현 필요)
        - 명령어 리다이렉션 (>>report.txt) 자동 제거
        - 변수 ($APACHE_DIRECTORY 등)는 그대로 유지
    """
    logger.info(f"bash 스크립트 파싱 시작: {bash_file}")

    # 파일 읽기
    try:
        with open(bash_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        logger.debug(f"bash 파일 읽기 완료: {len(lines):,} 줄")
    except FileNotFoundError:
        logger.warning(f"bash 파일 없음: {bash_file}, 빈 딕셔너리 반환")
        return {}
    except Exception as e:
        logger.error(f"bash 파일 읽기 실패: {e}")
        return {}

    commands_by_kisa = {}
    current_kisa = None
    current_commands = []
    in_for_loop = False

    # KISA 번호 패턴: "1-1 root 계정 원격 접속 제한"
    kisa_pattern = re.compile(r'^echo\s+"(\d+)-(\d+)\s')

    # 명령어 시작 패턴
    cmd_patterns = ['cat', 'ls', 'ps', 'grep', 'egrep', 'find', 'pwconv']

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # KISA 코드 인식
        match = kisa_pattern.match(line)
        if match:
            # 이전 섹션 저장
            if current_kisa and current_commands:
                commands_by_kisa[current_kisa] = current_commands
                logger.debug(f"{current_kisa}: {len(current_commands)}개 명령어 추출")

            section, num = match.groups()
            current_kisa = f"U-{int(num):02d}"
            current_commands = []
            in_for_loop = False
            continue

        # 섹션 종료 (tmp 또는 tmp_s)
        if line.startswith('tmp'):
            if current_kisa and current_commands:
                commands_by_kisa[current_kisa] = current_commands
                logger.debug(f"{current_kisa}: {len(current_commands)}개 명령어 추출")
            current_kisa = None
            current_commands = []
            in_for_loop = False
            continue

        # for 루프 감지
        if line.startswith('for '):
            in_for_loop = True
            continue
        if line == 'done':
            in_for_loop = False
            continue
        if line == 'do':
            continue

        # 명령어 수집 (현재 KISA 섹션 내에서만)
        if current_kisa:
            # 명령어 라인인지 확인
            is_command = any(line.startswith(cmd) for cmd in cmd_patterns)

            if is_command:
                # 리다이렉션 제거
                cmd = re.sub(r'\s*[12]?>>?report[_a-z]*\.txt', '', line)
                cmd = re.sub(r'\s*[12]?>report[_a-z]*\.txt', '', cmd)
                cmd = cmd.strip()

                if cmd:
                    current_commands.append(cmd)
                    logger.debug(f"{current_kisa}: 명령어 추출: {cmd[:50]}...")

    # 마지막 섹션 저장
    if current_kisa and current_commands:
        commands_by_kisa[current_kisa] = current_commands
        logger.debug(f"{current_kisa}: {len(current_commands)}개 명령어 추출")

    logger.info(f"bash 스크립트 파싱 완료: {len(commands_by_kisa)}개 KISA 코드 처리")

    # 통계 정보
    total_commands = sum(len(cmds) for cmds in commands_by_kisa.values())
    logger.info(f"총 {total_commands}개 명령어 추출 (평균 {total_commands / len(commands_by_kisa):.1f}개/규칙)")

    # 명령어 없는 KISA 코드 확인
    empty_kisa = [k for k, v in commands_by_kisa.items() if not v]
    if empty_kisa:
        logger.warning(f"명령어 없는 KISA 코드: {empty_kisa}")

    return commands_by_kisa


def extract_severity(node: ast.FunctionDef, logger: logging.Logger) -> Severity:
    """함수 내에서 심각도 추출

    Legacy 패턴:
    - _SETHIGH() → Severity.HIGH
    - _SETMID() → Severity.MID
    - _SETLOW() → Severity.LOW

    Args:
        node: AST FunctionDef 노드
        logger: Logger 인스턴스

    Returns:
        심각도 (기본값: HIGH)
    """
    # 함수 내 모든 노드 순회
    for child in ast.walk(node):
        # Call 노드 찾기
        if isinstance(child, ast.Call):
            # 함수 호출 이름 확인
            if isinstance(child.func, ast.Name):
                func_name = child.func.id

                if func_name == '_SETHIGH':
                    logger.debug(f"{node.name}: Severity.HIGH")
                    return Severity.HIGH
                elif func_name == '_SETMID':
                    logger.debug(f"{node.name}: Severity.MID")
                    return Severity.MID
                elif func_name == '_SETLOW':
                    logger.debug(f"{node.name}: Severity.LOW")
                    return Severity.LOW

    # 심각도 함수 호출을 찾지 못한 경우
    logger.warning(f"{node.name}: 심각도 미발견, 기본값 HIGH 사용")
    return Severity.HIGH


def extract_function_info(
    node: ast.FunctionDef,
    func_number_str: str,
    commands_by_kisa: Dict[str, List[str]],
    logger: logging.Logger
) -> FunctionInfo:
    """단일 함수 정보 추출

    Args:
        node: AST FunctionDef 노드
        func_number_str: 함수 번호 (문자열, 예: "4")
        commands_by_kisa: KISA 코드별 bash 명령어 딕셔너리
        logger: Logger 인스턴스

    Returns:
        FunctionInfo 객체
    """
    func_number = int(func_number_str)

    # 1. KISA 코드 생성
    kisa_code = f"U-{func_number:02d}"

    # 2. 소스 코드 추출 (Python 3.9+)
    try:
        source = ast.unparse(node)
    except Exception as e:
        logger.warning(f"{node.name}: ast.unparse 실패, 빈 소스 사용: {e}")
        source = f"# ast.unparse 실패: {node.name}"

    # 3. 복잡도 계산 (AST 노드 수)
    complexity = len(list(ast.walk(node)))

    # 4. 심각도 추출
    severity = extract_severity(node, logger)

    # 5. bash 명령어 추출 (Task 3.1)
    commands = commands_by_kisa.get(kisa_code, [])
    if commands:
        logger.debug(f"{node.name}: {len(commands)}개 명령어 연결")
    else:
        logger.debug(f"{node.name}: 명령어 없음 (정상, 일부 규칙은 수동 점검)")

    logger.debug(
        f"{node.name}: number={func_number}, kisa={kisa_code}, "
        f"complexity={complexity}, severity={severity.value}, commands={len(commands)}"
    )

    return FunctionInfo(
        name=node.name,
        number=func_number,
        kisa_code=kisa_code,
        source=source,
        complexity=complexity,
        severity=severity,
        commands=commands,
        ast_node=node
    )


def extract_functions(
    python3_code: str,
    commands_by_kisa: Dict[str, List[str]],
    logger: logging.Logger
) -> List[FunctionInfo]:
    """AST 기반 함수 추출

    Python 3 코드를 AST로 파싱하고, _XSCRIPT 패턴의 Legacy 함수를 추출합니다.

    Args:
        python3_code: Python 3 소스 코드
        commands_by_kisa: KISA 코드별 bash 명령어 딕셔너리
        logger: Logger 인스턴스

    Returns:
        추출된 함수 정보 목록 (FunctionInfo)

    Raises:
        SyntaxError: Python 3 파싱 실패
    """
    logger.info("AST 기반 함수 추출 시작")

    # 1. AST 파싱
    try:
        tree = ast.parse(python3_code)
        logger.debug("AST 파싱 완료")
    except SyntaxError as e:
        logger.error(f"AST 파싱 실패: {e}")
        raise

    # 2. 함수 추출
    functions = []
    func_pattern = re.compile(r'^_(\d+)SCRIPT$')

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 3. 함수명 패턴 확인: _\d+SCRIPT
            match = func_pattern.match(node.name)
            if match:
                try:
                    func_info = extract_function_info(
                        node, match.group(1), commands_by_kisa, logger
                    )
                    functions.append(func_info)
                except Exception as e:
                    logger.error(f"{node.name}: 함수 정보 추출 실패: {e}")
                    continue

    # 4. 함수 번호 순 정렬
    functions.sort(key=lambda f: f.number)

    logger.info(f"함수 추출 완료: {len(functions)}개")

    if not functions:
        logger.warning("추출된 함수가 없습니다. _XSCRIPT 패턴 확인 필요")

    return functions


def infer_category(kisa_code: str) -> str:
    """KISA 코드로 카테고리 자동 추론

    KISA 표준 번호 범위를 기반으로 카테고리를 결정합니다.

    Args:
        kisa_code: KISA 코드 (U-01, U-04, ...)

    Returns:
        카테고리 문자열

    Examples:
        >>> infer_category("U-01")
        '계정관리'
        >>> infer_category("U-18")
        '파일 및 디렉터리 관리'
        >>> infer_category("U-42")
        '서비스 관리'
    """
    # U-XX에서 숫자 부분 추출
    num = int(kisa_code.split('-')[1])

    if 1 <= num <= 15:
        return "계정관리"
    elif 16 <= num <= 35:
        return "파일 및 디렉터리 관리"
    elif 36 <= num <= 70:
        return "서비스 관리"
    elif num == 71:
        return "패치 관리"
    else:  # 72, 73
        return "로그 관리"


def generate_validator_name(kisa_code: str) -> str:
    """validator 함수명 생성

    KISA 코드를 validator 모듈의 함수명으로 변환합니다.

    Args:
        kisa_code: KISA 코드 (U-01, U-04, ...)

    Returns:
        validator 함수 경로 문자열

    Examples:
        >>> generate_validator_name("U-01")
        'validators.linux.check_u01'
        >>> generate_validator_name("U-42")
        'validators.linux.check_u42'
    """
    # U-01 → u01, U-42 → u42
    code_lower = kisa_code.lower().replace('-', '')
    return f"validators.linux.check_{code_lower}"


def generate_yaml_template(func_info: FunctionInfo) -> Dict[str, Any]:
    """FunctionInfo에서 YAML 템플릿 생성 (Task 3.2)

    FunctionInfo 객체를 받아 YAML 규칙 파일 구조를 dict로 생성합니다.

    Args:
        func_info: 함수 정보 (FunctionInfo)

    Returns:
        YAML 템플릿 딕셔너리

    Example:
        >>> func_info = FunctionInfo(
        ...     name="_1SCRIPT",
        ...     number=1,
        ...     kisa_code="U-01",
        ...     source="...",
        ...     complexity=82,
        ...     severity=Severity.HIGH,
        ...     commands=["cat /etc/pam.d/login", "cat /etc/securetty"]
        ... )
        >>> yaml_dict = generate_yaml_template(func_info)
        >>> yaml_dict['id']
        'U-01'
        >>> yaml_dict['name']
        'root 계정 원격 접속 제한'
    """
    # 규칙 이름 (KISA_NAMES에서 가져오기)
    name = KISA_NAMES.get(func_info.kisa_code, f"규칙 {func_info.kisa_code}")

    # 카테고리 자동 추론
    category = infer_category(func_info.kisa_code)

    # validator 함수명 생성
    validator = generate_validator_name(func_info.kisa_code)

    # YAML 구조 생성
    yaml_dict = {
        "id": func_info.kisa_code,
        "name": name,
        "category": category,
        "severity": func_info.severity.value,
        "description": f"{name} 취약점을 점검합니다.",
        "check": {
            "commands": func_info.commands
        },
        "validator": validator,
        "remediation": {
            "auto": False,
            "backup_files": [],
            "commands": []
        }
    }

    return yaml_dict


def save_yaml_file(
    yaml_dict: Dict[str, Any],
    kisa_code: str,
    output_dir: Path,
    logger: logging.Logger
) -> None:
    """YAML 딕셔너리를 파일로 저장 (Task 3.3)

    YAML 템플릿 dict를 파일로 저장합니다. UTF-8 인코딩으로 한글을 보존합니다.

    Args:
        yaml_dict: YAML 템플릿 딕셔너리
        kisa_code: KISA 코드 (U-01, U-04, ...)
        output_dir: 출력 디렉토리 (Path 객체)
        logger: Logger 인스턴스

    Raises:
        OSError: 디렉토리 생성 실패
        IOError: 파일 쓰기 실패
        yaml.YAMLError: YAML 변환 실패

    Example:
        >>> yaml_dict = {"id": "U-01", "name": "root 계정 원격 접속 제한", ...}
        >>> save_yaml_file(yaml_dict, "U-01", Path("config/rules/linux"), logger)
        # config/rules/linux/U-01.yaml 파일 생성됨
    """
    # 파일 경로 생성: output_dir/U-01.yaml
    yaml_file = output_dir / f"{kisa_code}.yaml"

    try:
        # YAML 변환 (한글 보존)
        yaml_content = yaml.dump(
            yaml_dict,
            allow_unicode=True,     # 한글 출력
            sort_keys=False,        # 키 순서 유지
            default_flow_style=False,  # 블록 스타일
            indent=2                # 들여쓰기 2칸
        )

        # UTF-8로 파일 쓰기
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        logger.info(f"{kisa_code}.yaml 저장 완료")
        logger.debug(f"파일 경로: {yaml_file.absolute()}")

    except yaml.YAMLError as e:
        logger.error(f"{kisa_code}: YAML 변환 실패: {e}")
        raise
    except IOError as e:
        logger.error(f"{kisa_code}: 파일 쓰기 실패: {e}")
        raise


def generate_validator_skeleton(func_info: FunctionInfo) -> str:
    """Validator 함수 스켈레톤 코드 생성 (Task 4.0)

    FunctionInfo 객체로부터 validator 함수의 Python 코드를 생성합니다.
    함수는 실행 가능한 스켈레톤이며, TODO 주석으로 구현 위치를 표시합니다.

    Args:
        func_info: 함수 정보 (FunctionInfo)

    Returns:
        Python 함수 코드 문자열

    Example:
        >>> func_info = FunctionInfo(
        ...     name="_1SCRIPT",
        ...     kisa_code="U-01",
        ...     severity=Severity.HIGH,
        ...     ...
        ... )
        >>> code = generate_validator_skeleton(func_info)
        >>> print(code)
        def check_u01(command_outputs: List[str]) -> CheckResult:
            \"\"\"U-01: root 계정 원격 접속 제한
            ...
            \"\"\"
            ...
    """
    # U-01 → u01, U-42 → u42
    kisa_code_lower = func_info.kisa_code.lower().replace('-', '')
    func_name = f"check_{kisa_code_lower}"

    # 규칙 이름
    name = KISA_NAMES.get(func_info.kisa_code, "알 수 없는 항목")

    # 함수 코드 생성
    code = f'''def {func_name}(command_outputs: List[str]) -> CheckResult:
    """{func_info.kisa_code}: {name}

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
        - Legacy 코드 {func_info.name}의 로직 참고
        - command_outputs 파싱 및 검증 로직 추가
        - 심각도: {func_info.severity.value}
    """
    # TODO: 구현 필요
    return CheckResult(
        status=Status.MANUAL,
        message="구현 예정 - {func_info.kisa_code} {name}"
    )


'''
    return code


def save_validator_files(
    functions: List[FunctionInfo],
    output_dir: Path,
    logger: logging.Logger
) -> None:
    """Validator 함수들을 카테고리별 파일로 저장 (Task 4.0)

    73개 validator 함수를 카테고리별로 그룹화하여 5개 Python 파일로 저장합니다.
    각 파일은 UTF-8 인코딩으로 저장되며, 필요한 import 문이 자동으로 추가됩니다.

    Args:
        functions: 함수 정보 목록 (FunctionInfo)
        output_dir: 출력 디렉토리 (src/core/analyzer/validators/linux/)
        logger: Logger 인스턴스

    Raises:
        OSError: 디렉토리 생성 실패
        IOError: 파일 쓰기 실패

    Example:
        >>> functions = [...]  # 73개 FunctionInfo
        >>> output_dir = Path("src/core/analyzer/validators/linux/")
        >>> save_validator_files(functions, output_dir, logger)
        # account_management.py, file_management.py 등 5개 파일 생성
    """
    logger.info("Validator 파일 저장 시작")

    # 카테고리별로 함수 그룹화
    categories = {
        "계정관리": ("account_management.py", []),
        "파일 및 디렉터리 관리": ("file_management.py", []),
        "서비스 관리": ("service_management.py", []),
        "패치 관리": ("patch_management.py", []),
        "로그 관리": ("log_management.py", [])
    }

    # 각 함수를 카테고리에 할당
    for func in functions:
        category = infer_category(func.kisa_code)
        if category in categories:
            categories[category][1].append(func)
        else:
            logger.warning(f"{func.kisa_code}: 알 수 없는 카테고리 {category}")

    # 카테고리별로 파일 생성
    for category_name, (filename, funcs) in categories.items():
        if not funcs:
            logger.debug(f"{category_name}: 함수 없음, 파일 생략")
            continue

        file_path = output_dir / filename
        logger.info(f"{filename}: {len(funcs)}개 함수 저장 중...")

        try:
            # 파일 헤더
            header = f'''"""
Linux 보안 점검 Validator 함수 모음 - {category_name}

이 모듈은 KISA 기준 Linux 보안 점검 항목 중 {category_name} 관련
validator 함수들을 포함합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)
"""

from typing import List
from src.core.domain.models import CheckResult, Status


'''

            # 각 함수 스켈레톤 생성
            function_codes = []
            for func in funcs:
                code = generate_validator_skeleton(func)
                function_codes.append(code)

            # 파일 내용 조합
            file_content = header + '\n'.join(function_codes)

            # UTF-8로 파일 쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            logger.info(f"{filename} 저장 완료: {len(funcs)}개 함수")
            logger.debug(f"파일 경로: {file_path.absolute()}")

        except IOError as e:
            logger.error(f"{filename}: 파일 쓰기 실패: {e}")
            raise

    logger.info("Validator 파일 저장 완료")


def create_init_file(
    functions: List[FunctionInfo],
    output_dir: Path,
    logger: logging.Logger
) -> None:
    """validators/linux/__init__.py 파일 생성 (Task 4.0)

    모든 validator 함수를 import하는 __init__.py를 생성합니다.
    이를 통해 다른 모듈에서 간단하게 validator를 사용할 수 있습니다.

    Args:
        functions: 함수 정보 목록 (FunctionInfo)
        output_dir: 출력 디렉토리 (src/core/analyzer/validators/linux/)
        logger: Logger 인스턴스

    Raises:
        IOError: 파일 쓰기 실패

    Example:
        >>> create_init_file(functions, output_dir, logger)
        # __init__.py 파일 생성됨
        # from .account_management import check_u01, check_u02, ...
    """
    logger.info("__init__.py 파일 생성 중...")

    init_file = output_dir / "__init__.py"

    # 카테고리별 파일명 매핑
    category_files = {
        "계정관리": "account_management",
        "파일 및 디렉터리 관리": "file_management",
        "서비스 관리": "service_management",
        "패치 관리": "patch_management",
        "로그 관리": "log_management"
    }

    # 카테고리별로 함수 그룹화
    imports_by_category = {}
    for func in functions:
        category = infer_category(func.kisa_code)
        module_name = category_files.get(category)
        if not module_name:
            continue

        if module_name not in imports_by_category:
            imports_by_category[module_name] = []

        kisa_lower = func.kisa_code.lower().replace('-', '')
        func_name = f"check_{kisa_lower}"
        imports_by_category[module_name].append(func_name)

    # __init__.py 내용 생성
    header = '''"""Linux validator 함수 모듈

이 모듈은 KISA 기준 Linux 보안 점검 항목(U-01 ~ U-73)의
validator 함수들을 제공합니다.

생성일: 2025-10-17
자동 생성: scripts/migrate_legacy.py (Task 4.0)

사용 예시:
    >>> from src.core.analyzer.validators.linux import check_u01
    >>> result = check_u01(["..."])
    >>> print(result.status)
"""

'''

    import_lines = []
    all_functions = []

    # 각 모듈에서 import
    for module_name in sorted(imports_by_category.keys()):
        funcs = sorted(imports_by_category[module_name])
        all_functions.extend(funcs)

        # import 문 생성 (한 줄에 최대 4개)
        for i in range(0, len(funcs), 4):
            chunk = funcs[i:i+4]
            import_line = f"from .{module_name} import {', '.join(chunk)}"
            import_lines.append(import_line)

    imports = '\n'.join(import_lines)

    # __all__ 리스트 생성
    all_list = '__all__ = [\n'
    for i in range(0, len(all_functions), 4):
        chunk = all_functions[i:i+4]
        all_list += '    ' + ', '.join(f'"{f}"' for f in chunk) + ',\n'
    all_list += ']\n'

    file_content = header + imports + '\n\n' + all_list

    try:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(file_content)

        logger.info(f"__init__.py 생성 완료: {len(all_functions)}개 함수 export")
        logger.debug(f"파일 경로: {init_file.absolute()}")

    except IOError as e:
        logger.error(f"__init__.py 쓰기 실패: {e}")
        raise


def filter_functions(
    functions: List[FunctionInfo],
    args: argparse.Namespace,
    logger: logging.Logger
) -> List[FunctionInfo]:
    """함수 필터링 (--functions 또는 --all)

    Args:
        functions: 전체 함수 목록 (FunctionInfo)
        args: CLI 인자
        logger: Logger 인스턴스

    Returns:
        필터링된 함수 목록 (FunctionInfo)
    """
    if args.all:
        logger.info(f"모든 함수 선택: {len(functions)}개")
        return functions

    # --functions로 지정된 함수만
    selected_kisa_codes = set(f.strip() for f in args.functions.split(','))
    filtered = [
        f for f in functions
        if f.kisa_code in selected_kisa_codes
    ]

    logger.info(f"선택된 함수: {len(filtered)}개 / {len(functions)}개")

    # 누락된 함수 경고
    found_codes = {f.kisa_code for f in filtered}
    missing = selected_kisa_codes - found_codes
    if missing:
        logger.warning(f"찾을 수 없는 함수: {missing}")

    return filtered


def main() -> int:
    """메인 함수

    Returns:
        종료 코드 (0: 성공, 1: 실패)
    """
    # 1. CLI 파싱
    args = parse_arguments()

    # 2. 로깅 초기화
    logger = setup_logging(args.verbose, args.log_file)
    logger.info("=" * 60)
    logger.info("Python 2 → 3 마이그레이션 스크립트")
    logger.info("=" * 60)
    logger.info(f"입력 파일: {args.input}")
    logger.info(f"출력 디렉토리: {args.output_dir}")
    if args.dry_run:
        logger.info("모드: Dry-run (시뮬레이션)")

    try:
        # 3. 입력 검증
        logger.info("입력 검증 중...")
        validate_inputs(args, logger)
        logger.info("입력 검증 완료")

        # 4. Legacy 파일 읽기 (Task 2.2)
        logger.info("Legacy 파일 읽기 중...")
        legacy_code = read_legacy_file(args.input, logger)
        logger.info(f"Legacy 파일 읽기 완료: {len(legacy_code):,} bytes")

        # 5. Python 2→3 변환 (Task 2.3)
        logger.info("Python 3 변환 중...")
        python3_code = convert_to_python3(legacy_code, logger)
        logger.info("Python 3 변환 완료")

        # 5.5. bash 명령어 추출 (Task 3.1)
        logger.info("bash 명령어 추출 중...")
        bash_script_path = PROJECT_ROOT / "legacy/infra/linux/자동점검 코드/점검자료조사/Linux_Check_1.txt"
        commands_by_kisa = parse_linux_bash_script(str(bash_script_path), logger)
        logger.info(f"bash 명령어 추출 완료: {len(commands_by_kisa)}개 규칙")

        # 6. 함수 추출 (Task 2.4 + Task 3.1)
        logger.info("함수 추출 중...")
        functions = extract_functions(python3_code, commands_by_kisa, logger)
        logger.info(f"함수 추출 완료: {len(functions)}개")

        # 7. 함수 필터링
        selected_functions = filter_functions(functions, args, logger)

        # 8. 각 함수 처리 (Task 3.0, 4.0)
        logger.info("=" * 60)
        logger.info("함수 처리 시작")
        logger.info("=" * 60)

        results = []
        for i, func in enumerate(selected_functions, 1):
            logger.info(f"[{i}/{len(selected_functions)}] 처리 중: {func.kisa_code}")

            # Task 3.2: YAML 템플릿 생성
            yaml_dict = generate_yaml_template(func)
            logger.debug(f"{func.kisa_code}: YAML 템플릿 생성 완료")

            # TODO: Task 4.0에서 구현
            # - Validator 스켈레톤 생성

            results.append({
                'function': func,
                'yaml': yaml_dict,
                'validator': None,  # TODO: Task 4.0
                'commands': func.commands
            })

        # 9. 파일 저장 (--dry-run이 아닐 때만)
        if not args.dry_run:
            logger.info("=" * 60)
            logger.info("YAML 파일 저장 중...")
            logger.info("=" * 60)

            # 출력 디렉토리 Path 객체 생성
            output_dir = Path(args.output_dir)

            # YAML 파일 저장
            for i, result in enumerate(results, 1):
                func = result['function']
                yaml_dict = result['yaml']

                try:
                    save_yaml_file(yaml_dict, func.kisa_code, output_dir, logger)
                except Exception as e:
                    logger.error(f"{func.kisa_code}: 파일 저장 실패 - {e}")
                    # 에러가 발생해도 계속 진행

            logger.info("=" * 60)
            logger.info(f"YAML 파일 저장 완료: {len(results)}개 파일")
            logger.info(f"저장 위치: {output_dir.absolute()}")
            logger.info("=" * 60)

            # Task 4.0 - Validator 파일 저장
            logger.info("=" * 60)
            logger.info("Validator 파일 생성 중...")
            logger.info("=" * 60)

            # Validator 디렉토리: src/core/analyzer/validators/linux/
            validator_dir = PROJECT_ROOT / "src/core/analyzer/validators/linux"
            validator_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Validator 디렉토리: {validator_dir.absolute()}")

            # Validator 파일 저장 (5개 파일: 카테고리별)
            save_validator_files(selected_functions, validator_dir, logger)

            # __init__.py 생성
            create_init_file(selected_functions, validator_dir, logger)

            logger.info("=" * 60)
            logger.info(f"Validator 파일 생성 완료: {len(selected_functions)}개 함수")
            logger.info(f"저장 위치: {validator_dir.absolute()}")
            logger.info("=" * 60)

        else:
            logger.info("Dry-run 모드: 파일 저장 생략")

        # 10. 마이그레이션 보고서 생성
        logger.info("마이그레이션 보고서 생성 중...")
        # TODO: Task 6.1, 6.2에서 구현

        logger.info("=" * 60)
        logger.info("마이그레이션 완료!")
        logger.info("=" * 60)
        return 0

    except NotImplementedError as e:
        logger.error(f"구현 필요: {e}")
        logger.info("현재는 Task 2.1 (기본 구조)만 구현되었습니다.")
        logger.info("다음 단계: Task 2.2 (인코딩 변환) 구현")
        return 1

    except (FileNotFoundError, ValueError, PermissionError) as e:
        logger.error(f"입력 오류: {e}")
        return 1

    except Exception as e:
        logger.error(f"치명적 오류: {e}")
        logger.debug("상세 정보:", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
