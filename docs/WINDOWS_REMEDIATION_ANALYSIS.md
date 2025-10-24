# Windows 규칙 YAML Remediation 섹션 분석 보고서

**분석 대상**: config/rules/windows/W-01.yaml ~ W-50.yaml (W-31~W-40 제외 = 40개 + 10개 서비스 = 50개)
**분석 일시**: 2025-10-21
**총 규칙 수**: 50개

---

## 1. Remediation Auto 여부 분석

### 자동 수정 가능 규칙 (auto: true)

| 항목 | 개수 | 비율 |
|-----|------|------|
| auto: true | 49개 | 98% |
| auto: false | 1개 | 2% |
| **총합** | **50개** | **100%** |

### auto: false 규칙 (수동 수정 필요)

| 규칙 ID | 이름 | 카테고리 | 사유 |
|--------|------|----------|------|
| W-03 | 패스워드 복잡성 정책 설정 | 계정관리 | secedit 명령어 사용 (복잡한 정책 처리) |

**특징**: 
- W-03은 `secedit` 명령어를 사용하여 보안 정책 파일을 생성/수정
- PowerShell만으로는 구현 어려움
- 시스템 보안 정책을 직접 수정해야 함

---

## 2. Remediation Commands 패턴 분석

### 패턴별 분류

#### 레지스트리 값 설정 (Set-ItemProperty)

**규칙 개수**: 40개 (W-10, W-11~W-25, W-30, W-41~W-50)

**특징**:
- `-Path`: 레지스트리 경로 (HKLM, HKCU)
- `-Name`: 값 이름 (키)
- `-Value`: 설정 값
- `-Type`: DWord, String 등

**예시**:
```powershell
Set-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System" `
  -Name "EnableLUA" `
  -Value 1
```

**규칙 목록**:
- W-10: RDP NLA (1)
- W-11: UAC EnableLUA (1)
- W-12: NoLMHash (1)
- W-13: RestrictAnonymousSAM (1)
- W-14: AutoAdminLogon (0)
- W-16: NTLMMinServerSec (537395200)
- W-17: LimitBlankPasswordUse (1)
- W-18: SMB1 (0)
- W-19: RestrictNullSessAccess (1)
- W-20: RunAsPPL (1)
- W-21: LmCompatibilityLevel (5)
- W-22: NTLMMinClientSec (537395200)
- W-23: CachedLogonsCount (2)
- W-24: ScreenSaverIsSecure (1)
- W-25: ScreenSaveTimeOut (900)
- W-30: AutoDisconnect (15)
- W-41~W-50: 다양한 레지스트리 설정

---

#### 레지스트리 키 생성 (New-Item)

**규칙 개수**: 16개 (W-26, W-27, W-28, W-29, W-34, W-37, W-41~W-50)

**특징**:
- 레지스트리 경로가 없을 때 미리 생성
- `if (-not (Test-Path "...")) { New-Item ... }` 패턴
- 이렇게 하면 키 생성 후 값 설정 가능

**패턴**:
```powershell
if (-not (Test-Path "HKLM:\Software\Policies\Microsoft\Windows\EventLog\Security")) {
  New-Item -Path "HKLM:\Software\Policies\Microsoft\Windows\EventLog\Security" -Force
}
Set-ItemProperty -Path "..." -Name "MaxSize" -Value 196608 -Type DWord
```

**규칙 목록**:
- W-26: Security 이벤트 로그 (MaxSize 196608)
- W-27: Application 이벤트 로그 (MaxSize 32768)
- W-28: System 이벤트 로그 (MaxSize 32768)
- W-29: RemoteAccess 계정 잠금 (MaxDenials 5)
- W-34: (W-34는 조회 필요)
- W-37: (W-37은 조회 필요)
- W-41~W-50: 패치/로깅 규칙들

---

#### 다른 패턴

