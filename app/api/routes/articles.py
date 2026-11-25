"""
Articles API Route.
Provides endpoints for fetching game guides by slug, id, and with multi-filters,
backed by zero-serialization RAM caching and ETag 304 short-circuiting.
"""

import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.concurrency import run_in_threadpool
from app.database.session import SessionLocal
from app.services.publisher_service import PublisherService
from app.services.cache_service import cache_service

router = APIRouter(prefix="/articles", tags=["Articles"])


def _cache_headers(etag: str) -> dict:
    return {
        "Cache-Control": "no-cache, must-revalidate",
        "ETag": etag,
        "X-Cache-Engine": "WorldGames-HighConcurrency-MemoryCache",
    }


@router.get("")
async def get_articles(
    request: Request,
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    article_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
):
    """Combines 3-way filters: Category, Region, and Date with pagination and zero-DB RAM caching."""
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
        def _load_articles():
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

        json_bytes, etag = await run_in_threadpool(_load_articles)

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(status_code=304, headers=_cache_headers(etag))

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers=_cache_headers(etag),
    )


@router.get("/slug/{slug}")
async def get_article_by_slug(slug: str, request: Request):
    """Fetches full encyclopedic game article by unique slug from RAM cache."""
    cache_key = f"article:slug:{slug}"
    json_bytes, etag = cache_service.get_json(cache_key)
    if json_bytes is None:
        def _load_slug():
            db = SessionLocal()
            try:
                return PublisherService(db).fetch_and_cache_article_by_slug(slug)
            finally:
                db.close()

        json_bytes, etag = await run_in_threadpool(_load_slug)
        if not json_bytes:
            raise HTTPException(status_code=404, detail="Game guide not found.")

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(status_code=304, headers=_cache_headers(etag))

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers=_cache_headers(etag),
    )


@router.get("/id/{article_id}")
async def get_article_by_id(article_id: int, request: Request):
    """Fetches article by primary key ID from RAM cache."""
    cache_key = f"article:id:{article_id}"
    json_bytes, etag = cache_service.get_json(cache_key)
    if json_bytes is None:
        def _load_id():
            db = SessionLocal()
            try:
                return PublisherService(db).fetch_and_cache_article_by_id(article_id)
            finally:
                db.close()

        json_bytes, etag = await run_in_threadpool(_load_id)
        if not json_bytes:
            raise HTTPException(status_code=404, detail="Game guide not found.")

    if_none_match = request.headers.get("if-none-match")
    if if_none_match and if_none_match.strip() == etag:
        return Response(status_code=304, headers=_cache_headers(etag))

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers=_cache_headers(etag),
    )
