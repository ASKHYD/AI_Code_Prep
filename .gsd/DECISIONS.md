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

### [DECISION-008] Phase 2 Corrective Round Resolutions

**Date**: 2026-11-06  
**Status**: Accepted  

#### Context
Following owner review of the initial Phase 2 return, five specific defects were identified:
1. **Defect 1 (Mock Scorecard Scoping)**: Ending an unattempted mock displayed historical 2026-11-04 practice data for Problem 1 instead of session-scoped attempts.
2. **Defect 2 (Practice Arena Layout)**: Alignment with `mockups/practice.html` column assignments and code editor height minimum (>= 440px).
3. **Defect 3 (Nav Pill Tint per Area)**: Sidebar active pill tint switching dynamically per active screen (Home mint, Practice lilac, Mock peach, Dashboard sky).
4. **Defect 4 (Nowrap Badges)**: Dashboard table status badges ("NOT STARTED", "MASTERED") wrapping across lines.
5. **Defect 5 (State Honesty & Mock Start Rules)**: Streak badge reflecting 0 days as "Not Started", and Mock start view showing Simulation Rules with empty past sessions omitted.

#### Resolutions & Enforced Architecture
1. **Mock Session Scoping**:
   - Implemented `get_mock_problem_evaluation` in `app.py` query/render layer scoping all attempts by `session_start_iso`.
   - Problems without an authentic submission inside the current mock session render `NOT ATTEMPTED` with runtime `—`, hints `0`, and no pass/fail badge.
   - Ending an unsubmitted mock writes 0 rows to SQLite and leaves all dashboard figures byte-identical.
   - Authorized new unit test suite: `tests/test_mock_session_scoping.py` (5 tests passing; total suite 31/31 passed).
2. **Practice Arena Column Structure**:
   - Left column (4 cols / 35%): Statement card (with nowrap starter signature and inputs/outputs) + visible tests + vertically stacked hint ladder buttons (`use_container_width=True`).
   - Right column (7 cols / 65%): Editor card with single-line flex header strip, Ace code editor locked at 440px minimum computed height, Run pill, and sandbox verdict cards.
3. **Dynamic Sidebar Pill Tinting**:
   - `NAV_TINTS` dictionary injects area-specific tokens:
     - Home: `#DFF3E4` (bg) / `#167B48` (fg)
     - Practice Arena: `#E8E2FF` (bg) / `#5932EA` (fg)
     - Mock Interview: `#FFE8D1` (bg) / `#B93815` (fg)
     - Dashboard: `#DCEBFF` (bg) / `#1D5EC2` (fg)
   - Zero new hex codes; zero hex drift.
4. **Table Badge Nowrap**:
   - `.dashboard-table th:last-child`, `.dashboard-table td:last-child`, and `.stat-badge` enforce `white-space: nowrap !important; min-width: 140px;`.
5. **State Honesty**:
   - Home streak card conditionally renders "Not Started" (deep ink `#171712` on muted background, WCAG AA compliant) when `streak_count == 0`, and "Active" (mint) when `>= 1`.
   - Mock start view includes the Simulation Rules & Evaluation Protocol card and renders Past Mock Sessions only when `attempts` with `mode = 'mock'` exist (omitted when count is 0).

---

### [DECISION-009] Phase 2 Corrective Round 2 Resolutions (Practice Arena Focus)

**Date**: 2026-11-06  
**Status**: Accepted  

#### Context
Owner live testing identified 5 defects on the Practice Arena screen:
1. **P1 — Editor Height Honestly**: Round 1 script reported 440px by measuring outer wrapper CSS while the rendered Ace dark field was ~250px tall.
2. **P2 — Starter Signature Fits on One Line**: The longest starter signature line (`log-timestamp-filter`, 79 chars) must fit on one line in Ace editor with soft-wrap OFF and no horizontal scrollbar.
3. **P3 — Workbench Recomposition**: Mirroring `mockups/practice.html`, Left column holds filter header card + statement card; Right column holds editor card on top, verdict card, visible test cases, and hint ladder. Column bottoms must balance within 20% and document horizontal overflow is prohibited.
4. **P4 — Broken Signature Display Box**: Statement signature box must break after each comma with 4-space continuation indent, visible at a glance with no scrollbar.
5. **P5 — Single-Line Test Case Card Labels**: Test case headers must display short label `TEST CASE #n` on one line with no two-line wrapping.

#### Resolutions & Measurement Honesty
1. **P1 Editor Height**:
   - Removed artificial wrapper/iframe CSS overrides (`min-height: 440px !important; height: 440px !important;`).
   - Sized Ace editor directly via `code_editor(..., height="450px")` (passing a string rather than an integer, which sets Ace container height directly instead of `{minLines: 1, maxLines: n}`).
   - Measured exact HTMLIFrameElement bounding rect via CDP: 450px rendered height at both 1920×1080 and 1600×1000 ($\ge 440$px).
