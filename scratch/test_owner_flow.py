from datetime import date, timedelta
from coach.problems import load_problem
from coach.judge import run_solution
from coach.store import CoachStore

print("=== STARTING OWNER FLOW TEST ===")
store = CoachStore("test_owner_flow.db")
p = load_problem("two-sum").model_dump()

# Step 1: Submit reference solution
print("1. Submitting reference solution for two-sum...")
res_pass = run_solution(p["reference_solution"], p)
print(f"   Judge Result: status={res_pass['status']}, passed={res_pass['passed']}/{res_pass['total']}, runtime_ms={res_pass['runtime_ms']}")
assert res_pass["status"] == "pass"
assert res_pass["passed"] == res_pass["total"]

# Step 2: Record attempt in store
today = date.today().isoformat()
tomorrow = (date.today() + timedelta(days=1)).isoformat()
store.record_attempt(p["id"], res_pass["status"], res_pass["runtime_ms"], hints_used=0, mode="practice", topic=p["topic"], attempt_date=today)

# Step 3: Verify dashboard topic stats
stats = store.topic_stats()
print(f"2. Dashboard topic stats: {stats.get('arrays')}")
assert stats["arrays"]["passed"] == 1

# Step 4: Submit failing code
print("3. Submitting failing solution for two-sum...")
res_fail = run_solution("def two_sum(nums, target): return []", p)
print(f"   Judge Result: status={res_fail['status']}, passed={res_fail['passed']}/{res_fail['total']}, failed_cases={len(res_fail['failed_cases'])}")
assert res_fail["status"] == "fail"

store.record_attempt(p["id"], res_fail["status"], res_fail["runtime_ms"], hints_used=1, mode="practice", topic=p["topic"], attempt_date=today)

# Step 5: Check Due for review on tomorrow
due_tomorrow = store.due_problems(today=tomorrow)
print(f"4. Due problems on {tomorrow}: {[d['problem_id'] for d in due_tomorrow]}")
assert any(d["problem_id"] == "two-sum" for d in due_tomorrow)

print("=== OWNER FLOW TEST PASSED COMPLETELY ===")
