from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.repositories.source_repo import SourceRepository
from app.schemas.source import SourceRead, SourceUpdate
from app.pipeline.runner import PipelineRunner

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("", response_model=List[SourceRead])
def list_sources(
    enabled_only: bool = False,
    db: Session = Depends(get_db),
):
    """Lists all registered sources and their health statuses."""
    repo = SourceRepository(db)
    items = repo.get_all(enabled_only=enabled_only)
    return [SourceRead.model_validate(item) for item in items]

@router.patch("/{source_id}", response_model=SourceRead)
def update_source(
    source_id: str,
    update_in: SourceUpdate,
    db: Session = Depends(get_db),
):
    """Enables/disables or updates a source configuration."""
    repo = SourceRepository(db)
    updated = repo.update(source_id, update_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Source not found")
    db.commit()
    return SourceRead.model_validate(updated)

@router.post("/health-check", response_model=list)
def trigger_health_check():
    """Runs health checks across all registered sources."""
    runner = PipelineRunner()
    results = runner.health_check_all()
    return [r.model_dump() for r in results]
