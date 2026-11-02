import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.database.repositories.source_repo import SourceRepository
from app.database.repositories.opportunity_repo import OpportunityRepository
from app.database.repositories.run_repo import RunRepository
from app.schemas.source import SourceCreate
from app.schemas.opportunity import NormalizedOpportunity

@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_source_repository_crud(test_session):
    repo = SourceRepository(test_session)
    source_in = SourceCreate(
        id="test_source",
        name="Test Platform",
        category="ai_training_and_evaluation",
        official_website="https://test.ai",
        collection_method="public_web",
        supports_egypt="verified",
    )
    created = repo.upsert(source_in)
    test_session.commit()
    assert created.id == "test_source"

    fetched = repo.get_by_id("test_source")
    assert fetched is not None
    assert fetched.name == "Test Platform"

    all_sources = repo.get_all(enabled_only=True)
    assert len(all_sources) == 1


def test_opportunity_repository_upsert_and_dedup(test_session):
    # First create source
    source_repo = SourceRepository(test_session)
    source_repo.upsert(SourceCreate(
        id="outlier",
        name="Outlier AI",
        category="ai_training_and_evaluation",
        official_website="https://outlier.ai",
    ))
    test_session.commit()

    opp_repo = OpportunityRepository(test_session)
    opp = NormalizedOpportunity(
        id="test_opp_1",
        source_id="outlier",
        source_name="Outlier AI",
        source_type="ai_training_and_evaluation",
        title="AI Evaluation Specialist - Computer Vision",
        company="Outlier",
        description="Evaluate vision models and multimodal outputs.",
        original_url="https://outlier.ai/jobs/123",
        canonical_url="https://outlier.ai/jobs/123",
        egypt_eligibility="likely_eligible",
        overall_score=85.0,
        recommendation="Strong Match",
    )
    
    model, is_new = opp_repo.upsert(opp)
    test_session.commit()
    assert is_new is True
    assert model.overall_score == 85.0

    # Upsert same opportunity with updated score
    opp.overall_score = 92.0
    opp.recommendation = "Excellent Match"
    model2, is_new2 = opp_repo.upsert(opp)
    test_session.commit()
    assert is_new2 is False
    assert model2.overall_score == 92.0

    # Test metrics
    metrics = opp_repo.get_metrics_summary()
    assert metrics["total_opportunities"] == 1
    assert metrics["excellent_matches"] == 1
    assert metrics["eligible_in_egypt"] == 1


def test_run_repository_lifecycle(test_session):
    run_repo = RunRepository(test_session)
    run = run_repo.create_run("run_001", trigger_type="manual_cli")
    test_session.commit()
    assert run.status == "running"

    finished = run_repo.finish_run(
        run_id="run_001",
        status="completed",
        attempted=5,
        succeeded=5,
        failed=0,
        total_collected=20,
        new_count=15,
        duplicate_count=3,
        excluded_count=2,
        relevant_count=18,
    )
    test_session.commit()
    assert finished.status == "completed"
    assert finished.total_collected == 20
    assert finished.new_count == 15
