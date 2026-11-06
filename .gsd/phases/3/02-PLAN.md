---
phase: 3
plan: "02"
wave: 2
depends_on: ["01"]
---

# Plan 3.2: Scheduling Integration, Ladder Retirement & Truth-in-Copy

## Objective
Implement Workstream 1b: switch all scheduling consumers across the application to read from FSRS card states, retire the old 1/1/3/7/21-day ladder from the store execution path, enforce truth-in-copy by replacing legacy repetition descriptions, and pin current streak behavior with regression tests.

## Context
- `coach/store.py`
- `coach/repetition.py`
- `app.py`
- `tests/test_store.py`
- `tests/test_streak_regression.py` (new test module)

## Execution Gate
> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**

---

## Tasks

<task type="auto">
  <name>Task 2.1: Due-Set Consumer Switching to FSRS Cards</name>
  <files>coach/store.py, app.py</files>
  <action>
    <!-- Skill binding: /agency-minimal-change-engineer -->
    1. In `coach/store.py`, update `CoachStore.due_problems(today=...)` to query `problem_fsrs_cards`:
       - A problem is due when its card's due ISO timestamp $\le$ target timestamp (`now`).
       - Query returns problems sorted by urgency (`due ASC`).
       - Ensure backward-compatible dictionary keys (`problem_id`, `next_due_date`, `last_status`) so calling code in `app.py` transitions smoothly.
    2. In `coach/store.py`, update `record_attempt()` to update the problem's FSRS card upon submission:
       - Compute `rating = map_judge_to_rating(status, hints_used, attempts_on_problem)`.
       - Execute `fsrs.review_card(card, rating, review_time)`.
       - Persist updated `card_json`, `due`, `state`, and `last_review` into `problem_fsrs_cards`.
    3. Verify that all 4 scheduling consumers in `app.py` read the new FSRS state:
       - Home topbar due chip & counter (`render_topbar("Home", streak_count, len(due_list))`).
       - Home daily practice queue container (`home_due_section`).
       - Practice Arena topbar due counter.
       - Dashboard due status & metrics.
  </action>
  <verify>.venv\Scripts\python.exe -c "from coach.store import CoachStore; s = CoachStore(); print('Due query OK:', len(s.due_problems()))"</verify>
  <done>`CoachStore.due_problems()` and `record_attempt()` operate exclusively via `problem_fsrs_cards`; Home, Practice, Mock, and Dashboard reflect FSRS due states.</done>
</task>

<task type="auto">
  <name>Task 2.2: Old Ladder Call-Site Disconnection & Grep Sweep Proof</name>
  <files>coach/store.py, coach/repetition.py</files>
  <action>
    <!-- Skill bindings: /agency-minimal-change-engineer, /empirical-validation -->
    1. Account for all call sites of `coach/repetition.py`:
       - Site 1: `coach/store.py:12` (`from coach.repetition import calculate_due_date`) $\rightarrow$ DISCONNECT. Remove import.
       - Site 2: `coach/store.py:75` (`calculate_due_date(...)`) $\rightarrow$ DISCONNECT. Replaced by FSRS card review.
       - Site 3: `coach/store.py:90` (`INSERT INTO problem_reviews`) $\rightarrow$ RETIRE from active write path.
       - Site 4: `tests/test_store.py:2` (`from coach.repetition import calculate_next_due`) $\rightarrow$ Retain in test suite as legacy contract reference.
    2. Function Disposition:
       - `coach/repetition.py` is marked DEPRECATED in its docstring but retained in the codebase unreferenced by runtime code. Reason: preserves git commit clarity, provides instant fallback reference, and keeps existing isolated unit tests functional without breaking backward compatibility.
    3. Execute grep sweep to prove that zero active scheduling callers to `calculate_due_date` exist in `coach/store.py` or `app.py`.
  </action>
  <verify>.venv\Scripts\python.exe -c "import subprocess; res = subprocess.run(['git', 'grep', 'calculate_due_date', 'coach/store.py', 'app.py'], capture_output=True, text=True); assert res.stdout.strip() == '', f'Callers remain: {res.stdout}'; print('Grep proof OK: 0 callers')"</verify>
  <done>Zero runtime callers of `calculate_due_date` exist in `coach/store.py` or `app.py`; grep proof confirms disconnection.</done>
</task>

<task type="auto">
  <name>Task 2.3: Truth-in-Copy Replacement & Streak Invariant Guard</name>
  <files>app.py, tests/test_streak_regression.py</files>
  <action>
    <!-- Skill bindings: /agency-minimal-change-engineer, /agency-test-automation-engineer -->
    1. In `app.py` at line 1164, replace:
       `Interview-targeted spaced repetition schedule (1 / 1 / 3 / 7 / 21 days) based strictly on objective test results.`
       with:
       `Adaptive spaced repetition (FSRS) scheduled from your objective test results.`
    2. Perform a sweep across `app.py` for ladder phrasing:
       - `"21 days"`: verify 0 occurrences remaining.
       - `"1 / 1 / 3 / 7 / 21"`: verify 0 occurrences remaining.
       - `"spaced repetition schedule ("`: verify 0 occurrences remaining.
       - Note: `"Progressive Hint Ladder"` occurrences (lines 463, 1427, 1926) are strictly visual hint disclosures, NOT spaced repetition, and are intentionally preserved.
    3. Invoke `/agency-test-automation-engineer` to author `tests/test_streak_regression.py`:
       - Verify that `CoachStore.current_streak()` behavior is 100% activity-based and unaffected by FSRS card swaps.
       - Assert streak calculation matches existing logic across multi-day attempt fixtures.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/test_streak_regression.py</verify>
  <done>UI copy truthfully describes FSRS without ladder phrasing; streak regression test confirms activity-based streak calculation is unchanged.</done>
</task>

---

## Success Criteria
- [ ] All 4 scheduling consumers read from `problem_fsrs_cards`.
- [ ] `calculate_due_date` has 0 callers in `coach/store.py` and `app.py`.
- [ ] `app.py` copy updated to describe FSRS; 0 ladder phrasing matches found.
- [ ] Streak calculation behavior pinned and passing in regression tests.