2. **P2 Longest Signature Fit**:
   - Lever 1: Column ratio widened to `[3.5, 8.5]`.
   - Lever 2: Editor component `fontSize` set to `13` with `wrap: False`.
   - Result: `log-timestamp-filter` (`def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:`, 79 chars) renders on exactly 1 line with `hScrollDisplay: "none"` and `hasHorizontalOverflow: false`.
3. **P3 Workbench Recomposition**:
   - Left column (`practice_left_col`): `practice_filter_card` + `practice_statement_card` only.
   - Right column (`practice_right_col`): `practice_editor_card` on top $\rightarrow$ sandbox verdict banners $\rightarrow$ `visible_test_card_{i}` $\rightarrow$ `practice_hint_card`.
   - Balance measured via CDP: 4.3% diff at 1920×1080 (55px) and 12.5% diff at 1600×1000 (185px) (both well within the 20% limit). Document `scrollWidth == clientWidth` (1920/1920 and 1600/1600).
4. **P4 Signature Box Formatting**:
   - Broken after commas: `formatted_sig = sig_line.replace(", ", ",\n    ")`.
   - Monospace preformatted block with `scrollWidth == clientWidth` (342px/342px at 1920, 249px/249px at 1600), 0 horizontal scrollbar.
5. **P5 Single-Line Test Case Headings**:
   - Short heading `TEST CASE #{i}` with `white-space: nowrap !important;` and `class="test-case-card-title"`. Measured height: 21px (single line).

---

### [DECISION-010] Topbar Workbench Layout Redesign Approval

**Date**: 2026-11-06  
**Status**: Accepted  

#### Context
Owner live testing of the Phase 2 Direction A implementation rejected the sidebar navigation and stacked-card Practice arena as "really ridiculous". Three candidate redesign directions were explored, and the owner selected Option B ("Topbar Workbench"). Static mockups were created in `mockups/topbar/` and approved by the owner after Corrective Round 2 (closed 2026-11-06).

#### Decision
1. **Sidebar Superseded**: The sidebar layout from Waves 00–07 is superseded and removed. Content flow reclaims the ~450px sidebar width across all 4 screens.
2. **Topbar Navbar Architecture**: A slim 56px topbar navbar is adopted with Fraunces wordmark and "Offline · Code-Judged" pill (left), 4 screen nav pills with area-specific tint washes (center), and live streak/due status chips from `CoachStore` (right).
3. **Practice Workbench Recomposition**: Two-pane workbench layout (~42/58 ratio). Left pane contains single-row filter strip, ONE Problem Card containing all problem specifications, and the Hint Ladder below as a separate butter block. Right pane contains the Editor Card (with glued action row and no window dots) directly followed by ONE Output Card (holding verdict band header and visible test cases).
4. **Home Screen H1 Title**: The Home screen H1 heading is officially designated as "Today's Practice" (replacing "Daily Review and Practice Queue").
5. **Anti-Slop & De-slopped Tables**: Daily Practice Queue and Dashboard tables enforce a maximum of 1 pill per row (status only); track and difficulty are plain typography in partner colors. Decorative tags (`READY`, `BANK`, `RECORDED`, `ZERO HINTS`) are removed; tags must carry state or they do not exist.
6. **Mock Interview Module**: Governed by Addendum A with single-source-of-truth countdown timer in sub-strip pill and scorecard header, and strict session-scoping by `session_start_iso` and `mode == 'mock'`.

---

### [DECISION-011] Phase 2 Final Corrective: Topbar Workbench Polish (Items X1–X9 & Evidence §E)

**Date**: 2026-11-06  
**Status**: Accepted  

#### Context
Owner live-tested the Topbar Workbench implementation (08-PLAN) and rejected the finish based on visual/functional issues captured during testing:
1. **Top Void (X1)**: Noticeable whitespace above the topbar; navbar not cleanly sticky full-bleed at `top: 0`.
2. **Hardcoded Navbar Version Chip (X2)**: Static "3.11" chip in navbar does not derive from runtime environment.
3. **Missing Dashboard Graph (X3)**: Topic pass-rate Plotly chart missing from Dashboard; needs restoration using store data for attempted topics only.
4. **Home CTAs & Subtext (X4, X7-Home)**: Start Practice / Continue Practice buttons need primary pill styling; exact mockup subtexts restored; `NOT STARTED` tag when streak is 0.
5. **Practice Filter Strip Clutter (X5R)**: 3-select filter strip rejected by owner. Replaced with ONE slim picker row: full problem title with prev/next navigation arrows, no box, no field labels; single selection source across app.
6. **Practice Signature & Output Card (X6, X7-Practice, X8, X9)**: Single source of truth for signatures across all 12 problems; neutral Output Card header "Run your code to see results"; natural-width Run & Submit button; small-caps `STARTER FUNCTION SIGNATURE` label; inline code as pastel wash chips.
7. **Audit Evidence Deficit (§E)**: Verification evidence still owed for Mock store snapshots/scoping, hint ladder, pill-tint CDP hexes, and Impeccable live audit.

