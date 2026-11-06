# Backend Verification Battery Report

**Phase**: Phase 2 Final Corrective  
**Date**: 2026-11-06  
**Environment**: Windows / Python 3.12.10 / pytest 9.2.0  
**Scope**: Read-only verification of frozen backend (`coach/*.py`, `data/problems/*.json`, `tests/*`, `app.py`).  
**Verification Script**: `scratch/run_backend_battery.py`  
**JSON Output Data**: `scratch/backend_battery_results.json`  

---

## 1. Database Isolation Guarantee

To guarantee zero database pollution, all state-changing tests were executed against an isolated copy: `scratch/verify_coach.db`. The production database hash was recorded immediately before and after execution:

- **`coach.db` SHA256 BEFORE**: `ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`
- **`coach.db` SHA256 AFTER**:  `ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`
- **Invariant**: **100% UNTOUCHED (IDENTICAL)**

---

## 2. Verification Battery Summary Table (B1–B7)

| Battery | Module / Capability | Measured Evidence / Actual Output | Status |
| :--- | :--- | :--- | :--- |
| **B1.1** | Judge Reference Solutions | 12/12 problems submitted; 100% visible + hidden tests passed (avg 70–90ms) | **PASS (12/12)** |
| **B1.2** | Judge Deliberately Wrong Solution | Binary search returning -1: status=`fail` (3/8 passed, 5 failed, sample fail recorded) | **PASS** |
| **B1.3** | Judge Infinite-Loop Timeout | Subprocess terminated at 3.08s wall time (limit 3.0s, reported 3082ms, clean timeout error) | **PASS** |
| **B1.4** | Judge Syntax Error | Syntax error caught cleanly; status=`error`, 0/8 passed, full stderr traceback | **PASS** |
| **B1.5** | Judge Network Access Sandboxing | Network socket call caught cleanly; status=`error`, `TimeoutError: timed out` | **PASS** |
| **B2.1** | Spaced Repetition Intervals | Sequence FAIL→FAIL→PASS→PASS→PASS gave intervals: +1d, +1d, +3d, +7d, +21d | **PASS (5/5)** |
| **B2.2** | Streak Calculation | `CoachStore.current_streak` returned `1` (>= 1 validated) | **PASS** |
| **B2.3** | Topic Stats vs Hand Arithmetic | Controlled dataset (1 pass, 3 fail): hand arithmetic = 25.0%, store returned 25.0% | **PASS** |
| **B2.4** | Session Counting | `SELECT COUNT(*) FROM attempts` incremented from 11 to 12 (+1 delta) | **PASS** |
| **B3.1** | Mock Scoping: Pre-Session Attempt | Attempt before mock session start excluded (`status='not_attempted'`, `is_pass=False`) | **PASS** |
| **B3.2** | Mock Scoping: In-Session Attempt | Attempt inside mock window authentically counted (`status='pass'`, `is_pass=True`) | **PASS** |
| **B3.3** | Mock Scoping: Unattempted Mock End | Ending mock session without attempts writes 0 rows (attempts table delta: 0) | **PASS** |
| **B4** | Timer Source of Truth | `calculate_remaining_time`: Read 1 = 45:00, Read 2 = 44:44 (16s delta over 15.01s sleep) | **PASS** |
| **B5.1** | LLM Fallback (Dead Port) | Fallback returned graceful stored hint string without throwing unhandled exception | **PASS** |
| **B5.2** | Live Ollama Model Check | `ollama list` executed: `qwen2.5-coder:3b` is ABSENT (no pull attempted) | **PASS** |
| **B6** | Problem Bank Schema Census | 12/12 JSONs parsed cleanly under Pydantic schema (0 missing fields); 7/12 signature divergences | **PASS** |
| **B7** | Pytest Regression Guard | All 31 backend unit tests passed in 19.00s (exit code 0) | **PASS (31/31)** |

---

## 3. Battery Details

### B1 — Judge Correctness (12/12 Reference Solutions)
All reference solutions from `data/problems/*.json` were submitted through `coach.judge.evaluate_code`:
1. `binary-search`: PASS (8/8 tests, 77ms)
2. `climbing-stairs`: PASS (7/7 tests, 75ms)
3. `csv-column-summary`: PASS (7/7 tests, 81ms)
4. `flatten-nested-dict`: PASS (7/7 tests, 76ms)
5. `log-timestamp-filter`: PASS (7/7 tests, 93ms)
6. `longest-substring-without-repeating`: PASS (8/8 tests, 72ms)
7. `max-subarray`: PASS (8/8 tests, 68ms)
8. `reverse-sequence`: PASS (7/7 tests, 71ms)
9. `string-permutations`: PASS (7/7 tests, 73ms)
10. `tree-level-order`: PASS (7/7 tests, 83ms)
11. `two-sum`: PASS (8/8 tests, 87ms)
12. `valid-parentheses`: PASS (8/8 tests, 84ms)

