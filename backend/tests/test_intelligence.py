import pytest
from app.intelligence.exclusions import ExclusionEngine
from app.intelligence.classifier import DomainClassifier
from app.intelligence.skill_extractor import SkillExtractor
from app.intelligence.payment_parser import PaymentParser
from app.intelligence.eligibility import CountryEligibilityEvaluator
from app.intelligence.deduplicator import DeduplicationEngine
from app.intelligence.matcher import MatchingEngine
from app.intelligence.normalizer import OpportunityNormalizer
from app.schemas.opportunity import NormalizedOpportunity

def test_exclusion_engine_speech():
    engine = ExclusionEngine()
    excluded, cat, reason = engine.evaluate(
        "Speech Recognition Specialist",
        "We are building a Whisper-based ASR pipeline."
    )
    assert excluded is True
    assert cat == "speech_and_audio"


def test_exclusion_engine_audio_transcription():
    engine = ExclusionEngine()
    excluded, cat, reason = engine.evaluate(
        "Audio Transcription and Labeling",
        "Transcribe audio clips and tag accents."
    )
    assert excluded is True
    assert cat == "speech_and_audio"


def test_exclusion_engine_automation():
    engine = ExclusionEngine()
    excluded, cat, reason = engine.evaluate(
        "Senior Automation Engineer - RPA & UiPath",
        "Build business process automation workflows using UiPath and Blue Prism."
    )
    assert excluded is True
    assert cat == "automation_job_category"


def test_ai_agent_not_excluded():
    engine = ExclusionEngine()
    # AI Agent engineering must NOT be excluded
    excluded, cat, reason = engine.evaluate(
        "Senior AI Agent Engineer",
        "Develop autonomous multi-agent systems using LangGraph, tool calling, and LLM reasoning."
    )
    assert excluded is False


def test_domain_classifier():
    classifier = DomainClassifier()
    domains = classifier.classify("Build computer vision models for object detection with YOLO and PyTorch.")
    assert "computer_vision" in domains
    assert "deep_learning_and_ml" in domains


def test_payment_parser():
    parser = PaymentParser()
    p1 = parser.parse("Offering $35 - $50 / hr for senior engineer")
    assert p1["payment_model"] == "hourly"
    assert p1["hourly_rate_min"] == 35.0
    assert p1["hourly_rate_max"] == 50.0

    p2 = parser.parse("Fixed price: $1,500 for model fine-tuning")
    assert p2["payment_model"] == "fixed"
    assert p2["fixed_budget_min"] == 1500.0


def test_egypt_eligibility_worldwide():
    evaluator = CountryEligibilityEvaluator()
    res = evaluator.evaluate("Worldwide remote applicants welcome. We hire globally.", location_field="Remote - Global")
    assert res["egypt_eligibility"] == "likely_eligible"
    assert res["payout_compatible"] is True


def test_egypt_eligibility_ineligible():
    evaluator = CountryEligibilityEvaluator()
    res = evaluator.evaluate("Must reside in the US. US work authorization required.", location_field="United States")
    assert res["egypt_eligibility"] == "not_eligible"
    assert res["eligibility_score"] == 0.0


def test_deduplicator():
    dedup = DeduplicationEngine()
    opp1 = NormalizedOpportunity(
        id="opp_1",
        source_id="remotive",
        source_name="Remotive",
        title="Senior LLM Engineer",
        company="Scale AI",
        description="Develop RAG and fine-tuning pipelines.",
        original_url="https://remotive.com/jobs/123",
        canonical_url="https://remotive.com/jobs/123",
        overall_score=85.0,
    )
    opp2 = NormalizedOpportunity(
        id="opp_2",
        source_id="remoteok",
        source_name="Remote OK",
        title="Senior LLM Engineer",
        company="Scale AI",
        description="Develop RAG and fine-tuning pipelines.",
        original_url="https://remoteok.com/l/456",
        canonical_url="https://remoteok.com/l/456",
        overall_score=87.0,
    )
    is_dup, reason = dedup.are_duplicates(opp1, opp2)
    assert is_dup is True
    assert "Scale AI" in reason

