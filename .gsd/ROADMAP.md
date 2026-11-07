---
milestone: Milestone 5 — MCQ Practice (180 Questions across 10 Categories)
version: 5.0.0
updated: 2026-11-08
---

# ROADMAP.md

> **Current Milestone**: Milestone 5 — MCQ Practice  
> **Current Phase**: Phase 9: MCQ Bank (180 Questions across 10 Categories)  
> **Status**: 💬 REGISTERED / DISCUSSING (Execution Gated: Starts after Windup Closing)

---

## Milestone 1: Premium UI Redesign (Status: ✅ Complete / Verified)

- [x] Phase 1: Static HTML Mockups & Design Tokens
- [x] Phase 2: Streamlit UI Implementation (10/10 Verification Gates Passed, Return Filed)

---

## Milestone 2: Make the Loop Smarter (Status: Complete — accepted with corrective (2026-11-07))

### Goal
Upgrade the learning loop with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review ladders with individualized memory modeling and non-adjacent topic sequencing to optimize retention.

### Phases
- **Phase 3: FSRS + Interleaving** — Status: Complete — accepted with corrective (2026-11-07)
- **Phase 4: Per-Run Resource Measurement** (Milestone 2 Backlog) — Peak memory + CPU execution time instrumentation inside judge runner; unlock `Rating.Easy`.
- **Phase 5: Attempt History & Ruff Diagnostics Panel** (Milestone 2 Backlog) — Historical attempt timeline, code diffs, inline Ruff linting.

---

## Milestone 3: Terracotta Editorial Redesign (Status: ✅ Complete / Verified)

### Goal
Redesign the application visual identity and layouts into Option 3 — **TERRACOTTA EDITORIAL**, combining the "Terracota Mediterrâneo" color architecture with a "Bento Grid Tech Minimalist" layout structure, disciplined by strict frontend feasibility, matte surfaces, and 100% authentic data truth.

### Phases
- **Phase 6: Terracotta Static Mockups & Token Sheet (T1)** — Status: ✅ Complete (Owner Approved Mockups, Rounds 1–2 + Fix Round)
- **Phase 7: Terracotta Streamlit Implementation (T2)** — Status: ✅ Complete (Phase Return Filed, Fix Round Closed, 82/82 Tests Green, Visual Captures Verified. Note: Login gate removed by owner decision 2026-11-08; auth_store.py dormant; re-enable = restore the gate call in app.py.)

---

## Milestone 4: Problem Bank Expansion (20 Problems) (Status: ✅ Complete / Verified)

### Goal
Grow the problem bank of AI Prep Coach from 12 problems to 20 by authoring 8 new problems sourced from the internet's classic problem canon — 2 Easy, 3 Medium, and 3 Hard (introducing the "Hard" difficulty tier).

### Phases
- **Phase 8: Problem Bank Expansion (8 New Problems: 2 Easy, 3 Medium, 3 Hard)**
  - Status: ✅ Complete (Authored, judge-passed 100%, 0 signature divergence, 82/82 full suite pass)

---

## Milestone 5: MCQ Practice, Quizzes & Flashcards (180 MCQs + 100 Flashcards across 10 Categories)

### Goal
Add a comprehensive technical assessment and spaced-repetition module covering 10 major programming subjects mapped from the Sanfoundry programming index taxonomy:
1. **MCQ Practice & Timed Quizzes**: 180 questions (6 Easy, 6 Medium, 6 Hard per category) in `data/mcqs/<category>.json`, authored fresh under strict no-copy law, machine-verified where runtimes exist. Features two interactive modes: Practice (instant feedback + explanation) and Timed Quiz (10 mixed questions, 10-minute countdown timer, mock-style scorecard review, `mcq_attempts` with `mode` column).
2. **Flashcards with FSRS Spaced Repetition**: 100 flashcards across the same 10 categories (10 cards/deck in `data/flashcards/<category>.json`), sharing the existing `coach/fsrs_engine.py` scheduler (`desired_retention=0.9`) with a dedicated self-grade mapper permitting `Again`, `Hard`, `Good`, `Easy`, persisting in `flashcard_fsrs_cards`, with daily new card caps (20/day) and live next-interval preview buttons.
Both screens gated behind owner-approved static Terracotta mockups (`mockups/terracotta/mcq.html` and `mockups/terracotta/flashcards.html`).

### Must-Haves
- [ ] **The No-Copy Rule (Binding)**:
  - Sanfoundry's index supplies the subject taxonomy only.
  - Every question, option set, answer key, explanation, card front, back, and tag is authored fresh in this project, in the coach's own words.
  - Zero scraping, copying, or paraphrasing.
- [ ] **10 Shared Categories**:
  - `python`, `data-structures`, `algorithms`, `oop`, `c`, `cpp`, `java`, `javascript`, `sql`, `data-science`.
