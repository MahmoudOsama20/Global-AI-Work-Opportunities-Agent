from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.database.models.collection_run import CollectionRunModel

class RunRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, run_id: str) -> Optional[CollectionRunModel]:
        stmt = select(CollectionRunModel).where(CollectionRunModel.id == run_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_recent_runs(self, limit: int = 20) -> List[CollectionRunModel]:
        stmt = select(CollectionRunModel).order_by(desc(CollectionRunModel.started_at)).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def create_run(self, run_id: str, trigger_type: str = "manual_cli") -> CollectionRunModel:
        model = CollectionRunModel(
            id=run_id,
            trigger_type=trigger_type,
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        self.session.add(model)
        self.session.flush()
        return model

    def finish_run(
        self,
        run_id: str,
        status: str,
        attempted: int,
        succeeded: int,
        failed: int,
        total_collected: int,
        new_count: int,
        duplicate_count: int,
        excluded_count: int,
        relevant_count: int,
        report_html_path: Optional[str] = None,
        report_md_path: Optional[str] = None,
        summary_json: Optional[dict] = None,
    ) -> Optional[CollectionRunModel]:
        run = self.get_by_id(run_id)
        if run:
            run.finished_at = datetime.now(timezone.utc)
            run.status = status
            run.sources_attempted = attempted
            run.sources_succeeded = succeeded
            run.sources_failed = failed
            run.total_collected = total_collected
            run.new_count = new_count
            run.duplicate_count = duplicate_count
            run.excluded_count = excluded_count
            run.relevant_count = relevant_count
            run.report_html_path = report_html_path
            run.report_md_path = report_md_path
            run.summary_json = summary_json
            self.session.flush()
        return run
