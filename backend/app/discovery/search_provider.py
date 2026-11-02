from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings
from app.core.logging import app_logger

class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Executes a web search query.
        Returns a list of dicts: [{"title": "...", "url": "...", "snippet": "..."}]
        """
        pass


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """Zero-key, polite HTML search provider using DuckDuckGo HTML endpoint."""

    SEARCH_URL = "https://html.duckduckgo.com/html/"

    def search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        results: List[Dict[str, str]] = []
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.post(
                    self.SEARCH_URL,
                    data={"q": query},
                    headers=headers,
                )
                if resp.status_code != 200:
                    app_logger.warning(f"DuckDuckGo search returned HTTP {resp.status_code}")
                    return results

                soup = BeautifulSoup(resp.text, "html.parser")
                links = soup.select(".result__title .result__url, a.result__url")
                snippets = soup.select(".result__snippet")
                titles = soup.select(".result__title")

                for i in range(min(limit, len(links))):
                    url = links[i].get("href") or links[i].text.strip()
                    title = titles[i].text.strip() if i < len(titles) else ""
                    snippet = snippets[i].text.strip() if i < len(snippets) else ""
                    if url and not url.startswith("/"):
                        if not url.startswith("http"):
                            url = f"https://{url}"
                        results.append({"title": title, "url": url, "snippet": snippet})

        except Exception as e:
            app_logger.warning(f"DuckDuckGo search error: {e}")
        return results


class MockSearchProvider(BaseSearchProvider):
    """Deterministic mock provider for unit testing without network dependency."""

    def __init__(self, predefined_results: Optional[List[Dict[str, str]]] = None):
        self.predefined_results = predefined_results or [
            {
                "title": "Mercor AI - Elite AI Talent and Evaluators",
                "url": "https://mercor.com",
                "snippet": "Mercor hires global AI engineers and model trainers worldwide.",
            },
            {
                "title": "Invisible Technologies - Advanced AI Training",
                "url": "https://invisible.co",
                "snippet": "Join global AI evaluation operations, prompt review, and RLHF.",
            }
        ]

    def search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        return self.predefined_results[:limit]


def get_search_provider() -> BaseSearchProvider:
    provider_type = (settings.SEARCH_PROVIDER or "duckduckgo").lower()
    if provider_type == "duckduckgo":
        return DuckDuckGoSearchProvider()
    return DuckDuckGoSearchProvider()
