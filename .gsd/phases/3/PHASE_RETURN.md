# Phase 3 Return: FSRS + Interleaving

**Milestone**: Milestone 2: Make the Loop Smarter  
**Phase**: Phase 3: FSRS + Interleaving  
**Date**: 2026-11-07  
**Status**: Execution & Verification Complete — Awaiting Owner Live Acceptance  
**Source Contract**: Block M2 (`MILESTONE-2-DISCUSS-BLOCK.md`) & Block P3 (`PLAN_CONTRACT.md`)  

---

## 1. Executive Summary

Milestone 2 Phase 3 replaces the deterministic 1/1/3/7/21-day spaced repetition ladder with modern adaptive memory modeling via `py-fsrs` and introduces cognitive topic interleaving for all system-generated problem queues.

Both workstreams have been fully executed across 5 atomic waves with zero regressions on the frozen problem bank and judge execution logic:
- **Workstream 1 (FSRS Scheduler Swap)**: Pinned `fsrs==6.3.2`, implemented SQLite card storage (`problem_fsrs_cards`), established the 3-rule judge rating mapper with a strict `Rating.Easy` ban, wrapped py-fsrs defaults with `desired_retention = 0.9` (optimizer forbidden), implemented history-seeded idempotent migration with A1 last-attempt timestamps, disconnected the old ladder from the store write path (0 callers), updated Home UI copy to truthfully describe FSRS, and pinned activity-based streak calculation.
- **Workstream 2 (Cognitive Interleaving)**: Implemented non-adjacent topic sequencing (`topic[i] != topic[i-1]`) weighted by due count and weakest topic pass rate for Home Daily Practice and Mock Interview simulation queues, while leaving manual free picking in the Practice Arena 100% unrestricted.
- **Verification Suite**: 57 tests passing in 17.22s (31 baseline tests + 26 new Phase 3 tests).
- **Visual Evidence**: Captured live 1450×900 Chrome CDP screenshot (`docs/screenshots/m2_p3_home_1450x900.png`) proving truthful FSRS copy and active FSRS due chip.

---

## 2. Workstream 1 Return — FSRS Scheduler Swap

### Dependency Gate
- Pinned in `requirements.txt`: `fsrs==6.3.2`.
- Offline execution confirmed: `fsrs.Card`, `fsrs.Rating`, `fsrs.Scheduler` operate entirely in-process without network calls.

### Storage Schema
- Created `problem_fsrs_cards` table in SQLite (`coach/store.py`):
  ```sql
  CREATE TABLE IF NOT EXISTS problem_fsrs_cards (
      problem_id TEXT PRIMARY KEY,
      card_json TEXT NOT NULL,
      due TEXT NOT NULL,
      state INTEGER NOT NULL,
      last_review TEXT,
      updated_at TEXT NOT NULL
  )
  ```
- **Invariant**: The `attempts` table is the immutable history of record and was never modified by FSRS initialization or card updates.

### Judge-to-Rating Mapping (Binding)
Implemented as a pure function in `coach/fsrs_engine.py`:
- `FAIL`, `TIMEOUT`, `ERROR` $\rightarrow$ `Rating.Again` (1)
- `PASS` with `hints_used > 0` OR `attempts_on_problem > 1` $\rightarrow$ `Rating.Hard` (2)
- Clean first-attempt `PASS` with 0 hints $\rightarrow$ `Rating.Good` (3)
- `Rating.Easy` (4) is **STRICTLY BANNED** and raises `ValueError` if emitted. Verified exhaustively across all permutations in `tests/test_fsrs_core.py`.

### Scheduler Configuration
- Initialized via `fsrs.Scheduler(desired_retention=0.9)` with default parameters.
- **Optimizer Ban Proof**: `git grep -i optimizer coach/ tests/` returned 0 matches, confirming complete absence of optimizer modules or training code.

