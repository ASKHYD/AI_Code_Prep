# Phase 2 Wave 3: Home Screen Redesign & Direction A Implementation Summary

**Plan:** `.gsd/phases/2/03-PLAN.md`  
**Phase:** 2 (Wave 3)  
**Execution Date:** 2026-11-05  

---

## 1. Executive Summary

Phase 2 Wave 3 implemented the full Direction A (Brilliant Light) redesign of the Home screen (`app.py`), translating the approved `mockups/home.html` specification into production code with single named container mechanisms, offline Google Fonts (Fraunces + Inter), Lucide iconography, and owner-selected Variant B metric numerals (Inter SemiBold 600 Tabular).

Key accomplishments:
1. **Home Header Banner:** Fraunces serif display heading ("Daily Review and Practice Queue", 32px 700-weight), Inter muted caption explaining the 1/1/3/7/21-day spaced repetition schedule, and primary CTA pill button "Start Practice" (`#15803D` background, 999px radius, white text, `white-space: nowrap`) routing directly to Practice Arena.
2. **Three Category-Tinted Stat Cards:** Implemented using single named mechanism `st.container(border=True, key=...)` with keyed CSS overrides:
   - **Streak Card (`home_card_streak`):** Mint wash `#DFF3E4`, border `rgba(22, 123, 72, 0.25)`, 24px border radius, Lucide flame icon in saturated green fill tile (`#1F9D63`), Inter SemiBold 600 tabular numeral, and streak caption.
   - **Due Review Card (`home_card_due`):** Sky wash `#DCEBFF`, border `rgba(29, 94, 194, 0.25)`, 24px border radius, Lucide calendar icon in saturated blue fill tile (`#2273E6`), Inter SemiBold 600 tabular numeral ("0 due"), and review schedule caption.
   - **Total Library Card (`home_card_library`):** Butter wash `#FFF0C4`, border `rgba(154, 52, 18, 0.25)`, 24px border radius, Lucide book-open icon in saturated amber fill tile (`#B45309`), Inter SemiBold 600 tabular numeral ("12 problems"), and library caption.
3. **Due for Review Section (st.info Strictly Banned):** Bordered white container (`st.container(border=True, key="home_due_section")`) with `#E7E1D6` border and 24px radius. Empty queue state renders a dedicated sky-wash card (`home_caught_up`) in wash `#DCEBFF`, border `rgba(29, 94, 194, 0.25)`, Lucide calendar icon, and copy: *"You are all caught up! No problems due for review today. Open Practice Arena to solve a new problem."* When items are due, clean problem rows with difficulty chips and "Practice" routing pills render.
4. **Recent Practice Attempts Section:** Bordered white container (`home_recent_section`) displaying authentic SQLite attempts with saturated Direction A tint chips:
   - `PASS`: wash-mint `#DFF3E4`, text `#167B48`, Lucide check icon
   - `TIMEOUT`: wash-butter `#FFF0C4`, text `#9A3412`, Lucide clock icon
   - `FAIL`: wash-rose `#FFE0E0`, text `#C5221F`, Lucide circle-x icon
   - Exact runtime in ms and hint count formatted in Inter tabular figures, plus "Review" pill button routing to Practice Arena.
5. **Real Application Screenshot Capture:** Automated dual-resolution headless Chrome captures via Chrome DevTools Protocol (`scratch/capture_screen.py`) producing:
   - `docs/screenshots/r3/home_real_1920x1080.png` (139,045 bytes)
   - `docs/screenshots/r3/home_real_1600x1000.png` (137,436 bytes)
6. **Backend Freeze & Regression Guard:** 26/26 backend pytest tests passing cleanly. Zero quarantine violations (`coach/*.py`, `data/problems/*.json`, and `tests/*` strictly untouched).

---

## 2. Tasks Completed

| Task | Summary | Files Modified | Verification | Commit |
|------|---------|----------------|--------------|--------|
| Task 1 | Implement Home Header & Three Tinted Stat Cards in `app.py` | `app.py` | Python compile & import cleanly | `fec259b` |
| Task 2 | Implement Home Queue, Activity List & Screenshot Capture | `app.py`, `scratch/capture_screen.py`, `docs/screenshots/r3/*` | Dual screenshots verified; 26/26 pytest tests pass | `fd8ff5f` |

---

## 3. Implementation Details

### Task 1: Home Header & Category-Tinted Stat Cards
- **Header Banner:** Replaced plain text container with a two-column layout:
  - Left column: Fraunces serif heading "Daily Review and Practice Queue" (font size 32px, weight 700, ink `#171712`) and Inter muted caption (`#66635A`, font size 15px).
  - Right column: Primary CTA pill button "Start Practice" styled with `#15803D`, 999px radius, white text, and `white-space: nowrap`. On click, sets `st.session_state["nav_sidebar_radio"] = "Practice Arena"`, syncs `st.query_params["screen"] = "practice"`, and triggers `st.rerun()`.
- **Keyed Tinted Stat Cards:**
  - Used `st.container(border=True, key="...")` pattern with keyed CSS in `get_global_css()`.
  - Outer border wrappers suppressed (`div.st-key-*:has([data-testid="stVerticalBlockBorderWrapper"]) { border: none !important; background: transparent !important; padding: 0 !important; }`), applying styling directly to the inner bordered block (`[data-testid="stVerticalBlockBorderWrapper"] > div`).
  - Mint, sky, and butter washes applied with 24px border radii and soft elevation shadows (`0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06)`).
  - Stat icon tiles created with 44x44px dimensions, 14px border radius, and saturated backgrounds (`#1F9D63`, `#2273E6`, `#B45309`), inlining Lucide flame, calendar, and book-open SVGs in pure white.
  - Numerals styled in Inter SemiBold 600 Tabular (`font-variant-numeric: tabular-nums`, letter spacing `-0.025em`) per owner selection (Variant B).

