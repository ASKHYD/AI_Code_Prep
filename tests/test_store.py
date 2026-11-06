
from coach.repetition import calculate_next_due
from coach.store import CoachStore


def test_repetition_schedule_exact_days():
    # 1. Failed problem: due in 1 day, consecutive passes resets to 0
    next_passes, interval = calculate_next_due(current_consecutive_passes=0, status="fail")
    assert next_passes == 0
    assert interval == 1

    # Failed again: still due in 1 day
    next_passes, interval = calculate_next_due(current_consecutive_passes=0, status="error")
    assert next_passes == 0
    assert interval == 1

    # Failed after previously having 2 passes: resets to 0 passes, due in 1 day
    next_passes, interval = calculate_next_due(current_consecutive_passes=2, status="timeout")
    assert next_passes == 0
    assert interval == 1

    # First pass after fail: due in 3 days
    next_passes, interval = calculate_next_due(current_consecutive_passes=0, status="pass")
    assert next_passes == 1
    assert interval == 3

    # Second consecutive pass: due in 7 days
    next_passes, interval = calculate_next_due(current_consecutive_passes=1, status="pass")
    assert next_passes == 2
    assert interval == 7

    # Third consecutive pass: due in 21 days
    next_passes, interval = calculate_next_due(current_consecutive_passes=2, status="pass")
    assert next_passes == 3
    assert interval == 21

    # Fourth consecutive pass: remains at 21 days
    next_passes, interval = calculate_next_due(current_consecutive_passes=3, status="pass")
    assert next_passes == 4
    assert interval == 21

def test_store_roundtrip_and_due_problems(tmp_path):
    db_file = tmp_path / "test_coach.db"
    store = CoachStore(db_path=str(db_file))

    base_time = "2026-11-04T00:00:00"

    # Record a failure on 'two-sum' -> FSRS step 0: due in 1 min (2026-11-04T00:01:00)
    store.record_attempt("two-sum", status="fail", runtime_ms=120, hints_used=1, mode="practice", attempt_date=base_time)

    # Record a pass on 'valid-parentheses' -> FSRS step 1: due in 10 min (2026-11-04T00:10:00)
    store.record_attempt("valid-parentheses", status="pass", runtime_ms=45, hints_used=0, mode="practice", attempt_date=base_time)

    # Check due problems at base time: none due yet
    due_start = store.due_problems(today="2026-11-04T00:00:00")
    assert len(due_start) == 0

    # Check due problems after 5 mins (00:05:00): 'two-sum' is due!
    due_soon = store.due_problems(today="2026-11-04T00:05:00")
    assert len(due_soon) == 1
    assert due_soon[0]["problem_id"] == "two-sum"

    # Check due problems after 15 mins (00:15:00): both are due!
    due_later = store.due_problems(today="2026-11-04T00:15:00")
    assert len(due_later) == 2

def test_store_topic_stats(tmp_path):
    db_file = tmp_path / "test_stats.db"
    store = CoachStore(db_path=str(db_file))

    # Assume problem topics: two-sum -> arrays, max-subarray -> arrays, valid-parentheses -> stack
    store.record_attempt("two-sum", status="pass", runtime_ms=50, hints_used=0, topic="arrays")
    store.record_attempt("max-subarray", status="fail", runtime_ms=100, hints_used=2, topic="arrays")
    store.record_attempt("valid-parentheses", status="pass", runtime_ms=30, hints_used=0, topic="stack")

    stats = store.topic_stats()
    assert "arrays" in stats
    assert stats["arrays"]["attempts"] == 2
    assert stats["arrays"]["passed"] == 1
    assert stats["arrays"]["pass_rate"] == 50.0

    assert "stack" in stats
    assert stats["stack"]["attempts"] == 1
    assert stats["stack"]["passed"] == 1
    assert stats["stack"]["pass_rate"] == 100.0

def test_store_streak_calculation(tmp_path):
    db_file = tmp_path / "test_streak.db"
    store = CoachStore(db_path=str(db_file))

    # Attempts on Nov 2, Nov 3, Nov 4 -> 3-day streak
    store.record_attempt("p1", status="pass", runtime_ms=10, hints_used=0, attempt_date="2026-11-02")
    store.record_attempt("p2", status="pass", runtime_ms=10, hints_used=0, attempt_date="2026-11-03")
    store.record_attempt("p3", status="pass", runtime_ms=10, hints_used=0, attempt_date="2026-11-04")

    streak = store.current_streak(today="2026-11-04")
    assert streak == 3

    # If gap on Nov 5 and checking Nov 6 -> streak is 0
    streak_gap = store.current_streak(today="2026-11-06")
    assert streak_gap == 0
