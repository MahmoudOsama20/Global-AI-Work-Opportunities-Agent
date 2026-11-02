from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.repositories.run_repo import RunRepository
from app.schemas.collection import CollectionRunRead
from app.pipeline.runner import PipelineRunner

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/run", response_model=Dict[str, Any])
def run_pipeline(
    source_id: Optional[str] = None,
    category: Optional[str] = None,
    discover_sources: bool = False,
):
    """Manually triggers a full collection, analysis, and reporting run."""
    runner = PipelineRunner()
    summary = runner.run_manual(
        source_filter=source_id,
        category_filter=category,
        trigger_discovery=discover_sources,
    )
    return summary

@router.get("/runs", response_model=List[CollectionRunRead])
def list_runs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lists audit history of previous search runs."""
    repo = RunRepository(db)
    items = repo.get_recent_runs(limit=limit)
    return [CollectionRunRead.model_validate(item) for item in items]
