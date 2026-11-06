"""
DEPRECATED: Old deterministic 1/1/3/7/21-day ladder logic.
Retired in Milestone 2 Phase 3 in favor of FSRS adaptive repetition (coach/fsrs_engine.py).
Retained unreferenced in runtime for legacy contract reference and rollback safety.

Historical ladder:
- Failed problem: due in 1 day; subsequent fails: 1 day; resets consecutive_passes to 0.
- 1st consecutive pass: due in 3 days.
- 2nd consecutive pass: due in 7 days.
- 3rd+ consecutive pass: due in 21 days.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta


def get_next_consecutive_passes(current_consecutive_passes: int, status: str) -> int:
    """Calculates updated consecutive passes count based on outcome."""
    if status.lower() == "pass":
        return current_consecutive_passes + 1
    return 0


def calculate_next_due(current_consecutive_passes: int, status: str) -> tuple[int, int]:
    """
    Returns (next_consecutive_passes, interval_in_days).
    """
    if status.lower() != "pass":
        return 0, 1

    next_passes = current_consecutive_passes + 1
    if next_passes == 1:
        interval = 3
    elif next_passes == 2:
        interval = 7
    else:
        interval = 21
    return next_passes, interval


def calculate_due_date(
    current_consecutive_passes: int,
    status: str,
    from_date: str | None = None
) -> tuple[int, str]:
    """
    Returns (next_consecutive_passes, next_due_date_iso_string).
    """
    if from_date:
        base_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    else:
        base_date = date.today()

    next_passes, interval = calculate_next_due(current_consecutive_passes, status)
    due_date = base_date + timedelta(days=interval)
    return next_passes, due_date.isoformat()
