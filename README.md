# BluePy 2.0

> 비전공자도 쉽게 사용하는 멀티플랫폼 인프라 보안 점검 및 자동 수정 도구

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()

---

## 📖 프로젝트 개요

**BluePy 2.0**은 Linux, macOS, Windows 서버의 보안 취약점을 자동으로 점검하고 원클릭으로 수정할 수 있는 GUI 기반 보안 관리 플랫폼입니다.

2017년 Legacy 시스템(CLI 전문가용)을 현대화하여, **중소기업과 스타트업**도 전문 보안 인력 없이 인프라 보안을 관리할 수 있도록 재구성했습니다.

### 한 문장 요약
*"버튼 클릭만으로 리눅스/맥OS/윈도우 서버의 보안을 진단하고 자동으로 수정하는 도구"*

---

## ✨ 주요 기능

### 🌐 멀티플랫폼 지원
- **Linux** (73개 점검 항목) ✅ - KISA 기준 완전 준수
- **macOS** (50개 점검 항목) ✅ - SIP, Gatekeeper, FileVault 등 (Phase 2 완료)
- **Windows** (완료, 50/50개 항목, 100%) ✅ - 레지스트리, 서비스, 패치, 로깅

### ⚡ 원클릭 자동 수정 (Phase 3-4 완료)
- 취약점 자동 수정 ✅ - Windows 30개 + macOS 5개 + Linux 10개 규칙 지원
- 안전한 백업 + 롤백 ✅ - SHA256 체크섬 (Linux/macOS), reg export/import (Windows)
- Dry-run 모드 ✅ - 실제 실행 전 시뮬레이션
- GUI 통합 ✅ - 미리보기, 배치 수정 (commit 78bb83d)
- Linux Remediation ✅ - 완료 (10개 규칙: chmod 6개, PAM 3개, sed 1개)
- Windows Remediation ✅ - MVP 완료 (30개 레지스트리 규칙: W-11~W-30, W-41~W-50)

### 🖥️ 비전공자 친화 GUI
- PySide6 기반 네이티브 GUI
- 직관적인 대시보드 (점수, 차트)
- 색상 코드 (🔴 위험, 🟡 경고, 🟢 안전)
- 내장 교육 콘텐츠 (왜 위험한지, 어떻게 고치는지)

### 📊 이력 관리 및 분석 (Phase 5 부분 완료)
- 과거 점검 결과 저장 ✅
- 트렌드 분석 (개선/악화 추세) ✅ - PyQtGraph 차트
- History View ✅ - QTableWidget + 트렌드 차트 (commit 4ceb74c)
- 다크 모드 지원 ✅ - VSCode 색상 팔레트 (commit ca08e0c)
- PDF/Excel/HTML 보고서 생성 ✅ - Excel 완료 (commit b2cd6cc)

---

## 🚀 빠른 시작

### 요구사항
- Python 3.12 이상
- Linux, macOS, 또는 Windows 10+
- SSH 접근 권한 (점검 대상 서버)

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/bluepy.git
cd bluepy

# 가상환경 생성
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# GUI 실행
python -m src.gui.app

