# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# AI Dev Tasks
Use these files when I request structured feature development using PRDs:
/ai-dev-tasks/create-prd.md
/ai-dev-tasks/generate-tasks.md
/ai-dev-tasks/process-task-list.md

# agents 사용 지침
- **반드시** 병렬 수행에 유리한 작업을 스스로 판단하고 적절한 agents를 배정해서 사용.

# 철칙
- **반드시** 📋 ❌ ✅ 🔴 📂 와 같거나 유사한 이모티콘은 **절대적으로** 작성 금지.

## AI Dev Tasks 사용법
1. **PRD 생성**: `Use @create-prd.md` + 기능 설명
   - 결과: `tasks/prd-[feature-name].md`
2. **Task List 생성**: `@prd-[feature-name].md와 @generate-tasks.md 사용`
   - 결과: `tasks/tasks-prd-[feature-name].md`
3. **구현 진행**: `@process-task-list.md 사용`
   - Task 단위로 단계별 구현 및 검증

## BluePy 2.0 프로젝트

### 프로젝트 개요
멀티플랫폼(Linux, macOS, Windows) 인프라 보안 점검 및 자동 수정 도구.
2017년 Legacy 시스템을 Python 3.12, Clean Architecture로 재구성.

**참고 문서:**
- `PROJECT_PLAN.md` - 전체 프로젝트 계획 및 로드맵
- `docs/ARCHITECTURE.md` - Clean Architecture 설계
- `docs/ROADMAP.md` - Phase별 상세 개발 일정
- `docs/LEGACY_ANALYSIS.md` - 2017년 시스템 분석

### 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 테스트 실행
```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/unit

# 통합 테스트만
pytest tests/integration

# 커버리지 리포트 (목표 60%+)
pytest --cov=src --cov-report=html
# 결과: htmlcov/index.html

# 특정 테스트만 실행
pytest tests/unit/test_scanner.py::test_connect
```

### GUI 실행
```bash
# GUI 애플리케이션 실행
python -m src.gui.app

# CLI 모드 (고급 사용자)
python -m src.cli.commands scan --server myserver.com
```

### 프로젝트 아키텍처

**Clean Architecture (Hexagonal) 레이어:**
- `src/core/domain/` - 도메인 모델 (Entity, Value Object)
- `src/core/scanner/` - 스캔 엔진 (Linux/macOS/Windows Scanner)
- `src/core/analyzer/` - 분석 엔진 (결과 파싱, 평가)
- `src/core/remediation/` - 자동 수정 엔진 (백업, 실행, 롤백)
- `src/application/` - 유스케이스 (비즈니스 로직 조율)
- `src/infrastructure/` - 외부 어댑터 (DB, Network, Reporting)
- `src/gui/` - PySide6 GUI (Presentation Layer)

**핵심 패턴:**
- Factory Pattern: Scanner 생성 (플랫폼별 분기)
- Repository Pattern: DB 접근 추상화
- YAML 기반 규칙 시스템: 확장 가능한 점검 항목

**규칙 파일 구조:**
```yaml
# config/rules/linux/U-01.yaml
id: U-01
name: root 원격 로그인 제한
severity: high
check:
  commands:
    - cat /etc/pam.d/login | grep pam_securetty
validator: validators.linux.check_pam_securetty
remediation:
  auto: true
  backup_files:
    - /etc/pam.d/login
  commands:
    - echo "auth required pam_securetty.so" >> /etc/pam.d/login
```

### Legacy 코드 참고
- `legacy/infra/linux/자동점검 코드/점검자료분석/Linux_Check_2.py` - 73개 점검 함수 (`_1SCRIPT` ~ `_73SCRIPT`)
- Python 2 코드이므로 직접 실행 불가, 로직만 참고

### 스크립트 (개발 예정)
- `scripts/migrate_legacy.py` - Legacy Python 2 → 3 변환
- `scripts/import_rules.py` - YAML 규칙 검증/가져오기
- `scripts/build.py` - PyInstaller 빌드 자동화
- `scripts/setup_dev.sh` - 개발 환경 자동 설정

## 프로젝트 필수 지침

### .md 수정 지침
- 작업을 마칠 때마다, **우선적으로 모든 문서 최신화**를 고려해야 함.

### git 규칙
- 모든 작업을 마칠 때마다, @.gitignore 를 최신화하고, 항상 해당 github를 최신화 해야함 (백업 개념에서)
- 모든 git 내용에 너(Claude)의 흔적이 존재하면 안됨.

### MCP 사용 기준
- sequential-thinking : 깊은 사고력이 요구되는 작업이나, 복잡한 과정을 수행할 때 본인 판단하에 자유롭게 사용.
- context7 : 의존성 문제나, 새로운 패키지의 다운로드가 필요할 시 반드시 사용해서 해결.

### 프롬프트 언어
- 항상 한글로 대답하고, 생각하는 부분도 한글로 표기할 것.

### 코드 작성 지침
- 모든 Class, def 위에는 간단하게 기능을 설명하는 주석을 달아줄 것.
- **모듈 사용을 기본**으로 하여 호환성 / 재사용성 / 유지보수성 의 원칙을 꼭 지킬 것.