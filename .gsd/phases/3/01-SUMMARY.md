---
phase: 3
plan: "01"
wave: 1
status: complete
---

# Plan 3.1 Summary: FSRS Core Engine, Storage & Migration

## Objective
Implement Workstream 1a: the core FSRS engine, SQLite card storage schema, deterministic judge metadata-to-rating mapper with an explicit `Easy` ban, the `py-fsrs` default scheduler wrapper, and an idempotent migration function seeding cards from historical attempts using the last-attempt timestamp (Milo audit correction A1).

## Tasks Completed
1. **Task 1.1: FSRS Storage Schema & py-fsrs Scheduler Wrapper**
   - Created `coach/fsrs_engine.py` wrapping `fsrs.Scheduler(desired_retention=0.9)` with default parameters.
   - Verified that the FSRS optimizer is strictly absent via `git grep -i optimizer`.
   - Created `problem_fsrs_cards` table in SQLite (`coach/store.py`).
   - Implemented card serialization helpers (`card_to_json`, `card_from_json`).
2. **Task 1.2: Deterministic Judge-to-Rating Mapper & Explicit Easy Ban**
   - Implemented `map_judge_to_rating(verdict, hints_used, attempts_on_problem)` in `coach/fsrs_engine.py`:
     - `FAIL/TIMEOUT/ERROR` -> `Rating.Again` (1)
     - `PASS` + (hints>0 or attempts>1) -> `Rating.Hard` (2)
     - Clean first-attempt `PASS` -> `Rating.Good` (3)
     - Explicit ban raising `ValueError` if `Rating.Easy` is emitted.
   - Created comprehensive unit tests in `tests/test_fsrs_core.py` covering all outcome combinations and asserting `Rating.Easy` is never returned.
3. **Task 1.3: History-Seeded Idempotent Migration with A1 Last-Attempt Timestamp**
   - Implemented `CoachStore.migrate_history_to_fsrs()`:
     - Seeds an `fsrs.Card()` per problem with historical attempts.
     - Reviews card strictly at the problem's last attempt timestamp (`attempts.created_at`) per Milo audit correction A1.
     - Idempotent: skipping already-migrated cards.
     - Invariant assertion: `attempts` table count before == count after (100% untouched).
   - Created `tests/test_fsrs_migration.py` verifying A1 timestamp derivation and idempotency on an isolated SQLite database.

## Commit
- `513c7e0`: `feat(phase-3): implement FSRS core, storage schema, rating mapper, and idempotent migration`

## Verification Output
```text
tests\test_fsrs_core.py ...............                                  [ 31%]
tests\test_fsrs_migration.py .                                           [ 34%]
tests\test_judge.py ........                                             [ 51%]
tests\test_llm_fallback.py ....                                          [ 59%]
tests\test_mock_session_scoping.py .....                                 [ 70%]
tests\test_problems.py .....                                             [ 80%]
tests\test_store.py ....                                                 [ 89%]
tests\test_timer.py .....                                                [100%]

============================= 47 passed in 28.61s =============================
```

## Next Step
Proceed to Wave 2: Plan 3.2 (`02-PLAN.md`) — Scheduling Integration, Ladder Retirement & Truth-in-Copy.

