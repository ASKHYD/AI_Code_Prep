# Phase 2 Redesign Mockup Return: Option B "Topbar Workbench"

> **Governing System:** Direction A (Brilliant Light)  
> **Status:** Static HTML Mockup Stage — Gate Ready for Owner Screenshot Review  
> **Date:** 2026-11-06  
> **Worktree Directory:** `e:\resume_project`  
> **Quarantine Boundary:** Absolute (Zero application code touched)  

---

## 1. Quality Gates & Quarantine Proof

| Gate | Requirement | Measured Result | Verdict |
|---|---|---|---|
| **Codebase & Backend Quarantine** | `app.py`, `coach/*.py`, `data/problems/*.json`, `tests/*`, `DESIGN.md`, `config.toml`, existing `mockups/` strictly untouched | Verified via `git status --porcelain` (0 modified files) | **PASS** |
| **Color Token Governance** | Zero hex drift against frozen Direction A tokens in `DESIGN.md` | **32 hexes cataloged; 0 unapproved hexes** across all mockup files | **PASS** |
| **Impeccable UI Audit** | Pre-capture detection audit on HTML mockups | **0 primary findings (0 errors, 0 warnings)** via `npx impeccable detect --json` | **PASS** |
| **Anti-Crush List (1450×900 Primary)** | Items (a) through (h) visibly verified at 1450px width | **100% PASS** on all 8 criteria | **PASS** |
| **Pane Width Thresholds (1450×900)** | Left pane $\ge 500$px, Right pane $\ge 800$px | **Left Pane: 609px ($\ge 500$px)**<br>**Right Pane: 841px ($\ge 800$px)** | **PASS** |
| **Page Horizontal Overflow** | Zero horizontal scrollbar across all resolutions | **1450×900**: 1450 / 1450 (0 overflow)<br>**1920×1080**: 1905 / 1905 (0 overflow)<br>**1600×1000**: 1585 / 1585 (0 overflow) | **PASS** |

### Quarantine Proof (`git status --porcelain`)
```
?? .gsd/phases/2/REDESIGN_MOCKUP_RETURN.md
?? docs/screenshots/r4/
?? mockups/topbar/
?? scratch/capture_r4_mockups.py
```
*(Zero tracked application files modified; working tree clean)*

---

## 2. Option B "Topbar Workbench" Anatomy

1. **Top Navbar Chrome (56px)**:
   - Sidebar is eliminated. One slim top navbar spans the screen (`height: 56px; background: #FBFAF7; border-bottom: 1px solid #E7E1D6;`).
   - **Left**: Fraunces wordmark "AI Coding Prep Coach" + outlined pill "Offline · Code-Judged".
   - **Center**: Nav pills for Home, Practice Arena, Mock Interview, and Dashboard with screen-specific active tint washes (Home mint `#DFF3E4`/`#167B48`, Practice lilac `#E8E2FF`/`#5932EA`, Mock peach `#FFE8D1`/`#B93815`, Dashboard sky `#DCEBFF`/`#1D5EC2`).
   - **Right**: Compact store status chips: streak chip (Lucide flame + "0 days" in mint wash) and due chip (Lucide calendar + "0 due" in sky wash).
2. **Two-Pane Practice Workbench**:
   - Split: ~42% Left (reading) / ~58% Right (working), separated by a crisp hairline border.
   - **Left Pane (Reading)**:
     - **Filter Strip**: Single hairline-divided row at pane head (`TRACK: DSA`, `DIFFICULTY: Easy`, `TOPIC: Binary Search`, `PROBLEM: Binary Search`) with full-word labels that never wrap. Replaces the crushed filter card permanently.
     - **Statement Flow**: Title on one line $\rightarrow$ Track/Topic/Difficulty chips $\rightarrow$ Description prose $\rightarrow$ Preformatted JetBrains Mono signature block broken after each comma with 4-space continuations $\rightarrow$ Inputs & Outputs specs.
     - **Hint Ladder**: One tinted butter block (`#FFF0C4` / `#9A3412`) with progressive level indicators (Level 1 Revealed › Level 2 › Level 3) and full-width stacked buttons: "Reveal Next Hint (Level 2)" and "Ask AI to Explain Hint".
   - **Right Pane (Working)**:
     - **Editor Strip**: Single line flex strip ("SOLUTION EDITOR · PYTHON" with traffic lights left / "Sandbox · 3.0s · Python 3.12" right).
     - **Dark Editor Surface**: `#14161A` single dark surface, tall (440px), line numbers gutter, syntax-highlighted code.
     - **Glued Action Row**: Directly integrated under the editor bottom border ("Clean environment · Network disabled" left / primary pill "Run & Submit" in CTA `#15803D` right).
     - **Verdict Band**: Directly under action row in PASS state with authentic attempt (`Binary Search · PASS · 178 ms · Hints 0`).
     - **Visible Test Cases**: Compact list rows ("TEST CASE #1", "TEST CASE #2" + Provided chip + Input/Expected).
