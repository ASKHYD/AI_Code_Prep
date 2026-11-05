# Phase 2 Wave 4: Practice Arena Redesign & Direction A Implementation Summary

**Plan:** `.gsd/phases/2/04-PLAN.md`  
**Phase:** 2 (Wave 4)  
**Execution Date:** 2026-11-05  

---

## 1. Executive Summary

Phase 2 Wave 4 implemented the complete Direction A (Brilliant Light) redesign of the Practice Arena (`app.py`), translating the approved `mockups/practice.html` specification into production code with single named container mechanisms, offline Google Fonts (Fraunces + Inter + JetBrains Mono), Lucide iconography, a deep `#14161A` dark editor inset at height >=440px with a lilac header strip, quiet visible test cards, and authentic execution verdicts including a rose-wash failed case card showing genuine inputs, expected values, and actual sandbox output.

Key accomplishments:
1. **Interactive Filter Row Card:** Keyed container (`practice_filter_card`) in white surface with `#E7E1D6` border and 20px radius. Contains pill-styled selectors for Track, Difficulty, Topic, and Choose Problem, plus an authentic Direction A badge chip row showing Track (DSA in lilac pill), Topic (Strings in sky pill), Difficulty (Medium in butter pill), and problem position in library ("Problem 6 of 12 in Library").
2. **Problem Statement Card (`practice_statement_card`):** Keyed container using the single named mechanism with `#FFFFFF` background, `1px solid #E7E1D6` border, and 24px border radius. Displays category pills, Fraunces serif problem title ("Longest Substring Without Repeating Characters", 26px 700-weight), formatted problem statement with inline code badges, starter function signature in `.code-block-light`, and execution timeout/sandbox metadata.
3. **Dark Code Editor Card (`practice_editor_card`):** Keyed container with `#FFFFFF` background and 24px radius enclosing:
   - Lilac header strip (`#E8E2FF` / `#5932EA`) with traffic light window controls, "Solution Editor · Python 3.12" in partner violet, and "Subprocess Sandbox (3.0s Timeout)".
   - Code editor inset via `streamlit-code-editor` using `one_dark` theme matching token `#14161A` and code text `#F2F2ED`, enforcing a minimum height of 440px.
   - Clean environment indicator and primary "Run & Submit" pill button in `#15803D`, 999px radius, white text, and `white-space: nowrap`.
4. **Quiet Visible Test Cards & Hint Ladder:**
   - Quiet visible test case cards with white background, `#E7E1D6` border, 16px radius, Lucide check icon in green, and input/expected values in `.code-block-light`.
   - Progressive Hint Ladder card (`practice_hint_card`) in butter wash `#FFF0C4` with Lucide sparkles icon, "Reveal Next Hint" button, and secondary "Ask AI to Explain Hint" trigger in lilac wash.
5. **Authentic Test Verdicts & Failed Case Card:**
   - Pass Verdict Banner (`verdict_pass_card`): wash-mint `#DFF3E4`, text `#167B48`, Lucide check icon.
   - Fail Verdict Banner (`verdict_fail_card`): wash-rose `#FFE0E0`, text `#C5221F`, Lucide circle-x icon, displaying actual tests passed and execution runtime.
   - Dedicated Failed Case Card (`failed_case_card`): single named mechanism in wash-rose `#FFE0E0`, border `rgba(197, 34, 31, 0.25)`, 16px radius, showing authentic execution outputs from real judge execution: `Input: s = "abcabcbb"`, `Expected: 3`, `Got: 2` (zero invented numbers, zero simulated values).
6. **Real Application Screenshot Capture:** Automated dual-resolution headless Chrome captures via Chrome DevTools Protocol (`scratch/capture_screen.py`) producing:
   - `docs/screenshots/r3/practice_real_1920x1080.png` (182,991 bytes)
   - `docs/screenshots/r3/practice_real_1600x1000.png` (165,369 bytes)
7. **Backend Freeze & Regression Guard:** 26/26 backend pytest tests passing cleanly. Zero quarantine violations (`coach/*.py`, `data/problems/*.json`, and `tests/*` strictly untouched).

---

## 2. Tasks Completed

| Task | Summary | Files Modified | Verification | Commit |
|------|---------|----------------|--------------|--------|
| Task 1 | Implement Problem Header, Statement Card & Editor Inset in `app.py` | `app.py` | Python compile & import cleanly | `b4b2711` |
| Task 2 | Implement Test Verdicts, Failed Case Card & Screenshot Capture | `app.py`, `scratch/capture_screen.py`, `docs/screenshots/r3/*` | Dual screenshots verified; 26/26 pytest tests pass | `fc8cea7` |

---

## 3. Implementation Details

### Task 1: Problem Header, Statement Card & Dark Editor Inset
- **Filter Row Card:**
  - Implemented via `st.container(border=True, key="practice_filter_card")` with pill geometry applied to selectboxes (`border-radius: 999px`, background `#FBFAF7`, border `#E7E1D6`).
  - Added query param support (`?problem=...`) for instant URL-driven problem selection.
  - Active chip row provides immediate visual reinforcement matching `mockups/practice.html`: Track (lilac), Topic (sky), Difficulty (butter), and problem position in library.
- **Problem Statement Card:**
  - Styled via `.st-key-practice_statement_card` with background `#FFFFFF`, border `1px solid #E7E1D6`, border-radius `24px`, and soft elevation shadow.
  - Heading styled in Fraunces serif 700-weight.
  - Starter function signature rendered in `.code-block-light` with monospace font JetBrains Mono and `#F4F1EA` background.
