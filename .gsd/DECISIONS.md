# DECISIONS.md — Architecture Decision Records

> **Purpose**: Log significant technical and design decisions and their rationale.

---

## Decisions

### [DECISION-001] Design Direction Selection: Direction A (Brilliant-Style)

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
The original dark OLED theme was rejected by the owner as generic AI slop. An inspiring, polished visual identity was needed for the coding-interview practice platform.

#### Decision
Adopt Direction A: a colourful light learning app inspired by Brilliant. Key elements include warm paper canvas, rich ink typography with Fraunces serif headings and Inter sans-serif body, tinted pastel accent system per problem category, large rounded cards (16-24px), and pill-shaped action buttons.

#### Rationale
Creates an inviting, premium educational atmosphere that minimizes eye fatigue and feels intentional rather than boilerplate.

#### Consequences
Requires custom CSS injection and tailored component markup when translating to Streamlit in Phase 2.

---

### [DECISION-002] Two-Phase Implementation Gate

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
Risk of premature coding or unaligned visual rework in Streamlit before the aesthetic is validated.

#### Decision
Enforce a two-phase protocol:
- **Phase 1**: Produce static HTML/CSS mockups of all 4 views (Home, Practice, Mock, Dashboard) and a design token sheet. Capture screenshots and require explicit owner sign-off. Zero production application code changes allowed.
- **Phase 2**: Only after visual approval, implement the approved styling into the Streamlit app.

#### Rationale
Eliminates thrash in Streamlit code and ensures 100% aesthetic alignment before touching app files.

---

### [DECISION-003] Strict Backend and Problem Bank Freeze

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
The core backend execution sandbox, judge engine, spaced repetition scheduler, timer, and problem definitions are complete and tested (26 tests passing).

#### Decision
All files in `coach/*.py` and `data/problems/*.json` are strictly frozen. No refactoring, additions, or modifications are permitted.

#### Rationale
Ensures zero regression in working judge and evaluation functionality while focusing 100% of effort on the UI overhaul.

---

## Phase 1 Decisions

**Date:** 2026-11-05

### Scope
- **Visual Mockups Only**: Deliver static HTML mockups for Home, Practice, Mock, and Dashboard plus a Direction A Token Sheet.
- **Strict Code Quarantine**: Zero edits to `app.py`, `.streamlit/config.toml`, `coach/*.py`, `data/problems/*.json`, or `tests/`.
- **R3 Specification Integration**: Full Direction A tokens, area tint palette, typography rules (Fraunces/Inter/JetBrains Mono), and anti-slop rules will be injected directly from the owner's R3 handoff at planning.

### Approach
- **Authentic Content Grounding**: Mockups must display actual app data and signatures:
  - Daily streak: "1 day"
  - Spaced repetition queue: "0 due"
  - Total problem inventory: 12 problems
  - Solved problem: Binary Search PASS (178ms)
  - Active unsolved problem: Longest Substring Without Repeating Characters with genuine starter signature (`longest_substring(s: str) -> int`)
  - Mock countdown timer state: "44:41"
- **Dual-Resolution Evidence Capture**: Screen captures rendered and captured at both `1600x1000` (compact desktop) and `1920x1080` (full HD) for owner verification.

### Constraints & Finish Gate
- **Deliverable Gate**: Phase 1 is complete ONLY when the owner explicitly reviews and approves the rendered mockup screenshots. (PASSED: Approved by owner on 2026-11-05).
- **Zero Implementation**: No Streamlit code or application CSS is written until Phase 2 is unlocked following Phase 1 approval.

---

### [DECISION-004] Phase 1 Owner Acceptance & Phase 2 Directives

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
Owner completed live browser and dual-resolution screenshot inspection of the Direction A mockups (`mockups/` on port 8085, `docs/screenshots/r3/`) and officially approved Phase 1.

#### Directives for Phase 2 Implementation:
1. **Unattempted Topic Mastery Bars**: Dashboard mastery bars must use `"NOT STARTED"` for unattempted topics (matching the table), never `"0% (0/0)"`.
2. **Mock Screen Timer Redundancy**: The Mock view shows the countdown timer three times in various places — consolidate and reduce to two placements.
3. **Metric Numeral Typography**: The Fraunces zero glyph reads like a lowercase "o" in large metric values (e.g. `"0 problems"`) — evaluate Inter or tabular monospace figures for primary metric numerals during Streamlit implementation. Monospace for metric values subsequently BANNED in Phase 2 discussion.
4. **Button Whitespace Handling**: All button elements must strictly enforce `white-space: nowrap` with adequate horizontal padding to ensure labels never wrap unexpectedly on compact layouts.

---

### [DECISION-005] Phase 2 Implementation Architecture & Shell Gate Feasibility

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
Phase 2 translates the approved Direction A mockups into the real application. Before planning, the Shell Gate requires evaluating the feasibility of the mockups' four load-bearing elements in Streamlit 1.66.1 and locking implementation constraints.

#### Feasibility Recount (The 4 Load-Bearing Elements):
1. **Per-card tinted backgrounds in six washes**: `[bordered container]` + `[keyed CSS]` (FEASIBLE via `.st-key-<wash>_card [data-testid="stVerticalBlockBorderWrapper"] > div` and native `st.html()` card containers).
2. **Pill primary buttons**: `[config token]` + `[keyed CSS]` (FEASIBLE via `.streamlit/config.toml` `primaryColor = "#15803D"` + `button[kind="primary"], .stButton > button { border-radius: 999px; white-space: nowrap; padding: 10px 24px; }`).
3. **Tinted active-nav pill in the sidebar**: `[keyed CSS]` (FEASIBLE via `.st-key-nav_sidebar_radio` label pseudo-classes or `st.sidebar.pills` active indicator styled with wash `#DFF3E4` and ink `#167B48`).
4. **Fraunces headings + Inter body genuinely loading**: `[keyed CSS]` (FEASIBLE via self-hosted offline font files in `assets/fonts/` loaded through base64 `@font-face` / static serving; verified by automated computed-font proof task).

