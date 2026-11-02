import json
import httpx
from typing import Dict, Any
from app.llm.base import BaseLLMProvider, DeterministicFallbackLLM
from app.core.logging import app_logger

class GeminiProvider(BaseLLMProvider):
    """Integrates with Google Gemini API via lightweight HTTP requests."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        self.fallback = DeterministicFallbackLLM()

    async def analyze_opportunity(
        self,
        title: str,
        description: str,
        profile_summary: str,
    ) -> Dict[str, Any]:
        prompt = f"""
You are an expert AI career intelligence analyst.
Analyze the following job opportunity for a Senior AI & ML Engineer based in Egypt:

JOB TITLE: {title}
JOB DESCRIPTION:
{description[:2000]}

CANDIDATE PROFILE:
{profile_summary}

Respond ONLY in valid JSON matching this exact structure:
{{
  "relevance_summary": "1-2 concise sentences summarizing fit",
  "key_strengths": ["strength 1", "strength 2"],
  "risks": ["risk 1", "risk 2"],
  "recommended_approach": "Actionable advice on application"
}}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidate = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(candidate)
                else:
                    app_logger.warning(f"Gemini API returned status {resp.status_code}, falling back to deterministic.")
                    return await self.fallback.analyze_opportunity(title, description, profile_summary)
        except Exception as e:
            app_logger.warning(f"Gemini API call failed: {e}. Using deterministic fallback.")
            return await self.fallback.analyze_opportunity(title, description, profile_summary)
