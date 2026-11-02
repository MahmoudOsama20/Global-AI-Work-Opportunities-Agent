import hashlib
from typing import Dict, Any, Optional, Tuple
from app.core.security import canonicalize_url
from app.intelligence.exclusions import ExclusionEngine
from app.intelligence.classifier import DomainClassifier
from app.intelligence.skill_extractor import SkillExtractor
from app.intelligence.payment_parser import PaymentParser
from app.intelligence.eligibility import CountryEligibilityEvaluator
from app.intelligence.risk_analyzer import RiskAnalyzer
from app.intelligence.matcher import MatchingEngine
from app.intelligence.freshness import parse_timestamp, calculate_freshness
from app.schemas.opportunity import NormalizedOpportunity

class OpportunityNormalizer:
    """Universal Normalization Engine transforming raw connector data into the standard intelligence schema."""

    def __init__(self, cv_profile: Optional[Dict[str, Any]] = None):
        self.exclusions = ExclusionEngine()
        self.classifier = DomainClassifier()
        self.skill_extractor = SkillExtractor()
        self.payment_parser = PaymentParser()
        self.eligibility_evaluator = CountryEligibilityEvaluator()
        self.risk_analyzer = RiskAnalyzer()
        self.matcher = MatchingEngine()
        self.cv_profile = cv_profile

    def normalize(
        self,
        raw_item: Dict[str, Any],
        source_id: str,
        source_name: str,
        source_type: str = "job_board",
        source_supports_egypt: str = "unknown",
        cv_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[NormalizedOpportunity], bool, Optional[str]]:
        """
        Transforms raw data into a NormalizedOpportunity.
        Returns:
            (opportunity: NormalizedOpportunity | None, is_excluded: bool, exclusion_reason: str | None)
        """
        title = (raw_item.get("title") or "").strip()
        description = (raw_item.get("description") or "").strip()
        original_url = (raw_item.get("url") or raw_item.get("original_url") or "").strip()
        company = (raw_item.get("company") or raw_item.get("company_name") or "").strip()
        location_field = (raw_item.get("location") or raw_item.get("candidate_required_location") or "").strip()

        if not title or not original_url:
            return None, True, "Missing title or URL"

        # 1. Evaluate Strict Exclusions (Speech/Audio, RPA/Automation, Unpaid)
        is_excluded, cat, reason = self.exclusions.evaluate(title, description)
        if is_excluded:
            return None, True, f"Excluded [{cat}]: {reason}"

        # 2. Canonicalize URL and generate deterministic ID
        canonical_url = canonicalize_url(original_url)
        opp_id = hashlib.sha256(f"{source_id}_{canonical_url}".encode()).hexdigest()[:24]

        # 3. Classify Technical Domains
        full_text = f"{title}\n{description}"
        domains = self.classifier.classify(full_text)
        # If no AI domain matches, flag as irrelevant non-AI work
        if not domains:
            return None, True, "Excluded [non_ai]: No matched AI/ML technical domain detected"

        # 4. Extract Skills
        matched_skills, missing_skills = self.skill_extractor.extract_and_match(full_text)

        # 5. Parse Compensation
        payment_info = self.payment_parser.parse(
            raw_item.get("salary") or raw_item.get("compensation") or full_text
        )

        # 6. Evaluate Egyptian Eligibility
        elig_result = self.eligibility_evaluator.evaluate(
            text=full_text,
            location_field=location_field,
            source_supports_egypt=source_supports_egypt,
        )

        # 7. Evaluate Risk & Quality
        risk_level, risk_explanation = self.risk_analyzer.analyze(
            title=title,
            description=description,
            company=company,
            hourly_rate_max=payment_info["hourly_rate_max"],
        )

        # 8. Parse publication and freshness timestamps
        raw_posted = (
            raw_item.get("posted_at")
            or raw_item.get("publication_date")
            or raw_item.get("date")
            or raw_item.get("pub_date")
            or raw_item.get("created_at")
        )
        posted_at = parse_timestamp(raw_posted)
        raw_updated = raw_item.get("updated_at")
        updated_at = parse_timestamp(raw_updated)
        is_rel = isinstance(raw_posted, str) and any(
            t in raw_posted.lower() for t in ["ago", "yesterday", "today", "just now", "hour", "minute"]
        )
        freshness_status, freshness_score = calculate_freshness(posted_at, updated_at, is_relative=is_rel)

        # 9. Score & Rank
        active_cv = cv_profile or self.cv_profile
        scoring_res = self.matcher.score_opportunity(
            domains=domains,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            eligibility_score=elig_result["eligibility_score"],
            egypt_eligibility=elig_result["egypt_eligibility"],
            hourly_rate_min=payment_info["hourly_rate_min"],
            hourly_rate_max=payment_info["hourly_rate_max"],
            fixed_budget=payment_info["fixed_budget_max"] or payment_info["fixed_budget_min"],
            description=description,
            title=title,
            risk_level=risk_level,
            freshness_score=freshness_score,
            cv_profile=active_cv,
        )

        # 10. Assemble Universal Opportunity Object
        opp = NormalizedOpportunity(
            id=opp_id,
            source_id=source_id,
            source_name=source_name,
            source_type=source_type,
            title=title,
            company=company or None,
            description=description,
            original_url=original_url,
            canonical_url=canonical_url,
            category=raw_item.get("category", "engineering"),
            technical_domains=domains,
            required_skills=matched_skills + missing_skills,
            preferred_skills=[],
            experience_level=raw_item.get("experience_level"),
            employment_type=raw_item.get("employment_type", "remote_contract"),
            payment_model=payment_info["payment_model"],
            hourly_rate_min=payment_info["hourly_rate_min"],
            hourly_rate_max=payment_info["hourly_rate_max"],
            fixed_budget_min=payment_info["fixed_budget_min"],
            fixed_budget_max=payment_info["fixed_budget_max"],
            currency=payment_info["currency"],
            payment_details=payment_info["payment_details"],
            location=location_field or "Remote",
            remote_status="remote",
            eligible_countries=elig_result["eligible_countries"],
            egypt_eligibility=elig_result["egypt_eligibility"],
            payment_methods=raw_item.get("payment_methods", []),
            application_requirements=raw_item.get("application_requirements"),
            assessment_required="assessment" in full_text.lower(),
            posted_at=posted_at,
            freshness_status=freshness_status,
            freshness_score=freshness_score,
            seniority_compatibility=scoring_res.get("seniority_compatibility"),
            seniority_mismatch_reason=scoring_res.get("seniority_mismatch_reason"),
            cv_match_breakdown=scoring_res.get("cv_match_breakdown", {}),
            listing_status="active",
            verification_status="verified" if source_supports_egypt == "verified" else "unverified",
            skill_match_score=scoring_res["skill_match_score"],
            eligibility_score=scoring_res["eligibility_score"],
            overall_score=scoring_res["overall_score"],
            match_explanation=scoring_res["match_explanation"],
            missing_skills=missing_skills,
            recommendation=scoring_res["recommendation"],
            risk_level=risk_level,
            risk_explanation=risk_explanation,
        )

        return opp, False, None

