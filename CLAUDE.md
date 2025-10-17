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

**현재 PRD**: `tasks/prd-dialogue-summarization-performance-improvement.md`

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