**Shell Gate Verdict**: 0 elements are `[impossible in Streamlit]`. The default Streamlit shell (`app.py`) is retained; no NiceGUI port required.

#### Locked Phase 2 Constraints:
1. **Backend & Data Freeze**: Absolute freeze on `coach/*.py`, `data/problems/*.json`, and `tests/*`. `app.py` modifications are strictly layout and presentation. All 26 pytest tests must pass before the first UI edit and after the last.
2. **Frozen Design Tokens**: Strict adherence to Phase 1 token sheet. Paper `#FBFAF7`, surface `#FFFFFF`, ink `#171712`, muted `#66635A`, hairline `#E7E1D6`, CTA green `#15803D`, 6 wash pairs, code dark inset `#14161A` / `#F2F2ED`.
3. **Offline Font Self-Hosting**: Fraunces, Inter, and JetBrains Mono self-hosted locally in `assets/fonts/`. No runtime Google Fonts CDN requests. Mandatory computed-font proof task using headless Chrome CDP to assert rendered font families.
4. **Lucide-Only Icons**: Icons copied exclusively from `agent-resources/lucide/icons` to `assets/icons/` and inlined. Material Symbols fallback allowed only if inlining is technically impossible, with each fallback individually listed in UI resource map. Zero emoji icons.
5. **Phase 1 Directives**:
   - (i) Unattempted topics display `NOT STARTED` everywhere, including mastery progress bars.
   - (ii) Mock timer rendered in exactly 2 places (header pill and in-card countdown).
   - (iii) Metric numerals A/B screenshot task generated during planning (Fraunces vs Inter semibold tabular) for owner selection before execution. Monospace for metric numerals is strictly BANNED.
   - (iv) All buttons enforce `white-space: nowrap` and adequate padding.
6. **CSS Budget**: Priority: Config tokens $\rightarrow$ Native components $\rightarrow$ Keyed CSS (`.st-key-*`). Global selectors strictly forbidden except for 3 named exceptions: `@font-face`, button `nowrap`, and metric numeral typography. All keyed instances cataloged in UI resource map.
7. **Visual Finish Gate**: Phase 2 completes only upon owner review and sign-off on real application screenshots.

---

### [DECISION-006] Offline Font Asset Acquisition & Inventory

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
To guarantee offline-readiness and eliminate runtime Google Fonts CDN requests without violating the frozen typography contract, binary font files were extracted directly into `assets/fonts/` following owner approval of Option A (NPM Fontsource extraction).

#### Sourced Packages & Versions:
- `@fontsource/fraunces@5.3.0`
- `@fontsource/inter@5.3.0`
- `@fontsource/jetbrains-mono@5.3.0`

#### Extracted Asset Inventory (Weights matching `mockups/style.css` @import exactly):
1. `fraunces-latin-500-normal.woff2` (18,000 bytes) — Header Display (Medium)
2. `fraunces-latin-600-normal.woff2` (18,096 bytes) — Header Display (SemiBold)
3. `fraunces-latin-700-normal.woff2` (18,212 bytes) — Header Display (Bold)
4. `fraunces-latin-800-normal.woff2` (18,224 bytes) — Header Display (ExtraBold)
5. `inter-latin-400-normal.woff2` (23,664 bytes) — UI / Body Regular
6. `inter-latin-500-normal.woff2` (24,272 bytes) — UI / Body Medium
7. `inter-latin-600-normal.woff2` (24,452 bytes) — UI SemiBold / Button text / Tabular Numerals
8. `inter-latin-700-normal.woff2` (24,356 bytes) — UI Bold
9. `jetbrains-mono-latin-400-normal.woff2` (21,168 bytes) — Code Inset Regular
10. `jetbrains-mono-latin-500-normal.woff2` (21,832 bytes) — Code Inset Medium
11. `jetbrains-mono-latin-600-normal.woff2` (21,860 bytes) — Code Inset SemiBold
12. `jetbrains-mono-latin-700-normal.woff2` (21,908 bytes) — Code Inset Bold

**Validation**: All 12 files verified with magic bytes `0x77 0x4F 0x46 0x32` (`b"wOF2"`).

---

### [DECISION-007] Metric Numeral Typography Selection: Variant B (Inter SemiBold 600 Tabular)

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
As required by Phase 1 Directive 3, the Home stat row numerals were evaluated empirically in dual variants (Variant A: Fraunces Display 700 vs Variant B: Inter SemiBold 600 with tabular figures) via a 1920×1080 headless Chrome screenshot (`docs/screenshots/r3/metrics_ab_eval.png`). In Variant A, the Fraunces circular zero glyph in "0 due" read ambiguously as a lowercase "o".

#### Decision
Project owner explicitly selected **Variant B (Inter SemiBold 600 with tabular figures)** for all primary metric numeral values across the application:
- Home stat cards (`Active Streak`, `Problems Due Today`, `Total Problem Bank`)
- Dashboard stat cards (`Solved Problems`, `Practice Sessions`, `Average Hints Used`)
- Sidebar summary mini-card (`Active Streak`, `Due for Review`)

#### Typography Rules:
- Metric numerals: `font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-variant-numeric: tabular-nums !important; letter-spacing: -0.025em;`
- Headings and card title labels: strictly retain **`Fraunces`**.
- Unchosen variant CSS (Variant A metric styling): deleted from all stylesheets (no dead CSS).

---

*Last updated: 2026-11-05*

