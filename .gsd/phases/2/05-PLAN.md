---
phase: 2
plan: 5
wave: 5
depends_on: [4]
---

# Plan 2.5: Mock Interview Redesign & Direction A Implementation

## Objective
Implement the Direction A Mock Interview screen matching `mockups/mock.html`, enforcing the two-countdown rule (peach header pill and in-card time-remaining figure), preserving the R1 timer fragment mechanism, restyling problem tabs with coral active states, and displaying an authentic scorecard with an export pill.

## Context
- mockups/mock.html
- app.py
- coach/timer.py

## Tasks

<task type="auto">
  <name>Implement Two-Timer Countdown & Mock Session Header</name>
  <files>app.py</files>
  <action>
    1. Preserve Timer Logic:
       - Keep the R1 @st.fragment(run_every=1) live countdown loop without altering calculate_remaining_time() or store interactions.
    2. Consolidate Countdown Displays to Exactly TWO (Directive 2):
       - Display 1: Header capsule in wash-peach #FFE8D1, text #B93815, 999px radius, containing Lucide timer icon and live ticking mm:ss.
       - Display 2: In-card primary time-remaining figure inside the session control card.
       - Remove any third live countdown display (e.g. redundant session-clock sidebar line or footer timer).
    3. Setup & Session Control Card using the single named mechanism: Bordered container with keyed CSS:
       - Container: st.container(border=True, key="mock_timer_card")
       - CSS: background #FFE8D1 (wash-peach), border 1px solid rgba(185, 56, 21, 0.25), border-radius 24px
       - Render time remaining, problems solved count, and "End Interview Early" danger pill button.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -c 'import app; print(\"Mock timer imported cleanly\")'"</verify>
  <done>Mock screen displays exactly two countdown timers in wash-peach; timer fragment ticks live without backend regressions.</done>
</task>

<task type="auto">
  <name>Implement Problem Tabs, Authentic Scorecard & Screenshot Capture</name>
  <files>app.py, scratch/capture_screen.py, docs/screenshots/r3/mock_real_1920x1080.png, docs/screenshots/r3/mock_real_1600x1000.png</files>
  <action>
    1. Style Problem Tabs:
       - Style stTabs active tab indicator in coral (#B93815) with soft peach highlight.
    2. Implement Scorecard Summary Card using the single named mechanism: Bordered container with keyed CSS:
       - Container: st.container(border=True, key="mock_scorecard_card")
       - CSS: background #FFFFFF, border 1px solid #E7E1D6, border-radius 24px
       - Display authentic results only:
         - Completed problem row: Binary Search · PASS · 178 ms · Hints: 0
         - Summary metrics: 1 Solved, 1 In Progress
       - Export Scorecard Action: Render secondary pill button with Lucide download icon: "Export Results as Markdown".
    3. Capture real app screenshots of Mock screen in active state at 1920x1080 and 1600x1000 using scratch/capture_screen.py.
    4. Run self-critique loop against mockups/mock.html and record findings in KNOWN LIMITS.
  </action>
  <verify>Test-Path docs/screenshots/r3/mock_real_1920x1080.png; Test-Path docs/screenshots/r3/mock_real_1600x1000.png</verify>
  <done>Mock tabs, authentic scorecard, and export pill render with Direction A styling; dual-resolution screenshots captured.</done>
</task>

## Success Criteria
- [ ] Countdown timer rendered in exactly TWO places (peach header pill and in-card figure)
- [ ] R1 fragment mechanism (run_every=1) preserved with live ticking
- [ ] Mock scorecard displays only authentic results (Binary Search · PASS · 178 ms)
- [ ] Export button styled as an unbroken pill button with Lucide icon
- [ ] Dual-resolution screenshots captured at 1920x1080 and 1600x1000
