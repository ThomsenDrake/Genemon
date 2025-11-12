"""
Performance profiling and benchmarking utilities for Genemon.

This module provides tools to measure and optimize performance of critical game systems.
"""

import time
import functools
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ProfileResult:
    """Result of a profiling run."""
    name: str
    duration: float  # seconds
    iterations: int
    avg_time: float  # seconds per iteration
    min_time: float
    max_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of profile result."""
        return (
            f"Profile: {self.name}\n"
            f"  Duration: {self.duration:.4f}s\n"
            f"  Iterations: {self.iterations}\n"
            f"  Avg: {self.avg_time*1000:.2f}ms\n"
            f"  Min: {self.min_time*1000:.2f}ms\n"
            f"  Max: {self.max_time*1000:.2f}ms"
        )


class PerformanceProfiler:
    """
    Performance profiler for measuring execution time of functions and code blocks.

    Usage:
        profiler = PerformanceProfiler()

        # As a decorator
        @profiler.profile("my_function")
        def my_function():
            pass

        # As a context manager
        with profiler.measure("code_block"):
            # code to measure
            pass

        # Manual timing
        profiler.start("operation")
        # ... code ...
        profiler.stop("operation")

        # Get results
        results = profiler.get_results()
    """

    def __init__(self):
        """Initialize the profiler."""
        self.measurements: Dict[str, List[float]] = defaultdict(list)
        self.active_timers: Dict[str, float] = {}
        self.metadata: Dict[str, Dict] = {}

    def profile(self, name: str = None, enabled: bool = True):
        """
        Decorator to profile a function.

        Args:
            name: Name for the profiling entry (defaults to function name)
            enabled: Whether profiling is enabled

        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            profile_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not enabled:
                    return func(*args, **kwargs)

                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start
                    self.measurements[profile_name].append(duration)

            return wrapper
        return decorator

    def measure(self, name: str):
        """
        Context manager to measure a code block.

        Args:
            name: Name for the profiling entry

        Usage:
            with profiler.measure("my_code"):
                # code to measure
                pass
        """
        class MeasureContext:
            def __init__(ctx_self, profiler, name):
                ctx_self.profiler = profiler
                ctx_self.name = name
                ctx_self.start_time = None

            def __enter__(ctx_self):
                ctx_self.start_time = time.perf_counter()
                return ctx_self

            def __exit__(ctx_self, exc_type, exc_val, exc_tb):
                duration = time.perf_counter() - ctx_self.start_time
                ctx_self.profiler.measurements[ctx_self.name].append(duration)
                return False

        return MeasureContext(self, name)

    def start(self, name: str):
        """
        Start timing an operation.

        Args:
            name: Name for the profiling entry
        """
        self.active_timers[name] = time.perf_counter()

    def stop(self, name: str) -> float:
        """
        Stop timing an operation and record the duration.

        Args:
            name: Name for the profiling entry

        Returns:
            Duration in seconds

        Raises:
            KeyError: If timer was not started
        """
        if name not in self.active_timers:
            raise KeyError(f"Timer '{name}' was not started")

        start_time = self.active_timers.pop(name)
        duration = time.perf_counter() - start_time
        self.measurements[name].append(duration)
        return duration

    def add_metadata(self, name: str, metadata: Dict[str, Any]):
        """
        Add metadata to a profiling entry.

        Args:
            name: Name of the profiling entry
            metadata: Metadata dictionary
        """
        if name not in self.metadata:
            self.metadata[name] = {}
        self.metadata[name].update(metadata)

    def get_result(self, name: str) -> Optional[ProfileResult]:
        """
        Get profiling result for a specific entry.

        Args:
            name: Name of the profiling entry

        Returns:
            ProfileResult if measurements exist, None otherwise
        """
        if name not in self.measurements or not self.measurements[name]:
            return None

        measurements = self.measurements[name]
        total_duration = sum(measurements)
        iterations = len(measurements)

        return ProfileResult(
            name=name,
            duration=total_duration,
            iterations=iterations,
            avg_time=total_duration / iterations,
            min_time=min(measurements),
            max_time=max(measurements),
            metadata=self.metadata.get(name, {})
        )

    def get_results(self) -> List[ProfileResult]:
        """
        Get all profiling results.

        Returns:
            List of ProfileResult objects sorted by total duration (descending)
        """
        results = []
        for name in self.measurements:
            result = self.get_result(name)
            if result:
                results.append(result)

        # Sort by total duration (highest first)
        results.sort(key=lambda r: r.duration, reverse=True)
        return results

    def clear(self, name: str = None):
        """
        Clear measurements.

        Args:
            name: Name of specific entry to clear, or None to clear all
        """
        if name is None:
            self.measurements.clear()
            self.metadata.clear()
            self.active_timers.clear()
        else:
            if name in self.measurements:
                del self.measurements[name]
            if name in self.metadata:
                del self.metadata[name]
            if name in self.active_timers:
                del self.active_timers[name]

    def print_results(self, min_duration: float = 0.0):
        """
        Print profiling results to console.

        Args:
            min_duration: Minimum total duration to display (in seconds)
        """
        results = self.get_results()

        if not results:
            print("No profiling data available.")
            return

        print("\n" + "=" * 70)
        print("PERFORMANCE PROFILING RESULTS")
        print("=" * 70)

        for result in results:
            if result.duration >= min_duration:
                print(f"\n{result}")
                if result.metadata:
                    print("  Metadata:")
                    for key, value in result.metadata.items():
                        print(f"    {key}: {value}")

        print("\n" + "=" * 70)


# Global profiler instance
_global_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """
    Get the global profiler instance.

    Returns:
        Global PerformanceProfiler instance
    """
    return _global_profiler


def profile(name: str = None, enabled: bool = True):
    """
    Decorator to profile a function using the global profiler.

    Args:
        name: Name for the profiling entry (defaults to function name)
        enabled: Whether profiling is enabled

    Returns:
        Decorated function

    Usage:
        @profile("my_function")
        def my_function():
            pass
    """
    return _global_profiler.profile(name, enabled)
