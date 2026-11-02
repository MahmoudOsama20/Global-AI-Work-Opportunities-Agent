from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base, utc_now

class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    official_website: Mapped[str] = mapped_column(String(512), nullable=False)
    careers_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    api_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    collection_method: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, default="verified")
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_account_inspection: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_egypt: Mapped[str] = mapped_column(String(32), default="unknown")
    payment_methods: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    last_health_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    opportunities = relationship("OpportunityModel", back_populates="source", cascade="all, delete-orphan")

