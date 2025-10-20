"""스캔 이력 Repository

ScanHistory 모델에 대한 CRUD 기능을 제공합니다.

주요 기능:
- Create: 스캔 이력 추가
- Read: 스캔 이력 조회 (서버별, 트렌드 데이터)
- Delete: 오래된 이력 삭제
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict

from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from ..models import ScanHistory


class HistoryRepository:
    """스캔 이력 Repository 클래스

    ScanHistory 모델에 대한 데이터베이스 작업을 제공합니다.
    """

    def __init__(self, session: Session):
        """초기화

        Args:
            session: SQLAlchemy Session
        """
        self.session = session

    def create(
        self,
        server_id: int,
        total: int,
        passed: int,
        failed: int,
        manual: int,
        score: int,
        result_data: Optional[str] = None,
    ) -> ScanHistory:
        """스캔 이력 추가

        Args:
            server_id: 서버 ID
            total: 전체 점검 항목 수
            passed: 양호 항목 수
            failed: 취약 항목 수
            manual: 수동 점검 필요 항목 수
            score: 점수 (0~100)
            result_data: 상세 결과 데이터 (JSON 문자열)

        Returns:
            생성된 ScanHistory 객체
        """
        history = ScanHistory(
            server_id=server_id,
            scan_time=datetime.now(),
            total=total,
            passed=passed,
            failed=failed,
            manual=manual,
            score=score,
            result_data=result_data,
        )

        self.session.add(history)
        self.session.commit()
        self.session.refresh(history)

        return history

    def get_history_by_server(
        self, server_id: int, limit: int = 10
    ) -> List[ScanHistory]:
        """특정 서버의 스캔 이력 조회 (최근순)

        Args:
            server_id: 서버 ID
            limit: 조회할 최대 개수 (기본값: 10)

        Returns:
            ScanHistory 객체 리스트 (최신순)
        """
        return (
            self.session.query(ScanHistory)
            .filter(ScanHistory.server_id == server_id)
            .order_by(desc(ScanHistory.scan_time))
            .limit(limit)
            .all()
        )

    def get_trend_data(self, server_id: int, days: int = 30) -> List[Dict]:
        """지난 N일간의 점수 트렌드 데이터 조회

        Args:
            server_id: 서버 ID
            days: 조회할 일수 (기본값: 30일)

        Returns:
            트렌드 데이터 리스트 (날짜, 점수, 통과/실패/전체 수)
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        histories = (
            self.session.query(ScanHistory)
            .filter(
                and_(
                    ScanHistory.server_id == server_id,
                    ScanHistory.scan_time >= cutoff_date,
                )
            )
            .order_by(ScanHistory.scan_time)
            .all()
        )

        return [
            {
                "scan_time": h.scan_time,
                "score": h.score,
                "passed": h.passed,
                "failed": h.failed,
                "manual": h.manual,
                "total": h.total,
            }
            for h in histories
        ]

    def get_latest_scan(self, server_id: int) -> Optional[ScanHistory]:
        """특정 서버의 가장 최근 스캔 이력 조회

        Args:
            server_id: 서버 ID

        Returns:
            ScanHistory 객체 (없으면 None)
        """
        return (
            self.session.query(ScanHistory)
            .filter(ScanHistory.server_id == server_id)
            .order_by(desc(ScanHistory.scan_time))
            .first()
        )

    def delete_old_scans(self, server_id: int, keep_count: int = 10) -> int:
        """오래된 스캔 이력 삭제 (최근 N개만 유지)

        Args:
            server_id: 서버 ID
            keep_count: 유지할 이력 개수 (기본값: 10개)

        Returns:
            삭제된 이력 개수
        """
        # 최근 N개의 ID 조회
        recent_ids = (
            self.session.query(ScanHistory.id)
            .filter(ScanHistory.server_id == server_id)
            .order_by(desc(ScanHistory.scan_time))
            .limit(keep_count)
            .subquery()
        )

        # 최근 N개가 아닌 이력 삭제
        deleted_count = (
            self.session.query(ScanHistory)
            .filter(
                and_(
                    ScanHistory.server_id == server_id,
                    ~ScanHistory.id.in_(recent_ids),
                )
            )
            .delete(synchronize_session=False)
        )

        self.session.commit()
        return deleted_count

    def get_all_history(self, limit: int = 100) -> List[ScanHistory]:
        """모든 서버의 스캔 이력 조회 (최근순)

        Args:
            limit: 조회할 최대 개수 (기본값: 100)

        Returns:
            ScanHistory 객체 리스트 (최신순)
        """
        return (
            self.session.query(ScanHistory)
            .order_by(desc(ScanHistory.scan_time))
            .limit(limit)
            .all()
        )

    def delete_by_id(self, history_id: int) -> bool:
        """특정 스캔 이력 삭제

        Args:
            history_id: 이력 ID

        Returns:
            삭제 성공 여부
        """
        history = self.session.query(ScanHistory).get(history_id)

        if not history:
            return False

        self.session.delete(history)
        self.session.commit()
        return True
