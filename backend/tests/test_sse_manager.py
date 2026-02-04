"""Tests for SSE manager module."""

import pytest
from asyncio import Queue
from app.services.sse_manager import SSEManager


class TestSSEManagerSubscribe:
    """Test cases for subscribe method."""

    def test_subscribe_adds_client_to_evaluation(self):
        """Test that subscribing adds a client queue to the evaluation."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        assert "eval_123" in manager._clients
        assert queue in manager._clients["eval_123"]

    def test_subscribe_multiple_clients_same_evaluation(self):
        """Test multiple clients can subscribe to same evaluation."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_123", queue2)

        assert len(manager._clients["eval_123"]) == 2
        assert queue1 in manager._clients["eval_123"]
        assert queue2 in manager._clients["eval_123"]

    def test_subscribe_different_evaluations(self):
        """Test clients can subscribe to different evaluations."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_456", queue2)

        assert queue1 in manager._clients["eval_123"]
        assert queue2 in manager._clients["eval_456"]
        assert "eval_123" in manager._clients
        assert "eval_456" in manager._clients


class TestSSEManagerUnsubscribe:
    """Test cases for unsubscribe method."""

    def test_unsubscribe_removes_client(self):
        """Test that unsubscribing removes the client from evaluation."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)
        manager.unsubscribe("eval_123", queue)

        assert queue not in manager._clients.get("eval_123", [])

    def test_unsubscribe_nonexistent_client(self):
        """Test unsubscribing a client that doesn't exist doesn't raise error."""
        manager = SSEManager()
        queue = Queue()

        manager.unsubscribe("eval_123", queue)

    def test_unsubscribe_evaluation_with_no_clients(self):
        """Test unsubscribing from evaluation with no clients doesn't raise error."""
        manager = SSEManager()
        queue = Queue()

        manager.unsubscribe("eval_nonexistent", queue)

    def test_unsubscribe_one_of_multiple_clients(self):
        """Test unsubscribing one client leaves others intact."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_123", queue2)
        manager.unsubscribe("eval_123", queue1)

        assert queue2 in manager._clients["eval_123"]
        assert queue1 not in manager._clients["eval_123"]


class TestSSEManagerPublish:
    """Test cases for publish method."""

    @pytest.mark.asyncio
    async def test_publish_sends_event_to_all_subscribers(self):
        """Test that publishing sends event to all subscribed clients."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_123", queue2)

        event = {"type": "status", "data": "running"}
        await manager.publish("eval_123", event)

        assert queue1.empty() is False
        assert queue2.empty() is False

    @pytest.mark.asyncio
    async def test_publish_specific_event_data(self):
        """Test that published event contains correct data."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        event = {"type": "status", "data": "completed", "score": 85}
        await manager.publish("eval_123", event)

        received = await queue.get()
        assert received["type"] == "status"
        assert received["data"] == "completed"
        assert received["score"] == 85

    @pytest.mark.asyncio
    async def test_publish_to_evaluation_with_no_subscribers(self):
        """Test publishing to evaluation with no subscribers doesn't raise error."""
        manager = SSEManager()

        event = {"type": "status", "data": "running"}
        await manager.publish("eval_nonexistent", event)

    @pytest.mark.asyncio
    async def test_publish_multiple_event_types(self):
        """Test publishing different event types."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        events = [
            {"type": "status", "data": "started"},
            {"type": "marcel", "data": "completed"},
            {"type": "isabella", "data": "completed"},
            {"type": "final", "data": {"score": 90, "tier": "Grand Cru"}},
        ]

        for event in events:
            await manager.publish("eval_123", event)

        received_events = []
        for _ in range(4):
            received_events.append(await queue.get())

        assert len(received_events) == 4
        assert received_events[0]["type"] == "status"


class TestSSEManagerGetSubscriberCount:
    """Test cases for get_subscriber_count method."""

    def test_get_subscriber_count_empty(self):
        """Test subscriber count for evaluation with no subscribers."""
        manager = SSEManager()

        count = manager.get_subscriber_count("eval_123")

        assert count == 0

    def test_get_subscriber_count_single(self):
        """Test subscriber count for evaluation with one subscriber."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        count = manager.get_subscriber_count("eval_123")

        assert count == 1

    def test_get_subscriber_count_multiple(self):
        """Test subscriber count for evaluation with multiple subscribers."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()
        queue3 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_123", queue2)
        manager.subscribe("eval_456", queue3)

        count_123 = manager.get_subscriber_count("eval_123")
        count_456 = manager.get_subscriber_count("eval_456")

        assert count_123 == 2
        assert count_456 == 1


class TestSSEManagerIsSubscribed:
    """Test cases for is_subscribed method."""

    def test_is_subscribed_true(self):
        """Test is_subscribed returns True for subscribed client."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        assert manager.is_subscribed("eval_123", queue) is True

    def test_is_subscribed_false(self):
        """Test is_subscribed returns False for unsubscribed client."""
        manager = SSEManager()
        queue = Queue()

        assert manager.is_subscribed("eval_123", queue) is False

    def test_is_subscribed_after_unsubscribe(self):
        """Test is_subscribed returns False after client unsubscribes."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)
        manager.unsubscribe("eval_123", queue)

        assert manager.is_subscribed("eval_123", queue) is False


class TestSSEManagerCloseEvaluation:
    """Test cases for close_evaluation method."""

    @pytest.mark.asyncio
    async def test_close_evaluation_removes_all_subscribers(self):
        """Test that close_evaluation removes all subscribers."""
        manager = SSEManager()
        queue1 = Queue()
        queue2 = Queue()

        manager.subscribe("eval_123", queue1)
        manager.subscribe("eval_123", queue2)

        manager.close_evaluation("eval_123")

        assert queue1 not in manager._clients.get("eval_123", [])
        assert queue2 not in manager._clients.get("eval_123", [])

    @pytest.mark.asyncio
    async def test_close_evaluation_nonexistent(self):
        """Test closing nonexistent evaluation doesn't raise error."""
        manager = SSEManager()

        manager.close_evaluation("eval_nonexistent")

    @pytest.mark.asyncio
    async def test_close_evaluation_sends_close_event(self):
        """Test that close_evaluation sends a close event to all subscribers."""
        manager = SSEManager()
        queue = Queue()

        manager.subscribe("eval_123", queue)

        manager.close_evaluation("eval_123")

        assert queue.empty() is False
        event = await queue.get()
        assert event["type"] == "close"


class TestSSEManagerConcurrency:
    """Concurrency tests for SSE manager."""

    @pytest.mark.asyncio
    async def test_concurrent_subscribes(self):
        """Test concurrent subscription operations."""
        import asyncio

        manager = SSEManager()
        queues = [Queue() for _ in range(10)]

        async def subscribe_all():
            for i, queue in enumerate(queues):
                manager.subscribe(f"eval_{i % 2}", queue)

        await asyncio.gather(*[subscribe_all() for _ in range(2)])

        assert len(manager._clients["eval_0"]) == 10
        assert len(manager._clients["eval_1"]) == 10

    @pytest.mark.asyncio
    async def test_concurrent_publish_and_subscribe(self):
        """Test concurrent publish and subscribe operations."""
        import asyncio

        manager = SSEManager()
        queue = Queue()
        publish_count = [0]

        async def publisher():
            for _ in range(5):
                await manager.publish("eval_123", {"type": "status"})
                publish_count[0] += 1

        async def subscriber():
            for _ in range(5):
                manager.subscribe("eval_123", Queue())

        await asyncio.gather(publisher(), subscriber())

        assert publish_count[0] == 5
