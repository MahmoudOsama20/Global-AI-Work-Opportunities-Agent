from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CollectionRunBase(BaseModel):
    trigger_type: str = "manual_cli"  # manual_cli, manual_ui
    status: str = "running"


class CollectionRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trigger_type: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    sources_attempted: int = 0
    sources_succeeded: int = 0
    sources_failed: int = 0
    total_collected: int = 0
    new_count: int = 0
    duplicate_count: int = 0
    excluded_count: int = 0
    relevant_count: int = 0
    report_html_path: Optional[str] = None
    report_md_path: Optional[str] = None
    summary_json: Optional[Dict[str, Any]] = None


class PipelineProgressEvent(BaseModel):
    run_id: str
    stage: str
    message: str
    progress_percent: float
    current_source: Optional[str] = None
    sources_done: int = 0
    sources_total: int = 0
    collected_count: int = 0
    excluded_count: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
