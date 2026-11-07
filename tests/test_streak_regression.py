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
    # Corrective C1: On Nov 3, yesterday (Nov 2) had activity, so streak is alive (2) awaiting Nov 3 activity
    assert temp_store.current_streak(today="2026-11-03") == 2
    # Corrective C1: On Nov 4, gap is older than yesterday (last attempt was 2 days ago) -> resets to 0
    assert temp_store.current_streak(today="2026-11-04") == 0


def test_streak_multiple_attempts_same_day(temp_store):
    """Multiple attempts on the same day count as 1 day towards the streak."""
    temp_store.record_attempt("p1", status="fail", attempt_date="2026-11-01")
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-01")
    temp_store.record_attempt("p3", status="pass", attempt_date="2026-11-01")
    assert temp_store.current_streak(today="2026-11-01") == 1


# --- Corrective C1 Specification Tests ---

def test_streak_yesterday_only(temp_store):
    """(i) yesterday-only -> 1 (Corrective C1: streak alive, awaiting today's practice)."""
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-06")
    assert temp_store.current_streak(today="2026-11-07") == 1


def test_streak_today_plus_yesterday(temp_store):
    """(ii) today + yesterday -> 2 (Corrective C1)."""
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-06")
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-07")
    assert temp_store.current_streak(today="2026-11-07") == 2


def test_streak_last_attempt_two_plus_days_ago(temp_store):
    """(iii) last attempt 2+ days ago -> 0 (Corrective C1)."""
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-05")
    # Today is Nov 7, yesterday is Nov 6 (both without activity)
    assert temp_store.current_streak(today="2026-11-07") == 0


def test_streak_chain_with_gap(temp_store):
    """(iv) chain with a gap (today, today-2) -> 1 (Corrective C1: yesterday missing breaks earlier chain)."""
    temp_store.record_attempt("p1", status="pass", attempt_date="2026-11-05")
    # Nov 6 has no attempt
    temp_store.record_attempt("p2", status="pass", attempt_date="2026-11-07")
    assert temp_store.current_streak(today="2026-11-07") == 1

