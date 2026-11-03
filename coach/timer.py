"""
AI Coding Prep Coach — Timer Module.
Pure functions for time calculations in mock interview sessions.
"""

from __future__ import annotations


def calculate_remaining_time(
    start_time: float, duration_sec: float, now: float
) -> tuple[int, int, bool]:
    """
    Pure function to calculate remaining time in a mock interview.

    Args:
        start_time: POSIX timestamp when session started
        duration_sec: Total allowed duration in seconds (e.g. 45 * 60 = 2700)
        now: Current POSIX timestamp

    Returns:
        (minutes, seconds, is_expired)
        If time has expired (remaining <= 0), returns (0, 0, True).
    """
    elapsed = max(0.0, now - start_time)
    remaining = duration_sec - elapsed
    if remaining <= 0.0:
        return 0, 0, True

    rem_int = int(remaining)
    minutes = rem_int // 60
    seconds = rem_int % 60
    return minutes, seconds, False
