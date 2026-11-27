"""
Live Sports News API Route powered by ESPN & APITube.
Supports fetching live breaking news from ESPN (`now.core.api.espn.com`), APITube, or both combined.
"""

from typing import Literal, Optional
from fastapi import APIRouter, Query
from app.services.apitube_service import APITubeNewsService
from app.services.espn_news_service import ESPNNewsService

router = APIRouter(prefix="/news", tags=["Live Sports News"])


@router.get("/live")
async def get_live_sports_news(
    query: Optional[str] = Query("sports", description="Sport, game, or league search term (e.g. cricket, football, sports)"),
    limit: int = Query(10, ge=1, le=10, description="Number of news articles per source (up to 10)"),
    source: Literal["all", "espn", "apitube"] = Query("all", description="News provider: all, espn, or apitube"),
):
    """Fetches live global sports news headlines via ESPN and/or APITube."""
    espn_items = []
    apitube_items = []

    if source in ("all", "espn"):
        espn_items = await ESPNNewsService().fetch_sports_news(query=query, limit=limit)
    if source in ("all", "apitube"):
        apitube_items = await APITubeNewsService().fetch_sports_news(query=query, limit=limit)

    combined = espn_items + apitube_items
    combined.sort(key=lambda x: str(x.get("published_at") or ""), reverse=True)

    return {
        "status": "ok",
        "source": source,
        "query": query,
        "count": len(combined),
        "articles": combined[:limit] if source != "all" else combined,
    }
