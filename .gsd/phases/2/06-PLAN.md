---
phase: 2
plan: 6
wave: 6
depends_on: [5]
---

# Plan 2.6: Analytics Dashboard Redesign & Direction A Implementation

## Objective
Implement the Direction A Analytics Dashboard matching `mockups/dashboard.html`, featuring three category-tinted metric cards, a Plotly mastery bar chart restyled to flat tint bars on white with hairline gridlines, NOT STARTED displayed for unattempted topics without 0% bars (Directive 1), and a structured topic breakdown table in a white 24px card.

## Context
- mockups/dashboard.html
- app.py
- coach/store.py

## Tasks

<task type="auto">
  <name>Implement Dashboard Metrics & Restyle Plotly Mastery Chart</name>
  <files>app.py</files>
  <action>
    1. Render Three Category-Tinted Stat Cards using the single named mechanism: Bordered container with keyed CSS:
       - Solved Problems: st.container(border=True, key="dash_card_solved") in wash-mint #DFF3E4 with green partner text #167B48.
       - Practice Sessions: st.container(border=True, key="dash_card_sessions") in wash-sky #DCEBFF with blue partner text #1D5EC2.
       - Average Hints Used: st.container(border=True, key="dash_card_hints") in wash-butter #FFF0C4 with amber partner text #9A3412.
    2. Restyle Plotly Mastery Chart:
       - Canvas: paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)".
       - Gridlines: axis gridlines in hairline token #E7E1D6 (1px, dashed or solid light).
       - Bar colors: Use Direction A saturated tint partners (Emerald #1F9D63, Sky #2273E6, Amber #B45309, Lilac #6C4CF1, Coral #E4572E); eliminate all default Plotly colors.
       - Directive 1 Enforcement: For topics with 0 attempts, display "NOT STARTED" and render zero bar height (never "0% (0/0)"). Only attempted topics display a filled mastery percentage bar.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -c 'import app; print(\"Dashboard chart imported cleanly\")'"</verify>
  <done>Dashboard metric cards and restyled Plotly chart render with Direction A tokens and NOT STARTED enforcement.</done>
</task>

<task type="auto">
  <name>Implement Topic Breakdown Table & Screenshot Capture</name>
  <files>app.py, scratch/capture_screen.py, docs/screenshots/r3/dashboard_real_1920x1080.png, docs/screenshots/r3/dashboard_real_1600x1000.png</files>
  <action>
    1. Implement Topic Breakdown Table using the single named mechanism: Bordered container with keyed CSS:
       - Container: st.container(border=True, key="dashboard_table_card")
       - CSS: background #FFFFFF, border 1px solid #E7E1D6, border-radius 24px
       - Render topic rows with Topic name, Track tag, Solved / Total ratio, Mastery progress bar, and Status chip.
       - Status Chip: Render NOT STARTED in muted chip (#66635A) for unattempted topics, and MASTERED / IN PROGRESS for active topics.
       - Document any HTML/CSS table vs Streamlit dataframe approximations in KNOWN LIMITS.
    2. Capture real app screenshots of Dashboard at 1920x1080 and 1600x1000 using scratch/capture_screen.py.
    3. Run self-critique loop against mockups/dashboard.html and log any differences in KNOWN LIMITS.
  </action>
  <verify>Test-Path docs/screenshots/r3/dashboard_real_1920x1080.png; Test-Path docs/screenshots/r3/dashboard_real_1600x1000.png</verify>
  <done>Dashboard breakdown table rendered in white card; dual-resolution screenshots captured.</done>
</task>

## Success Criteria
- [ ] Three dashboard stat cards styled in mint, sky, and butter washes
- [ ] Plotly chart restyled with flat tint partners and hairline gridlines
- [ ] Unattempted topics display NOT STARTED (no 0% 0/0 bars)
- [ ] Topic breakdown table renders in white 24px card container
- [ ] Dual-resolution screenshots captured at 1920x1080 and 1600x1000
