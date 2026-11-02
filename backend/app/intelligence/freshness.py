from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any
import re
from email.utils import parsedate_to_datetime
try:
    import zoneinfo
    CAIRO_TZ = zoneinfo.ZoneInfo("Africa/Cairo")
except Exception:
    CAIRO_TZ = timezone(timedelta(hours=2), name="EET")

class FreshnessStatus:
    FRESH_VERIFIED = "fresh_verified"
    FRESH_RELATIVE_DATE = "fresh_relative"
    UPDATED_RECENTLY = "updated_recently"
    STALE = "stale"
    UNKNOWN_DATE = "unknown_date"
    EXPIRED = "expired"


def parse_timestamp(val: Any) -> Optional[datetime]:
    """
    Parses various date/timestamp formats into a timezone-aware UTC datetime.
    Supports:
    - datetime objects (naive assumed UTC, or converted to UTC)
    - ISO 8601 strings (e.g. 2026-11-02T10:00:00Z, 2026-11-01)
    - RFC 2822 / RSS pubDate strings (e.g. Mon, 02 Nov 2026 12:00:00 GMT)
    - Unix epoch timestamps (seconds or milliseconds)
    - Relative date strings (e.g. '3 hours ago', 'yesterday', '4d ago', 'just now')
    """
    if val is None:
        return None

    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    # Numeric timestamp (int or float)
    if isinstance(val, (int, float)):
        # Milliseconds if > 1e11
        if val > 1e11:
            val = val / 1000.0
        try:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        except Exception:
            return None

    if not isinstance(val, str):
        return None

    val_str = val.strip()
    if not val_str:
        return None

    # Check for numeric string (e.g. "1730548800")
    if val_str.isdigit():
        try:
            num = float(val_str)
            if num > 1e11:
                num = num / 1000.0
            return datetime.fromtimestamp(num, tz=timezone.utc)
        except Exception:
            pass

    # Check for relative strings (e.g. "2 hours ago", "yesterday", "3d ago")
    relative_dt = parse_relative_date(val_str)
    if relative_dt is not None:
        return relative_dt

    # Try RFC 2822 (common in RSS feeds)
    try:
        dt = parsedate_to_datetime(val_str)
        if dt is not None:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
    except Exception:
        pass

    # Try ISO 8601 format variants
    # Clean trailing 'Z' if present for standard fromisoformat
    iso_candidate = val_str
    if iso_candidate.endswith("Z"):
        iso_candidate = iso_candidate[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(iso_candidate)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    # Common date formats
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]:
        try:
            dt = datetime.strptime(val_str, fmt)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue

    return None


