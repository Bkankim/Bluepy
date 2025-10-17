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
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

# 프로젝트 루트를 sys.path에 추가 (src 모듈 import를 위해)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.domain.models import Severity

# 상수
DEFAULT_LOG_FILE = 'migration.log'
KISA_PATTERN = r'^U-\d{2}$'


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
        ast_node: AST FunctionDef 노드 (Optional, 추가 분석용)
    """
    name: str
    number: int
    kisa_code: str
    source: str
    complexity: int
    severity: Severity
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
    logger: logging.Logger
) -> FunctionInfo:
    """단일 함수 정보 추출

    Args:
        node: AST FunctionDef 노드
        func_number_str: 함수 번호 (문자열, 예: "4")
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

    logger.debug(
        f"{node.name}: number={func_number}, kisa={kisa_code}, "
        f"complexity={complexity}, severity={severity.value}"
    )

    return FunctionInfo(
        name=node.name,
        number=func_number,
        kisa_code=kisa_code,
        source=source,
        complexity=complexity,
        severity=severity,
        ast_node=node
    )


def extract_functions(python3_code: str, logger: logging.Logger) -> List[FunctionInfo]:
    """AST 기반 함수 추출

    Python 3 코드를 AST로 파싱하고, _XSCRIPT 패턴의 Legacy 함수를 추출합니다.

    Args:
        python3_code: Python 3 소스 코드
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
                    func_info = extract_function_info(node, match.group(1), logger)
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

        # 6. 함수 추출 (Task 2.4)
        logger.info("함수 추출 중...")
        functions = extract_functions(python3_code, logger)
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

            # TODO: Task 3.0, 4.0에서 구현
            # - bash 명령어 추출
            # - YAML 생성
            # - Validator 스켈레톤 생성

            results.append({
                'function': func,
                'yaml': None,  # TODO
                'validator': None,  # TODO
                'commands': []  # TODO
            })

        # 9. 파일 저장 (--dry-run이 아닐 때만)
        if not args.dry_run:
            logger.info("결과 저장 중...")
            # TODO: Task 3.3, 4.4에서 구현
            logger.info(f"결과 저장 완료: {args.output_dir}")
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
