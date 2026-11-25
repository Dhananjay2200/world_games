"""
Topics Discovery and Management Routes.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.session import get_db
from app.database.models import GameTopic
from app.services.discovery_service import DiscoveryService, WORLD_REGIONS, GAME_CATEGORIES

router = APIRouter(prefix="/topics", tags=["Topics"])


class DiscoverTopicRequest(BaseModel):
    region: Optional[str] = None
    category: Optional[str] = None


@router.get("")
def list_topics(
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Lists discovered game topics with optional region, genre and status filters."""
    q = db.query(GameTopic)
    if region and region != "All":
        q = q.filter(GameTopic.origin_region == region)
    if category and category != "All":
        q = q.filter(GameTopic.category == category)
    if status:
        q = q.filter(GameTopic.status == status)

    total = q.count()
    topics = q.order_by(GameTopic.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "topics": topics,
    }


@router.get("/taxonomy")
def get_taxonomy():
    """Returns supported global regions and game categories."""
    return {
        "regions": WORLD_REGIONS,
        "categories": GAME_CATEGORIES,
    }


@router.post("/discover")
async def trigger_discovery(
    req: DiscoverTopicRequest,
    db: Session = Depends(get_db),
):
    """Forces discovery of a novel game topic."""
    service = DiscoveryService(db)
    result = await service.discover_new_game(
        target_region=req.region,
        target_genre=req.category,
    )
    return {"status": "success", "discovered_topic": result}
