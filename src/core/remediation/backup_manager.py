"""BackupManager - 백업/롤백 관리자

자동 수정 전 파일을 백업하고, 실패 시 롤백하는 기능을 제공합니다.
"""

import json
import hashlib
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class BackupFile:
    """백업된 파일 정보"""

    original_path: str
    backup_path: str
    mode: str
    checksum: str


@dataclass
class BackupSession:
    """백업 세션"""

    session_id: str
    timestamp: str
    server: str
    rule_ids: List[str]
    files: List[dict]
    status: str  # completed, failed


class BackupManager:
    """백업/롤백 관리자

    자동 수정 전 파일을 백업하고, 실패 시 롤백합니다.
    """

    def __init__(self, backup_root: str = "/var/backups/bluepy"):
        """초기화

        Args:
            backup_root: 백업 루트 디렉토리
        """
        self.backup_root = Path(backup_root)
        self.sessions_dir = self.backup_root / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, server: str, rule_ids: List[str]) -> str:
        """백업 세션 생성

        Args:
            server: 서버 ID
            rule_ids: 규칙 ID 목록

        Returns:
            session_id: "session_YYYYMMDD_HHMMSS"
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "files").mkdir()

        logger.info(f"백업 세션 생성: {session_id}")
        return session_id

    def backup_file(self, session_id: str, file_path: str) -> BackupFile:
        """파일 백업 (간소화 버전)

        Args:
            session_id: 백업 세션 ID
            file_path: 백업할 파일 경로

        Returns:
            BackupFile: 백업 메타데이터
        """
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"원본 파일 없음: {file_path}")

        # 백업 파일명 생성
        backup_name = str(src).replace("/", "_") + ".bak"
        session_dir = self.sessions_dir / session_id
        dst = session_dir / "files" / backup_name

        # 파일 복사
        shutil.copy2(src, dst)

        # 메타데이터
        stat_info = src.stat()
        mode = oct(stat_info.st_mode)[-4:]
        checksum = self._calculate_checksum(src)

        logger.info(f"파일 백업 완료: {file_path}")
        return BackupFile(
            original_path=str(src), backup_path=str(dst), mode=mode, checksum=checksum
        )

    def save_metadata(self, session: BackupSession) -> None:
        """백업 메타데이터 저장

        Args:
            session: 백업 세션
        """
        session_dir = self.sessions_dir / session.session_id
        metadata_path = session_dir / "metadata.json"

        with metadata_path.open("w") as f:
            json.dump(asdict(session), f, indent=2)

        logger.info(f"메타데이터 저장 완료: {session.session_id}")

    def rollback_file(self, backup_file: BackupFile) -> bool:
        """파일 롤백

        Args:
            backup_file: 백업 파일 정보

        Returns:
            bool: 성공 여부
        """
        try:
            src = Path(backup_file.backup_path)
            dst = Path(backup_file.original_path)

            # 체크섬 검증
            if self._calculate_checksum(src) != backup_file.checksum:
                raise ValueError("백업 파일 손상됨")

            # 파일 복원
            shutil.copy2(src, dst)
            logger.info(f"파일 롤백 완료: {backup_file.original_path}")
            return True
        except Exception as e:
            logger.error(f"롤백 실패: {backup_file.original_path}, {e}")
            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """SHA256 체크섬 계산

        Args:
            file_path: 파일 경로

        Returns:
            str: "sha256:xxx..."
        """
        sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"


__all__ = ["BackupManager", "BackupFile", "BackupSession"]
