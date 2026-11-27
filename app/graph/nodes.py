"""
LangGraph Nodes for WorldGames AI Pipeline.
"""

import json
from typing import Dict, Any
from app.graph.state import WorldGamesState
from app.services.discovery_service import DiscoveryService, generate_canonical_key
from app.services.research_service import ResearchService
from app.services.writer_service import WriterService
from app.services.seo_service import SEOService
from app.services.image_service import ImageService
from app.services.evaluator_service import EvaluatorService
from app.services.publisher_service import PublisherService
from app.services.espn_news_service import ESPNNewsService
from app.services.apitube_service import APITubeNewsService
from app.database.session import SessionLocal
from app.database.models import GameTopic, GameArticle
from app.utils.logging import logger


async def discover_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 1: Discovers or validates a world game/sport."""
    logger.info("[Workflow] Node 1: Running Discovery...")
    db = SessionLocal()
    try:
        service = DiscoveryService(db)
        if state.get("topic") and state["topic"].get("name"):
            t = state["topic"]
            canonical = generate_canonical_key(t["name"])
            topic_data = {
                "name": t["name"],
                "canonical_name": canonical,
                "category": t.get("category", "Indigenous, Folk & Traditional Games"),
                "origin_region": t.get("origin_region", "Global & Multi-Regional"),
                "origin_country": t.get("origin_country", "Global"),
            }
        else:
            topic_data = await service.discover_new_game(
                target_region=state.get("target_region"),
                target_genre=state.get("target_genre"),
            )
        return {"topic": topic_data, "errors": state.get("errors", [])}
    finally:
        db.close()


async def deduplicate_node(state: WorldGamesState) -> Dict[str, Any]:
    """
    Node 2: Deduplication Gate.
    - If article_type == "NEWS": Checks whether this specific news story/angle has already been published.
      It DOES NOT reject the base sport, allowing fresh news stories for existing sports.
    - If article_type == "PLAYBOOK": Ensures only 1 foundational guide per game exists.
    """
    logger.info("[Workflow] Node 2: Checking Deduplication...")
    topic = state.get("topic", {})
    article_type = state.get("article_type", "PLAYBOOK")
    db = SessionLocal()
    try:
        if article_type == "NEWS":
            news_angle = state.get("news_angle", "Breaking News")
            news_slug_check = generate_canonical_key(f"{topic.get('name', '')} news {news_angle}")
            # Check if this exact news article already exists
            existing_news = db.query(GameArticle).filter(
                GameArticle.slug.ilike(f"%{news_slug_check[:40]}%")
            ).first()

            if existing_news:
                logger.warning(f"[Workflow] Duplicate news story detected: '{news_angle}'. Ending pipeline.")
                return {"is_duplicate": True, "status": "DUPLICATE_REJECTED"}
            return {"is_duplicate": False, "status": "NOVEL_NEWS_STORY"}
        else:
            # Playbook mode: 1 foundational guide per sport
            canonical = topic.get("canonical_name", generate_canonical_key(topic.get("name", "")))
            existing_playbook = db.query(GameArticle).join(GameTopic).filter(
                GameTopic.canonical_name == canonical,
                GameArticle.article_type == "PLAYBOOK",
                GameArticle.status == "PUBLISHED"
            ).first()

            if existing_playbook:
                topic_name = topic.get("name", "")
                logger.info(
                    f"[Deduplicate] Playbook for sport '{topic_name}' already exists in DB -> moving to latest NEWS check (ESPN & APITube)..."
                )

                recent_news_rows = (
                    db.query(GameArticle.title)
                    .filter(GameArticle.article_type == "NEWS")
                    .order_by(GameArticle.created_at.desc())
                    .limit(100)
                    .all()
                )
                seen_titles = {r[0].lower().strip() for r in recent_news_rows if r[0]}

                live_candidates = await ESPNNewsService().fetch_sports_news(query=topic_name, limit=5)
                if not live_candidates:
                    live_candidates = await APITubeNewsService().fetch_sports_news(query=topic_name, limit=5)

                # If exact multi-word name returned 0 hits (e.g. 'Amateur Wrestling' or 'Australian Rules Football (AFL)'),
                # try the primary sport noun/keyword (without parentheticals or modifiers)
                if not live_candidates:
                    base_clean = topic_name.split("(")[0].strip()
                    words = [w for w in base_clean.split() if len(w) > 3]
                    if words:
                        short_kw = words[-1]
                        live_candidates = await ESPNNewsService().fetch_sports_news(query=short_kw, limit=5)
                        if not live_candidates:
                            live_candidates = await APITubeNewsService().fetch_sports_news(query=short_kw, limit=5)

                for item in live_candidates:
                    headline = (item.get("title") or "").strip()
                    if not headline:
                        continue
                    h_lower = headline.lower()
                    if any(h_lower in s or s in h_lower or h_lower[:35] in s for s in seen_titles):
                        continue

                    logger.info(
                        f"[Workflow] Playbook for '{topic_name}' already exists -> moving immediately to latest NEWS: '{headline[:70]}'"
                    )
                    return {
                        "is_duplicate": False,
                        "article_type": "NEWS",
                        "news_angle": headline,
                        "status": "PLAYBOOK_EXISTS_SWITCHED_TO_NEWS",
                    }

                logger.warning(
                    f"[Workflow] Playbook already exists for '{topic_name}' and no new live news was found. Ending pipeline."
                )
                return {"is_duplicate": True, "status": "DUPLICATE_REJECTED"}
            return {"is_duplicate": False, "status": "NOVEL_PLAYBOOK"}
    finally:
        db.close()


async def research_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 3: Gathers Wikipedia data, Wikidata, and Tavily search findings."""
    logger.info("[Workflow] Node 3: Conducting Deep Research...")
    topic = state["topic"]
    service = ResearchService()
    dossier = await service.gather_full_research(
        topic_name=topic["name"],
        category=topic["category"],
        region=topic["origin_region"],
        country=topic.get("origin_country", "Global"),
        article_type=state.get("article_type", "PLAYBOOK"),
        news_angle=state.get("news_angle"),
    )
    return {"research": dossier}