3. **Mock Chrome Variant**:
   - Screen-local slim substrip beneath topbar carrying problem tabs (`Problem 1: Binary Search`, `Problem 2: Longest Substring`) and peach timer pill (`44:41`). Countdown timer is rendered in exactly two places total (substrip + scorecard), never a third.
4. **Authentic Specimen Treatments**:
   - FAIL band treatment rendered in rose wash (`#FFE0E0` / `#C5221F`) using the authentic Longest Substring state (`s = "abcabcbb"` $\rightarrow$ Expected 3, Got 2). Zero invented numbers.
5. **Stress Case Verification**:
   - Tested on `Log Timestamp Filter` (`log-timestamp-filter`) with 79-character signature: `def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:`.
   - In statement pre block: broken after each comma with 4-space indent, zero clipping, zero inner scrollbar.
   - In editor: sits on **ONE line** with zero horizontal overflow.

---

## 3. CDP Measurements Under The Measurement Rule

All measurements recorded via automated Chrome DevTools Protocol (`scratch/capture_r4_mockups.py`):

```json
{
  "1450x900 (PRIMARY OWNER VIEWPORT)": {
    "practice": {
      "leftPaneWidth": 609,
      "rightPaneWidth": 841,
      "isLeftPaneGte500": true,
      "isRightPaneGte800": true,
      "editorHeight": 440,
      "isEditorTall": true,
      "sigScrollWidth": 558,
      "sigClientWidth": 558,
      "sigNoOverflow": true,
      "titleOnOneLine": true,
      "docScrollWidth": 1450,
      "docClientWidth": 1450,
      "noDocOverflow": true,
      "testCasesSingleLine": true,
      "filterLabelsSingleLine": true,
      "filterItemsCount": 4,
      "hintButtonsLabels": [
        "Reveal Next Hint (Level 2)",
        "Ask AI to Explain Hint"
      ],
      "navPillsLabels": [
        "Home",
        "Practice Arena",
        "Mock Interview",
        "Dashboard"
      ],
      "statusChipsLabels": [
        "0 days",
        "0 due"
      ]
    },
    "practice_stress": {
      "firstLineText": "def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:",
      "firstLineLength": 79,
      "sigScrollWidth": 552,
      "sigClientWidth": 552,
      "sigNoOverflow": true,
      "docScrollWidth": 1435,
      "docClientWidth": 1435,
      "noDocOverflow": true,
      "leftPaneWidth": 603,
      "rightPaneWidth": 832
    }
  },
  "1920x1080": {
    "practice": {
      "leftPaneWidth": 800,
      "rightPaneWidth": 1105,
      "isLeftPaneGte500": true,
      "isRightPaneGte800": true,
      "editorHeight": 440,
      "isEditorTall": true,
      "sigScrollWidth": 749,
      "sigClientWidth": 749,
      "sigNoOverflow": true,
      "titleOnOneLine": true,
      "docScrollWidth": 1905,
      "docClientWidth": 1905,
      "noDocOverflow": true,
      "testCasesSingleLine": true,
      "filterLabelsSingleLine": true,
      "filterItemsCount": 4
    }
  },
  "1600x1000": {
    "practice": {
      "leftPaneWidth": 666,
      "rightPaneWidth": 919,
      "isLeftPaneGte500": true,
      "isRightPaneGte800": true,
      "editorHeight": 440,
      "isEditorTall": true,
      "sigScrollWidth": 615,
      "sigClientWidth": 615,
      "sigNoOverflow": true,
      "titleOnOneLine": true,
      "docScrollWidth": 1585,
      "docClientWidth": 1585,
      "noDocOverflow": true,
      "testCasesSingleLine": true,
      "filterLabelsSingleLine": true,
      "filterItemsCount": 4
    }
  }
}
```

