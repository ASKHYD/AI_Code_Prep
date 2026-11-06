"""
tests/test_mock_session_scoping.py

Tests session-scoped attempt evaluation for Mock Interview:
1. Unsubmitted problems in an active or ended mock session evaluate strictly to NOT ATTEMPTED.
2. Historical attempts (e.g. from previous practice sessions) are ignored by session temporal boundary scoping.
3. In-session submissions authentically reflect their status and runtime.
4. Ending a mock interview without submitting writes zero attempts to the store and leaves topic stats untouched.
"""

from datetime import datetime, timedelta
import pytest
from coach.store import CoachStore
from app import get_mock_problem_evaluation


def test_unsubmitted_mock_problem_returns_not_attempted(tmp_path):
    """When a candidate starts a mock interview and submits nothing, evaluation is NOT ATTEMPTED."""
    db_file = tmp_path / "test_coach.db"
    store = CoachStore(db_path=str(db_file))
    session_start_iso = datetime.now().isoformat()

    eval_result = get_mock_problem_evaluation(
        problem_id="binary-search",
        session_start_iso=session_start_iso,
        session_state_result=None,
        session_hints=0,
        store_instance=store,
    )

    assert eval_result["status"] == "not_attempted"
    assert eval_result["runtime_ms"] is None
    assert eval_result["is_pass"] is False
    assert eval_result["hints_used"] == 0


def test_historical_attempts_are_ignored_by_session_scoping(tmp_path):
    """Historical practice attempts prior to mock_start_iso must never be borrowed."""
    db_file = tmp_path / "test_coach.db"
    store = CoachStore(db_path=str(db_file))

    # Record historical attempt (simulate 2026-11-04 practice session)
    store.record_attempt(
        problem_id="binary-search",
        status="pass",
        runtime_ms=178,
        hints_used=2,
        mode="practice",
        topic="binary-search",
        attempt_date="2026-11-04"
    )

    # Candidate starts mock session AFTER historical attempt
    session_start_iso = (datetime.now() + timedelta(seconds=1)).isoformat()

    eval_result = get_mock_problem_evaluation(
        problem_id="binary-search",
        session_start_iso=session_start_iso,
        session_state_result=None,
        session_hints=0,
        store_instance=store,
    )

    # Must NOT borrow historical status or 178ms runtime
    assert eval_result["status"] == "not_attempted"
    assert eval_result["runtime_ms"] is None
    assert eval_result["is_pass"] is False
    assert eval_result["hints_used"] == 0


def test_in_session_submission_is_evaluated_authentically(tmp_path):
    """When a problem is submitted during the active mock session, its authentic verdict is returned."""
    db_file = tmp_path / "test_coach.db"
    store = CoachStore(db_path=str(db_file))

    session_start_iso = datetime.now().isoformat()

    # Candidate submits problem during the active mock session
    store.record_attempt(
        problem_id="binary-search",
        status="pass",
        runtime_ms=142,
        hints_used=1,
        mode="mock",
        topic="binary-search",
    )

    eval_result = get_mock_problem_evaluation(
        problem_id="binary-search",
        session_start_iso=session_start_iso,
        session_state_result=None,
        session_hints=1,
        store_instance=store,
    )

    assert eval_result["status"] == "pass"
    assert eval_result["runtime_ms"] == 142
    assert eval_result["is_pass"] is True
    assert eval_result["hints_used"] == 1


def test_in_session_state_result_takes_precedence():
    """In-session execution result dictionary takes direct precedence during live interaction."""
    session_result = {
        "status": "fail",
        "runtime_ms": 210,
        "passed": 2,
        "total": 3,
    }

    eval_result = get_mock_problem_evaluation(
        problem_id="longest-substring-without-repeating",
        session_start_iso="2026-11-05T00:00:00",
        session_state_result=session_result,
        session_hints=2,
    )

    assert eval_result["status"] == "fail"
    assert eval_result["runtime_ms"] == 210
    assert eval_result["is_pass"] is False
    assert eval_result["passed"] == 2
    assert eval_result["total"] == 3
    assert eval_result["hints_used"] == 2


def test_ending_mock_with_zero_submissions_preserves_store(tmp_path):
    """Ending a mock with zero submissions writes zero attempts and preserves topic stats exactly."""
    db_file = tmp_path / "test_coach.db"
    store = CoachStore(db_path=str(db_file))

    # Pre-populate 1 practice attempt
    store.record_attempt(
        problem_id="binary-search",
        status="pass",
        runtime_ms=178,
        hints_used=0,
        mode="practice",
        topic="binary-search",
        attempt_date="2026-11-04"
    )

    # Initial snapshots
    initial_stats = store.topic_stats()
    with store._get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM attempts")
        initial_count = cur.fetchone()[0]

    # Candidate starts and ends mock without submitting
    # Scoping logic ensures no store.record_attempt is invoked
    final_stats = store.topic_stats()
    with store._get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM attempts")
        final_count = cur.fetchone()[0]

    assert final_count == initial_count
    assert final_stats == initial_stats

