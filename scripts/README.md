# Scripts Directory

BluePy 2.0 유틸리티 스크립트

---

##  스크립트 목록

| 스크립트 | 용도 | 상태 |
|----------|------|------|
| `migrate_legacy.py` | 2017년 Legacy 코드 마이그레이션 |  개발 예정 |
| `import_rules.py` | YAML 규칙 파일 가져오기/검증 |  개발 예정 |
| `build.py` | PyInstaller 빌드 자동화 |  개발 예정 |
| `setup_dev.sh` | 개발 환경 설정 (가상환경, 의존성) |  개발 예정 |

---

##  스크립트 설명

### migrate_legacy.py
**목적**: Legacy Python 2 코드를 Python 3로 마이그레이션

**사용법**:
```bash
python scripts/migrate_legacy.py --input legacy/infra/linux/자동점검\ 코드/점검자료분석/Linux_Check_2.py --output config/rules/linux/
```

**주요 기능**:
- Python 2 → 3 문법 변환
- `_1SCRIPT` ~ `_73SCRIPT` → YAML 규칙 추출
- validator 함수 자동 생성

---

### import_rules.py
**목적**: 외부 YAML 규칙 파일 가져오기 및 검증

**사용법**:
```bash
# 규칙 검증
python scripts/import_rules.py --validate config/rules/linux/

# 외부 규칙 가져오기
python scripts/import_rules.py --import custom_rules.yaml --output config/rules/linux/
```

**검증 항목**:
- YAML 문법 오류
- 필수 필드 (id, name, commands, validator)
- 중복 ID 확인

---

### build.py
**목적**: PyInstaller로 실행 파일 빌드

**사용법**:
```bash
# 기본 빌드
python scripts/build.py

# 플랫폼 지정
python scripts/build.py --platform linux
python scripts/build.py --platform macos
python scripts/build.py --platform windows
```

**결과물**:
- `dist/bluepy` (Linux/macOS)
- `dist/bluepy.exe` (Windows)
- `dist/bluepy.app` (macOS App Bundle)

---

### setup_dev.sh
**목적**: 개발 환경 자동 설정

**사용법**:
```bash
bash scripts/setup_dev.sh
```

**수행 작업**:
1. Python 3.12 설치 확인
2. 가상환경 생성 (venv/)
3. 의존성 설치 (requirements.txt)
4. pre-commit hooks 설정
5. 테스트 환경 검증

---

##  스크립트 작성 가이드

### 템플릿
```python
#!/usr/bin/env python3
"""
Script Name: example_script.py
Purpose: 간단한 설명
Usage: python scripts/example_script.py --arg value
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="스크립트 설명")
    parser.add_argument("--arg", help="인자 설명")
    args = parser.parse_args()

    # 로직
    print(f"Argument: {args.arg}")

if __name__ == "__main__":
    main()
```

### 작성 원칙
1. **Docstring 필수**: 용도, 사용법 명시
2. **argparse 사용**: 명령줄 인자 처리
3. **에러 처리**: try-except로 예외 처리
4. **로깅**: print 대신 logging 사용 권장
5. **테스트 가능**: 함수로 분리하여 테스트 가능하게

---

##  공통 실행 패턴

### 건식 실행 (Dry-run)
대부분의 스크립트는 `--dry-run` 옵션 지원:
```bash
python scripts/migrate_legacy.py --dry-run
```

### 디버그 모드
```bash
python scripts/build.py --verbose
```

---

**스크립트를 추가하면 이 README도 업데이트해주세요!**