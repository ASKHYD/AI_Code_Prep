"""
Unit tests for FSRS history migration (Task 1.3).
Verifies:
- Idempotent migration from attempts table.
- Milo Audit Correction A1: card's due date is computed from the last attempt timestamp, not migration time.
- Passing last attempt maps to Good initial review; failing last attempt maps to Again.
- Attempts table is 100% untouched (zero writes).
- Running migration twice produces zero delta.
"""

import tempfile

import pytest

from coach.fsrs_engine import parse_utc_datetime
from coach.store import CoachStore


@pytest.fixture
def temp_store():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    store = CoachStore(db_path=db_path)
    yield store


def test_migration_a1_timestamp_and_idempotency(temp_store):
    """
    Verifies that:
    1. Migration seeds cards from historical attempts.
    2. Card due date derives from the problem's last attempt timestamp (A1).
    3. Re-running migration produces 0 new cards (idempotency).
    4. Attempts table is 100% untouched.
    """
    # 1. Seed sample attempts in the isolated store
    # Problem 1: binary-search, last attempt passed at 2026-11-01T10:00:00
    # Problem 2: two-sum, last attempt failed at 2026-11-03T15:00:00
    ts1_first = "2026-10-30T09:00:00"
    ts1_last = "2026-11-01T10:00:00"
    ts2_last = "2026-11-03T15:00:00"

    with temp_store._get_connection() as conn:
        conn.execute(
            """
            INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("binary-search", "algorithms", "fail", 100, 0, "practice", "2026-10-30", ts1_first)
        )
        conn.execute(
            """
            INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("binary-search", "algorithms", "pass", 80, 0, "practice", "2026-11-01", ts1_last)
        )
        conn.execute(
            """
            INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("two-sum", "arrays", "fail", 90, 0, "practice", "2026-11-03", ts2_last)
        )
        conn.commit()

    # Capture attempts snapshot before migration
    with temp_store._get_connection() as conn:
        cur = conn.execute("SELECT * FROM attempts ORDER BY id")
        attempts_before = [dict(row) for row in cur.fetchall()]

    # 2. Run first migration
    res1 = temp_store.migrate_history_to_fsrs()
    assert res1["migrated"] == 2
    assert res1["skipped"] == 0

    # 3. Verify attempts table is 100% UNTOUCHED
    with temp_store._get_connection() as conn:
        cur = conn.execute("SELECT * FROM attempts ORDER BY id")
        attempts_after = [dict(row) for row in cur.fetchall()]
    assert attempts_before == attempts_after

    # 4. Verify A1 Timestamp: Card due dates must be derived from last attempt timestamps
    card_bs = temp_store.get_fsrs_card("binary-search")
    assert card_bs is not None
    assert card_bs.last_review == parse_utc_datetime(ts1_last)
    # Passed attempt -> review was Good -> due date is in the future relative to ts1_last
    assert card_bs.due > parse_utc_datetime(ts1_last)
    # The due date must be relative to 2026-11-01, NOT relative to current wall time (e.g., year 2026-11-01)
    assert card_bs.due.year == 2026
    assert card_bs.due.month == 11
    assert card_bs.due.day in (1, 2, 3)

    card_ts = temp_store.get_fsrs_card("two-sum")
    assert card_ts is not None
    assert card_ts.last_review == parse_utc_datetime(ts2_last)
    # Failed attempt -> review was Again -> due date is within minutes of ts2_last
    assert card_ts.due.year == 2026
    assert card_ts.due.month == 11
    assert card_ts.due.day == 3

    # 5. Verify Idempotency: Running migration a second time produces 0 writes
    res2 = temp_store.migrate_history_to_fsrs()
    assert res2["migrated"] == 0
    assert res2["skipped"] == 2

    # Cards remain identical
    card_bs_second = temp_store.get_fsrs_card("binary-search")
    assert card_bs_second.card_id == card_bs.card_id
    assert card_bs_second.due == card_bs.due

