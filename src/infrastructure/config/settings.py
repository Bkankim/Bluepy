"""설정 관리

애플리케이션 설정을 JSON 파일로 저장/로드하는 모듈입니다.

주요 기능:
- 설정 저장/로드
- 기본값 관리
- 에러 처리
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


# 설정 파일 경로
DEFAULT_SETTINGS_FILE = Path("config/settings.json")

# 기본값 정의
DEFAULT_SETTINGS = {
    "appearance": {
        "theme": "dark",  # dark 또는 light
    },
    "logging": {
        "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    },
    "language": {
        "locale": "ko_KR",  # ko_KR (한국어), en_US (English)
    },
    "backup": {
        "directory": "data/backups",  # 백업 디렉토리 경로
    },
}


def get_default_settings() -> Dict[str, Any]:
    """기본 설정 반환

    Returns:
        기본 설정 딕셔너리 (깊은 복사본)
    """
    import copy

    return copy.deepcopy(DEFAULT_SETTINGS)


def load_settings(settings_file: Optional[Path] = None) -> Dict[str, Any]:
    """설정 로드

    JSON 파일에서 설정을 로드합니다.
    파일이 없거나 파싱 오류가 발생하면 기본값을 반환합니다.

    Args:
        settings_file: 설정 파일 경로 (기본값: config/settings.json)

    Returns:
        설정 딕셔너리
    """
    if settings_file is None:
        settings_file = DEFAULT_SETTINGS_FILE

    # 파일이 없으면 기본값 반환
    if not settings_file.exists():
        return get_default_settings()

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # 기본값과 병합 (누락된 키 처리)
        merged_settings = get_default_settings()
        _deep_update(merged_settings, settings)

        return merged_settings

    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load settings from {settings_file}: {e}")
        print("Using default settings")
        return get_default_settings()


def save_settings(settings: Dict[str, Any], settings_file: Optional[Path] = None) -> bool:
    """설정 저장

    설정을 JSON 파일로 저장합니다.

    Args:
        settings: 저장할 설정 딕셔너리
        settings_file: 설정 파일 경로 (기본값: config/settings.json)

    Returns:
        성공 여부
    """
    if settings_file is None:
        settings_file = DEFAULT_SETTINGS_FILE

    try:
        # 디렉토리 생성 (없으면)
        settings_file.parent.mkdir(parents=True, exist_ok=True)

        # JSON 저장 (들여쓰기 포함)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        return True

    except (IOError, TypeError) as e:
        print(f"Error: Failed to save settings to {settings_file}: {e}")
        return False


def _deep_update(base: Dict[str, Any], update: Dict[str, Any]) -> None:
    """딕셔너리 깊은 병합

    update 딕셔너리의 값을 base 딕셔너리에 재귀적으로 병합합니다.

    Args:
        base: 기본 딕셔너리 (변경됨)
        update: 업데이트할 값
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


def get_setting(settings: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """설정 값 가져오기 (점 표기법)

    "appearance.theme" 형태의 키로 중첩된 값을 가져옵니다.

    Args:
        settings: 설정 딕셔너리
        key_path: 점으로 구분된 키 경로 (예: "appearance.theme")
        default: 키가 없을 때 반환할 기본값

    Returns:
        설정 값 또는 기본값

    Example:
        >>> settings = {"appearance": {"theme": "dark"}}
        >>> get_setting(settings, "appearance.theme")
        'dark'
        >>> get_setting(settings, "nonexistent.key", "fallback")
        'fallback'
    """
    keys = key_path.split(".")
    value = settings

    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def set_setting(settings: Dict[str, Any], key_path: str, value: Any) -> None:
    """설정 값 설정 (점 표기법)

    "appearance.theme" 형태의 키로 중첩된 값을 설정합니다.

    Args:
        settings: 설정 딕셔너리 (변경됨)
        key_path: 점으로 구분된 키 경로 (예: "appearance.theme")
        value: 설정할 값

    Example:
        >>> settings = {}
        >>> set_setting(settings, "appearance.theme", "dark")
        >>> settings
        {'appearance': {'theme': 'dark'}}
    """
    keys = key_path.split(".")
    current = settings

    # 마지막 키 전까지 딕셔너리 생성
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # 마지막 키에 값 설정
    current[keys[-1]] = value


__all__ = [
    "get_default_settings",
    "load_settings",
    "save_settings",
    "get_setting",
    "set_setting",
    "DEFAULT_SETTINGS_FILE",
]
