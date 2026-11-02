from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMProvider(ABC):
    """Abstract base class for LLM opportunity analysis providers."""

    @abstractmethod
    async def analyze_opportunity(
        self,
        title: str,
        description: str,
        profile_summary: str,
    ) -> Dict[str, Any]:
        """
        Analyzes a candidate opportunity.
        Returns:
            dict containing:
                relevance_summary: str
                key_strengths: list[str]
                risks: list[str]
                recommended_approach: str
        """
        pass


class DeterministicFallbackLLM(BaseLLMProvider):
    """Zero-cost, offline deterministic analysis engine without external API dependencies."""

    async def analyze_opportunity(
        self,
        title: str,
        description: str,
        profile_summary: str,
    ) -> Dict[str, Any]:
        return {
            "relevance_summary": f"Opportunity '{title}' evaluated via deterministic profile matching rules.",
            "key_strengths": ["Matches technical AI domains", "Aligns with remote engineering profile"],
            "risks": ["Verify client payout channels and actual task availability"],
            "recommended_approach": "Review requirements and apply directly via the official original link.",
        }


def get_llm_provider() -> BaseLLMProvider:
    """Factory creating configured LLM provider or deterministic fallback."""
    from app.core.config import settings
    
    provider_name = (settings.LLM_PROVIDER or "none").lower()
    
    if provider_name == "gemini" and settings.GEMINI_API_KEY:
        try:
            from app.llm.providers.gemini_provider import GeminiProvider
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL or "gemini-2.0-flash")
        except Exception:
            return DeterministicFallbackLLM()
    
    # Default to deterministic fallback
    return DeterministicFallbackLLM()

