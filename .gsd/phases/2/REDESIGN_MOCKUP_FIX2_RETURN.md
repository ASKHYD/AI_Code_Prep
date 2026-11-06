# Phase 2 Redesign Mockup Corrective 2 Return: Topbar Workbench Premium + De-Slop

> **Governing System:** Direction A (Brilliant Light)  
> **Status:** Static HTML Mockup Corrective 2 Stage — Gate Ready for Owner Approval  
> **Date:** 2026-11-06  
> **Worktree Directory:** `e:\resume_project`  
> **Quarantine Boundary:** Absolute (Zero application code touched: `app.py`, `coach/*.py`, `data/problems/*.json`, `tests/*`, `DESIGN.md`, `config.toml` strictly untouched)

---

## Preliminary Verification of Previous Fix Round (F1–F6)
All items from the previous fix round were verified 100% complete before beginning P1:
- **F1 (Dashboard Mockup)**: `mockups/topbar/dashboard.html` verified intact with authentic store values (`Solved 1`, `Sessions 1`, `Avg hints 0.0`), `binary-search` at 100%, unattempted topics labeled `NOT STARTED` with NO bar, and bidirectional navbar navigation.
- **F2 (Fail Specimen Runtime)**: `navbar-states.html` State 6 verified with `Runtime: —` and authentic failure message `Visible Case 1 Failed`.
- **F3 (Pass Specimen Sourcing)**: `data/problems/binary-search.json` test counts (2 visible, 6 hidden) verified authentic; `Memory: Clean` removed.
- **F4 (Editor Strip Window Dots)**: Removed from all templates; single-line flex header strip.
- **F5 (Home Track Copy)**: Verified strictly `['dsa', 'python']` tracks across all 12 problem files; copy updated to `"Across DSA and Python tracks."`.
- **F6 (Evidence Captures)**: Dual-resolution captures across 1450×900, 1920×1080, and 1600×1000 verified in `docs/screenshots/r4/`.

---

## 1. Table P1–P7 Status & Evidence

| Item | Requirement | Status | Evidence & Implementation Details |
|---|---|---|---|
| **P1** | **One Problem Card** (Practice, Left Pane) | **DONE** | All problem content enclosed inside ONE card (`.problem-card`, surface `#FFFFFF`, hairline `#E7E1D6` border, radius 24px, padding 24px 28px) in exact order: Title $\rightarrow$ Chips $\rightarrow$ Prose $\rightarrow$ Starter Function Signature Block $\rightarrow$ Inputs $\rightarrow$ Outputs. No loose problem content floats in the pane. Filter strip remains at pane head; Hint Ladder remains below as a separate butter block. |
| **P2** | **One Output Card** (Practice, Right Pane) | **DONE** | All result elements enclosed inside ONE card (`.output-card`, surface `#FFFFFF`, hairline `#E7E1D6` border, radius 24px, overflow hidden) directly under `.editor-container`. Verdict band acts as card header strip (PASS state: `Binary Search · PASS · 178 ms · Hints 0 · 2026-11-04`); all visible test cases live under hairline divider inside the same card. |
| **P3** | **De-Slop the Queue & Tables** (Home + Dashboard) | **DONE** | Daily Practice Queue redesigned with max 1 pill per row (status: `Next Due: +1 Day` / `Unattempted`). Track (`DSA` lilac `#5932EA`, `Python` butter `#9A3412`) and difficulty (`Easy` green `#167B48`, `Medium` coral `#B93815`) rendered as plain text typography. Fraunces 600 problem titles, muted Inter subtext, 3px left track accent bar and hover lift on rows, and reactive bordered text button `"Practice →"` filling CTA green on hover. Removed decorative badges `Ready` and `Bank` from Home stat cards; removed `Recorded` and `Zero Hints` from Dashboard stat cards; track column in Dashboard topic table converted to plain typography. |
| **P4** | **Motion and Premium Feel** (Restrained CSS) | **DONE** | Added restrained CSS transitions: nav pills 160ms ease; card/queue row hover lift -2px with soft shadow (`0 4px 12px rgba(23, 23, 18, 0.06)`, flat at rest); button hover deepen with active `translateY(1px)` press; verdict entrance keyframe (240ms slide-down/fade-in); editor `:focus-within` ring in lilac partner `#5932EA` at 40% opacity; queue action button 160ms fill. Zero gradients, zero blur, zero emoji. Respects `prefers-reduced-motion`. |
| **P5** | **Slop Audit Gate** (Pre-Capture Check) | **DONE** | Executed full audit table across all 5 mockup pages against the 8 trope list. All tropes verified CLEAN or FOUND+FIXED. |
| **P6** | **Pro Max on Record** (Bounded Role) | **DONE** | Exercised `/ui-ux-pro-max` and `/design-system` scripts locally; reported 3 agreement points, 1 token import conflict, and concrete quoted output lines. Accounted for all 7 Pro Max skills by name. |
| **P7** | **Evidence Pack** (1450×900 Primary Gate) | **DONE** | Captured all viewports via automated Chrome CDP: `practice_fullpage_1450x900.png`, `practice_stress_1450x900.png`, `home_1450x900.png`, `home_queue_closeup_1450x900.png`, `dashboard_1450x900.png`, `navbar_states_specimens_1450x900.png`, plus secondary 1920×1080 and 1600×1000 captures. |

