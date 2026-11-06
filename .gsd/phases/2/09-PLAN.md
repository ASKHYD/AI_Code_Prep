---
phase: 2
plan: "09"
wave: 0
depends_on: []
---

# Phase 2 Wave 09 Plan: Topbar Workbench Final Corrective (Items X1–X9, Evidence §E)

> **Phase:** Phase 2 (Milestone 1 — UI Redesign)  
> **Wave:** 09 — Final Corrective (Topbar Workbench Polish & Verification §E)  
> **Source Contract:** Owner Live-Test Rejection Brief & `TOPBAR-IMPLEMENTATION-CORRECTIVE`  
> **Governing System:** Direction A (Brilliant Light, 26 Tokens in `DESIGN.md`)  
> **Quarantine Boundary:** `coach/*.py`, `data/problems/*.json`, `tests/*` strictly frozen (31/31 suite invariant)  
> **Architecture:** Parallel Subagents across 3 Waves (`/dispatching-parallel-agents` under `/executor`)  

---

## 1. Objective & Overview

Address the owner's live-test rejection of the Topbar Workbench finish across items X1–X9 and settle all evidence debts (§E) from the implementation audit.

The work is organized into 3 sequential waves with maximum internal parallelism:
- **Wave 0 (Sequential Gate)**: E7 disposition (`build_app.py` documented as scratch artifact, `app.py` single source of truth), top-level Plotly import check in `app.py`, and baseline pytest validation (31 passed).
- **Wave 1 (3 Parallel Lanes via `/dispatching-parallel-agents`)**:
  - **Lane A (Shell)**: X1 (kill top void, sticky full-bleed navbar), X2 (runtime-derived version text). Owns `get_global_css()` and `render_topbar()`.
  - **Lane B (Home + Dashboard)**: X3 (Plotly topic pass-rate horizontal bar chart from store data), X4 (primary pill buttons), X7-Home (mockup subtexts, `NOT STARTED` streak 0). Owns Home and Dashboard.
  - **Lane C (Practice Arena)**: X5R (filter strip deleted, ONE slim picker row), X6 (signature single source of truth 12/12), X7-Practice (Output neutral header "Run your code to see results"), X8 ("Run & Submit" natural width), X9 (small-caps `STARTER FUNCTION SIGNATURE` label, inline code pastel chips). Owns Practice Arena.
- **Wave 2 (Parallel Evidence Fan-Out & Gate)**: Lane D fans out into subagents:
  - **D1**: E6 Mock proofs (store snapshots, in-session-solve scorecard, $\ge 10$s timer pair).
  - **D2**: E1 Impeccable live audit across 4 screens in parallel.
  - **D3**: E2 Font proof + E9 Pill-tint CDP hexes + r6 capture set.
  - **Orchestrator**: E3–E5 assembly, `/agency-ui-finish-gate-reviewer` anti-slop check, `/verify 2` re-run, and filing `.gsd/phases/2/IMPLEMENTATION_CORRECTIVE_RETURN.md`.

---

## 2. Frozen Boundaries & Freezes

1. **Backend & Problem Bank Freeze**: Under no circumstances modify `coach/*.py`, `data/problems/*.json`, or `tests/*`. The test suite must remain strictly 31 unit tests.
2. **Logic Freeze in `app.py`**: Queries, judge execution, scoring algorithms, hints, repetition intervals, and session-scoping semantics (`mode == 'mock'` AND `created_at >= session_start_iso`) remain identical.
3. **Zero Hex Drift**: Only the 26 Direction A tokens defined in `DESIGN.md` are permitted.
4. **Stop Gate**:
   `Stopped at Topbar Workbench final corrective gate, awaiting owner live approval.`

---

## 3. Detailed Wave & Lane Tasks

### WAVE 0: SEQUENTIAL PRE-FLIGHT GATE
*Gate keeper: Orchestrator. No Wave 1 lane may start until Wave 0 is committed.*

<task type="auto">
  <name>Wave 0.1: E7 Disposition & Single Source of Truth</name>
  <files>scratch/build_app.py, app.py</files>
  <action>
    - Formally document the status of `build_app.py`: It was placed in `scratch/build_app.py` during initial bootstrap.
    - Confirm on record that `scratch/build_app.py` is a scratch historical artifact and `app.py` is the SINGLE, SOLE source of truth for all application code.
    - Ensure `scratch/build_app.py` remains untracked or archived in `scratch/`, never imported or run by the application.
  </action>
  <verify>powershell -Command "Test-Path 'scratch/build_app.py'"</verify>
  <done>build_app.py documented under scratch/; app.py verified as sole source of truth.</done>
