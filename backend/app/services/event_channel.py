"""Event Channel for real-time SSE streaming with 2-stage sync→async bridge.

This module provides the EventChannel class that bridges synchronous graph node
execution with asynchronous SSE streaming. Key features:
- Thread-safe sync emission (emit_sync) for LangGraph nodes
- Async emission (emit) for other contexts
- Pending event buffer for late subscribers
- Critical event protection (errors, completion never dropped)
- Automatic heartbeat generation

Architecture:
    Graph Node (sync) → emit_sync() → sync_buffer (thread-safe Queue)
                                            ↓
    Transfer Loop (async) → emit() → subscriber async queues
                                            ↓
    SSE Endpoint → subscribe() → yield events
"""

from __future__ import annotations

import asyncio
import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, AsyncIterator, Optional

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

PENDING_EVENTS_MAX_SIZE = 50
PENDING_EVENTS_MAX_AGE_SECONDS = 30.0
CRITICAL_EVENT_TYPES = {"sommelier_error", "evaluation_complete", "evaluation_error"}
TRANSFER_LOOP_INTERVAL_SECONDS = 0.01
TRANSFER_BATCH_SIZE = 10
STALE_CHANNEL_MAX_AGE_SECONDS = 600.0
HEARTBEAT_TIMEOUT_SECONDS = 30.0


class EventType(str, Enum):
    """Event types for sommelier progress streaming."""

    SOMMELIER_START = "sommelier_start"
    SOMMELIER_COMPLETE = "sommelier_complete"
    SOMMELIER_ERROR = "sommelier_error"
    EVALUATION_COMPLETE = "evaluation_complete"
    EVALUATION_ERROR = "evaluation_error"
    HEARTBEAT = "heartbeat"
    STATUS = "status"


