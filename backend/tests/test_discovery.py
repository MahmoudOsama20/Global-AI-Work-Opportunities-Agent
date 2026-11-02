import pytest
from app.discovery.query_generator import DiscoveryQueryGenerator
from app.discovery.search_provider import MockSearchProvider
from app.discovery.source_validator import SourceValidator
from app.discovery.source_registry import SourceDiscoveryEngine
from app.database.session import SessionLocal, init_db
from app.database.models.source import SourceModel
from sqlalchemy import delete
from app.database.models.candidate import SourceCandidateModel

def test_query_generator():
    gen = DiscoveryQueryGenerator()
    queries = gen.generate_queries()
    assert len(queries) >= 8
    assert any("ai training" in q.lower() for q in queries)
    assert any("-speech" in q.lower() or "-audio" in q.lower() for q in queries)


def test_source_validator_valid_candidate():
    validator = SourceValidator()
    res = validator.validate_candidate(
        url="https://mercor.com/ai-evaluators",
        snippet="Mercor is hiring worldwide AI model evaluators and LLM engineers."
    )
    assert res["is_valid"] is True
    assert res["domain"] == "mercor.com"
    assert res["legitimacy_score"] >= 70.0


def test_source_validator_excluded_domain():
    validator = SourceValidator()
    res = validator.validate_candidate(
        url="https://www.youtube.com/watch?v=123",
        snippet="Watch how to do AI data entry."
    )
    assert res["is_valid"] is False
    assert res["status"] == "unsupported"


def test_discovery_engine_lifecycle():
    init_db()
    mock_provider = MockSearchProvider([
        {
            "title": "Mercor AI - Elite AI Talent Platform",
            "url": "https://mercor.com",
            "snippet": "Mercor hires global AI engineers, coding evaluators, and LLM trainers worldwide.",
        }
    ])
    engine = SourceDiscoveryEngine(search_provider=mock_provider)
    result = engine.discover_new_sources(max_queries=1)
    assert result["candidates_found"] >= 1

    pending = engine.list_pending_candidates()
    assert any(c["domain"] == "mercor.com" for c in pending)

    candidate = next(c for c in pending if c["domain"] == "mercor.com")
    cand_id = candidate["id"]

    # Test approval
    approved = engine.approve_candidate(cand_id)
    assert approved is True

    # Check that source now exists in sources table
    with SessionLocal() as session:
        promoted_source = session.get(SourceModel, "mercor.com")
        assert promoted_source is not None
        assert promoted_source.name == "Mercor"
        assert promoted_source.status == "verified"


def test_discovery_engine_duplicate_domains_in_results():
    """Verify that multiple search results yielding the same domain do not fail on UNIQUE constraint."""
    init_db()
    test_domain = "unique-test-eval-domain.ai"
    with SessionLocal() as session:
        session.execute(
            delete(SourceCandidateModel).where(SourceCandidateModel.domain == test_domain)
        )
        session.commit()

    mock_provider = MockSearchProvider([
        {
            "title": "AI Training Jobs 1",
            "url": f"https://{test_domain}/page1",
            "snippet": "Worldwide AI model training and evaluation remote jobs.",
        },
        {
            "title": "AI Training Jobs 2",
            "url": f"https://{test_domain}/page2",
            "snippet": "Worldwide AI model training and evaluation remote jobs.",
        },
    ])
    engine = SourceDiscoveryEngine(search_provider=mock_provider)
    result = engine.discover_new_sources(max_queries=2)
    assert result["candidates_found"] >= 2
    assert result["new_sources_registered"] == 1


