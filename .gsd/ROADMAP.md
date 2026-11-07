---
milestone: Milestone 3 — Terracotta Editorial Redesign
version: 3.0.0
updated: 2026-11-07
---

# ROADMAP.md

> **Current Milestone**: Milestone 3 — Terracotta Editorial Redesign  
> **Current Phase**: Phase 7: Terracotta Streamlit Implementation (T2)  
> **Status**: ✅ Phase 7 Complete — Phase Return Filed

---

## Milestone 1: Premium UI Redesign (Status: ✅ Complete / Verified)

- [x] Phase 1: Static HTML Mockups & Design Tokens
- [x] Phase 2: Streamlit UI Implementation (10/10 Verification Gates Passed, Return Filed)

---

## Milestone 2: Make the Loop Smarter (Status: Complete — accepted with corrective (2026-11-07))

### Goal
Upgrade the learning loop with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review ladders with individualized memory modeling and non-adjacent topic sequencing to optimize retention.

### Must-Haves
- [x] **Dependency Gate**: `fsrs==6.3.2` installed and pinned in `requirements.txt`.
- [x] **FSRS Scheduler Swap (Workstream 1)**:
  - FSRS card state persistence table in SQLite (`coach.db`).
  - Strict judge-to-rating mapping (`Again`, `Hard`, `Good`; `Easy` omitted).
  - Default parameters with `desired_retention = 0.9` (optimizer forbidden).
  - Zero-loss, idempotent migration from historical attempts on DB copy with A1 last-attempt timestamps.
  - Retirement of old ladder function from scheduling path (0 callers).
  - Truth-in-copy: replace 21-day schedule text on Home with FSRS explanation.
- [x] **Interleaved Review Queue (Workstream 2)**:
  - Review and mock queue generators forbid adjacent same-topic problems when alternatives exist.
  - Topic sampling weighted by due-ness first, then weakest topic pass rate.
  - Free problem picker in Practice Arena remains untouched.
- [x] **Empirical Verification Suite**:
  - Rating mapping unit tests covering all outcome branches (15 tests).
  - Database migration idempotency and correctness tests.
  - Due-set equivalence check between old ladder and FSRS.
  - Interleaving adjacency test on multi-topic problem sets.
  - All 57 tests green in 17.22s.
  - Live 1450×900 browser capture of Home screen showing FSRS due chip and queue.

### Phases
- **Phase 3: FSRS + Interleaving** — Status: Complete — accepted with corrective (2026-11-07)
- **Phase 4: Per-Run Resource Measurement** (Milestone 2 Backlog) — Peak memory + CPU execution time instrumentation inside judge runner; unlock `Rating.Easy`.
- **Phase 5: Attempt History & Ruff Diagnostics Panel** (Milestone 2 Backlog) — Historical attempt timeline, code diffs, inline Ruff linting.

---

## Milestone 3: Terracotta Editorial Redesign

### Goal
Redesign the application visual identity and layouts into Option 3 — **TERRACOTTA EDITORIAL**, combining the "Terracota Mediterrâneo" color architecture with a "Bento Grid Tech Minimalist" layout structure, disciplined by strict frontend feasibility, matte surfaces, and 100% authentic data truth.

### Must-Haves
- [x] **Design Tokens & System Sheet**:
  - Sun-white `#FFF8F0` canvas / paper.
  - Sandy beige `#E8D5B7` quiet panel / tile (used sparingly, never as page background).
  - Primary action / terracotta `#C2452D`.
  - Success / streak / PASS zone: olive `#6B7F3B`.
  - Info / mock / links zone: Mediterranean blue `#1565C0`.
  - Secondary warm accent: clay `#D4956B`.
  - Deep accent (sparing): deep fig `#4A1942`.
  - Fresh zone accent (sparing): sea foam `#A8D8C8`.
  - Typography: DM Serif Display for headlines/wordmark; Plus Jakarta Sans for body/UI (named self-hosted family); JetBrains Mono ONLY for code, editor strip, mock timer.
  - Surfaces: matte only; 1px warm hairlines at low alpha (borders over shadows); card radius 24px; flat colors only.
  - Strict bans: golden-hour gradients, plaster/stone textures, arch-shaped containers, entrance animations, glass, glow, shimmer, independent pane scrolling.
  - Motion: hover/press states only (~150ms ease-out, press scale 0.97).
- [x] **Screen Layouts & Bento Structure**:
  - **Home**: Serif "Today's Practice" headline, terracotta primary pill, 3 stat tiles, de-slopped queue panel (max 1 status pill per row, track/difficulty as colored text).
  - **Practice Arena**: Page-scroll two-pane workbench, 1 Problem Card + 1 Output Card, slim problem picker row (Round 2 format), dark anchor editor card (iframe internals untouched).
  - **Mock Interview**: Start screen (serif title, sandy format panel with real facts, terracotta Start, timer card at 45:00), session screen (sandy session band, mono timer with exactly 2 display places), scorecard (PASS olive / FAIL terracotta, sandy summary strip, terracotta Download Report, outline Back to Home).
  - **Dashboard**: Bento tiles + restored Plotly "Topic Mastery & Pass Rates" chart ABOVE the table, data strictly from `store.topic_stats()`, attempted topics only, unattempted = NOT STARTED in table; chart colors from Terracotta zone palette.
