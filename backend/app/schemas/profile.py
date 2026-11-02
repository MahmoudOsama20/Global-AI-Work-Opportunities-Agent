from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PrimaryLocation(BaseModel):
    country: str = "Egypt"
    country_code: str = "EG"
    city: str = "Cairo"
    timezone: str = "Africa/Cairo"
    remote_only: bool = True


class PaymentPreferences(BaseModel):
    currencies: List[str] = Field(default_factory=lambda: ["USD", "EUR", "GBP"])
    supported_methods_in_location: List[str] = Field(
        default_factory=lambda: ["payoneer", "wire_transfer", "bank_transfer", "wise", "paypal", "direct_deposit"]
    )
    minimum_hourly_usd: float = 15.0
    minimum_fixed_project_usd: float = 100.0


class TechnicalDomain(BaseModel):
    name: str
    priority: int
    skills: List[str]


class UserProfile(BaseModel):
    name: str = "Senior AI & Machine Learning Engineer"
    primary_location: PrimaryLocation = Field(default_factory=PrimaryLocation)
    payment_preferences: PaymentPreferences = Field(default_factory=PaymentPreferences)
    priority_order: List[str] = Field(default_factory=list)
    domains: Dict[str, TechnicalDomain] = Field(default_factory=dict)
    languages: List[Dict[str, str]] = Field(default_factory=list)