---

## 2. Slop Audit Table (P5 Gate)

| Trope Checked | Pages Audited | Result | Findings & Fixes Applied |
|---|---|---|---|
| **1. Chip soup** (more than one filled pill per row/cell) | `practice.html`, `practice_stress.html`, `home.html`, `dashboard.html`, `navbar-states.html` | **FOUND + FIXED** | In `home.html` queue table and `dashboard.html` topic table, eliminated track and difficulty pills, replacing them with plain typography in partner colors (`#5932EA`, `#9A3412`, `#167B48`, `#B93815`). Capped at maximum ONE status pill per row. |
| **2. Uniform pastel card grids** (identical structure repeated without hierarchy) | All 5 files | **CLEAN** | Layouts employ asymmetrical two-pane workbench (42% reading / 58% execution), distinct stat card sizing, and clear hierarchical nesting inside contained Problem and Output cards. |
| **3. Decorative badge/tag kits** (tags that carry no state) | `home.html`, `dashboard.html` | **FOUND + FIXED** | Removed non-state decorative badges `Ready` and `Bank` from Home stat cards, and `Recorded` and `Zero Hints` from Dashboard stat cards. Preserved `Not Started` on Active Streak where streak = 0 represents authentic store state. |
| **4. Gradients, glassmorphism, glow, coloured shadows at rest** | All 5 files | **FOUND + FIXED** | Removed resting `box-shadow` from `.editor-container` and `.navbar-frame`. All cards and frames render flat at rest with crisp hairline borders. Shadows exist strictly on hover (`0 4px 12px rgba(23, 23, 18, 0.06)`). Zero gradients, blur, or glow. |
| **5. Emoji as icons; window-control dots; unspec'd decoration** | All 5 files | **CLEAN** | Zero emojis found across all files. Window traffic-light dots eliminated in F4. All iconography consists strictly of Lucide SVGs. |
| **6. Generic SaaS table styling** (zebra striping, dense grid borders, pill-per-cell) | `home.html`, `dashboard.html` | **FOUND + FIXED** | Replaced dense grid with spacious hairline-separated rows (18px padding), Fraunces 600 titles, 3px left track accent bars on hover, and reactive `"Practice →"` outline-to-fill buttons. |
| **7. Hero phrases / marketing copy in a work tool** | All 5 files | **CLEAN** | Topbar reads concise functional wordmark "AI Coding Prep Coach" with "Offline · Code-Judged" status chip; zero landing-page marketing copy. |
| **8. Invented figures ANYWHERE** (specimens included) | `navbar-states.html`, `practice.html`, `dashboard.html` | **CLEAN** | Re-verified against `coach.db` (`attempts`: 1 row, 178ms, hints 0, 2026-11-04) and `data/problems/binary-search.json` (visible 2, hidden 6). State 6 FAIL specimen renders `Runtime: —`, `Visible Case 1 Failed`, and authentic string fixture diff with zero invented milliseconds or memory metrics. |

---

## 3. Motion List (P4 Restrained Motion)

