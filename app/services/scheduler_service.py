"""
WorldGames AI - Autonomous Scheduler Service.
Drives continuous automated generation of world games guides (up to 200/day),
tracking daily quotas, 24-hour reset windows, and interval triggers.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models import AutomationState
from app.utils.logging import logger

_scheduler_task: Optional[asyncio.Task] = None
_stop_event = asyncio.Event()


class SchedulerService:
    @staticmethod
    def is_running() -> bool:
        global _scheduler_task
        return _scheduler_task is not None and not _scheduler_task.done()

    @staticmethod
    async def start_automation(interval_seconds: int = 300) -> bool:
        """Starts background automation worker loop."""
        global _scheduler_task, _stop_event

        if SchedulerService.is_running():
            logger.info("Scheduler already running.")
            return True

        _stop_event.clear()
        
        # Update DB state
        db = SessionLocal()
        try:
            state = db.query(AutomationState).first()
            if not state:
                state = AutomationState(is_running=True, interval_seconds=interval_seconds)
                db.add(state)
            else:
                state.is_running = True
                state.interval_seconds = interval_seconds
                state.next_run_at = datetime.utcnow() + timedelta(seconds=interval_seconds)
            db.commit()
        finally:
            db.close()

        _scheduler_task = asyncio.create_task(SchedulerService._worker_loop(interval_seconds))
        logger.info(f"[+] Autonomous generation loop started (Interval: {interval_seconds}s)")
        return True

    @staticmethod
    async def stop_automation() -> bool:
        """Stops background automation worker loop."""
        global _scheduler_task, _stop_event

        _stop_event.set()
        if _scheduler_task:
            _scheduler_task.cancel()
            _scheduler_task = None

        db = SessionLocal()
        try:
            state = db.query(AutomationState).first()
            if state:
                state.is_running = False
                state.next_run_at = None
                db.commit()
        finally:
            db.close()

        logger.info("[-] Autonomous generation loop stopped.")
        return True

    @staticmethod
    async def _worker_loop(interval_seconds: int):
        from app.graph.workflow import run_single_game_workflow

        while not _stop_event.is_set():
            db = SessionLocal()
            try:
                state = db.query(AutomationState).first()
                today_str = date.today().isoformat()
                
                # Check 24-hr daily reset
                if state and state.last_reset_date != today_str:
                    state.daily_count = 0
                    state.last_reset_date = today_str
                    db.commit()

                daily_count = state.daily_count if state else 0
                daily_limit = state.daily_limit if state else 200

                if daily_count >= daily_limit:
                    logger.info(f"Daily quota reached ({daily_count}/{daily_limit}). Sleeping until next window.")
                    await asyncio.sleep(600)
                    continue

                logger.info(f"[*] Automation triggering workflow cycle [{daily_count + 1}/{daily_limit}]...")
                # Run complete workflow
                await run_single_game_workflow()

                # Update next run time
                if state:
                    state.last_run_at = datetime.utcnow()
                    state.next_run_at = datetime.utcnow() + timedelta(seconds=interval_seconds)
                    db.commit()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler execution cycle: {e}")
            finally:
                db.close()

            try:
                await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
            except asyncio.TimeoutError:
                pass
