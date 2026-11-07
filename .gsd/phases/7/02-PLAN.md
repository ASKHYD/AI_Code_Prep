# Wave 2: Home Bento & Dashboard Implementation

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.2 (Wave 2)  
**Status**: DRAFT — READY FOR AUDIT  

---

## 1. Plan Overview

Wave 2 rebuilds the Home and Dashboard views in `app.py` to match the approved Terracotta Editorial specifications (`home.html` and `dashboard.html`):
1. Restyles the Home hero and bento stat grid (Active Streak, Problems Due Today, Target Retention), enforcing tabular semibold numerals and the verbatim FSRS explanatory copy.
2. Formats the system-generated Home Problem Queue into a tactile 24px bento container, preserving all Phase 3 corrective logic (C3 due-first partitioning, C2 amber `DUE FOR REVIEW` pills, dynamic `Next Due: +N Day(s)` deltas, and zero adjacent topic collisions).
3. Restyles the Dashboard with a dedicated Plotly pass-rate chart for ATTEMPTED topics only placed ABOVE the full topic table, themed in Terracotta colors.
4. Renders the full 11-topic mastery table below, displaying `NOT STARTED` for unattempted rows (never 0%).

---

## 2. Tasks

### Task 2.1: Home Screen Bento Layout & Verified FSRS Copy
- **Actions**:
  - Update `Home` view in `app.py`:
    - Hero title in `DM Serif Display`: "Today's Practice", subline "Focus on high-yield retention and cognitive variety."
    - Stat Bento Cards (3-column layout, 24px white containers with warm hairline):
      1. **Active Streak Tile**:
         - Label: `ACTIVE STREAK`
         - Metric: `{N} day` or `{N} days` in `Plus Jakarta Sans` bold tabular numeral.
         - Status: Olive pill `ACTIVE` if streak > 0, else quiet warm gray `NOT STARTED`.
         - Subtitle: `Consecutive active days.`
      2. **Problems Due Today Tile**:
         - Label: `PROBLEMS DUE TODAY`
         - Metric: `{len(due_list)} due` in tabular numeral.
         - Subtitle: `Scheduled by FSRS algorithm.`
      3. **Target Retention Tile**:
         - Label: `TARGET RETENTION`
         - Metric: `90.0%` in tabular numeral.
         - Subtitle: `Adaptive memory optimizer.`
    - Primary CTA Pill:
      - "Start Daily Practice" styled with `#C2452D` background, `#FFF8F0` text, 9999px pill radius.
    - Verified FSRS Explanation Strip (sandy quiet panel `#E8D5B7`):
      - Verbatim copy: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
- **Verification**:
  - Live browser check: Bento cards match `mockups/terracotta/home.html`.
  - Numerals render in tabular semibold sans (not monospace).

### Task 2.2: Home Problem Queue Table (Terracotta Styling with C1–C3 Logic)
- **Actions**:
  - Refactor the queue table container in `app.py`:
    - Wrap in a 24px white card with warm hairline and header "Recommended Practice Queue", subline "Interleaved topic sequence prioritized by memory decay and weakness."
    - Table columns: `PROBLEM`, `TOPIC`, `DIFFICULTY`, `STATUS / NEXT REVIEW`, `ACTION`.
    - Rows derived from `build_interleaved_queue(all_problems, topic_stats=store.topic_stats(), due_problems=due_list)`:
      - Due problems placed first (C3).
      - Due problems render amber pill `<span class="stat-badge badge-amber">DUE FOR REVIEW</span>` and subtitle `"Due for review · Scheduled by FSRS"` (C2).
      - Solved non-due problems render mint/olive pill `<span class="stat-badge badge-mint">Next Due: +{N} Day(s)</span>` computed from `card.due` relative to today (C2).
      - Unattempted problems render quiet gray pill `Unattempted`.
      - Topic badges: themed subtle washes (`#1565C0` for algorithms, `#6B7F3B` for data structures).
      - Difficulty indicator: `Easy` (olive `#6B7F3B`), `Medium` (terracotta `#C2452D`), `Hard` (deep-fig `#4A1942`).
      - Seam verification: Zero adjacent problems share a topic.
- **Verification**:
  - Inspect live queue table at 1450×900: First row is Binary Search with `DUE FOR REVIEW` amber pill, second row is Maximum Subarray Sum (`arrays`), zero table overflow.

### Task 2.3: Dashboard View — Attempted Chart Above Full Topic Table
- **Actions**:
  - Update `Dashboard` view in `app.py`:
    - Hero title in `DM Serif Display`: "Performance & Retention", subline "Objective mastery tracked across data structures and algorithms."
    - Summary Metrics Strip: Total attempts, overall pass rate, and problems practiced in 24px bento cards.
    - **Attempted Topics Pass Rate Chart (Plotly)**:
      - Sourced exclusively from `store.topic_stats()`.
      - Filters topics to only those with `attempts > 0` (today: Binary Search alone, 50.0%).
      - Placed strictly **ABOVE** the full topic table.
      - Themed with Terracotta Plotly palette:
        - Bar color: Olive `#6B7F3B` for $\ge 70\%$, Terracotta `#C2452D` for $< 70\%$.
        - Background: `#FFFFFF`, gridlines `rgba(74, 25, 66, 0.08)`.
        - Fonts: `Plus Jakarta Sans` for labels and hover text.
    - **Full Topic Mastery Table**:
      - Placed below the chart.
      - Lists all 11 topics from `store.topic_stats()`.
      - Attempted rows show attempts, passed count, and computed pass rate.
      - Unattempted rows display status `NOT STARTED` with muted styling (never `0%`).
      - Meta-captions and specimen notes removed per fix round F2.
- **Verification**:
  - Live inspection: Plotly chart renders above table showing only attempted topics; unattempted rows in table read `NOT STARTED`.
