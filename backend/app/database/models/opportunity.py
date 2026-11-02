from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base, utc_now

class OpportunityModel(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(64), ForeignKey("sources.id"), index=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)

    title: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    original_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)

    category: Mapped[str] = mapped_column(String(64), index=True, default="engineering")
    technical_domains: Mapped[list] = mapped_column(JSON, default=list)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list)
    experience_level: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    employment_type: Mapped[str] = mapped_column(String(64), default="remote_contract")
    payment_model: Mapped[str] = mapped_column(String(64), default="not_disclosed")
    hourly_rate_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hourly_rate_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fixed_budget_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fixed_budget_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    payment_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    remote_status: Mapped[str] = mapped_column(String(32), default="remote")
    eligible_countries: Mapped[list] = mapped_column(JSON, default=list)
    egypt_eligibility: Mapped[str] = mapped_column(String(32), index=True, default="unverified")

    payment_methods: Mapped[list] = mapped_column(JSON, default=list)
    application_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assessment_required: Mapped[bool] = mapped_column(Boolean, default=False)

    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    freshness_status: Mapped[str] = mapped_column(String(32), index=True, default="unknown_date")
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)

    listing_status: Mapped[str] = mapped_column(String(32), index=True, default="active")
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified")

    skill_match_score: Mapped[float] = mapped_column(Float, default=0.0)
    eligibility_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, index=True, default=0.0)

    seniority_compatibility: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    seniority_mismatch_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cv_match_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)

    match_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(64), default="Low Match")

    duplicate_group_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    raw_data_reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    risk_level: Mapped[str] = mapped_column(String(32), default="low")
    risk_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    source = relationship("SourceModel", back_populates="opportunities")

    __table_args__ = (
        Index("idx_opp_score_eligibility", "overall_score", "egypt_eligibility"),
    )

