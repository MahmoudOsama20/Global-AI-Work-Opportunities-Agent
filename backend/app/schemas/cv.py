from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CVSkillEvidence(BaseModel):
    skill_name: str
    normalized_name: str
    evidence_source: str = Field("skills_list", description="project, employment, skills_list, inferred")
    context_snippet: Optional[str] = None
    associated_project: Optional[str] = None
    confidence: float = Field(0.7, ge=0.0, le=1.0)


class CVProject(BaseModel):
    title: str
    domain: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    description: str = ""
    metrics: Optional[str] = None
    responsibilities: Optional[str] = None


class CVExperience(BaseModel):
    title: str
    company: Optional[str] = None
    duration: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class CVEducation(BaseModel):
    degree: str
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None


class CVCertification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[str] = None


class CVProfileBase(BaseModel):
    filename: str
    file_type: str = "pdf"
    file_size_bytes: int = 0
    professional_headline: Optional[str] = None
    career_summary: Optional[str] = None
    years_of_experience: Optional[float] = None
    seniority_level: str = "intermediate"
    has_leadership_experience: bool = False

    technical_skills: List[str] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list)
    skill_evidence: List[CVSkillEvidence] = Field(default_factory=list)

    projects: List[CVProject] = Field(default_factory=list)
    employment_history: List[CVExperience] = Field(default_factory=list)
    education: List[CVEducation] = Field(default_factory=list)
    certifications: List[CVCertification] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    extraction_confidence: float = Field(0.0, ge=0.0, le=100.0)
    approved: bool = False
    version: int = 1


class CVProfileUpdate(BaseModel):
    professional_headline: Optional[str] = None
    career_summary: Optional[str] = None
    years_of_experience: Optional[float] = None
    seniority_level: Optional[str] = None
    has_leadership_experience: Optional[bool] = None
    technical_skills: Optional[List[str]] = None
    projects: Optional[List[CVProject]] = None
    employment_history: Optional[List[CVExperience]] = None
    approved: Optional[bool] = None


class CVProfileRead(CVProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime
