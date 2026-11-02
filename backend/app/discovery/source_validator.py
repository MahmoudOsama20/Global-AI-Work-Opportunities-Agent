from urllib.parse import urlparse
import httpx
from typing import Dict, Any
from app.core.config import settings
from app.core.logging import app_logger

class SourceValidator:
    """Validates candidate platforms for legitimacy, country coverage, and paid AI roles."""

    KNOWN_EXCLUDED_DOMAINS = {
        "google.com", "bing.com", "yahoo.com", "duckduckgo.com",
        "youtube.com", "facebook.com", "twitter.com", "x.com",
        "reddit.com", "medium.com", "wikipedia.org", "quora.com",
    }

    def validate_candidate(self, url: str, snippet: str = "") -> Dict[str, Any]:
        """
        Validates whether a candidate URL is a legitimate source of paid AI work.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
        except Exception:
            return {"is_valid": False, "status": "broken", "reason": "Malformed URL"}

        if not domain or domain in self.KNOWN_EXCLUDED_DOMAINS:
            return {"is_valid": False, "status": "unsupported", "reason": "General content/search domain"}

        legitimacy_score = 50.0
        status = "candidate"
        notes = []

        # Check HTTPS
        if parsed.scheme == "https":
            legitimacy_score += 10.0
            notes.append("HTTPS verified")

        # Inspect snippet keywords
        text = snippet.lower()
        if any(term in text for term in ["career", "job", "hire", "hiring", "talent", "contractor", "platform"]):
            legitimacy_score += 15.0
            notes.append("Hiring markers in snippet")
        if any(term in text for term in ["ai", "evaluation", "annotation", "llm", "vision", "model"]):
            legitimacy_score += 15.0
            notes.append("AI domain relevance confirmed")
        if any(term in text for term in ["worldwide", "global", "remote"]):
            legitimacy_score += 10.0
            notes.append("Global remote capability indicated")

        # Check domain responsiveness if needed
        try:
            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                resp = client.head(f"{parsed.scheme}://{domain}", headers={"User-Agent": settings.USER_AGENT})
                if resp.status_code < 400:
                    legitimacy_score += 10.0
                    notes.append("Domain active and responsive")
                else:
                    status = "broken"
        except Exception:
            # Network failure or unreachable
            status = "unverified"
            notes.append("Could not connect directly via HTTP")

        if legitimacy_score >= 80.0:
            status = "candidate"

        return {
            "domain": domain,
            "platform_name": domain.split(".")[0].capitalize(),
            "source_url": f"{parsed.scheme}://{domain}",
            "legitimacy_score": min(100.0, legitimacy_score),
            "status": status,
            "notes": " | ".join(notes),
            "is_valid": legitimacy_score >= 50.0 and status != "broken",
        }

