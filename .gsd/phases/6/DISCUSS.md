# Phase 6 Discussion: Terracotta Static Mockups & Token Sheet (T1)

**Milestone**: Milestone 3: Terracotta Editorial Redesign  
**Phase**: Phase 6: Terracotta Static Mockups & Token Sheet (T1)  
**Date**: 2026-11-07  
**Status**: Discussed & Scope Locked — Ready for `/plan 6`  
**Source Contract**: Block T (`MILESTONE-3-TERRACOTTA-BLOCK.md`)  

---

## 1. Milestone Relationship & Pre-Conditions

1. **Milestone 2 Invariance**:
   - Milestone 2 Phase 3 (FSRS + interleaving) is EXECUTED and VERIFIED (57/57 tests green, return filed, Gate G1 closed).
   - Milestone 2 is NOT cancelled, NOT rewritten, and NOT renumbered.
   - Milestone 2 backlog (Phase 4: Resource Measurement, Phase 5: Attempt History + Ruff) remains intact in `TODO.md` and `ROADMAP.md`.
2. **Milestone 3 Registration**:
   - Milestone 3 is registered as "Milestone 3: Terracotta Editorial Redesign".
   - Next free phase numbers assigned:
     - **Phase 6**: Terracotta Static Mockups & Token Sheet (T1) — *Current Phase*
     - **Phase 7**: Terracotta Streamlit Implementation (T2) — *Gated*
3. **Execution Gate**:
   - Phase 6 (T1) authorises DISCUSS + PLAN + MOCKUP BUILD now.
   - Phase 7 (T2 Streamlit implementation) execution starts ONLY after owner live acceptance of Phase 3 AND owner approval of Phase 6 mockups.
   - No application code (`app.py`, `coach/*.py`) may be touched in Phase 6.

---

## 2. Style Direction & Owner Decision

- **Approved Direction**: Option 3 — **TERRACOTTA EDITORIAL**.
- **Foundational Sources**: `designmd.app` "Terracota Mediterrâneo" color architecture + "Bento Grid Tech Minimalist" layout structure, disciplined by strict frontend feasibility and authentic data truth.
- **Generator Fiction Ban**: The 6 AI style renders shown to the owner are style direction only. All figures, percentages, problem counts, code snippets, and metrics are generator fiction.
- **Data Truth Rule**: Mockups and code must use ONLY the app's real data and real problem bank (12 problems). No owl, no Duolingo marks, no copied brand assets.

---

## 3. Design Token Architecture (Binding)

### Color Architecture
- **Canvas / Paper**: Sun-white `#FFF8F0`
- **Quiet Panel / Tile**: Sandy beige `#E8D5B7` (used sparingly for explanatory/summary panels, never as full page background)
- **Primary Action / Terracotta**: `#C2452D` (primary buttons, active nav underline/indicator)
- **Success / Streak / PASS Zone**: Olive `#6B7F3B` (PASS badges, streak counters)
- **Info / Mock / Links Zone**: Mediterranean blue `#1565C0` (mock interview badges, links)
- **Secondary Warm Accent**: Clay `#D4956B`
- **Deep Accent**: Deep fig `#4A1942` (sparingly)
- **Fresh Zone Accent**: Sea foam `#A8D8C8` (sparingly)

### Color Jobs
- `Terracotta (#C2452D)`: Primary CTAs, active nav tab indicator, high-priority interactive states.
- `Olive (#6B7F3B)`: Success badges, PASS verdicts, streak icons and values.
- `Mediterranean Blue (#1565C0)`: Info alerts, mock interview mode styling, external links.
- `Sandy Beige (#E8D5B7)`: Quiet panels, format fact strips, session timer bands, summary cards.
- `Clay / Deep Fig / Sea Foam`: Decorative accent boundaries and charts only; never competing primaries.
- `Verdict Matrix`:
  - `PASS`: Olive (`#6B7F3B`)
  - `FAIL`: Terracotta / deep rust (`#C2452D`)
  - `TIMEOUT / NOT ATTEMPTED`: Neutral warm gray

### Typography System
- **Display Headlines & Wordmark**: DM Serif Display (warm, editorial serif).
- **Body & General UI**: Humanist Sans (e.g. Plus Jakarta Sans or Source Sans 3; self-hosted in `assets/fonts/`).
- **Code, Editor Strip & Mock Timer**: JetBrains Mono ONLY.
- **Metric Numerals**: Inter-style tabular semibold per DECISION-007 (never monospace numerals).

### Surfaces & Styling
- **Surfaces**: Matte surfaces only; flat colors.
- **Borders over Shadows**: 1px warm hairlines at low alpha (`rgba(74, 25, 66, 0.08)` / warm clay border). No drop shadows or heavy blur.
- **Card Geometry**: 24px corner radius per the approved Bento renders.
- **Strict Bans (Stripped from source)**:
  - Banned: golden-hour gradients, plaster/stone textures, arch-shaped containers, cinematic/entrance motion, glass, glow, shimmer, independent pane scrolling.
  - Motion: hover/press states only (~150ms ease-out, press scale 0.97).

---