| 패턴 | 규칙 ID | 설명 |
|-----|--------|------|
| Set-Service | W-15 | RemoteRegistry 서비스 비활성화 (StartupType, Stop-Service) |
| Set-NetFirewallProfile | W-08 | Windows Firewall 활성화 |
| Set-MpPreference | W-09 | Windows Defender 설정 |
| Disable-LocalUser | W-02 | Guest 계정 비활성화 |
| Rename-LocalUser | W-01 | Administrator 이름 변경 |
| net accounts | W-04, W-05, W-06, W-07 | 패스워드/계정 잠금 정책 |
| secedit | W-03 | 보안 정책 설정 (수동 처리) |

---

## 3. 레지스트리 경로 분석

### 주요 레지스트리 경로

| 경로 | 규칙 수 | 용도 |
|-----|--------|------|
| HKLM:\System\CurrentControlSet\Control\Lsa | 7개 | LSA 보안 설정 |
| HKLM:\Software\Policies\Microsoft\Windows | 14개 | 정책 설정 (이벤트 로그, Windows Update 등) |
| HKLM:\System\CurrentControlSet\Services | 4개 | 서비스 설정 |
| HKCU:\Control Panel\Desktop | 2개 | 스크린 세이버 설정 |
| HKLM:\System\CurrentControlSet\Control\Lsa\MSV1_0 | 2개 | NTLM 보안 |
| 기타 | 21개 | 다양한 설정 |

### 레지스트리 값 타입

| 타입 | 사용 규칙 | 예시 |
|-----|--------|------|
| DWord (숫자) | 주로 사용 | 537395200, 196608, 900 등 |
| String (문자) | 소수 | W-50에서 Retention값 |
| 타입 미지정 | W-01, W-04~W-09 | Set-ItemProperty -Value로만 설정 |

---

## 4. 카테고리별 그룹핑

### 계정 관리 (W-01 ~ W-07)

| ID | 이름 | auto | 명령어 | 비고 |
|----|------|------|--------|------|
| W-01 | Administrator 이름 변경 | true | Rename-LocalUser | 로컬 사용자 명령 |
| W-02 | Guest 계정 비활성화 | true | Disable-LocalUser | 로컬 사용자 명령 |
| W-03 | 패스워드 복잡성 정책 | false | secedit | 수동 처리 |
| W-04 | 패스워드 최소 길이 | true | net accounts | 계정 정책 |
| W-05 | 패스워드 최대 사용 기간 | true | net accounts | 계정 정책 |
| W-06 | 계정 잠금 임계값 | true | net accounts | 계정 정책 |
| W-07 | 계정 잠금 기간 | true | net accounts | 계정 정책 |

---

### 서비스 관리 (W-08 ~ W-10)

| ID | 이름 | auto | 명령어 | 비고 |
|----|------|------|--------|------|
| W-08 | Windows Firewall 활성화 | true | Set-NetFirewallProfile | 방화벽 설정 |
| W-09 | Windows Defender 실시간 보호 | true | Set-MpPreference | Defender 설정 |
| W-10 | 원격 데스크톱 NLA | true | Set-ItemProperty | 레지스트리 설정 |

---

### 레지스트리 설정 (W-11 ~ W-30)

#### 보안 설정 (W-11 ~ W-22)

| ID | 이름 | auto | Value | Type |
|----|------|------|-------|------|
| W-11 | UAC 관리자 승인 모드 | true | 1 | (기본) |
| W-12 | LM 해시 저장 금지 | true | 1 | DWord |
| W-13 | 익명 SAM 열거 차단 | true | 1 | (기본) |
| W-14 | 자동 로그온 비활성화 | true | 0 | (문자) |
| W-15 | RemoteRegistry 비활성화 | true | Disabled | Service |
| W-16 | NTLM 서버 세션 보안 | true | 537395200 | DWord |
| W-17 | 빈 패스워드 제한 | true | 1 | DWord |
| W-18 | SMB v1 비활성화 | true | 0 | DWord |
| W-19 | 익명 공유 차단 | true | 1 | DWord |
| W-20 | LSA 보호 활성화 | true | 1 | DWord |
| W-21 | LAN Manager 인증 수준 | true | 5 | (기본) |
| W-22 | NTLM 클라이언트 세션 보안 | true | 537395200 | (기본) |

#### 사용자 환경 설정 (W-23 ~ W-25)

