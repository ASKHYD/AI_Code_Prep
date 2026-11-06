"""
Regression tests for CoachStore.current_streak.
Verifies Task 2.3 requirement:
- Streak calculation remains 100% activity-based (consecutive days with attempts).
- Unaffected by FSRS scheduling or individual problem outcomes (pass/fail).
"""

import tempfile
import pytest
from coach.store import CoachStore


@pytest.fixture
def temp_store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    store = CoachStore(db_path=db_path)
    yield store


def test_streak_calculation_continuous(temp_store):
    """Verifies that consecutive attempt dates build a continuous streak."""
    # Day 1: Fail on Nov 1
    temp_store.record_attempt("p1", status="fail", attempt_date="2026-11-01")
    assert temp_store.current_streak(today="2026-11-01") == 1

    # Day 2: Pass on Nov 2
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-02")
    assert temp_store.current_streak(today="2026-11-02") == 2

    # Day 3: Another attempt on Nov 3
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-03")
    assert temp_store.current_streak(today="2026-11-03") == 3


def test_streak_gap_resets(temp_store):
    """Verifies that a missing day breaks the streak."""
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-01")
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-02")
    # No attempts on Nov 3
    assert temp_store.current_streak(today="2026-11-03") == 0
    assert temp_store.current_streak(today="2026-11-04") == 0


def test_streak_multiple_attempts_same_day(temp_store):
    """Multiple attempts on the same day count as 1 day towards the streak."""
    temp_store.record_attempt("p1", status="fail", attempt_date="2026-11-01")
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-01")
    temp_store.record_attempt("p3", status="pass", attempt_date="2026-11-01")
    assert temp_store.current_streak(today="2026-11-01") == 1