| Interaction / Component | CSS Selector | Key Transition / Animation | Survivability Tag |
|---|---|---|---|
| **Nav pills** | `.nav-pill` | `transition: background-color 160ms ease, color 160ms ease;` | `[keyed-CSS: survives into Streamlit]` |
| **Problem Card hover lift** | `.problem-card:hover` | `transform: translateY(-2px); box-shadow: 0 4px 12px rgba(23, 23, 18, 0.06);` (rest: flat) | `[mockup-only]` |
| **Output Card hover lift** | `.output-card:hover` | `transform: translateY(-2px); box-shadow: 0 4px 12px rgba(23, 23, 18, 0.06);` (rest: flat) | `[mockup-only]` |
| **Stat cards hover lift** | `.stat-card:hover` | `transform: translateY(-2px); box-shadow: 0 4px 12px rgba(23, 23, 18, 0.06);` (rest: flat) | `[keyed-CSS: survives into Streamlit]` |
| **Daily Queue rows hover lift & accent bar** | `.queue-row:hover td` | `transform: translateY(-2px); box-shadow: 0 4px 12px rgba(23, 23, 18, 0.06); border-left: 3px solid var(--partner-*)` | `[keyed-CSS: survives into Streamlit]` |
| **Dashboard topic table row hover** | `.queue-row:hover td` | `transform: translateY(-2px); box-shadow: 0 4px 12px rgba(23, 23, 18, 0.06);` | `[keyed-CSS: survives into Streamlit]` |
| **Buttons hover deepen & active press** | `.btn-primary-pill`, `.btn-hint-outline`, `.btn-hint-solid`, `.btn-row-action` | `transition: background-color 140ms ease, border-color 140ms ease, transform 100ms ease; :active { transform: translateY(1px); }` | `[keyed-CSS: survives into Streamlit]` |
| **Verdict band entrance** | `.output-card .verdict-band` | `@keyframes verdictEntrance { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }` (240ms cubic-bezier) | `[keyed-CSS: survives into Streamlit]` |
| **Editor surface focus ring** | `.editor-container:focus-within` | `box-shadow: 0 0 0 2px rgba(89, 50, 234, 0.40); transition: box-shadow 160ms ease;` | `[keyed-CSS: survives into Streamlit]` |
| **Queue row action button fill** | `.btn-row-action` | `transition: background-color 160ms ease, color 160ms ease, border-color 160ms ease;` (fills `#15803D` on hover) | `[keyed-CSS: survives into Streamlit]` |
| **Accessibility override** | `@media (prefers-reduced-motion: reduce)` | Zero-duration reset (`0.01ms !important`) for all transitions and animations | `[keyed-CSS: survives into Streamlit]` |

---

## 4. Pro Max Cross-Check (P6)

### (a) Agreements (Top 3 Points)
1. **Container Width & Reading Hierarchy**: UI Pro Max guidelines recommend limiting text line length inside card containers (`max-w-prose` / 65–75ch) rather than allowing unrestrained full-width lines. Enclosing statement flow inside `.problem-card` directly fulfills this.
2. **Progressive Enhancement for Hover Interactions**: Guidelines mandate that hover animations must be non-destructive visual enhancements, with primary actions remaining fully clickable (`onClick handler` rather than `onMouseEnter only`). The row button `"Practice →"` and card lifts strictly adhere to this.
3. **Accessible Motion Compliance**: Guidelines require respecting user accessibility preferences (`@media (prefers-reduced-motion: reduce)`). Added to `style.css` to neutralize transforms and transitions.

### (b) Conflicts (Reported, Never Applied)
1. **External Token CSS File Dependency**: `html-token-validator.py` flagged `practice.html` with:
   `Missing design-tokens.css import`
   *Resolution*: Reported and not applied. Direction A governance strictly embeds all 26 approved tokens in `style.css` under `:root` to ensure self-contained zero-drift styling without spawning unspec'd external token stylesheets.

### (c) Quoted Evidence Lines
- **ui-ux-pro-max output**:
  `**Description:** Content too wide is hard to read | **Do:** Limit max-width for text content (65-75ch) | **Don't:** Let text span full viewport width`
- **design-system output**:
  `Missing design-tokens.css import` (from `html-token-validator.py mockups/topbar/practice.html`)

---

## 5. Resources Exercised

### Slash Invocations
1. **/ui-ux-pro-max**: **USED**. Executed `.agents/skills/ui-ux-pro-max/scripts/search.py` on container hierarchy, hover effects, and motion accessibility; integrated guidance on container constraints and reduced-motion standards. Quoted concrete output line in P6.
2. **/design-system**: **USED**. Executed `.agents/skills/design-system/scripts/html-token-validator.py`; identified and documented the external token import conflict in P6.
3. **/impeccable**: **USED**. Executed `npx impeccable detect mockups/topbar/*.html`. Pre-capture audit caught `[repeated-container-text]` in `practice.html` inside `.problem-card`; rephrased prose and output descriptions, achieving **0 anti-patterns found (0 errors, 0 warnings)** with exit code 0.
4. **/verification-before-completion**: **USED**. Verified quarantine boundary (`git status --porcelain`), color token governance (`audit_hex_drift.py`), test fixture truth (`binary-search.json`), and automated CDP measurements across all viewports.

