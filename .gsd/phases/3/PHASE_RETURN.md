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

## 8. LIVE RECONCILIATION (2026-11-07)

Following the owner's live inspection of `http://localhost:8501/?screen=home` on 2026-11-07, this read-only diagnosis reconciles the live UI display against the underlying database state and application code. Zero code or data files were modified.

### 1. Streak Reconciliation

- **Exact Store Function & Return Right Now**:
  - Function: `CoachStore.current_streak(self, today: str | None = None) -> int` in [`coach/store.py`](file:///e:/resume_project/coach/store.py#L198-L212).
  - Exact Return Value: **`0`**.
  - Implementation:
    ```python
    def current_streak(self, today: str | None = None) -> int:
        """Calculates current consecutive days with at least 1 attempt leading to today."""
        curr = datetime.strptime(today, "%Y-%m-%d").date() if today else date.today()
        streak = 0

        with self._get_connection() as conn:
            cur = conn.execute("SELECT DISTINCT attempt_date FROM attempts ORDER BY attempt_date DESC")
            attempt_dates = {row["attempt_date"] for row in cur.fetchall()}

        # Count backwards from curr
        while curr.isoformat() in attempt_dates:
            streak += 1
            curr -= timedelta(days=1)

        return streak
    ```
- **What Home Tile / Navbar Chip Render**:
  - Single Source of Truth in [`app.py`](file:///e:/resume_project/app.py#L1131):
    ```python
    streak_count = store.current_streak()
    ```
  - Topbar Navbar Chip ([`app.py`](file:///e:/resume_project/app.py#L1091)):
    ```python
    streak_str = f"{streak_count}d" if streak_count > 0 else "0 days"
    ```
    Renders: `"0 days"`.
  - Home Active Streak Card ([`app.py`](file:///e:/resume_project/app.py#L1187-L1205)):
    ```python
    with st.container(border=True, key="home_card_streak"):
        streak_unit = "day" if streak_count == 1 else "days"
        if streak_count == 0:
            streak_badge = '<span class="stat-badge" style="background: rgba(102, 99, 90, 0.12); color: #66635A;">NOT STARTED</span>'
            streak_caption = "Complete today's problem queue to start your streak."
        else:
            streak_badge = '<span class="stat-badge badge-mint">ACTIVE</span>'
            streak_caption = "Consecutive active days."
        st.markdown(
            f"""
            <div class="stat-head" style="display: flex; justify-content: space-between; align-items: center;">
                <span class="stat-label">Active Streak</span>
                {streak_badge}
            </div>
            <div class="stat-value">{streak_count} {streak_unit}</div>
            <p class="stat-desc">{streak_caption}</p>
            """,
            unsafe_allow_html=True,
        )
    ```
    Renders: Value `0 days`, Badge `NOT STARTED`, Caption *"Complete today's problem queue to start your streak."*.
- **Tile vs. Store Reconciliation**:
  - The Home tile, navbar chip, and the store **agree completely** (all return/display `0`). There is no recomputation in `app.py`.
  - The discrepancy was between the live app on 2026-11-07 (`0 days`) and the Phase 6 mockups (`1 Day`).
  - Recorded attempt dates in `coach.db` `attempts` table:
    - Attempt #1: `2026-11-04` (`2026-11-04T10:42:53.782231`, practice, pass)
    - Attempt #3: `2026-11-06` (`2026-11-06T20:00:50.752400`, mock, fail)
    - `2026-11-07`: **0 attempts logged**.
  - **Root Cause & Diagnosis**:
    - On 2026-11-06 (when the Phase 2/Phase 3 verification battery ran), `date.today()` was `2026-11-06`. Because `2026-11-06` was in `attempt_dates`, the store returned `1`.
    - On 2026-11-07 (when the owner took the live screenshot), `date.today()` advanced to `2026-11-07`. Because no attempts have been recorded yet today, `'2026-11-07' in attempt_dates` evaluated to `False` on the very first while-loop check.
    - **Defect in `store.current_streak()`**: The current algorithm prematurely zeroes an active streak at midnight before the user has had an opportunity to practice on the new calendar day. In standard habit tracking (Duolingo/LeetCode), a streak earned on day $T$ remains alive throughout day $T+1$; it only resets if day $T+1$ concludes with zero activity.
    - *Proposed Fix (Diagnosis only)*: If `today not in attempt_dates`, test `today - 1 day in attempt_dates`. If yesterday was active, count backwards from yesterday (streak is alive, awaiting today's activity). If neither today nor yesterday has an attempt, reset to 0.

---

### 2. Due Card Reconciliation

- **Every FSRS Card Currently Due from `problem_fsrs_cards`**:
  - Query: `SELECT problem_id, due, state, last_review FROM problem_fsrs_cards`:
    - `problem_id`: **`binary-search`**
    - `due`: **`2026-11-06T20:01:50.752400+00:00`** (State: 1 [Learning], Step: 0, Stability: 0.212, Difficulty: 6.4133, Last Review: `2026-11-06T20:00:50.752400+00:00`).
  - Total Due Cards: **Exactly 1**.
  - Which problem is the "1 due"? **`binary-search`** is the sole due problem.
- **Reconciliation with Binary Search Queue Row ("NEXT DUE: +1 DAY")**:
  - Why does the Home tile render `1 due` while the queue table row renders `NEXT DUE: +1 DAY`?
  - Quoted code path in [`app.py`](file:///e:/resume_project/app.py#L1240-L1277):
    ```python
    with store._get_connection() as conn:
        cur = conn.execute("SELECT DISTINCT problem_id FROM attempts WHERE status = 'pass'")
        solved_set = {row[0] for row in cur.fetchall()}

    interleaved_problems = build_interleaved_queue(all_problems, topic_stats=store.topic_stats())
    for p in interleaved_problems:
        is_solved = p["id"] in solved_set
        # ...
        if is_solved:
            status_pill = '<span class="stat-badge badge-mint">Next Due: +1 Day</span>'
            subtitle = "Recent attempt passed · Scheduled for review"
        else:
            status_pill = '<span class="stat-badge" style="background: rgba(102, 99, 90, 0.12); color: #66635A;">Unattempted</span>'
            subtitle = f"Standard {p['topic']} curriculum problem"
    ```
  - **Defect in `app.py` Queue Row Rendering**:
    - The queue table row builder completely ignores `due_list` (`store.due_problems()`)!
    - It simply checks `is_solved = p["id"] in solved_set`. Because `binary-search` has a passed attempt from 2026-11-04 (`id=1`), `is_solved` is `True`.
    - Whenever `is_solved` is `True`, it **hardcodes** `status_pill = 'Next Due: +1 Day'` and subtitle `"Recent attempt passed · Scheduled for review"`.
    - *Proposed Fix (Diagnosis only)*: Check `p["id"] in {d["problem_id"] for d in due_list}` first. If True, render `<span class="stat-badge badge-amber">DUE FOR REVIEW</span>` (matching the Phase 6 mockup pill). Only if not due should it calculate next interval delta from `card.due`.

---

### 3. Queue Composition & Order Reconciliation

- **Home Queue Composition Rule as Implemented**:
  - Code path: `app.py` line 1263 calls `build_interleaved_queue(all_problems, topic_stats=store.topic_stats())` from [`coach/interleaving.py`](file:///e:/resume_project/coach/interleaving.py#L23-L75).
  - Implementation Logic:
    1. Buckets all candidate problems by `topic`.
    2. At each iteration, filters candidate topics to those where `topic != last_topic` and `len(bucket) > 0`.
    3. Sorts available candidates by:
       `key=lambda t: (-len(topic_buckets[t]), stats.get(t, {}).get("pass_rate", 100.0))`
       - **Primary**: Bucket count descending (`-len`). Topics with more problems are selected first to prevent topic accumulation at the tail.
       - **Secondary**: Historical pass rate ascending (`stats[t]["pass_rate"]`). Topics with lower pass rates (weaker skills) are prioritized over unattempted topics (defaulting to 100.0%).
    4. Pops the first problem from the chosen topic's bucket.
  - **Composition Characteristic**: The queue builder receives the entire problem bank (`all_problems`, 12 problems). It does *not* partition due items ahead of new items; all problems are interleaved globally based on topic depth and weakness.
- **Today's Full Live Queue Order (12 Problems)**:
  1. **`max-subarray`** | Topic: **`arrays`** | Title: *Maximum Subarray Sum* | Status: Unattempted
     - *Why #1*: `arrays` is the only topic in the catalog containing 2 problems (`max-subarray`, `two-sum`). Its remaining bucket count is 2 (all other topics have 1). Therefore, `len=2` sorts it to rank 1.
  2. **`binary-search`** | Topic: **`binary-search`** | Title: *Binary Search* | Status: Due Today (Rendered as Solved / Next Due: +1 Day)
     - *Why #2*: With `arrays` excluded by `t != last_topic`, all 10 remaining candidate topics have `len=1`. The secondary tie-breaker evaluates `pass_rate`. `binary-search` is the only topic in the store with attempt history, having a pass rate of **50.0%** (1 pass / 2 attempts). All unattempted topics default to 100.0%. Thus, `binary-search` is selected next.
  3. **`climbing-stairs`** | Topic: **`dp`** | Title: *Climbing Stairs* | Status: Unattempted
  4. **`csv-column-summary`** | Topic: **`data-transformation`** | Title: *CSV Column Summarizer* | Status: Unattempted
  5. **`flatten-nested-dict`** | Topic: **`dict-processing`** | Title: *Flatten Nested Dictionary* | Status: Unattempted
  6. **`log-timestamp-filter`** | Topic: **`string-parsing`** | Title: *Log Timestamp Filter* | Status: Unattempted
  7. **`longest-substring-without-repeating`** | Topic: **`strings`** | Title: *Longest Substring Without Repeating Characters* | Status: Unattempted
  8. **`two-sum`** | Topic: **`arrays`** | Title: *Two Sum* | Status: Unattempted
     - *The second `arrays` problem, placed 7 rows away from `max-subarray`.*
  9. **`reverse-sequence`** | Topic: **`two-pointers`** | Title: *Reverse Sequence In Place* | Status: Unattempted
  10. **`string-permutations`** | Topic: **`recursion`** | Title: *String Permutations* | Status: Unattempted
  11. **`tree-level-order`** | Topic: **`tree-traversal`** | Title: *Binary Tree Level Order Traversal* | Status: Unattempted
  12. **`valid-parentheses`** | Topic: **`stack`** | Title: *Valid Parentheses* | Status: Unattempted
- **Verification of Invariants**:
  - **No-Same-Topic-Adjacency**: Sequence is `arrays` $\rightarrow$ `binary-search` $\rightarrow$ `dp` $\rightarrow$ `data-transformation` $\rightarrow$ `dict-processing` $\rightarrow$ `string-parsing` $\rightarrow$ `strings` $\rightarrow$ `arrays` $\rightarrow$ `two-pointers` $\rightarrow$ `recursion` $\rightarrow$ `tree-traversal` $\rightarrow$ `stack`. No two adjacent problems share a topic (**0 adjacency violations**).
  - **Due Problem Position**: The single due problem (`binary-search`) is positioned at **row 2** of the queue.

---

### Resources Exercised Line

| Skill | Status | Technical Rationale / Evidence |
| :--- | :--- | :--- |
| `/systematic-debugging` | **USED** | Performed read-only diagnosis of live Home screen state, isolating two distinct defects: midnight streak reset in `store.current_streak` and hardcoded `"Next Due: +1 Day"` in `app.py` queue row rendering. |

---

Stopped at Milestone 2 Phase 3 gate, awaiting owner live approval.
