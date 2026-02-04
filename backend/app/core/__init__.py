"""Core package

This package contains core functionality:
- config: Application settings and configuration
- logging: Logging setup and configuration
- exceptions: Wine-themed custom HTTP exceptions
"""

from app.core import config
from app.core.logging import setup_logging, logger
from app.core.exceptions import (
    CorkedError,
    NoInvitationError,
    EmptyCellarError,
    OverconsumptionError,
    SpoiledBatchError,
)

__all__ = [
    "config",
    "setup_logging",
    "logger",
    "CorkedError",
    "NoInvitationError",
    "EmptyCellarError",
    "OverconsumptionError",
    "SpoiledBatchError",
]
