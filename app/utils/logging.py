"""
Logging utility for WorldGames AI using Rich formatting.
"""

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=False)]
)

logger = logging.getLogger("world_games")
logger.setLevel(logging.INFO)