</task>

<task type="auto">
  <name>Wave 0.2: Plotly Import Check & Baseline Pytest</name>
  <files>app.py</files>
  <action>
    - Inspect top imports in `app.py` (lines 1–35). Add `import plotly.graph_objects as go` directly beneath `import streamlit as st` so Lane B never has to touch imports outside its assigned bounds.
    - Run the baseline test suite: `.venv\Scripts\python.exe -m pytest tests`.
    - Record exact baseline result (expecting 31 passed in ~8s).
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>Plotly imported at top of app.py; pytest passes 31/31.</done>
</task>

*Coverage Wave 0: E7.*

---

### WAVE 1: THREE CONCURRENT SUBAGENTS (`/dispatching-parallel-agents`)

#### LANE A: SHELL & TOPBAR
*Skill Binding:* `/agency-minimal-change-engineer`  
*Boundaries in `app.py`:* Lines 127–836 (`get_global_css`) and Lines 935–1005 (`render_topbar`).  
*Exclusive Responsibility:* Shared CSS block belongs to Lane A only.

<task type="auto">
  <name>Lane A.1: X1 — Top Void Killed & Sticky Full-Bleed Navbar</name>
  <files>app.py</files>
  <action>
    - In `get_global_css()`:
      - Override `.block-container` so top padding is completely eliminated: `padding-top: 0 !important; margin-top: 0 !important;`.
      - Suppress default Streamlit header completely: `header[data-testid="stHeader"] { display: none !important; height: 0 !important; }`.
      - Set `.topbar` container to `position: sticky; top: 0; z-index: 999; margin: 0 -2rem 24px -2rem;` ensuring it anchors flush to the top edge (`top: 0`) with zero gap across viewports.
  </action>
  <verify>.venv\Scripts\python.exe scratch/audit_hex_drift.py</verify>
  <done>Top void eliminated; navbar anchored sticky at top: 0 with 0px gap.</done>
</task>

<task type="auto">
  <name>Lane A.2: X2 — Runtime-Derived Navbar Version Chip</name>
  <files>app.py</files>
  <action>
    - In `render_topbar()`:
      - Remove the hardcoded `"3.11"` text chip from `.status-chip-py`.
      - Derive version dynamically at runtime using `sys.version_info`: `py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"`.
      - Render runtime version in the navbar chip (e.g., `3.12`), ensuring zero static version discrepancies.
  </action>
  <verify>.venv\Scripts\python.exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"</verify>
  <done>Navbar version chip derives dynamically from Python runtime.</done>
</task>

<task type="auto">
  <name>Lane A.3: Embedded CSS Maintenance for Lanes B & C</name>
  <files>app.py</files>
  <action>
    - In `get_global_css()`:
      - Add styling requested by Lane B: primary pill CTA styles (`.btn-pill-primary { border-radius: 9999px !important; background: #15803D !important; color: #FFFFFF !important; font-weight: 600 !important; }`).
      - Add styling requested by Lane C: slim problem picker row styling (`.problem-picker-row`, `.picker-title`, `.picker-arrow-btn`), small-caps signature label (`.signature-subhead { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #66635A; }`), and inline code pastel wash chips (`.problem-statement code { background: rgba(102, 99, 90, 0.08) !important; color: #171712 !important; padding: 2px 6px !important; border-radius: 4px !important; }`).
  </action>
  <verify>.venv\Scripts\python.exe scratch/audit_hex_drift.py</verify>
  <done>All required styles for Lanes B & C incorporated without hex drift.</done>
</task>

*Coverage Lane A: X1, X2.*

---

#### LANE B: HOME & DASHBOARD
*Skill Binding:* `/agency-frontend-developer`  
*Boundaries in `app.py`:* Lines 1006–1162 (`Home`) and Lines 2084–2315 (`Dashboard`).

