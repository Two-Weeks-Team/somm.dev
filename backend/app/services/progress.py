import threading
import time
from dataclasses import dataclass, field


@dataclass
class ProgressTracker:
    """Thread-safe progress tracker for full_techniques evaluation."""

    total_techniques: int = 75
    _completed: int = field(default=0, init=False)
    _in_progress: int = field(default=0, init=False)
    _failed: int = field(default=0, init=False)
    _durations: list = field(default_factory=list, init=False)
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )
    _start_time: float = field(default_factory=time.time, init=False)

    def technique_started(self) -> None:
        with self._lock:
            self._in_progress += 1

    def technique_completed(self, duration_ms: int = 0) -> None:
        with self._lock:
            self._in_progress = max(0, self._in_progress - 1)
            self._completed += 1
            if duration_ms > 0:
                self._durations.append(duration_ms)

    def technique_failed(self) -> None:
        with self._lock:
            self._in_progress = max(0, self._in_progress - 1)
            self._failed += 1

    @property
    def completed(self) -> int:
        with self._lock:
            return self._completed

    @property
    def in_progress(self) -> int:
        with self._lock:
            return self._in_progress

    @property
    def failed(self) -> int:
        with self._lock:
            return self._failed

    @property
    def progress_percent(self) -> float:
        with self._lock:
            done = self._completed + self._failed
            return (
                (done / self.total_techniques * 100) if self.total_techniques > 0 else 0
            )

    @property
    def eta_seconds(self) -> float | None:
        with self._lock:
            if not self._durations:
                return None
            avg_ms = sum(self._durations) / len(self._durations)
            remaining = self.total_techniques - self._completed - self._failed
            return (remaining * avg_ms) / 1000

    def summary(self) -> dict:
        with self._lock:
            elapsed = time.time() - self._start_time
            done = self._completed + self._failed
            progress_pct = (
                (done / self.total_techniques * 100) if self.total_techniques > 0 else 0
            )
            if self._durations:
                avg_ms = sum(self._durations) / len(self._durations)
                remaining = self.total_techniques - done
                eta = (remaining * avg_ms) / 1000
            else:
                eta = None
            return {
                "total": self.total_techniques,
                "completed": self._completed,
                "in_progress": self._in_progress,
                "failed": self._failed,
                "progress_percent": round(progress_pct, 1),
                "eta_seconds": eta,
                "elapsed_seconds": round(elapsed, 1),
            }
