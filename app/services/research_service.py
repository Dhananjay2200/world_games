"""
WorldGames AI - Multi-Source Research Service.
Integrates Wikipedia REST/Action API, Wikidata, and Tavily Search API to gather
authentic facts, rules, dimensions, equipment, and historical context.
"""

from typing import Dict, List, Optional
import httpx
from app.config import get_settings
from app.utils.logging import logger


class ResearchService:
    def __init__(self):
        self.settings = get_settings()

    async def fetch_wikipedia_summary(self, topic_name: str) -> Optional[Dict]:
        """Fetches extracts and page data from Wikipedia API."""
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": topic_name,
            "prop": "extracts|pageprops|info",
            "exintro": "1",
            "explaintext": "1",
            "redirects": "1",
        }
        headers = {"User-Agent": "WorldGamesAI/1.0 (contact: info@worldgames.ai)"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id, page in pages.items():
                        if page_id != "-1":
                            return {
                                "title": page.get("title", topic_name),
                                "extract": page.get("extract", ""),
                                "page_id": page_id,
                                "source": "Wikipedia",
                            }
        except Exception as e:
            logger.warning(f"Wikipedia fetch error for '{topic_name}': {e}")
        return None

    async def fetch_tavily_research(self, topic_name: str, category: str) -> List[Dict]:
        """Queries Tavily Search API for game rules, equipment, and tournament records."""
        if not self.settings.TAVILY_API_KEY or self.settings.TAVILY_API_KEY.startswith("tvly-placeholder"):
            return []

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.settings.TAVILY_API_KEY,
            "query": f"{topic_name} {category} official rules equipment field dimensions history tournaments",
            "search_depth": self.settings.TAVILY_SEARCH_DEPTH,
            "include_answer": True,
            "max_results": 5,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    answer = data.get("answer")
                    if answer:
                        results.append({"title": f"{topic_name} Overview", "content": answer, "url": "tavily_answer"})
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", ""),
                            "content": r.get("content", ""),
                            "url": r.get("url", ""),
                        })
                    return results
        except Exception as e:
            logger.warning(f"Tavily search error for '{topic_name}': {e}")
        return []

    async def gather_full_research(self, topic_name: str, category: str, region: str, country: str) -> Dict:
        """Assembles research dossier from Wikipedia and Tavily."""
        wiki_data = await self.fetch_wikipedia_summary(topic_name)
        tavily_data = await self.fetch_tavily_research(topic_name, category)

        dossier = {
            "topic_name": topic_name,
            "category": category,
            "origin_region": region,
            "origin_country": country,
            "wikipedia_summary": wiki_data.get("extract") if wiki_data else "",
            "search_findings": tavily_data,
            "citations": [r.get("url") for r in tavily_data if r.get("url") and r.get("url") != "tavily_answer"],
        }
        return dossier
