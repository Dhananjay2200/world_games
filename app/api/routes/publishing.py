"""
Publishing, Review Queue, Cache Telemetry, and Stats API Routes.
Zero-DB-session async fast-path on RAM cache hits for 1M+ concurrent readers.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db, SessionLocal
from app.database.models import GameArticle
from app.services.publisher_service import PublisherService
from app.services.cache_service import cache_service

router = APIRouter(prefix="/publish", tags=["Publishing"])


class BatchPublishRequest(BaseModel):
    article_ids: List[int]


def _cache_headers(etag: str) -> dict:
    return {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "ETag": etag,
        "X-Cache-Engine": "WorldGames-HighConcurrency-MemoryCache",
    }


@router.get("/feed")
async def get_public_feed(
    request: Request,
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    article_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Public visitor feed with combinatorial filters, zero-serialization RAM caching,
    and HTTP 304 ETag short-circuiting.
    """
    cache_key = PublisherService.build_feed_cache_key(
        category=category,
        region=region,
        target_date=date,
        article_type=article_type,
        search_query=search,
        limit=limit,
        offset=offset,
    )

    json_bytes, etag = cache_service.get_json(cache_key)
    if json_bytes is None:
        def _load_feed():
            db = SessionLocal()
            try:
                return PublisherService(db).fetch_and_cache_public_feed(
                    cache_key=cache_key,
                    category=category,
                    region=region,
                    target_date=date,
                    article_type=article_type,
                    search_query=search,
                    limit=limit,
                    offset=offset,
                )
            finally:
                db.close()

        json_bytes, etag = await run_in_threadpool(_load_feed)

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(
            status_code=304,
            headers={
                "ETag": etag,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "X-Cache-Engine": "WorldGames-HighConcurrency-MemoryCache",
            },
        )

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers=_cache_headers(etag),
    )


@router.get("/review-queue")
def get_review_queue(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Admin review queue for articles scoring below the 8.0 quality threshold."""
    service = PublisherService(db)
    articles, total = service.get_review_queue(limit=limit, offset=offset)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "articles": articles,
    }


@router.post("/batch")
def batch_publish(req: BatchPublishRequest, db: Session = Depends(get_db)):
    """Batch publishes selected articles by ID."""
    if not req.article_ids:
        raise HTTPException(status_code=400, detail="No article IDs provided.")
    service = PublisherService(db)
    published_count = service.batch_publish(req.article_ids)
    return {
        "status": "success",
        "published_count": published_count,
        "message": f"Successfully published {published_count} game articles.",
    }


@router.get("/stats")
async def get_system_stats(request: Request):
    """Returns dashboard statistics with zero-DB RAM caching and ETag 304 support."""
    cache_key = "stats:system"
    json_bytes, etag = cache_service.get_json(cache_key)
    if json_bytes is None:
        def _load_stats():
            db = SessionLocal()
            try:
                stats = PublisherService(db).get_system_stats()
                etag_val = cache_service.set(cache_key, stats)
                raw = cache_service._json_cache.get(cache_key) or json.dumps(stats, default=str).encode("utf-8")
                return raw, etag_val
            finally:
                db.close()

        json_bytes, etag = await run_in_threadpool(_load_stats)

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(
            status_code=304,
            headers={
                "ETag": etag,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "X-Cache-Engine": "WorldGames-HighConcurrency-MemoryCache",
            },
        )

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers=_cache_headers(etag),
    )


@router.get("/cache/stats")
def get_cache_telemetry():
    """Returns live in-memory cache metrics: hit ratio, requests count, and entries."""
    return cache_service.get_stats()


@router.post("/cache/flush")
def flush_cache():
    """Manually invalidates the high-concurrency memory cache."""
    cache_service.invalidate()
    return {"message": "Memory cache successfully flushed.", "stats": cache_service.get_stats()}


@router.post("/{article_id}")
def publish_single_article(article_id: int, db: Session = Depends(get_db)):
    """Publishes a single article from review queue."""
    service = PublisherService(db)
    count = service.batch_publish([article_id])
    if count == 0:
        raise HTTPException(status_code=404, detail="Article not found or already published.")
    return {"status": "success", "message": f"Article {article_id} published successfully."}


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Deletes or rejects an article and flushes cached entries."""
    article = db.query(GameArticle).filter(GameArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    db.delete(article)
    db.commit()
    cache_service.invalidate()
    return {"status": "success", "message": f"Article {article_id} deleted successfully."}
