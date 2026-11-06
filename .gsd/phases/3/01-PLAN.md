---
phase: 3
plan: "01"
wave: 1
depends_on: ["00"]
---

# Plan 3.1: FSRS Core Engine, Storage & Migration

## Objective
Implement Workstream 1a: the core FSRS engine, SQLite card storage schema, deterministic judge metadata-to-rating mapper with an explicit `Easy` ban, the `py-fsrs` default scheduler wrapper, and an idempotent migration function seeding cards from historical attempts using the last-attempt timestamp (Milo audit correction A1).

## Context
- `.gsd/SPEC.md`
- `coach/store.py`
- `coach/fsrs_engine.py` (new module)
- `tests/test_fsrs_core.py` (new test module)

## Execution Gate
> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**

---

## Tasks

<task type="auto">
  <name>Task 1.1: FSRS Storage Schema & py-fsrs Scheduler Wrapper</name>
  <files>coach/fsrs_engine.py, coach/store.py</files>
  <action>
    <!-- Skill bindings: /agency-senior-developer, /agency-test-automation-engineer -->
    1. Invoke `/agency-senior-developer` to create `coach/fsrs_engine.py` wrapping `py-fsrs`:
       - Instantiate `fsrs.FSRS` using DEFAULT parameters only, setting `desired_retention = 0.9`.
       - Enforce that the FSRS optimizer (`fsrs.optimizer` or parameter training) is STRICTLY FORBIDDEN.
       - Provide serialization/deserialization helpers between `fsrs.Card` and JSON string storage.
    2. In `coach/store.py`, define and initialize the `problem_fsrs_cards` table in SQLite:
       - Columns: `problem_id TEXT PRIMARY KEY, card_json TEXT NOT NULL, due TEXT NOT NULL, state INTEGER NOT NULL, last_review TEXT, updated_at TEXT`.
       - Guarantee that the `attempts` table is NEVER mutated by FSRS schema initialization or card updates (immutable audit log).
    3. Invoke `/agency-test-automation-engineer` to write unit tests confirming `py-fsrs` wrapper initialization, default parameter invariants, and absence of optimizer symbols.
  </action>
  <verify>.venv\Scripts\python.exe -c "from coach.fsrs_engine import get_fsrs_scheduler; s = get_fsrs_scheduler(); assert s.p.request_retention == 0.9; print('Scheduler OK')"</verify>
  <done>`coach/fsrs_engine.py` wraps `FSRS` with retention 0.9, `problem_fsrs_cards` table is created in SQLite, and optimizer imports are absent.</done>
</task>

<task type="auto">
  <name>Task 1.2: Deterministic Judge-to-Rating Mapper & Explicit Easy Ban</name>
  <files>coach/fsrs_engine.py, tests/test_fsrs_core.py</files>
  <action>
    <!-- Skill bindings: /agency-senior-developer, /agency-test-automation-engineer -->
    1. In `coach/fsrs_engine.py`, implement the pure function `map_judge_to_rating(verdict: str, hints_used: int, attempts_on_problem: int) -> fsrs.Rating`:
       - `verdict.lower() in ("fail", "timeout", "error")` $\rightarrow$ `fsrs.Rating.Again` (1)
       - `verdict.lower() == "pass"` AND (`hints_used > 0` OR `attempts_on_problem > 1`) $\rightarrow$ `fsrs.Rating.Hard` (2)
       - `verdict.lower() == "pass"` AND `hints_used == 0` AND `attempts_on_problem == 1` $\rightarrow$ `fsrs.Rating.Good` (3)
       - `fsrs.Rating.Easy` (4) is FORBIDDEN and MUST NEVER be emitted under any combination of inputs.
    2. Invoke `/agency-test-automation-engineer` to author exhaustive parameterized unit tests in `tests/test_fsrs_core.py` covering:
       - Clean first-attempt pass (asserts `Rating.Good`).
       - First-attempt pass with 1 hint (asserts `Rating.Hard`).
       - Second-attempt pass with 0 hints (asserts `Rating.Hard`).
       - Pass with both hints and multiple attempts (asserts `Rating.Hard`).
       - Failures, timeouts, and errors (asserts `Rating.Again`).
       - Explicit assertion checking that no test or input combination emits `Rating.Easy`.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/test_fsrs_core.py -k "test_map_judge_to_rating"</verify>
  <done>All rating mapping rules are implemented as a pure function; unit tests verify all outcome branches and confirm `Rating.Easy` is never emitted.</done>
</task>

<task type="auto">
  <name>Task 1.3: History-Seeded Idempotent Migration with A1 Last-Attempt Timestamp</name>
  <files>coach/store.py, tests/test_fsrs_migration.py</files>
  <action>
    <!-- Skill bindings: /agency-senior-developer, /empirical-validation, /agency-test-automation-engineer -->
    1. In `coach/store.py`, implement `migrate_history_to_fsrs()`:
       - Query distinct problems present in `attempts`.
       - For each problem, fetch its most recent attempt row (`status`, `created_at`, `mode`).
       - Per Milo audit correction A1, seed a new `fsrs.Card` and record the initial review using the problem's LAST ATTEMPT TIMESTAMP (`created_at`), NOT migration time:
         - If last attempt was a pass $\rightarrow$ apply `Rating.Good` review at `created_at`.
         - If last attempt was a fail/timeout $\rightarrow$ apply `Rating.Again` review at `created_at`.
       - Store serialized card state and computed `due` timestamp into `problem_fsrs_cards`.
       - Assert that `attempts` table rows are 100% UNTOUCHED (zero insert, update, or delete).
       - Ensure idempotency: if a card already exists for `problem_id`, skip insertion unless forced. Re-running migration produces 0 changes.
    2. Write `tests/test_fsrs_migration.py`:
       - Create a temporary isolated SQLite database with sample attempts.
       - Run migration, verify card creation, verify due timestamp is derived from `last_attempt_date` (A1).
       - Run migration a second time, assert row count and card JSONs are identical (idempotency).
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/test_fsrs_migration.py</verify>
  <done>Migration seeds cards from historical attempts, derives due dates from last attempt timestamps (A1), is 100% idempotent, and leaves `attempts` untouched.</done>
</task>

---

## Success Criteria
- [ ] `problem_fsrs_cards` table is created in SQLite with zero modifications to `attempts`.
- [ ] Rating mapper implements all 3 rules; `Rating.Easy` is strictly banned.
- [ ] `py-fsrs` wrapper uses default parameters with `desired_retention = 0.9`; optimizer is completely absent.
- [ ] Migration accurately backfills cards from last attempt timestamps (A1) and is verified idempotent.

