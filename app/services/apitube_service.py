"""
WorldGames AI - APITube Live Sports News Integration Service.
Fetches real-time global sports news sorted by latest `published_at` descending
from APITube News API without altering existing Playbook logic.
"""

import re
from typing import Dict, List, Optional, Set
import httpx
from app.config import get_settings
from app.services.cache_service import cache_service
from app.utils.logging import logger

APITUBE_SPORTS_CATEGORY_ID = "medtop:15000000"

SPORT_TOPIC_MAP = [
    (["esport", "gaming", "valorant", "league of legends", "dota", "cs2", "fortnite", "twitch", "nintendo", "playstation", "xbox"],
     "Esports", "Esports & Competitive Digital Gaming"),
    (["ufc", "mma", "boxing", "wrestling", "judo", "karate", "taekwondo", "muay thai", "bout", "fighter"],
     "Combat Sports", "Combat Sports & Martial Arts"),
    (["soccer", "premier league", "champions league", "la liga", "bundesliga", "serie a", "fifa", "liverpool", "chelsea", "arsenal", "manchester"],
     "Association Football", "Field & Team Ball Sports"),
    (["nfl", "quarterback", "touchdown", "super bowl", "college football"],
     "American Football", "Field & Team Ball Sports"),
    (["nba", "wnba", "basketball", "ncaa"],
     "Basketball", "Field & Team Ball Sports"),
    (["rugby", "scrum", "six nations", "super league"],
     "Rugby", "Field & Team Ball Sports"),
    (["cricket", "ipl", "bbl", "test match", "t20", "odi", "wicket"],
     "Cricket", "Field & Team Ball Sports"),
    (["tennis", "atp", "wta", "wimbledon", "grand slam", "squash", "psa", "badminton", "pickleball", "padel"],
     "Tennis & Racquet Sports", "Racquet & Paddle Sports"),
    (["nhl", "hockey", "whl", "curling", "ski", "snowboard", "winter olympics"],
     "Ice Hockey", "Winter & Ice Sports"),
    (["swim", "rowing", "canoe", "surfing", "sailing", "water polo"],
     "Aquatic Sports", "Water & Aquatic Sports"),
    (["golf", "pga", "archery", "shooting", "darts", "snooker", "billiards"],
     "Golf & Precision Sports", "Target & Precision Sports"),
    (["chess", "poker", "checkers", "backgammon", "go "],
     "Mind Sports", "Mind Sports & Tabletop Games"),
    (["f1", "formula 1", "motogp", "marathon", "track", "athletics", "sprint", "gymnastics", "olympic"],
     "Athletics & Racing", "Athletic & Gymnastic Disciplines"),
]