- [x] **Preservations & Freezes**:
  - All Phase 2 corrective outcomes stay (full-bleed sticky topbar at top 0, navbar right side streak + due chips only, picker-only Practice selection, signature single source of truth, natural-width Run & Submit, small-caps signature label, mock session scoping & timer invariants, truthful FSRS copy).
  - Strict freezes: `coach/*.py`, `data/problems/*.json`, `coach.db` pre-existing tables untouched; pytest 71/71 passing.
  - Allowed edit surface: `app.py` presentation layer, `.streamlit/config.toml` theme, `DESIGN.md` (Terracotta token sheet), `assets/fonts/` (self-hosted), mockups/screenshots.
  - Data Truth: 100% authentic data from store at runtime; 12 real problems; zero generator fiction, zero invented numbers/counts.
- [x] **Phase Shape & Execution Split**:
  - **Phase 6 (T1)**: Static HTML mockups & token sheet FIRST (Home, Practice, Mock start, Mock session, Mock scorecard, Dashboard, Tokens, Login); captures at 1450×900 PRIMARY and 1920×1080; anti-slop audit. Complete & approved.
  - **Phase 7 (T2)**: Streamlit implementation with keyed-container CSS (`.st-key-*`) + native theme; zero `.st-emotion-cache-*` selectors; self-hosted fonts in `assets/fonts/` with base64 `@font-face` injection; functional auth gate in `auth_store.py`. Complete & verified.
- [x] **Verification & Skills Accounting**:
  - All 71 tests passing.
  - Chrome CDP captures across all 7 screens at 1450×900 and 1920×1080 (14 images, 0 horizontal overflow).
  - Automated anti-slop audit: 0 violations, live numerals traced to SQLite.
  - Full resources exercised accounting block filed in `PHASE_RETURN.md`.

---

## Phases

### Phase 1: Static HTML Mockups & Design Tokens
**Status**: ✅ Complete  
**Objective**: Build pixel-perfect static HTML/CSS mockups of Home, Practice, Mock, and Dashboard along with a design token sheet implementing Direction A.

---

### Phase 2: Streamlit UI Implementation
**Status**: ✅ Complete / Closed (Owner Live Approved)  
**Objective**: Implement approved Direction A topbar workbench, responsive layouts, Plotly dashboard chart, slim picker row, and design tokens in Streamlit. 10/10 verification gates passed, pytest 31/31. Formal live approval granted 2026-11-07.

---

### Phase 3: FSRS + Interleaving
**Status**: Complete — accepted with corrective (2026-11-07)  
**Objective**: Replace the deterministic 1/1/3/7/21-day review ladder with py-fsrs adaptive spaced repetition and implement cognitive topic interleaving for review and mock queues. 64/64 pytest passed.

---

### Phase 4: Per-Run Resource Measurement (Milestone 2 Backlog)
**Status**: ⏳ Backlog  
**Objective**: Peak memory allocation and CPU execution time instrumentation inside judge runner; unlock `Rating.Easy`.

---

### Phase 5: Attempt History & Ruff Diagnostics Panel (Milestone 2 Backlog)
**Status**: ⏳ Backlog  
**Objective**: Historical attempt timeline, diff view, and live Ruff linting in Practice Arena.

---

### Phase 6: Terracotta Static Mockups & Token Sheet (T1)
**Status**: ✅ Complete (Owner Approved Mockups, Rounds 1–2 + Fix Round)  
**Objective**: Author `DESIGN.md` Terracotta token sheet, build 7 static HTML mockups using real problem and store data, conduct anti-slop audit, and capture 1450×900 & 1920×1080 proofs for owner approval before any app code.

---

### Phase 7: Terracotta Streamlit Implementation (T2)
**Status**: ✅ Complete (Phase Return Filed, 71/71 Tests Green, 14 CDP Captures)  
**Objective**: Implement approved Terracotta Editorial theme, DM Serif Display & Plus Jakarta Sans typography, 24px bento cards, terracotta primary actions, olive/blue/sandy color zones, Plotly terracotta palette, and functional authentication with real email confirmation into Streamlit.

---

## Progress Summary

| Milestone | Phase | Status | Objective |
| :--- | :--- | :--- | :--- |
| **M1** | Phase 1 | ✅ Complete | Static HTML mockups & Direction A tokens |
| **M1** | Phase 2 | ✅ Complete | Streamlit UI implementation & 10-gate audit |
| **M2** | Phase 3 | Complete — accepted with corrective (2026-11-07) | FSRS scheduler swap & interleaved review queue |
| **M2** | Phase 4 | ⏳ Backlog | Per-run memory & CPU resource measurement |
| **M2** | Phase 5 | ⏳ Backlog | Attempt history timeline & live Ruff diagnostics |
| **M3** | Phase 6 | ✅ Complete | Terracotta static HTML mockups & token sheet (T1) |
| **M3** | Phase 7 | ✅ Complete | Terracotta Streamlit implementation & Auth (T2) |

---

*Last updated: 2026-11-07*
