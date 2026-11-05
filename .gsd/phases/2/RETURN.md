# Phase 2 Handoff & Return Artifact: Streamlit UI Redesign (Direction A)

> **Governing System:** Direction A (Brilliant Light)  
> **Status:** Completed Phase 2 Implementation Gate  
> **Date:** 2026-11-05 / 2026-11-06  
> **Worktree Directory:** `e:\resume_project`  

---

## §5.1 SUMMARY

### Shell Gate Outcome & Verification Tags

The Phase 2 Shell Gate evaluation confirmed that Streamlit 1.40+ natively accommodates all Direction A design elements without requiring an architecture migration or non-standard framework replacements. The shell gate outcome is cataloged with four strict canonical verification tags:

1. `[SHELL: STREAMLIT-RETAINED]` — All 4 target screens (Home, Practice Workbench, Mock Interview, and Analytics Dashboard) were successfully built within Streamlit using native layout primitives (`st.columns`, `st.container(border=True)`, `@st.fragment`, `st.sidebar`, `st.plotly_chart`), enhanced by single-keyed container styling (`.st-key-*`). Exactly 0 impossible elements were identified.
2. `[BACKEND: FROZEN]` — Zero mutations to core execution engine, database schemas, mock algorithms, problem banks, or existing test fixtures. `coach/*.py`, `data/problems/*.json`, and `tests/` remained strictly quarantined across all 7 implementation waves.
3. `[THEME: DIRECTION-A]` — Complete visual transition from legacy OLED dark mode to the approved Brilliant-style colorful light learning theme. 100% of rendered hex color codes match the 26 frozen tokens in `DESIGN.md`. Zero hex drift.
4. `[QUARANTINE: 100%-VERIFIED]` — Empirical proof verified via `git status --porcelain coach/ data/problems/ tests/` returning exactly 0 dirty files across every task and commit. Exactly 26 of 26 pytest tests continue passing cleanly.

### Numeral A/B Evaluation Winner

During Wave 0 pre-implementation planning, an empirical A/B screenshot evaluation was conducted at 1920×1080 (`docs/screenshots/r3/metrics_ab_eval.png`) comparing **Variant A (Fraunces Display 700)** vs **Variant B (Inter SemiBold 600 Tabular)** across the three primary Home stat cards (`Active Streak`, `Due for Review`, `Total Problems`):

- **Winner Selected:** **Variant B (Inter SemiBold 600 with Tabular Figures)**  
  `font-family: 'Inter', sans-serif; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -0.025em;`
- **Rationale:** Fraunces Display numerals render circular, wide zero glyphs ("0 due") that visually read as a lowercase letter "o" in isolated stat contexts, introducing ambiguity. Variant B provides unmistakable geometric oval zero glyphs, uniform tabular column alignment, and high optical legibility while harmonizing with the modern learning aesthetic.
- **Rule Enforcement:** Monospace fonts (`JetBrains Mono`) remain strictly banned for metric numerals to prevent typewriter anti-patterns.

### What Changed Per Screen

