from datetime import date, timedelta
from coach.store import CoachStore

store = CoachStore("coach.db")
today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()
two_days_ago = (date.today() - timedelta(days=2)).isoformat()

# Seed attempts for streak
store.record_attempt("climbing-stairs", "pass", runtime_ms=35, hints_used=0, topic="dp", attempt_date=two_days_ago)
store.record_attempt("valid-parentheses", "pass", runtime_ms=45, hints_used=0, topic="stack", attempt_date=yesterday)

# Seed an attempt that is due today
# A failure yesterday makes it due today!
store.record_attempt("two-sum", "fail", runtime_ms=120, hints_used=1, topic="arrays", attempt_date=yesterday)

# Seed other topics for dashboard charts
store.record_attempt("longest-substring-without-repeating", "pass", runtime_ms=85, hints_used=1, topic="strings", attempt_date=today)
store.record_attempt("binary-search", "pass", runtime_ms=25, hints_used=0, topic="binary-search", attempt_date=today)
store.record_attempt("csv-column-summary", "pass", runtime_ms=90, hints_used=1, topic="data-transformation", attempt_date=today)
store.record_attempt("flatten-nested-dict", "fail", runtime_ms=60, hints_used=2, topic="dict-processing", attempt_date=today)

print("Database seeded successfully.")
print("Due today:", len(store.due_problems()))
print("Current streak:", store.current_streak())
print("Topic stats:", store.topic_stats())