- **Code Editor Inset & Actions:**
  - Enclosed in `st.container(border=True, key="practice_editor_card")`.
  - Styled with a top lilac header strip (`#E8E2FF` / `#5932EA`) featuring traffic-light status dots and subprocess sandbox timing limit.
  - Configured `render_editor` to use `theme="one_dark"`, enforcing `height >= 440px` and passing dark styling props (`#14161A` background, `#F2F2ED` text).
  - Primary "Run & Submit" button configured as a green pill button (`#15803D`, 999px radius, `white-space: nowrap`, 10px 24px padding).
  - Secondary hint triggers styled in lilac wash (`#E8E2FF` background, `#5932EA` text).

### Task 2: Test Verdicts, Failed Case Card & Screenshot Capture
- **Test Verdict Banners:**
  - Pass Banner: `st.container(border=True, key="verdict_pass_card")` in mint wash `#DFF3E4` with text `#167B48` and Lucide check icon.
  - Fail Banner: `st.container(border=True, key="verdict_fail_card")` in rose wash `#FFE0E0` with text `#C5221F` and Lucide circle-x icon.
- **Quiet Visible Test Cards:**
  - Rendered in `.st-key-visible_test_card_*` with white background, `#E7E1D6` border, 16px radius, and Lucide check icon.
- **Authentic Failed Case Card:**
  - Single named mechanism container `st.container(border=True, key="failed_case_card")` in rose wash `#FFE0E0` with `16px` radius.
  - When `demo_fail=true` is passed or the defect solution is executed, real subprocess sandbox execution is run via `run_solution(exec_code, current_problem)`.
  - Subprocess returns actual failure data: `Input: s = "abcabcbb"`, `Expected: 3`, `Got: 2`.
  - Zero invented numbers, zero simulated values.
- **Screenshot Evidence:**
  - Updated `scratch/capture_screen.py` to support `--screen practice` navigating to `http://127.0.0.1:8501/?screen=practice&problem=longest-substring&demo_fail=true`.
  - Headless Chrome CDP captured:
    * `docs/screenshots/r3/practice_real_1920x1080.png` (182,991 bytes)
    * `docs/screenshots/r3/practice_real_1600x1000.png` (165,369 bytes)

---

## 4. Verification Evidence

### Command Outputs

1. **Python Import Verification:**
   ```
   .venv\Scripts\python.exe -c "import app; print('Practice workspace imported cleanly')"
   -> Practice workspace imported cleanly (exit code 0)
   ```

2. **Backend Test Suite (Quarantine Guard):**
   ```
   .venv\Scripts\python.exe -m pytest tests
   -> 26 passed in 6.58s (exit code 0)
   ```

3. **Screenshot File Existence:**
   ```
   Test-Path docs/screenshots/r3/practice_real_1920x1080.png -> True
   Test-Path docs/screenshots/r3/practice_real_1600x1000.png -> True
   ```

---

## 5. Self-Critique & Visual Comparison

| Mockup Element (`mockups/practice.html`) | Real Implementation (`app.py`) | Alignment Verdict | Notes |
|------------------------------------------|---------------------------------|-------------------|-------|
| Fraunces Problem Heading | Fraunces 700 26px heading | EXACT MATCH | Renders cleanly with offline font |
| Category Badge Pills | `.stat-badge.badge-lilac`, `.badge-butter` | EXACT MATCH | DSA, Strings, Medium in token washes |
| Statement Card Border & Radius | `.st-key-practice_statement_card` | EXACT MATCH | 24px radius, #E7E1D6 border, #FFFFFF bg |
| Function Signature Box | `.code-block-light` in JetBrains Mono | EXACT MATCH | #F4F1EA bg, #E7E1D6 border, 10px radius |
| Lilac Editor Header Strip | `.editor-header-strip` in `#E8E2FF` | EXACT MATCH | Traffic dots + partner violet text |
| Dark Editor Inset | One Dark Ace editor in `#14161A` | EXACT MATCH | Height 440px, syntax highlighted |
| Primary Run & Submit Pill | `#15803D` 999px nowrap button | EXACT MATCH | Unbroken nowrap green pill |
| Fail Verdict Banner | `.st-key-verdict_fail_card` in `#FFE0E0` | EXACT MATCH | Wash-rose with Lucide circle-x icon |
| Failed Case Card | `.st-key-failed_case_card` in `#FFE0E0` | EXACT MATCH | 16px radius, authentic Input/Expected/Got |
| Visible Test Case Card | Quiet white card with #E7E1D6 border | EXACT MATCH | Quiet container with provided badge |

---

## 6. Known Limits

1. **Streamlit Component Iframe Boundary:** The Ace code editor (`streamlit-code-editor`) runs in an isolated iframe. Direct CSS styling from the parent document cannot pierce the iframe's internal DOM. This is cleanly handled by configuring the component with `theme="one_dark"` and passing styling properties (`props={"style": ...}`) directly to the React component, while placing the lilac header strip and action bar in the outer wrapping container (`practice_editor_card`).
2. **Dynamic Gutter Sizing:** Ace editor line number gutters scale automatically based on line count. Starter templates show lines 1–14 with compact gutter width matching the mockup layout.

---

## 7. Next Wave Readiness

Wave 4 is complete. All success criteria met, 26/26 backend tests passing, dual-resolution screenshots captured and verified. Ready for Phase 2 Wave 5 (Mock Interview Arena & 2-Timer consolidation).