<task type="auto">
  <name>Lane B.1: X3 — Restore Plotly Topic Pass-Rate Chart on Dashboard</name>
  <files>app.py</files>
  <action>
    - In `render_dashboard()` (lines 2084–2315):
      - Build Plotly horizontal bar chart using `plotly.graph_objects as go`.
      - Sourced STRICTLY from store data (`store.topic_stats()`).
      - Filter to ATTEMPTED topics only (`attempts > 0`); topics with 0 attempts must not appear in the chart.
      - Chart styling: Paper background (`#FBFAF7`), bars colored with Direction A fill green (`#1F9D63`), font family Inter, hairline gridlines (`#E7E1D6`).
      - Embed via `st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})`.
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>Plotly topic pass-rate chart restored on Dashboard for attempted topics only.</done>
</task>

<task type="auto">
  <name>Lane B.2: X4 & X7-Home — Primary Pill CTAs & Mockup Subtexts</name>
  <files>app.py</files>
  <action>
    - In Home screen (lines 1006–1162):
      - Style "Start Practice" and "Continue Practice" action buttons as primary pill buttons (rounded-full, primary green `#15803D`, white text).
      - Restore exact approved mockup copy for card subtexts and captions.
      - In streak card: when `streak_count == 0`, render the status badge as `NOT STARTED` with muted styling rather than active streak text.
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>Primary pill CTAs rendered; exact mockup subtexts and NOT STARTED streak 0 state active.</done>
</task>

*Coverage Lane B: X3, X4, X7-Home.*

---

#### LANE C: PRACTICE ARENA
*Skill Binding:* `/agency-senior-developer`  
*Boundaries in `app.py`:* Lines 1163–1509 (`Practice Arena`).

<task type="auto">
  <name>Lane C.1: X5R — Filter Strip Deleted & ONE Slim Picker Row</name>
  <files>app.py</files>
  <action>
    - In Practice screen (lines 1163–1509):
      - DELETE the 3-select filter strip (Track, Difficulty, Topic selects and labels completely removed).
      - Implement ONE slim picker row at the top of the Left column:
        - Full problem title in Fraunces serif (`font-size: 18px; font-weight: 700; color: #171712;`).
        - Clean `← Prev` and `Next →` navigation buttons that cycle sequentially through all problems.
        - Zero enclosing filter card box, zero extraneous dropdowns.
        - Picker is the single source of truth for problem selection, preserving arrivals from Home queue via `st.query_params.get("problem")`.
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>Filter strip removed; ONE slim picker row serves as single selection source.</done>
</task>

<task type="auto">
  <name>Lane C.2: X6 & X9 — Signature Unification & Small-Caps Heading</name>
  <files>app.py</files>
  <action>
    - Unified Signature: Derive the preformatted statement signature box strictly from `problem["starter_code"]` or problem definition, verifying 12/12 problems match the editor code exactly.
    - X9 Label: Render section header as small-caps `STARTER FUNCTION SIGNATURE` (`font-size: 11px; letter-spacing: 0.08em; font-weight: 700; color: #66635A;`).
    - Inline Code: Render inline `code` snippets in markdown statements as styled pastel wash chips (`background: rgba(102, 99, 90, 0.08); padding: 2px 6px; border-radius: 4px;`).
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>12/12 signatures unified with editor; small-caps label and code chips styled.</done>
</task>

<task type="auto">
  <name>Lane C.3: X7-Practice & X8 — Neutral Output Header & Natural Width CTA</name>
  <files>app.py</files>
  <action>
    - Neutral Output Header: Set pre-run neutral Output Card header strictly to `"Run your code to see results"`.
    - Natural Width CTA: Remove artificial 100% full-width expansion from "Run & Submit" button so it hugs its natural width with generous padding.
  </action>
  <verify>.venv\Scripts\python.exe -m pytest tests</verify>
  <done>Output header reads "Run your code to see results"; Run & Submit button has natural width.</done>
</task>

*Coverage Lane C: X5R, X6, X7-Practice, X8, X9.*

---

### WAVE 2: EVIDENCE FAN-OUT & RETURN GATE (`/agency-evidence-collector`)
*Trigger: Initiates after Wave 1 lanes are merged, and orchestrator re-verifies 31/31 pytest and quarantine.*  
*Rule: Evidence subagents NEVER edit app.py.*

