from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.models.base import Base, utc_now

class CollectionRunModel(Base):
    __tablename__ = "collection_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trigger_type: Mapped[str] = mapped_column(String(32), default="manual_cli")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")  # running, completed, failed, partial

    sources_attempted: Mapped[int] = mapped_column(Integer, default=0)
    sources_succeeded: Mapped[int] = mapped_column(Integer, default=0)
    sources_failed: Mapped[int] = mapped_column(Integer, default=0)

    total_collected: Mapped[int] = mapped_column(Integer, default=0)
    new_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    excluded_count: Mapped[int] = mapped_column(Integer, default=0)
    relevant_count: Mapped[int] = mapped_column(Integer, default=0)

    report_html_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    report_md_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    summary_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