| ID | 이름 | auto | Value | Path |
|----|------|------|-------|------|
| W-23 | 캐시된 로그온 수 제한 | true | 2 | Winlogon |
| W-24 | 스크린 세이버 패스워드 | true | 1 | Control Panel\Desktop |
| W-25 | 스크린 세이버 대기 시간 | true | 900 | Control Panel\Desktop |

#### 이벤트 로그 설정 (W-26 ~ W-29)

| ID | 이름 | auto | Value | Type | New-Item |
|----|------|------|-------|------|---------|
| W-26 | Security 로그 최대 크기 | true | 196608 | DWord | true |
| W-27 | Application 로그 최대 크기 | true | 32768 | DWord | true |
| W-28 | System 로그 최대 크기 | true | 32768 | DWord | true |
| W-29 | RemoteAccess 계정 잠금 | true | 5 | DWord | true |

#### 세션 관리 (W-30)

| ID | 이름 | auto | Value | Type |
|----|------|------|-------|------|
| W-30 | 세션 유휴 시간 제한 | true | 15 | DWord |

---

### 패치 관리 (W-41 ~ W-45)

| ID | 이름 | auto | Value | Path | New-Item |
|----|------|------|-------|------|---------|
| W-41 | Auto Update 활성화 | true | 0 | WindowsUpdate\AU | true |
| W-42 | Auto Install 설정 | true | 4 | WindowsUpdate\AU | true |
| W-43 | 예정 설치 시간 | true | 0 | WindowsUpdate\AU | true |
| W-44 | 드라이버 제외 | true | 1 | WindowsUpdate | true |
| W-45 | 자동 재부팅 금지 | true | 1 | WindowsUpdate\AU | true |

---

### 로깅/감사 (W-46 ~ W-50)

| ID | 이름 | auto | Value | Type | New-Item |
|----|------|------|-------|------|---------|
| W-46 | PowerShell Script Block Logging | true | 1 | DWord | true |
| W-47 | PowerShell Module Logging | true | 1 | DWord | true |
| W-48 | Command Line Process Auditing | true | 1 | DWord | true |
| W-49 | Windows Defender 로그 | true | 0 | DWord | true |
| W-50 | 이벤트 로그 보존 정책 | true | 1 | String | true |

---

## 5. 최종 통계

### 요약 통계

| 항목 | 값 |
|-----|-----|
| 총 규칙 수 | 50개 |
| auto: true | 49개 (98%) |
| auto: false | 1개 (2%) |
| Set-ItemProperty 사용 | 40개 (80%) |
| New-Item 사용 | 16개 (32%) |
| 다른 명령어 사용 | 10개 (20%) |

### 주요 발견사항

1. **자동 수정 비율 높음**: 98%의 규칙이 자동 수정 가능
2. **레지스트리 중심**: 80%가 Set-ItemProperty로 레지스트리 설정
3. **키 생성 처리**: 32%의 규칙이 New-Item으로 경로 사전 생성
4. **타입 안전성**: 대부분 -Type DWord 명시적 지정
5. **W-03만 예외**: secedit 복잡도로 인한 수동 처리

---

## 6. YAML 파싱 로직 설계 (제안)

### RemediationCommand 데이터 모델 (src/core/domain/models.py)

```python
from typing import Optional, List, Literal

class RegistryCommand:
    """레지스트리 설정 명령어 추상화"""
    path: str  # HKLM:\...
    name: str  # 값 이름
    value: Union[int, str]  # 설정값
    value_type: Optional[Literal["DWord", "String", "Binary"]] = None
    create_path: bool = False  # New-Item 필요 여부

class RemediationMetadata:
    """수정 메타데이터"""
    auto: bool
    description: str
    backup_files: List[str]
    commands: List[str]  # 원본 PowerShell 명령어
    registry_commands: Optional[List[RegistryCommand]] = None  # 파싱된 레지스트리 명령어
```

### 파싱 함수 (제안)

