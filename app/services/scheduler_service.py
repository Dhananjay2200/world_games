"""
WorldGames AI - Autonomous Scheduler Service.
Drives continuous automated generation of world games guides (up to 200/day),
tracking daily quotas, 24-hour reset windows, and interval triggers.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Optional
from app.database.session import SessionLocal
from app.database.models import AutomationState
from app.services.cache_service import cache_service
from app.utils.logging import logger

_scheduler_task: Optional[asyncio.Task] = None
_stop_event = asyncio.Event()
_dispatched_news_angles: set[str] = set()


class SchedulerService:
    @staticmethod
    def is_running() -> bool:
        global _scheduler_task
        return _scheduler_task is not None and not _scheduler_task.done()

    @staticmethod
    def reconcile_stale_state() -> None:
        """
        Ensures DB AutomationState matches the actual in-memory scheduler task
        on startup or after a server restart.
        """
        if SchedulerService.is_running():
            return
        db = SessionLocal()
        try:
            state = db.query(AutomationState).first()
            if state and (state.is_running or state.next_run_at is not None):
                state.is_running = False
                state.next_run_at = None
                db.commit()
                cache_service.invalidate("stats:")
                logger.info("[*] Reconciled stale AutomationState -> STOPPED after restart.")
        finally:
            db.close()

    @staticmethod
    async def start_automation(interval_seconds: int = 300) -> bool:
        """Starts background automation worker loop."""
        global _scheduler_task, _stop_event

        if SchedulerService.is_running():
            logger.info("Scheduler already running.")
            return True

        _stop_event.clear()

        db = SessionLocal()
        try:
            state = db.query(AutomationState).first()
            if not state:
                state = AutomationState(
                    is_running=True,
                    interval_seconds=interval_seconds,
                    next_run_at=datetime.utcnow() + timedelta(seconds=interval_seconds),
                )
                db.add(state)
            else:
                state.is_running = True
                state.interval_seconds = interval_seconds
                state.next_run_at = datetime.utcnow() + timedelta(seconds=interval_seconds)
            db.commit()
        finally:
            db.close()

        _scheduler_task = asyncio.create_task(SchedulerService._worker_loop(interval_seconds))
        cache_service.invalidate("stats:")
        logger.info(f"[+] Autonomous generation loop started (Interval: {interval_seconds}s)")
        return True

    @staticmethod
    async def stop_automation() -> bool:
        """Stops background automation worker loop and clears next_run_at."""
        global _scheduler_task, _stop_event

        _stop_event.set()
        if _scheduler_task:
            _scheduler_task.cancel()
            try:
                await _scheduler_task
            except asyncio.CancelledError:
                pass
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

        cache_service.invalidate("stats:")
        logger.info("[-] Autonomous generation loop stopped.")
        return True

    @staticmethod
    async def _pick_auto_news_candidate(db, prefer_source: str = "espn") -> Optional[dict]:
        """Selects a fresh, unpublished breaking sports headline from ESPN and/or APITube."""
        from app.config import get_settings
        from app.database.models import GameArticle
        from app.services.apitube_service import APITubeNewsService
        from app.services.espn_news_service import ESPNNewsService

        recent_news = (
            db.query(GameArticle.title)
            .filter(GameArticle.article_type == "NEWS")
            .order_by(GameArticle.created_at.desc())
            .limit(100)
            .all()
        )
        existing_titles = {row[0] for row in recent_news if row[0]} | _dispatched_news_angles

        candidate = None
        if prefer_source == "espn":
            candidate = await ESPNNewsService().pick_fresh_sports_story(existing_titles=existing_titles)
            if not candidate and (get_settings().API_TUBE_KEY or "").strip():
                candidate = await APITubeNewsService().pick_fresh_sports_story(existing_titles=existing_titles)
        else:
            if (get_settings().API_TUBE_KEY or "").strip():
                candidate = await APITubeNewsService().pick_fresh_sports_story(existing_titles=existing_titles)
            if not candidate:
                candidate = await ESPNNewsService().pick_fresh_sports_story(existing_titles=existing_titles)

        if candidate and candidate.get("news_angle"):
            _dispatched_news_angles.add(candidate["news_angle"].lower().strip())
        return candidate

    @staticmethod
    async def _worker_loop(interval_seconds: int):
        from app.graph.workflow import run_single_game_workflow

        cycle_idx = 0
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
                    if state and not _stop_event.is_set():
                        state.next_run_at = datetime.utcnow() + timedelta(seconds=600)
                        db.commit()
                        cache_service.invalidate("stats:")
                    await asyncio.wait_for(_stop_event.wait(), timeout=600)
                    continue

                # Determine next cycle type from the last article in PostgreSQL so alternation stays exact across restarts:
                # If last article was PLAYBOOK -> run NEWS next; if last was NEWS -> run PLAYBOOK next.
                from app.database.models import GameArticle
                last_art = db.query(GameArticle.article_type).order_by(GameArticle.id.desc()).first()
                run_news_next = (last_art is not None and last_art[0] == "PLAYBOOK")

                if run_news_next:
                    news_source = "espn" if (cycle_idx % 2 == 0) else "apitube"
                    candidate = await SchedulerService._pick_auto_news_candidate(db, prefer_source=news_source)
                    if candidate:
                        logger.info(
                            f"[Scheduler] Last article was PLAYBOOK -> running LIVE NEWS ({news_source.upper()}) cycle [{daily_count + 1}/{daily_limit}]: "
                            f"'{candidate['news_angle'][:60]}...'"
                        )
                        await run_single_game_workflow(
                            topic_name=candidate["topic_name"],
                            category=candidate["category"],
                            region=candidate["region"],
                            country=candidate["country"],
                            article_type="NEWS",
                            news_angle=candidate["news_angle"],
                        )
                    else:
                        logger.info(f"[Scheduler] No fresh wire news available -> triggering PLAYBOOK cycle [{daily_count + 1}/{daily_limit}]...")
                        await run_single_game_workflow()
                else:
                    logger.info(f"[Scheduler] Last article was NEWS (or initial) -> running PLAYBOOK cycle [{daily_count + 1}/{daily_limit}]...")
                    pb_result = await run_single_game_workflow()
                    pb_status = pb_result.get("status") if pb_result else None
                    pb_topic = (pb_result.get("topic") or {}).get("name", "Unknown") if pb_result else "Unknown"

                    if pb_status == "PLAYBOOK_EXISTS_SWITCHED_TO_NEWS":
                        logger.info(
                            f"[Scheduler] Playbook for '{pb_topic}' already exists -> moved to latest NEWS: "
                            f"'{(pb_result.get('article') or {}).get('title', pb_result.get('news_angle', ''))[:70]}'"
                        )
                    elif pb_status == "DUPLICATE_REJECTED":
                        fallback_source = "espn" if (cycle_idx % 2 == 0) else "apitube"
                        candidate = await SchedulerService._pick_auto_news_candidate(db, prefer_source=fallback_source)
                        if candidate:
                            logger.info(
                                f"[Scheduler] Playbook for '{pb_topic}' already exists (no sport-specific news) -> "
                                f"moving to general latest NEWS: '{candidate['news_angle'][:60]}...'"
                            )
                            await run_single_game_workflow(
                                topic_name=candidate["topic_name"],
                                category=candidate["category"],
                                region=candidate["region"],
                                country=candidate["country"],
                                article_type="NEWS",
                                news_angle=candidate["news_angle"],
                            )

                cycle_idx += 1

                # Re-query fresh state and update next run time only if still active
                if not _stop_event.is_set():
                    state = db.query(AutomationState).first()
                    if state and state.is_running:
                        state.last_run_at = datetime.utcnow()
                        state.next_run_at = datetime.utcnow() + timedelta(seconds=interval_seconds)
                        db.commit()
                        cache_service.invalidate("stats:")

            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.error(f"Error in scheduler execution cycle: {e}")
            finally:
                db.close()

            if _stop_event.is_set():
                break

            try:
                await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
            except asyncio.TimeoutError:
                pass
