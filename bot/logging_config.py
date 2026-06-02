"""
Logging configuration for the trading bot.
Sets up both file-based and console-based (rich) logging.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler
from rich.console import Console

console = Console()

LOG_FILE = Path(__file__).parent.parent / "trading_bot.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure root logger with:
    - A rotating file handler (writes structured logs to trading_bot.log)
    - A rich console handler (colorful output in terminal)

    Returns the root logger.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers if setup_logging is called more than once
    if root_logger.handlers:
        return root_logger

    # ── File Handler (rotating, max 5 MB, keep 3 backups) ──────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # ── Rich Console Handler ────────────────────────────────────────────────
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        markup=True,
    )
    rich_handler.setLevel(level)
    rich_handler.setFormatter(logging.Formatter("%(message)s", datefmt=DATE_FORMAT))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(rich_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger (call setup_logging first)."""
    return logging.getLogger(name)