class APITubeNewsService:
    """Client for fetching live latest sports news dispatches via APITube."""

    def __init__(self):
        self.settings = get_settings()

    @staticmethod
    def _matches_keyword(kw: str, text: str) -> bool:
        return bool(re.search(rf"\b{re.escape(kw.strip())}\b", text))

    @classmethod
    def _is_relevant_sport_item(cls, item: Dict, is_general_sports: bool) -> bool:
        if not is_general_sports:
            return True
        cats = [c.get("name", "").lower() for c in (item.get("categories") or [])]
        if any("sport" in c or "esport" in c or "gaming" in c for c in cats):
            return True
        title_l = (item.get("title") or "").lower()
        return any(cls._matches_keyword(kw, title_l) for kws, _, _ in SPORT_TOPIC_MAP for kw in kws)

    @classmethod
    def map_article_to_worldgames(cls, item: Dict) -> Dict:
        """Maps an APITube news item to WorldGames topic_name, category, region, and news_angle."""
        text_blob = " ".join([
            (item.get("title") or "").lower(),
            (item.get("description") or "").lower(),
            " ".join(item.get("categories") or []).lower(),
        ])
        topic_name = "Olympic Sports"
        category = "Athletic & Gymnastic Disciplines"

        for kws, t_name, cat_name in SPORT_TOPIC_MAP:
            if any(cls._matches_keyword(kw, text_blob) for kw in kws):
                topic_name = t_name
                category = cat_name
                break

        return {
            "topic_name": topic_name,
            "category": category,
            "region": "Global & Multi-Regional",
            "country": "Global",
            "news_angle": (item.get("title") or "").strip(),
            "published_at": item.get("published_at"),
            "source_url": item.get("url"),
        }

    async def fetch_sports_news(
        self,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Queries APITube `/v1/news/everything` sorted by `published_at` desc.
        - General queries ('sports', 'all', None) query the IPTC Sports category (`medtop:15000000`).
        - Specific game/sport queries search within Sports (`category.id` + `title`), falling back to `title` search if needed.
        """
        api_key = (self.settings.API_TUBE_KEY or "").strip()
        if not api_key or api_key.startswith("your_"):
            logger.debug("[APITube] API_TUBE_KEY not configured; skipping live news fetch.")
            return []

        raw_q = (query or "").strip()
        is_general_sports = not raw_q or raw_q.lower() in ("sports", "sport", "all", "latest")
        cache_key = f"apitube:latest:{raw_q.lower() or 'all'}:{limit}"

        cached, _ = cache_service.get(cache_key)
        if cached is not None:
            return cached

        base_url = self.settings.API_TUBE_BASE_URL.rstrip("/")
        url = f"{base_url}/news/everything"
        per_page = max(1, min(limit, 10))
        headers = {
            "X-API-Key": api_key,
            "Accept": "application/json",
        }

        params = {
            "language.code": "en",
            "per_page": per_page,
            "sort_by": "published_at",
            "sort_order": "desc",
            "category.id": APITUBE_SPORTS_CATEGORY_ID,
        }
        if not is_general_sports:
            params["title"] = raw_q

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"[APITube] Non-200 response ({resp.status_code}): {resp.text[:200]}")
                    return []

                data = resp.json()
                raw_results = data.get("results", []) or []

                if not raw_results and not is_general_sports:
                    fallback_params = {
                        "language.code": "en",
                        "per_page": per_page,
                        "sort_by": "published_at",
                        "sort_order": "desc",
                        "title": raw_q,
                    }
                    fb_resp = await client.get(url, params=fallback_params, headers=headers)
                    if fb_resp.status_code == 200:
                        raw_results = fb_resp.json().get("results", []) or []

                articles: List[Dict] = []
                for item in raw_results:
                    if not self._is_relevant_sport_item(item, is_general_sports):
                        continue
                    source_obj = item.get("source") or {}
                    source_name = (
                        source_obj.get("domain")
                        or source_obj.get("name")
                        or "APITube Wire"
                    )
                    cats = [
                        c.get("name")
                        for c in (item.get("categories") or [])
                        if isinstance(c, dict) and c.get("name")
                    ]
                    articles.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "description": item.get("description") or item.get("summary") or "",
                        "url": item.get("href") or "",
                        "image": item.get("image") or "",
                        "published_at": item.get("published_at"),
                        "source_name": source_name,
                        "categories": cats,
                        "is_breaking": bool(item.get("is_breaking", False)),
                        "keywords": item.get("keywords") or [],
                        "read_time": item.get("read_time") or 3,
                    })

                if articles:
                    cache_service.set(cache_key, articles)
                logger.info(
                    f"[+] APITube fetched {len(articles)} latest sports news items for '{raw_q or 'sports'}'."
                )
                return articles
        except Exception as exc:
            logger.warning(f"[APITube] Sports news fetch error for '{raw_q or 'sports'}': {exc}")
            return []

    async def pick_fresh_sports_story(self, existing_titles: Optional[Set[str]] = None) -> Optional[Dict]:
        """
        Finds the freshest APITube sports headline that has not yet been covered
        in the database, mapped ready for the LangGraph NEWS pipeline.
        """
        seen = {t.lower().strip() for t in (existing_titles or set()) if t}
        items = await self.fetch_sports_news(query="sports", limit=10)
        for item in items:
            headline = (item.get("title") or "").strip()
            if not headline:
                continue
            h_lower = headline.lower()
            # Skip if already published or very similar title already exists
            if any(h_lower in s or s in h_lower or h_lower[:35] in s for s in seen):
                continue
            return self.map_article_to_worldgames(item)
        return None
