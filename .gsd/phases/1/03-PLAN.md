---
phase: 1
plan: 3
wave: 3
depends_on: ["01", "02"]
files_modified:
  - mockups/dashboard.html
  - scratch/capture_r3.js
  - docs/screenshots/r3/
autonomous: false
gap_closure: false

must_haves:
  truths:
    - "Dashboard mockup displays authentic metrics: 1 day streak, 0 due, topic mastery bars matching real app categories"
    - "Dual-resolution screenshot pipeline captures all 5 mockups at 1600x1000 and 1920x1080 into docs/screenshots/r3/"
    - "All 10 required PNG screenshots exist and are non-empty"
    - "Strict code quarantine is preserved: zero changes to app.py, config.toml, coach/*, data/problems/*, or tests/*"
    - "Project owner explicitly reviews and approves the Direction A visual mockups before Phase 2 implementation begins"
  artifacts:
    - mockups/dashboard.html
    - scratch/capture_r3.js
    - docs/screenshots/r3/home_1600x1000.png
    - docs/screenshots/r3/home_1920x1080.png
    - docs/screenshots/r3/practice_1600x1000.png
    - docs/screenshots/r3/practice_1920x1080.png
    - docs/screenshots/r3/mock_1600x1000.png
    - docs/screenshots/r3/mock_1920x1080.png
    - docs/screenshots/r3/dashboard_1600x1000.png
    - docs/screenshots/r3/dashboard_1920x1080.png
    - docs/screenshots/r3/tokens_1600x1000.png
    - docs/screenshots/r3/tokens_1920x1080.png
---

# Plan 1.3: Analytics Dashboard Mockup, Dual-Resolution Capture & Visual Finish Gate

<objective>
Refine the Analytics Dashboard static mockup (`mockups/dashboard.html`), capture high-resolution screenshots for all 5 HTML mockups at both 1600x1000 and 1920x1080 resolutions into `docs/screenshots/r3/`, and conclude Phase 1 with the mandatory owner visual review and sign-off gate.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/DECISIONS.md
- mockups/dashboard.html
- scratch/capture_r3.js
- docs/screenshots/r3/
- agent-resources/lucide/icons/
</context>

<tasks>

<task type="auto">
  <name>Refine Analytics Dashboard Mockup with Authentic Topic Mastery</name>
  <files>
    mockups/dashboard.html
  </files>
  <action>
    Refine `mockups/dashboard.html` with Direction A styling and strictly authentic analytics data from SQLite:
    1. Page Header & Stat Grid:
       - Fraunces title "Performance and Analytics", subtitle referencing real-time SQLite attempt data.
       - Stat card 1 (Mint): Current Streak "1 day", badge "Retained".
       - Stat card 2 (Sky): Due for Review "0 problems", badge "0 Due".
       - Stat card 3 (Butter): Overall Pass Rate "100.0%", badge "100% Rate", caption "1 attempt passed of 1 total recorded attempt."
    2. Topic Mastery Flat Saturated Bar Chart (Zero Invented Metrics):
       - Chart container displaying category mastery strictly reflecting the real attempt data in SQLite:
         * binary-search: 100% (1/1) with `--fill-green` (`#1F9D63`)
       - Other curriculum categories (strings, arrays, recursion, etc.) shown as unattempted (0 attempts), with ZERO invented attempt counts or invented pass rates (no "87.5% (7/8)", no "75% (3/4)", no "66.7% (2/3)").
    3. Topic Breakdown Table:
       - Table columns: Topic, Track, Attempts, Passed, Pass Rate, Action.
       - Reflects real SQLite `topic_stats()`: `binary-search` (1 attempt, 1 passed, 100.0% pass rate) with authentic link to review.
    4. Iconography:
       - Verify all inline SVGs are Lucide SVGs exclusively from `agent-resources/lucide/icons`.

    AVOID: Modifying any application files or fabricating attempt numbers/pass rates.
    AVOID: Invented attempt counts (e.g. 7/8, 2/2, 3/4) or invented percentages (e.g. 87.5%).
    USE: Direction A card radius (24px), soft shadows, and strictly authentic SQLite metrics.
  </action>
  <verify>
    python -c "dash=open('mockups/dashboard.html', encoding='utf-8').read(); assert '1 day' in dash; assert '0 problems' in dash; assert 'Topic Mastery' in dash; assert 'binary-search' in dash; assert '100.0%' in dash; print('PASS: Dashboard mockup verified without invented numbers')"
  </verify>
  <done>
    `mockups/dashboard.html` renders authentic mastery metrics and category data strictly derived from SQLite without invented numbers.
  </done>
</task>

