"""
Autonomous Generation Scheduler API Route.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/automation", tags=["Automation"])


class StartAutomationRequest(BaseModel):
    interval_seconds: int = 300


@router.post("/start")
async def start_automation(req: StartAutomationRequest):
    """Starts the continuous background article generator (target up to 200/day)."""
    success = await SchedulerService.start_automation(interval_seconds=req.interval_seconds)
    return {
        "status": "success" if success else "failed",
        "message": f"Autonomous generation daemon active (Interval: {req.interval_seconds}s).",
    }


@router.post("/stop")
async def stop_automation():
    """Stops the continuous background article generator."""
    await SchedulerService.stop_automation()
    return {
        "status": "success",
        "message": "Autonomous generation daemon paused.",
    }


@router.get("/status")
def get_automation_status():
    """Returns live status of the continuous generator."""
    running = SchedulerService.is_running()
    return {
        "is_running": running,
    }