def parse_relative_date(text: str, now: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parses expressions like '3 hours ago', '10m ago', 'yesterday', '4 days ago'.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    text_lower = text.strip().lower()
    if text_lower in ["just now", "moments ago", "today"]:
        return now

    if text_lower == "yesterday":
        return now - timedelta(days=1)

    # Patterns like "X hour(s) ago", "X h ago", "X mins ago"
    match = re.search(
        r"(\d+)\s*(m|min|minute|minutes|h|hr|hour|hours|d|day|days|w|wk|week|weeks|mo|month|months)\s*(?:ago)?\b",
        text_lower,
    )
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit in ["m", "min", "minute", "minutes"]:
            return now - timedelta(minutes=amount)
        elif unit in ["h", "hr", "hour", "hours"]:
            return now - timedelta(hours=amount)
        elif unit in ["d", "day", "days"]:
            return now - timedelta(days=amount)
        elif unit in ["w", "wk", "week", "weeks"]:
            return now - timedelta(weeks=amount)
        elif unit in ["mo", "month", "months"]:
            return now - timedelta(days=amount * 30)

    return None


def calculate_freshness(
    posted_at: Optional[datetime],
    updated_at: Optional[datetime] = None,
    is_relative: bool = False,
    now: Optional[datetime] = None,
) -> Tuple[str, float]:
    """
    Returns (freshness_status, freshness_score).
    Freshness score is between 0.0 and 100.0:
    - <= 6 hours: 100.0
    - <= 24 hours: 95.0
    - <= 3 days (72h): 85.0
    - <= 4 days (96h): 80.0
    - <= 7 days (168h): 65.0
    - <= 30 days (720h): 40.0
    - > 30 days: 15.0
    - Unknown date: 0.0
    """
    if now is None:
        now = datetime.now(timezone.utc)

    if posted_at is None:
        # Check if updated_at is recent
        if updated_at is not None:
            age_hours = (now - updated_at).total_seconds() / 3600.0
            if age_hours <= 168.0:
                return FreshnessStatus.UPDATED_RECENTLY, 50.0
        return FreshnessStatus.UNKNOWN_DATE, 0.0

    age_seconds = (now - posted_at).total_seconds()
    age_hours = max(0.0, age_seconds / 3600.0)

    # Status classification
    if age_hours <= 168.0:  # <= 7 days
        status = FreshnessStatus.FRESH_RELATIVE_DATE if is_relative else FreshnessStatus.FRESH_VERIFIED
    elif age_hours <= 720.0:  # <= 30 days
        status = FreshnessStatus.FRESH_VERIFIED
    else:
        status = FreshnessStatus.STALE

    # Score calculation
    if age_hours <= 6.0:
        score = 100.0
    elif age_hours <= 24.0:
        score = 95.0
    elif age_hours <= 72.0:  # 3 days
        score = 85.0
    elif age_hours <= 96.0:  # 4 days
        score = 80.0
    elif age_hours <= 168.0:  # 7 days
        score = 65.0
    elif age_hours <= 720.0:  # 30 days
        score = 40.0
    else:
        score = 15.0

    return status, score


def is_within_window(
    posted_at: Optional[datetime],
    window: str = "7d",
    posted_from: Optional[datetime] = None,
    posted_to: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> bool:
    """
    Evaluates whether posted_at falls within the designated rolling or custom window.
    Supported windows:
    - '6h': published within rolling 6 hours
    - '12h': published within rolling 12 hours
    - '24h': published within rolling 24 hours
    - '3d': published within rolling 72 hours
    - '4d': published within rolling 96 hours
    - '7d': published within rolling 7 days (default)
    - '30d': published within rolling 30 days
    - 'custom': posted_from <= posted_at <= posted_to
    - 'all': includes all records (even unknown date if explicitly allowed)
    """
    if window == "all":
        return True

    if posted_at is None:
        return False

    if now is None:
        now = datetime.now(timezone.utc)

    window_lower = window.strip().lower()

    if window_lower == "6h":
        return posted_at >= (now - timedelta(hours=6))
    elif window_lower == "12h":
        return posted_at >= (now - timedelta(hours=12))
    elif window_lower == "24h":
        return posted_at >= (now - timedelta(hours=24))
    elif window_lower == "3d":
        return posted_at >= (now - timedelta(days=3))
    elif window_lower == "4d":
        return posted_at >= (now - timedelta(days=4))
    elif window_lower == "7d":
        return posted_at >= (now - timedelta(days=7))
    elif window_lower == "30d":
        return posted_at >= (now - timedelta(days=30))
    elif window_lower == "custom":
        if posted_from and posted_at < posted_from:
            return False
        if posted_to and posted_at > posted_to:
            return False
        return True

    # Default to 7 days if unrecognized window
    return posted_at >= (now - timedelta(days=7))


def to_cairo_time(dt: Optional[datetime]) -> str:
    """
    Formats a UTC datetime in Africa/Cairo timezone.
    """
    if dt is None:
        return "Unknown Date"
    cairo_dt = dt.astimezone(CAIRO_TZ)
    return cairo_dt.strftime("%Y-%m-%d %H:%M %Z")


def human_readable_freshness(posted_at: Optional[datetime], now: Optional[datetime] = None) -> str:
    """
    Produces a human-friendly freshness string (e.g. '3 hours ago', '2 days ago', 'Date Unknown').
    """
    if posted_at is None:
        return "Date Unknown"

    if now is None:
        now = datetime.now(timezone.utc)

    diff = now - posted_at
    seconds = diff.total_seconds()

    if seconds < 0:
        return "Just now"
    if seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins} min{'s' if mins != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return to_cairo_time(posted_at)
