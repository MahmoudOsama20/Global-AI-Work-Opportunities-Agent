from datetime import datetime, timezone, timedelta
import pytest
from app.intelligence.freshness import (
    parse_timestamp,
    parse_relative_date,
    calculate_freshness,
    is_within_window,
    human_readable_freshness,
    to_cairo_time,
    FreshnessStatus,
)

def test_parse_iso_timestamp():
    dt = parse_timestamp("2026-11-02T10:00:00Z")
    assert dt is not None
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2026
    assert dt.month == 11
    assert dt.day == 2
    assert dt.hour == 10

def test_parse_iso_with_offset():
    dt = parse_timestamp("2026-11-02T12:00:00+02:00")
    assert dt is not None
    assert dt.tzinfo == timezone.utc
    assert dt.hour == 10  # 12:00 +02:00 is 10:00 UTC

def test_parse_rfc2822_timestamp():
    dt = parse_timestamp("Mon, 02 Nov 2026 14:30:00 GMT")
    assert dt is not None
    assert dt.tzinfo == timezone.utc
    assert dt.hour == 14
    assert dt.minute == 30

def test_parse_epoch_timestamp_seconds():
    epoch = 1730548800
    dt = parse_timestamp(epoch)
    assert dt is not None
    assert dt.tzinfo == timezone.utc

def test_parse_epoch_timestamp_milliseconds():
    epoch_ms = 1730548800000
    dt = parse_timestamp(epoch_ms)
    assert dt is not None
    assert dt.tzinfo == timezone.utc

def test_parse_relative_strings():
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    dt_hours = parse_relative_date("3 hours ago", now=now)
    assert dt_hours == now - timedelta(hours=3)

    dt_days = parse_relative_date("4 days ago", now=now)
    assert dt_days == now - timedelta(days=4)

    dt_yesterday = parse_relative_date("yesterday", now=now)
    assert dt_yesterday == now - timedelta(days=1)

    dt_now = parse_relative_date("just now", now=now)
    assert dt_now == now

def test_freshness_scores_and_statuses():
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)

    # Within 6 hours
    p_6h = now - timedelta(hours=3)
    status, score = calculate_freshness(p_6h, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 100.0

    # Within 24 hours
    p_24h = now - timedelta(hours=18)
    status, score = calculate_freshness(p_24h, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 95.0

    # Within 3 days (72 hours)
    p_3d = now - timedelta(hours=60)
    status, score = calculate_freshness(p_3d, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 85.0

    # Within 4 days (96 hours)
    p_4d = now - timedelta(hours=80)
    status, score = calculate_freshness(p_4d, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 80.0

    # Within 7 days
    p_7d = now - timedelta(days=6)
    status, score = calculate_freshness(p_7d, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 65.0

    # Within 30 days
    p_30d = now - timedelta(days=20)
    status, score = calculate_freshness(p_30d, now=now)
    assert status == FreshnessStatus.FRESH_VERIFIED
    assert score == 40.0

    # Older than 30 days -> Stale
    p_stale = now - timedelta(days=45)
    status, score = calculate_freshness(p_stale, now=now)
    assert status == FreshnessStatus.STALE
    assert score == 15.0

    # Unknown date -> Unknown
    status, score = calculate_freshness(None, now=now)
    assert status == FreshnessStatus.UNKNOWN_DATE
    assert score == 0.0

def test_relative_date_freshness_status():
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    p_rel = now - timedelta(hours=5)
    status, score = calculate_freshness(p_rel, is_relative=True, now=now)
    assert status == FreshnessStatus.FRESH_RELATIVE_DATE
    assert score == 100.0

def test_rolling_window_evaluator():
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    p_2h = now - timedelta(hours=2)
    p_10h = now - timedelta(hours=10)
    p_2d = now - timedelta(days=2)
    p_5d = now - timedelta(days=5)
    p_20d = now - timedelta(days=20)

    # 6h window
    assert is_within_window(p_2h, "6h", now=now) is True
    assert is_within_window(p_10h, "6h", now=now) is False

    # 12h window
    assert is_within_window(p_10h, "12h", now=now) is True
    assert is_within_window(p_2d, "12h", now=now) is False

    # 24h window
    assert is_within_window(p_10h, "24h", now=now) is True
    assert is_within_window(p_2d, "24h", now=now) is False

    # 3d window
    assert is_within_window(p_2d, "3d", now=now) is True
    assert is_within_window(p_5d, "3d", now=now) is False

    # 7d window (default)
    assert is_within_window(p_5d, "7d", now=now) is True
    assert is_within_window(p_20d, "7d", now=now) is False

    # Custom window
    from_dt = now - timedelta(days=6)
    to_dt = now - timedelta(days=3)
    assert is_within_window(p_5d, "custom", posted_from=from_dt, posted_to=to_dt, now=now) is True
    assert is_within_window(p_2h, "custom", posted_from=from_dt, posted_to=to_dt, now=now) is False

def test_human_readable_freshness_strings():
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    assert human_readable_freshness(None) == "Date Unknown"
    assert human_readable_freshness(now - timedelta(minutes=15), now=now) == "15 mins ago"
    assert human_readable_freshness(now - timedelta(hours=4), now=now) == "4 hours ago"
    assert human_readable_freshness(now - timedelta(days=3), now=now) == "3 days ago"

