#!/usr/bin/env python3
"""
이모티콘 제거 스크립트

위험 식별 이모티콘(🔴, 🟡, 🟢)을 제외한 모든 이모티콘을 마크다운 파일에서 제거합니다.
"""

import re
from pathlib import Path
from typing import Set

# 보존할 이모티콘 (위험 식별)
KEEP_EMOJIS: Set[str] = {'🔴', '🟡', '🟢'}

# 이모티콘 패턴 (유니코드 범위)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # 이모티콘 & 기호
    "\U00002600-\U000027BF"  # 기타 심볼
    "\U0001F1E0-\U0001F1FF"  # 국기
    "\U0001FA00-\U0001FAFF"  # 추가 이모티콘
    "\U00002300-\U000023FF"  # 기술 심볼
    "\U00002B50"              # 별 (⭐)
    "]+",
    flags=re.UNICODE
)


def remove_emojis(text: str) -> str:
    """텍스트에서 이모티콘 제거 (보존 목록 제외)"""
    def replace(match):
        emoji = match.group()
        # 한 글자씩 확인하여 보존할 이모티콘이면 유지
        result = []
        for char in emoji:
            if char in KEEP_EMOJIS:
                result.append(char)
            # else: 제거
        return ''.join(result)

    return EMOJI_PATTERN.sub(replace, text)


def process_markdown_file(file_path: Path) -> tuple[int, bool]:
    """마크다운 파일 처리

    Returns:
        (제거된 이모티콘 수, 변경 여부)
    """
    try:
        # UTF-8로 읽기
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # 이모티콘 제거
        cleaned_content = remove_emojis(content)

        # 변경 사항이 있으면 저장
        if cleaned_content != original_content:
            file_path.write_text(cleaned_content, encoding='utf-8')

            # 제거된 이모티콘 수 계산
            removed_count = len(original_content) - len(cleaned_content)
            return (removed_count, True)

        return (0, False)

    except Exception as e:
        print(f"오류 발생 ({file_path}): {e}")
        return (0, False)


def main():
    """메인 함수"""
    # 프로젝트 루트 경로
    root = Path(__file__).parent.parent

    # 마크다운 파일 찾기 (venv, .git, legacy 제외)
    exclude_dirs = {'venv', '.git', 'legacy', '__pycache__'}
    markdown_files = [
        f for f in root.rglob('*.md')
        if not any(ex in f.parts for ex in exclude_dirs)
    ]

    print(f"총 {len(markdown_files)}개 마크다운 파일 발견")
    print(f"보존할 이모티콘: {', '.join(KEEP_EMOJIS)}")
    print("-" * 60)

    # 파일별 처리
    total_removed = 0
    changed_files = 0

    for file_path in sorted(markdown_files):
        removed, changed = process_markdown_file(file_path)

        if changed:
            changed_files += 1
            total_removed += removed
            rel_path = file_path.relative_to(root)
            print(f"✓ {rel_path} (제거: {removed}자)")

    # 결과 출력
    print("-" * 60)
    print(f"완료: {changed_files}개 파일 수정, {total_removed}자 제거")


if __name__ == '__main__':
    main()
