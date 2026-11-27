"""
WorldGames AI - ESPN Live Sports News Service & LangChain Tool.
Provides real-time breaking sports news (Cricket, Basketball, Football, etc.)
from ESPN Core API alongside APITube without altering existing Playbook code.
"""

import re
from typing import Dict, List, Optional, Set
import httpx
import requests
from langchain_core.tools import tool
from app.services.apitube_service import APITubeNewsService
from app.services.cache_service import cache_service
from app.utils.logging import logger

ESPN_NEWS_URL = "https://now.core.api.espn.com/v1/sports/news"


@tool
def get_latest_sports_news(limit: int = 5) -> str:
    """Fetches the latest breaking sports headlines and summaries."""
    url = f"{ESPN_NEWS_URL}?limit={limit}"
    data = requests.get(url, timeout=15).json()

    articles = []
    for item in data.get("headlines", []):
        title = item.get("headline", "")
        desc = item.get("description", "")
        articles.append(f"- {title}: {desc}")

    return "\n".join(articles)


def _strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    return " ".join(text.split())


class ESPNNewsService:
    """Async client for fetching live breaking sports news from ESPN Core API."""

    async def fetch_sports_news(
        self,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Fetches latest breaking sports headlines from ESPN (`now.core.api.espn.com`).
        If `query` is specified (e.g. 'Cricket', 'Basketball'), pulls a wider batch
        and filters to headlines/categories/descriptions matching that sport.
        """
        clean_query = (query or "").strip()
        is_general = not clean_query or clean_query.lower() in ("sports", "sport", "all", "latest")
        fetch_limit = max(1, min(limit if is_general else max(limit * 3, 25), 50))
        cache_key = f"espn:latest:{clean_query.lower() or 'all'}:{limit}"

        cached, _ = cache_service.get(cache_key)
        if cached is not None:
            return cached

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(ESPN_NEWS_URL, params={"limit": fetch_limit})
                if resp.status_code != 200:
                    logger.warning(f"[ESPN] Non-200 response ({resp.status_code}): {resp.text[:200]}")
                    return []

                headlines = resp.json().get("headlines", []) or []
                articles: List[Dict] = []

                for item in headlines:
                    title = (item.get("headline") or item.get("title") or "").strip()
                    desc = (item.get("description") or "").strip()
                    story_clean = _strip_html(item.get("story") or "")
                    cats = [
                        (c.get("description") or c.get("type") or "").strip()
                        for c in (item.get("categories") or [])
                        if isinstance(c, dict) and (c.get("description") or c.get("type"))
                    ]
                    web_url = ((item.get("links") or {}).get("web") or {}).get("href") or ""
                    images = item.get("images") or []
                    img_url = images[0].get("url", "") if images and isinstance(images[0], dict) else ""

                    if not is_general:
                        q_lower = clean_query.lower()
                        searchable = " ".join([title, desc, " ".join(cats), web_url]).lower()
                        if not re.search(rf"\b{re.escape(q_lower)}\b", searchable):
                            continue

                    articles.append({
                        "id": item.get("id"),
                        "title": title,
                        "description": desc,
                        "story_text": story_clean[:1200] if story_clean else desc,
                        "url": web_url,
                        "image": img_url,
                        "published_at": item.get("published") or item.get("originallyPosted"),
                        "source_name": "ESPN",
                        "categories": cats,
                        "is_breaking": True,
                        "keywords": item.get("keywords") or [],
                        "read_time": 3,
                    })
                    if len(articles) >= limit:
                        break

                if articles:
                    cache_service.set(cache_key, articles)
                logger.info(f"[+] ESPN fetched {len(articles)} live sports news items for '{clean_query or 'sports'}'.")
                return articles
        except Exception as exc:
            logger.warning(f"[ESPN] Sports news fetch error for '{clean_query or 'sports'}': {exc}")
            return []

    async def pick_fresh_sports_story(self, existing_titles: Optional[Set[str]] = None) -> Optional[Dict]:
        """
        Finds the freshest ESPN sports headline not yet covered in the database,
        mapped ready for the LangGraph NEWS pipeline.
        """
        seen = {t.lower().strip() for t in (existing_titles or set()) if t}
        items = await self.fetch_sports_news(query="sports", limit=15)
        for item in items:
            headline = (item.get("title") or "").strip()
            if not headline:
                continue
            h_lower = headline.lower()
            if any(h_lower in s or s in h_lower or h_lower[:35] in s for s in seen):
                continue
            return APITubeNewsService.map_article_to_worldgames(item)
        return None
