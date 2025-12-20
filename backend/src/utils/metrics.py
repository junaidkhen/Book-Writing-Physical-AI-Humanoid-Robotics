from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Lock
import time


@dataclass
class PerformanceMetrics:
    """
    Data class to store performance metrics for the RAG service.
    """
    total_queries: int = 0
    total_errors: int = 0
    total_tokens_used: int = 0
    total_retrieval_time: float = 0.0  # in milliseconds
    total_agent_time: float = 0.0      # in milliseconds
    total_time: float = 0.0            # in milliseconds
    start_time: datetime = field(default_factory=datetime.now)

    def avg_response_time(self) -> float:
        """Average response time in milliseconds."""
        if self.total_queries == 0:
            return 0.0
        return self.total_time / self.total_queries

    def avg_token_usage(self) -> float:
        """Average token usage."""
        if self.total_queries == 0:
            return 0.0
        return self.total_tokens_used / self.total_queries

    def error_rate(self) -> float:
        """Error rate as a percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.total_errors / self.total_queries) * 100

    def uptime(self) -> str:
        """Service uptime as a string."""
        duration = datetime.now() - self.start_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"


class MetricsTracker:
    """
    Singleton class to track metrics across the application.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.metrics = PerformanceMetrics()
                    cls._instance._lock = Lock()
        return cls._instance

    def record_query(
        self,
        retrieval_time: float,
        agent_time: float,
        total_time: float,
        tokens_used: int
    ) -> None:
        """
        Record metrics for a completed query.
        """
        with self._lock:
            self.metrics.total_queries += 1
            self.metrics.total_retrieval_time += retrieval_time
            self.metrics.total_agent_time += agent_time
            self.metrics.total_time += total_time
            self.metrics.total_tokens_used += tokens_used

    def record_error(self) -> None:
        """
        Record an error occurrence.
        """
        with self._lock:
            self.metrics.total_errors += 1

    def get_metrics(self) -> PerformanceMetrics:
        """
        Get current performance metrics.
        """
        with self._lock:
            return self.metrics

    def reset_metrics(self) -> None:
        """
        Reset all metrics to initial state.
        """
        with self._lock:
            self.metrics = PerformanceMetrics()


# Global metrics tracker instance
metrics_tracker = MetricsTracker()


def track_request_time():
    """
    Decorator to track execution time of functions.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                return result, execution_time
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                metrics_tracker.record_error()
                raise e
        return wrapper
    return decorator