| Screen | Phase 1 Mockup Anchor | Phase 2 Implementation Highlights |
|---|---|---|
| **Global Shell & Sidebar** | `mockups/style.css` | Global canvas paper `#FBFAF7`, surface `#FFFFFF`, deep ink `#171712`, hairline borders `#E7E1D6`. Offline `@font-face` base64 injection for Fraunces, Inter, and JetBrains Mono. Custom radio navigation pills (`.st-key-nav_sidebar_radio`) with active mint wash `#DFF3E4` and partner green `#167B48`. Inlined Lucide SVG brand icon. |
| **Home Screen** | `mockups/home.html` | Fraunces display heading (`Daily Review and Practice Queue`). Three category-tinted stat cards: `wash-mint` (#DFF3E4) for Active Streak ("1 day"), `wash-sky` (#DCEBFF) for Due Today ("0 due"), and `wash-butter` (#FFF0C4) for Problem Bank ("12 problems") with Variant B Inter 600 tabular figures. Sky-tinted empty state for Spaced Repetition queue. Flattened recent attempts card container with hairline row dividers, authentic SQLite records, and high-contrast chips. |
| **Practice Workbench** | `mockups/practice.html` | Two-column split workbench: Left column features 24px rounded card with problem title, metadata chips, markdown problem description, and category-tinted visible test cases. Right column features dark code editor inset (`#14161A`, JetBrains Mono) crowned with a lilac area-tinted header strip (`#E8E2FF`, `#5932EA`) and window control dots. Full-pill CTA buttons (`Run & Submit` in `#15803D`, Hint/Review pills in `#E8E2FF`). Category-tinted structured verdict cards: PASS in mint wash, FAIL with granular expected vs got inputs in rose wash (`#FFE0E0`, `#C5221F`). |
| **Mock Interview** | `mockups/mock.html` | Consolidation of redundant timers into two canonical locations (setup card + active session bar). Monospace countdown ticker (`44:41`) inside coral capsule pill (`#FFE8D1`, `#B93815`). Two-problem tabbed workbench (`[data-baseweb="tab"]`) styled in paper/hairline with coral active selection indicator. Two-card authentic scorecard layout: Problem 1 locked authentic pass from SQLite (`178 ms`), Problem 2 real-time session outcome, and clean Markdown export download button with inlined download icon. |
| **Dashboard** | `mockups/dashboard.html` | Three tinted metric cards (`dash_card_solved` in mint, `dash_card_sessions` in sky, `dash_card_hints` in butter) with Variant B Inter 600 tabular numerals and Lucide SVGs. Plotly chart restyled to transparent canvas with Direction A categorical tints and strict Directive 1 enforcement: unattempted curriculum topics display `NOT STARTED` with zero bars (never deceptive 0% bars). Topic Breakdown Table in a 24px white card container with topic chips, ratio counts, progress bar tracks, and status badges. |

---

## §5.2 TOKENS & FONTS

### Configuration Mapping Used (`.streamlit/config.toml`)

All base Streamlit tokens are mapped directly to frozen Direction A specifications:

```toml
[server]
headless = true
port = 8501
address = "127.0.0.1"

[theme]
base = "light"
primaryColor = "#15803D"
backgroundColor = "#FBFAF7"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#171712"
font = "sans serif"
```

### Self-Hosted Offline `@font-face` Assets

All 12 font variants are stored locally as offline `.woff2` files under `assets/fonts/` (zero CDN dependencies) and embedded as base64 data URIs via `@lru_cache(maxsize=1)` in `app.py`:

| Family | Style | Weights | Files Added |
|---|---|---|---|
| **Fraunces** | Normal | 500, 600, 700, 800 | `fraunces-latin-500-normal.woff2`<br>`fraunces-latin-600-normal.woff2`<br>`fraunces-latin-700-normal.woff2`<br>`fraunces-latin-800-normal.woff2` |
| **Inter** | Normal | 400, 500, 600, 700 | `inter-latin-400-normal.woff2`<br>`inter-latin-500-normal.woff2`<br>`inter-latin-600-normal.woff2`<br>`inter-latin-700-normal.woff2` |
| **JetBrains Mono** | Normal | 400, 500, 600, 700 | `jetbrains-mono-latin-400-normal.woff2`<br>`jetbrains-mono-latin-500-normal.woff2`<br>`jetbrains-mono-latin-600-normal.woff2`<br>`jetbrains-mono-latin-700-normal.woff2` |

### Computed-Font Proof Output (`scratch/verify_fonts_cdp.js`)

Verified via headless Chrome DevTools Protocol attached to live Streamlit instance:

```text
================ COMPUTED FONT RESULTS ================
Heading (H1 "Daily Review and Practice Queu"):
  font-family: Fraunces, serif
Body (LABEL "Navigation"):
  font-family: Inter, sans-serif
Metric (DIV "0 days"):
  font-family: Inter, sans-serif
  font-weight: 600
  font-variant-numeric: tabular-nums
Code (CODE "nums"):
  font-family: "JetBrains Mono", monospace
======================================================

[Offline Isolation] Total requests captured: 232
[Offline Isolation] Google Fonts external requests: 0
✅ ALL COMPUTED FONT ASSERTIONS PASSED CLEANLY:
  - Heading computed family contains 'Fraunces'
  - Body computed family contains 'Inter'
  - Metric numeral computed family contains 'Inter' (Variant B 600 tabular)
  - Code computed family contains 'JetBrains Mono'
  - 0 Google Fonts network requests (pure offline base64 @font-face)
```

---

## §5.3 RESOURCES EXERCISED

All 7 UI/UX Pro Max resource areas and `developing-with-streamlit` workflows were actively exercised and evidenced across Phase 2:

| Resource / Skill | Implementation Wave | Specific Phase Evidence |
|---|---|---|
| **1. UI/UX Pro Max Design Intelligence** (`ui-ux-pro-max`) | Waves 0, 1, 3, 4, 5, 6 | Direction A Brilliant-style color emotional logic, 6-part functional tint pairings, Fraunces/Inter optical balance, 24px soft card geometry, and anti-pattern avoidance. |
| **2. UI Styling & CSS Tokens** (`ui-styling`) | Waves 1, 2, 3, 4, 6 | Global CSS injection via `st.html(get_global_css())`, 999px pill button geometry with `white-space: nowrap`, base64 offline fonts, `.st-key-*` container scoping. |
| **3. Design System Architecture** (`design-system`) | Waves 1, 2, 7 | Three-layer token governance (`primitive` → `semantic` → `component`), zero hex drift enforcement, WCAG AA/AAA contrast ratios ($\ge 4.5:1$ on text, $\ge 5.4:1$ on badges). |
| **4. Empirical Validation Protocol** (`empirical-validation`) | Waves 0, 1, 2, 3, 4, 5, 6, 7 | Headless CDP verification scripts (`verify_fonts_cdp.js`, `verify_sidebar_cdp.js`, `capture_screen.py`), automated dual-resolution screenshot capture at 1920×1080 and 1600×1000. |
| **5. Codebase Mapper** (`codebase-mapper`) | Waves 2, 3, 4, 5, 6 | Streamlit widget tree mapping, session state management (`st.session_state`), and query param synchronization (`?screen=...`). |
| **6. Brand Voice & Identity** (`brand`) | Waves 2, 3, 5 | Wordmark "AI Coding Prep Coach", tagline "Zero Cost • Code-Judged • Offline-Ready", Lucide SVG icons inlined directly from assets. |
| **7. Quality & Reality Checker** (`agency-reality-checker` / `plan-checker`) | Waves 0, 7 | Pre- and post-implementation regression guards, strict code quarantine verification, Impeccable accessibility/anti-pattern scan. |
| **8. Developing with Streamlit** (`developing-with-streamlit`) | Waves 2, 3, 4, 5, 6 | Custom CSS workarounds using single-named container wrappers (`st.container(border=True, key="...")`), `@st.fragment` live countdown timer, Plotly chart integration. |

---

## §5.4 GATES

### Gate 1: Regression Guard (Before & After)

- **Pre-Implementation Baseline (Wave 0):** `26 passed in 14.88s`
- **Post-Implementation Final (Wave 7):** `26 passed in 6.07s`
- **Fixture Verification:** `tests/test_judge.py::test_regression_longest_substring_fixture_mock_path` PASSED [100%].

```text
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

============================= 26 passed in 6.07s ==============================
```

### Gate 2: Quarantine Assertion

```text
$ git status --porcelain coach/ data/problems/ tests/
# Output: (zero changes, 100% clean)
```

### Gate 3: Impeccable Detection Runs & Final Scan

Executed `npx impeccable detect "<URL>" --json` across all 4 live states via `scratch/run_impeccable_audit.py`:

```text
================ FINAL IMPECCABLE AUDIT REPORT ================
  - Home Screen               : PASSED (0 Primary) (Advisories: 0, Exit Code: 0)
  - Practice Arena            : PASSED (0 Primary) (Advisories: 0, Exit Code: 0)
  - Mock Interview (Running)  : PASSED (0 Primary) (Advisories: 0, Exit Code: 0)
  - Dashboard                 : PASSED (0 Primary) (Advisories: 0, Exit Code: 0)

✅ AUDIT PASSED: Zero primary findings across all 4 live states!
```

### Gate 4: Zero Hex Drift Audit

Executed `scratch/audit_hex_drift.py` checking every hex occurrence in `app.py`, `.streamlit/config.toml`, and CSS rules against `DESIGN.md`:

```text
================ HEX DRIFT AUDIT ================
Catalog contains 26 approved Direction A tokens.

--- Cataloged Token Usage ---
  #14161A:   3 uses (code-bg (dark editor surface))
  #15803D:   3 uses (primary / cta-green (primary button))
  #167B48:  22 uses (partner-green (pass badge text / hover))
  #171712:  52 uses (ink (headings / deep text))
  #1D5EC2:   6 uses (partner-blue (due badge text / accent))
  #1F9D63:   3 uses (fill-green (mastery progress fill))
  #2273E6:   2 uses (fill-blue (analytics fill))
  #5932EA:   7 uses (partner-violet (practice badge text / accent))
  #66635A:  49 uses (muted (warm grey captions / secondary))
  #6C4CF1:   2 uses (fill-violet (practice fill))
  #9A3412:  10 uses (partner-amber (timeout badge text))
  #B45309:   3 uses (fill-amber (in-progress fill))
  #B93815:  13 uses (partner-coral (timer text / accent))
  #C5221F:  13 uses (partner-red (fail text / error badge text))
  #D92D20:   1 uses (fill-red (fail fill / error pill))
  #DCEBFF:   4 uses (wash-sky (due / analytics card bg))
  #DFF3E4:  11 uses (wash-mint (streak / pass card bg))
  #E4572E:   2 uses (fill-coral (timer pill fill))
  #E7E1D6:  38 uses (hairline (borders / dividers))
  #E8E2FF:   4 uses (wash-lilac (practice nav / editor strip bg))
  #F2F2ED:   2 uses (code-text (monospace editor text))
  #FBFAF7:  13 uses (paper (global canvas root))
  #FFE0E0:   6 uses (wash-rose (fail card bg / error wash))
  #FFE8D1:   6 uses (wash-peach (mock nav / timer wash))
  #FFF0C4:   6 uses (wash-butter (library / timeout card bg))
  #FFFFFF:  28 uses (surface (card white / on-primary))

✅ ZERO HEX DRIFT: All hex color codes match frozen Direction A tokens in DESIGN.md!
```

---

## §5.5 UI RESOURCE MAP & SCREENSHOTS

### Per-Element Component, Token & Key Map

| Screen | UI Element | Streamlit Component | Governing Token(s) | Key / Custom Selector |
|---|---|---|---|---|
| **Global** | Root Canvas | Base HTML | `paper` (`#FBFAF7`) | `html, body, .stApp` |
| **Global** | Headings | `st.markdown`, `st.header` | `ink` (`#171712`), Fraunces | `h1, h2, h3, .stTitle, .stSubheader` |
| **Global** | Body Copy | `st.markdown`, `p`, `span` | `ink` (`#171712`), Inter | `p, span, label` |
| **Global** | Buttons | `st.button(type="primary")` | `primary` (`#15803D`), `surface` (`#FFFFFF`) | `button[kind="primary"]` (pill 999px) |
| **Sidebar** | Brand Wordmark | `st.sidebar.markdown` | `ink` (`#171712`), Fraunces 700 | Inlined SVG + wordmark text |
| **Sidebar** | Navigation Pills | `st.sidebar.radio` | `wash-mint` (`#DFF3E4`), `partner-green` (`#167B48`) | `.st-key-nav_sidebar_radio` |
| **Home** | Streak Stat Card | `st.container(border=True)` | `wash-mint` (`#DFF3E4`), `partner-green` (`#167B48`) | `.st-key-card_streak` |
| **Home** | Due Today Card | `st.container(border=True)` | `wash-sky` (`#DCEBFF`), `partner-blue` (`#1D5EC2`) | `.st-key-card_due` |
| **Home** | Problem Bank Card| `st.container(border=True)` | `wash-butter` (`#FFF0C4`), `partner-amber` (`#9A3412`) | `.st-key-card_library` |
| **Home** | Spaced Rep Empty | `st.container(border=True)` | `wash-sky` (`#DCEBFF`), `partner-blue` (`#1D5EC2`) | `.st-key-home_due_card` |
| **Home** | Recent Attempts | `st.container(border=True)` | `surface` (`#FFFFFF`), `hairline` (`#E7E1D6`) | `.st-key-home_recent_card`, `.attempt-row` |
| **Practice**| Problem Statement | `st.container(border=True)` | `surface` (`#FFFFFF`), `hairline` (`#E7E1D6`) | `.st-key-practice_problem_card` |
| **Practice**| Editor Strip | `st.html` | `wash-lilac` (`#E8E2FF`), `partner-violet` (`#5932EA`) | `.editor-header-strip` |
| **Practice**| Code Inset | Ace Editor / `st.text_area` | `code-bg` (`#14161A`), `code-text` (`#F2F2ED`) | Inset code container (`#14161A`) |
| **Practice**| Run Action Pill | `st.button(type="primary")` | `primary` (`#15803D`), `surface` (`#FFFFFF`) | `.st-key-btn_run_code button` |
| **Practice**| PASS Verdict | `st.container(border=True)` | `wash-mint` (`#DFF3E4`), `partner-green` (`#167B48`) | `.st-key-verdict_pass_card` |
| **Practice**| FAIL Verdict | `st.container(border=True)` | `wash-rose` (`#FFE0E0`), `partner-red` (`#C5221F`) | `.st-key-verdict_fail_card` |
| **Mock** | Timer Capsule | `@st.fragment` container | `wash-peach` (`#FFE8D1`), `partner-coral` (`#B93815`) | `.st-key-mock_timer_card`, `.timer-capsule` |
| **Mock** | Problem Tabs | `st.tabs` | `paper` (`#FBFAF7`), `partner-coral` (`#B93815`) | `button[data-baseweb="tab"]` |
| **Mock** | Scorecard Boxes | `st.container` / columns | `paper` (`#FBFAF7`), `hairline` (`#E7E1D6`) | Scorecard problem boxes |
| **Dashboard**| Tinted Metric Cards| `st.container(border=True)` | `wash-mint`, `wash-sky`, `wash-butter` | `.st-key-dash_card_solved`, `.dash_card_sessions`, `.dash_card_hints` |
| **Dashboard**| Plotly Chart | `st.plotly_chart` | Categorical tint palette, transparent canvas | `.st-key-dashboard_chart_card` |
| **Dashboard**| Topic Table Card| `st.container(border=True)` | `surface` (`#FFFFFF`), `hairline` (`#E7E1D6`) | `.st-key-dashboard_table_card`, `.dashboard-table` |

---

### Screenshot Catalog (Dual-Resolution)

#### 1. Real Application Screenshots (Phase 2 Direction A Live Streamlit)
- **Home Screen:**  
  - Full HD: [`docs/screenshots/r3/home_real_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/home_real_1920x1080.png)  
  - Compact: [`docs/screenshots/r3/home_real_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/home_real_1600x1000.png)
- **Practice Workbench:**  
  - Full HD: [`docs/screenshots/r3/practice_real_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/practice_real_1920x1080.png)  
  - Compact: [`docs/screenshots/r3/practice_real_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/practice_real_1600x1000.png)
- **Mock Interview:**  
  - Full HD: [`docs/screenshots/r3/mock_real_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/mock_real_1920x1080.png)  
  - Compact: [`docs/screenshots/r3/mock_real_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/mock_real_1600x1000.png)
- **Dashboard Screen:**  
  - Full HD: [`docs/screenshots/r3/dashboard_real_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/dashboard_real_1920x1080.png)  
  - Compact: [`docs/screenshots/r3/dashboard_real_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/dashboard_real_1600x1000.png)  
  - Scrolled Table: [`docs/screenshots/r3/dashboard_table_scrolled.png`](file:///e:/resume_project/docs/screenshots/r3/dashboard_table_scrolled.png)

#### 2. Side-by-Side Comparison Composites (Phase 1 Mockup vs Phase 2 Real App)
- **Home Side-by-Side:**  
  - Full HD (3842×1144): [`docs/screenshots/r3/home_comparison_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/home_comparison_1920x1080.png)  
  - Compact (3202×1064): [`docs/screenshots/r3/home_comparison_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/home_comparison_1600x1000.png)
- **Practice Workbench Side-by-Side:**  
  - Full HD (3842×1144): [`docs/screenshots/r3/practice_comparison_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/practice_comparison_1920x1080.png)  
  - Compact (3202×1064): [`docs/screenshots/r3/practice_comparison_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/practice_comparison_1600x1000.png)
- **Mock Interview Side-by-Side:**  
  - Full HD (3842×1144): [`docs/screenshots/r3/mock_comparison_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/mock_comparison_1920x1080.png)  
  - Compact (3202×1064): [`docs/screenshots/r3/mock_comparison_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/mock_comparison_1600x1000.png)
- **Dashboard Side-by-Side:**  
  - Full HD (3842×1144): [`docs/screenshots/r3/dashboard_comparison_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r3/dashboard_comparison_1920x1080.png)  
  - Compact (3202×1064): [`docs/screenshots/r3/dashboard_comparison_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r3/dashboard_comparison_1600x1000.png)

#### 3. Legacy Pre-Redesign Baseline (R2 OLED Dark Mode)
- Home (Dark): [`docs/screenshots/01_home_screen.png`](file:///e:/resume_project/docs/screenshots/01_home_screen.png)
- Practice (Dark): [`docs/screenshots/02_practice_screen.png`](file:///e:/resume_project/docs/screenshots/02_practice_screen.png)
- Mock Interview (Dark): [`docs/screenshots/03_mock_timer_t1.png`](file:///e:/resume_project/docs/screenshots/03_mock_timer_t1.png) & [`04_mock_scorecard.png`](file:///e:/resume_project/docs/screenshots/04_mock_scorecard.png)
- Dashboard (Dark): [`docs/screenshots/05_dashboard_screen.png`](file:///e:/resume_project/docs/screenshots/05_dashboard_screen.png)

---

### Side-by-Side Visual Differences vs Mockups

| Screen | Phase 1 Mockup Spec | Phase 2 Real App Implementation | Difference & Justification |
|---|---|---|---|
| **Global Navigation** | Static HTML `<a>` tags with absolute styling | Streamlit `st.sidebar.radio` styled into full-pill items via `.st-key-nav_sidebar_radio` | Streamlit does not provide native link-based sidebar menus. Radio buttons provide authentic reactive rerun semantics and state retention while perfectly emulating pill buttons. |
| **Practice Editor** | Static HTML mockup container | Ace code editor inset with fallback `st.text_area` surrounded by `.editor-header-strip` | Necessary bridge to support bidirectional Python state synchronization with Monaco/Ace editors inside Streamlit's iframe architecture. |
| **Mock Interview Tabs** | Plain CSS flexbox buttons | BaseWeb tab widgets (`st.tabs`) restyled via `div[data-baseweb="tab-list"]` | Utilizes Streamlit's native accessible keyboard-navigable tabs while maintaining the coral pill indicator. |
| **Topic Breakdown Table** | Pure static HTML `<table>` | HTML table markup injected via `st.markdown(table_markup, unsafe_allow_html=True)` inside a 24px white card | Streamlit `st.dataframe` cannot render nested HTML progress bars, track chips, or tabular ratios without heavy canvas workarounds. Injected markup cleanly delivers the exact mockup layout. |
| **Recent Attempts** | Nested card rows | Flattened rows separated by hairline dividers | Impeccable audit flagged nested card borders inside elevated containers. Replacing them with dividers creates superior visual elegance and resolves the nested-cards anti-pattern. |

---

## §5.6 KNOWN LIMITS

1. **Editor Lilac Header Strip Integration:**  
   In Phase 1 mockups, the lilac header strip seamlessly caps the Monaco/Ace editor within a single unified HTML card. In Streamlit, custom HTML (`st.html`) and the Streamlit code widget/component exist in adjacent DOM nodes. Negative margins (`margin: -24px -24px 16px -24px; border-radius: 23px 23px 0 0;`) are applied to seamlessly attach the header strip to the container card's top edge.
2. **Interactive Tab Pills Mechanics:**  
   Tab pill selection in Practice and Mock utilizes BaseWeb tab overrides (`button[data-baseweb="tab"][aria-selected="true"]`). While visually identical to the mockups, the active pill indicator transitions via CSS `all 0.15s ease` rather than layout-shift animation.
3. **Deferred Items (P2/P3 Polish):**  
   - Ace editor syntax theme: Using standard dark Monokai/Tomorrow Night surface (`#14161A`). Future polish may introduce an exact custom Ace theme matching Direction A token highlights.
   - Hotkey bindings (`Ctrl+Enter` to submit): Deferred to future keyboard shortcut phase to preserve quarantine on judge backend.
4. **CSS Instances Beyond Native Widgets Justification:**  
   All injected CSS rules in `app.py` strictly adhere to the single CSS block pattern (`get_global_css()`) or scoped single-named container wrappers (`st.container(border=True, key="...")`). No wildcard style injections or uncataloged hex codes exist. Every instance is strictly justified to achieve Direction A's 24px card radius, 999px action pills, and self-hosted offline fonts.

---

## §5.7 STOP

> **Stopped at Phase 2 implementation gate, awaiting owner approval of the real app screenshots.**
