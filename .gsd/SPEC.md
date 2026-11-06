# SPEC.md — Project Specification

> **Status**: `MILESTONE 3 REGISTERED`
>
> ⚠️ **Milestone Invariants**: Milestone 1 complete & verified; Milestone 2 Phase 3 complete & verified (awaiting owner live acceptance); Milestone 3 defined.

---

## Vision
AI Coding Prep Coach is a local, zero-cost coding-interview practice platform built with Streamlit.

- **Milestone 1 (Complete)**: Transformed the visual experience from an uninspired dark UI into a warm, delightful, Brilliant-style light learning environment ("Direction A") featuring a warm paper background, ink typography (Fraunces headings + Inter body), pastel topic tints, tactile rounded cards, and pill buttons.
- **Milestone 2 (Phase 3 Verified)**: "Make the Loop Smarter." Upgrades the learning engine with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review intervals with individualized memory modeling and interleaving problem topics to optimize retention for coding interviews.
- **Milestone 3 (Current Target)**: "Terracotta Editorial Redesign." Redesigns the visual identity and layouts into Option 3 — **TERRACOTTA EDITORIAL**, combining the "Terracota Mediterrâneo" color architecture with a "Bento Grid Tech Minimalist" layout structure, disciplined by strict frontend feasibility, matte surfaces, and 100% authentic data truth.

---

## Milestone 1: Premium UI Redesign (Status: Complete / Verified)
1. **Design System & Token Specification** — Direction A design tokens established in `DESIGN.md`.
2. **Phase 1: High-Fidelity Static Mockups** — Standalone HTML mockups and dual-resolution captures approved.
3. **Phase 2: Streamlit Theme & UI Implementation** — Topbar workbench and responsive layout implemented, 10/10 verification gates passed, verified 31/31 pytest.

---

## Milestone 2: Make the Loop Smarter

### Phase 3: FSRS + Interleaving (Status: Verified — Awaiting Owner Live Acceptance)
- **Workstream 1 (FSRS Scheduler Swap)**: Pinned `fsrs==6.3.2`, SQLite card persistence in `problem_fsrs_cards`, 3-rule rating mapping with `Rating.Easy` ban, default parameters (`desired_retention = 0.9`, optimizer forbidden), idempotent migration with A1 last-attempt timestamps, ladder retired from write path (0 callers), truth-in-copy updated.
- **Workstream 2 (Cognitive Interleaving)**: `build_interleaved_queue` non-adjacent topic sequencing weighted by due count and weakest pass rate. Free picking in Practice Arena preserved.
- **Verification**: 57 passed tests in 17.22s, live 1450×900 CDP proof captured.

### Milestone 2 Backlog (Later Phases)
1. **Phase 4: Per-Run Resource Measurement**: Peak memory allocation and precise CPU execution time instrumentation inside the judge runner; generates trustworthy execution speed signals to unlock `Rating.Easy`.
2. **Phase 5: Attempt History & Ruff Diagnostics Panel**: Historical timeline of attempts with diff view, code evolution, and live Ruff lint/style feedback in the Practice Arena.

---

## Milestone 3: Terracotta Editorial Redesign

### Design Tokens & Color Architecture (Option 3 — Binding)
- **Canvas / Paper**: Sun-white `#FFF8F0`.
- **Quiet Panel / Tile**: Sandy beige `#E8D5B7` (used sparingly, never as full page background).
- **Primary Action / Terracotta**: `#C2452D` (primary CTAs, active nav underline/indicator).
- **Success / Streak / PASS Zone**: Olive `#6B7F3B` (PASS badges, streak counters).
- **Info / Mock / Links Zone**: Mediterranean blue `#1565C0` (mock interview badges, links).
- **Secondary Warm Accent**: Clay `#D4956B`.
- **Deep Accent**: Deep fig `#4A1942` (used sparingly).
- **Fresh Accent**: Sea foam `#A8D8C8` (used sparingly).
- **Typography**:
  - Display headlines & wordmark: DM Serif Display.
  - Body & UI: Humanist sans (self-hosted in `assets/fonts/`).
  - Code, editor strip, mock timer: JetBrains Mono only.
  - Metric numerals: Inter-style tabular semibold per DECISION-007 (never monospace).
