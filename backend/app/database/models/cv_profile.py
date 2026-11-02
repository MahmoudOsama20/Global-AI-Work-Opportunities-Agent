from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.models.base import Base, utc_now

class CVProfileModel(Base):
    __tablename__ = "cv_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)  # pdf, docx, txt
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    professional_headline: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    career_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    years_of_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seniority_level: Mapped[str] = mapped_column(String(64), default="intermediate")
    has_leadership_experience: Mapped[bool] = mapped_column(Boolean, default=False)

    technical_skills: Mapped[list] = mapped_column(JSON, default=list)
    normalized_skills: Mapped[list] = mapped_column(JSON, default=list)
    skill_evidence: Mapped[list] = mapped_column(JSON, default=list)

    projects: Mapped[list] = mapped_column(JSON, default=list)
    employment_history: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=list)

    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

