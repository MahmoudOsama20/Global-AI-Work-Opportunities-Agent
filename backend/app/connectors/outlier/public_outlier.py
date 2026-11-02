import time
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from app.connectors.base import BaseConnector
from app.schemas.connector import ConnectorResult, HealthCheckResult
from app.schemas.opportunity import NormalizedOpportunity
from app.core.logging import app_logger

class OutlierPublicConnector(BaseConnector):
    """Discovers public role listings from Outlier's official Greenhouse board API."""

    source_id = "outlier"
    source_name = "Outlier AI"
    category = "ai_training_and_evaluation"
    supports_egypt = "likely"
    official_website = "https://outlier.ai"
    BOARD_API_URL = "https://boards-api.greenhouse.io/v1/boards/outlierai/jobs"

    def health_check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            resp = self._safe_http_get(f"{self.BOARD_API_URL}", timeout=10.0)
            elapsed = (time.time() - start_time) * 1000
            is_healthy = resp.status_code == 200
            return HealthCheckResult(
                source_id=self.source_id,
                is_healthy=is_healthy,
                status_code=resp.status_code,
                response_time_ms=elapsed,
                message="Official Outlier board responsive" if is_healthy else f"HTTP {resp.status_code}",
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return HealthCheckResult(
                source_id=self.source_id,
                is_healthy=False,
                response_time_ms=elapsed,
                message=str(e),
            )

    def collect(self, limit: Optional[int] = 30) -> ConnectorResult:
        start_time = time.time()
        opportunities: List[NormalizedOpportunity] = []
        raw_count = 0

        try:
            resp = self._safe_http_get(f"{self.BOARD_API_URL}?content=true")
            if resp.status_code != 200:
                return ConnectorResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    success=False,
                    error_message=f"Outlier board API returned HTTP {resp.status_code}",
                    execution_time_seconds=time.time() - start_time,
                )

            data = resp.json()
            jobs = data.get("jobs", [])
            raw_count = len(jobs)
            if limit:
                jobs = jobs[:limit]

            for job in jobs:
                content_html = job.get("content", "")
                soup = BeautifulSoup(content_html, "html.parser")
                clean_desc = soup.get_text(separator="\n", strip=True)

                raw_item = {
                    "title": job.get("title"),
                    "company": "Outlier AI",
                    "description": clean_desc,
                    "url": job.get("absolute_url") or f"https://boards.greenhouse.io/outlierai/jobs/{job.get('id')}",
                    "location": job.get("location", {}).get("name", "Remote - Global"),
                    "category": "ai_training_and_evaluation",
                    "payment_methods": ["paypal", "airtm"],
                }
                opp, is_excluded, reason = self.normalizer.normalize(
                    raw_item=raw_item,
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_type=self.category,
                    source_supports_egypt=self.supports_egypt,
                )
                if opp and not is_excluded:
                    opportunities.append(opp)

            return ConnectorResult(
                source_id=self.source_id,
                source_name=self.source_name,
                success=True,
                opportunities=opportunities,
                raw_count=raw_count,
                normalized_count=len(opportunities),
                execution_time_seconds=time.time() - start_time,
            )

        except Exception as e:
            app_logger.error(f"Outlier public connector error: {e}")
            return ConnectorResult(
                source_id=self.source_id,
                source_name=self.source_name,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
            )
