# Tests Directory

BluePy 2.0 테스트 코드

---

## 📁 구조

```
tests/
├── unit/           # 단위 테스트 (개별 모듈)
│   ├── test_scanner.py
│   ├── test_analyzer.py
│   ├── test_remediation.py
│   └── ...
│
├── integration/    # 통합 테스트 (워크플로우)
│   ├── test_scan_workflow.py
│   ├── test_remediation_workflow.py
│   └── ...
│
└── fixtures/       # 테스트 데이터
    ├── sample_rules.yaml
    ├── mock_responses.json
    └── ...
```

---

## 🧪 테스트 종류

### 단위 테스트 (Unit Tests)
- **목적**: 개별 함수/클래스의 동작 검증
- **범위**: 외부 의존성 Mock 처리
- **예시**: Scanner.connect(), Analyzer.parse_result()

### 통합 테스트 (Integration Tests)
- **목적**: 모듈 간 상호작용 검증
- **범위**: 실제 SSH 연결 (Docker 테스트 환경)
- **예시**: 전체 스캔 워크플로우, 자동 수정 프로세스

---

## 🚀 실행 방법

### 전체 테스트 실행
```bash
pytest
```

### 특정 테스트만 실행
```bash
# 단위 테스트만
pytest tests/unit

# 통합 테스트만
pytest tests/integration

# 특정 파일
pytest tests/unit/test_scanner.py

# 특정 테스트 함수
pytest tests/unit/test_scanner.py::test_connect
```

### 커버리지 리포트
```bash
pytest --cov=src --cov-report=html
# 결과: htmlcov/index.html
```

---

## ✅ 테스트 목표

| 항목 | 목표 | 현재 |
|------|------|------|
| **커버리지** | 60% 이상 | TBD |
| **단위 테스트** | 모든 핵심 모듈 | TBD |
| **통합 테스트** | 주요 워크플로우 | TBD |

---

## 📝 테스트 작성 가이드

### 파일명 규칙
- `test_*.py` - pytest가 자동 인식
- 단위 테스트: `test_<module_name>.py`
- 통합 테스트: `test_<workflow_name>_workflow.py`

### 테스트 함수명
```python
def test_<function>_<scenario>_<expected_result>():
    # 예: test_connect_invalid_host_raises_error()
    pass
```

### AAA 패턴 사용
```python
def test_scan_success():
    # Arrange (준비)
    scanner = LinuxScanner(server_info)

    # Act (실행)
    result = scanner.scan()

    # Assert (검증)
    assert result.status == "success"
```

---

## 🔧 Fixtures

### conftest.py
공통 픽스처는 `tests/conftest.py`에 정의:
```python
@pytest.fixture
def sample_server():
    return {
        "host": "test.example.com",
        "username": "test",
        "password": "test123"
    }
```

---

## 🐳 테스트 환경

### Docker 테스트 환경
```bash
# Linux 테스트 컨테이너 실행
docker run -d --name test-linux ubuntu:22.04

# 테스트 실행
pytest tests/integration

# 정리
docker rm -f test-linux
```

---

## 📊 CI/CD

GitHub Actions에서 자동 실행:
- PR 생성 시
- main 브랜치 push 시
- 매일 자동 테스트

---

**테스트 작성은 코드 작성만큼 중요합니다!**