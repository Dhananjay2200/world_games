"""
Standalone Automation Daemon Runner for WorldGames AI.
Executes continuous game research and publishing (up to 200/day).
"""

import asyncio
from app.services.scheduler_service import SchedulerService
from app.utils.logging import logger


async def main():
    print("=" * 65)
    print(" WorldGames AI - Autonomous Continuous Generation Daemon")
    print("=" * 65)
    print("[*] Initializing daemon (Default interval: 180s)...")
    await SchedulerService.start_automation(interval_seconds=180)
    print("[+] Daemon is now running. Press Ctrl+C to terminate.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping automation daemon...")
        await SchedulerService.stop_automation()
        print("[+] Daemon stopped gracefully.")


if __name__ == "__main__":
    asyncio.run(main())
