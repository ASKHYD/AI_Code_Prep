import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date, datetime
from coach.store import CoachStore

db_scratch = Path("scratch/test_b2_store.db")
if db_scratch.exists():
    db_scratch.unlink()

store = CoachStore(db_path=str(db_scratch))
today_iso = date.today().isoformat()
pid = "binary-search"

# 1. Spaced Repetition Sequence
print("--- Spaced Repetition Test ---")
steps = [
    ("fail", 1),
    ("fail", 1),
    ("pass", 3),
    ("pass", 7),
    ("pass", 21)
]

for i, (status, expected_int) in enumerate(steps, 1):
    store.record_attempt(problem_id=pid, status=status, mode="practice", topic="binary-search", attempt_date=today_iso)
    # Read back from store
    with store._get_connection() as conn:
        row = conn.execute("SELECT consecutive_passes, next_due_date, last_attempt_date FROM problem_reviews WHERE problem_id = ?", (pid,)).fetchone()
    
    last_d = datetime.strptime(row["last_attempt_date"], "%Y-%m-%d").date()
    next_d = datetime.strptime(row["next_due_date"], "%Y-%m-%d").date()
    actual_int = (next_d - last_d).days
    print(f"Step {i}: status={status.upper()} -> consecutive_passes={row['consecutive_passes']}, next_due={row['next_due_date']}, actual_interval=+{actual_int} days (expected +{expected_int}d)")

# 2. Streak
print("\n--- Streak Test ---")
streak_val = store.current_streak(today=today_iso)
print(f"Function: CoachStore.current_streak(today='{today_iso}') -> value: {streak_val}")

# 3. Topic Stats
print("\n--- Topic Stats Test ---")
# Currently in scratch DB for 'binary-search': 5 attempts (2 fail, 3 pass).
# Expected: attempts=5, passed=3, pass_rate = round(3/5 * 100, 1) = 60.0%
stats = store.topic_stats()
bs_stat = stats.get("binary-search", {})
print(f"Set: 5 attempts (2 fail, 3 pass). Hand arithmetic: 3/5 = 60.0%. Store returned: {bs_stat}")

# 4. Session Counting
print("\n--- Session Counting Test ---")
with store._get_connection() as conn:
    before_sessions = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

store.record_attempt(problem_id="two-sum", status="pass", topic="hash-table", attempt_date=today_iso)

with store._get_connection() as conn:
    after_sessions = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

print(f"Session counting query: SELECT COUNT(*) FROM attempts")
print(f"Before recorded run: {before_sessions}")
print(f"After recorded run: {after_sessions} (increment: +{after_sessions - before_sessions})")

if db_scratch.exists():
    db_scratch.unlink()