<task type="auto">
  <name>Lane D1: E6 — Authentic Mock Proof Battery</name>
  <files>scratch/run_mock_e2e_evidence.py, docs/screenshots/r6/</files>
  <action>
    - Skill: `/agency-test-automation-engineer` + `/empirical-validation`.
    - Capture store snapshots before and after mock run (verifying database records).
    - Capture in-session-solve scorecard proof (solving Problem 1 in-session, proving scorecard shows 1/2 Solved authentically).
    - Capture timer pair with $\ge 10$ seconds elapsed time delta proving live ticking countdown.
  </action>
  <verify>powershell -Command "Test-Path 'docs/screenshots/r6/mock_in_session_solve.png'"</verify>
  <done>E6 mock store snapshots, scorecard solve, and timer pair captured.</done>
</task>

<task type="auto">
  <name>Lane D2: E1 — Impeccable UI Audit Fan-Out</name>
  <files>docs/screenshots/r6/</files>
  <action>
    - Skill: `/impeccable`.
    - Run 4 parallel audit reviews across all live screens: Home, Practice, Mock Interview, Dashboard.
    - Confirm zero primary visual slop or alignment findings.
  </action>
  <verify>.venv\Scripts\python.exe scratch/run_r5_verification.py</verify>
  <done>Impeccable audits recorded for all 4 screens.</done>
</task>

<task type="auto">
  <name>Lane D3: E2, E8, E9 — Font Proof, Hint Ladder & Pill-Tint CDP Hexes</name>
  <files>docs/screenshots/r6/, docs/screenshots/r6/r6_measurements.json</files>
  <action>
    - Skill: `/agency-evidence-collector`.
    - E2 Font Proof: CDP computed style check proving Fraunces headings, Inter body, and JetBrains Mono code fonts render from offline base64.
    - E8 Hint Ladder: Empirical screenshot showing butter block statement and expander states.
    - E9 Pill-Tint CDP Hexes: Measure exact computed `background-color` and `color` hexes on Practice and Mock pills.
    - Multi-resolution captures across 1450×900, 1920×1080, and 1600×1000 stored in `docs/screenshots/r6/`.
  </action>
  <verify>powershell -Command "Get-ChildItem -Path 'docs/screenshots/r6' -Filter '*.png' | Measure-Object | Select-Object -ExpandProperty Count"</verify>
  <done>E2 font proof, E8 hint ladder capture, E9 pill-tint hexes, and r6 captures saved.</done>
</task>

<task type="auto">
  <name>Orchestrator: E3–E5 Synthesis, Pre-Return Gate & Return Filing</name>
  <files>.gsd/phases/2/IMPLEMENTATION_CORRECTIVE_RETURN.md, .gsd/phases/2/VERIFICATION.md</files>
  <action>
    - Run `/agency-ui-finish-gate-reviewer` over r6 captures for anti-slop and mockup fidelity.
    - Re-run `/verify 2` protocol across all 10 gates; record verdict.
    - Synthesize E3 (quarantine), E4 (full resource accounting including parked skills), and E5 (pytest baseline).
    - File `.gsd/phases/2/IMPLEMENTATION_CORRECTIVE_RETURN.md` with full measurement rule tables and proofs.
  </action>
  <verify>powershell -Command "Test-Path '.gsd/phases/2/IMPLEMENTATION_CORRECTIVE_RETURN.md'"</verify>
  <done>IMPLEMENTATION_CORRECTIVE_RETURN.md filed ending with exact STOP line.</done>
</task>

*Coverage Wave 2 / Lane D: E1, E2, E3, E4, E5, E6, E8, E9.*

---

## 4. Parked Skills Accounting (§E4)

The following skills are intentionally **PARKED** for this round with documented rationale:
- `agency-ai-engineer`, `agency-ai-generated-code-security-auditor`, `agency-application-security-engineer`, `agency-code-reviewer`, `agency-document-generator`, `agency-growth-hacker`, `agency-performance-benchmarker`, `agency-privacy-engineer`, `agency-prompt-engineer`, `agency-software-architect`, `agency-technical-writer`, `agency-ux-researcher`: Backend is strictly frozen; no surface for them in a UI corrective.
- `agency-git-workflow-master`: GSD executor atomic per-task commits cover git workflows.
- `agency-ui-designer`: Visual design already owner-approved at mockup gate.
- `brainstorming`, `grill-me`: Architectural and visual decisions already finalized in DECISION-011.
- `teamwork`, `boost`: Native GSD executor orchestrator is the chosen execution model.
- `debugger`: On standby; invoke only if a lane hits a defect.
- `codebase-mapper`: The discussion already mapped all app.py line bounds.
- `speckit-*`: GSD governs this project.
- `finishing-a-development-branch`: Owner live acceptance gate replaces it.
- `brand`, `banner-design`, `slides`: Parked design sub-skills without application code surface.
- `context-fetch`, `context-compressor`, `context-health-monitor`, `learn`, `automation`, `plugin`, `agy-customizations`, `antigravity-guide`, `generative_ui`, `graphify`, `migrate-workflows`, `diagnosing-superpowers`: Session utilities / no surface in this UI implementation round.