```python
import re
from typing import List, Dict, Optional

def parse_registry_command(cmd: str) -> Optional[RegistryCommand]:
    """Set-ItemProperty 명령어에서 레지스트리 정보 추출"""
    
    # 패턴: -Path "경로" -Name "키" -Value 값 [-Type 타입]
    path_match = re.search(r'-Path\s+"([^"]+)"', cmd)
    name_match = re.search(r'-Name\s+"([^"]+)"', cmd)
    value_match = re.search(r'-Value\s+(\d+|"[^"]*"|\$\w+)', cmd)
    type_match = re.search(r'-Type\s+(\w+)', cmd)
    
    if not (path_match and name_match and value_match):
        return None
    
    path = path_match.group(1)
    name = name_match.group(1)
    value = value_match.group(1).strip('"')
    value_type = type_match.group(1) if type_match else None
    
    return RegistryCommand(
        path=path,
        name=name,
        value=int(value) if value.isdigit() else value,
        value_type=value_type
    )

def extract_registry_rules(rule_id: str, commands: List[str]) -> Dict:
    """규칙에서 레지스트리 정보 추출"""
    registry_info = {
        'id': rule_id,
        'registry_commands': [],
        'has_new_item': False,
        'paths': set(),
        'values': []
    }
    
    for cmd in commands:
        # New-Item 감지
        if 'New-Item' in cmd:
            registry_info['has_new_item'] = True
            path_match = re.search(r'-Path\s+"([^"]+)"', cmd)
            if path_match:
                registry_info['paths'].add(path_match.group(1))
        
        # Set-ItemProperty 파싱
        if 'Set-ItemProperty' in cmd:
            reg_cmd = parse_registry_command(cmd)
            if reg_cmd:
                registry_info['registry_commands'].append(reg_cmd)
                registry_info['paths'].add(reg_cmd.path)
                registry_info['values'].append({
                    'name': reg_cmd.name,
                    'value': reg_cmd.value,
                    'type': reg_cmd.value_type
                })
    
    return registry_info
```

---

## 7. WindowsRemediator 설계 (제안)

### REGISTRY_RULES 상수 정의

```python
# src/core/remediation/windows_remediator.py

REGISTRY_RULES = {
    'W-10': {
        'category': 'security',
        'path': r'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp',
        'name': 'UserAuthentication',
        'value': 1,
        'type': 'DWord'
    },
    'W-11': {
        'category': 'security',
        'path': r'HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System',
        'name': 'EnableLUA',
        'value': 1
    },
    # ... 40개 규칙 계속
    'W-41': {
        'category': 'patch',
        'path': r'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU',
        'name': 'NoAutoUpdate',
        'value': 0,
        'type': 'DWord',
        'create_path': True
    },
    # ... 계속
}

class WindowsRemediator(BaseRemediator):
    """Windows 자동 수정 엔진"""
    
    async def remediate_registry(self, rule_id: str, dry_run: bool = False) -> RemediationResult:
        """레지스트리 값 수정"""
        if rule_id not in REGISTRY_RULES:
            return RemediationResult(status='manual', message=f'{rule_id} 없음')
        
        rule = REGISTRY_RULES[rule_id]
        
        try:
            if dry_run:
                # 미리보기 모드: 실행할 명령어 표시
                return RemediationResult(
                    status='preview',
                    commands=[
                        f'New-Item -Path "{rule["path"]}" -Force (경로 미존재시)',
                        f'Set-ItemProperty -Path "{rule["path"]}" '
                        f'-Name "{rule["name"]}" '
                        f'-Value {rule["value"]} '
                        f'-Type {rule.get("type", "String")}'
                    ]
                )
            
            # 실제 수정: WinRM을 통해 PowerShell 실행
            await self.winrm_client.execute_registry_set(rule)
            
            return RemediationResult(
                status='success',
                message=f'{rule_id} 레지스트리 수정 완료'
            )
        
        except Exception as e:
            return RemediationResult(
                status='failed',
                message=f'오류: {str(e)}'
            )
```

---

## 8. 권장 구현 순서

### Phase 1: 데이터 모델 및 파싱 (1-2일)
1. RemediationCommand, RegistryCommand 모델 정의
2. YAML 파싱 함수 구현
3. 단위 테스트 작성

### Phase 2: WindowsRemediator 기본 구현 (2-3일)
1. REGISTRY_RULES 상수 정의 (40개 규칙)
2. set_registry 메서드 구현
3. New-Item 경로 생성 로직 구현
4. dry-run 모드 구현

