import time
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from app.connectors.base import BaseConnector
from app.schemas.connector import ConnectorResult, HealthCheckResult
from app.schemas.opportunity import NormalizedOpportunity
from app.core.logging import app_logger

class WeWorkRemotelyConnector(BaseConnector):
    source_id = "weworkremotely"
    source_name = "We Work Remotely"
    category = "remote_job_board"
    supports_egypt = "likely"
    official_website = "https://weworkremotely.com"
    RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    def health_check(self) -> HealthCheckResult:
        start_time = time.time()
        try:
            resp = self._safe_http_get(self.RSS_URL, timeout=10.0)
            elapsed = (time.time() - start_time) * 1000
            is_healthy = resp.status_code == 200
            return HealthCheckResult(
                source_id=self.source_id,
                is_healthy=is_healthy,
                status_code=resp.status_code,
                response_time_ms=elapsed,
                message="WWR RSS responsive" if is_healthy else f"HTTP {resp.status_code}",
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
            resp = self._safe_http_get(self.RSS_URL)
            if resp.status_code != 200:
                return ConnectorResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    success=False,
                    error_message=f"WWR RSS returned HTTP {resp.status_code}",
                    execution_time_seconds=time.time() - start_time,
                )

            root = ET.fromstring(resp.text)
            items = root.findall(".//item")
            raw_count = len(items)
            if limit:
                items = items[:limit]

            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")
                desc_elem = item.find("description")

                title = title_elem.text if title_elem is not None else ""
                link = link_elem.text if link_elem is not None else ""
                raw_desc = desc_elem.text if desc_elem is not None else ""

                soup = BeautifulSoup(raw_desc, "html.parser")
                clean_desc = soup.get_text(separator="\n", strip=True)

                company = "WeWorkRemotely Client"
                if ":" in title:
                    parts = title.split(":", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                raw_item = {
                    "title": title,
                    "company": company,
                    "description": clean_desc,
                    "url": link,
                    "location": "Worldwide",
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
            app_logger.error(f"WeWorkRemotely connector error: {e}")
            return ConnectorResult(
                source_id=self.source_id,
                source_name=self.source_name,
                success=False,
                error_message=str(e),
                execution_time_seconds=time.time() - start_time,
            )
