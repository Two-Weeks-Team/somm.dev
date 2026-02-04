"""SSE (Server-Sent Events) manager for real-time evaluation updates.

This module provides the SSEManager class for managing client connections
and broadcasting evaluation progress events.
"""

from asyncio import Queue
from typing import Dict, Set


class SSEManager:
    """Manages SSE client connections for evaluation streaming.

    This class handles:
    - Subscribing clients to evaluation updates
    - Publishing events to all subscribed clients
    - Unsubscribing clients when they disconnect
    - Closing evaluation streams
    """

    def __init__(self) -> None:
        """Initialize the SSE manager with empty client tracking."""
        self._clients: Dict[str, Set[Queue]] = {}

    def subscribe(self, evaluation_id: str, queue: Queue) -> None:
        """Subscribe a client to receive evaluation updates.

        Args:
            evaluation_id: The evaluation ID to subscribe to.
            queue: The asyncio Queue to send events to.
        """
        if evaluation_id not in self._clients:
            self._clients[evaluation_id] = set()

        self._clients[evaluation_id].add(queue)

    def unsubscribe(self, evaluation_id: str, queue: Queue) -> None:
        """Unsubscribe a client from evaluation updates.

        Args:
            evaluation_id: The evaluation ID to unsubscribe from.
            queue: The queue to remove.
        """
        if evaluation_id in self._clients:
            self._clients[evaluation_id].discard(queue)

            if not self._clients[evaluation_id]:
                del self._clients[evaluation_id]

    async def publish(self, evaluation_id: str, event: dict) -> None:
        """Publish an event to all subscribed clients.

        Args:
            evaluation_id: The evaluation ID to publish to.
            event: The event data to send.
        """
        if evaluation_id in self._clients:
            for queue in list(self._clients[evaluation_id]):
                await queue.put(event)

    def get_subscriber_count(self, evaluation_id: str) -> int:
        """Get the number of subscribers for an evaluation.

        Args:
            evaluation_id: The evaluation ID.

        Returns:
            The number of active subscribers.
        """
        return len(self._clients.get(evaluation_id, set()))

    def is_subscribed(self, evaluation_id: str, queue: Queue) -> bool:
        """Check if a queue is subscribed to an evaluation.

        Args:
            evaluation_id: The evaluation ID.
            queue: The queue to check.

        Returns:
            True if the queue is subscribed, False otherwise.
        """
        return queue in self._clients.get(evaluation_id, set())

    async def close_evaluation(self, evaluation_id: str) -> None:
        """Close an evaluation stream and notify all subscribers.

        Args:
            evaluation_id: The evaluation ID to close.
        """
        if evaluation_id in self._clients:
            close_event = {"type": "close", "data": "evaluation_complete"}

            for queue in list(self._clients[evaluation_id]):
                await queue.put(close_event)
                self._clients[evaluation_id].discard(queue)

            del self._clients[evaluation_id]


_sse_manager: SSEManager | None = None


def get_sse_manager() -> SSEManager:
    """Get or create the global SSE manager instance.

    Returns:
        The SSE manager singleton instance.
    """
    global _sse_manager
    if _sse_manager is None:
        _sse_manager = SSEManager()
    return _sse_manager