- **Surfaces & Borders**:
  - Matte surfaces only.
  - Borders over shadows: 1px warm hairlines at low alpha.
  - Card radius: 24px per approved bento renders.
  - Flat color only.
- **Strict Bans (Stripped from source)**:
  - Banned: golden-hour gradients, plaster/stone textures, arch-shaped containers, cinematic/entrance motion, glass, glow, shimmer, independent pane scrolling.
  - Allowed motion: hover/press states only (~150ms ease-out, press scale 0.97).
- **Color Jobs**:
  - Terracotta: primary actions + active nav underline/state.
  - Olive: success, PASS, streak.
  - Blue: info, mock interview, links.
  - Sandy: quiet explanatory panels (hint/format/summary strips).
  - Fig / Clay / Sea-foam: accents only, never competing primaries.
  - Verdicts: PASS olive (`#6B7F3B`), FAIL terracotta-red (`#C2452D`), TIMEOUT/NOT ATTEMPTED neutral gray.

### Screen Layouts & Bento Structure
- **Home**: Serif "Today's Practice" headline, terracotta primary pill, 3 stat tiles, de-slopped queue panel (max 1 status pill per row; track/difficulty as colored text).
- **Practice Arena**: Page-scroll two-pane workbench (no independent scroll), 1 Problem Card + 1 Output Card, slim picker row (X5R), dark anchor editor card (iframe internals untouched).
- **Mock Interview**:
  - Start screen: serif title, sandy format panel with real facts (45 min, 2 problems, hints allowed), terracotta Start, timer card at 45:00.
  - Session screen: sandy session band, mono timer with exactly 2 display places.
  - Scorecard: PASS olive / FAIL blue-or-terracotta, sandy summary strip, terracotta Download Report, outline Back to Home.
- **Dashboard**: Bento tiles + restored Plotly "Topic Mastery & Pass Rates" chart ABOVE table, data strictly from `store.topic_stats()`, attempted topics only, unattempted = NOT STARTED in table; chart colors from Terracotta zone palette.

### Absolute Preservations
- Full-bleed sticky topbar at top: 0.
- Navbar right side: streak + due chips only (version chip status reported, not changed).
- Picker-only Practice selection.
- Signature single-source-of-truth (`starter_code` first line).
- Natural-width right-aligned Run & Submit buttons.
- Small-caps signature label (`STARTER FUNCTION SIGNATURE`).
- Wash-chip inline code.
- Mock session scoping and timer invariants.
- Truthful copy: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
- Freezes: `coach/*.py`, `data/problems/*.json`, `tests/*` 100% frozen; 57/57 tests green.
- Data Truth: All numbers, metrics, problem lists from real store and real 12 problems; 0 generator fiction.

### Milestone 3 Phases
- **Phase 6: Terracotta Static Mockups & Token Sheet (T1)**: Static HTML mockups for all 6 screens + tokens page with real data; 1450×900 PRIMARY and 1920×1080 secondary captures; anti-slop audit. STOP for owner approval. No app code.
- **Phase 7: Terracotta Streamlit Implementation (T2)**: Streamlit implementation with keyed-container CSS (`.st-key-*`) and native theme; self-hosted fonts in `assets/fonts/`; full verification battery and CDP DOM measurements.

---

## Entry Gates
- **Gate G-T1**: Phase 6 static HTML mockups and token sheet approved by owner.
- **Gate G-M2**: Milestone 2 Phase 3 live acceptance granted by owner.
- **Gate G-EXEC**: Phase 7 execution authorized only after G-T1 and G-M2 (or explicit chat override).

---

*Last updated: 2026-11-07*