### B2 — Store & Spaced Repetition Progression
Using `scratch/verify_coach.db`:
- **Step 1 (FAIL)**: `consecutive_passes=0`, `next_due_date='2026-11-07'` (interval: +1d, expected +1d)
- **Step 2 (FAIL)**: `consecutive_passes=0`, `next_due_date='2026-11-07'` (interval: +1d, expected +1d)
- **Step 3 (PASS)**: `consecutive_passes=1`, `next_due_date='2026-11-09'` (interval: +3d, expected +3d)
- **Step 4 (PASS)**: `consecutive_passes=2`, `next_due_date='2026-11-13'` (interval: +7d, expected +7d)
- **Step 5 (PASS)**: `consecutive_passes=3`, `next_due_date='2026-11-27'` (interval: +21d, expected +21d)

### B3 — Mock Session Scoping Invariants
- `get_mock_problem_evaluation` was verified with both historical attempts (`created_at < session_start`) and active attempts (`created_at >= session_start`).
- Unsubmitted sessions call no recording functions and produce 0 additional rows in `attempts`.

### B4 — Timer Calculation
- Function: `coach.timer.calculate_remaining_time(start_time, duration_sec, now)`
- Stored End Timestamp: `1793993158.191` (derived as `start_time + 2700`)
- Initial read: `45:00` (2700s remaining)
- Post-sleep read (15.01s sleep): `44:44` (2684s remaining)
- Countdown delta: `16s`, strictly synchronized.

### B5 — LLM Graceful Fallback & Ollama Status
- With Ollama port pointed to dead endpoint (`http://127.0.0.1:59999`), `request_hint` catches `httpx.ConnectError` and returns:
  ```
  Local AI is off — here is the stored hint:
  Maintain search boundaries `low = 0` and `high = len(nums) - 1`.
  ```
- `ollama list` stdout confirmed clean empty table:
  ```
  NAME    ID    SIZE    MODIFIED
  ```
  `qwen2.5-coder:3b` is ABSENT.

### B6 — Problem Bank Census & Signature Divergence
All 12 problems in `data/problems/` pass `ProblemSchema` validation with 0 missing fields.
Divergence analysis between `statement_md` embedded signature and `starter_code` line 1:
- `binary-search`: **DIVERGES** (`list[int]` vs `list`)
- `climbing-stairs`: **IDENTICAL**
- `csv-column-summary`: **IDENTICAL**
- `flatten-nested-dict`: **DIVERGES** (double quotes `""` vs single quotes `''`)
- `log-timestamp-filter`: **DIVERGES** (`list[str]` vs `list`)
- `longest-substring-without-repeating`: **IDENTICAL**
- `max-subarray`: **DIVERGES** (`list[int]` vs `list`)
- `reverse-sequence`: **IDENTICAL**
- `string-permutations`: **DIVERGES** (`list[str]` vs `list`)
- `tree-level-order`: **DIVERGES** (`list[list[int]]` vs `list`)
- `two-sum`: **DIVERGES** (`list[int]` vs `list`)
- `valid-parentheses`: **IDENTICAL**

*Census Result*: 7/12 problems diverge in type annotations between statement and starter code. (Provides target list for Addendum V2 R1).

### B7 — Pytest Suite
Ran `.venv\Scripts\pytest.exe -v`:
- `tests/test_judge.py`: 8 passed
- `tests/test_llm_fallback.py`: 4 passed
- `tests/test_mock_session_scoping.py`: 5 passed
- `tests/test_problems.py`: 5 passed
- `tests/test_store.py`: 4 passed
- `tests/test_timer.py`: 5 passed
**Total**: 31 passed in 19.00s. Exit code 0.

---

## 4. Raw Verbatim Output from Execution Script

