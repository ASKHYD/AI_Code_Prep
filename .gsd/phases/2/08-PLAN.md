# Phase 2 Wave 8 Plan: Topbar Workbench Implementation

> **Phase:** Phase 2 (Milestone 1 — UI Redesign)  
> **Wave:** 08 — Topbar Workbench Implementation (Replacing Superseded Waves 00–07)  
> **Source Contract:** Owner Approved Mockups (`mockups/topbar/` + `style.css` closed 2026-11-06 after Corrective-2)  
> **Governing System:** Direction A (Brilliant Light)  
> **Quarantine Boundary:** `coach/*.py`, `data/problems/*.json`, `tests/*` strictly frozen (31/31 pytest suite untouched)

---

## Objective
Implement the owner-approved Topbar Workbench redesign in the live Streamlit application (`app.py`), replacing the superseded sidebar and stacked-card layout. The static mockups in `mockups/topbar/` serve as the visual ground truth, governed by Addendum A for the Mock Interview module.

---

## Tasks

### Task 1: W1 — Shell Architecture (Navbar Replaces Sidebar)
- Remove the sidebar from layout flow entirely (`initial_sidebar_state="collapsed"` or CSS suppression), reclaiming ~450px for content.
- Implement the slim Topbar Navbar as a keyed container on all 4 screens:
  - Left: Fraunces serif wordmark "AI Coding Prep Coach" + outlined pill "Offline · Code-Judged".
  - Center: Nav pills (Home / Practice Arena / Mock Interview / Dashboard) routing via `?screen=` with area-specific active tint washes (`NAV_TINTS`).
  - Right: Streak chip (Lucide flame + "N days", mint) and due chip (Lucide calendar + "N due", sky) driven by the authentic `CoachStore` metrics.
- CSS Budget: Global selectors restricted to `@font-face`, button nowrap, metric-numeral tabular fonts, sidebar removal, and navbar frame; all other element styling is strictly keyed (`.st-key-*`).
- Append layout amendment to `DESIGN.md` recording "Topbar Workbench — APPROVED 2026-11-06".

### Task 2: W2 — Home Screen ("Today's Practice" & De-slopped Queue)
- Update page heading H1 to "Today's Practice".
- Stat cards matching `mockups/topbar/home.html`: Active streak preserves "Not Started" at 0; decorative badges `READY` and `BANK` removed.
- Daily Practice Queue table redesigned: maximum ONE status pill per row; track (`DSA` lilac `#5932EA`, `Python` butter `#9A3412`) and difficulty (`Easy` green `#167B48`, `Medium` coral `#B93815`) rendered as plain text typography; Fraunces 600 titles, muted Inter subtext, 3px left track accent bars on hover, and reactive `"Practice →"` button that fills CTA green on hover.

### Task 3: W3 — Practice Arena (Two-Pane Workbench: One Problem Card + One Output Card)
- Recompose Practice screen into two columns at ~42/58 ratio:
  - Left Column: Filter strip at head (Track, Difficulty, Topic, Problem selects in one row); followed by **ONE Problem Card** containing Title $\rightarrow$ Chips $\rightarrow$ Description $\rightarrow$ Preformatted Comma-Broken Signature $\rightarrow$ Inputs $\rightarrow$ Outputs; followed by the **Hint Ladder** below as a separate butter block.
  - Right Column: **Editor Card** with header strip ("SOLUTION EDITOR · PYTHON" / "Sandbox · 3.0s · Python 3.12", no window dots), Ace code editor locked at height `"450px"`, and glued action row ("Clean environment · Network disabled" + "Run & Submit"); followed directly by **ONE Output Card** (neutral state before run; verdict band header strip + visible test cases with live results after run).
- Ace editor: soft-wrap OFF, fontSize 13, fitting longest 79-char starter signature (`log-timestamp-filter`) on one line with 0 horizontal overflow.

### Task 4: W4 & Addendum A — Mock Interview Module
- Sub-strip header directly beneath navbar: problem tabs ("Problem 1: <real title>" / "Problem 2: <real title>", active peach) + countdown timer pill (peach wash, Lucide timer icon, JetBrains Mono numerals).
- Workspace mirrors Practice (Problem Card left, Editor Card + Output Card right) with per-problem session-state keys preserving independent editor text, revealed hints, and run states.
- Start Screen: no 40% void; Simulation Rules & Evaluation Protocol card fills space; Past Sessions rendered only when store contains mock sessions.
- Timer Invariants: single source of truth (`session_start_iso` + duration); countdown computed on render; ticking via `@st.fragment(run_every=1)`; displayed in exactly two places (sub-strip during interview, scorecard header after end).
- Scoring Invariants: results scoped strictly by `mode == 'mock'` AND `created_at >= session_start_iso`; zero hardcoded verdicts or runtimes; grep proof of no `'178'` literal in mock code paths.
- End Screen: Scorecard with session-scoped results and Markdown export.

### Task 5: W5 — Performance Dashboard (De-slopped Topic Table & 80% Threshold)
- Stat cards (Solved / Sessions / Avg hints) matching approved `dashboard.html` with decorative badges `RECORDED` and `ZERO HINTS` removed.
- Topic Mastery Bars: `binary-search` at 100.0% (1/1); unattempted topics labeled `NOT STARTED` with no bar and no percentage.
- Topic Breakdown Table: de-slopped with maximum one status pill per row and track as colored plain text typography.
- Resolve "Target Threshold: 80%": investigate codebase and documentation for authentic source; cite or remove text.

### Task 6: W6 — Motion & Verification Battery
- Implement surviving keyed CSS motion: nav pill transitions (160ms), stat-card and queue-row hover lift/accent, button hover/press, verdict entrance keyframe (240ms), editor `:focus-within` ring (`rgba(89, 50, 234, 0.40)`), queue action button fill (160ms).
- Explicitly drop [mockup-only] items (Problem/Output card hover lifts) without faking.
- Quality Gates:
  1. Full pytest suite 31/31 passed green.
  2. Quarantine proof (`git diff --stat`): zero changes in `coach/`, `data/problems/`, `tests/`.
  3. Hex drift: zero unapproved hexes vs 26 Direction A tokens.
  4. Impeccable UI Audit: 0 primary findings across all live rendered screens.
  5. Computed-font verification (Fraunces headings, Inter body, JetBrains Mono code).
  6. CDP captures at 1450×900 (primary), 1920×1080, and 1600×1000 in `docs/screenshots/r5/`.
  7. Side-by-side comparison vs r4 mockups.
  8. Measurement Rule verification.
  9. Addendum A Mock E2E proofs (scenarios a–d).
  10. `/verify 2` phase verification and file `VERIFICATION.md`.

