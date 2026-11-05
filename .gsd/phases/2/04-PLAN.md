---
phase: 2
plan: 4
wave: 4
depends_on: [3]
---

# Plan 2.4: Practice Arena Arena Redesign & Direction A Implementation

## Objective
Implement the Direction A Practice Arena matching `mockups/practice.html`, including the filter chips row, clean problem statement card with starter signature block, the dark #14161A editor inset at height >=440px with Run & Submit primary pill, quiet visible test cards, and a rose-wash failed case card with authentic inputs and actual execution output.

## Context
- mockups/practice.html
- app.py
- data/problems/

## Tasks

<task type="auto">
  <name>Implement Problem Header, Statement Card & Editor Inset</name>
  <files>app.py</files>
  <action>
    1. Render Filter Row:
       - Track, Difficulty, and Topic selectors styled as clean pill-like selection elements.
       - Problem title in Fraunces serif with difficulty pill (e.g. Medium in butter wash #FFF0C4 / #9A3412).
    2. Render Problem Statement Card using the single named mechanism: Bordered container with keyed CSS:
       - Container: st.container(border=True, key="practice_statement_card")
       - CSS: background #FFFFFF, border 1px solid #E7E1D6, border-radius 24px
       - Render formatted description, examples with input/output blocks, constraints list, and function signature box.
    3. Render Code Editor:
       - Use streamlit-code-editor with custom dark theme inset matching token #14161A and code text #F2F2ED.
       - Enforce minimum height of 440px.
       - Attempt to style the editor header strip in lilac wash (#E8E2FF / #5932EA) via wrapping container st.container(border=True, key="practice_editor_card"); document any component-iframe styling boundaries in KNOWN LIMITS.
    4. Render Action Row:
       - "Run & Submit" button configured as primary pill button: background #15803D, border-radius 999px, white-space: nowrap, padding 10px 24px.
       - AI Hint and Code Review triggers styled as secondary pill buttons in lilac wash.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -c 'import app; print(\"Practice workspace imported cleanly\")'"</verify>
  <done>Practice Arena displays statement card, #14161A dark editor, and primary Run & Submit pill.</done>
</task>

<task type="auto">
  <name>Implement Test Verdicts, Failed Case Card & Screenshot Capture</name>
  <files>app.py, scratch/capture_screen.py, docs/screenshots/r3/practice_real_1920x1080.png, docs/screenshots/r3/practice_real_1600x1000.png</files>
  <action>
    1. Implement Test Case Display & Verdict Banners:
       - Pass Verdict Banner: st.container(border=True, key="verdict_pass_card") with wash-mint #DFF3E4, text #167B48, and Lucide check-circle-2 icon.
       - Fail Verdict Banner: st.container(border=True, key="verdict_fail_card") with wash-rose #FFE0E0, text #C5221F, and Lucide x-circle icon.
       - Visible Test Cases: Rendered as quiet cards with white background, #E7E1D6 border, and test case status indicator.
       - Failed Test Case Detail: When a test fails, render a dedicated rose-wash card using the single named mechanism: Bordered container with keyed CSS (.st-key-failed_case_card). Show authentic input, expected output, and actual produced output from the real code judge execution (no simulated or invented values).
    2. Capture real app screenshots with Longest Substring problem loaded at 1920x1080 and 1600x1000 using scratch/capture_screen.py.
    3. Run self-critique loop against mockups/practice.html and log any deviations in KNOWN LIMITS.
  </action>
  <verify>Test-Path docs/screenshots/r3/practice_real_1920x1080.png; Test-Path docs/screenshots/r3/practice_real_1600x1000.png</verify>
  <done>Practice Arena verdicts and failed-case cards render in token washes; dual-resolution screenshots captured.</done>
</task>

## Success Criteria
- [ ] Problem statement card renders with Fraunces heading and 24px radius
- [ ] Code editor is the single dark inset (#14161A) at height >= 440px
- [ ] Run & Submit button is an unbroken nowrap pill (#15803D)
- [ ] Failed case card renders in rose wash with authentic execution output
- [ ] Dual-resolution screenshots captured at 1920x1080 and 1600x1000
