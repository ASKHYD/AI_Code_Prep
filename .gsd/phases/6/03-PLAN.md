---
phase: 6
plan: "03"
wave: 2
depends_on: ["01"]
---

# Plan 6.3: Mock Interview Experience Mockups (Start, Session, Scorecard)

## Objective
Implement static HTML/CSS mockups for the three states of the Mock Interview simulation: Start Screen, Active Session Screen, and Final Scorecard. Ensure strict compliance with Addendum A invariants: sandy session bands, mono timer with exactly 2 display places, real simulation parameters (45m, 2 problems), and clear olive/terracotta verdict semantics.

## Context
- `.gsd/SPEC.md`
- `.gsd/phases/6/DISCUSS.md`
- `mockups/terracotta/style.css`
- `mockups/mock.html` (Phase 1 reference)
- `coach/timer.py` (timer invariants)

---

## Tasks

<task type="auto">
  <name>Task 3.1: Implement Mock Start & Active Session Screens</name>
  <files>mockups/terracotta/mock_start.html, mockups/terracotta/mock_session.html</files>
  <action>
    <!-- Skill binding: /agency-frontend-developer + /ui-ux-pro-max -->
    1. Create `mockups/terracotta/mock_start.html`:
       - Sticky topbar with Mock Interview active (Terracotta underline).
       - Display headline: DM Serif Display "Coding Interview Simulation".
       - Sandy format panel in `#E8D5B7`:
         - Explanatory strip with authentic format facts: 45 minutes total time, 2 interleaved technical problems, progressive hints available with score penalties.
       - Timer Preview Card: 24px rounded card displaying `45:00` in JetBrains Mono semibold.
       - Primary CTA: Terracotta pill button ("Begin Mock Interview").
    2. Create `mockups/terracotta/mock_session.html`:
       - Sandy session band across the top of the workbench:
         - Displays Problem 1 of 2 indicator, problem switcher pill toggle.
         - Running Countdown Timer in JetBrains Mono with exactly TWO display places (`MM:SS` e.g. `38:42`). Never three places (`HH:MM:SS`).
       - Two-pane workbench with Problem Card on left and dark code editor on right.
       - "Submit Solution" & "Finish Interview" action controls with hover/press micro-interactions.
  </action>
  <verify>.venv\Scripts\python.exe -c "import os; assert os.path.isfile('mockups/terracotta/mock_start.html') and os.path.isfile('mockups/terracotta/mock_session.html'); print('Mock start & session mockups exist')"</verify>
  <done>`mockups/terracotta/mock_start.html` and `mockups/terracotta/mock_session.html` implemented and verified.</done>
</task>

<task type="auto">
  <name>Task 3.2: Implement Mock Scorecard Screen</name>
  <files>mockups/terracotta/mock_scorecard.html</files>
  <action>
    <!-- Skill binding: /agency-frontend-developer + /ui-ux-pro-max -->
    1. Create `mockups/terracotta/mock_scorecard.html`:
       - Topbar with Mock Interview active.
       - Display headline: DM Serif Display "Interview Performance Scorecard".
       - Verdict Banner:
         - Overall Verdict: PASS in Olive `#6B7F3B` / FAIL in Terracotta `#C2452D`.
       - Sandy Summary Strip in `#E8D5B7`:
         - Total Time Spent (e.g. `24m 18s / 45m 00s`), Problems Solved (e.g. `2 / 2`), Hints Consulted (e.g. `1 hint`).
       - Problem-by-problem outcome cards:
         - Problem 1: Two Sum (Arrays & Hashing) — PASS (Olive chip, 0 hints, 8m 12s).
         - Problem 2: Valid Palindrome (Two Pointers) — PASS (Olive chip, 1 hint used, 16m 06s).
       - Action Footer:
         - Primary: Terracotta pill button ("Download Assessment Report").
         - Secondary: Outline button ("Return to Dashboard / Home").
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('mockups/terracotta/mock_scorecard.html').read(); assert 'Scorecard' in content and 'Download Assessment' in content; print('Mock scorecard mockup valid')"</verify>
  <done>`mockups/terracotta/mock_scorecard.html` implemented with authentic scorecard data and styling.</done>
</task>

---

## Must-Haves
After all tasks complete, verify:
- [ ] Format panel on start screen uses sandy beige `#E8D5B7` and states 45 min, 2 problems.
- [ ] Running timer uses JetBrains Mono and exactly 2 display places (`MM:SS`).
- [ ] Scorecard renders PASS in olive `#6B7F3B` and FAIL in terracotta `#C2452D`.
- [ ] Primary actions use terracotta `#C2452D`.

## Success Criteria
- [ ] All 3 mock interview screens render cleanly and adhere to the Terracotta token system.
- [ ] Addendum A timer and session scoping invariants preserved.
