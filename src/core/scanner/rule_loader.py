"""YAML 규칙 파일 로더

규칙 파일 디렉토리에서 YAML 파일을 읽어서
RuleMetadata 객체 리스트로 변환합니다.

주요 기능:
- YAML 파일 파싱
- RuleMetadata 객체 생성
- Pydantic validation
- 오류 처리 및 로깅
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import ValidationError

from ..domain.models import RemediationInfo, RuleMetadata, Severity

logger = logging.getLogger(__name__)


class RuleLoaderError(Exception):
    """규칙 로더 예외"""

    pass


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """YAML 파일 읽기

    Args:
        file_path: YAML 파일 경로

    Returns:
        파싱된 YAML 딕셔너리

    Raises:
        RuleLoaderError: 파일 읽기 또는 파싱 실패
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise RuleLoaderError(f"YAML 파일이 딕셔너리가 아닙니다: {file_path}")

        return data

    except FileNotFoundError:
        raise RuleLoaderError(f"파일을 찾을 수 없습니다: {file_path}")
    except yaml.YAMLError as e:
        raise RuleLoaderError(f"YAML 파싱 실패: {file_path}, 오류: {e}")
    except Exception as e:
        raise RuleLoaderError(f"파일 읽기 실패: {file_path}, 오류: {e}")


def convert_yaml_to_metadata(yaml_data: Dict[str, Any], file_path: Path) -> RuleMetadata:
    """YAML 딕셔너리를 RuleMetadata로 변환

    YAML 구조:
        id, name, category, severity, description
        check:
          commands: [...]
        validator
        remediation: {...}

    RuleMetadata 구조:
        id, name, category, severity, kisa_standard, description
        commands: [...]
        validator
        remediation

    Args:
        yaml_data: 파싱된 YAML 딕셔너리
        file_path: 파일 경로 (오류 메시지용)

    Returns:
        RuleMetadata 객체

    Raises:
        RuleLoaderError: 필수 필드 누락 또는 validation 실패
    """
    try:
        # 필수 필드 확인
        required_fields = [
            "id",
            "name",
            "category",
            "severity",
            "description",
            "check",
            "validator",
        ]
        missing_fields = [f for f in required_fields if f not in yaml_data]
        if missing_fields:
            raise RuleLoaderError(f"필수 필드 누락: {', '.join(missing_fields)} ({file_path})")

        # check.commands 추출
        check_data = yaml_data.get("check", {})
        commands = check_data.get("commands", [])

        if not commands:
            # 명령어가 없는 경우 경고 (수동 점검 규칙일 수 있음)
            logger.warning(f"명령어가 없는 규칙: {yaml_data.get('id')} ({file_path})")
            commands = []  # 빈 리스트 허용

        # remediation 정보 변환
        remediation = None
        remediation_data = yaml_data.get("remediation")
        if remediation_data:
            try:
                remediation = RemediationInfo(**remediation_data)
            except ValidationError as e:
                logger.warning(f"Remediation validation 실패: {yaml_data.get('id')}, {e}")
                # Remediation은 선택사항이므로 None으로 설정

        # Severity 변환
        severity_str = yaml_data.get("severity", "").lower()
        try:
            severity = Severity(severity_str)
        except ValueError:
            raise RuleLoaderError(f"올바르지 않은 severity 값: {severity_str} ({file_path})")

        # RuleMetadata 생성
        metadata = RuleMetadata(
            id=yaml_data["id"],
            name=yaml_data["name"],
            category=yaml_data["category"],
            severity=severity,
            kisa_standard=yaml_data["id"],  # id를 kisa_standard로 사용
            description=yaml_data["description"],
            commands=(
                commands if commands else ["echo 'No commands (manual check)'"]
            ),  # 최소 1개 필요
            validator=yaml_data["validator"],
            expected_result=yaml_data.get("expected_result"),
            remediation=remediation,
        )

        return metadata

    except ValidationError as e:
        raise RuleLoaderError(f"RuleMetadata validation 실패: {file_path}\n{e}")
    except KeyError as e:
        raise RuleLoaderError(f"필수 필드 누락: {e} ({file_path})")


def load_rules(rules_dir: str, platform: str = "linux") -> List[RuleMetadata]:
    """규칙 디렉토리에서 모든 YAML 파일 로드

    Args:
        rules_dir: 규칙 파일 디렉토리 경로 (예: config/rules 또는 config/rules/linux)
        platform: 플랫폼 이름 (linux, macos, windows) - rules_dir이 플랫폼 포함하지 않을 때만 사용

    Returns:
        RuleMetadata 객체 리스트 (id 순서로 정렬)

    Raises:
        RuleLoaderError: 디렉토리가 없거나 파일 로드 실패
    """
    rules_path = Path(rules_dir)

    # rules_dir이 이미 플랫폼별 경로인지 확인 (예: config/rules/linux)
    # 아니면 platform을 추가 (예: config/rules + linux)
    if rules_path.name not in ["linux", "macos", "windows"]:
        rules_path = rules_path / platform

    if not rules_path.exists():
        raise RuleLoaderError(f"규칙 디렉토리가 존재하지 않습니다: {rules_path}")

    if not rules_path.is_dir():
        raise RuleLoaderError(f"규칙 경로가 디렉토리가 아닙니다: {rules_path}")

    # YAML 파일 찾기 (*.yaml, *.yml)
    yaml_files = sorted(rules_path.glob("*.yaml")) + sorted(rules_path.glob("*.yml"))

    if not yaml_files:
        raise RuleLoaderError(f"규칙 파일이 없습니다: {rules_path}")

    rules: List[RuleMetadata] = []
    errors: List[str] = []

    for yaml_file in yaml_files:
        try:
            yaml_data = load_yaml_file(yaml_file)
            metadata = convert_yaml_to_metadata(yaml_data, yaml_file)
            rules.append(metadata)
            logger.debug(f"규칙 로드 성공: {metadata.id} ({yaml_file.name})")
        except RuleLoaderError as e:
            error_msg = f"{yaml_file.name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)

    if errors:
        logger.warning(f"규칙 로드 중 {len(errors)}개 오류 발생")
        # 오류가 있어도 성공한 규칙은 반환 (일부만 로드)

    if not rules:
        raise RuleLoaderError(f"규칙을 하나도 로드하지 못했습니다.\n오류:\n" + "\n".join(errors))

    # id 순서로 정렬 (U-01, U-02, ...)
    rules.sort(key=lambda r: r.id)

    logger.info(f"{platform} 규칙 {len(rules)}개 로드 완료 (오류: {len(errors)}개)")
    return rules


__all__ = [
    "RuleLoaderError",
    "load_yaml_file",
    "convert_yaml_to_metadata",
    "load_rules",
]