---

## 4. Anti-Crush List Confirmation (Item-by-Item at 1450×900)

- **(a) Filter strip labels in full, one line, selects side by side in ONE row**: **CONFIRMED**. `TRACK`, `DIFFICULTY`, `TOPIC`, `PROBLEM` displayed side-by-side in a 4-item flex row (`filterItemsCount: 4`, `filterLabelsSingleLine: true`).
- **(b) Statement title on one line**: **CONFIRMED**. Rendered at 24px Fraunces on one line (`titleOnOneLine: true`, height 29px).
- **(c) Signature block fully readable, breaks only after commas**: **CONFIRMED**. `def binary_search(nums: list,\n    target: int) -> int:` rendered in JetBrains Mono with 0 clipping and 0 horizontal scrollbar (`sigScrollWidth == sigClientWidth == 558px`).
- **(d) Hint buttons show full labels**: **CONFIRMED**. Stacked buttons display full text: `"Reveal Next Hint (Level 2)"` and `"Ask AI to Explain Hint"`.
- **(e) "TEST CASE #n" labels on one line**: **CONFIRMED**. Height = 21px, single line with `white-space: nowrap !important;` beside "Provided" badge.
- **(f) Navbar pills show full screen names; streak and due chips fully readable**: **CONFIRMED**. Full labels `"Home"`, `"Practice Arena"`, `"Mock Interview"`, `"Dashboard"`, and chips `"0 days"`, `"0 due"`.
- **(g) No horizontal scrollbar on the page**: **CONFIRMED**. `document.scrollWidth <= document.clientWidth` across all resolutions (1450/1450, 1905/1905, 1585/1585).
- **(h) Editor's dark field extends well below starter code**: **CONFIRMED**. Editor dark surface is 440px tall, leaving >350px of dark inset below the 3 starter code lines.

---

## 5. Feasibility Note for Future Streamlit Implementation

This note evaluates how Option B's load-bearing elements will be mapped into Streamlit during the subsequent implementation round:

1. **Sidebar Removal**:
   - *Streamlit Mechanism*: `[config token]` + `[keyed CSS]`.
   - *Feasibility*: Native config `[client] showSidebarNavigation = false` coupled with CSS hiding `[data-testid="stSidebar"]` and `[data-testid="collapsedControl"]`. Fully feasible.
2. **Sticky Slim Topbar Navbar**:
   - *Streamlit Mechanism*: `[keyed CSS]` + `[st.html / st.pills]`.
   - *Feasibility*: Topbar container rendered at `app.py` root with `position: sticky; top: 0; z-index: 999; height: 56px; border-bottom: 1px solid #E7E1D6;`. Screen navigation mapped via query parameters (`?screen=practice`) or styled Streamlit pills. Fully feasible.
3. **Two-Pane Split (~40% Left / ~58% Right)**:
   - *Streamlit Mechanism*: `[native st.columns]`.
   - *Feasibility*: Built natively with `st.columns([4.2, 5.8], gap="large")`. Page scroll model is accepted (independent pane scrolling is explicitly not promised). Fully feasible.
4. **Single-Row Filter Strip at Left Pane Head**:
   - *Streamlit Mechanism*: `[keyed CSS]` + `[st.columns([1, 1, 1, 1], gap="small")]` or native `st.html()` select controls.
   - *Feasibility*: 4 compact selects side by side with full labels. Fully feasible.
5. **Action Row Glued Directly Under Editor**:
   - *Streamlit Mechanism*: `[keyed CSS]`.
   - *Feasibility*: Editor wrapper and action row container styled with `margin-top: 0 !important; border-top: none !important; border-radius: 0 0 14px 14px !important;` to visually fuse into one unified block. Run & Submit pill button positioned on the right. Fully feasible.
