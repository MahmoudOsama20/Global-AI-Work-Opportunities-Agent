import pytest
from app.core.security import sanitize_log_message, canonicalize_url

def test_sanitize_log_message():
    raw = "Request failed with api_key=secret_123456 and token: abcdefgh"
    sanitized = sanitize_log_message(raw)
    assert "secret_123456" not in sanitized
    assert "abcdefgh" not in sanitized
    assert "***REDACTED***" in sanitized


def test_canonicalize_url():
    url_with_tracking = "https://boards.greenhouse.io/outlierai/jobs/12345?utm_source=linkedin&utm_medium=cpc&ref=affiliate#apply"
    canonical = canonicalize_url(url_with_tracking)
    assert canonical == "https://boards.greenhouse.io/outlierai/jobs/12345"
    assert "utm_source" not in canonical
    assert "#apply" not in canonical

    # Trailing slash normalization
    url2 = "https://example.com/jobs/ai-engineer/"
    assert canonicalize_url(url2) == "https://example.com/jobs/ai-engineer"

