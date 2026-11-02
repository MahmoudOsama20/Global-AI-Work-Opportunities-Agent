import pytest
from app.database.session import SessionLocal, init_db
from app.api.routes.opportunities import list_opportunities, get_metrics
from app.api.routes.sources import list_sources
from app.api.routes.profile import get_profile
from app.api.routes.discovery import list_candidates
from app.api.routes.reports import list_reports
from app.api.routes.pipeline import list_runs

@pytest.fixture
def db():
    init_db()
    with SessionLocal() as session:
        yield session

def test_api_route_metrics(db):
    metrics = get_metrics(db=db)
    assert "total_opportunities" in metrics
    assert "eligible_in_egypt" in metrics

def test_api_route_opportunities(db):
    res = list_opportunities(limit=10, offset=0, db=db)
    assert "items" in res
    assert "total" in res
    assert res["total"] >= 1

def test_api_route_sources(db):
    sources = list_sources(db=db)
    assert len(sources) >= 1
    assert any(s.id == "remotive" for s in sources)

def test_api_route_profile():
    p = get_profile()
    assert p["primary_location"]["country"] == "Egypt"

def test_api_route_candidates():
    candidates = list_candidates()
    assert isinstance(candidates, list)

def test_api_route_reports():
    reports = list_reports()
    assert isinstance(reports, list)
    assert len(reports) >= 1

def test_api_route_runs(db):
    runs = list_runs(limit=10, db=db)
    assert isinstance(runs, list)
    assert len(runs) >= 1
