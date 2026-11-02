from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.opportunity import NormalizedOpportunity

class HealthCheckResult(BaseModel):
    source_id: str
    is_healthy: bool
    status_code: Optional[int] = None
    response_time_ms: float = 0.0
    message: str = "OK"
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class ConnectorResult(BaseModel):
    source_id: str
    source_name: str
    success: bool
    opportunities: List[NormalizedOpportunity] = Field(default_factory=list)
    raw_count: int = 0
    normalized_count: int = 0
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    telemetry: Dict[str, Any] = Field(default_factory=dict)