### History-Seeded Idempotent Migration (Milo Audit Correction A1)
- Implemented `CoachStore.migrate_history_to_fsrs()`:
  - For each problem with attempt history, fetches the most recent attempt (`created_at`, `status`).
  - **A1 Timestamp**: Seeds `fsrs.Card()` and applies the initial review using the problem's **last attempt timestamp** (`created_at`), NOT migration time.
  - If last attempt passed $\rightarrow$ reviewed with `Rating.Good` at `created_at`.
  - If last attempt failed/timed-out $\rightarrow$ reviewed with `Rating.Again` at `created_at`.
  - Idempotent: Skips already-seeded cards. Re-running migration produces 0 changes.
  - Shipped code path: Wired into `get_store()` startup in `app.py`.

### Old Ladder Removal & Grep Proof
- Call-site dispositions:
  - `coach/store.py`: Removed import of `calculate_due_date` and call in `record_attempt()`.
  - `coach/repetition.py`: Marked DEPRECATED in docstrings; retained unreferenced for rollback safety.
  - `git grep calculate_due_date coach/store.py app.py`: 0 matches found (exit code 1).
- Scheduling consumers: `CoachStore.due_problems()` reads exclusively from `problem_fsrs_cards` (`due <= now_iso`).

### Truth-in-Copy
- Replaced `app.py` line 1164 with:
  `Adaptive spaced repetition (FSRS) scheduled from your objective test results.`
- Grep sweep across `app.py` for `"21 days"`, `"1 / 1 / 3 / 7 / 21"`, `"spaced repetition schedule ("`: 0 matches.
- Verified `"Progressive Hint Ladder"` UI element is preserved.

### Streak Invariant Guard
- `CoachStore.current_streak()` behavior remains 100% activity-based. Verified in `tests/test_streak_regression.py`.

---

## 3. Workstream 2 Return — Cognitive Interleaving

### Queue Generator
- Implemented `build_interleaved_queue()` in `coach/interleaving.py`:
  - Groups candidate problems into topic buckets.
  - Sequences problems such that `queue[i]["topic"] != queue[i-1]["topic"]` whenever alternatives exist.
  - Prioritizes topics with higher problem counts and lowest pass rates (`topic_stats`).
  - Single remaining topic problems gracefully fall back to the tail.

### Integration
- **Home Screen**: Daily Practice Queue card sequences problems via `build_interleaved_queue(all_problems, topic_stats=store.topic_stats())`.
- **Mock Interview**: Two-problem simulation selection uses `build_interleaved_queue()`, guaranteeing the candidate receives problems from two different topics.

### Invariants
- **Free Picking Intact**: The manual Problem Picker in the Practice Arena (`render_practice_arena` `st.selectbox` and `←`/`→` buttons) remains 100% unrestricted. Candidates can select any problem in any order.
- **First Exposure**: Brand-new unattempted topics are detected via `is_first_exposure()` to allow initial topic exploration in roadmap curriculum order.

---

## 4. Verification Battery & Test Evidence

Ran `.venv\Scripts\pytest.exe -o pythonpath=. tests/`:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: E:\resume_project
plugins: anyio-4.16.0
collected 57 items

tests\test_fsrs_core.py ...............                                  [ 26%]
tests\test_fsrs_equivalence.py .                                         [ 28%]
tests\test_fsrs_migration.py .                                           [ 29%]
tests\test_interleaving.py ....                                          [ 36%]
tests\test_interleaving_invariants.py ..                                 [ 40%]
tests\test_judge.py ........                                             [ 54%]
tests\test_llm_fallback.py ....                                          [ 61%]
tests\test_mock_session_scoping.py .....                                 [ 70%]
tests\test_problems.py .....                                             [ 78%]
tests\test_store.py ....                                                 [ 85%]
tests\test_streak_regression.py ...                                      [ 91%]
tests\test_timer.py .....                                                [100%]

