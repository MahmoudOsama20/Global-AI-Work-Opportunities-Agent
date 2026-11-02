import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import app_logger
from app.schemas.connector import ConnectorResult, HealthCheckResult
from app.intelligence.normalizer import OpportunityNormalizer

class BaseConnector(ABC):
    """Abstract Base Class for all opportunity connectors."""

    source_id: str
    source_name: str
    category: str
    supports_egypt: str = "unknown"
    official_website: str = ""

    def __init__(self):
        self.normalizer = OpportunityNormalizer()
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/json, application/xml, text/html, */*",
        }

    @abstractmethod
    def health_check(self) -> HealthCheckResult:
        """Verifies external availability of source endpoint."""
        pass

    @abstractmethod
    def collect(self, limit: Optional[int] = None) -> ConnectorResult:
        """Fetches raw items, processes them through the normalizer, and returns ConnectorResult."""
        pass

    def _safe_http_get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Helper for resilient, synchronous rate-limited HTTP GET requests."""
        merged_headers = {**self.headers, **(headers or {})}
        timeout_val = timeout or float(settings.REQUEST_TIMEOUT_SECONDS)
        with httpx.Client(timeout=timeout_val, follow_redirects=True) as client:
            return client.get(url, params=params, headers=merged_headers)