- [ ] **MCQ Bank (180 MCQs total: 6 Easy, 6 Medium, 6 Hard each)**:
  - Schema in `data/mcqs/<category>.json`: `id`, `category`, `difficulty`, `kind`, `question`, `options` (exactly 4), `answer_index` (0–3), `explanation` (1–3 sentences).
  - Roughly even answer-index distribution across 0–3 per category (no clustering).
- [ ] **Flashcard Bank (100 Flashcards total: 10 per category)**:
  - Schema in `data/flashcards/<category>.json`: `id`, `category`, `front`, `back`, `tag`.
- [ ] **Verification Standard (B1 Equivalent)**:
  - 100% of Python output questions and card code facts machine-verified via Python 3.12 sandbox; observed output equals keyed answer option text.
  - JavaScript output questions machine-verified via Node.js.
  - C, C++, Java, and SQL: 100% `concept`-kind questions (zero unverified output predictions, since no local compiler exists).
  - Independent 20% sample re-derivation audit with 100% resolved agreement.
  - 180-question schema census report + 100-card census report.
- [ ] **FSRS Reuse & Boundary Doctrine**:
  - Reuses `coach/fsrs_engine.py` scheduler (`fsrs==6.3.2`, default parameters, `desired_retention=0.9`).
  - Table: `flashcard_fsrs_cards` (card_id, state, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review, due) keyed on `card_id`.
  - Flashcard self-grade rating mapper emits `Again` (1), `Hard` (2), `Good` (3), `Easy` (4) with live next-interval calculation.
  - Coding problem rating mapper in `coach/fsrs_engine.py` remains **strictly frozen and untouched** (`Rating.Easy` remains strictly forbidden for judge verdicts).
- [ ] **Terracotta Screen & Mockup Gates**:
  - Phase 10 Mockup: `mockups/terracotta/mcq.html` showing Practice Mode, Timed Quiz Mode (timer, locked submission), and Quiz Scorecard. Approved by owner before implementation.
  - Phase 11 Mockup: `mockups/terracotta/flashcards.html` showing Deck Picker with live counts (due / new / total), card review flow (Front -> Show Answer -> Back -> 4 interval buttons), session summary, no JS flip animations (clean state toggle). Approved by owner before implementation.
- [ ] **Persistence & Analytics**:
  - `mcq_attempts` table schema: `(id, category, difficulty, question_id, selected_index, correct, mode, timestamp)` with `mode` in `('practice', 'quiz')`.
  - `flashcard_fsrs_cards` tracking card states and reviews.

### Phases
- **Phase 9: MCQ Bank (180 Questions across 10 Categories)**
  - Status: 💬 DISCUSSING / PLANNING
  - Objective: Define schema, author 180 fresh MCQs across 10 categories, machine-verify output questions, conduct 20% independent derivation audit, and file bank census.
- **Phase 10: MCQ & Quiz Screen (Practice + Timed Quiz Modes, Mockup Gate)**
  - Status: 🔒 GATED (Starts after Phase 9 & Owner Mockup Approval)
  - Objective: Author static Terracotta mockup (`mockups/terracotta/mcq.html`), secure owner approval, implement Streamlit screen with Practice and Timed Quiz modes, `mcq_attempts` table with `mode` column, and verify via CDP captures.
- **Phase 11: Flashcards (100 Cards, FSRS Reuse & Review Screen)**
  - Status: 🔒 GATED (Starts after Phase 10 & Owner Mockup Approval)
  - Objective: Author 100 flashcards across 10 categories, verify Python/Node facts, reuse FSRS scheduler with `flashcard_fsrs_cards` and 4-button self-grader, author `mockups/terracotta/flashcards.html`, implement review screen with 20 new cards/day cap, and verify via CDP captures.

---

## Progress Summary

| Milestone | Phase | Status | Objective |
| :--- | :--- | :--- | :--- |
| **M1** | Phase 1 | ✅ Complete | Static HTML mockups & Direction A tokens |
| **M1** | Phase 2 | ✅ Complete | Streamlit UI implementation & 10-gate audit |
| **M2** | Phase 3 | ✅ Complete | FSRS scheduler swap & interleaved review queue |
| **M2** | Phase 4 | ⏳ Backlog | Per-run memory & CPU resource measurement |
| **M2** | Phase 5 | ⏳ Backlog | Attempt history timeline & live Ruff diagnostics |
| **M3** | Phase 6 | ✅ Complete | Terracotta static HTML mockups & token sheet (T1) |
| **M3** | Phase 7 | ✅ Complete | Terracotta Streamlit implementation & Auth (T2) |
| **M4** | Phase 8 | ✅ Complete | Problem Bank Expansion (8 new problems: 2E, 3M, 3H; 20 total) |
| **M5** | Phase 9 | 💬 Discussing | MCQ Bank (180 MCQs, 10 categories, machine-verified) |
| **M5** | Phase 10| 🔒 Gated | MCQ & Quiz Screen (Practice + Timed Quiz, Terracotta Mockup Gate) |
| **M5** | Phase 11| 🔒 Gated | Flashcards (100 cards, FSRS scheduler reuse, Terracotta Mockup Gate) |

---

*Last updated: 2026-11-08*
