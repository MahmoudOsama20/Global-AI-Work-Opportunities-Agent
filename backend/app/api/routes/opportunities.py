from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.repositories.opportunity_repo import OpportunityRepository
from app.schemas.opportunity import OpportunityRead, OpportunityFilter

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

@router.get("", response_model=dict)
def list_opportunities(
    category: Optional[str] = None,
    domain: Optional[str] = None,
    source_id: Optional[str] = None,
    egypt_eligibility: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    search_query: Optional[str] = None,
    payment_model: Optional[str] = None,
    recommendation: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search and filter normalized opportunities."""
    repo = OpportunityRepository(db)
    filters = OpportunityFilter(
        category=category,
        domain=domain,
        source_id=source_id,
        egypt_eligibility=egypt_eligibility,
        min_score=min_score,
        max_score=max_score,
        search_query=search_query,
        payment_model=payment_model,
        recommendation=recommendation,
        limit=limit,
        offset=offset,
    )
    items, total = repo.search(filters)
    return {
        "total": total,
        "items": [OpportunityRead.model_validate(item) for item in items],
        "limit": limit,
        "offset": offset,
    }

@router.get("/metrics", response_model=dict)
def get_metrics(db: Session = Depends(get_db)):
    """Overview metrics for dashboard statistics."""
    repo = OpportunityRepository(db)
    return repo.get_metrics_summary()

@router.get("/{opp_id}", response_model=OpportunityRead)
def get_opportunity(opp_id: str, db: Session = Depends(get_db)):
    """Fetch complete normalized details for an opportunity."""
    repo = OpportunityRepository(db)
    item = repo.get_by_id(opp_id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return OpportunityRead.model_validate(item)
