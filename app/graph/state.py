"""
WorldGames AI - LangGraph State Definition.
"""

from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict


class WorldGamesState(TypedDict, total=False):
    # Discovery phase
    topic: Dict[str, Any]
    target_region: Optional[str]
    target_genre: Optional[str]
    article_type: Optional[str]  # "PLAYBOOK" or "NEWS"
    news_angle: Optional[str]    # Custom news headline/event angle
    is_duplicate: bool
    
    # Research phase
    research: Dict[str, Any]
    
    # Writing & SEO phase
    article: Dict[str, Any]
    seo: Dict[str, Any]
    
    # Media & Image phase
    image: Dict[str, Any]
    
    # Quality gate & Revision phase
    evaluation: Dict[str, Any]
    revision_count: int
    max_revisions: int
    
    # Final publication
    published_article_id: Optional[int]
    status: str
    errors: List[str]
