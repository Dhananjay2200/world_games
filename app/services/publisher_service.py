"""
WorldGames AI - Publisher Service.
Persists generated articles, logs evaluations, manages publication status,
handles multi-criteria combinatorial filtering, and serves sub-millisecond cached payloads.
"""

from datetime import datetime, date
import json
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.models import GameTopic, GameArticle, QualityEvaluation, AutomationState
from app.services.cache_service import cache_service
from app.utils.logging import logger


def serialize_article(article: GameArticle) -> Dict[str, Any]:
    """
    Converts a SQLAlchemy GameArticle ORM object into a plain, JSON-safe dictionary.
    Prevents DetachedInstanceError across threads and enables safe RAM caching.
    """
    return {
        "id": article.id,
        "topic_id": article.topic_id,
        "article_type": article.article_type,
        "title": article.title,
        "slug": article.slug,
        "meta_description": article.meta_description,
        "summary": article.summary,
        "content": article.content,
        "category": article.category,
        "origin_region": article.origin_region,
        "origin_country": article.origin_country,
        "score": article.score,
        "status": article.status,
        "primary_image_url": article.primary_image_url,
        "image_caption": article.image_caption,
        "image_attribution": article.image_attribution,
        "image_license": article.image_license,
        "seo_keywords": article.seo_keywords,
        "reading_time_minutes": article.reading_time_minutes,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    }


