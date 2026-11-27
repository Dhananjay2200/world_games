"""
WorldGames AI - Multi-Source Research Service.
Integrates Wikipedia REST/Action API, Wikidata, and Tavily Search API to gather
authentic facts, rules, dimensions, equipment, and historical context.
"""

from datetime import date
from typing import Dict, List, Optional
import httpx
from app.config import get_settings
from app.services.apitube_service import APITubeNewsService
from app.services.espn_news_service import ESPNNewsService
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

    async def fetch_tavily_research(
        self,
        topic_name: str,
        category: str,
        article_type: str = "PLAYBOOK",
        news_angle: Optional[str] = None,
    ) -> List[Dict]:
        """Queries Tavily Search API for rules (PLAYBOOK) or latest breaking news (NEWS)."""
        if not self.settings.TAVILY_API_KEY or self.settings.TAVILY_API_KEY.startswith("tvly-placeholder"):
            return []

        url = "https://api.tavily.com/search"
        current_year = date.today().year
        if article_type == "NEWS":
            query_text = f"{topic_name} {news_angle or 'latest breaking news results tournament'} {current_year}"
            payload = {
                "api_key": self.settings.TAVILY_API_KEY,
                "query": query_text,
                "topic": "news",
                "search_depth": self.settings.TAVILY_SEARCH_DEPTH,
                "include_answer": True,
                "max_results": 5,
            }
        else:
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

    async def fetch_espn_news(self, topic_name: str, news_angle: Optional[str] = None) -> List[Dict]:
        """Queries ESPN live sports news API for Cricket and global sports headlines."""
        service = ESPNNewsService()
        query = (topic_name or "").strip() or "sports"
        items = await service.fetch_sports_news(query=query, limit=5)
        if not items and news_angle:
            # Try general sports feed or match keywords from news_angle
            items = await service.fetch_sports_news(query="sports", limit=5)
        elif not items:
            items = await service.fetch_sports_news(query="sports", limit=5)
        return [
            {
                "title": item.get("title", ""),
                "content": item.get("story_text") or item.get("description", ""),
                "url": item.get("url", ""),
                "published_at": item.get("published_at"),
                "source": item.get("source_name", "ESPN"),
            }
            for item in items
        ]

    async def fetch_apitube_news(self, topic_name: str, news_angle: Optional[str] = None) -> List[Dict]:
        """Queries APITube News API for recent live sports news matching the topic or general sports."""
        service = APITubeNewsService()
        query = (topic_name or "").strip() or "sports"
        items = await service.fetch_sports_news(query=query, limit=5)
        if not items:
            # Fallback to latest breaking global sports headlines if niche sport name had no exact title match
            items = await service.fetch_sports_news(query="sports", limit=5)
        return [
            {
                "title": item.get("title", ""),
                "content": item.get("description", ""),
                "url": item.get("url", ""),
                "published_at": item.get("published_at"),
                "source": item.get("source_name", "APITube"),
            }
            for item in items
        ]

    async def gather_full_research(
        self,
        topic_name: str,
        category: str,
        region: str,
        country: str,
        article_type: str = "PLAYBOOK",
        news_angle: Optional[str] = None,
    ) -> Dict:
        """Assembles research dossier from Wikipedia, Tavily, and (for NEWS) ESPN + APITube."""
        wiki_data = await self.fetch_wikipedia_summary(topic_name)
        tavily_data = await self.fetch_tavily_research(
            topic_name,
            category,
            article_type=article_type,
            news_angle=news_angle,
        )
        espn_data = (
            await self.fetch_espn_news(topic_name, news_angle=news_angle)
            if article_type == "NEWS"
            else []
        )
        apitube_data = (
            await self.fetch_apitube_news(topic_name, news_angle=news_angle)
            if article_type == "NEWS"
            else []
        )

        live_news = espn_data + apitube_data
        combined_findings = live_news + tavily_data

        dossier = {
            "topic_name": topic_name,
            "category": category,
            "origin_region": region,
            "origin_country": country,
            "wikipedia_summary": wiki_data.get("extract") if wiki_data else "",
            "search_findings": combined_findings,
            "espn_news": espn_data,
            "apitube_news": apitube_data,
            "live_news": live_news,
            "citations": [
                r.get("url")
                for r in combined_findings
                if r.get("url") and r.get("url") != "tavily_answer"
            ],
        }
        return dossier
