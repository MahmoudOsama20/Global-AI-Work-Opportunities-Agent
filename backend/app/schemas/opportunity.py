from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict

class OpportunityBase(BaseModel):
    title: str = Field(..., description="Job or opportunity title")
    company: Optional[str] = Field(None, description="Hiring company or client")
    description: str = Field(..., description="Full text description or job summary")
    original_url: str = Field(..., description="Direct link to source listing")
    canonical_url: Optional[str] = Field(None, description="Normalized canonical link without tracking")

    category: str = Field("engineering", description="High-level category: engineering, evaluation, annotation, research")
    technical_domains: List[str] = Field(default_factory=list, description="Matched AI domains")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = Field(None, description="Junior, Mid, Senior, Lead, Expert")

    employment_type: str = Field("remote_contract", description="freelance, contract, hourly, fixed_price, per_task")
    payment_model: str = Field("not_disclosed", description="hourly, fixed, per_task, milestone, not_disclosed")
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None
    fixed_budget_min: Optional[float] = None
    fixed_budget_max: Optional[float] = None
    currency: str = Field("USD", max_length=8)
    payment_details: Optional[str] = None

    location: Optional[str] = None
    remote_status: str = Field("remote", description="remote, hybrid, onsite")
    eligible_countries: List[str] = Field(default_factory=list)
    egypt_eligibility: str = Field(
        "unverified",
        description="eligible, likely_eligible, unverified, not_eligible, restricted"
    )

    payment_methods: List[str] = Field(default_factory=list)
    application_requirements: Optional[str] = None
    assessment_required: bool = False

    posted_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    freshness_status: str = Field("unknown_date", description="fresh_verified, fresh_relative, updated_recently, stale, unknown_date, expired")
    freshness_score: float = Field(0.0, ge=0.0, le=100.0)

    listing_status: str = Field("active", description="active, expired, removed")
    verification_status: str = Field("unverified", description="verified, unverified, disputed")

    skill_match_score: float = Field(0.0, ge=0.0, le=100.0)
    eligibility_score: float = Field(0.0, ge=0.0, le=100.0)
    overall_score: float = Field(0.0, ge=0.0, le=100.0)

    seniority_compatibility: Optional[str] = None
    seniority_mismatch_reason: Optional[str] = None
    cv_match_breakdown: Dict[str, Any] = Field(default_factory=dict)

    match_explanation: Optional[str] = None
    missing_skills: List[str] = Field(default_factory=list)
    recommendation: str = Field("Low Match")

    duplicate_group_id: Optional[str] = None
    raw_data_reference: Optional[str] = None
    risk_level: str = Field("low", description="low, review, high, scam")
    risk_explanation: Optional[str] = None


class NormalizedOpportunity(OpportunityBase):
    id: str = Field(..., description="Unique deterministic identifier")
    source_id: str = Field(..., description="ID of origin source")
    source_name: str = Field(..., description="Display name of origin source")
    source_type: str = Field("job_board", description="Origin source category")


class OpportunityCreate(NormalizedOpportunity):
    pass


class OpportunityRead(NormalizedOpportunity):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime


class OpportunityFilter(BaseModel):
    category: Optional[str] = None
    domain: Optional[str] = None
    source_id: Optional[str] = None
    egypt_eligibility: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    search_query: Optional[str] = None
    payment_model: Optional[str] = None
    recommendation: Optional[str] = None
    freshness: Optional[str] = None
    posted_from: Optional[datetime] = None
    posted_to: Optional[datetime] = None
    include_unknown_dates: bool = True
    limit: int = 50
    offset: int = 0
