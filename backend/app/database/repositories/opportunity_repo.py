from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_, desc
from app.database.models.opportunity import OpportunityModel
from app.schemas.opportunity import NormalizedOpportunity, OpportunityFilter

class OpportunityRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, opp_id: str) -> Optional[OpportunityModel]:
        stmt = select(OpportunityModel).where(OpportunityModel.id == opp_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_canonical_url(self, canonical_url: str) -> Optional[OpportunityModel]:
        stmt = select(OpportunityModel).where(OpportunityModel.canonical_url == canonical_url)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def upsert(self, opp: NormalizedOpportunity) -> Tuple[OpportunityModel, bool]:
        """Upserts an opportunity. Returns (model, is_new)."""
        existing = self.get_by_id(opp.id)
        if not existing and opp.canonical_url:
            existing = self.get_by_canonical_url(opp.canonical_url)

        now = datetime.now(timezone.utc)
        if existing:
            # Update timestamps and fresh analysis
            existing.last_seen_at = now
            existing.last_verified_at = now
            existing.listing_status = "active"
            existing.skill_match_score = opp.skill_match_score
            existing.eligibility_score = opp.eligibility_score
            existing.overall_score = opp.overall_score
            existing.recommendation = opp.recommendation
            existing.match_explanation = opp.match_explanation
            existing.missing_skills = opp.missing_skills
            existing.technical_domains = opp.technical_domains
            existing.required_skills = opp.required_skills
            existing.egypt_eligibility = opp.egypt_eligibility
            existing.updated_at = now
            self.session.flush()
            return existing, False
        else:
            data = opp.model_dump()
            data["first_seen_at"] = now
            data["last_seen_at"] = now
            data["last_verified_at"] = now
            data["created_at"] = now
            data["updated_at"] = now
            model = OpportunityModel(**data)
            self.session.add(model)
            self.session.flush()
            return model, True

    def search(self, filters: OpportunityFilter) -> Tuple[List[OpportunityModel], int]:
        stmt = select(OpportunityModel)
        count_stmt = select(func.count(OpportunityModel.id))

        conditions = []
        if filters.category:
            conditions.append(OpportunityModel.category == filters.category)
        if filters.source_id:
            conditions.append(OpportunityModel.source_id == filters.source_id)
        if filters.egypt_eligibility:
            conditions.append(OpportunityModel.egypt_eligibility == filters.egypt_eligibility)
        if filters.min_score is not None:
            conditions.append(OpportunityModel.overall_score >= filters.min_score)
        if filters.max_score is not None:
            conditions.append(OpportunityModel.overall_score <= filters.max_score)
        if filters.payment_model:
            conditions.append(OpportunityModel.payment_model == filters.payment_model)
        if filters.recommendation:
            conditions.append(OpportunityModel.recommendation == filters.recommendation)
        if filters.search_query:
            term = f"%{filters.search_query.lower()}%"
            conditions.append(or_(
                func.lower(OpportunityModel.title).like(term),
                func.lower(OpportunityModel.company).like(term),
                func.lower(OpportunityModel.description).like(term),
            ))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = self.session.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(desc(OpportunityModel.overall_score), desc(OpportunityModel.last_seen_at))
        stmt = stmt.offset(filters.offset).limit(filters.limit)

        items = list(self.session.execute(stmt).scalars().all())
        return items, total

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Calculates global metrics for the dashboard overview."""
        total_stmt = select(func.count(OpportunityModel.id))
        total = self.session.execute(total_stmt).scalar_one()

        excellent_stmt = select(func.count(OpportunityModel.id)).where(OpportunityModel.overall_score >= 90)
        excellent = self.session.execute(excellent_stmt).scalar_one()

        strong_stmt = select(func.count(OpportunityModel.id)).where(
            and_(OpportunityModel.overall_score >= 80, OpportunityModel.overall_score < 90)
        )
        strong = self.session.execute(strong_stmt).scalar_one()

        eligible_egypt_stmt = select(func.count(OpportunityModel.id)).where(
            OpportunityModel.egypt_eligibility.in_(["eligible", "likely_eligible"])
        )
        eligible_egypt = self.session.execute(eligible_egypt_stmt).scalar_one()

        unverified_egypt_stmt = select(func.count(OpportunityModel.id)).where(
            OpportunityModel.egypt_eligibility == "unverified"
        )
        unverified_egypt = self.session.execute(unverified_egypt_stmt).scalar_one()

        # Group by source
        source_stmt = select(
            OpportunityModel.source_name,
            func.count(OpportunityModel.id)
        ).group_by(OpportunityModel.source_name)
        source_counts = dict(self.session.execute(source_stmt).all())

        return {
            "total_opportunities": total,
            "excellent_matches": excellent,
            "strong_matches": strong,
            "eligible_in_egypt": eligible_egypt,
            "unverified_eligibility": unverified_egypt,
            "by_source": source_counts,
        }