### Task 2: Queue, Activity List & Screenshot Capture
- **Due for Review Section:**
  - Keyed container `st.container(border=True, key="home_due_section")` styled in white surface (`#FFFFFF`) with `#E7E1D6` border and 24px radius.
  - Header displays blue calendar Lucide icon and queue status indicator ("Queue Status: Clear" or count).
  - `st.info` completely eliminated. Empty state renders `st.container(border=True, key="home_caught_up")` in wash `#DCEBFF`, border `rgba(29, 94, 194, 0.25)`, 16px radius, calendar icon tile, and required confirmation copy.
  - When problems are due, displays problem rows with difficulty badges and a "Practice" button.
- **Recent Practice Attempts Section:**
  - Keyed container `st.container(border=True, key="home_recent_section")` styled in white surface with `#E7E1D6` border and 24px radius.
  - Displays recent attempts from `store.get_recent_attempts(limit=5)`.
  - Saturated status tint chips implemented:
    - `.chip-pass`: background `#DFF3E4`, text `#167B48`, Lucide check icon
    - `.chip-timeout`: background `#FFF0C4`, text `#9A3412`, Lucide clock icon
    - `.chip-fail`: background `#FFE0E0`, text `#C5221F`, Lucide circle-x icon
  - Problem title, track, topic, difficulty, date, runtime in ms, and hint count displayed cleanly.
  - "Review" button on each attempt redirects to Practice Arena with `selected_problem_id` populated.
- **Automated Capture Pipeline:**
  - Authored `scratch/capture_screen.py` utilizing Chrome DevTools Protocol over WebSockets and headless Chrome.
  - Automatically manages local Streamlit process on port 8501, sets device metrics overrides to 1920x1080 and 1600x1000, and captures PNG screenshots to `docs/screenshots/r3/` and mirrors to brain directory.

---

## 4. Verification Evidence

### 4.1. File Existence & Import Verification
```powershell
powershell -Command "Test-Path docs/screenshots/r3/home_real_1920x1080.png; Test-Path docs/screenshots/r3/home_real_1600x1000.png"
# Result: True, True
```

### 4.2. Python Import Cleanliness Check
```powershell
cmd /c "set PYTHONPATH=. && .venv\Scripts\python.exe -c ""import app; print('Home screen compiled cleanly')"""
# Result: Home screen compiled cleanly (Exit Code 0)
```

### 4.3. Backend Regression Tests (26/26 Passing)
```powershell
cmd /c "set PYTHONPATH=. && .venv\Scripts\pytest tests"
# Result:
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: E:\resume_project
plugins: anyio-4.16.0
collected 26 items

tests\test_judge.py ........                                             [ 30%]
tests\test_llm_fallback.py ....                                          [ 46%]
tests\test_problems.py .....                                             [ 65%]
tests\test_store.py ....                                                 [ 80%]
tests\test_timer.py .....                                                [100%]

============================= 26 passed in 6.31s ==============================
```

### 4.4. Screenshot Artifacts
- `docs/screenshots/r3/home_real_1920x1080.png` (139,045 bytes, 1920x1080 resolution)
- `docs/screenshots/r3/home_real_1600x1000.png` (137,436 bytes, 1600x1000 resolution)

---

## 5. Self-Critique & Visual Review against mockups/home.html

| Mockup Element | Production Implementation | Fidelity Status | Notes |
|----------------|---------------------------|-----------------|-------|
| Header display title | Fraunces 700 32px serif heading | Exact | Uses self-hosted offline Fraunces font |
| Header subtitle | Inter 400 15px muted caption | Exact | In `#66635A` with comfortable line height |
| "Start Practice" CTA | 999px pill button in `#15803D` | Exact | White text, nowrap, routes to Practice Arena |
| Active Streak card | Wash-mint `#DFF3E4` container, 24px radius | Exact | Saturated green flame tile (`#1F9D63`) |
| Due Review card | Wash-sky `#DCEBFF` container, 24px radius | Exact | Saturated blue calendar tile (`#2273E6`) |
| Total Library card | Wash-butter `#FFF0C4` container, 24px radius | Exact | Saturated amber book tile (`#B45309`) |
| Metric numerals | Inter SemiBold 600 Tabular figures | Exact | Owner selected Variant B; monospace eliminated |
| Due for Review section | White container with `#E7E1D6` border | Exact | Single named mechanism `.st-key-home_due_section` |
| Empty queue state | Sky-wash card in `#DCEBFF` with calendar icon | Exact | `st.info` completely banned and absent |
| Recent attempts chips | Saturated tint chips (mint/butter/rose) | Exact | Direction A washes with matching text colors |
| Recent attempt row | Problem metadata, runtime, hints, "Review" btn | Exact | Tabular runtime figures; pill button routes to practice |

### Known Limits & Approximations
- Streamlit's container DOM generates nested block wrappers (`[data-testid="stVerticalBlockBorderWrapper"]`); keyed CSS rules specifically target the inner div and zero out the outer div to guarantee crisp 24px card radii without double borders or clip artifacts.

---

## 6. Commit Audit

- `fec259b`: `feat(phase-2): implement Home header and tinted stat cards with Inter tabular numerals`
- `fd8ff5f`: `feat(phase-2): implement Home queue activity list and capture real screenshots`