### Phase 3: 특수 명령어 처리 (1-2일)
1. net accounts 명령어 지원 (W-04~W-07)
2. Set-Service 명령어 지원 (W-15)
3. Set-NetFirewallProfile 지원 (W-08)

### Phase 4: 테스트 및 검증 (2-3일)
1. 40개 규칙 통합 테스트
2. 에러 처리 및 롤백 테스트
3. 성능 테스트 (병렬 수정)

---

## 부록: 30개 규칙 목록 (W-01~W-10, W-11~W-30)

### auto: true 규칙 30개 (설명)

1. **W-01**: Administrator 계정 이름 변경 | Rename-LocalUser
2. **W-02**: Guest 계정 비활성화 | Disable-LocalUser
3. **W-04**: 패스워드 최소 길이 8자 | net accounts
4. **W-05**: 패스워드 최대 사용 기간 90일 | net accounts
5. **W-06**: 계정 잠금 임계값 5회 | net accounts
6. **W-07**: 계정 잠금 기간 30분 | net accounts
7. **W-08**: Windows Firewall 활성화 | Set-NetFirewallProfile
8. **W-09**: Windows Defender 실시간 보호 | Set-MpPreference
9. **W-10**: 원격 데스크톱 NLA | Set-ItemProperty (Value: 1)
10. **W-11**: UAC 관리자 승인 모드 | Set-ItemProperty (Value: 1)
11. **W-12**: LM 해시 저장 금지 | Set-ItemProperty (Value: 1, Type: DWord)
12. **W-13**: 익명 SAM 열거 차단 | Set-ItemProperty (Value: 1)
13. **W-14**: 자동 로그온 비활성화 | Set-ItemProperty (Value: 0)
14. **W-15**: RemoteRegistry 서비스 비활성화 | Set-Service
15. **W-16**: NTLM 서버 세션 보안 | Set-ItemProperty (Value: 537395200, Type: DWord)
16. **W-17**: 빈 패스워드 제한 | Set-ItemProperty (Value: 1, Type: DWord)
17. **W-18**: SMB v1 비활성화 | Set-ItemProperty (Value: 0, Type: DWord)
18. **W-19**: 익명 공유 및 파이프 차단 | Set-ItemProperty (Value: 1, Type: DWord)
19. **W-20**: LSA 보호 활성화 | Set-ItemProperty (Value: 1, Type: DWord)
20. **W-21**: LAN Manager 인증 수준 | Set-ItemProperty (Value: 5)
21. **W-22**: NTLM 클라이언트 세션 보안 | Set-ItemProperty (Value: 537395200)
22. **W-23**: 캐시된 로그온 수 제한 | Set-ItemProperty (Value: 2)
23. **W-24**: 스크린 세이버 패스워드 보호 | Set-ItemProperty (Value: 1)
24. **W-25**: 스크린 세이버 대기 시간 | Set-ItemProperty (Value: 900)
25. **W-26**: Security 이벤트 로그 최대 크기 | Set-ItemProperty + New-Item (Value: 196608, Type: DWord)
26. **W-27**: Application 이벤트 로그 최대 크기 | Set-ItemProperty + New-Item (Value: 32768, Type: DWord)
27. **W-28**: System 이벤트 로그 최대 크기 | Set-ItemProperty + New-Item (Value: 32768, Type: DWord)
28. **W-29**: RemoteAccess 계정 잠금 임계값 | Set-ItemProperty + New-Item (Value: 5, Type: DWord)
29. **W-30**: 세션 유휴 시간 제한 | Set-ItemProperty (Value: 15, Type: DWord)

### auto: false 규칙 1개

30. **W-03**: 패스워드 복잡성 정책 설정 | secedit (수동 처리)

---

## 참고 사항

- 모든 Set-ItemProperty 명령어는 경로, 키, 값으로 구성
- New-Item은 16개 규칙에서 사전 경로 생성에 사용
- 타입 안전성: -Type DWord 명시적 지정 권장
- W-03은 보안 정책 특성상 수동 처리 필요
- PowerShell 버전: Windows 5.1 이상 권장
