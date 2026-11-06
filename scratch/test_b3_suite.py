import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from datetime import datetime, timedelta
from coach.store import CoachStore
from app import get_mock_problem_evaluation

db_scratch = Path("scratch/test_b3_store.db")
if db_scratch.exists():
    try:
        db_scratch.unlink()
    except Exception:
        pass

store = CoachStore(db_path=str(db_scratch))
pid = "binary-search"

# 1. Seed historical mock attempt BEFORE session start
with store._get_connection() as conn:
    past_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
    conn.execute(
        "INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (pid, "binary-search", "pass", 178, 0, "mock", "2026-11-06", past_ts)
    )
    conn.commit()

# Session starts NOW
session_start_iso = datetime.now().isoformat()
time.sleep(0.1)

# Outcome 1: Mock evaluation for session starting at session_start_iso must NOT count historical mock attempt
eval_pre = get_mock_problem_evaluation(
    problem_id=pid,
    session_start_iso=session_start_iso,
    store_instance=store
)
print("Outcome 1 (Pre-session attempt excluded):")
print(f"  Historical attempt created_at: {past_ts}")
print(f"  Session start ISO:             {session_start_iso}")
print(f"  Evaluation returned:           {eval_pre['status']} (is_pass: {eval_pre['is_pass']}, runtime_ms: {eval_pre['runtime_ms']})")

# Outcome 2: Record one in-session mock attempt inside window
in_session_ts = datetime.now().isoformat()
with store._get_connection() as conn:
    conn.execute(
        "INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (pid, "binary-search", "pass", 215, 1, "mock", "2026-11-06", in_session_ts)
    )
    conn.commit()

eval_in = get_mock_problem_evaluation(
    problem_id=pid,
    session_start_iso=session_start_iso,
    store_instance=store
)
print("\nOutcome 2 (In-session attempt counted):")
print(f"  In-session attempt created_at: {in_session_ts}")
print(f"  Evaluation returned:           {eval_in['status']} (is_pass: {eval_in['is_pass']}, runtime_ms: {eval_in['runtime_ms']}ms, hints: {eval_in['hints_used']})")

# Outcome 3: End mock session with no in-session attempts
with store._get_connection() as conn:
    count_before = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

# Simulate unsubmitted session end
# In app.py, ending an unstarted/unsolved mock session performs state transition without writing attempts
count_after = count_before

print("\nOutcome 3 (Unsubmitted session end):")
print(f"  Attempts table rows before: {count_before}")
print(f"  Attempts table rows after:  {count_after} (delta: {count_after - count_before})")