### Seven Pro Max Skills Accounting (.agents/skills/)
1. **ui-ux-pro-max**: **USED** with evidence. Queried local design intelligence dataset for card containment rules, hover accessibility, and reduced-motion standards.
2. **design-system**: **USED** with evidence. Evaluated token hierarchy via `html-token-validator.py` and validated token compliance against frozen Direction A specs.
3. **ui-styling**: **USED** with evidence. Applied tokenized flexbox layout, single-pill queue table, hairline borders, and hover lift elevation.
4. **design**: **NOT USED / PARKED**. Corporate identity programs, brand mockups, and logo generation are out of scope for mockup card composition.
5. **brand**: **NOT USED / PARKED**. Brand voice messaging frameworks and marketing asset guidelines are out of scope for technical coding workbench ergonomics.
6. **banner-design**: **NOT USED / PARKED**. Social ad banners and promotional banners are out of scope for in-product mockups.
7. **slides**: **NOT USED / PARKED**. HTML slide decks and presentations are out of scope for IDE workbench interfaces.

---

## 6. Pasted Quality Gates

### Quarantine (`git status --porcelain`)
```
?? .gsd/phases/2/REDESIGN_MOCKUP_FIX2_RETURN.md
?? .gsd/phases/2/REDESIGN_MOCKUP_FIX_RETURN.md
?? .gsd/phases/2/REDESIGN_MOCKUP_RETURN.md
?? docs/screenshots/r4/
?? mockups/topbar/
?? scratch/capture_r4_mockups.py
```
*(Zero tracked application code modified; working tree clean)*

### Color Token Governance (`audit_hex_drift.py`)
```
================ HEX DRIFT AUDIT ================
Catalog contains 26 approved Direction A tokens.
✅ ZERO HEX DRIFT: All hex color codes match frozen Direction A tokens in DESIGN.md!
```

### Impeccable UI Audit (`npx impeccable detect`)
```
npx -y impeccable detect mockups/topbar/practice.html mockups/topbar/practice_stress.html mockups/topbar/home.html mockups/topbar/dashboard.html mockups/topbar/navbar-states.html

0 anti-patterns found.
Exit code: 0
```

---

## 7. Captures Inventory (`docs/screenshots/r4/`)

- [practice_fullpage_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/practice_fullpage_1450x900.png) (102,749 bytes) — Full-page capture showing filter strip, Problem Card, hint block, editor card, and Output Card.
- [practice_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/practice_1450x900.png) (100,741 bytes) — Primary 1450×900 viewport capture.
- [practice_stress_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/practice_stress_1450x900.png) (114,845 bytes) — 79-char signature on 1 line in editor, contained Problem Card.
- [home_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/home_1450x900.png) (91,685 bytes) — Home screen with de-slopped queue and clean stat cards.
- [home_queue_closeup_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/home_queue_closeup_1450x900.png) (39,879 bytes) — Close-up capture of the redesigned Daily Practice Queue table.
- [dashboard_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/dashboard_1450x900.png) (101,665 bytes) — Dashboard with de-slopped stat cards and typography-driven topic table.
- [dashboard_1920x1080.png](file:///e:/resume_project/docs/screenshots/r4/dashboard_1920x1080.png) (116,983 bytes) — Secondary widescreen resolution capture.
- [dashboard_1600x1000.png](file:///e:/resume_project/docs/screenshots/r4/dashboard_1600x1000.png) (110,308 bytes) — Secondary desktop resolution capture.
- [navbar_states_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/navbar_states_1450x900.png) (115,569 bytes) — Topbar navigation states sheet.
- [navbar_states_specimens_1450x900.png](file:///e:/resume_project/docs/screenshots/r4/navbar_states_specimens_1450x900.png) (20,753 bytes) — Close-up capture of State 6 PASS and authentic FAIL verdict specimens.

Stopped at Topbar Workbench premium corrective gate, awaiting owner approval.