---

## 5. Item Coverage Matrix

| Scope Item | Description | Assigned Lane | Verification |
|---|---|---|---|
| **E7** | Disclose `build_app.py` under `scratch/`, establish `app.py` as single source of truth | Wave 0 | File path verified |
| **X1** | Kill top void, navbar sticky full-bleed at top: 0 | Wave 1 / Lane A | CDP top rect == 0 |
| **X2** | Remove static "3.11" chip; runtime-derived version text | Wave 1 / Lane A | Text matches `sys.version_info` |
| **X3** | Restore Plotly topic pass-rate horizontal chart (store data, attempted only) | Wave 1 / Lane B | Chart renders attempted topics |
| **X4** | Start Practice / Continue Practice as primary pill buttons | Wave 1 / Lane B | Rounded-full CTA styling |
| **X7-Home** | Exact mockup subtexts restored; `NOT STARTED` tag at streak 0 | Wave 1 / Lane B | Subtext match, badge text check |
| **X5R** | Filter strip deleted; ONE slim picker row (title + prev/next) | Wave 1 / Lane C | 0 filter dropdowns, 1 title row |
| **X6** | Starter signature unified to single source of truth (12/12 check) | Wave 1 / Lane C | 12/12 match editor starter code |
| **X7-Practice**| Output Card neutral header "Run your code to see results" | Wave 1 / Lane C | DOM text match |
| **X8** | "Run & Submit" button natural width (no full-width stretch) | Wave 1 / Lane C | Button width < container width |
| **X9** | Small-caps `STARTER FUNCTION SIGNATURE` label; code wash chips | Wave 1 / Lane C | Small-caps styling + pastel chips |
| **E1** | Impeccable ×4 live audits across all screens | Wave 2 / Lane D2 | Zero primary slop findings |
| **E2** | Font proof: Fraunces & Inter offline base64 rendering | Wave 2 / Lane D3 | Computed font family check |
| **E3** | Quarantine proof: `coach/`, `data/problems/`, `tests/` untouched | Wave 2 / Orchestrator | `git diff --stat` clean on frozen dirs |
| **E4** | Resource accounting table with parked skills documented | Wave 2 / Orchestrator | Complete return table |
| **E5** | Pytest baseline before line + final 31/31 green | Wave 0 & Wave 2 | 31 passed in pytest |
| **E6** | Mock proofs: store snapshots, in-session solve, $\ge 10$s timer pair | Wave 2 / Lane D1 | Evidence PNGs + JSON delta |
| **E8** | Hint ladder statement and empirical screenshot | Wave 2 / Lane D3 | Expander behavior capture |
| **E9** | Pill-tint CDP hex values measured for Practice and Mock | Wave 2 / Lane D3 | Computed background/color hexes |

*Total Coverage: 100% (All 10 X items and 9 §E items assigned to exactly one lane).*

---

## 6. Success Criteria

- [ ] Wave 0 gate passes: `build_app.py` disclosed under `scratch/`, Plotly import in place, pytest 31/31 green.
- [ ] Wave 1 completes in parallel:
  - Lane A: Top void eliminated (navbar sticky at top 0), runtime version chip active.
  - Lane B: Plotly pass-rate chart restored on Dashboard, primary pill CTAs on Home, mockup subtexts restored.
  - Lane C: Cluttered filter strip replaced by ONE slim picker row, signatures unified 12/12, neutral output header restored, natural width button, small-caps label.
- [ ] Wave 2 evidence fan-out captures all E1–E9 proof artifacts into `docs/screenshots/r6/`.
- [ ] Full suite 31/31 passes green; quarantine strictly preserved.
- [ ] Stop line reached:
  `Stopped at Topbar Workbench final corrective gate, awaiting owner live approval.`
