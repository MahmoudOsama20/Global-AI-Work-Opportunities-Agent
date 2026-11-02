import pytest
from app.core.config import config_manager, settings

def test_profile_config_loaded():
    profile = config_manager.get_profile()
    assert profile is not None
    assert "domains" in profile
    assert "large_language_models" in profile["domains"]
    assert "computer_vision" in profile["domains"]
    assert profile["primary_location"]["country"] == "Egypt"


def test_sources_config_loaded():
    sources = config_manager.get_sources()
    assert isinstance(sources, list)
    assert len(sources) >= 5
    source_ids = [s["id"] for s in sources]
    assert "outlier" in source_ids
    assert "remotive" in source_ids
    assert "oneforma" in source_ids


def test_scoring_config_loaded():
    scoring = config_manager.get_scoring()
    assert "weights" in scoring
    weights = scoring["weights"]
    assert sum(weights.values()) == 100
    assert scoring["thresholds"]["excellent"] == 90


def test_exclusions_config_loaded():
    exclusions = config_manager.get_exclusions()
    assert "speech_and_audio" in exclusions
    assert "transcription" in exclusions["speech_and_audio"]["keywords"]
    assert "automation_as_job_category" in exclusions
    assert "rpa" in exclusions["automation_as_job_category"]["keywords"]
