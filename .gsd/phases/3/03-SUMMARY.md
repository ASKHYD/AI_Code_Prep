---
phase: 3
plan: "03"
wave: 3
status: complete
---

# Plan 3.3 Summary: Cognitive Interleaving Queue & Invariants

## Objective
Implement Workstream 2: cognitive topic interleaving for app-generated problem queues (Home daily review queue and mock interview selection) ensuring no two problems of the same topic appear consecutively when alternatives exist, while preserving unrestricted free picking in the Practice Arena.

## Tasks Completed
1. **Task 3.1: Interleaved Review Queue Generator**
   - Implemented `build_interleaved_queue(problems, topic_stats)` in `coach/interleaving.py`:
     - Groups problems by topic.
     - Sequences problems such that `queue[i]["topic"] != queue[i-1]["topic"]` whenever alternatives exist.
     - Prioritizes higher due counts and lowest pass rates (weakest topic first).
   - Wired into `app.py`:
     - Home Daily Practice Queue (`interleaved_problems = build_interleaved_queue(...)`).
     - Mock Interview simulation problem selection (`mock_pool = build_interleaved_queue(...)`).
   - Authored `tests/test_interleaving.py` validating adjacency elimination and weakness prioritization.
2. **Task 3.2: Free Picking Invariant & First-Exposure Roadmap Branch**
   - Audited Practice Arena picker path in `app.py`: confirmed `render_practice_arena` manual selectbox and `←`/`→` buttons remain completely unrestricted.
   - Implemented `is_first_exposure(topic, attempted_topics)` in `coach/interleaving.py` to allow brand-new topics to be introduced in roadmap order.
   - Authored `tests/test_interleaving_invariants.py` verifying free-picking options and roadmap first-exposure logic.

## Commit
- `179f849`: `feat(phase-3): implement cognitive interleaving queue and preserve free picking`

## Deviations
None.

## Verification Output
```text
tests\test_fsrs_core.py ...............                                  [ 26%]
tests\test_fsrs_migration.py .                                           [ 28%]
tests\test_interleaving.py ....                                          [ 35%]
tests\test_interleaving_invariants.py ..                                 [ 39%]
tests\test_judge.py ........                                             [ 53%]
tests\test_llm_fallback.py ....                                          [ 60%]
tests\test_mock_session_scoping.py .....                                 [ 69%]
tests\test_problems.py .....                                             [ 78%]
tests\test_store.py ....                                                 [ 85%]
tests\test_streak_regression.py ...                                      [ 91%]
tests\test_timer.py .....                                                [100%]

============================= 56 passed in 29.13s =============================
```

## Next Step
Proceed to Wave 4: Plan 3.4 (`04-PLAN.md`) — Verification Suite, Dry-Run Evidence & Phase Return.