## 4. Screen-by-Screen Structure

1. **Home Screen**:
   - Serif "Today's Practice" display headline.
   - Terracotta primary pill CTA ("Start Practice" / "Continue Review").
   - 3 Bento stat tiles (Streak in Olive, Problems Due in Terracotta/Olive, Problems Solved in Warm Ink).
   - De-slopped daily queue panel: max ONE status pill per row; topic and difficulty rendered as colored text.
   - Truthful copy: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
2. **Practice Arena**:
   - Page-scroll two-pane workbench (no independent pane scroll).
   - Left: ONE Problem Card with slim picker row (X5R), small-caps signature label (`STARTER FUNCTION SIGNATURE`), wash-chip inline code.
   - Right: Dark anchor editor card (iframe internals NOT restyled) + ONE Output Card with natural-width right-aligned Run & Submit.
3. **Mock Interview**:
   - **Start Screen**: Serif headline, sandy format panel with real facts (45 minutes, 2 problems, hints allowed), terracotta Start button, timer card previewing 45:00.
   - **Session Screen**: Sandy session band, mono timer with exactly TWO display places (`MM:SS`), candidate problem toggle.
   - **Scorecard Screen**: PASS in olive / FAIL in terracotta, sandy summary strip with actual session statistics, terracotta "Download Report" button, outline "Back to Home" button.
4. **Dashboard**:
   - Bento metric tiles.
   - Restored Plotly "Topic Mastery & Pass Rates" chart positioned ABOVE the problem table.
   - Chart palette drawn strictly from Terracotta zone palette (olive, terracotta, blue, clay, sea foam).
   - Problem table: data exclusively from `store.topic_stats()`; attempted topics only; unattempted = `NOT STARTED`.

---

## 5. Non-Negotiable Preservations & Freezes

- **Phase 2 Corrective Invariants**:
  - Full-bleed sticky topbar at `top: 0`.
  - Navbar right side: streak + due chips only.
  - Picker-only Practice selection.
  - Signature single-source-of-truth (`starter_code` first line).
  - Natural-width right-aligned Run & Submit buttons.
  - Wash-chip inline code.
  - Mock session scoping & timer invariants from Addendum A.
- **Backend Freezes**:
  - `coach/*.py`, `data/problems/*.json`, `tests/*` strictly frozen.
  - Pytest suite invariant at 57/57 passing.
- **Data Truth Invariant**:
  - All mockups and screens use the owner's real runtime data (2 attempts, 1 solved, current streak, real 12 problem bank).
  - Zero placeholder percentages, zero sample rows, zero invented counts.

---

## 6. Phase 6 (T1) Deliverables & Capture Set

1. **Token Sheet**: Update `DESIGN.md` with complete Terracotta Editorial tokens.
2. **Static HTML Mockups** in `mockups/terracotta/`:
   - `home.html`
   - `practice.html`
   - `mock_start.html`
   - `mock_session.html`
   - `mock_scorecard.html`
   - `dashboard.html`
   - `tokens.html`
   - `style.css`
3. **Anti-Slop Audit Checklist** (Run BEFORE any capture):
   - [ ] No chip soup (max 1 pill per row in tables/queues).
   - [ ] No invented figures (100% real data from store and problems).
   - [ ] No gradients, glass, glow, or textures.
   - [ ] No serif body text (DM Serif Display for headlines only).
   - [ ] No monospace numerals in metric tiles.
4. **Dual-Resolution CDP Captures**:
   - Primary: 1450 × 900 (owner's native test viewport).
   - Secondary: 1920 × 1080.
5. **Phase Gate**: STOP for owner mockup and token sheet approval. No application code in T1.

---

## 7. Resources Exercised Gate Accounting

| Resource | Scope / Status | Pre-Execution Gate |
| :--- | :--- | :--- |
| `Lucide Icons` | `agent-resources/lucide` | **FOUND / AVAILABLE** |
| `designmd.app Terracota & Bento` | `agent-resources/awesome-design-md` | Specific files MISSING; token specifications fully provided in Block T contract |
| `/ui-ux-pro-max` | UI design intelligence & token reasoning | Available for token refinement |
| `/ui-styling` | CSS token architecture & component styling | Available for mockup CSS |
| `/design-system` | Design tokens & component specifications | Available for `DESIGN.md` authoring |
| `/design` | Visual identity & layout design | Available for bento layouts |
| `/brand` | Brand consistency & tone | Available for editorial typography |
| `/impeccable` | Design critique & anti-slop detection | Available for mockup review |
| `/agency-frontend-developer` | Implementation of HTML/CSS mockups | Active in Phase 6 |
| `/agency-ui-finish-gate-reviewer` | Pre-return audit of captured mockups | Active before Phase 6 return |
| `/empirical-validation` | Data-truth and measurement proofs | Active for CDP captures |
| `developing-with-streamlit` | Streamlit guidance | Parked for Phase 6 (mockups only); available for Phase 7 |

---

## 8. Next Action
Proceed to `/plan 6` to create execution plans `00-PLAN.md` through `04-PLAN.md` for Phase 6 (T1).
