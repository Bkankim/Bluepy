"""WindowsRemediator - Windows 자동 수정

Windows 레지스트리 기반 보안 규칙의 자동 수정을 지원합니다.
지원 규칙:
- W-11~W-20: 레지스트리 보안 설정 (10개)
- W-21~W-30: 레지스트리 사용자/로깅 (10개)
- W-41~W-50: 패치 관리 및 로깅/감사 (10개)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..domain.models import RemediationResult, RuleMetadata
from ..scanner.base_scanner import BaseScanner
from ..scanner.rule_loader import RuleLoaderError, load_rules
from .backup_manager import BackupManager
from .base_remediator import BaseRemediator

logger = logging.getLogger(__name__)


class WindowsRemediator(BaseRemediator):
    """Windows 자동 수정

    Windows 레지스트리 기반 보안 규칙의 자동 수정을 지원합니다.
    현재 30개의 레지스트리 규칙을 지원합니다 (W-11~W-30, W-41~W-50).

    BaseRemediator가 백업/롤백/dry-run을 자동 처리하므로,
    PowerShell 명령어 실행 로직만 구현합니다.

    지원 규칙 범위:
    - REGISTRY_RULES: 레지스트리 Set-ItemProperty 명령어 (30개)
    - SERVICE_RULES: Windows 서비스 관리 (10개, 향후 확장)
    - SPECIAL_RULES: 특수 명령어 (10개, 향후 확장)

    사용 예시:
        >>> remediator = WindowsRemediator(
        ...     scanner=windows_scanner,
        ...     backup_manager=backup_manager
        ... )
        >>> # Dry-run으로 미리보기
        >>> result = await remediator.remediate(rule, dry_run=True)
        >>> print(result.message)
        >>> # 실제 수정 실행
        >>> result = await remediator.remediate(rule, dry_run=False)
        >>> if result.success:
        ...     print(f"수정 완료: {result.backup_id}")
        >>> else:
        ...     print(f"수정 실패: {result.error}")
    """

    # 레지스트리 자동 수정 지원 규칙 (30개)
    # Set-ItemProperty 명령어를 사용하는 규칙들
    REGISTRY_RULES = [
        # 레지스트리 보안 설정 (W-11~W-20)
        "W-11",  # SAM 원격 접근 제한
        "W-12",  # LAN Manager 인증 레벨
        "W-13",  # NTLM SSP 기반 서버 최소 보안
        "W-14",  # 익명 SID/이름 변환 허용 안 함
        "W-15",  # 익명 SAM 계정 열거 허용 안 함
        "W-16",  # Everyone 익명 사용자 포함 안 함
        "W-17",  # 공유 보안 모델 (클래식 로컬)
        "W-18",  # NTLM SSP 기반 클라이언트 최소 보안
        "W-19",  # NULL 세션 익명 접근 불가
        "W-20",  # NTLM 인증 거부
        # 레지스트리 사용자/로깅 (W-21~W-30)
        "W-21",  # 콘솔 로그온 시 마지막 사용자 이름 표시 안 함
        "W-22",  # 로그온 시도 제한 (계정 잠금)
        "W-23",  # SAM 계정 및 공유 익명 열거 불가
        "W-24",  # 시스템 종료 시 가상 메모리 페이지 파일 지움
        "W-25",  # 자동 로그온 기능 제거
        "W-26",  # 이동식 미디어 포맷 및 꺼내기 제한
        "W-27",  # 원격 시스템의 강제 종료 권한 제한
        "W-28",  # 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한
        "W-29",  # 경고 메시지 제목 설정
        "W-30",  # 경고 메시지 내용 설정
        # 패치 관리 (W-41~W-45)
        "W-41",  # Windows Update 자동 업데이트
        "W-42",  # Windows Update 자동 업데이트 구성
        "W-43",  # 자동 업데이트 다운로드 허용
        "W-44",  # 자동 업데이트 알림 허용
        "W-45",  # Windows Update 서비스 활성화
        # 로깅/감사 (W-46~W-50)
        "W-46",  # 감사 정책 - 계정 로그온 이벤트
        "W-47",  # 감사 정책 - 계정 관리
        "W-48",  # 감사 정책 - 로그온 이벤트
        "W-49",  # 감사 정책 - 개체 액세스
        "W-50",  # 감사 정책 - 정책 변경
    ]

    # 서비스 관리 규칙 (10개, Phase 3 이후 확장 예정)
    # Set-Service, Stop-Service, Disable-Service 명령어 사용
    SERVICE_RULES = [
        "W-31",  # Windows Defender Antivirus Service
        "W-32",  # Windows Firewall
        "W-33",  # Windows Update Service
        "W-34",  # Remote Registry Service
        "W-35",  # Remote Desktop Services
        "W-36",  # Server Service
        "W-37",  # Workstation Service
        "W-38",  # Print Spooler Service
        "W-39",  # Telnet Service
        "W-40",  # FTP Service
    ]

    # 특수 명령어 규칙 (10개, Phase 3 이후 확장 예정)
    # Rename-LocalUser, Disable-LocalUser, net accounts 등
    SPECIAL_RULES = [
        "W-01",  # Rename-LocalUser (Administrator 이름 변경)
        "W-02",  # Disable-LocalUser (Guest 계정 비활성화)
        "W-03",  # secedit (암호 정책, 수동 점검)
        "W-04",  # net accounts /maxpwage (패스워드 최대 사용 기간)
        "W-05",  # net accounts /minpwlen (패스워드 최소 길이)
        "W-06",  # net accounts /minpwage (패스워드 최소 사용 기간)
        "W-07",  # net accounts /uniquepw (패스워드 최소 길이)
        "W-08",  # Set-NetFirewallProfile (방화벽 활성화)
        "W-09",  # Set-MpPreference (Windows Defender)
        "W-10",  # Set-ItemProperty (RDP NLA 설정)
    ]

    def __init__(self, scanner: BaseScanner, backup_manager: Optional[BackupManager] = None):
        """WindowsRemediator 초기화

        Args:
            scanner: WindowsScanner 인스턴스 (WinRMClient 포함)
            backup_manager: 백업 관리자 (선택사항, 기본값 자동 생성)

        사용 예시:
            >>> scanner = WindowsScanner(...)
            >>> await scanner.connect()
            >>> remediator = WindowsRemediator(scanner)
            >>> await remediator.remediate(rule)
        """
        super().__init__(scanner, backup_manager)
        logger.debug(f"WindowsRemediator 초기화: {scanner.server_id}")

    async def _execute_commands(self, commands: List[str]) -> List[str]:
        """Windows PowerShell 명령어 실행

        WindowsScanner의 WinRM 연결을 재사용하여 PowerShell 명령어를 실행합니다.
        BaseRemediator가 백업/롤백/dry-run을 자동 처리하므로,
        이 메서드는 순수하게 명령어 실행만 담당합니다.

        Args:
            commands: 실행할 PowerShell 명령어 목록 (YAML remediation.commands)

        Returns:
            List[str]: 실행 성공한 명령어 목록

        Raises:
            Exception: 명령어 실행 실패 시 (BaseRemediator가 자동 롤백 처리)

        사용 예시:
            >>> commands = [
            ...     "Set-ItemProperty -Path 'HKLM:\\Path' -Name 'Key' -Value 1",
            ...     "Restart-Service -Name 'ServiceName'"
            ... ]
            >>> executed = await remediator._execute_commands(commands)
            >>> print(f"{len(executed)}개 명령어 실행 완료")
        """
        executed = []

        for cmd in commands:
            try:
                # Scanner의 WinRM 연결 재사용
                # WindowsScanner.execute_command() -> WinRMClient.execute_powershell()
                result = await self.scanner.execute_command(cmd)
                executed.append(cmd)
                logger.info(f"명령어 실행 완료: {cmd[:50]}...")
                logger.debug(f"명령어 출력: {result[:200]}...")

            except Exception as e:
                logger.error(f"명령어 실행 실패: {cmd[:50]}..., {e}")
                # Exception 발생 -> BaseRemediator가 자동 롤백
                raise Exception(f"명령어 실행 실패: {cmd[:30]}... ({e})")

        return executed

    async def _backup_registry(self, registry_path: str, rule_id: str) -> Optional[str]:
        r"""레지스트리 키 백업 (원격 서버)

        reg export 명령어를 사용하여 원격 Windows 서버의 레지스트리 키를
        .reg 파일로 백업합니다. 백업 파일은 원격 서버의 임시 디렉토리에
        저장됩니다.

        Args:
            registry_path: 레지스트리 경로 (예: "HKLM\System\CurrentControlSet\...")
            rule_id: 규칙 ID (백업 파일 이름 생성용)

        Returns:
            Optional[str]: 백업 파일 경로 (원격 서버 경로), 실패 시 None

        사용 예시:
            >>> backup_file = await remediator._backup_registry(
            ...     r"HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System",
            ...     "W-11"
            ... )
            >>> print(backup_file)
            C:\Windows\Temp\bluepy_backup_W-11_20250120_143052.reg
        """
        # 백업 파일 경로 생성 (원격 서버의 임시 디렉토리)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"C:\\Windows\\Temp\\bluepy_backup_{rule_id}_{timestamp}.reg"

        # reg export 명령어 생성
        # /y 플래그: 기존 파일 덮어쓰기 확인 없이 실행
        cmd = f'reg export "{registry_path}" "{backup_file}" /y'

        try:
            # WinRMClient를 통해 PowerShell 실행
            _ = await self.scanner.execute_command(cmd)
            logger.info(f"{rule_id}: 레지스트리 백업 완료 - {backup_file}")
            logger.debug(f"백업 경로: {registry_path}")
            return backup_file

        except Exception as e:
            # 백업 실패해도 계속 진행 (warning 레벨)
            logger.warning(f"{rule_id}: 레지스트리 백업 실패 (자동 수정은 계속 진행) - {e}")
            logger.debug(f"백업 시도한 경로: {registry_path}")
            return None

    async def _rollback_registry(self, backup_file: str, rule_id: str) -> bool:
        r"""레지스트리 롤백 (백업 파일로 복원)

        백업된 .reg 파일을 사용하여 레지스트리를 이전 상태로 복원합니다.
        reg import 명령어를 사용하여 원격 서버의 레지스트리를 복구합니다.

        Args:
            backup_file: 백업 파일 경로 (원격 서버 경로)
            rule_id: 규칙 ID

        Returns:
            bool: 성공 여부

        사용 예시:
            >>> success = await remediator._rollback_registry(
            ...     r"C:\Windows\Temp\bluepy_backup_W-11_20250120_143052.reg",
            ...     "W-11"
            ... )
            >>> if success:
            ...     print("롤백 성공")
            ... else:
            ...     print("롤백 실패")
        """
        # reg import 명령어 생성
        cmd = f'reg import "{backup_file}"'

        try:
            # WinRMClient를 통해 PowerShell 실행
            _ = await self.scanner.execute_command(cmd)
            logger.info(f"{rule_id}: 레지스트리 롤백 완료")
            logger.debug(f"복원한 파일: {backup_file}")
            return True

        except Exception as e:
            # 롤백 실패는 에러 레벨 (심각한 상황)
            logger.error(f"{rule_id}: 레지스트리 롤백 실패 - {e}")
            logger.error(f"복원 시도한 파일: {backup_file}")
            return False

    async def _remediate_registry(self, rule_id: str, dry_run: bool = False) -> RemediationResult:
        """레지스트리 자동 수정 (W-11~W-50 중 30개 규칙)

        Windows 레지스트리 규칙의 자동 수정을 수행합니다.
        YAML 파일에서 remediation.commands를 로드하여 PowerShell 명령어를 실행합니다.

        처리 플로우:
        1. YAML 규칙 로드 (RuleLoader 사용)
        2. remediation.commands 추출
        3. dry_run이면 미리보기만 반환
        4. 실제 PowerShell 명령어 실행 (WinRMClient)
        5. RemediationResult 생성 및 반환

        Args:
            rule_id: 규칙 ID (예: "W-11", "W-21", "W-45")
            dry_run: True이면 시뮬레이션만 (실제 수정 안 함)

        Returns:
            RemediationResult: 수정 결과
                - success: 성공 여부
                - message: 결과 메시지
                - executed_commands: 실행한 명령어 목록
                - error: 에러 정보 (실패 시)

        Raises:
            없음 (모든 예외는 RemediationResult로 반환)

        사용 예시:
            >>> remediator = WindowsRemediator(scanner)
            >>> # Dry-run으로 미리보기
            >>> result = await remediator._remediate_registry("W-11", dry_run=True)
            >>> print(result.message)
            [Dry-run] W-11: 실행할 명령어 2개
            >>> # 실제 수정 실행
            >>> result = await remediator._remediate_registry("W-11", dry_run=False)
            >>> if result.success:
            ...     print(f"수정 완료: {len(result.executed_commands)}개 명령어")
            ... else:
            ...     print(f"수정 실패: {result.error}")
        """
        # 1. YAML 규칙 로드
        try:
            # config/rules/windows 디렉토리에서 규칙 로드
            rules_dir = Path(__file__).parents[3] / "config" / "rules"
            rules = load_rules(str(rules_dir), platform="windows")

            # 딕셔너리로 변환 (rule_id로 검색)
            rules_dict = {rule.id: rule for rule in rules}

            # 해당 규칙 찾기
            rule = rules_dict.get(rule_id)

            if not rule:
                error_msg = f"{rule_id}: 규칙을 찾을 수 없습니다."
                logger.error(error_msg)
                return RemediationResult(
                    success=False,
                    message=error_msg,
                    error="Rule not found",
                    dry_run=dry_run,
                    timestamp=datetime.now(),
                )

        except RuleLoaderError as e:
            error_msg = f"{rule_id}: YAML 로드 실패 - {e}"
            logger.error(error_msg)
            return RemediationResult(
                success=False,
                message=error_msg,
                error=str(e),
                dry_run=dry_run,
                timestamp=datetime.now(),
            )

        # 2. remediation.commands 추출 및 유효성 검사
        if not rule.remediation or not rule.remediation.auto:
            error_msg = f"{rule_id}: 자동 수정이 불가능한 규칙입니다."
            logger.warning(error_msg)
            return RemediationResult(
                success=False,
                message=error_msg,
                error="Auto remediation not enabled",
                dry_run=dry_run,
                timestamp=datetime.now(),
            )

        commands = rule.remediation.commands
        if not commands:
            error_msg = f"{rule_id}: 실행할 명령어가 없습니다."
            logger.error(error_msg)
            return RemediationResult(
                success=False,
                message=error_msg,
                error="No commands to execute",
                dry_run=dry_run,
                timestamp=datetime.now(),
            )

        # 3. Dry-run 모드 (미리보기만)
        if dry_run:
            message = f"[Dry-run] {rule_id}: 실행할 명령어 {len(commands)}개\n" + "\n".join(
                f"  - {cmd[:80]}..." for cmd in commands[:3]
            )
            if len(commands) > 3:
                message += f"\n  ... 외 {len(commands) - 3}개"

            logger.info(f"Dry-run: {rule_id} - {len(commands)}개 명령어")
            return RemediationResult(
                success=True,
                message=message,
                executed_commands=commands,
                dry_run=True,
                timestamp=datetime.now(),
            )

        # 4. 레지스트리 백업 (선택사항)
        backup_file = None
        backup_registry_path = getattr(rule.remediation, "backup_registry_path", None)

        if backup_registry_path:
            logger.info(f"{rule_id}: 레지스트리 백업 시작 - {backup_registry_path}")
            backup_file = await self._backup_registry(backup_registry_path, rule_id)
            if backup_file:
                logger.info(f"{rule_id}: 백업 성공 - {backup_file}")
            else:
                logger.warning(f"{rule_id}: 백업 실패 (자동 수정은 계속 진행)")
        else:
            logger.debug(f"{rule_id}: 백업 경로 미지정 (백업 생략)")

        # 5. 실제 PowerShell 명령어 실행
        executed_commands = []
        try:
            logger.info(f"{rule_id}: 자동 수정 시작 ({len(commands)}개 명령어)")

            for idx, cmd in enumerate(commands, 1):
                try:
                    # WinRMClient를 통해 PowerShell 실행
                    result = await self.scanner.execute_command(cmd)
                    executed_commands.append(cmd)
                    logger.info(f"{rule_id}: [{idx}/{len(commands)}] 명령어 실행 완료")
                    logger.debug(f"명령어: {cmd[:100]}...")
                    logger.debug(f"출력: {result[:200]}...")

                except Exception as cmd_error:
                    error_msg = f"{rule_id}: 명령어 실행 실패 [{idx}/{len(commands)}] - {str(cmd_error)[:100]}"
                    logger.error(error_msg)
                    logger.error(f"실패한 명령어: {cmd[:100]}...")

                    # 6. 롤백 시도 (백업 파일이 있으면)
                    if backup_file:
                        logger.info(f"{rule_id}: 명령어 실행 실패 - 롤백 시도")
                        rollback_success = await self._rollback_registry(backup_file, rule_id)
                        if rollback_success:
                            logger.info(f"{rule_id}: 롤백 성공 - 이전 상태로 복원됨")
                        else:
                            logger.error(f"{rule_id}: 롤백 실패 - 수동 복구 필요")

                    return RemediationResult(
                        success=False,
                        message=error_msg,
                        executed_commands=executed_commands,
                        error=str(cmd_error),
                        rollback_performed=bool(backup_file),
                        dry_run=False,
                        timestamp=datetime.now(),
                    )

            # 7. 성공 결과 반환
            success_msg = (
                f"{rule_id}: 레지스트리 자동 수정 완료 ({len(executed_commands)}개 명령어 실행)"
            )
            if backup_file:
                success_msg += f" [백업: {backup_file}]"

            logger.info(success_msg)
            return RemediationResult(
                success=True,
                message=success_msg,
                executed_commands=executed_commands,
                dry_run=False,
                timestamp=datetime.now(),
            )

        except Exception as e:
            # 예상치 못한 에러 처리
            error_msg = f"{rule_id}: 자동 수정 중 예외 발생 - {str(e)[:100]}"
            logger.error(error_msg, exc_info=True)

            # 롤백 시도 (백업 파일이 있으면)
            if backup_file:
                logger.info(f"{rule_id}: 예외 발생 - 롤백 시도")
                rollback_success = await self._rollback_registry(backup_file, rule_id)
                if rollback_success:
                    logger.info(f"{rule_id}: 롤백 성공 - 이전 상태로 복원됨")
                else:
                    logger.error(f"{rule_id}: 롤백 실패 - 수동 복구 필요")

            return RemediationResult(
                success=False,
                message=error_msg,
                executed_commands=executed_commands,
                error=str(e),
                rollback_performed=bool(backup_file),
                dry_run=False,
                timestamp=datetime.now(),
            )

    async def remediate(self, rule: RuleMetadata, dry_run: bool = True) -> RemediationResult:
        """자동 수정 실행 (레지스트리 규칙 전용 오버라이드)

        WindowsRemediator는 레지스트리 규칙(W-11~W-50 중 30개)에 특화되어 있습니다.
        REGISTRY_RULES에 해당하는 규칙이면 _remediate_registry()를 호출하고,
        아니면 BaseRemediator의 기본 동작(_execute_commands)을 사용합니다.

        Args:
            rule: 점검 규칙 (RuleMetadata)
            dry_run: True이면 시뮬레이션만 (기본값: True)

        Returns:
            RemediationResult: 수정 결과

        사용 예시:
            >>> rule = RuleMetadata(id="W-11", ...)
            >>> result = await remediator.remediate(rule, dry_run=True)
            >>> print(result.message)
            [Dry-run] W-11: 실행할 명령어 2개
        """
        # 레지스트리 규칙이면 전용 메서드 사용
        if rule.id in self.REGISTRY_RULES:
            logger.debug(f"{rule.id}: 레지스트리 자동 수정 경로 사용")
            return await self._remediate_registry(rule.id, dry_run)

        # 아니면 BaseRemediator의 기본 동작 사용
        logger.debug(f"{rule.id}: BaseRemediator 기본 경로 사용")
        return await super().remediate(rule, dry_run)


__all__ = ["WindowsRemediator"]
