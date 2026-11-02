import time
from typing import Optional, List, Dict, Any
from app.connectors.base import BaseConnector
from app.schemas.connector import ConnectorResult, HealthCheckResult
from app.schemas.opportunity import NormalizedOpportunity
from app.core.logging import app_logger

class HimalayasConnector(BaseConnector):
    source_id = "himalayas"
    source_name = "Himalayas"
    category = "remote_job_board"
    supports_egypt = "likely"
    official_website = "https://himalayas.app"
    API_URL = "https://himalayas.app/jobs/api"

    def health_check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            resp = self._safe_http_get(f"{self.API_URL}?limit=1", timeout=10.0)
            elapsed = (time.time() - start_time) * 1000
            is_healthy = resp.status_code == 200
            return HealthCheckResult(
                source_id=self.source_id,
                is_healthy=is_healthy,
                status_code=resp.status_code,
                response_time_ms=elapsed,
                message="Endpoint responsive" if is_healthy else f"HTTP {resp.status_code}",
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return HealthCheckResult(
                source_id=self.source_id,
                is_healthy=False,
                response_time_ms=elapsed,
                message=str(e),
            )

    def collect(self, limit: Optional[int] = 25) -> ConnectorResult:
        start_time = time.time()
        opportunities: List[NormalizedOpportunity] = []
        raw_count = 0

        try:
            resp = self._safe_http_get(f"{self.API_URL}?search=AI&limit={limit or 25}")
            if resp.status_code != 200:
                return ConnectorResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    success=False,
                    error_message=f"Himalayas API returned HTTP {resp.status_code}",
                    execution_time_seconds=time.time() - start_time,
                )

            data = resp.json()
            jobs = data.get("jobs", [])
            raw_count = len(jobs)

            for job in jobs:
                location_str = "Worldwide"
                if job.get("restricted_to_countries"):
                    location_str = ", ".join(job.get("restricted_to_countries", []))

                salary_str = None
                if job.get("min_salary") and job.get("max_salary"):
                    salary_str = f"${job.get('min_salary'):,} - ${job.get('max_salary'):,} / year"

                raw_item = {
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "description": job.get("description", ""),
                    "url": job.get("application_link") or f"https://himalayas.app/companies/{job.get('company_slug')}/jobs/{job.get('slug')}",
                    "location": location_str,
                    "salary": salary_str,
                    "posted_at": job.get("pub_date"),
                    "category": "engineering",
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
            app_logger.error(f"Himalayas connector error: {e}")
            return ConnectorResult(
                source_id=self.source_id,
                source_name=self.source_name,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
            )
