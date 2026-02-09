import threading
import time

import pytest

from app.services.event_channel import (
    CRITICAL_EVENT_TYPES,
    EventType,
    SSEEvent,
    create_technique_event,
)
from app.services.progress import ProgressTracker


class TestEventTypeEnum:
    def test_event_type_has_all_technique_event_types(self):
        technique_events = [
            EventType.TECHNIQUE_START,
            EventType.TECHNIQUE_COMPLETE,
            EventType.TECHNIQUE_ERROR,
            EventType.CATEGORY_START,
            EventType.CATEGORY_COMPLETE,
            EventType.DEEP_SYNTHESIS_START,
            EventType.DEEP_SYNTHESIS_COMPLETE,
            EventType.QUALITY_GATE_COMPLETE,
            EventType.METRICS_UPDATE,
        ]
        for event in technique_events:
            assert isinstance(event, EventType)

    def test_technique_event_type_values(self):
        assert EventType.TECHNIQUE_START.value == "technique_start"
        assert EventType.TECHNIQUE_COMPLETE.value == "technique_complete"
        assert EventType.TECHNIQUE_ERROR.value == "technique_error"
        assert EventType.CATEGORY_START.value == "category_start"
        assert EventType.CATEGORY_COMPLETE.value == "category_complete"
        assert EventType.DEEP_SYNTHESIS_START.value == "deep_synthesis_start"
        assert EventType.DEEP_SYNTHESIS_COMPLETE.value == "deep_synthesis_complete"
        assert EventType.QUALITY_GATE_COMPLETE.value == "quality_gate_complete"
        assert EventType.METRICS_UPDATE.value == "metrics_update"


class TestCriticalEventTypes:
    def test_critical_event_types_includes_technique_error(self):
        assert "technique_error" in CRITICAL_EVENT_TYPES

    def test_critical_event_types_includes_existing_events(self):
        assert "sommelier_error" in CRITICAL_EVENT_TYPES
        assert "evaluation_complete" in CRITICAL_EVENT_TYPES
        assert "evaluation_error" in CRITICAL_EVENT_TYPES


class TestCreateTechniqueEvent:
    def test_create_technique_event_returns_sse_event(self):
        event = create_technique_event(
            evaluation_id="eval_123",
            event_type="technique_start",
        )
        assert isinstance(event, SSEEvent)
        assert event.evaluation_id == "eval_123"
        assert event.event_type == EventType.TECHNIQUE_START

    def test_create_technique_event_with_all_fields(self):
        event = create_technique_event(
            evaluation_id="eval_456",
            event_type="technique_complete",
            technique_id="tech_001",
            technique_name="Code Quality Analysis",
            category_id="quality",
            progress_percent=50.5,
            score=85.0,
            max_score=100.0,
            confidence="high",
            duration_ms=1500,
            message="Technique completed successfully",
        )
        assert event.data["technique_id"] == "tech_001"
        assert event.data["technique_name"] == "Code Quality Analysis"
        assert event.data["category_id"] == "quality"
        assert event.data["progress_percent"] == 50.5
        assert event.data["score"] == 85.0
        assert event.data["max_score"] == 100.0
        assert event.data["confidence"] == "high"
        assert event.data["duration_ms"] == 1500
        assert event.data["message"] == "Technique completed successfully"

    def test_create_technique_event_default_values(self):
        event = create_technique_event(
            evaluation_id="eval_789",
            event_type="technique_error",
        )
        assert event.data["technique_id"] == ""
        assert event.data["technique_name"] == ""
        assert event.data["category_id"] == ""
        assert event.data["progress_percent"] == 0
        assert event.data["score"] is None
        assert event.data["max_score"] is None
        assert event.data["confidence"] is None
        assert event.data["duration_ms"] is None
        assert event.data["error_message"] is None
        assert event.data["message"] == ""

    def test_create_technique_event_to_dict(self):
        event = create_technique_event(
            evaluation_id="eval_abc",
            event_type="technique_start",
            technique_name="Test Technique",
        )
        result = event.to_dict()
        assert result["evaluation_id"] == "eval_abc"
        assert result["event_type"] == "technique_start"
        assert result["data"]["technique_name"] == "Test Technique"
        assert "timestamp" in result


