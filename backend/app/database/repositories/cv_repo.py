from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.database.models.cv_profile import CVProfileModel

class CVRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, profile_id: str) -> Optional[CVProfileModel]:
        stmt = select(CVProfileModel).where(CVProfileModel.id == profile_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_profile(self) -> Optional[CVProfileModel]:
        """
        Retrieves the active profile.
        Prioritizes approved profiles, otherwise returns the most recently uploaded profile.
        """
        # First check for latest approved profile
        stmt = select(CVProfileModel).where(CVProfileModel.approved == True).order_by(desc(CVProfileModel.updated_at))
        approved = self.session.execute(stmt).scalar_one_or_none()
        if approved:
            return approved

        # Otherwise fallback to the most recent upload
        stmt_recent = select(CVProfileModel).order_by(desc(CVProfileModel.uploaded_at))
        return self.session.execute(stmt_recent).scalar_one_or_none()

    def save_profile(self, data: Dict[str, Any]) -> CVProfileModel:
        now = datetime.now(timezone.utc)
        profile = CVProfileModel(
            id=data["id"],
            filename=data["filename"],
            file_type=data["file_type"],
            file_size_bytes=data.get("file_size_bytes", 0),
            uploaded_at=now,
            raw_text=data["raw_text"],
            professional_headline=data.get("professional_headline"),
            career_summary=data.get("career_summary"),
            years_of_experience=data.get("years_of_experience"),
            seniority_level=data.get("seniority_level", "intermediate"),
            has_leadership_experience=data.get("has_leadership_experience", False),
            technical_skills=data.get("technical_skills", []),
            normalized_skills=data.get("normalized_skills", []),
            skill_evidence=data.get("skill_evidence", []),
            projects=data.get("projects", []),
            employment_history=data.get("employment_history", []),
            education=data.get("education", []),
            certifications=data.get("certifications", []),
            languages=data.get("languages", []),
            extraction_confidence=data.get("extraction_confidence", 0.0),
            approved=data.get("approved", False),
            version=data.get("version", 1),
            created_at=now,
            updated_at=now,
        )
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Optional[CVProfileModel]:
        profile = self.get_by_id(profile_id)
        if not profile:
            return None

        now = datetime.now(timezone.utc)
        for key, val in updates.items():
            if hasattr(profile, key) and val is not None:
                setattr(profile, key, val)

        profile.updated_at = now
        profile.version += 1
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        profile = self.get_by_id(profile_id)
        if not profile:
            return False
        self.session.delete(profile)
        self.session.commit()
        return True

    def delete_all(self) -> int:
        stmt = select(CVProfileModel)
        items = list(self.session.execute(stmt).scalars().all())
        count = len(items)
        for item in items:
            self.session.delete(item)
        self.session.commit()
        return count
