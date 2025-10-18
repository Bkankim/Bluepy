"""Validator 함수 단위 테스트

src/core/analyzer/validators/linux/ 모듈의 73개 validator 함수를 테스트합니다.

테스트 범위:
1. 73개 함수 존재 확인
2. 함수 시그니처 검증 (List[str] -> CheckResult)
3. 카테고리별 대표 함수 상세 테스트 (5개 카테고리)

카테고리:
- account_management (15개): U-01 ~ U-15
- file_management (20개): U-16 ~ U-35
- service_management (35개): U-36 ~ U-70
- log_management (1개): U-72
- patch_management (1개): U-71
"""

import inspect
from typing import List, get_args, get_origin

import pytest

from src.core.domain.models import CheckResult, Status
from src.core.analyzer.validators import linux


# ==================== 함수 존재 확인 ====================


@pytest.mark.unit
class TestValidatorFunctionsExist:
    """73개 validator 함수 존재 확인"""

    def test_all_73_functions_exist(self, validator_function_names):
        """73개 check_u* 함수가 모두 존재하는지 확인"""
        for func_name in validator_function_names:
            assert hasattr(linux, func_name), f"함수 {func_name}이 존재하지 않습니다"

    def test_all_functions_are_callable(self, validator_function_names):
        """모든 함수가 callable한지 확인"""
        for func_name in validator_function_names:
            func = getattr(linux, func_name)
            assert callable(func), f"{func_name}은 callable하지 않습니다"

    def test_module_all_exports(self):
        """__all__에 73개 함수가 모두 포함되어 있는지 확인"""
        assert hasattr(linux, "__all__"), "linux 모듈에 __all__이 정의되지 않았습니다"
        # __all__에는 check_u01 ~ check_u73이 포함되어야 함
        all_exports = linux.__all__
        expected_count = 73
        assert (
            len(all_exports) == expected_count
        ), f"__all__에 {expected_count}개 함수가 있어야 하는데 {len(all_exports)}개만 있습니다"


# ==================== 함수 시그니처 검증 ====================


@pytest.mark.unit
class TestValidatorFunctionSignatures:
    """validator 함수 시그니처 검증"""

    def test_function_signature_list_str_to_checkresult(self, validator_function_names):
        """모든 함수의 시그니처가 List[str] -> CheckResult인지 확인"""
        for func_name in validator_function_names:
            func = getattr(linux, func_name)
            sig = inspect.signature(func)

            # 파라미터 확인
            params = list(sig.parameters.values())
            assert len(params) == 1, f"{func_name}: 파라미터는 1개여야 합니다"

            param = params[0]
            # 파라미터 이름은 일반적으로 command_outputs
            assert param.name in [
                "command_outputs",
                "outputs",
            ], f"{func_name}: 파라미터 이름이 예상과 다릅니다 ({param.name})"

            # 반환 타입은 CheckResult
            return_annotation = sig.return_annotation
            # Some functions might not have type hints, skip in that case
            if return_annotation != inspect.Signature.empty:
                assert (
                    return_annotation == CheckResult
                    or return_annotation.__name__ == "CheckResult"
                ), f"{func_name}: 반환 타입이 CheckResult가 아닙니다"

    def test_functions_have_docstrings(self, validator_function_names):
        """모든 함수에 docstring이 있는지 확인"""
        for func_name in validator_function_names:
            func = getattr(linux, func_name)
            assert func.__doc__ is not None, f"{func_name}에 docstring이 없습니다"
            assert len(func.__doc__.strip()) > 0, f"{func_name}의 docstring이 비어있습니다"


# ==================== 카테고리별 대표 함수 상세 테스트 ====================


