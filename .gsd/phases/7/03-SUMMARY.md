# Wave 3: Practice Arena & Mock Interview Simulation Summary

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.3 (Wave 3)  
**Status**: COMPLETE  
**Commit**: `8ceab63`  

---

## 1. Work Completed

### Task 3.1: Practice Arena Slim Picker & Navigation Controls
- Rebuilt the problem picker row into the approved Round 2 label format:
  `f"{curr_idx + 1}. {current_problem['title']} · {current_problem['topic'].replace('-', ' ').title()} ({current_problem['difficulty'].title()})"`
  (e.g., `1. Binary Search · Binary Search (Easy)`).
- Enclosed the title inside a clean white pill container with 1px warm hairline (`rgba(74, 25, 66, 0.10)`) and `DM Serif Display` typography.
- Styled previous (`←`) and next (`→`) arrow buttons with `.btn-nav-arrow` (`padding: 6px 14px !important; font-size: 16px !important; font-weight: 700 !important; min-width: 44px !important; white-space: nowrap !important; border-radius: 9999px !important;`), preventing text truncation at 1450px viewport.

### Task 3.2: Problem Card Signature Block & Dark Code Editor Anchor
- Updated Problem Statement card to Terracotta tokens:
  - Title in `DM Serif Display` (`28px`, `#2C1810`).
  - Active due indicator `<span class="stat-badge badge-amber">DUE FOR REVIEW</span>` dynamically displayed when problem is due.
  - Semantic difficulty badges (`badge-olive` for Easy, `badge-amber` for Medium, `badge-terracotta` for Hard).
  - Maintained single-source-of-truth starter signature block `<span class="signature-subhead">STARTER FUNCTION SIGNATURE</span>` with `{sig_line}` extracted from `starter_code.splitlines()[0]`.
  - Replaced legacy Hint Ladder styling with Terracotta sandy quiet panel (`#E8D5B7`, border `rgba(74, 25, 66, 0.12)`, radius `16px`) and terracotta accent label.
- Preserved 24px dark code editor card (`#1E1E1E`), 450px height, with editor strip `{title} · PYTHON` and natural-width right-aligned "Run & Submit" primary button (`#C2452D`, 9999px pill).

### Task 3.3: Output Card Rebuild (F1 Invariant: No Invented Telemetry)
- Neutral unrun state: "Run your code to see results" with calm explanatory text in `DM Serif Display` and `Plus Jakarta Sans`.
- Evaluated state:
  - PASS: Olive `#6B7F3B` badge (`PASS`), headline `{title} · PASS · {runtime} ms · Hints {hints_used}`, subhead `All Tests Accepted`, and test count `{passed} / {total} Passed`.
  - FAIL: Terracotta `#C2452D` badge (`FAIL`), failed test case input/expected/got diff.
  - Visible test cases rendered authentically from problem JSON.
  - **F1 Invariant strictly enforced**: Completely omitted memory figures (`MB`) and simulated telemetry. All numbers trace directly to subprocess execution or SQLite store.

### Task 3.4: Mock Interview Cycle (Start Facts, 2-Place Timer, Scorecard)
- **Start Screen** (`mock_start.html`):
  - Headline "Coding Interview Simulation" in `DM Serif Display`.
  - Sandy format facts panel in `#E8D5B7` with 4 protocol cards: 45 Minutes Duration, 2 Interleaved Problems, Hints Allowed, Performance Report.
  - Session Timer Budget preview card showing `45:00` in `JetBrains Mono` bold.
  - Primary CTA pill "Begin Mock Interview" (`#C2452D`, 9999px pill).
  - Past sessions table styled with Terracotta `.queue-table` when mock attempts exist in store.
- **Active Session Screen** (`mock_session.html`):
  - Session navigation strip with Problem 1 & 2 switcher buttons.
  - Strict two-place countdown timer (`{mins:02d}:{secs:02d}`) in `JetBrains Mono` bold via `@st.fragment(run_every=1.0)`.
  - Two-pane workspace with problem card, hint ladder, dark editor, and execution output.
  - "End Interview Early" terminates without writing false records (zero-write unsolved end).
- **Scorecard Screen** (`mock_scorecard.html`):
  - "Interview Performance Scorecard" in `DM Serif Display`.
  - Overall verdict banner: Olive `#6B7F3B` for PASS (2/2 solved), Terracotta `#C2452D` for FAIL (<2 solved).
  - Sandy quiet summary strip (`#E8D5B7`): Time Consumed (`{mins}m {secs}s / 45m`), Problems Solved (`{score} / 2`), Hints Consulted (`{total_hints} Hint(s)`).
  - Problem breakdown cards (Outcome 01, Outcome 02) detailing title, topic, difficulty, runtime, and hints.
  - "Export Results as Markdown" and "Start New Mock Session" actions.

---

## 2. Verification & Invariants

- **Pytest Suite**: 71/71 tests passing (`tests/test_auth.py`, `tests/test_mock_session_scoping.py`, `tests/test_streak_regression.py`, `tests/test_judge.py`, etc.).
- **Database Immutability**: `coach.db` row counts strictly preserved (`attempts`: 2, `problem_fsrs_cards`: 1). Zero writes occurred during unrun or uncompleted states.
- **Brand Consistency**: Header serif wordmark reads "AI Prep Coach" across all views.
