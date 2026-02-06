"""Background task registry for managing evaluation tasks.

Provides registration, cancellation, and status tracking for background
evaluation tasks. Each evaluation runs as an asyncio task that can be
monitored and cancelled if needed.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_running_tasks: Dict[str, asyncio.Task] = {}
_tasks_lock = asyncio.Lock()


def _cleanup_task_sync(evaluation_id: str) -> None:
    """Callback to clean up task entry after completion."""
    _running_tasks.pop(evaluation_id, None)
    logger.info(f"Task cleanup for {evaluation_id}")


async def register_task(evaluation_id: str, task: asyncio.Task) -> None:
    """Register an evaluation task for tracking.

    Args:
        evaluation_id: The evaluation ID.
        task: The asyncio Task running the evaluation.
    """
    async with _tasks_lock:
        if evaluation_id in _running_tasks:
            old_task = _running_tasks[evaluation_id]
            if not old_task.done():
                logger.warning(f"Cancelling existing task for {evaluation_id}")
                old_task.cancel()

        _running_tasks[evaluation_id] = task
        task.add_done_callback(lambda t: _cleanup_task_sync(evaluation_id))
        logger.info(f"Registered task for {evaluation_id}")


async def cancel_task(evaluation_id: str) -> bool:
    """Cancel a running evaluation task.

    Args:
        evaluation_id: The evaluation ID to cancel.

    Returns:
        True if task was cancelled, False if no task found or already done.
    """
    async with _tasks_lock:
        task = _running_tasks.get(evaluation_id)
        if task and not task.done():
            task.cancel()
            logger.info(f"Cancelled task for {evaluation_id}")
            return True
        return False


async def get_task_status(evaluation_id: str) -> Optional[str]:
    """Get the status of an evaluation task.

    Args:
        evaluation_id: The evaluation ID.

    Returns:
        'running', 'completed', 'cancelled', or None if not found.
    """
    async with _tasks_lock:
        task = _running_tasks.get(evaluation_id)
        if task is None:
            return None
        if task.done():
            return "cancelled" if task.cancelled() else "completed"
        return "running"


def get_running_task_count() -> int:
    """Get the number of currently running tasks."""
    return sum(1 for t in _running_tasks.values() if not t.done())
