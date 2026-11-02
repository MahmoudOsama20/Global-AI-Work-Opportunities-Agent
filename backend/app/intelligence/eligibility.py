import re
from typing import Dict, Any, List, Tuple
from app.core.config import config_manager

class CountryEligibilityEvaluator:
    """Evaluates location requirements, country eligibility, and Egyptian payout feasibility."""

    def __init__(self):
        self.profile = config_manager.get_profile()
        self.location_config = self.profile.get("primary_location", {})
        self.payment_prefs = self.profile.get("payment_preferences", {})
        self.supported_payouts = set(self.payment_prefs.get("supported_methods_in_location", []))

    def evaluate(
        self,
        text: str,
        location_field: str = "",
        source_supports_egypt: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Evaluates eligibility.
        Returns:
            egypt_eligibility: str (eligible, likely_eligible, unverified, not_eligible, restricted)
            eligibility_score: float (0.0 to 100.0)
            eligible_countries: list[str]
            payout_compatible: bool
            explanation: str
        """
        combined = f"{location_field} {text}".lower()

        # 1. Check for explicit exclusions / foreign residency requirements (NOT ELIGIBLE)
        ineligible_patterns = [
            r"\b(us|usa|united states)\s+(only|citizens?|residents?|based)\b",
            r"\bmust\s+reside\s+in\s+(the\s+)?(us|usa|united states|uk|canada|eu|europe)\b",
            r"\b(uk|canada|germany|france|australia)\s+only\b",
            r"\b(us|eu|uk)\s+work\s+authorization\s+required\b",
            r"\b(w2|1099)\s+only\b",
            r"\bnot\s+open\s+to\s+international\b",
            r"\b(security\s+clearance|dod\s+clearance)\b",
            r"\bno\s+c2c\b",
            r"\begypt\s+(is\s+)?(excluded|not\s+eligible|restricted)\b",
        ]
        for pattern in ineligible_patterns:
            if re.search(pattern, combined):
                return {
                    "egypt_eligibility": "not_eligible",
                    "eligibility_score": 0.0,
                    "eligible_countries": ["Foreign Residency / Authorization Required"],
                    "payout_compatible": False,
                    "explanation": f"Ineligible: Stated foreign residency, citizenship, or authorization requirement matching '{pattern}'.",
                }

        # 2. Check for explicit Egypt support
        egypt_explicit_patterns = [
            r"\begypt\b",
            r"\begyptian\b",
            r"\bcairo\b",
            r"\balexandria\b",
            r"\bmiddle\s+east\b",
            r"\bmena\b",
            r"\barab\s+countries\b",
        ]
        for pattern in egypt_explicit_patterns:
            if re.search(pattern, combined):
                return {
                    "egypt_eligibility": "eligible",
                    "eligibility_score": 100.0,
                    "eligible_countries": ["Egypt"],
                    "payout_compatible": True,
                    "explanation": "Fully Eligible: Egypt, Cairo, or MENA explicitly cited in eligible locations.",
                }

        # 3. Check for Worldwide / Global Remote
        worldwide_patterns = [
            r"\bworldwide\b",
            r"\bglobal(ly)?\b",
            r"\banywhere\s+in\s+the\s+world\b",
            r"\bopen\s+to\s+international\s+applicants\b",
            r"\banywhere\b",
            r"\ball\s+locations\b",
            r"\bremote\s*-\s*global\b",
        ]
        for pattern in worldwide_patterns:
            if re.search(pattern, combined):
                # Check timezone constraints e.g., "PST timezone only", "US hours only"
                tz_warning = ""
                if re.search(r"\b(est|pst|cst)\s+(only|hours|timezone)\b", combined):
                    tz_warning = " (Note: US time-zone overlap required)"
                return {
                    "egypt_eligibility": "likely_eligible",
                    "eligibility_score": 85.0,
                    "eligible_countries": ["Worldwide / Global"],
                    "payout_compatible": True,
                    "explanation": f"Likely Eligible: Listing explicitly welcomes Worldwide / Global applicants{tz_warning}.",
                }

        # 4. Check platform-level default if listing location is unspecified or just "Remote"
        if source_supports_egypt == "verified":
            return {
                "egypt_eligibility": "likely_eligible",
                "eligibility_score": 80.0,
                "eligible_countries": ["Platform verified in Egypt"],
                "payout_compatible": True,
                "explanation": "Platform Officially Supports Egypt, but individual listing location details are generic.",
            }
        elif source_supports_egypt == "likely":
            return {
                "egypt_eligibility": "likely_eligible",
                "eligibility_score": 75.0,
                "eligible_countries": ["Worldwide Platform"],
                "payout_compatible": True,
                "explanation": "Platform accepts international contractors; listing location unspecified.",
            }

        # 5. Default: Unverified (never assume pure 'Remote' means Egypt is accepted)
        return {
            "egypt_eligibility": "unverified",
            "eligibility_score": 40.0,
            "eligible_countries": ["Unverified"],
            "payout_compatible": False,
            "explanation": "Unverified Eligibility: Location mentions 'Remote' without explicit worldwide or international confirmation.",
        }

