import time
from typing import Optional, List, Dict, Any
from app.connectors.base import BaseConnector
from app.schemas.connector import ConnectorResult, HealthCheckResult
from app.schemas.opportunity import NormalizedOpportunity
from app.core.logging import app_logger

class RemoteOKConnector(BaseConnector):
    source_id = "remoteok"
    source_name = "Remote OK"
    category = "remote_job_board"
    supports_egypt = "likely"
    official_website = "https://remoteok.com"
    API_URL = "https://remoteok.com/api"

    def health_check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            resp = self._safe_http_get(f"{self.API_URL}?tag=ai", timeout=10.0)
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
            resp = self._safe_http_get(f"{self.API_URL}?tag=ai")
            if resp.status_code != 200:
                return ConnectorResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    success=False,
                    error_message=f"Remote OK API returned HTTP {resp.status_code}",
                    execution_time_seconds=time.time() - start_time,
                )

            data = resp.json()
            jobs = [j for j in data if isinstance(j, dict) and "position" in j]
            raw_count = len(jobs)
            if limit:
                jobs = jobs[:limit]

            for job in jobs:
                raw_item = {
                    "title": job.get("position"),
                    "company": job.get("company"),
                    "description": job.get("description", ""),
                    "url": job.get("url") or f"https://remoteok.com/l/{job.get('id')}",
                    "location": job.get("location") or "Worldwide",
                    "salary": f"${job.get('salary_min', 0)} - ${job.get('salary_max', 0)} / year" if job.get("salary_max") else None,
                    "posted_at": job.get("date"),
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
            app_logger.error(f"Remote OK connector error: {e}")
            return ConnectorResult(
                source_id=self.source_id,
                source_name=self.source_name,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
            )
