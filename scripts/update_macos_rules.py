#!/usr/bin/env python3.12
"""Linux 규칙 40개를 macOS와 공유하도록 platforms 필드 업데이트

Explore 에이전트가 선별한 macOS 호환 규칙 40개:
- 계정 관리: U-01 ~ U-15 (15개)
- 파일 관리: U-16~U-20, U-23~U-30, U-32~U-35, U-39 (18개)
- 서비스 관리: U-36, U-38, U-40, U-46, U-59, U-64, U-67 (7개)
"""

import yaml
from pathlib import Path

# macOS 호환 가능한 규칙 ID 목록
MACOS_COMPATIBLE_RULES = [
    # 계정 관리 (15개)
    "U-01", "U-02", "U-03", "U-04", "U-05",
    "U-06", "U-07", "U-08", "U-09", "U-10",
    "U-11", "U-12", "U-13", "U-14", "U-15",
    # 파일 관리 (18개)
    "U-16", "U-17", "U-18", "U-19", "U-20",
    "U-23", "U-24", "U-25", "U-26", "U-27",
    "U-28", "U-29", "U-30", "U-32", "U-33",
    "U-34", "U-35", "U-39",
    # 서비스 관리 (7개)
    "U-36", "U-38", "U-40", "U-46", "U-59",
    "U-64", "U-67",
]


def update_rule_platforms(rule_file: Path) -> bool:
    """규칙 파일의 platforms 필드를 [linux, macos]로 업데이트

    Args:
        rule_file: YAML 규칙 파일 경로

    Returns:
        bool: 업데이트 성공 여부
    """
    try:
        # YAML 파일 읽기
        with open(rule_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 규칙 ID 확인
        rule_id = data.get("id")
        if rule_id not in MACOS_COMPATIBLE_RULES:
            return False

        # platforms 필드 업데이트
        current_platforms = data.get("platforms", ["linux"])
        if "macos" not in current_platforms:
            data["platforms"] = ["linux", "macos"]

            # YAML 파일 쓰기 (한글 보존, 정렬 유지)
            with open(rule_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

            print(f"✓ {rule_id}: platforms 업데이트 완료")
            return True
        else:
            print(f"- {rule_id}: 이미 macOS 포함됨 (skip)")
            return False

    except Exception as e:
        print(f"✗ {rule_file.name}: 오류 발생 - {e}")
        return False


def main():
    """메인 함수"""
    linux_rules_dir = Path("config/rules/linux")

    if not linux_rules_dir.exists():
        print(f"오류: {linux_rules_dir} 디렉토리가 존재하지 않습니다.")
        return

    print(f"Linux 규칙 디렉토리: {linux_rules_dir}")
    print(f"macOS 호환 규칙: {len(MACOS_COMPATIBLE_RULES)}개")
    print("-" * 50)

    updated_count = 0
    skipped_count = 0

    # U-01.yaml ~ U-73.yaml 파일 처리
    for rule_id in MACOS_COMPATIBLE_RULES:
        rule_file = linux_rules_dir / f"{rule_id}.yaml"

        if not rule_file.exists():
            print(f"✗ {rule_id}: 파일이 존재하지 않습니다.")
            continue

        if update_rule_platforms(rule_file):
            updated_count += 1
        else:
            skipped_count += 1

    print("-" * 50)
    print(f"완료: {updated_count}개 업데이트, {skipped_count}개 skip")


if __name__ == "__main__":
    main()
