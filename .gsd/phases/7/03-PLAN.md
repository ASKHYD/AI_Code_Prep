# Wave 3: Practice Arena & Mock Interview Simulation

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.3 (Wave 3)  
**Status**: DRAFT — READY FOR AUDIT  

---

## 1. Plan Overview

Wave 3 translates the Practice Arena and Mock Interview workflows into the Terracotta Editorial design system (`practice.html`, `mock_start.html`, `mock_session.html`, `mock_scorecard.html`):
1. Rebuilds the slim problem picker row in the owner-mandated Round 2 format: `"N. Title · Topic (Difficulty)"`, ensuring prev/next arrow buttons are padded to eliminate clipping at 1450px viewport (no X10).
2. Enforces the X6/X9 signature doctrine: renders the small-caps `STARTER FUNCTION SIGNATURE` header and derives the signature directly from `starter_code.splitlines()[0]` across all 12 problems without modifying JSON files.
3. Preserves the dark 450px code editor anchor and right-aligned natural-width Run & Submit button.
4. Enforces the F1 Output Card invariant: renders authentic judge results only (verdict, visible tests with expected/got, real attempt runtime); strictly forbids invented memory metrics or telemetry.
5. Implements the complete Mock Interview cycle: 45-min facts panel, strict 2-place countdown timer (`MM:SS`), session-scoped scoring, and zero-write unsolved end.

---

## 2. Tasks

### Task 3.1: Practice Arena Slim Picker & Navigation Controls
- **Actions**:
  - Update `Practice Arena` view in `app.py`:
    - Slim picker row container: clean white strip with 1px warm hairline.
    - Format problem labels:
      `f"{idx + 1}. {p['title']} · {p['topic'].replace('-', ' ').title()} ({p['difficulty'].title()})"`
      (e.g. `1. Binary Search · Binary Search (Easy)`).
    - Prev/Next Arrow Buttons:
      - Rendered as `←` and `→`.
      - Styled with `.btn-nav-arrow` (`padding: 6px 14px !important; min-width: 44px !important; border-radius: 9999px;`).
      - Verified at 1450px viewport: zero text truncation or ellipsis (`←…`).
- **Verification**:
  - Live inspection: Picker displays all 12 problems in Round 2 format; arrow buttons fit cleanly without clipping.

### Task 3.2: Problem Card Signature Block & Dark Code Editor Anchor
- **Actions**:
  - Rebuild Problem Statement Card in `app.py`:
    - 24px white container with 1px warm hairline.
    - Title in `DM Serif Display`, difficulty and topic chips in olive/terracotta/med-blue.
    - Statement body in `Plus Jakarta Sans`.
    - Signature Block:
      - Header label: `<span class="signature-subhead">STARTER FUNCTION SIGNATURE</span>` (11px uppercase letter-spaced).
      - Signature line: extracted dynamically from `p.starter_code.splitlines()[0].strip()`.
      - Strips any embedded `### Function Signature` markdown from `p.statement_md` rendering.
  - Code Editor Anchor:
    - 24px dark card (`#1E1E1E`), 450px height.
    - Ace / Streamlit code editor internals preserved.
    - Header strip: "Python 3.12 · 3.0s Timeout · Tabular Editor".
  - Action Strip:
    - Natural-width, right-aligned "Run & Submit" button styled with Terracotta primary token (`#C2452D`, `#FFF8F0` text, 9999px pill).
- **Verification**:
  - Inspect Problem Card DOM: Signature matches `starter_code.splitlines()[0]` character-for-character across all 12 problems; no duplicate signature headings.

### Task 3.3: Output Card Rebuild (F1 Invariant: No Invented Telemetry)
- **Actions**:
  - Rebuild Output Card rendering in `app.py` following fix round F1:
    - Default unrun state: Neutral header "Run your code to see results" with calm message "Test suite results, execution telemetry, and judge feedback will appear here."
    - Evaluated state:
      - Verdict banner:
        - PASS: Olive `#6B7F3B` badge `PASS — All Tests Succeeded`.
        - FAIL: Terracotta `#C2452D` badge `FAIL — Logic Divergence`.
        - TIMEOUT / ERROR: Rust badge with error details.
      - Test Count: equals the tests actually displayed (e.g. `2/2 Tests Passed` for Binary Search visible tests).
      - Test Cases: renders visible tests with Input, Expected, and Got exactly as returned by the judge.
      - Runtime: renders the real attempt's execution time (e.g. `23ms`).
      - Memory: **OMITTED ENTIRELY** (the app measures no memory; invented metrics are strictly banned).
- **Verification**:
  - Inspect Output Card after running Binary Search: Displays authentic test cases and runtime; zero memory or invented metric references.

### Task 3.4: Mock Interview Cycle (Start Facts, 2-Place Timer, Scorecard)
- **Actions**:
  - **Start Screen** (`mock_start.html`):
    - 24px white card, serif headline "Coding Interview Simulation".
    - Sandy beige facts panel (`#E8D5B7`):
      - 45 Minutes Duration.
      - 2 Interleaved Problems (selected via cognitive interleaving).
      - Hints Allowed (deducts 15% from problem score).
    - Primary CTA pill: "Begin Mock Interview" (`#C2452D`).
  - **Active Session Screen** (`mock_session.html`):
    - Top session bar with two-place countdown timer (`MM:SS`) in `JetBrains Mono` bold (e.g. `44:59`).
    - Multi-problem navigation tabs.
    - Code editor and submission action.
    - Session-scoped scoring.
  - **Scorecard Screen** (`mock_scorecard.html`):
    - Overall outcome (PASS olive / FAIL terracotta).
    - Summary metrics in sandy quiet strip (Final Score, Time Elapsed, Problems Solved).
    - Problem breakdown table.
    - FSRS scheduling impact note.
    - Zero-write unsolved end: Quitting without solving writes zero false records to `coach.db`.
- **Verification**:
  - Live mock session test: Timer displays strictly two places (`MM:SS`); scorecard displays authentic session results; exiting early creates zero false database records.

---

## 3. Skill Bindings

- `developing-with-streamlit`: Governs Streamlit Ace editor integration, timer countdown loops, session-scoped scoring, and Output Card layout.
- `/ui-styling`: Guides slim picker styling, dark editor container styling, and Output Card verdict card typography.


