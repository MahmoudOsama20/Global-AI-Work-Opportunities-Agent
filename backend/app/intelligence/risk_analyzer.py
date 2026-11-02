import re
from typing import Dict, Any, Tuple
from app.core.config import config_manager

class RiskAnalyzer:
    """Analyzes opportunities for scam patterns, fraud signals, and quality risks."""

    def __init__(self):
        exclusions = config_manager.get_exclusions()
        self.scam_keywords = exclusions.get("quality_and_scam_flags", {}).get("suspicious_keywords", [])

    def analyze(self, title: str, description: str, company: str, hourly_rate_max: float | None = None) -> Tuple[str, str]:
        """
        Returns: (risk_level: str, risk_explanation: str)
        risk_level: 'low', 'review', 'high', 'scam'
        """
        text_lower = f"{title} {description}".lower()
        warnings = []

        # 1. Direct scam keywords
        for kw in self.scam_keywords:
            if kw in text_lower:
                return "scam", f"High confidence scam signal: Detected phrase '{kw}'."

        # 2. Suspicious interview channels (e.g., Telegram / WhatsApp only)
        if re.search(r"\b(contact|message|interview)\s+(via|on)?\s*telegram\b", text_lower):
            warnings.append("Directs applicant to interview via Telegram.")
        if re.search(r"\b(contact|message|interview)\s+(via|on)?\s*whatsapp\b", text_lower):
            warnings.append("Directs applicant to interview via WhatsApp.")

        # 3. Unrealistic compensation
        if hourly_rate_max and hourly_rate_max > 250:
            warnings.append(f"Unusually high advertised hourly compensation (${hourly_rate_max}/hr). Verify client identity.")

        # 4. Extremely vague description
        if len(description.strip()) < 80:
            warnings.append("Extremely short or vague job description.")

        # 5. Missing company identity
        if not company or company.lower() in ["confidential", "undisclosed", "anonymous", "private client"]:
            warnings.append("Client or company identity is undisclosed.")

        if any("scam" in w.lower() for w in warnings):
            return "high", " | ".join(warnings)
        elif len(warnings) >= 2:
            return "review", " | ".join(warnings)
        elif len(warnings) == 1:
            return "review", warnings[0]
        else:
            return "low", "Verified low risk profile."