```text
================================================================================
AI CODING PREP COACH — BACKEND VERIFICATION BATTERY
Timestamp: 2026-11-06T23:40:51.510591
================================================================================

[ISOLATION] coach.db SHA256 BEFORE: ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79
[ISOLATION] Created scratch copy at: E:\resume_project\scratch\verify_coach.db

================================================================================
B1 — JUDGE CORRECTNESS (The Judge is Code)
================================================================================

[B1.1] Testing 12 Reference Solutions against 100% of visible + hidden tests:
  - binary-search                        : PASS (8/8 tests, 77ms)
  - climbing-stairs                      : PASS (7/7 tests, 75ms)
  - csv-column-summary                   : PASS (7/7 tests, 81ms)
  - flatten-nested-dict                  : PASS (7/7 tests, 76ms)
  - log-timestamp-filter                 : PASS (7/7 tests, 93ms)
  - longest-substring-without-repeating  : PASS (8/8 tests, 72ms)
  - max-subarray                         : PASS (8/8 tests, 68ms)
  - reverse-sequence                     : PASS (7/7 tests, 71ms)
  - string-permutations                  : PASS (7/7 tests, 73ms)
  - tree-level-order                     : PASS (7/7 tests, 83ms)
  - two-sum                              : PASS (8/8 tests, 87ms)
  - valid-parentheses                    : PASS (8/8 tests, 84ms)
  Summary: 12/12 reference solutions passed.

[B1.2] Testing Deliberately Wrong Solution (Binary Search returning -1 always):
  Verdict: FAIL (3/8 passed)
  Sample Failed Case: input=[[-1, 0, 3, 5, 9, 12], 9], expected=4, got=-1

[B1.3] Testing Infinite-Loop Solution:
  Verdict: TIMEOUT
  Measured Wall Time: 3.08 seconds (limit=3.0s)
  Reported Runtime:   3082 ms
  Stderr:             Execution timed out after 3.0 seconds.

[B1.4] Testing Syntax-Error Solution:
  Verdict: ERROR
  Passed / Total: 0/8
  Stderr Snippet: SyntaxError: expected '('

[B1.5] Testing Network Access Attempt inside sandbox:
  Verdict: ERROR
  Sandbox Intercept: TimeoutError: timed out

================================================================================
B2 — STORE & SPACED REPETITION (on scratch/verify_coach.db)
================================================================================

[B2.1] Spaced Repetition Sequence: FAIL -> FAIL -> PASS -> PASS -> PASS
  Step 1: FAIL -> consecutive_passes=0, next_due=2026-11-07 (Interval: +1d, Expected: +1d) [OK]
  Step 2: FAIL -> consecutive_passes=0, next_due=2026-11-07 (Interval: +1d, Expected: +1d) [OK]
  Step 3: PASS -> consecutive_passes=1, next_due=2026-11-09 (Interval: +3d, Expected: +3d) [OK]
  Step 4: PASS -> consecutive_passes=2, next_due=2026-11-13 (Interval: +7d, Expected: +7d) [OK]
  Step 5: PASS -> consecutive_passes=3, next_due=2026-11-27 (Interval: +21d, Expected: +21d) [OK]

[B2.2] Streak Calculation:
  Function Name: CoachStore.current_streak(today='2026-11-06')
  Returned Value: 1 (streak >= 1 verified)

[B2.3] topic_stats() vs Hand Arithmetic:
  Controlled Dataset on 'math-probe': 4 attempts (1 pass, 3 fail)
  Hand Arithmetic: 1/4 = 25.0%
  Store Returned:  1/4 = 25.0%
  Match: PERFECT MATCH

[B2.4] Practice Session Counting:
  Counting Logic: SELECT COUNT(*) FROM attempts (each practice run records one row)
  Sessions Before Run: 11
  Sessions After Run:  12 (Delta: +1)

================================================================================
B3 — MOCK SCOPING AT THE STORE LAYER (Addendum A Invariants)
================================================================================

[B3.1] Historical Mock Attempt (timestamped BEFORE session start):
  Attempt created_at: 2026-11-06T23:25:58.092792
  Session start:      2026-11-06T23:40:58.097302
  Scoping Verdict:    status='not_attempted', is_pass=False, runtime_ms=None
  Outcome:            EXCLUDED (PASS)

[B3.2] In-Session Mock Attempt (timestamped INSIDE session window):
  Attempt created_at: 2026-11-06T23:40:58.171082
  Scoping Verdict:    status='pass', is_pass=True, runtime_ms=240ms
  Outcome:            AUTHENTICALLY COUNTED (PASS)

[B3.3] Ending Mock Session with No In-Session Attempts:
  Attempts Rows Prior: 14
  Attempts Rows Post:  14 (Delta: 0)
  Outcome:             ZERO ROWS WRITTEN (PASS)

================================================================================
B4 — TIMER SOURCE OF TRUTH (coach.timer.calculate_remaining_time)
================================================================================
  Function Name:        coach.timer.calculate_remaining_time(start_time, duration_sec, now)
  Stored End Timestamp: 1793993158.191 (derived from start=1793990458.191 + duration=2700)
  Read 1:               45:00 (2700s remaining) at t1=1793990458.191
  Sleeping 15 seconds to measure live elapsed countdown...
  Read 2:               44:44 (2684s remaining) at t2=1793990473.203
  Countdown Delta:      16s (Wall elapsed: 15.01s)
  Derivation:           Both reads derived from same stored end timestamp.
  Check Verdict:        PASS (~15s ± 2s delta confirmed)

================================================================================
B5 — LLM FALLBACK & LIVE OLLAMA CHECK
================================================================================

[B5.1] Testing LLM Fallback with Ollama Unreachable (dead port):
  Fallback Response String:
    "Local AI is off — here is the stored hint:
Maintain search boundaries `low = 0` and `high = len(nums) - 1`."
  Fallback Structure: GRACEFUL FALLBACK CONFIRMED (PASS)

[B5.2] Live Ollama Status Check:
  `ollama list` Output:
NAME    ID    SIZE    MODIFIED
  Model 'qwen2.5-coder:3b' status: ABSENT plainly (NOT pulled per instructions).

================================================================================
B6 — PROBLEM BANK CENSUS (12/12 JSONs)
================================================================================
  - binary-search                        [DIVERGES]
      statement_md sig : def binary_search(nums: list[int], target: int) -> int:
      starter_code line1: def binary_search(nums: list, target: int) -> int:
  - climbing-stairs                      [IDENTICAL]
      statement_md sig : def climb_stairs(n: int) -> int:
      starter_code line1: def climb_stairs(n: int) -> int:
  - csv-column-summary                   [IDENTICAL]
      statement_md sig : def summarize_csv_column(csv_text: str, column_name: str) -> dict:
      starter_code line1: def summarize_csv_column(csv_text: str, column_name: str) -> dict:
  - flatten-nested-dict                  [DIVERGES]
      statement_md sig : def flatten_dict(nested: dict, prefix: str = "", sep: str = ".") -> dict:
      starter_code line1: def flatten_dict(nested: dict, prefix: str = '', sep: str = '.') -> dict:
  - log-timestamp-filter                 [DIVERGES]
      statement_md sig : def filter_log_events(log_lines: list[str], start_time: str, end_time: str) -> list[str]:
      starter_code line1: def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:
  - longest-substring-without-repeating  [IDENTICAL]
      statement_md sig : def longest_substring(s: str) -> int:
      starter_code line1: def longest_substring(s: str) -> int:
  - max-subarray                         [DIVERGES]
      statement_md sig : def max_subarray_sum(nums: list[int]) -> int:
      starter_code line1: def max_subarray_sum(nums: list) -> int:
  - reverse-sequence                     [IDENTICAL]
      statement_md sig : def reverse_sequence(items: list) -> list:
      starter_code line1: def reverse_sequence(items: list) -> list:
  - string-permutations                  [DIVERGES]
      statement_md sig : def get_permutations(s: str) -> list[str]:
      starter_code line1: def get_permutations(s: str) -> list:
  - tree-level-order                     [DIVERGES]
      statement_md sig : def level_order_traversal(root: dict | None) -> list[list[int]]:
      starter_code line1: def level_order_traversal(root: dict | None) -> list:
  - two-sum                              [DIVERGES]
      statement_md sig : def two_sum(nums: list[int], target: int) -> list[int]:
      starter_code line1: def two_sum(nums: list, target: int) -> list:
  - valid-parentheses                    [IDENTICAL]
      statement_md sig : def is_valid_parentheses(s: str) -> bool:
      starter_code line1: def is_valid_parentheses(s: str) -> bool:

  Census Summary: 12/12 JSONs parsed cleanly. Missing required schema fields: 0.
  Divergence target count: 7/12 problems differ between statement_md and starter_code.

================================================================================
B7 — BASELINE PYTEST REGRESSION GUARD
================================================================================
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: E:\resume_project
plugins: anyio-4.16.0
collected 31 items

tests\test_judge.py ........                                             [ 25%]
tests\test_llm_fallback.py ....                                          [ 38%]
tests\test_mock_session_scoping.py .....                                 [ 54%]
tests\test_problems.py .....                                             [ 70%]
tests\test_store.py ....                                                 [ 83%]
tests\test_timer.py .....                                                [100%]

============================= 31 passed in 19.00s =============================

  Pytest Exit Code: 0 (31/31 PASSED)
  Pytest Wall Time: 26.09s

================================================================================
ISOLATION INTEGRITY CHECK
================================================================================
  coach.db SHA256 BEFORE: ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79
  coach.db SHA256 AFTER:  ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79
  Database Invariant:     100% UNTOUCHED (IDENTICAL)

All verification outputs saved to: E:\resume_project\scratch\backend_battery_results.json
================================================================================
```

---

## 5. Defects & Findings

- **Functional Backend Defects**: **NONE**. The judge, store, timer, LLM fallback, and test suite are completely functioning as specified.
- **Problem Bank Divergence**: 7 of 12 problems exhibit minor typing annotation divergence between markdown text in `statement_md` and Python code in `starter_code`. This confirms the target problem list for UI normalization in Addendum V2 (R1).