@dataclass
class SommelierProgressEvent:
    """Event data structure for sommelier progress updates.

    Attributes:
        evaluation_id: The evaluation this event belongs to.
        event_type: Type of event (start, complete, error, etc.).
        sommelier: Name of the sommelier (marcel, isabella, etc.).
        message: Human-readable message.
        progress_percent: Overall progress percentage (0-100).
        tokens_used: Number of tokens consumed by this sommelier.
        cost_usd: Cost in USD for this sommelier's execution.
        timestamp: When the event occurred.
    """

    evaluation_id: str
    event_type: EventType
    sommelier: Optional[str] = None
    message: str = ""
    progress_percent: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert event to JSON-serializable dictionary."""
        return {
            "evaluation_id": self.evaluation_id,
            "event_type": self.event_type.value,
            "sommelier": self.sommelier,
            "message": self.message,
            "progress_percent": self.progress_percent,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp.isoformat(),
        }


class EventChannel:
    """2-stage event channel: sync → async bridge for SSE streaming.

    This class manages event distribution from synchronous graph node execution
    to asynchronous SSE subscribers. It handles:
    - Thread-safe sync→async bridging via transfer loop
    - Multiple subscribers per evaluation
    - Pending event buffering for late subscribers
    - Critical event protection (never dropped)
    - Automatic stale channel cleanup

    Usage:
        # In graph node (sync context):
        event_channel.emit_sync(eval_id, event)

        # In SSE endpoint (async context):
        async for event in event_channel.subscribe(eval_id):
            yield f"data: {json.dumps(event.to_dict())}\\n\\n"
    """

    def __init__(self) -> None:
        """Initialize the event channel with empty state."""
        self._channels: dict[str, list[asyncio.Queue]] = {}
        self._channel_timestamps: dict[str, float] = {}
        self._pending_events: dict[str, list[tuple[float, SommelierProgressEvent]]] = {}
        self._closed_channels: set[str] = set()
        self._lock = asyncio.Lock()
        self._max_queue_size = 100

        self._sync_buffer: queue.Queue = queue.Queue(maxsize=1000)
        self._transfer_task: Optional[asyncio.Task] = None
        self._transfer_running = False

    async def create_channel(self, evaluation_id: str) -> None:
        """Create an event channel for an evaluation.

        This should be called when starting a new evaluation to ensure
        the channel exists before events are emitted.

        Args:
            evaluation_id: The evaluation ID to create a channel for.
        """
        async with self._lock:
            self._closed_channels.discard(evaluation_id)

            if evaluation_id not in self._channels:
                self._channels[evaluation_id] = []
                self._channel_timestamps[evaluation_id] = time.monotonic()
                logger.info(f"Created event channel for {evaluation_id}")

            if not self._transfer_running:
                self._transfer_running = True
                self._transfer_task = asyncio.create_task(self._transfer_loop())
                logger.info("Started event transfer loop")

    async def _transfer_loop(self) -> None:
        """Background loop transferring events from sync buffer to async queues.

        This loop runs continuously while there are active channels, pulling
        events from the thread-safe sync buffer and distributing them to
        async subscriber queues.
        """
        while self._transfer_running:
            try:
                events_processed = 0
                while events_processed < TRANSFER_BATCH_SIZE:
                    try:
                        evaluation_id, event = self._sync_buffer.get_nowait()
                        await self.emit(evaluation_id, event)
                        events_processed += 1
                    except queue.Empty:
                        break
                await asyncio.sleep(TRANSFER_LOOP_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                logger.info("Transfer loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Transfer loop error: {e}")
                await asyncio.sleep(0.1)

    def emit_sync(self, evaluation_id: str, event: SommelierProgressEvent) -> None:
        """Thread-safe synchronous event emission for graph nodes.

        This method can be safely called from synchronous LangGraph node
        execution. Events are buffered and transferred to async subscribers
        by the transfer loop.

        Args:
            evaluation_id: The evaluation ID to emit to.
            event: The event to emit.
        """
        try:
            is_critical = event.event_type.value in CRITICAL_EVENT_TYPES
            if is_critical:
                self._sync_buffer.put((evaluation_id, event), timeout=5.0)
                logger.debug(
                    f"Emitted critical event {event.event_type.value} "
                    f"for {evaluation_id}"
                )
            else:
                self._sync_buffer.put_nowait((evaluation_id, event))
                logger.debug(
                    f"Emitted event {event.event_type.value} for {evaluation_id}"
                )
        except queue.Full:
            logger.warning(
                f"Dropped non-critical event {event.event_type.value} "
                f"for {evaluation_id} (buffer full)"
            )

    async def emit(self, evaluation_id: str, event: SommelierProgressEvent) -> None:
        """Async event emission to all subscribers.

        If no subscribers exist, the event is buffered for late subscribers.

        Args:
            evaluation_id: The evaluation ID to emit to.
            event: The event to emit.
        """
        async with self._lock:
            if evaluation_id in self._closed_channels:
                logger.debug(f"Ignoring event for closed channel {evaluation_id}")
                return

            if evaluation_id not in self._channels:
                self._channels[evaluation_id] = []
                self._channel_timestamps[evaluation_id] = time.monotonic()

            queues = self._channels.get(evaluation_id, [])

            if len(queues) == 0:
                self._buffer_pending_event(evaluation_id, event)
                logger.debug(
                    f"Buffered pending event {event.event_type.value} "
                    f"for {evaluation_id}"
                )
                return

            for q in queues:
                try:
                    await asyncio.wait_for(q.put(event), timeout=1.0)
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Timeout putting event to subscriber queue for {evaluation_id}"
                    )
                except Exception as e:
                    logger.warning(f"Error putting event to queue: {e}")

    def _buffer_pending_event(
        self, evaluation_id: str, event: SommelierProgressEvent
    ) -> None:
        """Buffer an event for late subscribers.

        Maintains size and age limits on the pending event buffer.

        Args:
            evaluation_id: The evaluation ID.
            event: The event to buffer.
        """
        current_time = time.monotonic()

        if evaluation_id not in self._pending_events:
            self._pending_events[evaluation_id] = []

        pending = self._pending_events[evaluation_id]

        pending = [
            (ts, ev)
            for ts, ev in pending
            if current_time - ts < PENDING_EVENTS_MAX_AGE_SECONDS
        ]

        if len(pending) >= PENDING_EVENTS_MAX_SIZE:
            critical = [
                (ts, ev)
                for ts, ev in pending
                if ev.event_type.value in CRITICAL_EVENT_TYPES
            ]
            non_critical = [
                (ts, ev)
                for ts, ev in pending
                if ev.event_type.value not in CRITICAL_EVENT_TYPES
            ]

            while (
                len(critical) + len(non_critical) >= PENDING_EVENTS_MAX_SIZE
                and non_critical
            ):
                non_critical.pop(0)

            pending = non_critical + critical

        pending.append((current_time, event))
        self._pending_events[evaluation_id] = pending

    async def subscribe(
        self, evaluation_id: str
    ) -> AsyncIterator[SommelierProgressEvent]:
        """Subscribe to events for an evaluation.

        This is an async generator that yields events as they arrive.
        It first delivers any pending events, then waits for new events.
        Heartbeat events are generated on timeout to keep the connection alive.

        Args:
            evaluation_id: The evaluation ID to subscribe to.

        Yields:
            SommelierProgressEvent objects as they arrive.
        """
        subscriber_queue: asyncio.Queue = asyncio.Queue(maxsize=self._max_queue_size)

        async with self._lock:
            if evaluation_id not in self._channels:
                self._channels[evaluation_id] = []
                self._channel_timestamps[evaluation_id] = time.monotonic()

            # Deliver pending events INSIDE lock to prevent race with _transfer_loop
            delivered = await self._deliver_pending_events(
                evaluation_id, subscriber_queue
            )
            if delivered > 0:
                logger.info(f"Delivered {delivered} pending events to new subscriber")

            # Register subscriber AFTER pending events delivered to ensure ordering
            self._channels[evaluation_id].append(subscriber_queue)
            logger.info(
                f"New subscriber for {evaluation_id}, "
                f"total: {len(self._channels[evaluation_id])}"
            )

        try:
            while True:
                try:
                    event = await asyncio.wait_for(
                        subscriber_queue.get(), timeout=HEARTBEAT_TIMEOUT_SECONDS
                    )

                    if event is None:
                        logger.info(f"Channel closed for {evaluation_id}")
                        break

                    yield event

                    if event.event_type == EventType.EVALUATION_COMPLETE:
                        logger.info(f"Evaluation complete for {evaluation_id}")
                        break

                except asyncio.TimeoutError:
                    yield SommelierProgressEvent(
                        evaluation_id=evaluation_id,
                        event_type=EventType.HEARTBEAT,
                        message="heartbeat",
                        progress_percent=-1,
                    )

        except asyncio.CancelledError:
            logger.info(f"Subscriber cancelled for {evaluation_id}")
        finally:
            async with self._lock:
                if evaluation_id in self._channels:
                    try:
                        self._channels[evaluation_id].remove(subscriber_queue)
                        logger.info(
                            f"Removed subscriber for {evaluation_id}, "
                            f"remaining: {len(self._channels[evaluation_id])}"
                        )
                    except ValueError:
                        pass

    async def _deliver_pending_events(
        self, evaluation_id: str, queue: asyncio.Queue
    ) -> int:
        """Deliver buffered pending events to a new subscriber.

        Args:
            evaluation_id: The evaluation ID.
            queue: The subscriber's queue.

        Returns:
            Number of events delivered.
        """
        if evaluation_id not in self._pending_events:
            return 0

        pending = self._pending_events.pop(evaluation_id, [])
        delivered = 0

        for _ts, event in pending:
            try:
                await asyncio.wait_for(queue.put(event), timeout=1.0)
                delivered += 1
            except asyncio.TimeoutError:
                logger.warning("Timeout delivering pending event")
                break

        return delivered

    async def close_channel(self, evaluation_id: str) -> None:
        """Close an evaluation channel and notify all subscribers.

        Args:
            evaluation_id: The evaluation ID to close.
        """
        async with self._lock:
            self._closed_channels.add(evaluation_id)

            if evaluation_id in self._channels:
                for q in self._channels[evaluation_id]:
                    try:
                        q.put_nowait(None)
                    except asyncio.QueueFull:
                        pass

                del self._channels[evaluation_id]
                self._channel_timestamps.pop(evaluation_id, None)
                self._pending_events.pop(evaluation_id, None)
                logger.info(f"Closed event channel for {evaluation_id}")

            if not self._channels and self._transfer_running:
                self._transfer_running = False
                if self._transfer_task:
                    self._transfer_task.cancel()
                    try:
                        await self._transfer_task
                    except asyncio.CancelledError:
                        pass
                    self._transfer_task = None
                logger.info("Stopped event transfer loop (no channels)")

    async def cleanup_stale_channels(self) -> int:
        """Remove channels that have been inactive for too long.

        Returns:
            Number of channels cleaned up.
        """
        current_time = time.monotonic()
        stale_ids = []

        async with self._lock:
            for eval_id, created_at in self._channel_timestamps.items():
                if current_time - created_at > STALE_CHANNEL_MAX_AGE_SECONDS:
                    stale_ids.append(eval_id)

        for eval_id in stale_ids:
            await self.close_channel(eval_id)
            logger.info(f"Cleaned up stale channel for {eval_id}")

        return len(stale_ids)

    def get_subscriber_count(self, evaluation_id: str) -> int:
        """Get the number of active subscribers for an evaluation.

        Args:
            evaluation_id: The evaluation ID.

        Returns:
            Number of active subscribers.
        """
        return len(self._channels.get(evaluation_id, []))

    def get_channel_count(self) -> int:
        """Get the total number of active channels.

        Returns:
            Number of active channels.
        """
        return len(self._channels)


_event_channel: Optional[EventChannel] = None
_event_channel_lock = threading.Lock()


def get_event_channel() -> EventChannel:
    """Get or create the global EventChannel instance.

    Returns:
        The EventChannel singleton.
    """
    global _event_channel
    if _event_channel is None:
        with _event_channel_lock:
            if _event_channel is None:
                _event_channel = EventChannel()
    return _event_channel


def create_sommelier_event(
    evaluation_id: str,
    sommelier: str,
    event_type: str,
    progress_percent: int,
    message: str = "",
    tokens_used: int = 0,
    cost_usd: float = 0.0,
) -> SommelierProgressEvent:
    """Factory function to create a SommelierProgressEvent.

    Args:
        evaluation_id: The evaluation ID.
        sommelier: Name of the sommelier.
        event_type: Event type string (sommelier_start, sommelier_complete, etc.).
        progress_percent: Progress percentage (0-100).
        message: Optional human-readable message.
        tokens_used: Optional token count.
        cost_usd: Optional cost in USD.

    Returns:
        A new SommelierProgressEvent instance.
    """
    return SommelierProgressEvent(
        evaluation_id=evaluation_id,
        event_type=EventType(event_type),
        sommelier=sommelier,
        message=message or f"{sommelier} {event_type}",
        progress_percent=progress_percent,
        tokens_used=tokens_used,
        cost_usd=cost_usd,
    )
