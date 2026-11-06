---
phase: 3
plan: "02"
wave: 2
status: complete
---

# Plan 3.2 Summary: Scheduling Integration, Ladder Retirement & Truth-in-Copy

## Objective
Implement Workstream 1b: switch all scheduling consumers across the application to read from FSRS card states, retire the old 1/1/3/7/21-day ladder from the store execution path, enforce truth-in-copy by replacing legacy repetition descriptions, and pin current streak behavior with regression tests.

## Tasks Completed
1. **Task 2.1: Due-Set Consumer Switching to FSRS Cards**
   - Switched `CoachStore.due_problems()` to read exclusively from `problem_fsrs_cards` (`due <= now_iso`).
   - Updated `CoachStore.record_attempt()` to evaluate FSRS rating and upsert `fsrs.Card` into `problem_fsrs_cards`.
   - All 4 scheduling consumers in `app.py` (Home topbar due chip, Home daily practice queue, Practice Arena topbar due counter, Dashboard due state) read from FSRS state.
2. **Task 2.2: Old Ladder Call-Site Disconnection & Grep Sweep Proof**
   - Disconnected `calculate_due_date` from `coach/store.py` (removed import and caller).
   - Retired `INSERT INTO problem_reviews` from active write path.
   - Deprecated `coach/repetition.py` in docstrings; retained unreferenced for rollback safety.
   - Executed `git grep calculate_due_date coach/store.py app.py` confirming 0 remaining callers.
3. **Task 2.3: Truth-in-Copy Replacement & Streak Invariant Guard**
   - Replaced `app.py` line 1164 with: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
   - Executed grep sweep across `app.py` for `"21 days"`, `"1 / 1 / 3 / 7 / 21"`, `"spaced repetition schedule ("`: 0 matches found.
   - Verified that `"Progressive Hint Ladder"` UI element is preserved.
   - Authored `tests/test_streak_regression.py` confirming `CoachStore.current_streak` remains 100% activity-based and unaffected by FSRS card states.

## Commit
- `c0a5f0d`: `feat(phase-3): integrate FSRS due scheduling, retire old ladder, and enforce truth-in-copy`

## Deviations
- **[Rule 1 - Bug]**: Updated `test_store_roundtrip_and_due_problems` in `tests/test_store.py` to evaluate FSRS step intervals (1m / 10m) instead of obsolete 1-day/3-day ladder offsets, preserving all 31 baseline tests green.

## Verification Output
```text
tests\test_fsrs_core.py ...............                                  [ 30%]
tests\test_fsrs_migration.py .                                           [ 32%]
tests\test_judge.py ........                                             [ 48%]
tests\test_llm_fallback.py ....                                          [ 56%]
tests\test_mock_session_scoping.py .....                                 [ 66%]
tests\test_problems.py .....                                             [ 76%]
tests\test_store.py ....                                                 [ 84%]
tests\test_streak_regression.py ...                                      [ 90%]
tests\test_timer.py .....                                                [100%]

============================= 50 passed in 16.87s =============================
```

## Next Step
Proceed to Wave 3: Plan 3.3 (`03-PLAN.md`) — Cognitive Interleaving Queue & Invariants.