6. **Verdict Band Directly Under Action Row**:
   - *Streamlit Mechanism*: `[bordered container]` + `[keyed CSS]`.
   - *Feasibility*: Rendered via `st.container(border=True, key="verdict_band")` using Direction A tint washes (`#DFF3E4` / `#FFE0E0`). Fully feasible.

---

## 6. Resources & Skills Exercised

- **`/impeccable`**: **USED**. Executed `npx impeccable detect` across all mockup files. Discovered and resolved undersized functional text, cramped padding, and heading level skipping, achieving **0 primary findings (0 errors, 0 warnings)**.
- **`/agency-ui-finish-gate-reviewer`**: **USED**. Conducted structured finish-gate evaluation of `practice.html` and `practice_stress.html` against the 8-item anti-crush list at the primary 1450px viewport. Returned **PASS**.
- **`/verification-before-completion`**: **USED**. Verified git status quarantine, headless Chrome CDP measurements, and hex token adherence before making completion claims.

### 7 Pro Max Skills Accounting:
- `ui-ux-pro-max`: **NOT USED for generation** (design tokens frozen from Phase 1). Used anti-pattern checklist for pre-delivery audit.
- `design-system`: **USED**. Verified that all 32 hex colors match the frozen Direction A tokens in `DESIGN.md`. Zero hex drift.
- `ui-styling`: **USED**. Authored framework-agnostic two-pane workbench CSS in `mockups/topbar/style.css`.
- `design`: **USED**. Designed Option B Topbar Workbench anatomy based on LeetCode/Exercism/HackerRank research consensus.
- `brand`, `banner-design`, `slides`: **NOT USED**, parked (out of scope for static mockups).
- `developing-with-streamlit`: **USED** in Section 5 (Feasibility Note evaluating implementation mechanisms without touching application code).

---

## 7. Deliverables & Screenshots Inventory

### Mockup Files
- [`mockups/topbar/style.css`](file:///e:/resume_project/mockups/topbar/style.css): Shared stylesheet with frozen Direction A tokens, topbar, and workbench rules.
- [`mockups/topbar/practice.html`](file:///e:/resume_project/mockups/topbar/practice.html): Two-pane workbench with Binary Search, filter strip, broken signature, butter hint ladder, glued action row, PASS verdict band, and visible test cases.
- [`mockups/topbar/practice_stress.html`](file:///e:/resume_project/mockups/topbar/practice_stress.html): Stress case with Log Timestamp Filter (79-character signature on 1 line in editor).
- [`mockups/topbar/navbar-states.html`](file:///e:/resume_project/mockups/topbar/navbar-states.html): 4 navbar active-tint states, Mock timer substrip variant, and PASS/FAIL verdict specimens.
- [`mockups/topbar/home.html`](file:///e:/resume_project/mockups/topbar/home.html): Approved Direction A Home content and cards with topbar chrome.

### Screenshots Captured in `docs/screenshots/r4/` (and mirrored to brain artifacts)
- **Primary Viewport (1450×900)**:
  - [`practice_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/practice_1450x900.png)
  - [`practice_fullpage_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/practice_fullpage_1450x900.png)
  - [`practice_stress_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/practice_stress_1450x900.png)
  - [`home_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/home_1450x900.png)
  - [`navbar_states_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/navbar_states_1450x900.png)
  - [`navbar_states_fullpage_1450x900.png`](file:///e:/resume_project/docs/screenshots/r4/navbar_states_fullpage_1450x900.png)
- **Secondary Viewports**:
  - 1920×1080: [`practice_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r4/practice_1920x1080.png), [`practice_stress_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r4/practice_stress_1920x1080.png), [`home_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r4/home_1920x1080.png), [`navbar_states_1920x1080.png`](file:///e:/resume_project/docs/screenshots/r4/navbar_states_1920x1080.png)
  - 1600×1000: [`practice_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r4/practice_1600x1000.png), [`practice_stress_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r4/practice_stress_1600x1000.png), [`home_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r4/home_1600x1000.png), [`navbar_states_1600x1000.png`](file:///e:/resume_project/docs/screenshots/r4/navbar_states_1600x1000.png)

---

Stopped at Practice redesign mockup gate, awaiting owner approval of the Topbar Workbench mockups.

