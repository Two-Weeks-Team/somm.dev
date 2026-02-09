"""Logging configuration for somm.dev backend.

This module provides centralized logging setup for the application.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure application logging with wine-themed formatting.

    Sets up logging with appropriate handlers, formatters, and log levels.
    The logger uses a custom formatter that includes timestamps and log levels.

    Returns:
        Configured logger instance.
    """
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_filename = log_dir / f"somm_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"

    logger = logging.getLogger("somm")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