============================= 57 passed in 17.22s =============================
```

### Coverage by Required Category
1. **Category 1 (Rating Mapper Matrix)**: `tests/test_fsrs_core.py` (15 tests) verifying all outcome branches and `Rating.Easy` ban.
2. **Category 2 (Migration & A1 Timestamp)**: `tests/test_fsrs_migration.py` verifying card due derivation from `attempts.created_at` and 100% idempotency.
3. **Category 3 (Due-Set Equivalence)**: `tests/test_fsrs_equivalence.py` comparing legacy ladder vs FSRS due schedules, confirming 0 silent losses and accounting for FSRS learning steps vs flat calendar jumps.
4. **Category 4 (Interleaving Adjacency)**: `tests/test_interleaving.py` and `tests/test_interleaving_invariants.py` (6 tests) verifying topic alternation and free-picking independence.
5. **Category 5 (Streak Invariant)**: `tests/test_streak_regression.py` (3 tests) verifying continuous streaks, gap resets, and same-day deduplication.

---

## 5. Live Browser Capture & DOM Evidence

- **Screenshot File**: `docs/screenshots/m2_p3_home_1450x900.png` (126,304 bytes).
- **Viewport**: 1450 × 900 (primary owner testing viewport).
- **Live CDP DOM Measurements**:
  - `FSRS Truth-in-Copy verified in DOM`: `True` (`"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`)
  - `Due chip text`: `"1 due"` (reflecting migrated card state).

---

## 6. Resources Exercised Accounting Block

| Skill | Status | Technical Rationale / Evidence |
| :--- | :--- | :--- |
| `/empirical-validation` | **USED** | Wave 0 baseline verification, pip installation verification, and copy database migration proofs. |
| `/agency-senior-developer` | **USED** | Implementation of `coach/fsrs_engine.py` (FSRS wrapper, rating mapper) and `coach/interleaving.py` (interleaving queue generator). |
| `/agency-test-automation-engineer` | **USED** | Authoring 26 new tests across 5 test files (`test_fsrs_core.py`, `test_fsrs_migration.py`, `test_fsrs_equivalence.py`, `test_interleaving.py`, `test_streak_regression.py`). |
| `/agency-minimal-change-engineer` | **USED** | Surgical UI integration in `app.py` (due-set consumption, truth-in-copy line 1164 swap, preserving free picking). |
| `/agency-evidence-collector` | **USED** | Live Chrome CDP automated capture at 1450×900 with DOM element verification. |
| `/impeccable` | **PARKED** | Direction A UI design is strictly frozen for Phase 3; only one sentence of text changed. |
| `/ui-ux-pro-max` | **PARKED** | Direction A UI design is strictly frozen for Phase 3; no new components or styles created. |
| `/ui-styling` | **PARKED** | CSS tokens and layout strictly frozen. |
| `/design-system` | **PARKED** | Design tokens strictly frozen. |
| `/design` | **PARKED** | Brand identity and visual tokens strictly frozen. |
| `/brand` | **PARKED** | Visual assets strictly frozen. |
| `/agency-frontend-developer` | **PARKED** | No frontend components built; `app.py` modifications were purely logic wiring. |
| `/speckit-*` | **PARKED** | GSD is the planning and execution system of record. |
| `/teamwork` | **PARKED** | Parked per standing owner rule. |

---

## 7. Internal Verification (`/verify 3`)

Internal verification of Phase 3 must-haves:
- `fsrs==6.3.2` installed and pinned: **PASS**
- Card-per-problem JSON SQLite storage: **PASS**
- Attempts table immutable audit log: **PASS**
- Rating mapper 3 rules + `Easy` ban: **PASS**
- py-fsrs defaults + retention 0.9 + optimizer absent: **PASS**
- 4 due-set consumers read FSRS state: **PASS**
- Idempotent migration with A1 last-attempt timestamp: **PASS**
- Old ladder disconnected from scheduling path (0 callers): **PASS**
- Truth-in-copy line on Home + 0 ladder matches: **PASS**
- Activity-based streak regression: **PASS**
- Interleaving queue eliminates adjacent same topics: **PASS**
- Free picking in Practice Arena unrestricted: **PASS**
- All 57 tests passing: **PASS**
- Live 1450×900 browser capture verified: **PASS**

> `/verify 3` Verdict: **PASS — 14/14 Must-Haves Satisfied with Empirical Proofs.**

---

Stopped at Milestone 2 Phase 3 gate, awaiting owner live approval.
