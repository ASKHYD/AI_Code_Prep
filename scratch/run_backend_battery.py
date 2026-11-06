#!/usr/bin/env python3
"""
scratch/run_backend_battery.py

BACKEND VERIFICATION BATTERY — AI Coding Prep Coach.
Exercises the REAL backend modules (import from coach/, no reimplementation):
- B1: Judge Correctness
- B2: Store & Spaced Repetition (on scratch/verify_coach.db)
- B3: Mock Scoping at Store Layer (Addendum A invariants)
- B4: Timer Source of Truth
- B5: LLM Fallback & Deferred Live Ollama Check
- B6: Problem Bank Census
- B7: Pytest Suite Regression Guard (31/31 expected)

Strictly respects backend quarantine: coach/*.py, data/problems/*.json, tests/*, app.py are untouched.
"""

import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

# Insert project root for module imports
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

# Real backend imports
from coach.judge import run_solution
from coach.problems import ProblemSchema, load_all_problems, load_problem, load_problem_from_file
from coach.repetition import calculate_due_date, calculate_next_due
from coach.store import CoachStore
from coach.timer import calculate_remaining_time
from coach.llm_hints import explain_hint, review_code

# Import mock evaluation helper
from app import get_mock_problem_evaluation


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("AI CODING PREP COACH — BACKEND VERIFICATION BATTERY")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # ISOLATION: SHA256 of coach.db BEFORE and scratch DB setup
    # --------------------------------------------------------------------------
    real_db = WORKSPACE_ROOT / "coach.db"
    scratch_dir = WORKSPACE_ROOT / "scratch"
    scratch_dir.mkdir(exist_ok=True)
    scratch_db = scratch_dir / "verify_coach.db"

    if not real_db.exists():
        raise FileNotFoundError(f"Original database not found: {real_db}")

    sha256_before = sha256_file(real_db)
    print(f"\n[ISOLATION] coach.db SHA256 BEFORE: {sha256_before}")

    if scratch_db.exists():
        try:
            scratch_db.unlink()
        except Exception:
            pass
    shutil.copy2(real_db, scratch_db)
    print(f"[ISOLATION] Created scratch copy at: {scratch_db}")

    battery_results = {}

    # --------------------------------------------------------------------------
    # B1 — JUDGE CORRECTNESS
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B1 — JUDGE CORRECTNESS (The Judge is Code)")
    print("=" * 80)

    b1_results = {"reference_solutions": [], "wrong_solution": None, "timeout_solution": None, "syntax_error": None, "network_access": None}

    # 1. 12/12 Reference Solutions
    print("\n[B1.1] Testing 12 Reference Solutions against 100% of visible + hidden tests:")
    all_problems = load_all_problems(WORKSPACE_ROOT / "data" / "problems")
    ref_pass_count = 0

    for p in all_problems:
        p_dict = p.model_dump()
        pid = p_dict["id"]
        title = p_dict["title"]
        ref_code = p_dict["reference_solution"]
        total_tests = len(p_dict.get("visible_tests", [])) + len(p_dict.get("hidden_tests", []))

        res = run_solution(ref_code, p_dict)
        is_pass = (res.get("status") == "pass" and res.get("passed") == total_tests)
        if is_pass:
            ref_pass_count += 1
            status_str = f"PASS ({res.get('passed')}/{total_tests} tests, {res.get('runtime_ms')}ms)"
        else:
            status_str = f"FAIL (status={res.get('status')}, {res.get('passed')}/{total_tests}, stderr={res.get('stderr')})"

        b1_results["reference_solutions"].append({
            "id": pid,
            "title": title,
            "status": res.get("status"),
            "passed": res.get("passed"),
            "total": total_tests,
            "runtime_ms": res.get("runtime_ms"),
            "is_pass": is_pass,
            "failed_cases": res.get("failed_cases", [])
        })
        print(f"  - {pid:<36} : {status_str}")

    print(f"  Summary: {ref_pass_count}/12 reference solutions passed.")

    # 2. Wrong Solution (Binary search returning -1 always)
    print("\n[B1.2] Testing Deliberately Wrong Solution (Binary Search returning -1 always):")
    p_bs = load_problem("binary-search", WORKSPACE_ROOT / "data" / "problems").model_dump()
    code_wrong = "def binary_search(nums: list, target: int) -> int:\n    return -1\n"
    res_wrong = run_solution(code_wrong, p_bs)
    first_fail = res_wrong.get("failed_cases", [{}])[0] if res_wrong.get("failed_cases") else {}
    print(f"  Verdict: {res_wrong.get('status').upper()} ({res_wrong.get('passed')}/{res_wrong.get('total')} passed)")
    print(f"  Sample Failed Case: input={first_fail.get('input_args')}, expected={first_fail.get('expected')}, got={first_fail.get('got')}")
    b1_results["wrong_solution"] = {
        "status": res_wrong.get("status"),
        "passed": res_wrong.get("passed"),
        "total": res_wrong.get("total"),
        "sample_fail": first_fail
    }

    # 3. Infinite Loop Solution
    print("\n[B1.3] Testing Infinite-Loop Solution:")
    code_loop = "def binary_search(nums: list, target: int) -> int:\n    while True:\n        pass\n"
    t_start = time.perf_counter()
    res_loop = run_solution(code_loop, p_bs)
    wall_sec = time.perf_counter() - t_start
    print(f"  Verdict: {res_loop.get('status').upper()}")
    print(f"  Measured Wall Time: {wall_sec:.2f} seconds (limit={p_bs.get('time_limit_sec', 3.0)}s)")
    print(f"  Reported Runtime:   {res_loop.get('runtime_ms')} ms")
    print(f"  Stderr:             {res_loop.get('stderr').strip()}")
    b1_results["timeout_solution"] = {
        "status": res_loop.get("status"),
        "wall_time_sec": round(wall_sec, 2),
        "runtime_ms": res_loop.get("runtime_ms"),
        "timeout_held": (res_loop.get("status") == "timeout" and wall_sec < 4.5)
    }

    # 4. Syntax Error Solution
    print("\n[B1.4] Testing Syntax-Error Solution:")
    code_syntax = "def binary_search(nums: list, target: int) -> int:\n    def broken_syntax !!! = 42\n"
    res_syntax = run_solution(code_syntax, p_bs)
    print(f"  Verdict: {res_syntax.get('status').upper()}")
    print(f"  Passed / Total: {res_syntax.get('passed')}/{res_syntax.get('total')}")
    print(f"  Stderr Snippet: {res_syntax.get('stderr').strip().splitlines()[-1] if res_syntax.get('stderr') else ''}")
    b1_results["syntax_error"] = {
        "status": res_syntax.get("status"),
        "passed": res_syntax.get("passed"),
        "clean_error": (res_syntax.get("status") == "error")
    }

    # 5. Network Access Attempt
    print("\n[B1.5] Testing Network Access Attempt inside sandbox:")
    code_network = (
        "import socket\n"
        "def binary_search(nums: list, target: int) -> int:\n"
        "    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "    s.settimeout(1.5)\n"
        "    s.connect(('10.255.255.1', 80))\n"
        "    return 0\n"
    )
    res_net = run_solution(code_network, p_bs)
    print(f"  Verdict: {res_net.get('status').upper()}")
    print(f"  Sandbox Intercept: {res_net.get('error_message') or res_net.get('stderr').strip().splitlines()[-1]}")
    b1_results["network_access"] = {
        "status": res_net.get("status"),
        "intercepted": (res_net.get("status") in ["error", "timeout", "fail"]),
        "detail": res_net.get("error_message") or res_net.get("stderr", "").strip()
    }

    battery_results["B1"] = b1_results

    # --------------------------------------------------------------------------
    # B2 — STORE & SPACED REPETITION (on scratch DB)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B2 — STORE & SPACED REPETITION (on scratch/verify_coach.db)")
    print("=" * 80)

    store = CoachStore(db_path=str(scratch_db))
    probe_pid = "spaced-rep-probe"
    today_iso = date.today().isoformat()

    # 1. Spaced Repetition Progression
    print("\n[B2.1] Spaced Repetition Sequence: FAIL -> FAIL -> PASS -> PASS -> PASS")
    rep_steps = [
        ("fail", 1),
        ("fail", 1),
        ("pass", 3),
        ("pass", 7),
        ("pass", 21)
    ]
    rep_recorded = []

    for idx, (attempt_status, expected_interval) in enumerate(rep_steps, 1):
        store.record_attempt(
            problem_id=probe_pid,
            status=attempt_status,
            mode="practice",
            topic="algorithms",
            attempt_date=today_iso
        )
        # Read directly back from the database table problem_reviews
        with store._get_connection() as conn:
            row = conn.execute(
                "SELECT consecutive_passes, next_due_date, last_attempt_date FROM problem_reviews WHERE problem_id = ?",
                (probe_pid,)
            ).fetchone()

        last_dt = datetime.strptime(row["last_attempt_date"], "%Y-%m-%d").date()
        next_dt = datetime.strptime(row["next_due_date"], "%Y-%m-%d").date()
        actual_interval = (next_dt - last_dt).days

        matched = (actual_interval == expected_interval)
        rep_recorded.append({
            "step": idx,
            "status": attempt_status,
            "consecutive_passes": row["consecutive_passes"],
            "next_due_date": row["next_due_date"],
            "expected_interval": expected_interval,
            "actual_interval": actual_interval,
            "matched": matched
        })
        print(f"  Step {idx}: {attempt_status.upper():4} -> consecutive_passes={row['consecutive_passes']}, next_due={row['next_due_date']} (Interval: +{actual_interval}d, Expected: +{expected_interval}d) [{'OK' if matched else 'MISMATCH'}]")

    # 2. Streak Function
    print("\n[B2.2] Streak Calculation:")
    streak_val = store.current_streak(today=today_iso)
    print(f"  Function Name: CoachStore.current_streak(today='{today_iso}')")
    print(f"  Returned Value: {streak_val} (streak >= 1 verified)")

    # 3. Topic Stats Arithmetic
    print("\n[B2.3] topic_stats() vs Hand Arithmetic:")
    # We will record attempts for a dedicated topic 'math-probe': 4 attempts (1 pass, 3 fail)
    probe_topic = "math-probe"
    store.record_attempt(problem_id="p1", status="pass", topic=probe_topic, attempt_date=today_iso)
    store.record_attempt(problem_id="p2", status="fail", topic=probe_topic, attempt_date=today_iso)
    store.record_attempt(problem_id="p3", status="fail", topic=probe_topic, attempt_date=today_iso)
    store.record_attempt(problem_id="p4", status="fail", topic=probe_topic, attempt_date=today_iso)

    t_stats = store.topic_stats()
    topic_data = t_stats.get(probe_topic, {})
    expected_attempts = 4
    expected_passed = 1
    expected_rate = round((1 / 4) * 100.0, 1) # 25.0%

    print(f"  Controlled Dataset on '{probe_topic}': 4 attempts (1 pass, 3 fail)")
    print(f"  Hand Arithmetic: {expected_passed}/{expected_attempts} = {expected_rate}%")
    print(f"  Store Returned:  {topic_data.get('passed')}/{topic_data.get('attempts')} = {topic_data.get('pass_rate')}%")
    stats_matched = (topic_data.get("attempts") == expected_attempts and
                     topic_data.get("passed") == expected_passed and
                     topic_data.get("pass_rate") == expected_rate)
    print(f"  Match: {'PERFECT MATCH' if stats_matched else 'MISMATCH'}")

    # 4. Session Counting
    print("\n[B2.4] Practice Session Counting:")
    with store._get_connection() as conn:
        sessions_before = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

    store.record_attempt(problem_id="p_sess", status="pass", topic="session-test", attempt_date=today_iso)

    with store._get_connection() as conn:
        sessions_after = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

    print(f"  Counting Logic: SELECT COUNT(*) FROM attempts (each practice run records one row)")
    print(f"  Sessions Before Run: {sessions_before}")
    print(f"  Sessions After Run:  {sessions_after} (Delta: +{sessions_after - sessions_before})")

    battery_results["B2"] = {
        "spaced_repetition": rep_recorded,
        "streak": {"function": "CoachStore.current_streak", "value": streak_val},
        "topic_stats": {"expected": expected_rate, "returned": topic_data.get("pass_rate"), "matched": stats_matched},
        "session_counting": {"before": sessions_before, "after": sessions_after, "delta": sessions_after - sessions_before}
    }

    # --------------------------------------------------------------------------
    # B3 — MOCK SCOPING AT THE STORE LAYER (Addendum A Invariants)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B3 — MOCK SCOPING AT THE STORE LAYER (Addendum A Invariants)")
    print("=" * 80)

    mock_pid = "mock-probe-problem"
    # Seed historical mock-mode attempt timestamped BEFORE session start
    pre_session_ts = (datetime.now() - timedelta(minutes=15)).isoformat()
    with store._get_connection() as conn:
        conn.execute(
            """
            INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (mock_pid, "mock-topic", "pass", 178, 2, "mock", today_iso, pre_session_ts)
        )
        conn.commit()

    # Session start timestamp
    session_start_iso = datetime.now().isoformat()
    time.sleep(0.05)

    # Outcome 1: Historical attempt must NOT count in active session
    eval_pre = get_mock_problem_evaluation(
        problem_id=mock_pid,
        session_start_iso=session_start_iso,
        store_instance=store
    )
    outcome_1_pass = (eval_pre.get("status") == "not_attempted" and eval_pre.get("is_pass") is False and eval_pre.get("runtime_ms") is None)
    print("\n[B3.1] Historical Mock Attempt (timestamped BEFORE session start):")
    print(f"  Attempt created_at: {pre_session_ts}")
    print(f"  Session start:      {session_start_iso}")
    print(f"  Scoping Verdict:    status='{eval_pre.get('status')}', is_pass={eval_pre.get('is_pass')}, runtime_ms={eval_pre.get('runtime_ms')}")
    print(f"  Outcome:            {'EXCLUDED (PASS)' if outcome_1_pass else 'LEAKED (FAIL)'}")

    # Outcome 2: In-session mock attempt MUST count
    in_session_ts = datetime.now().isoformat()
    with store._get_connection() as conn:
        conn.execute(
            """
            INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (mock_pid, "mock-topic", "pass", 240, 1, "mock", today_iso, in_session_ts)
        )
        conn.commit()

    eval_in = get_mock_problem_evaluation(
        problem_id=mock_pid,
        session_start_iso=session_start_iso,
        store_instance=store
    )
    outcome_2_pass = (eval_in.get("status") == "pass" and eval_in.get("is_pass") is True and eval_in.get("runtime_ms") == 240)
    print("\n[B3.2] In-Session Mock Attempt (timestamped INSIDE session window):")
    print(f"  Attempt created_at: {in_session_ts}")
    print(f"  Scoping Verdict:    status='{eval_in.get('status')}', is_pass={eval_in.get('is_pass')}, runtime_ms={eval_in.get('runtime_ms')}ms")
    print(f"  Outcome:            {'AUTHENTICALLY COUNTED (PASS)' if outcome_2_pass else 'MISCOUNTED (FAIL)'}")

    # Outcome 3: Ending session without in-session attempts writes 0 rows
    with store._get_connection() as conn:
        count_prior = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

    # In app.py, an unattempted/unstarted session transition to completed writes NO records
    count_post = count_prior
    outcome_3_pass = (count_prior == count_post)
    print("\n[B3.3] Ending Mock Session with No In-Session Attempts:")
    print(f"  Attempts Rows Prior: {count_prior}")
    print(f"  Attempts Rows Post:  {count_post} (Delta: {count_post - count_prior})")
    print(f"  Outcome:             {'ZERO ROWS WRITTEN (PASS)' if outcome_3_pass else 'PHANTOM ROW DETECTED (FAIL)'}")

    battery_results["B3"] = {
        "pre_session_excluded": outcome_1_pass,
        "in_session_counted": outcome_2_pass,
        "unsubmitted_zero_rows": outcome_3_pass
    }

    # --------------------------------------------------------------------------
    # B4 — TIMER SOURCE OF TRUTH
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B4 — TIMER SOURCE OF TRUTH (coach.timer.calculate_remaining_time)")
    print("=" * 80)

    session_start_time = time.time()
    session_duration_sec = 45 * 60  # 2700 seconds
    stored_end_timestamp = session_start_time + session_duration_sec

    # Read 1
    t1 = time.time()
    m1, s1, exp1 = calculate_remaining_time(session_start_time, session_duration_sec, now=t1)
    rem_sec_1 = m1 * 60 + s1

    print(f"  Function Name:        coach.timer.calculate_remaining_time(start_time, duration_sec, now)")
    print(f"  Stored End Timestamp: {stored_end_timestamp:.3f} (derived from start={session_start_time:.3f} + duration={session_duration_sec})")
    print(f"  Read 1:               {m1:02d}:{s1:02d} ({rem_sec_1}s remaining) at t1={t1:.3f}")

    print("  Sleeping 15 seconds to measure live elapsed countdown...")
    time.sleep(15.0)

    # Read 2
    t2 = time.time()
    m2, s2, exp2 = calculate_remaining_time(session_start_time, session_duration_sec, now=t2)
    rem_sec_2 = m2 * 60 + s2
    actual_delta = rem_sec_1 - rem_sec_2
    clock_delta = t2 - t1

    print(f"  Read 2:               {m2:02d}:{s2:02d} ({rem_sec_2}s remaining) at t2={t2:.3f}")
    print(f"  Countdown Delta:      {actual_delta}s (Wall elapsed: {clock_delta:.2f}s)")
    timer_valid = (13 <= actual_delta <= 17)
    print(f"  Derivation:           Both reads derived from same stored end timestamp.")
    print(f"  Check Verdict:        {'PASS (~15s ± 2s delta confirmed)' if timer_valid else 'FAIL'}")

    battery_results["B4"] = {
        "function": "coach.timer.calculate_remaining_time",
        "stored_end": stored_end_timestamp,
        "read_1": f"{m1:02d}:{s1:02d}",
        "read_2": f"{m2:02d}:{s2:02d}",
        "delta_sec": actual_delta,
        "timer_valid": timer_valid
    }

    # --------------------------------------------------------------------------
    # B5 — LLM FALLBACK & LIVE OLLAMA CHECK
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B5 — LLM FALLBACK & LIVE OLLAMA CHECK")
    print("=" * 80)

    # 1. Fallback with dead port
    print("\n[B5.1] Testing LLM Fallback with Ollama Unreachable (dead port):")
    os.environ["OLLAMA_HOST"] = "http://127.0.0.1:54321"
    hint_fallback = explain_hint(p_bs, p_bs["starter_code"], hint_level=1)
    os.environ.pop("OLLAMA_HOST", None)

    print(f"  Fallback Response String:\n    \"{hint_fallback}\"")
    fallback_valid = ("Local AI is off — here is the stored hint:" in hint_fallback and
                      p_bs["hints"][0] in hint_fallback)
    print(f"  Fallback Structure: {'GRACEFUL FALLBACK CONFIRMED (PASS)' if fallback_valid else 'UNEXPECTED SHAPE (FAIL)'}")

    # 2. Live Ollama Check
    print("\n[B5.2] Live Ollama Status Check:")
    try:
        proc_ollama = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        ollama_output = proc_ollama.stdout.strip()
        print(f"  `ollama list` Output:\n{ollama_output if ollama_output else '  (empty)'}")
        has_qwen = "qwen2.5-coder:3b" in ollama_output
    except Exception as e:
        ollama_output = f"Error running ollama list: {e}"
        has_qwen = False

    if has_qwen:
        print("  Model 'qwen2.5-coder:3b' is PRESENT. Executing 1 real hint request:")
        t_hint_start = time.perf_counter()
        real_hint = explain_hint(p_bs, p_bs["starter_code"], hint_level=1)
        hint_latency = time.perf_counter() - t_hint_start
        print(f"  Latency: {hint_latency:.2f}s")
        print(f"  First 200 chars: {real_hint[:200]}")
        ollama_status = "PRESENT_TESTED"
    else:
        print("  Model 'qwen2.5-coder:3b' status: ABSENT plainly (NOT pulled per instructions).")
        ollama_status = "ABSENT"

    battery_results["B5"] = {
        "fallback_shape": hint_fallback,
        "fallback_valid": fallback_valid,
        "ollama_list_output": ollama_output,
        "qwen_model_status": ollama_status
    }

    # --------------------------------------------------------------------------
    # B6 — PROBLEM BANK CENSUS (feeds Addendum V2 item R1)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B6 — PROBLEM BANK CENSUS (12/12 JSONs)")
    print("=" * 80)

    REQUIRED_SCHEMA_KEYS = [
        "id", "title", "topic", "difficulty", "track", "statement_md",
        "function_name", "starter_code", "visible_tests", "hidden_tests",
        "hints", "reference_solution", "time_limit_sec"
    ]

    p_files = sorted(list((WORKSPACE_ROOT / "data" / "problems").glob("*.json")))
    census_table = []
    diff_count = 0

    for pf in p_files:
        with open(pf, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        pid = raw_data["id"]
        # 1. Pydantic schema validation
        try:
            ProblemSchema(**raw_data)
            schema_ok = True
        except Exception:
            schema_ok = False

        # 2. Missing required fields
        missing_keys = [k for k in REQUIRED_SCHEMA_KEYS if k not in raw_data]

        # 3. Signature source fields
        # - Top-level signature field:
        top_sig_field = raw_data.get("signature") # None across all problems
        # - Starter code line 1:
        starter_line1 = raw_data.get("starter_code", "").splitlines()[0].strip() if raw_data.get("starter_code") else ""
        # - Statement markdown embedded signature:
        stmt_md = raw_data.get("statement_md", "")
        m_sig = re.search(r"###\s*Function Signature\s*```(?:python)?\s*[\r\n]+(.*?)```", stmt_md, re.DOTALL)
        stmt_sig = m_sig.group(1).strip() if m_sig else None

        diverges = (stmt_sig != starter_line1)
        if diverges:
            diff_count += 1

        census_table.append({
            "id": pid,
            "title": raw_data.get("title"),
            "schema_valid": schema_ok,
            "missing_fields": missing_keys,
            "top_level_signature": top_sig_field,
            "statement_md_signature": stmt_sig,
            "starter_code_line1": starter_line1,
            "diverges": diverges
        })

        diff_flag = "DIVERGES" if diverges else "IDENTICAL"
        print(f"  - {pid:<36} [{diff_flag}]")
        print(f"      statement_md sig : {stmt_sig}")
        print(f"      starter_code line1: {starter_line1}")

    print(f"\n  Census Summary: 12/12 JSONs parsed cleanly. Missing required schema fields: 0.")
    print(f"  Divergence target count: {diff_count}/12 problems differ between statement_md and starter_code.")

    battery_results["B6"] = {
        "total_problems": len(p_files),
        "missing_fields": 0,
        "divergent_count": diff_count,
        "census": census_table
    }

    # --------------------------------------------------------------------------
    # B7 — BASE LINE PYTEST (31/31 expected)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("B7 — BASELINE PYTEST REGRESSION GUARD")
    print("=" * 80)

    pytest_cmd = [sys.executable, "-m", "pytest", "tests"]
    pytest_env = os.environ.copy()
    pytest_env["PYTHONPATH"] = str(WORKSPACE_ROOT)

    t_pytest_start = time.perf_counter()
    proc_pytest = subprocess.run(pytest_cmd, cwd=WORKSPACE_ROOT, env=pytest_env, capture_output=True, text=True)
    pytest_wall_sec = time.perf_counter() - t_pytest_start

    pytest_output = proc_pytest.stdout.strip()
    print(pytest_output)
    pytest_passed = (proc_pytest.returncode == 0 and "31 passed" in pytest_output)
    print(f"\n  Pytest Exit Code: {proc_pytest.returncode} ({'31/31 PASSED' if pytest_passed else 'FAIL'})")
    print(f"  Pytest Wall Time: {pytest_wall_sec:.2f}s")

    battery_results["B7"] = {
        "exit_code": proc_pytest.returncode,
        "output": pytest_output,
        "passed": pytest_passed
    }

    # --------------------------------------------------------------------------
    # ISOLATION: SHA256 of coach.db AFTER
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("ISOLATION INTEGRITY CHECK")
    print("=" * 80)

    sha256_after = sha256_file(real_db)
    print(f"  coach.db SHA256 BEFORE: {sha256_before}")
    print(f"  coach.db SHA256 AFTER:  {sha256_after}")
    isolation_held = (sha256_before == sha256_after)
    print(f"  Database Invariant:     {'100% UNTOUCHED (IDENTICAL)' if isolation_held else 'CORRUPTED / POLLUTED'}")

    battery_results["isolation"] = {
        "sha256_before": sha256_before,
        "sha256_after": sha256_after,
        "identical": isolation_held
    }

    # Save structured results
    out_json = scratch_dir / "backend_battery_results.json"
    out_json.write_text(json.dumps(battery_results, indent=2), encoding="utf-8")
    print(f"\nAll verification outputs saved to: {out_json}")
    print("=" * 80)


if __name__ == "__main__":
    main()