class TestProgressTracker:
    def test_progress_tracker_starts_at_zero(self):
        tracker = ProgressTracker()
        assert tracker.completed == 0
        assert tracker.in_progress == 0
        assert tracker.failed == 0

    def test_progress_tracker_default_total_techniques(self):
        tracker = ProgressTracker()
        assert tracker.total_techniques == 75

    def test_progress_tracker_custom_total_techniques(self):
        tracker = ProgressTracker(total_techniques=100)
        assert tracker.total_techniques == 100

    def test_technique_started_increments_in_progress(self):
        tracker = ProgressTracker()
        tracker.technique_started()
        assert tracker.in_progress == 1
        tracker.technique_started()
        assert tracker.in_progress == 2

    def test_technique_completed_decrements_in_progress_and_increments_completed(self):
        tracker = ProgressTracker()
        tracker.technique_started()
        tracker.technique_started()
        assert tracker.in_progress == 2
        assert tracker.completed == 0

        tracker.technique_completed(duration_ms=1000)
        assert tracker.in_progress == 1
        assert tracker.completed == 1

        tracker.technique_completed(duration_ms=2000)
        assert tracker.in_progress == 0
        assert tracker.completed == 2

    def test_technique_completed_does_not_go_negative(self):
        tracker = ProgressTracker()
        assert tracker.in_progress == 0
        tracker.technique_completed()
        assert tracker.in_progress == 0

    def test_technique_completed_records_duration(self):
        tracker = ProgressTracker()
        tracker.technique_completed(duration_ms=1000)
        tracker.technique_completed(duration_ms=2000)
        assert tracker.eta_seconds is not None

    def test_technique_failed_increments_failed(self):
        tracker = ProgressTracker()
        tracker.technique_started()
        tracker.technique_started()
        assert tracker.in_progress == 2
        assert tracker.failed == 0

        tracker.technique_failed()
        assert tracker.in_progress == 1
        assert tracker.failed == 1

        tracker.technique_failed()
        assert tracker.in_progress == 0
        assert tracker.failed == 2

    def test_technique_failed_does_not_go_negative(self):
        tracker = ProgressTracker()
        assert tracker.in_progress == 0
        tracker.technique_failed()
        assert tracker.in_progress == 0

    def test_progress_percent_calculated_correctly(self):
        tracker = ProgressTracker(total_techniques=75)
        assert tracker.progress_percent == 0.0

        for _ in range(10):
            tracker.technique_completed()

        expected = (10 / 75) * 100
        assert tracker.progress_percent == pytest.approx(expected, rel=0.01)

    def test_progress_percent_with_failed_techniques(self):
        tracker = ProgressTracker(total_techniques=100)
        tracker.technique_completed()
        tracker.technique_completed()
        tracker.technique_failed()
        tracker.technique_failed()

        expected = (4 / 100) * 100
        assert tracker.progress_percent == pytest.approx(expected, rel=0.01)

    def test_progress_percent_zero_total_techniques(self):
        tracker = ProgressTracker(total_techniques=0)
        tracker.technique_completed()
        assert tracker.progress_percent == 0.0

    def test_eta_seconds_is_none_without_durations(self):
        tracker = ProgressTracker()
        assert tracker.eta_seconds is None

    def test_eta_seconds_computed_from_average_durations(self):
        tracker = ProgressTracker(total_techniques=10)
        tracker.technique_completed(duration_ms=1000)
        tracker.technique_completed(duration_ms=2000)
        tracker.technique_completed(duration_ms=3000)

        avg_duration_ms = (1000 + 2000 + 3000) / 3
        remaining = 10 - 3
        expected_eta = (remaining * avg_duration_ms) / 1000

        assert tracker.eta_seconds == pytest.approx(expected_eta, rel=0.01)

    def test_eta_seconds_updates_as_progress_increases(self):
        tracker = ProgressTracker(total_techniques=10)
        tracker.technique_completed(duration_ms=1000)

        eta_after_1 = tracker.eta_seconds
        assert eta_after_1 is not None

        for _ in range(5):
            tracker.technique_completed(duration_ms=1000)

        eta_after_6 = tracker.eta_seconds
        assert eta_after_6 is not None
        assert eta_after_6 < eta_after_1

    def test_summary_returns_correct_structure(self):
        tracker = ProgressTracker(total_techniques=100)
        tracker.technique_started()
        tracker.technique_completed(duration_ms=1000)
        tracker.technique_failed()

        summary = tracker.summary()
        assert summary["total"] == 100
        assert summary["completed"] == 1
        assert summary["in_progress"] == 0
        assert summary["failed"] == 1
        assert "progress_percent" in summary
        assert "eta_seconds" in summary
        assert "elapsed_seconds" in summary

    def test_summary_progress_percent_is_rounded(self):
        tracker = ProgressTracker(total_techniques=3)
        tracker.technique_completed()
        summary = tracker.summary()
        assert summary["progress_percent"] == 33.3

    def test_summary_elapsed_seconds_increases_over_time(self):
        tracker = ProgressTracker()
        summary1 = tracker.summary()
        time.sleep(0.15)
        summary2 = tracker.summary()
        assert summary2["elapsed_seconds"] > summary1["elapsed_seconds"]


