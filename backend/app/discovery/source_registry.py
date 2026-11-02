from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.database.models.candidate import SourceCandidateModel
from app.database.models.source import SourceModel
from app.database.session import SessionLocal
from app.discovery.query_generator import DiscoveryQueryGenerator
from app.discovery.search_provider import BaseSearchProvider, get_search_provider
from app.discovery.source_validator import SourceValidator
from app.core.logging import app_logger

class SourceDiscoveryEngine:
    """Discovers, validates, and registers new legitimate AI work platforms and career sites."""

    def __init__(self, search_provider: Optional[BaseSearchProvider] = None):
        self.query_generator = DiscoveryQueryGenerator()
        self.search_provider = search_provider or get_search_provider()
        self.validator = SourceValidator()

    def discover_new_sources(self, max_queries: int = 3) -> Dict[str, Any]:
        """
        Executes a discovery run and records candidate sources into the database.
        """
        queries = self.query_generator.generate_queries()[:max_queries]
        candidates_found = 0
        new_registered = 0

        with SessionLocal() as session:
            # Pre-load known candidate domains and source IDs to prevent duplicates
            existing_candidate_domains = set(
                session.execute(select(SourceCandidateModel.domain)).scalars().all()
            )
            existing_source_ids = set(
                session.execute(select(SourceModel.id)).scalars().all()
            )
            seen_domains = {d.strip().lower() for d in (existing_candidate_domains | existing_source_ids) if d}

            for query in queries:
                app_logger.info(f"Running discovery query: '{query}'")
                results = self.search_provider.search(query, limit=5)
                for res in results:
                    candidates_found += 1
                    val = self.validator.validate_candidate(res.get("url", ""), res.get("snippet", ""))
                    if not val.get("is_valid"):
                        continue

                    domain = (val.get("domain") or "").strip().lower()
                    if not domain or domain in seen_domains:
                        continue

                    seen_domains.add(domain)

                    cand_model = SourceCandidateModel(
                        domain=domain,
                        platform_name=val.get("platform_name", domain),
                        source_url=val.get("source_url"),
                        category="discovered_platform",
                        discovered_via_query=query,
                        validation_status=val.get("status", "candidate"),
                        legitimacy_score=val.get("legitimacy_score", 50.0),
                        supports_egypt="unverified",
                        payment_models_found=[],
                        detection_notes=val.get("notes"),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(cand_model)
                    new_registered += 1

            try:
                session.commit()
            except Exception as exc:
                app_logger.error(f"Failed to commit discovered candidates: {exc}")
                session.rollback()

        return {
            "queries_executed": len(queries),
            "candidates_found": candidates_found,
            "new_sources_registered": new_registered,
        }

    def list_pending_candidates(self) -> List[Dict[str, Any]]:
        """Returns all candidates awaiting user review in the Discovery Center."""
        with SessionLocal() as session:
            stmt = select(SourceCandidateModel).order_by(SourceCandidateModel.created_at.desc())
            items = session.execute(stmt).scalars().all()
            return [
                {
                    "id": item.id,
                    "domain": item.domain,
                    "platform_name": item.platform_name,
                    "source_url": item.source_url,
                    "validation_status": item.validation_status,
                    "legitimacy_score": item.legitimacy_score,
                    "discovered_via_query": item.discovered_via_query,
                    "detection_notes": item.detection_notes,
                    "created_at": item.created_at.isoformat(),
                }
                for item in items
            ]

    def approve_candidate(self, candidate_id: int) -> bool:
        """Approves a candidate source and promotes it into active registered sources."""
        with SessionLocal() as session:
            cand = session.get(SourceCandidateModel, candidate_id)
            if not cand:
                return False
            cand.validation_status = "approved"
            cand.reviewed_at = datetime.now(timezone.utc)

            # Register as active source
            source = SourceModel(
                id=cand.domain,
                name=cand.platform_name,
                category="ai_training_and_evaluation",
                official_website=cand.source_url,
                collection_method="public_web",
                status="verified",
                supports_egypt=cand.supports_egypt or "unverified",
                enabled=True,
                description=f"Discovered via search query: {cand.discovered_via_query}",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.merge(source)
            session.commit()
            return True

    def reject_candidate(self, candidate_id: int) -> bool:
        """Rejects a candidate source."""
        with SessionLocal() as session:
            cand = session.get(SourceCandidateModel, candidate_id)
            if not cand:
                return False
            cand.validation_status = "rejected"
            cand.reviewed_at = datetime.now(timezone.utc)
            session.commit()
            return True

