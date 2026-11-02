import pytest
from unittest.mock import patch, MagicMock
from app.connectors.job_boards.remotive import RemotiveConnector
from app.connectors.job_boards.remoteok import RemoteOKConnector
from app.connectors.job_boards.himalayas import HimalayasConnector
from app.connectors.job_boards.wwr import WeWorkRemotelyConnector
from app.connectors.outlier.public_outlier import OutlierPublicConnector
from app.connectors.evaluation.alignerr import AlignerrPublicConnector
from app.connectors.registry import connector_registry

def test_registry_contains_default_connectors():
    connectors = connector_registry.get_all()
    source_ids = [c.source_id for c in connectors]
    assert "remotive" in source_ids
    assert "remoteok" in source_ids
    assert "himalayas" in source_ids
    assert "weworkremotely" in source_ids
    assert "outlier" in source_ids
    assert "alignerr" in source_ids


def test_remotive_connector_collect():
    connector = RemotiveConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jobs": [
            {
                "id": 101,
                "title": "Senior AI Agent Developer",
                "company_name": "Agentic Labs",
                "description": "Develop multi-agent autonomous systems using LangGraph, Python, and FastAPI.",
                "url": "https://remotive.com/jobs/101",
                "candidate_required_location": "Worldwide",
                "salary": "$40 - $60 / hr",
            }
        ]
    }

    with patch.object(connector, "_safe_http_get", return_value=mock_response):
        result = connector.collect()
        assert result.success is True
        assert result.raw_count == 1
        assert len(result.opportunities) == 1
        opp = result.opportunities[0]
        assert opp.title == "Senior AI Agent Developer"
        assert opp.source_id == "remotive"
        assert opp.payment_model == "hourly"
        assert opp.hourly_rate_min == 40.0
        assert opp.egypt_eligibility == "likely_eligible"


def test_outlier_public_connector_collect():
    connector = OutlierPublicConnector()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jobs": [
            {
                "id": 555,
                "title": "AI Model Evaluation Specialist - Computer Vision",
                "content": "<p>Evaluate and benchmark state-of-the-art vision models and YOLO detectors. Worldwide contractors welcome.</p>",
                "absolute_url": "https://boards.greenhouse.io/outlierai/jobs/555",
                "location": {"name": "Remote - Worldwide"},
            }
        ]
    }

    with patch.object(connector, "_safe_http_get", return_value=mock_response):
        result = connector.collect()
        assert result.success is True
        assert len(result.opportunities) == 1
        opp = result.opportunities[0]
        assert opp.source_id == "outlier"
        assert "computer_vision" in opp.technical_domains
        assert opp.egypt_eligibility == "likely_eligible"


def test_connector_failure_handling():
    connector = HimalayasConnector()
    with patch.object(connector, "_safe_http_get", side_effect=Exception("Connection timed out")):
        result = connector.collect()
        assert result.success is False
        assert len(result.opportunities) == 0
        assert "Connection timed out" in result.error_message
