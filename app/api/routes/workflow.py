"""
Workflow Execution API Route.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph.workflow import run_single_game_workflow
from app.utils.logging import logger

router = APIRouter(prefix="/workflow", tags=["Workflow"])


class RunWorkflowRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    article_type: Optional[str] = "PLAYBOOK"  # "PLAYBOOK" or "NEWS"
    news_angle: Optional[str] = None


@router.post("/run")
async def trigger_workflow(req: RunWorkflowRequest):
    """Executes a complete LangGraph cycle for a Playbook or Sports News story."""
    try:
        result = await run_single_game_workflow(
            topic_name=req.name,
            category=req.category,
            region=req.region,
            country=req.country,
            article_type=req.article_type or "PLAYBOOK",
            news_angle=req.news_angle,
        )
        return {
            "status": "success",
            "workflow_result": {
                "topic": result.get("topic"),
                "status": result.get("status"),
                "article_title": result.get("article", {}).get("title"),
                "article_type": result.get("article_type", "PLAYBOOK"),
                "score": result.get("evaluation", {}).get("overall_score"),
                "passed": result.get("evaluation", {}).get("passed"),
                "published_article_id": result.get("published_article_id"),
            }
        }
    except Exception as e:
        logger.error(f"Workflow execution failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