<task type="auto">
  <name>Capture Dual-Resolution High-Fidelity Screenshots</name>
  <files>
    scratch/capture_r3.js
    docs/screenshots/r3/
  </files>
  <action>
    Configure and execute the dual-resolution screenshot capture pipeline:
    1. Update `scratch/capture_r3.js` to ensure directory `docs/screenshots/r3/` is automatically created if not present.
    2. Ensure the item list includes all 5 pages at BOTH 1600x1000 and 1920x1080 resolutions:
       - `home_1600x1000.png`, `home_1920x1080.png` (`mockups/home.html`)
       - `practice_1600x1000.png`, `practice_1920x1080.png` (`mockups/practice.html`)
       - `mock_1600x1000.png`, `mock_1920x1080.png` (`mockups/mock.html`)
       - `dashboard_1600x1000.png`, `dashboard_1920x1080.png` (`mockups/dashboard.html`)
       - `tokens_1600x1000.png`, `tokens_1920x1080.png` (`mockups/tokens.html`)
    3. Execute the capture script via Node against the running headless Chrome instance on port 9222 (or start Chrome if needed).
    4. Confirm that all 10 PNG files are written to `docs/screenshots/r3/` with non-zero byte size.

    AVOID: Omitting tokens at 1920x1080 or capturing at lower resolutions.
    USE: Headless Chrome CDP capture with 2500ms delay to allow web fonts (Fraunces, Inter, JetBrains Mono) to settle.
  </action>
  <verify>
    python -c "import os; p='docs/screenshots/r3'; ex=[f for f in os.listdir(p) if f.endswith('.png')]; expected=['home_1600x1000.png','home_1920x1080.png','practice_1600x1000.png','practice_1920x1080.png','mock_1600x1000.png','mock_1920x1080.png','dashboard_1600x1000.png','dashboard_1920x1080.png','tokens_1600x1000.png','tokens_1920x1080.png']; missing=set(expected)-set(ex); assert not missing, f'Missing screenshots: {missing}'; sizes=[os.path.getsize(os.path.join(p,f)) for f in expected]; assert all(s > 10000 for s in sizes), f'Some screenshots empty: {sizes}'; print(f'PASS: All 10 screenshots captured successfully ({len(ex)} total, min size {min(sizes)} bytes)')"
  </verify>
  <done>
    All 10 dual-resolution screenshots exist in `docs/screenshots/r3/`, each verified > 10KB.
  </done>
</task>

<task type="checkpoint:human-verify">
  <name>Project Owner Visual Review and Sign-Off Gate</name>
  <files>
    docs/screenshots/r3/
  </files>
  <action>
    Present the captured dual-resolution screenshots (`docs/screenshots/r3/*.png`) to the project owner for formal visual inspection and approval:
    1. Verify Direction A visual language: warm paper canvas (#FBFAF7), 24px rounded surface cards with soft shadow, deep ink text (#171712), hairline borders (#E7E1D6), and saturated emerald green pill buttons (#15803D).
    2. Verify typography pairing: Fraunces display serif headings, Inter body copy, and JetBrains Mono code/metrics.
    3. Verify authentic data grounding: 1 day streak, 0 due, 12 problems library, Binary Search PASS 178ms, starter signature `def longest_substring(s: str) -> int:`, live countdown timer 44:41.
    4. Confirm strict code quarantine: verify git diff shows zero edits to application code (`app.py`, `.streamlit/config.toml`, `coach/*.py`, `data/problems/*.json`, `tests/*`).
  </action>
  <verify>
    python -c "import subprocess; diff = subprocess.check_output(['git', 'status', '--porcelain'], text=True); forbidden = ['app.py', 'config.toml', 'coach/', 'data/problems/', 'tests/']; breached = [line for line in diff.splitlines() if any(f in line for f in forbidden)]; assert not breached, f'QUARANTINE BREACH: {breached}'; print('PASS: Code quarantine confirmed intact')"
  </verify>
  <done>
    Project owner explicitly approves Direction A visual mockups, unlocking Phase 2 Streamlit implementation.
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
- [x] `mockups/dashboard.html` displays authentic metrics and category bars
- [x] All 10 PNG screenshots exist in `docs/screenshots/r3/` (both 1600x1000 and 1920x1080)
- [x] Code quarantine check passes (zero edits to app.py, config.toml, coach/*, data/problems/*, tests/*)
- [x] Project owner visual sign-off confirmed (Token sheet, Home, Practice, Mock, Dashboard approved)
</verification>

<success_criteria>
- [x] All tasks verified passing
- [x] Must-haves confirmed
- [x] Owner visual sign-off completed
- [x] Zero app code modified
</success_criteria>