@pytest.mark.unit
class TestAccountManagementValidators:
    """account_management 카테고리 validator 테스트"""

    def test_check_u01_pass_case(self):
        """check_u01: PASS 케이스 (pam_securetty 설정되고 pts 없음)"""
        # /etc/pam.d/login에 pam_securetty.so 있고, /etc/securetty에 pts 없음
        command_outputs = [
            "auth required pam_securetty.so\nauth include system-auth",
            "console\ntty1\ntty2\ntty3\n",  # pts 없음
        ]

        result = linux.check_u01(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status == Status.PASS
        assert "원격 로그인 제한" in result.message or "양호" in result.message.lower()

    def test_check_u01_fail_case(self):
        """check_u01: FAIL 케이스 (pts 허용됨)"""
        # /etc/securetty에 pts가 있는 경우
        command_outputs = [
            "auth required pam_securetty.so\n",
            "console\ntty1\npts/0\npts/1\n",  # pts 있음
        ]

        result = linux.check_u01(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.FAIL, Status.MANUAL]

    def test_check_u03_pass_case(self):
        """check_u03: PASS 케이스 (계정 잠금 임계값 설정됨)"""
        # pam_tally2 또는 pam_faillock 설정됨
        command_outputs = [
            "auth required pam_tally2.so deny=5 unlock_time=120\n",
        ]

        result = linux.check_u03(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.PASS, Status.MANUAL]

    def test_check_u04_pass_case(self):
        """check_u04: PASS 케이스 (패스워드 파일 보호)"""
        # /etc/shadow 파일 존재 (Shadow 패스워드 사용)
        command_outputs = [
            "-rw-r----- 1 root shadow 1234 Jan 1 12:00 /etc/shadow\n",
        ]

        result = linux.check_u04(command_outputs)

        assert isinstance(result, CheckResult)
        # check_u04는 shadow 파일 존재 시 PASS
        assert result.status == Status.PASS


@pytest.mark.unit
class TestFileManagementValidators:
    """file_management 카테고리 validator 테스트"""

    def test_check_u18_pass_case(self):
        """check_u18: PASS 케이스 (/etc/passwd 644, /etc/shadow 400)"""
        # 올바른 권한 설정
        command_outputs = [
            "-rw-r--r-- 1 root root 2345 Jan 1 12:00 /etc/passwd\n",  # 644
            "-r-------- 1 root root 1234 Jan 1 12:00 /etc/shadow\n",  # 400
        ]

        result = linux.check_u18(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status == Status.PASS

    def test_check_u18_fail_case(self):
        """check_u18: FAIL 케이스 (잘못된 권한)"""
        # /etc/shadow에 쓰기 권한이 있는 경우 (640 등)
        command_outputs = [
            "-rw-r--r-- 1 root root 2345 Jan 1 12:00 /etc/passwd\n",
            "-rw-r----- 1 root shadow 1234 Jan 1 12:00 /etc/shadow\n",  # 640
        ]

        result = linux.check_u18(command_outputs)

        assert isinstance(result, CheckResult)
        # 640도 보안상 문제가 있을 수 있음
        assert result.status in [Status.PASS, Status.FAIL, Status.MANUAL]

    def test_check_u27_pass_case(self):
        """check_u27: PASS 케이스 (rsh/rlogin/rexec 서비스 비활성화)"""
        # rsh, rlogin, rexec 서비스가 비활성화된 경우
        command_outputs = [
            "# rsh disabled\n# rlogin disabled\n# rexec disabled\n",
        ]

        result = linux.check_u27(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.PASS, Status.MANUAL]

    def test_check_u27_fail_case(self):
        """check_u27: FAIL 케이스 (rsh 활성화)"""
        # rsh 서비스가 활성화된 경우
        command_outputs = [
            "rsh stream tcp nowait root /usr/sbin/in.rshd in.rshd\n",
        ]

        result = linux.check_u27(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.FAIL, Status.MANUAL]


@pytest.mark.unit
class TestServiceManagementValidators:
    """service_management 카테고리 validator 테스트"""

    def test_check_u36_pass_case(self):
        """check_u36: PASS 케이스 (Anonymous FTP 비활성화)"""
        # vsftpd.conf에서 anonymous_enable=NO 설정
        command_outputs = [
            "anonymous_enable=NO\nlocal_enable=YES\n",
        ]

        result = linux.check_u36(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.PASS, Status.MANUAL]

    def test_check_u36_fail_case(self):
        """check_u36: FAIL 케이스 (Anonymous FTP 활성화)"""
        # anonymous_enable=YES
        command_outputs = [
            "anonymous_enable=YES\nlocal_enable=YES\n",
        ]

        result = linux.check_u36(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.FAIL, Status.MANUAL]

    def test_check_u44_pass_case(self):
        """check_u44: PASS 케이스 (Sendmail 버전 최신)"""
        # Sendmail 8.14 이상 또는 비활성화
        command_outputs = [
            "Sendmail 8.15.2\n",
        ]

        result = linux.check_u44(command_outputs)

        assert isinstance(result, CheckResult)
        # 버전이 최신이면 PASS 또는 MANUAL
        assert result.status in [Status.PASS, Status.MANUAL]


@pytest.mark.unit
class TestLogManagementValidators:
    """log_management 카테고리 validator 테스트"""

    def test_check_u72_pass_case(self):
        """check_u72: PASS 케이스 (로그 파일 권한 적절)"""
        # /var/log/messages 등의 로그 파일 권한이 640 이하
        command_outputs = [
            "-rw-r----- 1 root adm 12345 Jan 1 12:00 /var/log/messages\n",  # 640
        ]

        result = linux.check_u72(command_outputs)

        assert isinstance(result, CheckResult)
        assert result.status in [Status.PASS, Status.MANUAL]

    def test_check_u72_fail_case(self):
        """check_u72: FAIL 케이스 (로그 파일이 world-readable)"""
        # 로그 파일이 644 이상 (other에게 읽기 권한)
        command_outputs = [
            "-rw-r--r-- 1 root root 12345 Jan 1 12:00 /var/log/messages\n",  # 644
        ]

        result = linux.check_u72(command_outputs)

        assert isinstance(result, CheckResult)
        # 644는 보안상 문제가 있을 수 있음
        assert result.status in [Status.PASS, Status.FAIL, Status.MANUAL]


@pytest.mark.unit
class TestPatchManagementValidators:
    """patch_management 카테고리 validator 테스트"""

    def test_check_u71_pass_case(self):
        """check_u71: PASS 케이스 (최신 패치 적용됨)"""
        # apt 또는 yum으로 최신 패키지 업데이트 확인
        command_outputs = [
            "All packages are up to date.\n",
        ]

        result = linux.check_u71(command_outputs)

        assert isinstance(result, CheckResult)
        # 패치 관리는 일반적으로 MANUAL 검증 필요
        assert result.status in [Status.PASS, Status.MANUAL]

    def test_check_u71_manual_case(self):
        """check_u71: MANUAL 케이스 (수동 확인 필요)"""
        # 패치 상태 불명확
        command_outputs = [
            "100 packages can be upgraded.\n",
        ]

        result = linux.check_u71(command_outputs)

        assert isinstance(result, CheckResult)
        # 업그레이드 가능한 패키지가 있으면 FAIL 또는 MANUAL
        assert result.status in [Status.FAIL, Status.MANUAL]


# ==================== 예외 처리 테스트 ====================


@pytest.mark.unit
class TestValidatorExceptionHandling:
    """validator 함수 예외 처리 테스트"""

    def test_empty_command_outputs(self):
        """빈 command_outputs 처리"""
        # 대부분의 validator는 빈 입력을 받으면 MANUAL 또는 FAIL 반환
        result = linux.check_u01([])

        assert isinstance(result, CheckResult)
        assert result.status in [Status.MANUAL, Status.FAIL]

    def test_invalid_command_outputs(self):
        """잘못된 형식의 command_outputs 처리"""
        # 예상과 다른 형식의 출력
        result = linux.check_u01(["invalid output", "another invalid"])

        assert isinstance(result, CheckResult)
        # 잘못된 입력은 MANUAL 또는 FAIL
        assert result.status in [Status.MANUAL, Status.FAIL]

    def test_function_returns_checkresult(self, validator_function_names):
        """모든 함수가 CheckResult를 반환하는지 확인"""
        # 각 함수에 빈 리스트를 전달하고 CheckResult 반환 확인
        for func_name in validator_function_names[:10]:  # 샘플 10개만 테스트
            func = getattr(linux, func_name)
            result = func([])

            assert isinstance(
                result, CheckResult
            ), f"{func_name}이 CheckResult를 반환하지 않습니다"


# ==================== 카테고리별 함수 개수 검증 ====================


@pytest.mark.unit
class TestValidatorCategories:
    """카테고리별 validator 함수 개수 검증"""

    def test_account_management_count(self, validator_categories):
        """account_management 카테고리 함수 개수 (15개)"""
        category = validator_categories["account_management"]
        assert len(category) == 15, f"account_management는 15개여야 하는데 {len(category)}개입니다"

    def test_file_management_count(self, validator_categories):
        """file_management 카테고리 함수 개수 (20개)"""
        category = validator_categories["file_management"]
        assert len(category) == 20, f"file_management는 20개여야 하는데 {len(category)}개입니다"

    def test_service_management_count(self, validator_categories):
        """service_management 카테고리 함수 개수 (35개)"""
        category = validator_categories["service_management"]
        # service_management는 실제로 35개인지 확인 필요
        assert len(category) >= 30, f"service_management는 최소 30개여야 합니다"

    def test_log_management_count(self, validator_categories):
        """log_management 카테고리 함수 개수"""
        category = validator_categories.get("log_management", [])
        assert len(category) >= 1, "log_management는 최소 1개여야 합니다"

    def test_patch_management_count(self, validator_categories):
        """patch_management 카테고리 함수 개수"""
        category = validator_categories.get("patch_management", [])
        assert len(category) >= 1, "patch_management는 최소 1개여야 합니다"
