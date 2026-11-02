from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class SourceBase(BaseModel):
    name: str
    category: str
    official_website: str
    careers_url: Optional[str] = None
    api_url: Optional[str] = None
    collection_method: str = "public_web"  # api, rss, public_web, browser_session
    status: str = "verified"  # verified, candidate, unverified, restricted, broken, deprecated
    requires_auth: bool = False
    supports_account_inspection: bool = False
    supports_egypt: str = "unknown"  # verified, likely, unverified, restricted, ineligible
    payment_methods: List[str] = Field(default_factory=list)
    enabled: bool = True
    description: Optional[str] = None


class SourceCreate(SourceBase):
    id: str


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    official_website: Optional[str] = None
    careers_url: Optional[str] = None
    api_url: Optional[str] = None
    collection_method: Optional[str] = None
    status: Optional[str] = None
    requires_auth: Optional[bool] = None
    supports_account_inspection: Optional[bool] = None
    supports_egypt: Optional[str] = None
    payment_methods: Optional[List[str]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class SourceRead(SourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    last_health_check_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    consecutive_failures: int = 0
    opportunities_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