class TestProgressTrackerThreadSafety:
    def test_concurrent_technique_started_updates(self):
        tracker = ProgressTracker()
        num_threads = 5
        updates_per_thread = 50

        def worker():
            for _ in range(updates_per_thread):
                tracker.technique_started()

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert tracker.in_progress == num_threads * updates_per_thread

    def test_concurrent_technique_completed_updates(self):
        tracker = ProgressTracker(total_techniques=500)
        num_threads = 5
        updates_per_thread = 25

        for _ in range(num_threads * updates_per_thread):
            tracker.technique_started()

        def worker():
            for _ in range(updates_per_thread):
                tracker.technique_completed(duration_ms=100)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert tracker.completed == num_threads * updates_per_thread
        assert tracker.in_progress == 0

    def test_concurrent_mixed_operations(self):
        tracker = ProgressTracker(total_techniques=150)
        num_threads = 5

        def worker():
            for i in range(5):
                tracker.technique_started()
                if i % 3 == 0:
                    tracker.technique_failed()
                else:
                    tracker.technique_completed(duration_ms=100)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert tracker.in_progress == 0
        assert tracker.completed + tracker.failed == 25

    def test_concurrent_summary_access(self):
        tracker = ProgressTracker(total_techniques=50)
        results = []

        def updater():
            for _ in range(10):
                tracker.technique_started()
                tracker.technique_completed(duration_ms=100)

        def reader():
            for _ in range(10):
                summary = tracker.summary()
                results.append(summary)

        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=updater))
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 30
        for summary in results:
            assert "total" in summary
            assert "completed" in summary
            assert "in_progress" in summary
            assert "failed" in summary


class TestProgressTrackerEdgeCases:
    def test_negative_duration_ignored(self):
        tracker = ProgressTracker()
        tracker.technique_completed(duration_ms=-100)
        assert tracker.eta_seconds is None

    def test_zero_duration_ignored(self):
        tracker = ProgressTracker()
        tracker.technique_completed(duration_ms=0)
        assert tracker.eta_seconds is None

    def test_large_number_of_techniques(self):
        tracker = ProgressTracker(total_techniques=10000)
        for _ in range(5000):
            tracker.technique_completed(duration_ms=100)
        assert tracker.progress_percent == 50.0

    def test_single_technique_total(self):
        tracker = ProgressTracker(total_techniques=1)
        assert tracker.progress_percent == 0.0
        tracker.technique_completed(duration_ms=1000)
        assert tracker.progress_percent == 100.0