#### Decision
Structure final corrective as parallel lanes across waves:
- **Wave 0 (Sequential Gate)**: Disclose and dispose `build_app.py` under `scratch/`; record baseline pytest (31 passing).
- **Wave 1 (3 Parallel Lanes on Disjoint app.py Regions)**:
  - **Lane A (Shell)**: X1 (top void, sticky navbar), X2 (runtime version chip). Owns global embedded CSS (`get_global_css`) and `render_topbar()`.
  - **Lane B (Home + Dashboard)**: X3 (Plotly topic pass-rate chart), X4 (primary pill buttons), X7-Home (mockup subtexts, NOT STARTED streak 0). Owns `Home` and `Dashboard` sections.
  - **Lane C (Practice)**: X5R (slim picker row), X6 (signature source of truth), X7-Practice (neutral output header), X8 (Run & Submit natural width), X9 (small-caps signature label, code chips). Owns `Practice Arena` section.
- **Wave 2 (Sequential Gate)**: Lane D (Mock + Evidence E1–E9, r6 screenshots, `/verify 2` verdict, `.gsd/phases/2/IMPLEMENTATION_CORRECTIVE_RETURN.md`).

#### Freezes
- `coach/*.py`, `data/problems/*.json`, `tests/*` untouched (suite remains 31/31).
- Logic behavior frozen; zero new hex tokens beyond DESIGN.md.

---

### [DECISION-012] Addendum V2 Rework (R1–R4) & Empirical Evidence Invariants (V1–V6)

**Date**: 2026-11-06  
**Status**: Accepted  

#### Context
Following review of the initial 09-PLAN implementation return, owner issued ADDENDUM V2 specifying 4 rework items (R1–R4) and 6 evidence items (V1–V6) to achieve clean visual finish and rigorous empirical validation.

#### Decisions & Outcomes
1. **X2 Disposition (Runtime Versioning)**: The static "3.11" version chip in the topbar and the static "Python 3.11" text in the editor strips were eliminated. All surfaces derive the version dynamically at runtime from `sys.version_info` (`3.12`), ensuring truth in environment reporting.
2. **R1 (X6 Redo: Editor Starter Single Source of Truth)**: `starter_code.splitlines()[0].strip()` governs the function signature across the entire application. Problem JSONs contain `statement_md` (which historically had divergent handwritten signatures) and `starter_code`. Rendering logic in `app.py` strips the embedded `### Function Signature` markdown block and renders the exact `starter_code` first line, verified live across all 12 problems (12/12 matching character-for-character).
3. **R2 (X9 Label Redo)**: The Problem Card signature block is labelled by `<span class="signature-subhead">STARTER FUNCTION SIGNATURE</span>` (11px uppercase letter-spaced). The large serif `### Function Signature` heading was removed from `statement_md` rendering, confirmed via CDP DOM query (0 heading elements matching "Function Signature" in Problem Card).
4. **R3 (X10 Picker Buttons)**: Prev/Next buttons in the slim problem picker row are styled as arrow-only (`←` and `→`) with dedicated padding (`padding: 6px 12px !important; min-width: 44px !important;`). Measured via CDP at 1450 viewport: `scrollWidth == clientWidth` (42px/42px), eliminating any ellipsis clipping (`←…` / `N…`).
5. **R4 (X11 Zero Horizontal Overflow & Anchors)**: Practice Arena workbench fits 1450 viewport with `document.documentElement.scrollWidth == document.documentElement.clientWidth` (1450px / 1450px, zero overflow). The editor strip's right-side text ("Sandbox · 3.0s · Python 3.12") renders in full without truncation. Streamlit heading-anchor link icons (`[data-testid="stHeaderActionElements"]`, `[data-testid="stHeadingAnchor"]`, `a.anchor-link`) are hidden globally across ALL screens via CSS.
6. **V1–V6 Evidence**:
   - V1: `/verify 2` verdict and tally recorded.
   - V2: Active nav pill computed backgrounds measured via CDP (`#E8E2FF` for Practice Arena, `#FFE8D1` for Mock Interview) with paired screenshots.
   - V3: Authentic `npx impeccable detect` output and exit codes recorded for all 4 screens.
   - V4: Full named accounting of parked Pro Max skills (`ui-ux-pro-max`, `design`, `design-system`, `ui-styling`).
   - V5: Unsolved-end store pair snapshot proving zero phantom attempt writes (`count` and `max(created_at)` identical).
   - V6: Longest problem title (`Longest Substring Without Repeating Characters`, 46 chars) captured untruncated in picker row.

#### Freezes Preserved
- `coach/*.py`, `data/problems/*.json`, `tests/*` strictly frozen.
- Pytest suite invariant at 31/31 passing.

---

*Last updated: 2026-11-06*



