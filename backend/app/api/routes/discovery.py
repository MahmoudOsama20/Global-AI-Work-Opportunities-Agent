from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.discovery.source_registry import SourceDiscoveryEngine

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.get("/candidates", response_model=List[Dict[str, Any]])
def list_candidates():
    """Lists newly discovered platforms awaiting human review in the Discovery Center."""
    engine = SourceDiscoveryEngine()
    return engine.list_pending_candidates()

@router.post("/candidates/{candidate_id}/approve", response_model=dict)
def approve_candidate(candidate_id: int):
    """Approves and activates a discovered source."""
    engine = SourceDiscoveryEngine()
    success = engine.approve_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "approved", "candidate_id": candidate_id}

@router.post("/candidates/{candidate_id}/reject", response_model=dict)
def reject_candidate(candidate_id: int):
    """Rejects a candidate source."""
    engine = SourceDiscoveryEngine()
    success = engine.reject_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "rejected", "candidate_id": candidate_id}

@router.post("/run", response_model=dict)
def trigger_discovery(max_queries: int = 3):
    """Triggers the Source Discovery Engine."""
    engine = SourceDiscoveryEngine()
    return engine.discover_new_sources(max_queries=max_queries)
