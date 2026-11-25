"""
Health Check and Diagnostics Route.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.llm import check_llm_connection
from app.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """System health check endpoint verifying database and LLM connections."""
    settings = get_settings()
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    llm_health = await check_llm_connection()

    return {
        "status": "healthy" if db_status == "ok" and llm_health.get("status") in ("ok", "warning") else "degraded",
        "app_name": settings.APP_NAME,
        "database": db_status,
        "llm_service": llm_health,
        "environment": settings.APP_ENV,
    }
