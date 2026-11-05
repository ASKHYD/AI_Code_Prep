---
phase: 2
plan: 2
wave: 2
depends_on: [1]
---

# Plan 2.2: Lucide Icon Pipeline & Direction A Sidebar Implementation

## Objective
Establish the Lucide SVG icon pipeline in `assets/icons/`, and implement the Direction A sidebar featuring a Fraunces serif wordmark, quiet tagline, keyed CSS active-nav pill navigation, and a bordered mini-card for streak and due metrics that exactly matches Home's store calls.

## Context
- agent-resources/lucide/icons/
- app.py
- mockups/home.html

## Tasks

<task type="auto">
  <name>Populate assets/icons/ with Required Lucide SVGs</name>
  <files>assets/icons/</files>
  <action>
    1. Create assets/icons/ directory.
    2. Copy needed Lucide SVG icons from agent-resources/lucide/icons/:
       - home.svg (Home nav)
       - code-2.svg (Practice nav)
       - timer.svg (Mock nav & timer pill)
       - bar-chart-3.svg (Dashboard nav)
       - flame.svg (Streak metric)
       - calendar.svg (Due metric)
       - book-open.svg (Library metric)
       - check-circle-2.svg (Pass verdict)
       - x-circle.svg (Fail verdict)
       - clock.svg (Timeout verdict & test runtime)
       - sparkles.svg (AI hint)
       - download.svg (Export scorecard)
    3. Ensure zero emoji icons exist in the navigation or sidebar.
    4. Provide an inlining helper in app.py that reads SVG strings and embeds them into HTML markup.
  </action>
  <verify>Test-Path assets/icons/flame.svg; Test-Path assets/icons/home.svg; Test-Path assets/icons/bar-chart-3.svg</verify>
  <done>All required Lucide SVG files present in assets/icons/ and accessible to app.py.</done>
</task>

<task type="auto">
  <name>Implement Direction A Sidebar & Keyed Nav Pill</name>
  <files>app.py</files>
  <action>
    1. Restructure the sidebar layout in app.py:
       - Header: Fraunces serif wordmark "AI Coding Prep Coach" (font-size 20px, font-weight 700, color #171712).
       - Tagline: Inter caption "Zero Cost • Code-Judged • Offline-Ready" (color #66635A).
    2. Navigation Mechanism (Single Named Mechanism): Keyed CSS on radio labels (.st-key-nav_sidebar_radio):
       - Style .st-key-nav_sidebar_radio div[role="radiogroup"] label to have 999px border-radius, generous horizontal padding (10px 18px), and 4px vertical margin.
       - Style the checked state .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) with background-color: #DFF3E4 (wash-mint) and color: #167B48 (partner-green) with font-weight: 600.
       - Hide the default radio circle indicator (.st-key-nav_sidebar_radio div[role="radiogroup"] label > div:first-child { display: none !important; }).
    3. Metric Mini-Card (Single Named Mechanism): Bordered container with keyed CSS:
       - st.container(border=True, key="sidebar_summary_card")
       - CSS: .st-key-sidebar_summary_card [data-testid="stVerticalBlockBorderWrapper"] > div { border: 1px solid #E7E1D6; border-radius: 16px; background-color: #FFFFFF; }
       - Display Active Streak ("X days") and Due for Review ("Y problems") using the identical store calls as Home: streak_count and len(due_list).
    4. Verify navigation switching works seamlessly across all 4 destinations (Home, Practice Arena, Mock Interview, Dashboard) and query parameters stay in sync.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -c 'import app; print(\"App imported cleanly\")'"</verify>
  <done>Sidebar displays Fraunces wordmark, active-nav pill in wash-mint, and metric figures exactly matching Home.</done>
</task>

## Success Criteria
- [ ] assets/icons/ contains all required Lucide SVGs (no emoji icons)
- [ ] Sidebar renders Fraunces wordmark and Direction A styling
- [ ] Active nav state is a tinted pill in wash-mint with green text
- [ ] All four screen destinations switch properly and preserve URL query parameter sync
- [ ] Sidebar streak/due metrics match Home exactly