# CLI 실행 (고급 사용자)
python -m src.cli.commands scan --server myserver.com
```

---

## 📁 프로젝트 구조

```
bluepy/
├── src/                     # 소스 코드
│   ├── core/               # 핵심 비즈니스 로직
│   │   ├── scanner/        # 스캔 엔진 (Linux/macOS/Windows)
│   │   ├── analyzer/       # 분석 엔진
│   │   └── remediation/    # 자동 수정 엔진
│   ├── gui/                # PySide6 GUI
│   ├── infrastructure/     # DB, 네트워크, 보고서
│   └── utils/              # 공통 유틸리티
│
├── config/                  # 설정 파일
│   └── rules/              # 점검 규칙 (YAML)
│       ├── linux/          # Linux 73개 규칙 ✅
│       ├── macos/          # macOS 10개 전용 + 40개 공유 ✅
│       └── windows/        # Windows 50개 규칙 ✅
│
├── data/                    # 데이터 저장소
│   ├── databases/          # SQLite
│   ├── reports/            # 생성된 보고서
│   └── backups/            # 백업 파일
│
├── tests/                   # 테스트 코드
├── docs/                    # 문서
│   ├── PROJECT_PLAN.md     # 프로젝트 계획서
│   ├── ARCHITECTURE.md     # 아키텍처 상세
│   └── ROADMAP.md          # 개발 로드맵
│
└── legacy/                  # 2017년 Legacy 코드 (참고용)
```

---

## 🗓️ 개발 로드맵

| Phase | 기간 | 주요 기능 | 상태 |
|-------|------|----------|------|
| **Phase 1** | Week 1-4 | Linux MVP (Scanner, Analyzer, GUI, Excel) | ✅ 완료 |
| **Phase 1 기술 부채** | 2일 | 테스트 271/272 통과, 커버리지 56% | ✅ 완료 |
| **Phase 1.5** | Day 1-3 | Testing Infrastructure | ✅ 완료 (커버리지 65% 달성) |
| **Phase 2** | Day 1-5 | macOS 지원 (50개 규칙, UnixScanner 추상화) | ✅ 완료 |
| **Phase 3** | Week 7-8 | Remediation 엔진 + GUI 통합 (macOS 완성) | ✅ 완료 |
| **테스트 강화** | 2일 | Remediation/Database/Repository 테스트 | ✅ 완료 (커버리지 63%) |
| **Linux Remediation** | 2일 | Linux 자동 수정 10개 규칙 (Tier 1+2) | ✅ 완료 |
| **Phase 4** | 3주 | Windows 지원 (50/50개 규칙) | ✅ 완료 (100%) |
| **Phase 5** | 2주 | 고급 기능 (대시보드, 이력, 다크 모드) | 🔄 진행 중 (2/3 완료) |

**진행률**: **98% 완료 (약 11.5주 작업)**

**주요 성과**:
- 테스트 354개 통과 (100% 통과율)
- 커버리지 63% (핵심 모듈 90-100%)
- GUI 완성 (서버 관리, 스캔, 결과, 보고서, 자동 수정, 이력, 테마)
- Linux Remediation 완성 (10개 규칙: chmod 6개, PAM 3개, sed 1개)
- macOS Remediation 완성 (5개 규칙)
- Phase 5 Quick Wins 완료 (다크 모드, History View)
- Windows 50개 규칙 완성 (W-01~W-50, 100%) ✅
  * Week 1: 계정/서비스 관리 10개 (commit 3735972)
  * Week 2 Day 1: 레지스트리 10개 W-11~W-20 (commit 1bcef01)
  * Week 2 Day 2: 레지스트리 10개 W-21~W-30 (commit dff93ae)
  * Week 2 Day 3: 서비스 관리 10개 W-31~W-40 (commit 2131477)
  * Week 2 Day 4: 패치/로깅 10개 W-41~W-50 (100% 달성!)
- 총 26개 Git 커밋

자세한 내용은 [docs/ROADMAP.md](docs/ROADMAP.md) 참조

---

## 📚 문서

| 문서 | 설명 |
|------|------|
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | 프로젝트 전체 계획서 (비전, 목표, 기술 스택) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 시스템 아키텍처 상세 (Clean Architecture) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 개발 로드맵 (Phase별 상세 일정) |
| [docs/LEGACY_ANALYSIS.md](docs/LEGACY_ANALYSIS.md) | 2017년 시스템 분석 및 마이그레이션 전략 |

---

## 🏗️ 기술 스택

### 핵심 기술
- **언어**: Python 3.12+
- **GUI**: PySide6 (Qt)
- **데이터베이스**: SQLite
- **통신**: AsyncSSH, PyWinRM
- **보고서**: openpyxl, ReportLab, Jinja2

### 아키텍처
- **패턴**: Clean Architecture (Hexagonal)
- **원칙**: SOLID, DRY, KISS
- **테스트**: pytest (커버리지 60%+)

---

## 🤝 기여 방법

현재 프로젝트는 **개발 초기 단계**입니다.

기여를 원하시면:
1. 이슈를 생성하여 논의
2. Fork & Pull Request
3. 테스트 커버리지 유지 (60%+)
4. 코드 스타일 준수 (black, ruff)

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🔗 관련 링크

- **2017년 Legacy 프로젝트**: `legacy/infra/`
- **KISA 취약점 가이드**: https://www.kisa.or.kr
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks/

---

## 📞 문의

프로젝트 관련 문의는 Issues에 남겨주세요.

---

**BluePy 2.0** - Making infrastructure security accessible to everyone.