class PublisherService:
    def __init__(self, db: Session):
        self.db = db

    def save_and_publish_article(
        self,
        topic_data: Dict,
        article_data: Dict,
        seo_data: Dict,
        image_data: Dict,
        eval_data: Dict,
        article_type: str = "PLAYBOOK",
    ) -> GameArticle:
        """
        Saves article to database.
        - For PLAYBOOK: Creates or updates the foundational guide.
        - For NEWS: Always creates a separate NEW article row without altering the old playbook!
        """
        # 1. Upsert Topic
        c_name = topic_data.get("canonical_name", topic_data["name"].lower().strip())
        topic = self.db.query(GameTopic).filter(GameTopic.canonical_name == c_name).first()
        if not topic:
            topic = GameTopic(
                name=topic_data["name"],
                canonical_name=c_name,
                category=topic_data["category"],
                origin_region=topic_data["origin_region"],
                origin_country=topic_data.get("origin_country", "Global"),
                status="GENERATED",
            )
            self.db.add(topic)
            self.db.flush()
        else:
            topic.status = "GENERATED"

        # 2. Determine Publication Status
        score = float(eval_data.get("overall_score", 8.0))
        passed = eval_data.get("passed", score >= 8.0)
        status = "PUBLISHED" if passed else "IN_REVIEW"
        pub_time = datetime.utcnow() if status == "PUBLISHED" else None

        # Ensure unique slug
        base_slug = seo_data.get("slug", "game-article")
        unique_slug = base_slug
        counter = 1
        while self.db.query(GameArticle).filter(GameArticle.slug == unique_slug).first():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        # 3. Create Article Row
        # If it's a NEWS article, we ALWAYS add a brand-new row so old playbooks are preserved
        article = GameArticle(
            topic_id=topic.id,
            article_type=article_type,
            title=article_data["title"],
            slug=unique_slug,
            meta_description=seo_data.get("meta_description", "")[:500],
            summary=article_data.get("summary", ""),
            content=article_data["content"],
            category=topic.category,
            origin_region=topic.origin_region,
            origin_country=topic.origin_country,
            score=score,
            status=status,
            primary_image_url=image_data.get("image_url"),
            image_caption=image_data.get("caption"),
            image_attribution=image_data.get("attribution"),
            image_license=image_data.get("license"),
            seo_keywords=json.dumps(seo_data.get("keywords", [])),
            reading_time_minutes=seo_data.get("reading_time_minutes", 6),
            published_at=pub_time,
        )
        self.db.add(article)
        self.db.flush()

        # 4. Record Evaluation Log
        evaluation = QualityEvaluation(
            article_id=article.id,
            score=score,
            passed=passed,
            criteria_breakdown=json.dumps(eval_data.get("criteria_scores", {})),
            feedback=eval_data.get("actionable_feedback", ""),
            revision_count=eval_data.get("revision_count", 0),
        )
        self.db.add(evaluation)

        # 5. Update Automation State counter if published
        if status == "PUBLISHED":
            self._increment_daily_counter()

        self.db.commit()
        self.db.refresh(article)

        # Invalidate cache immediately so readers get updated stories
        cache_service.invalidate("feed:")
        cache_service.invalidate("stats:")
        cache_service.invalidate(f"article:slug:{article.slug}")

        logger.info(f"[+] Article saved ({article_type}): '{article.title}' [Status: {article.status}, Score: {article.score}/10]")
        return article

    def _increment_daily_counter(self) -> None:
        today_str = date.today().isoformat()
        auto_state = self.db.query(AutomationState).first()
        if not auto_state:
            auto_state = AutomationState(
                is_running=False,
                daily_count=1,
                last_reset_date=today_str,
            )
            self.db.add(auto_state)
        else:
            if auto_state.last_reset_date != today_str:
                auto_state.daily_count = 1
                auto_state.last_reset_date = today_str
            else:
                auto_state.daily_count += 1
        self.db.flush()

    def get_public_feed(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        target_date: Optional[str] = None,
        article_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[GameArticle], int]:
        """Returns filtered, published game articles with combinatorial multi-filters."""
        query = self.db.query(GameArticle).filter(GameArticle.status == "PUBLISHED")

        if article_type and article_type != "All":
            query = query.filter(GameArticle.article_type == article_type)
        if category and category != "All":
            query = query.filter(GameArticle.category == category)
        if region and region != "All":
            query = query.filter(GameArticle.origin_region == region)
        if target_date:
            try:
                dt = datetime.strptime(target_date, "%Y-%m-%d").date()
                query = query.filter(func.date(GameArticle.created_at) == dt)
            except ValueError:
                pass
        if search_query:
            term = f"%{search_query}%"
            query = query.filter(
                (GameArticle.title.ilike(term)) |
                (GameArticle.summary.ilike(term)) |
                (GameArticle.origin_country.ilike(term))
            )

        total = query.count()
        articles = query.order_by(desc(GameArticle.created_at)).offset(offset).limit(limit).all()
        return articles, total

    @staticmethod
    def build_feed_cache_key(
        category: Optional[str] = None,
        region: Optional[str] = None,
        target_date: Optional[str] = None,
        article_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> str:
        norm_search = (search_query or "").strip().lower()
        return (
            f"feed:type={article_type or 'All'}:cat={category or 'All'}"
            f":reg={region or 'All'}:dt={target_date or 'none'}:q={norm_search}"
            f":lim={limit}:off={offset}"
        )

    def fetch_and_cache_public_feed(
        self,
        cache_key: str,
        category: Optional[str] = None,
        region: Optional[str] = None,
        target_date: Optional[str] = None,
        article_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[bytes, str]:
        """Queries PostgreSQL on cache miss, serializes, stores in RAM+JSON cache, and returns (json_bytes, etag)."""
        articles, total = self.get_public_feed(
            category=category,
            region=region,
            target_date=target_date,
            article_type=article_type,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )
        payload = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "articles": [serialize_article(a) for a in articles],
        }
        etag = cache_service.set(cache_key, payload)
        json_bytes = cache_service._json_cache.get(cache_key) or json.dumps(payload, default=str).encode("utf-8")
        return json_bytes, etag

    def get_cached_public_feed(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        target_date: Optional[str] = None,
        article_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Sub-millisecond RAM-cached public feed with deterministic ETag.
        Eliminates PostgreSQL queries for 1,000,000+ concurrent readers.
        """
        cache_key = self.build_feed_cache_key(
            category=category,
            region=region,
            target_date=target_date,
            article_type=article_type,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )

        def _fetch_from_db() -> Dict[str, Any]:
            articles, total = self.get_public_feed(
                category=category,
                region=region,
                target_date=target_date,
                article_type=article_type,
                search_query=search_query,
                limit=limit,
                offset=offset,
            )
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "articles": [serialize_article(a) for a in articles],
            }

        return cache_service.get_or_set(cache_key, _fetch_from_db)

    def fetch_and_cache_article_by_slug(self, slug: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Fetches an article by slug from DB, serializes, stores in RAM+JSON cache, and returns (bytes, etag)."""
        article = self.db.query(GameArticle).filter(GameArticle.slug == slug).first()
        if not article:
            return None, None
        payload = serialize_article(article)
        cache_key = f"article:slug:{slug}"
        etag = cache_service.set(cache_key, payload)
        json_bytes = cache_service._json_cache.get(cache_key) or json.dumps(payload, default=str).encode("utf-8")
        return json_bytes, etag

    def fetch_and_cache_article_by_id(self, article_id: int) -> Tuple[Optional[bytes], Optional[str]]:
        """Fetches an article by ID from DB, serializes, stores in RAM+JSON cache, and returns (bytes, etag)."""
        article = self.db.query(GameArticle).filter(GameArticle.id == article_id).first()
        if not article:
            return None, None
        payload = serialize_article(article)
        cache_key = f"article:id:{article_id}"
        etag = cache_service.set(cache_key, payload)
        json_bytes = cache_service._json_cache.get(cache_key) or json.dumps(payload, default=str).encode("utf-8")
        return json_bytes, etag

    def get_cached_article_by_slug(self, slug: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Retrieves an article by unique slug from RAM cache or DB."""
        cache_key = f"article:slug:{slug}"
        cached, etag = cache_service.get(cache_key)
        if cached is not None:
            return cached, etag

        article = self.db.query(GameArticle).filter(GameArticle.slug == slug).first()
        if not article:
            return None, None

        payload = serialize_article(article)
        etag = cache_service.set(cache_key, payload)
        return payload, etag

    def get_cached_article_by_id(self, article_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Retrieves an article by primary key ID from RAM cache or DB."""
        cache_key = f"article:id:{article_id}"
        cached, etag = cache_service.get(cache_key)
        if cached is not None:
            return cached, etag

        article = self.db.query(GameArticle).filter(GameArticle.id == article_id).first()
        if not article:
            return None, None

        payload = serialize_article(article)
        etag = cache_service.set(cache_key, payload)
        return payload, etag

    def get_review_queue(self, limit: int = 50, offset: int = 0) -> Tuple[List[GameArticle], int]:
        """Returns articles waiting in review queue (down-threshold)."""
        query = self.db.query(GameArticle).filter(GameArticle.status == "IN_REVIEW")
        total = query.count()
        articles = query.order_by(desc(GameArticle.created_at)).offset(offset).limit(limit).all()
        return articles, total

    def batch_publish(self, article_ids: List[int]) -> int:
        """Publishes multiple articles selected by admin."""
        articles = self.db.query(GameArticle).filter(
            GameArticle.id.in_(article_ids),
            GameArticle.status != "PUBLISHED"
        ).all()

        count = 0
        for art in articles:
            art.status = "PUBLISHED"
            art.published_at = datetime.utcnow()
            count += 1
            self._increment_daily_counter()

        self.db.commit()
        cache_service.invalidate()
        logger.info(f"[+] Admin batch-published {count} articles.")
        return count

    def get_system_stats(self) -> Dict:
        """Calculates system metrics, article counters, and quality statistics."""
        today_str = date.today().isoformat()
        auto_state = self.db.query(AutomationState).first()

        daily_count = 0
        if auto_state:
            if auto_state.last_reset_date != today_str:
                auto_state.daily_count = 0
                auto_state.last_reset_date = today_str
                self.db.commit()
            daily_count = auto_state.daily_count

        total_published = self.db.query(GameArticle).filter(GameArticle.status == "PUBLISHED").count()
        total_playbooks = self.db.query(GameArticle).filter(GameArticle.status == "PUBLISHED", GameArticle.article_type == "PLAYBOOK").count()
        total_news = self.db.query(GameArticle).filter(GameArticle.status == "PUBLISHED", GameArticle.article_type == "NEWS").count()
        total_in_review = self.db.query(GameArticle).filter(GameArticle.status == "IN_REVIEW").count()
        total_topics = self.db.query(GameTopic).count()

        from app.services.scheduler_service import SchedulerService
        live_running = SchedulerService.is_running()
        if auto_state and auto_state.is_running and not live_running:
            auto_state.is_running = False
            auto_state.next_run_at = None
            self.db.commit()

        avg_score_res = self.db.query(func.avg(GameArticle.score)).scalar() or 0.0

        return {
            "total_articles": total_published,
            "total_playbooks": total_playbooks,
            "total_news": total_news,
            "daily_published": daily_count,
            "daily_limit": auto_state.daily_limit if auto_state else 200,
            "in_review_count": total_in_review,
            "total_topics": total_topics,
            "average_score": round(float(avg_score_res), 2),
            "is_automation_running": live_running,
            "next_run_at": auto_state.next_run_at.isoformat() if (live_running and auto_state and auto_state.next_run_at) else None,
        }

    def get_cached_system_stats(self) -> Tuple[Dict[str, Any], str]:
        """RAM-cached dashboard statistics with short TTL and ETag."""
        return cache_service.get_or_set("stats:system", self.get_system_stats)
