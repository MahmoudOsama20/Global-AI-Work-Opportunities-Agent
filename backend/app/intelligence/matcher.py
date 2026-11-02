from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from app.core.config import config_manager
from app.schemas.opportunity import NormalizedOpportunity

class MatchingEngine:
    """
    Calculates deterministic 100-point multi-factor match score and recommendation.
    Incorporate 8 distinct scoring dimensions and strict seniority compatibility gating.
    """

    def __init__(self):
        scoring_cfg = config_manager.get_scoring()
        self.weights = scoring_cfg.get("weights", {
            "technical_skill_match": 25,
            "experience_match": 15,
            "opportunity_type_preference": 10,
            "egypt_eligibility": 15,
            "compensation_attractiveness": 10,
            "project_quality_and_clarity": 10,
            "freshness": 10,
            "application_feasibility": 5,
        })
        self.thresholds = scoring_cfg.get("thresholds", {
            "excellent": 90,
            "strong": 80,
            "good": 70,
            "moderate": 60,
        })
        self.multipliers = scoring_cfg.get("domain_priority_multiplier", {})

        # Controlled transferable skill relationships: source -> (target, confidence)
        self.transferable_graph = {
            "pytorch": [("model_serving", 0.85), ("deep_learning", 0.95)],
            "fastapi": [("ml_apis", 0.90), ("model_serving", 0.85)],
            "docker": [("containerization", 0.95), ("deployment", 0.80)],
            "yolo": [("object_detection", 0.95), ("computer_vision", 0.95), ("video_analytics", 0.80)],
            "opencv": [("image_processing", 0.95), ("computer_vision", 0.90)],
            "transformers": [("nlp", 0.95), ("embeddings", 0.90), ("rag", 0.85)],
            "langchain": [("ai_agents", 0.85), ("rag", 0.85)],
            "langgraph": [("multi_agent_systems", 0.90), ("ai_agents", 0.90)],
        }

    def detect_role_seniority(self, title: str, description: str) -> str:
        """
        Classifies role seniority level based on title and description.
        Levels: manager, principal, lead, senior, intermediate, junior, entry, intern.
        """
        t_lower = title.lower()
        d_lower = description.lower()

        # Manager / Director / VP
        if any(term in t_lower for term in ["engineering manager", "technical manager", "director of", "head of", "vp of"]):
            return "manager"
        if "manager" in t_lower and not any(term in t_lower for term in ["account manager", "product manager"]):
            return "manager"

        # Principal / Staff
        if any(term in t_lower for term in ["principal", "staff engineer", "distinguished"]):
            return "principal"

        # Lead / Architect
        if any(term in t_lower for term in ["lead", "architect", "tech lead", "team lead"]):
            return "lead"

        # Senior
        if any(term in t_lower for term in ["senior", "sr.", "sr "]):
            return "senior"

        # Check description indicators if title is ambiguous
        if any(term in d_lower for term in ["8+ years", "10+ years", "staff engineer", "principal engineer"]):
            return "principal"
        if any(term in d_lower for term in ["manage a team", "direct reports", "engineering management", "people manager"]):
            return "manager"
        if any(term in d_lower for term in ["5+ years", "5-7 years", "senior engineer"]):
            return "senior"
        if any(term in d_lower for term in ["junior", "entry level", "associate", "0-2 years"]):
            return "junior"
        if "intern" in t_lower or "internship" in d_lower:
            return "intern"

        return "intermediate"

    def score_opportunity(
        self,
        domains: List[str],
        matched_skills: List[str],
        missing_skills: List[str],
        eligibility_score: float,
        egypt_eligibility: str,
        hourly_rate_min: Optional[float] = None,
        hourly_rate_max: Optional[float] = None,
        fixed_budget: Optional[float] = None,
        description: str = "",
        title: str = "",
        risk_level: str = "low",
        freshness_score: float = 0.0,
        cv_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Computes the complete 100-point multi-factor score breakdown.
        """
        title_lower = title.lower()
        desc_lower = description.lower()

        # 1. Technical Skill Match (max 25 pts)
        project_evidence_count = 0
        transferable_matches = []
        if cv_profile and "skill_evidence" in cv_profile:
            evidence_list = cv_profile.get("skill_evidence", [])
            demonstrated_skills = {
                e.get("skill_name", "").lower()
                for e in evidence_list
                if e.get("evidence_source") in ["project", "employment"]
            }
            for s in matched_skills:
                if s.lower() in demonstrated_skills:
                    project_evidence_count += 1

            # Transferable skills check
            cv_skills = {s.lower() for s in cv_profile.get("technical_skills", [])}
            for src, targets in self.transferable_graph.items():
                if src in cv_skills:
                    for tgt, conf in targets:
                        if any(tgt in m.lower() for m in missing_skills):
                            transferable_matches.append(f"{src} -> {tgt} ({int(conf*100)}%)")

        skill_count = len(matched_skills)
        if skill_count >= 5:
            skill_subscore = 25.0
        elif skill_count >= 3:
            skill_subscore = 20.0
        elif skill_count >= 2:
            skill_subscore = 15.0
        elif skill_count >= 1:
            skill_subscore = 10.0
        else:
            skill_subscore = 4.0

        # Project evidence bonus within max 25 pts
        if project_evidence_count >= 2:
            skill_subscore = min(25.0, skill_subscore + 2.0)

        # Apply domain priority multiplier
        for d in domains:
            mult = self.multipliers.get(d, 1.0)
            skill_subscore = min(25.0, skill_subscore * mult)
            break

        # 2. Seniority & Experience Compatibility (max 15 pts) & Strict Penalty Gates
        role_seniority = self.detect_role_seniority(title=title, description=description)
        candidate_seniority = cv_profile.get("seniority_level", "intermediate") if cv_profile else "intermediate"
        has_leadership = cv_profile.get("has_leadership_experience", False) if cv_profile else False

        seniority_penalty = 0.0
        seniority_compatibility = "compatible"
        seniority_mismatch_reason = None

        if role_seniority == "manager" and not has_leadership:
            # Major mismatch: People management role for IC candidate
            exp_subscore = 0.0
            seniority_penalty = 25.0
            seniority_compatibility = "incompatible_leadership"
            seniority_mismatch_reason = (
                "Role requires dedicated engineering management / people leadership experience, "
                "which is not present in candidate profile."
            )
        elif role_seniority == "principal" and candidate_seniority in ["junior", "intermediate"]:
            # High mismatch: Staff/Principal for junior/mid candidate
            exp_subscore = 3.0
            seniority_penalty = 15.0
            seniority_compatibility = "insufficient_seniority"
            seniority_mismatch_reason = (
                "Role requires Principal/Staff seniority (8-10+ years industry leadership), "
                "exceeding candidate's intermediate profile."
            )
        elif role_seniority == "senior":
            if candidate_seniority in ["senior", "lead", "principal"]:
                exp_subscore = 15.0
            elif candidate_seniority == "intermediate":
                exp_subscore = 12.0  # Viable reach
            else:
                exp_subscore = 6.0
                seniority_penalty = 8.0
                seniority_compatibility = "experience_gap"
                seniority_mismatch_reason = "Role requires senior level; candidate has entry/junior level."
        elif role_seniority in ["intermediate", "junior"]:
            exp_subscore = 15.0
        elif role_seniority == "intern" and candidate_seniority in ["senior", "lead"]:
            exp_subscore = 5.0
            seniority_penalty = 10.0
            seniority_compatibility = "overqualified"
            seniority_mismatch_reason = "Candidate is significantly overqualified for an internship."
        else:
            exp_subscore = 12.0

        # 3. Opportunity Type Preference (max 10 pts)
        if any(term in desc_lower for term in ["contract", "freelance", "hourly", "project-based", "task", "per-task"]):
            type_subscore = 10.0
        else:
            type_subscore = 8.0

        # 4. Egypt Eligibility (max 15 pts)
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
                comp_subscore = 3.5
        elif fixed_budget:
            if fixed_budget >= 1000.0:
                comp_subscore = 9.0
            elif fixed_budget >= 250.0:
                comp_subscore = 7.5
            else:
                comp_subscore = 5.0
        else:
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

        # 7. Freshness Score (max 10 pts)
        fresh_subscore = (freshness_score / 100.0) * 10.0

        # 8. Application Feasibility (max 5 pts)
        feasibility_subscore = 5.0
        if "assessment required" in desc_lower or "video interview" in desc_lower:
            feasibility_subscore = 4.0

        # Compute raw total and apply seniority penalty
        raw_total = (
            skill_subscore
            + exp_subscore
            + type_subscore
            + elig_subscore
            + comp_subscore
            + quality_subscore
            + fresh_subscore
            + feasibility_subscore
        )
        total_score = round(max(0.0, min(100.0, raw_total - seniority_penalty)), 1)

        # Recommendation determination
        if egypt_eligibility == "not_eligible":
            recommendation = "Not Recommended / Ineligible"
            action = "Ineligible due to residency/authorization restrictions"
        elif seniority_penalty >= 20.0:
            recommendation = "Low Match (Seniority Mismatch)"
            action = "Role requires management/leadership not present in profile"
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

        if egypt_eligibility == "unverified" and "Match" in recommendation and "Low Match" not in recommendation:
            recommendation = f"{recommendation} (Eligibility Verification Required)"

        explanation_parts = [
            f"Technical skill alignment: {len(matched_skills)} matched skills ({', '.join(matched_skills[:4]) or 'General AI'}).",
            f"Seniority alignment: {role_seniority.capitalize()} role evaluated against {candidate_seniority} profile.",
            f"Eligibility status: {egypt_eligibility.replace('_', ' ').capitalize()}.",
            f"Freshness subscore: {round(fresh_subscore, 1)}/10 pts.",
            f"Action: {action}."
        ]
        if seniority_mismatch_reason:
            explanation_parts.append(f"Seniority warning: {seniority_mismatch_reason}")
        if missing_skills:
            explanation_parts.append(f"Additional skills in posting: {', '.join(missing_skills[:3])}.")

        cv_breakdown = {
            "skill_subscore": round(skill_subscore, 1),
            "experience_subscore": round(exp_subscore, 1),
            "type_subscore": round(type_subscore, 1),
            "eligibility_subscore": round(elig_subscore, 1),
            "compensation_subscore": round(comp_subscore, 1),
            "quality_subscore": round(quality_subscore, 1),
            "freshness_subscore": round(fresh_subscore, 1),
            "feasibility_subscore": round(feasibility_subscore, 1),
            "seniority_penalty": round(seniority_penalty, 1),
            "role_seniority": role_seniority,
            "project_evidence_count": project_evidence_count,
            "transferable_matches": transferable_matches,
        }

        return {
            "overall_score": total_score,
            "skill_match_score": round((skill_subscore / 25.0) * 100, 1),
            "eligibility_score": eligibility_score,
            "seniority_compatibility": seniority_compatibility,
            "seniority_mismatch_reason": seniority_mismatch_reason,
            "cv_match_breakdown": cv_breakdown,
            "recommendation": recommendation,
            "match_explanation": " ".join(explanation_parts),
        }
