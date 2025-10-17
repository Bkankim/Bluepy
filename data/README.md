# Data Directory

BluePy 2.0 데이터 저장소

## 구조

```
data/
├── databases/      # SQLite 데이터베이스 파일
│   └── bluepy.db  # 메인 DB (서버, 스캔 이력 등)
│
├── reports/        # 생성된 보고서 파일
│   ├── *.xlsx     # Excel 보고서
│   ├── *.pdf      # PDF 보고서
│   └── *.html     # HTML 보고서
│
└── backups/        # 자동 수정 시 백업 파일
    └── backup_YYYYMMDD_HHMMSS/
```

## 주의사항

- 이 디렉토리의 모든 내용은 Git에 추적되지 않음 (.gitignore)
- 데이터베이스는 자동으로 생성됨
- 백업 파일은 30일 후 자동 삭제 (설정 가능)

## 데이터베이스 스키마

자세한 내용은 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md#9-데이터베이스-설계) 참조