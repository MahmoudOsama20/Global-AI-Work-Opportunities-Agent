from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models.source import SourceModel
from app.schemas.source import SourceCreate, SourceUpdate

class SourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, source_id: str) -> Optional[SourceModel]:
        stmt = select(SourceModel).where(SourceModel.id == source_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, enabled_only: bool = False) -> List[SourceModel]:
        stmt = select(SourceModel)
        if enabled_only:
            stmt = stmt.where(SourceModel.enabled.is_(True))
        stmt = stmt.order_by(SourceModel.category, SourceModel.name)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def upsert(self, source_in: SourceCreate) -> SourceModel:
        existing = self.get_by_id(source_in.id)
        now = datetime.now(timezone.utc)
        if existing:
            for field, val in source_in.model_dump(exclude={"id"}).items():
                setattr(existing, field, val)
            existing.updated_at = now
            self.session.flush()
            return existing
        else:
            model = SourceModel(**source_in.model_dump())
            model.created_at = now
            model.updated_at = now
            self.session.add(model)
            self.session.flush()
            return model

    def update(self, source_id: str, update_in: SourceUpdate) -> Optional[SourceModel]:
        existing = self.get_by_id(source_id)
        if not existing:
            return None
        data = update_in.model_dump(exclude_unset=True)
        for field, val in data.items():
            setattr(existing, field, val)
        existing.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return existing

    def record_health_check(self, source_id: str, is_healthy: bool):
        source = self.get_by_id(source_id)
        if source:
            source.last_health_check_at = datetime.now(timezone.utc)
            if is_healthy:
                source.last_success_at = datetime.now(timezone.utc)
                source.consecutive_failures = 0
            else:
                source.consecutive_failures += 1
                if source.consecutive_failures >= 3 and source.status == "verified":
                    source.status = "broken"
            self.session.flush()
