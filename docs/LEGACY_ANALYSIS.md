# BluePy - Legacy 시스템 분석 (2017년)

**작성일**: 2025-10-17
**분석 대상**: infra/ 폴더 (2017년 프로젝트)
**목적**: 재사용 가능 항목 파악 및 마이그레이션 전략 수립

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [아키텍처 분석](#2-아키텍처-분석)
3. [점검 항목 분석](#3-점검-항목-분석-73개)
4. [문제점 및 한계](#4-문제점-및-한계)
5. [재사용 가능 항목](#5-재사용-가능-항목)
6. [마이그레이션 전략](#6-마이그레이션-전략)

---

## 1. 시스템 개요

### 1.1 프로젝트 정보

| 항목 | 내용 |
|------|------|
| **개발 시기** | 2017년 10월 |
| **개발 언어** | Python 2, C++ (Qt) |
| **플랫폼** | Linux만 지원 |
| **점검 항목** | KISA 기준 73개 |
| **통신** | 소켓 (Python2) |
| **GUI** | Qt 5.7.2 (C++) |
| **보고서** | Excel (xlsxwriter) |

### 1.2 파일 구조

```
infra/
├── linux/
│   ├── 소켓통신/
│   │   ├── 관리자/
│   │   │   └── Script_For_Manager.txt
│   │   └── 서버/
│   │       └── srv.py                # Python2 소켓 서버
│   └── 자동점검 코드/
│       ├── 점검자료조사/
│       │   └── Linux_Check_1.txt     # 73개 bash 명령어
│       ├── 점검자료분석/
│       │   └── Linux_Check_2.py      # 결과 분석 (Python2)
│       ├── 점검자료보고서작성/
│       │   └── Linux_Check_3.py      # Excel 보고서 (xlsxwriter)
│       └── README.txt
│
├── window/
│   ├── 소켓통신/
│   │   ├── 관리자/
│   │   │   └── Script_For_Manager_window.py  # 클라이언트
│   │   └── 서버/
│   │       └── window_remote.py              # 파일 수신
│   └── 자동점검 프로그램/
│       ├── EXE파일/
│       └── POWER SHELL CODE/
│
├── bluepy/                           # Qt C++ GUI
│   ├── BluePY.pro
│   ├── main.cpp
│   ├── mainwindow.cpp/h/ui
│   ├── login.cpp/h/ui
│   ├── server.cpp/h/ui
│   ├── chart.cpp/h/ui
│   ├── check.cpp/h/ui
│   ├── information.cpp/h/ui
│   ├── setting.cpp/h/ui
│   └── searching.cpp/h/ui
│
└── python/
    └── setup.py                       # cx_Freeze 설정
```

---

## 2. 아키텍처 분석

### 2.1 전체 워크플로우

```
┌──────────────────┐
│ Linux 서버       │
│ (점검 대상)      │
└────────┬─────────┘
         │
         │ SSH (수동)
         ▼
┌──────────────────┐
│ 점검 스크립트    │
│ Linux_Check_1.txt│  ← 73개 bash 명령어
└────────┬─────────┘
         │
         │ 명령어 실행
         ▼
┌──────────────────┐
│ report.txt       │  ← 원시 결과 파일
│ report_error.txt │
└────────┬─────────┘
         │
         │ 분석
         ▼
┌──────────────────┐
│ Linux_Check_2.py │  ← _1SCRIPT ~ _73SCRIPT
│ (Python2)        │     함수 73개
└────────┬─────────┘
         │
         │ 분석 결과
         ▼
┌──────────────────┐
│report_excel.txt  │  ← 0/1/2 숫자 코드
└────────┬─────────┘
         │
         │ 보고서 생성
         ▼
┌──────────────────┐
│ Linux_Check_3.py │  ← xlsxwriter
│ (Python2)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│Report_Linux_     │
│Server.xlsx       │  ← 최종 보고서
└──────────────────┘
```

### 2.2 통신 구조

```
┌─────────────────┐         ┌─────────────────┐
│ Linux 서버      │         │ Windows 클라이언│
│ srv.py          │ ◄───── │ window_remote.py│
│ (포트 8282)     │  소켓   │                 │
└─────────────────┘         └─────────────────┘
        │                            │
        │ 1. 연결 수락                │
        │ 2. sh run.sh 실행          │
        │ 3. report.txt 전송         │
        │ 4. 연결 종료               │
        └────────────────────────────┘
```

**srv.py 핵심 코드** (Python2):
```python
s = socket(AF_INET, SOCK_STREAM)
s.bind(('192.168.0.16', 8282))  # 하드코딩!
s.listen(1)

while True:
    conn, addr = s.accept()
    os.system("sh run.sh")  # 점검 실행
    data = _FOPEN()  # report.txt 읽기
    conn.send(data)  # 전송
    conn.send(b'END DATA')
```

### 2.3 GUI 구조 (Qt C++)

```
MainWindow
├── Login (로그인)
├── Server (서버 설정)
│   ├── IP 입력 (4개 필드)
│   ├── OS 선택 (Linux/Windows 라디오 버튼)
│   └── 연결 버튼
├── Chart (차트 표시 - 미완성)
├── Check (점검 항목 트리)
├── Information (정보)
├── Setting (설정)
└── Searching (검색 - 미완성)
```

---

## 3. 점검 항목 분석 (73개)

### 3.1 카테고리별 분류

| 카테고리 | 항목 수 | 코드 번호 | 설명 |
|----------|---------|-----------|------|
| **계정 관리** | 15 | U-01 ~ U-15 | root 로그인, 패스워드 정책, 계정 잠금 등 |
| **파일/디렉터리** | 20 | U-16 ~ U-35 | 파일 권한, SUID, 환경 변수 등 |
| **서비스 관리** | 35 | U-36 ~ U-70 | 불필요한 서비스, 포트, 웹 서버 설정 등 |
| **패치 관리** | 1 | U-71 | 패치 정책 수립 (수동 확인) |
| **로그 관리** | 2 | U-72 ~ U-73 | 로그 검토, 정책 (수동 확인) |

### 3.2 위험도 분류

| 위험도 | 항목 수 | 예시 |
|--------|---------|------|
| **HIGH** | 28 | U-01 (root 원격 로그인), U-18 (passwd 권한) |
| **MEDIUM** | 32 | U-05 (UID 중복), U-32 (umask 설정) |
| **LOW** | 13 | U-06 (wheel 그룹), U-30 (hosts 파일) |

### 3.3 주요 점검 항목 예시

**U-01: root 원격 로그인 제한** (HIGH)
```bash
# 점검 명령어
cat /etc/pam.d/login | grep pam_securetty
cat /etc/securetty | grep pts
```
```python
# 분석 로직 (_1SCRIPT)
def _1SCRIPT(data):
    data = _SPLIT(data)
    r1=['auth','required','/lib/security/pam_securetty.so']
    for i in data[0].split('\n'):
        if _NOSPACE(i.split(' '))==r1:
            for i in data[1].split('\n'):
                if i[0:2] == 'pts':
                    break
            else:
                _SETOK()
            break
    else:
        _SETBAD()
    _SETHIGH()
```

**U-18: /etc/passwd 파일 권한** (HIGH)
```bash
# 점검 명령어
ls -l /etc/passwd
```
```python
# 분석 로직
def _18SCRIPT(data):
    r = str(_NOSPACE(data.split('\n')))
    if r[1:3]=='rw' and r[5:7] == '--' and r[8:10] == '--' and r[14:19] == 'root':
        _SETOK()
    else:
        _SETBAD()
    _SETHIGH()
```

**U-42: NFS 서비스 비활성화** (HIGH)
```bash
# 점검 명령어
ps -ef | grep nfsd
```
```python
# 분석 로직
def _42SCRIPT(data):
    data=_NOSPACE(data.split('\n'))
    data=_DELGREP(data)  # grep 자신은 제외
    if data==[]:
        _SETOK()
    else:
        _SETBAD()
```

### 3.4 점검 결과 코드

```python
# Linux_Check_2.py 결과 코드
excel_data = []  # 0=안전, 1=취약, 2=보류
excel_data_dg = []  # 0=LOW, 1=MID, 2=HIGH
excel_data_hd = []  # 추가 데이터 (HOLD 항목용)

def _SETOK():
    excel_data.append("0")  # 안전

def _SETBAD():
    excel_data.append("1")  # 취약

def _SETHOLD():
    excel_data.append("2")  # 수동 확인 필요
```

---

## 4. 문제점 및 한계

### 4.1 치명적 기술 부채

#### Python 2 사용
```python
# 문제점
print "hello"  # Python 3에서는 오류
except:        # 모든 예외 무시 (위험)
u"한글"        # 인코딩 문제
```
- **영향**: 보안 업데이트 없음 (2020년 EOL)
- **해결**: Python 3.12+ 전면 재작성 필요

#### 하드코딩 73개 함수
```python
# 새 점검 항목 추가 시
def _74SCRIPT(data):  # 수동 추가
    # ... 로직 작성
    pass

# 호출 부분도 수정
for i in range(1, 74):  # 74로 변경
    tg = "_"+str(i)+"SCRIPT(report_data["+str(i-1)+"])"
    eval(tg)  # eval 사용 (보안 위험)
```
- **영향**: 확장성 제로, 유지보수 어려움
- **해결**: YAML 규칙 기반 시스템

#### 인코딩 문제
```bash
# README.txt 내용이 깨짐
���� ���� : QT_5_7_2
```
- **영향**: 한글 보고서 읽기 불가
- **해결**: UTF-8 통일

### 4.2 확장성 한계

| 한계 | 현재 상태 | 필요 작업 |
|------|----------|----------|
| **플랫폼** | Linux만 | macOS, Windows 추가 |
| **점검 항목** | 73개 고정 | 동적 추가 가능하게 |
| **서버 수** | 1대씩 | 다중 서버 관리 |
| **보고서** | Excel만 | PDF, HTML 추가 |
| **자동화** | 없음 | 스케줄러, 자동 수정 |

### 4.3 사용성 문제

**CLI 전문가 전용**:
```bash
# 사용자가 직접 실행해야 함
sh Linux_Check_1.txt  # 점검 실행
python3 Linux_Check_2.py  # 분석
python3 Linux_Check_3.py  # 보고서
```

**결과 이해 어려움**:
```
0=GOOD, 1=BAD, 2=HOLD
010112020...  # 숫자 나열만
```

**수동 수정**:
- 취약점 발견 후 직접 수정 필요
- 자동화 없음
- 롤백 기능 없음

### 4.4 보안 문제

**인증 없는 통신**:
```python
# srv.py
s.bind(('192.168.0.16', 8282))
conn, addr = s.accept()  # 누구든 연결 가능
```

**평문 전송**:
```python
conn.send(data)  # 암호화 없음
```

**root 권한**:
```bash
# 많은 명령어가 root 필요
ls -l /etc/shadow  # root만 가능
```

---

## 5. 재사용 가능 항목

### 5.1 점검 로직 (100% 재사용)

**73개 점검 항목의 비즈니스 로직은 그대로 사용 가능**:
- U-01 ~ U-73의 검증 로직
- 명령어 목록
- 위험도 분류

**마이그레이션 방법**:
1. Python 2 → 3 문법 변환
2. 하드코딩된 함수 → YAML 규칙 파일
3. `eval()` → 구조화된 실행

### 5.2 점검 명령어 (95% 재사용)

**Linux_Check_1.txt 명령어는 대부분 그대로 사용**:
```bash
# 예시 (U-01)
cat /etc/pam.d/login | grep pam_securetty
cat /etc/securetty | grep pts
# → YAML commands 섹션에 복사
```

**변경 필요 항목**:
- `>>report.txt 2>>report_error.txt` 제거 (리다이렉션 불필요)
- 일부 경로 업데이트 (최신 Linux 배포판)

### 5.3 보고서 레이아웃 (80% 재사용)

**Linux_Check_3.py의 Excel 레이아웃**:
- 분류, 코드, 수준, 상태 (4컬럼)
- 계정/파일/서비스/패치/로그 구분
- 색상 코드 (초록/빨강)

**개선 사항**:
- 차트 추가 (파이 차트, 트렌드)
- 경영진용 요약 페이지
- PDF 버전

### 5.4 재사용 불가 항목

| 항목 | 이유 | 대체 방안 |
|------|------|----------|
| **소켓 통신** | 하드코딩, 인증 없음 | SSH/WinRM |
| **Qt C++ GUI** | 오래된 버전, 유지보수 어려움 | PySide6 |
| **Python 2 코드** | EOL, 보안 위험 | Python 3.12+ |
| **eval() 사용** | 보안 위험 | 구조화된 실행 |

---

## 6. 마이그레이션 전략

### 6.1 단계별 접근

#### Phase 1: 점검 로직 마이그레이션
```python
# 기존 (Python 2)
def _1SCRIPT(data):
    data = _SPLIT(data)
    # ... 로직

# 신규 (YAML + Python 3)
# config/rules/linux/account.yaml
- id: U-01
  commands:
    - cat /etc/pam.d/login | grep pam_securetty
  validator: check_root_remote_login

# src/core/analyzer/validator.py
def check_root_remote_login(outputs):
    # 기존 로직 변환
    return has_pam and not has_pts
```

#### Phase 2: 명령어 추출
```bash
# 스크립트로 자동 추출
cat Linux_Check_1.txt | grep -v "^#" | grep -v "^$" > commands.txt
# → YAML 변환 스크립트 실행
```

#### Phase 3: GUI 재작성
```python
# Qt C++ → PySide6
# main.cpp → src/gui/app.py
# mainwindow.cpp → src/gui/main_window.py
```

### 6.2 마이그레이션 스크립트

```python
# scripts/migrate_legacy.py
import re

def convert_script_to_yaml(script_func, script_id):
    """_1SCRIPT 함수를 YAML로 변환"""
    # 정규식으로 패턴 추출
    # 예: r1=['auth','required','/lib/security/pam_securetty.so']
    # → validator 함수 생성

def extract_commands(check_file):
    """Linux_Check_1.txt에서 명령어 추출"""
    with open(check_file) as f:
        commands = []
        for line in f:
            if line.startswith("cat ") or line.startswith("grep "):
                commands.append(line.strip())
    return commands
```

### 6.3 검증 전략

**이중 검증**:
1. 기존 시스템으로 점검 실행
2. 새 시스템으로 점검 실행
3. 결과 비교 (100% 일치해야 함)

```python
# tests/integration/test_migration.py
def test_u01_migration():
    # Legacy 결과
    legacy_result = run_legacy_check("U-01")

    # 새 시스템 결과
    new_result = run_new_check("U-01")

    assert legacy_result == new_result
```

### 6.4 마이그레이션 타임라인

| 작업 | 예상 시간 | 우선순위 |
|------|----------|----------|
| 명령어 추출 | 1일 | 높음 |
| YAML 변환 (10개) | 2일 | 높음 |
| validator 함수 (10개) | 2일 | 높음 |
| 검증 테스트 | 1일 | 높음 |
| 나머지 63개 | 5일 | 중간 |
| 문서화 | 1일 | 중간 |

---

## 7. 결론

### 7.1 핵심 요약

**Legacy 시스템의 가치**:
- ✅ 73개 점검 항목 (KISA 기준)
- ✅ 검증된 로직 (실제 사용)
- ✅ 보고서 레이아웃

**재사용 전략**:
- 점검 로직: 100% 재사용 (Python 3 변환)
- 명령어: 95% 재사용
- GUI: 0% (PySide6 재작성)

**기대 효과**:
- 개발 시간 단축 (70% 로직 재사용)
- 검증된 규칙 활용
- 빠른 MVP 출시

### 7.2 추천 사항

1. **즉시 시작**: 명령어 추출 및 YAML 변환
2. **점진적 마이그레이션**: 10개씩 검증
3. **이중 검증**: 기존 vs 신규 결과 비교
4. **문서화**: 변환 과정 기록

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-10-17 | 1.0 | 초안 작성 | Claude |

---

**문서 끝**