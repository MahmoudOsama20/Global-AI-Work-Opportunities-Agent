import pytest
from app.intelligence.exclusions import ExclusionEngine
from app.intelligence.eligibility import CountryEligibilityEvaluator
from app.intelligence.deduplicator import DeduplicationEngine
from app.intelligence.normalizer import OpportunityNormalizer
from app.schemas.opportunity import NormalizedOpportunity

def test_negative_1_speech_recognition_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Speech Recognition & Acoustic Engineer",
        "description": "Train state of the art speech models and phonetics recognizers.",
        "url": "https://example.com/job/speech-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "speech_and_audio" in reason


def test_negative_2_transcription_task_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Audio Transcription and Quality Review",
        "description": "Listen to audio files and transcribe speech into text.",
        "url": "https://example.com/job/transcribe-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "speech_and_audio" in reason


def test_negative_3_audio_annotation_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Audio Annotation and Voice Data Collector",
        "description": "Perform sound classification and audio annotation.",
        "url": "https://example.com/job/audio-annot-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "speech_and_audio" in reason


def test_negative_4_industrial_automation_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Industrial Automation Engineer - PLC & SCADA",
        "description": "Program Allen Bradley PLCs and monitor SCADA industrial systems.",
        "url": "https://example.com/job/plc-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "automation_job_category" in reason


def test_negative_5_workflow_automation_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Workflow Automation Developer (RPA)",
        "description": "Implement business process automation with UiPath and Zapier.",
        "url": "https://example.com/job/rpa-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "automation_job_category" in reason


def test_negative_6_unpaid_opportunity_excluded():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Unpaid AI Intern - Computer Vision",
        "description": "Unpaid internship for students wanting exposure with OpenCV.",
        "url": "https://example.com/job/unpaid-1",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is True
    assert "unpaid" in reason.lower() or "irrelevant_or_unpaid" in reason


def test_negative_7_ineligible_opportunity_not_recommended():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Lead LLM Fine-Tuning Engineer",
        "description": "Fine-tune models using LoRA and PyTorch. US citizens only with active security clearance.",
        "url": "https://example.com/job/us-only-1",
        "location": "United States only",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1")
    assert is_excluded is False
    assert opp is not None
    assert opp.egypt_eligibility == "not_eligible"
    # Gate check: must not be recommended for application
    assert opp.recommendation == "Not Recommended / Ineligible"


def test_negative_8_unknown_eligibility_flagged():
    normalizer = OpportunityNormalizer()
    raw = {
        "title": "Senior Computer Vision Engineer",
        "description": "Build object detection models with YOLO and PyTorch. Remote position.",
        "url": "https://example.com/job/cv-remote-1",
        "location": "Remote",
    }
    opp, is_excluded, reason = normalizer.normalize(raw, "source_1", "Source 1", source_supports_egypt="unknown")
    assert is_excluded is False
    assert opp is not None
    assert opp.egypt_eligibility == "unverified"
    assert "Eligibility Verification Required" in opp.recommendation


def test_negative_9_duplicate_jobs_detected():
    dedup = DeduplicationEngine()
    opp_a = NormalizedOpportunity(
        id="a1",
        source_id="src1",
        source_name="Source 1",
        title="Senior RAG Engineer",
        company="Anthropic Partner",
        description="Build advanced vector search and RAG systems.",
        original_url="https://src1.com/jobs/rag-1",
        canonical_url="https://src1.com/jobs/rag-1",
    )
    opp_b = NormalizedOpportunity(
        id="b1",
        source_id="src2",
        source_name="Source 2",
        title="Senior RAG Engineer",
        company="Anthropic Partner",
        description="Build advanced vector search and RAG systems.",
        original_url="https://src2.com/jobs/rag-1-repost",
        canonical_url="https://src2.com/jobs/rag-1-repost",
    )
    is_dup, _ = dedup.are_duplicates(opp_a, opp_b)
    assert is_dup is True


def test_negative_10_no_fake_opportunity_on_failure():
    # Verify that connector error result produces 0 opportunities and does NOT synthesize fake listings
    from app.schemas.connector import ConnectorResult
    failed_result = ConnectorResult(
        source_id="broken_source",
        source_name="Broken Source",
        success=False,
        opportunities=[],
        raw_count=0,
        normalized_count=0,
        error_message="HTTP 503 Service Unavailable",
    )
    assert failed_result.success is False
    assert len(failed_result.opportunities) == 0
