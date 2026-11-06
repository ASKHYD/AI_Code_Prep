---
phase: 6
plan: "02"
wave: 2
depends_on: ["01"]
---

# Plan 6.2: Core Screen Mockups with Real Data (Home, Practice, Dashboard)

## Objective
Implement static HTML/CSS mockups for the three primary application workflows: Home Screen, Practice Arena, and Dashboard. Enforce 100% authentic data truth by populating cards and tables strictly from the active 12-problem bank and current store metrics (2 attempts, 1 solved, current streak), with zero generator fiction.

## Context
- `.gsd/SPEC.md`
- `.gsd/phases/6/DISCUSS.md`
- `mockups/terracotta/style.css`
- `mockups/home.html` (Phase 1 reference)
- `mockups/practice.html` (Phase 1 reference)
- `mockups/dashboard.html` (Phase 1 reference)
- `coach/store.py` (runtime data schema)
- `data/problems/*.json` (problem bank)

---

## Tasks

<task type="auto">
  <name>Task 2.1: Implement Home Screen & Practice Arena Mockups</name>
  <files>mockups/terracotta/home.html, mockups/terracotta/practice.html</files>
  <action>
    <!-- Skill binding: /agency-frontend-developer + /ui-ux-pro-max -->
    1. Create `mockups/terracotta/home.html`:
       - Full-bleed sticky topbar at top 0 with DM Serif wordmark, nav pills (Home active in Terracotta underline), and right-side streak (Olive) + due (Terracotta) chips.
       - Display headline: DM Serif Display "Today's Practice".
       - Primary action: Terracotta pill button ("Start Daily Practice").
       - 3 Bento stat tiles:
         - Day Streak: Olive `#6B7F3B` icon and numeral (1 day).
         - Due for Review: Terracotta `#C2452D` chip/numeral (1 due).
         - Problems Mastered / Solved: Warm ink numeral (1 solved of 12).
       - De-slopped Daily Practice Queue:
         - Real problems from store / interleaving (e.g. Two Sum, Valid Palindrome, Reverse Linked List).
         - Rule: Maximum ONE status pill per row. Topic (Arrays & Hashing, Two Pointers) and difficulty (Easy, Medium) rendered as clean colored text, NOT nested chips.
         - Truthful copy verbatim: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
    2. Create `mockups/terracotta/practice.html`:
       - Page-scroll two-pane workbench (no independent scroll promises).
       - Left Pane:
         - Slim problem picker row (X5R) with arrow buttons (`←` and `→`) and selectbox showing real problem (e.g. `1. Two Sum · Easy · Arrays & Hashing`).
         - Problem Card: serif problem title, topic/difficulty badges, statement markdown, wash-chip inline code (`vector<int>`, `target`).
         - Small-caps signature block header: `<span class="signature-subhead">STARTER FUNCTION SIGNATURE</span>`.
         - Single-source-of-truth signature code snippet matching `starter_code` first line.
         - Progressive Hint Ladder with expandable hint card in sandy panel `#E8D5B7`.
       - Right Pane:
         - Dark anchor code editor card (`#1E1E1E` background) with Python 3.12 syntax, line numbers, and starter code. Editor internals are NOT restyled.
         - Output Card: test results container with natural-width right-aligned Run & Submit buttons.
  </action>
  <verify>.venv\Scripts\python.exe -c "import os; assert os.path.isfile('mockups/terracotta/home.html') and os.path.isfile('mockups/terracotta/practice.html'); print('Home & Practice mockups exist')"</verify>
  <done>`mockups/terracotta/home.html` and `mockups/terracotta/practice.html` implemented with authentic data and verified.</done>
</task>

<task type="auto">
  <name>Task 2.2: Implement Dashboard Mockup with Bento Tiles & Topic Chart</name>
  <files>mockups/terracotta/dashboard.html</files>
  <action>
    <!-- Skill binding: /agency-frontend-developer + /ui-ux-pro-max -->
    1. Create `mockups/terracotta/dashboard.html`:
       - Full-bleed sticky topbar with Dashboard active.
       - Bento metric cards: Overall Pass Rate, Total Attempts (2), Solved Problems (1/12), FSRS Retention Target (90%).
       - Topic Mastery & Pass Rates horizontal bar chart positioned ABOVE the problem table:
         - Visualized using Terracotta palette: Olive for passed/mastered (Arrays & Hashing 100%), Clay/Terracotta for in-progress or failed, Sandy/Warm Gray for unattempted.
         - Attempted topics render authentic store statistics; unattempted topics render `NOT STARTED`.
       - Problem Inventory Table:
         - Lists the real 12 problems grouped by topic.
         - Columns: Problem, Topic, Difficulty, Attempts, Last Status (PASS in Olive, FAIL in Terracotta, NOT ATTEMPTED in Neutral Gray), FSRS State.
         - De-slopped styling: clean row borders, tabular semibold metric numbers.
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('mockups/terracotta/dashboard.html').read(); assert 'Topic Mastery' in content and 'NOT STARTED' in content; print('Dashboard mockup valid')"</verify>
  <done>`mockups/terracotta/dashboard.html` implemented with authentic data and chart placement above table.</done>
</task>

---

## Must-Haves
After all tasks complete, verify:
- [ ] Real 12 problems used throughout; 0 invented problem names.
- [ ] Real user data (2 attempts, 1 solved) reflected accurately in metrics.
- [ ] Max 1 status pill per row in queues/tables.
- [ ] Practice Arena retains slim picker row, small-caps signature label, dark anchor editor, and right-aligned buttons.
- [ ] Dashboard chart is positioned above the problem table.

## Success Criteria
- [ ] All 3 core mockups render cleanly in browser without console errors.
- [ ] Design constraints (matte, 24px radius, 1px warm hairlines) strictly maintained.