async def writer_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 4: Produces either 12-section Playbook or Sports News Dispatch."""
    logger.info("[Workflow] Node 4: Writing Article...")
    research_data = state["research"]
    service = WriterService()
    article = await service.generate_game_article(
        research_dossier=research_data,
        article_type=state.get("article_type", "PLAYBOOK"),
        news_angle=state.get("news_angle"),
    )
    return {"article": article}


async def seo_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 5: Computes SEO metadata, slug, reading time, and search keywords."""
    logger.info("[Workflow] Node 5: Optimizing SEO...")
    topic = state["topic"]
    article = state["article"]
    article_type = state.get("article_type", "PLAYBOOK")
    service = SEOService()
    
    prefix = f"{topic['name']} news" if article_type == "NEWS" else topic['name']
    seo_data = await service.generate_seo_metadata(
        topic_name=prefix,
        category=topic["category"],
        region=topic["origin_region"],
        country=topic.get("origin_country", "Global"),
        summary=article["summary"],
    )
    reading_time = service.calculate_reading_time(article["content"])
    seo_data["reading_time_minutes"] = reading_time
    return {"seo": seo_data}


async def image_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 6: Discovers Wikimedia Commons permitted imagery and attribution."""
    logger.info("[Workflow] Node 6: Discovering Media & Images...")
    topic = state["topic"]
    service = ImageService()
    image_data = await service.get_permitted_image(topic["name"], topic["category"])
    return {"image": image_data}


async def quality_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 7: Quality audit (requires >= 8.0/10 to pass)."""
    logger.info("[Workflow] Node 7: Executing Quality Gate...")
    topic = state["topic"]
    article = state["article"]
    service = EvaluatorService()
    evaluation = await service.evaluate_article(
        topic_name=topic["name"],
        category=topic["category"],
        content=article["content"],
        article_type=state.get("article_type", "PLAYBOOK"),
    )
    rev_count = state.get("revision_count", 0)
    evaluation["revision_count"] = rev_count
    return {"evaluation": evaluation}


async def revision_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 8: Corrective revision loop when article scores below threshold."""
    logger.info("[Workflow] Node 8: Applying Corrective Revisions...")
    topic = state["topic"]
    article = state["article"]
    evaluation = state["evaluation"]
    service = EvaluatorService()

    feedback = evaluation.get("actionable_feedback", "Improve clarity and coverage.")
    revised_content = await service.revise_article(topic["name"], article["content"], feedback)
    
    updated_article = dict(article)
    updated_article["content"] = revised_content
    rev_count = state.get("revision_count", 0) + 1
    
    return {
        "article": updated_article,
        "revision_count": rev_count,
    }


async def publisher_node(state: WorldGamesState) -> Dict[str, Any]:
    """Node 9: Persists article to PostgreSQL without touching old existing playbooks."""
    logger.info("[Workflow] Node 9: Persisting Article & Publishing...")
    db = SessionLocal()
    try:
        service = PublisherService(db)
        saved = service.save_and_publish_article(
            topic_data=state["topic"],
            article_data=state["article"],
            seo_data=state["seo"],
            image_data=state["image"],
            eval_data=state["evaluation"],
            article_type=state.get("article_type", "PLAYBOOK"),
        )
        return {
            "published_article_id": saved.id,
            "status": saved.status,
        }
    finally:
        db.close()
