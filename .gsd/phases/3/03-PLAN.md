---
phase: 3
plan: "03"
wave: 3
depends_on: ["02"]
---

# Plan 3.3: Cognitive Interleaving Queue & Invariants

## Objective
Implement Workstream 2: cognitive topic interleaving for app-generated problem queues (Home daily review queue and mock interview selection) ensuring no two problems of the same topic appear consecutively when alternatives exist, while preserving unrestricted free picking in the Practice Arena.

## Context
- `coach/interleaving.py` (new module)
- `coach/store.py`
- `app.py`
- `tests/test_interleaving.py` (new test module)

## Execution Gate
> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**

---

## Tasks

<task type="auto">
  <name>Task 3.1: Interleaved Review Queue Generator</name>
  <files>coach/interleaving.py, coach/store.py, app.py</files>
  <action>
    <!-- Skill bindings: /agency-senior-developer, /agency-test-automation-engineer -->
    1. In `coach/interleaving.py`, implement `build_interleaved_queue(due_problems: list[dict], topic_stats: dict[str, dict], problem_metadata: dict[str, dict]) -> list[dict]`:
       - Group due problems by topic.
       - Rank topics: Primary key = due-ness (count of overdue problems / days overdue), Secondary key = lowest pass rate from `topic_stats` (weakest topic prioritized).
       - Interleaving algorithm: Sequentially select problems from ranked topic buckets such that `queue[i]["topic"] != queue[i-1]["topic"]` whenever any candidate from a differing topic remains available.
       - If only problems of a single topic remain, append remaining items at the tail of the queue.
    2. Wire `build_interleaved_queue` to app-generated queues:
       - Home Daily Review Queue (`home_due_section` in `app.py`).
       - Mock Interview problem selector (`start_mock_session` in `coach/store.py` or `app.py`).
    3. Invoke `/agency-test-automation-engineer` to write tests in `tests/test_interleaving.py`:
       - Provide multi-topic fixtures with identical topics (e.g. 3 Arrays, 3 Trees, 2 Strings).
       - Assert that `queue[i]["topic"] != queue[i-1]["topic"]` holds for all positions where alternatives existed.
       - Verify that weakest topic problems are scheduled ahead of stronger topic problems within the interleaving constraints.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/test_interleaving.py</verify>
  <done>Interleaving algorithm sequences multi-topic due problems with 0 consecutive same-topic adjacencies (when alternatives exist) and prioritizes weaker topics.</done>
</task>

<task type="auto">
  <name>Task 3.2: Free Picking Invariant & First-Exposure Roadmap Branch</name>
  <files>app.py, tests/test_interleaving_invariants.py</files>
  <action>
    <!-- Skill bindings: /agency-senior-developer, /agency-minimal-change-engineer -->
    1. Audit the Practice Arena problem picker code path in `app.py` (`render_practice_arena` lines 1320–1360):
       - Confirm that the manual picker (`st.selectbox` and `←`/`→` prev/next navigation buttons) is completely UNTOUCHED by the interleaving queue.
       - Candidates retain 100% freedom to select any problem in any order across all tracks, difficulties, and topics.
       - State this invariant in code comments and automated assertions.
    2. Document and implement the first-exposure branch:
       - When a candidate encounters a topic for the very first time (zero previous attempts recorded in `attempts`), problems may follow the natural roadmap/problem bank order (`data/problems/*.json` sequence).
       - Interleaving applies strictly to review/consolidation (problems with existing attempts or active FSRS cards).
       - Locate this branch in `coach/interleaving.py` under `is_first_exposure()`.
    3. Author `tests/test_interleaving_invariants.py` to assert that free-picking functions remain independent of interleaving queues and that first-exposure topics preserve roadmap order.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/test_interleaving_invariants.py</verify>
  <done>Free picking is proven unrestricted; first-exposure roadmap branch is documented and verified.</done>
</task>

---

## Success Criteria
- [ ] Interleaved queue generator eliminates consecutive same-topic problems when alternatives exist.
- [ ] Topic ranking weights overdue count and lowest pass rate.
- [ ] Practice Arena free picker remains 100% unrestricted.
- [ ] First-exposure topics preserve roadmap ordering for initial learning.

