# Source Code Directory

BluePy 2.0 소스 코드

## 구조

```
src/
├── core/               # 핵심 비즈니스 로직
│   ├── domain/        # 도메인 모델 (CheckItem, ScanResult 등)
│   ├── scanner/       # 스캔 엔진 (Linux, macOS, Windows)
│   ├── analyzer/      # 분석 엔진 (파싱, 위험도 계산)
│   └── remediation/   # 자동 수정 엔진
│
├── application/        # Use Cases (비즈니스 로직 조율)
│   ├── scan_service.py
│   ├── remediation_service.py
│   └── report_service.py
│
├── gui/                # PySide6 GUI
│   ├── views/         # 화면 (Dashboard, Scan, Result 등)
│   ├── widgets/       # 재사용 위젯
│   ├── dialogs/       # 대화상자
│   └── resources/     # 아이콘, 스타일시트
│
├── infrastructure/     # 인프라 계층
│   ├── database/      # SQLite ORM
│   ├── network/       # SSH, WinRM 클라이언트
│   └── reporting/     # PDF, Excel, HTML 생성
│
└── utils/              # 공통 유틸리티
    ├── logger.py
    ├── config.py
    └── crypto.py
```

## 설계 원칙

- **Clean Architecture**: 계층 분리, 의존성 역전
- **SOLID 원칙**: 단일 책임, 개방-폐쇄 등
- **테스트 가능성**: 모든 모듈은 독립적으로 테스트 가능

## 개발 가이드

자세한 내용은 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) 참조