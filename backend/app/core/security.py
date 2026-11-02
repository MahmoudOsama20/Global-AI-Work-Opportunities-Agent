import re
from urllib.parse import urlparse, urlunparse

def sanitize_log_message(message: str) -> str:
    """Strips API keys, passwords, and tokens from log messages or exceptions."""
    # Pattern to match key=..., token=..., Bearer ...
    sanitized = re.sub(
        r"(api[-_]?key|token|secret|password|bearer\s+)[:=]\s*['\"]?[\w\-\._]+['\"]?",
        r"\1=***REDACTED***",
        message,
        flags=re.IGNORECASE,
    )
    return sanitized


def canonicalize_url(url: str) -> str:
    """Normalizes listing URLs by stripping tracking parameters, hashes, and trailing slashes."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        # Filter out common tracking query params
        tracking_params = {
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "ref", "source", "gh_src", "fbclid", "gclid", "msclkid"
        }
        
        query_parts = []
        if parsed.query:
            for param in parsed.query.split("&"):
                if "=" in param:
                    key, val = param.split("=", 1)
                    if key.lower() not in tracking_params:
                        query_parts.append(param)
                elif param and param.lower() not in tracking_params:
                    query_parts.append(param)
                    
        cleaned_query = "&".join(query_parts)
        cleaned_path = parsed.path.rstrip("/")
        if not cleaned_path:
            cleaned_path = "/"
            
        canonical = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            cleaned_path,
            parsed.params,
            cleaned_query,
            ""  # drop fragments
        ))
        return canonical
    except Exception:
        return url.strip()
