from typing import Dict, Any, List
from app.core.config import config_manager
from app.schemas.opportunity import NormalizedOpportunity

class MatchingEngine:
    """Calculates deterministic 100-point multi-factor match score and recommendation."""

    def __init__(self):
        scoring_cfg = config_manager.get_scoring()
        self.weights = scoring_cfg.get("weights", {
            "technical_skill_match": 30,
            "experience_match": 20,
            "opportunity_type_preference": 10,
            "egypt_eligibility": 15,
            "compensation_attractiveness": 10,
            "project_quality_and_clarity": 10,
            "application_feasibility": 5,
        })
        self.thresholds = scoring_cfg.get("thresholds", {
            "excellent": 90,
            "strong": 80,
            "good": 70,
            "moderate": 60,
        })
        self.multipliers = scoring_cfg.get("domain_priority_multiplier", {})

    def score_opportunity(
        self,
        domains: List[str],
        matched_skills: List[str],
        missing_skills: List[str],
        eligibility_score: float,
        egypt_eligibility: str,
        hourly_rate_min: float | None = None,
        hourly_rate_max: float | None = None,
        fixed_budget: float | None = None,
        description: str = "",
        risk_level: str = "low",
    ) -> Dict[str, Any]:
        """
        Computes 100-point score breakdown.
        """
        # 1. Technical Skill Match (max 30 pts)
        skill_count = len(matched_skills)
        if skill_count >= 5:
            skill_subscore = 30.0
        elif skill_count >= 3:
            skill_subscore = 24.0
        elif skill_count >= 2:
            skill_subscore = 18.0
        elif skill_count >= 1:
            skill_subscore = 12.0
        else:
            skill_subscore = 4.0

        # Apply domain priority multiplier (top priority domains get bonus)
        for d in domains:
            mult = self.multipliers.get(d, 1.0)
            skill_subscore = min(30.0, skill_subscore * mult)
            break

        # 2. Experience Match (max 20 pts)
        desc_lower = description.lower()
        if any(term in desc_lower for term in ["senior", "lead", "architect", "expert", "5+ years", "staff"]):
            exp_subscore = 20.0
        elif any(term in desc_lower for term in ["mid-level", "3+ years", "experienced"]):
            exp_subscore = 17.0
        elif any(term in desc_lower for term in ["junior", "entry level", "1-2 years"]):
            exp_subscore = 10.0
        else:
            exp_subscore = 16.0  # Flexible/general

        # 3. Opportunity Type Preference (max 10 pts)
        # Highly prefer remote contract, freelance, or per-task AI evaluation
        if any(term in desc_lower for term in ["contract", "freelance", "hourly", "project-based", "task"]):
            type_subscore = 10.0
        else:
            type_subscore = 8.0

        # 4. Egypt Eligibility (max 15 pts)
        # Proportional to eligibility_score (0 - 100)
        elig_subscore = (eligibility_score / 100.0) * 15.0

        # 5. Compensation Attractiveness (max 10 pts)
        rate = hourly_rate_max or hourly_rate_min
        if rate:
            if rate >= 40.0:
                comp_subscore = 10.0
            elif rate >= 25.0:
                comp_subscore = 8.5
            elif rate >= 15.0:
                comp_subscore = 7.0
            else:
                comp_subscore = 4.0
        elif fixed_budget:
            if fixed_budget >= 1000.0:
                comp_subscore = 9.0
            elif fixed_budget >= 250.0:
                comp_subscore = 7.5
            else:
                comp_subscore = 5.0
        else:
            # Undisclosed compensation
            comp_subscore = 6.0

        # 6. Project Quality and Clarity (max 10 pts)
        desc_len = len(description.strip())
        if desc_len > 800:
            quality_subscore = 10.0
        elif desc_len > 400:
            quality_subscore = 8.0
        elif desc_len > 150:
            quality_subscore = 6.0
        else:
            quality_subscore = 3.0

        if risk_level in ["high", "scam"]:
            quality_subscore = 0.0

        # 7. Application Feasibility (max 5 pts)
        feasibility_subscore = 5.0
        if "assessment required" in desc_lower or "interview" in desc_lower:
            feasibility_subscore = 4.0

        total_score = round(
            skill_subscore + exp_subscore + type_subscore + elig_subscore + comp_subscore + quality_subscore + feasibility_subscore,
            1,
        )
        total_score = max(0.0, min(100.0, total_score))

        # Determine Recommendation & Gate
        if egypt_eligibility == "not_eligible":
            recommendation = "Not Recommended / Ineligible"
            action = "Ineligible due to residency/authorization restrictions"
        elif total_score >= self.thresholds["excellent"]:
            recommendation = "Excellent Match"
            action = "Apply Immediately"
        elif total_score >= self.thresholds["strong"]:
            recommendation = "Strong Match"
            action = "High Priority Application"
        elif total_score >= self.thresholds["good"]:
            recommendation = "Good Match"
            action = "Consider Application"
        elif total_score >= self.thresholds["moderate"]:
            recommendation = "Moderate Match"
            action = "Review Details Before Applying"
        else:
            recommendation = "Low Match"
            action = "Not Recommended"

        if egypt_eligibility == "unverified" and recommendation not in ["Low Match", "Not Recommended / Ineligible"]:
            recommendation = f"{recommendation} (Eligibility Verification Required)"

        explanation_parts = [
            f"Technical skill alignment: {len(matched_skills)} matched skills ({', '.join(matched_skills[:4]) or 'General AI'}).",
            f"Eligibility status: {egypt_eligibility.replace('_', ' ').capitalize()}.",
            f"Action: {action}."
        ]
        if missing_skills:
            explanation_parts.append(f"Additional tech mentioned: {', '.join(missing_skills[:3])}.")

        return {
            "overall_score": total_score,
            "skill_match_score": round((skill_subscore / 30.0) * 100, 1),
            "eligibility_score": eligibility_score,
            "recommendation": recommendation,
            "match_explanation": " ".join(explanation_parts),
        }
