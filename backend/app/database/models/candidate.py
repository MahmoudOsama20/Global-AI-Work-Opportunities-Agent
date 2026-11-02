from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, JSON, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.models.base import Base, utc_now

class SourceCandidateModel(Base):
    __tablename__ = "source_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    platform_name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    discovered_via_query: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, approved, rejected, unsupported
    legitimacy_score: Mapped[float] = mapped_column(Float, default=0.0)
    supports_egypt: Mapped[Optional[str]] = mapped_column(String(32), default="unknown")
    payment_models_found: Mapped[list] = mapped_column(JSON, default=list)
    detection_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class DuplicateGroupModel(Base):
    __tablename__ = "duplicate_groups"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    canonical_opportunity_id: Mapped[str] = mapped_column(String(64), ForeignKey("opportunities.id"), nullable=False)
    merged_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
