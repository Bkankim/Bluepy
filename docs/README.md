# BluePy 2.0 - 문서 허브

**Last Updated**: 2025-10-20

BluePy 2.0 프로젝트의 모든 문서를 안내합니다.

---

##  문서 목록

| 문서 | 목적 | 대상 독자 | 링크 |
|------|------|----------|------|
| **프로젝트 계획서** | 프로젝트 전체 개요, 목표, 로드맵 요약 | 전체 관계자 | [../PROJECT_PLAN.md](../PROJECT_PLAN.md) |
| **아키텍처 문서** | 시스템 설계, 모듈 구조, 기술 스택 상세 | 개발자 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **개발 로드맵** | Phase별 상세 일정, 작업 항목, 마일스톤 | PM, 개발자 | [ROADMAP.md](ROADMAP.md) |
| **Legacy 분석** | 2017년 시스템 분석 및 마이그레이션 전략 | 개발자 | [LEGACY_ANALYSIS.md](LEGACY_ANALYSIS.md) |

---

##  문서 읽는 순서

### 처음 프로젝트를 접하는 경우
1. **README.md** (루트) - 프로젝트 개요
2. **PROJECT_PLAN.md** - 전체 계획 이해
3. **ARCHITECTURE.md** - 기술적 설계 파악

### 개발을 시작하는 경우
1. **ROADMAP.md** - 현재 Phase 확인
2. **ARCHITECTURE.md** - 구현할 모듈 구조 확인
3. **LEGACY_ANALYSIS.md** - 재사용 가능 코드 파악

### 문서를 업데이트하는 경우
- 각 문서 상단에 `Last Updated: YYYY-MM-DD` 기입
- 주요 변경사항은 Git commit 메시지에 기록
- 문서 간 링크가 깨지지 않도록 주의

---

##  문서 작성 원칙

### 명확성
- 전문 용어는 첫 사용 시 설명
- 코드 예시 포함
- 다이어그램 활용

### 일관성
- 동일한 용어 사용 (Scanner, Analyzer 등)
- 문서 형식 통일 (Markdown 스타일)

### 최신성
- 코드 변경 시 문서도 함께 업데이트
- Last Updated 날짜 갱신
- 더 이상 유효하지 않은 내용은 삭제

---

##  외부 참조

- **KISA 취약점 가이드**: https://www.kisa.or.kr
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks/
- **PySide6 문서**: https://doc.qt.io/qtforpython/
- **AsyncSSH 문서**: https://asyncssh.readthedocs.io/

---

**문서에 대한 피드백이나 개선 제안은 Issues에 남겨주세요.**