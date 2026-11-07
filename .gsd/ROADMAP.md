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
- **Phase 7: Terracotta Streamlit Implementation (T2)** — Status: ✅ Complete (Phase Return Filed, Fix Round Closed, 82/82 Tests Green, Visual Captures Verified)

---

## Milestone 4: Problem Bank Expansion (20 Problems) (Status: ✅ Complete / Verified)

### Goal
Grow the problem bank of AI Prep Coach from 12 problems to 20 by authoring 8 new problems sourced from the internet's classic problem canon — 2 Easy, 3 Medium, and 3 Hard (introducing the "Hard" difficulty tier).

### Phases
- **Phase 8: Problem Bank Expansion (8 New Problems: 2 Easy, 3 Medium, 3 Hard)**
  - Status: ✅ Complete (Authored, judge-passed 100%, 0 signature divergence, 82/82 full suite pass)

---

## Milestone 5: MCQ Practice (180 Questions across 10 Categories)

### Goal
Add a dedicated Multiple Choice Question (MCQ) Practice module covering 10 major programming subjects mapped from the Sanfoundry programming index taxonomy, each with 18 questions (6 Easy, 6 Medium, 6 Hard) for 180 total questions. Every question is authored fresh under strict no-copy law, machine-verified where runtimes exist, and presented in an owner-approved Terracotta practice interface with instant feedback and session scoring.

### Must-Haves
- [ ] **The No-Copy Rule (Binding)**:
  - Sanfoundry's index supplies the subject taxonomy only.
  - Every question, option set, answer key, and explanation is authored fresh in this project, in the coach's own words.
  - Zero scraping, copying, or paraphrasing.
- [ ] **10 Categories (180 MCQs total: 6 Easy, 6 Medium, 6 Hard each)**:
  - `python`, `data-structures`, `algorithms`, `oop`, `c`, `cpp`, `java`, `javascript`, `sql`, `data-science`.
- [ ] **Data Model Discipline (`data/mcqs/<category>.json`)**:
  - `id`, `category`, `difficulty`, `kind`, `question`, `options` (exactly 4), `answer_index` (0–3), `explanation` (1–3 sentences).
  - Roughly even answer-index distribution across 0–3 per category (no clustering).
- [ ] **Verification Standard (B1 Equivalent)**:
  - 100% of Python output questions machine-verified via Python 3.12 sandbox; observed output equals keyed answer option text.
  - JavaScript output questions machine-verified via Node.js.
  - C, C++, Java, and SQL: 100% `concept`-kind questions (zero unverified output predictions, since no local compiler exists).
  - Independent 20% sample re-derivation audit with 100% resolved agreement.
  - 180-question schema census report.
- [ ] **Terracotta Screen & Mockup Gate**:
  - Static HTML mockup at `mockups/terracotta/mcq.html` approved by owner before implementation.
  - Topbar nav destination "MCQ Practice".
  - One-at-a-time quiz flow: radio selection, submit -> instant verdict (olive correct / terracotta wrong) + explanation, running session score, end summary.
  - Persistence in `mcq_attempts` table (`category`, `difficulty`, `correct`, `timestamp`).
  - Dashboard & FSRS out of scope (honestly omitted from UI copy).

### Phases
- **Phase 9: MCQ Bank (180 Questions across 10 Categories)**
  - Status: 💬 DISCUSSING / PLANNING
  - Objective: Define schema, author 180 fresh MCQs across 10 categories, machine-verify output questions, conduct 20% independent derivation audit, and file bank census.
- **Phase 10: MCQ Screen (Terracotta Mockup Gate + Implementation)**
  - Status: 🔒 GATED (Starts after Phase 9 & Owner Mockup Approval)
  - Objective: Author static Terracotta mockup (`mockups/terracotta/mcq.html`), secure owner approval, implement Streamlit screen and `mcq_attempts` table, and verify via CDP captures.

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
| **M5** | Phase 10| 🔒 Gated | MCQ Screen (Terracotta Mockup Gate + Streamlit Screen) |

---

*Last updated: 2026-11-08*
