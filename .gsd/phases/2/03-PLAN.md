---
phase: 2
plan: 3
wave: 3
depends_on: [2]
---

# Plan 2.3: Home Screen Redesign & Direction A Implementation

## Objective
Implement the Direction A Home screen matching `mockups/home.html`, featuring a warm header with a "Start Practice" CTA pill, three category-tinted stat cards with Lucide icon tiles and the owner's selected numeral typography, a sky-wash Due for Review card (st.info strictly banned), and an authentic Recent Practice Attempts card with saturated tint chips.

## Context
- mockups/home.html
- app.py
- DESIGN.md

## Tasks

<task type="auto">
  <name>Implement Home Header & Three Tinted Stat Cards</name>
  <files>app.py</files>
  <action>
    1. Render Today's Practice header banner:
       - Fraunces serif heading "Daily Review and Practice Queue"
       - Inter muted caption explaining the 1/1/3/7/21-day spaced repetition schedule
       - Primary CTA pill button "Start Practice" (999px radius, #15803D, white text, nowrap) routing to Practice Arena
    2. Render three category-tinted stat cards using the single named mechanism: Bordered container with keyed CSS:
       - Streak Card: st.container(border=True, key="home_card_streak")
         - CSS: background #DFF3E4 (wash-mint), border 1px solid rgba(22, 123, 72, 0.25), border-radius 24px
         - Lucide flame icon in saturated green fill tile (#1F9D63)
         - Label: "Active Streak", Value: "{streak_count} day(s)" using owner's chosen numeral typography
       - Due Review Card: st.container(border=True, key="home_card_due")
         - CSS: background #DCEBFF (wash-sky), border 1px solid rgba(29, 94, 194, 0.25), border-radius 24px
         - Lucide calendar icon in saturated blue fill tile (#2273E6)
         - Label: "Problems Due Today", Value: "{len(due_list)} due"
       - Total Library Card: st.container(border=True, key="home_card_library")
         - CSS: background #FFF0C4 (wash-butter), border 1px solid rgba(154, 52, 18, 0.25), border-radius 24px
         - Lucide book-open icon in saturated amber fill tile (#B45309)
         - Label: "Total Problem Bank", Value: "{len(all_problems)} problems"
    3. Ensure no unchosen font variant remains as dead CSS.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -c 'import app; print(\"Home header imported cleanly\")'"</verify>
  <done>Home header and 3 stat cards render with exact Direction A tints and geometry.</done>
</task>

<task type="auto">
  <name>Implement Home Queue, Activity List & Screenshot Capture</name>
  <files>app.py, scratch/capture_screen.py, docs/screenshots/r3/home_real_1920x1080.png, docs/screenshots/r3/home_real_1600x1000.png</files>
  <action>
    1. Implement Due for Review section using the single named mechanism: Bordered container with keyed CSS:
       - Container: st.container(border=True, key="home_due_section")
       - CSS: background #FFFFFF, border 1px solid #E7E1D6, border-radius 24px
       - st.info is STRICTLY BANNED for the empty queue state.
       - If no problems due: render a sky-wash card (.st-key-home_caught_up) with wash #DCEBFF, border rgba(29, 94, 194, 0.25), Lucide calendar icon, and copy: "You are all caught up! No problems due for review today. Open Practice Arena to solve a new problem."
       - If problems due: render clean problem rows with title, topic tag, difficulty, consecutive passes, and a "Practice" pill button.
    2. Implement Recent Practice Attempts section:
       - Container: st.container(border=True, key="home_recent_section")
       - Table/list of recent attempts fetched from store.get_recent_attempts(limit=5):
         - Status chips styled with exact Direction A washes:
           - PASS: wash-mint #DFF3E4, text #167B48
           - TIMEOUT: wash-butter #FFF0C4, text #9A3412
           - FAIL: wash-rose #FFE0E0, text #C5221F
         - Display real runtime in ms and hint count.
    3. Capture real app screenshots at 1920x1080 and 1600x1000 using scratch/capture_screen.py.
    4. Run self-critique loop against mockups/home.html and record any approximations in KNOWN LIMITS.
  </action>
  <verify>Test-Path docs/screenshots/r3/home_real_1920x1080.png; Test-Path docs/screenshots/r3/home_real_1600x1000.png</verify>
  <done>Home screen fully implemented with sky-wash queue card, authentic attempts list, and dual-resolution screenshots captured.</done>
</task>

## Success Criteria
- [ ] Home header displays Fraunces serif title and primary CTA pill
- [ ] Three stat cards render in mint, sky, and butter washes with Lucide icons
- [ ] Due for Review state uses sky-wash card; st.info is completely absent
- [ ] Recent attempts display saturated tint chips for PASS, TIMEOUT, FAIL
- [ ] Dual-resolution screenshots captured at 1920x1080 and 1600x1000
