import time
import concurrent.futures
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.core.logging import app_logger
from app.connectors.registry import connector_registry
from app.database.session import SessionLocal
from app.database.repositories.source_repo import SourceRepository
from app.database.repositories.opportunity_repo import OpportunityRepository
from app.database.repositories.run_repo import RunRepository
from app.intelligence.deduplicator import DeduplicationEngine
from app.discovery.source_registry import SourceDiscoveryEngine
from app.reports.markdown_report import MarkdownReportGenerator
from app.reports.html_report import HtmlReportGenerator
from app.schemas.connector import HealthCheckResult, ConnectorResult

class PipelineRunner:
    """Orchestrates manual discovery, collection, deduplication, persistence, and reporting."""

    def __init__(self):
        self.registry = connector_registry
        self.deduplicator = DeduplicationEngine()
        self.md_reporter = MarkdownReportGenerator()
        self.html_reporter = HtmlReportGenerator()
        self.discovery_engine = SourceDiscoveryEngine()

    def health_check_all(self) -> List[HealthCheckResult]:
        """Runs synchronous health checks across all registered source connectors."""
        connectors = self.registry.get_all()
        results: List[HealthCheckResult] = []
        with SessionLocal() as session:
            repo = SourceRepository(session)
            for c in connectors:
                try:
                    res = c.health_check()
                except Exception as e:
                    res = HealthCheckResult(
                        source_id=c.source_id,
                        is_healthy=False,
                        message=str(e),
                    )
                results.append(res)
                repo.record_health_check(c.source_id, res.is_healthy)
            session.commit()
        return results

    def run_manual(
        self,
        source_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        trigger_discovery: bool = False,
    ) -> Dict[str, Any]:
        """Executes full manual search run."""
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        app_logger.info(f"Initiating pipeline run: {run_id}")

        with SessionLocal() as session:
            run_repo = RunRepository(session)
            run_repo.create_run(run_id, trigger_type="manual_cli")
            session.commit()

        # Step 1: Optional Source Discovery
        new_sources_summary = {}
        if trigger_discovery:
            app_logger.info("Executing Source Discovery Engine...")
            new_sources_summary = self.discovery_engine.discover_new_sources()

        # Step 2: Determine active connectors
        with SessionLocal() as session:
            source_repo = SourceRepository(session)
            enabled_sources = [s.id for s in source_repo.get_all(enabled_only=True)]

        connectors = self.registry.get_all(enabled_ids=enabled_sources)
        if source_filter:
            connectors = [c for c in connectors if c.source_id == source_filter.lower()]
        if category_filter:
            connectors = [c for c in connectors if c.category == category_filter.lower()]

        app_logger.info(f"Executing {len(connectors)} connectors in concurrent thread pool...")

        # Step 3: Concurrent Collection
        collected_raw: List[Any] = []
        sources_status: List[Dict[str, Any]] = []
        attempted = len(connectors)
        succeeded = 0
        failed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_CONNECTORS) as executor:
            future_to_connector = {executor.submit(c.collect): c for c in connectors}
            for future in concurrent.futures.as_completed(future_to_connector):
                conn = future_to_connector[future]
                try:
                    res: ConnectorResult = future.result()
                    if res.success:
                        succeeded += 1
                        collected_raw.extend(res.opportunities)
                        sources_status.append({
                            "source_id": conn.source_id,
                            "source_name": conn.source_name,
                            "is_healthy": True,
                            "message": f"Collected {len(res.opportunities)} items",
                        })
                    else:
                        failed += 1
                        sources_status.append({
                            "source_id": conn.source_id,
                            "source_name": conn.source_name,
                            "is_healthy": False,
                            "message": res.error_message or "Collection error",
                        })
                except Exception as e:
                    failed += 1
                    sources_status.append({
                        "source_id": conn.source_id,
                        "source_name": conn.source_name,
                        "is_healthy": False,
                        "message": str(e),
                    })

        total_collected = len(collected_raw)
        app_logger.info(f"Raw opportunities collected: {total_collected}")

        # Step 4: Deduplication
        deduplicated, duplicate_count = self.deduplicator.cluster_and_deduplicate(collected_raw)
        app_logger.info(f"Deduplication complete: {len(deduplicated)} unique, {duplicate_count} duplicates")

        # Step 5: Persistence & Metrics
        new_count = 0
        with SessionLocal() as session:
            opp_repo = OpportunityRepository(session)
            for opp in deduplicated:
                _, is_new = opp_repo.upsert(opp)
                if is_new:
                    new_count += 1
            session.commit()
            metrics = opp_repo.get_metrics_summary()

        metrics["sources_attempted"] = attempted
        metrics["sources_succeeded"] = succeeded
        metrics["sources_failed"] = failed
        metrics["total_collected"] = total_collected
        metrics["new_count"] = new_count
        metrics["duplicate_count"] = duplicate_count
        metrics["relevant_count"] = len(deduplicated)
        metrics["excluded_count"] = 0

        # Step 6: Generate Reports
        excluded_summary = {
            "speech_and_audio": 0,
            "automation_job_category": 0,
            "unpaid_or_irrelevant": 0,
        }
        md_path = self.md_reporter.generate(
            run_id=run_id,
            metrics=metrics,
            opportunities=deduplicated,
            excluded_summary=excluded_summary,
            sources_status=sources_status,
        )
        html_path = self.html_reporter.generate(
            run_id=run_id,
            metrics=metrics,
            opportunities=deduplicated,
            excluded_summary=excluded_summary,
            sources_status=sources_status,
        )

        # Step 7: Finalize Run Audit Record
        with SessionLocal() as session:
            run_repo = RunRepository(session)
            run_repo.finish_run(
                run_id=run_id,
                status="completed",
                attempted=attempted,
                succeeded=succeeded,
                failed=failed,
                total_collected=total_collected,
                new_count=new_count,
                duplicate_count=duplicate_count,
                excluded_count=0,
                relevant_count=len(deduplicated),
                report_html_path=str(html_path),
                report_md_path=str(md_path),
                summary_json=metrics,
            )
            session.commit()

        return {
            "run_id": run_id,
            "status": "completed",
            "total_collected": total_collected,
            "new_count": new_count,
            "duplicate_count": duplicate_count,
            "relevant_count": len(deduplicated),
            "report_html_path": str(html_path),
            "report_md_path": str(md_path),
            "metrics": metrics,
        }
