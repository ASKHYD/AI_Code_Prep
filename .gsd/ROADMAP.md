---
milestone: Milestone 4 — Problem Bank Expansion (20 Problems)
version: 4.0.0
updated: 2026-11-07
---

# ROADMAP.md

> **Current Milestone**: Milestone 4 — Problem Bank Expansion (20 Problems)  
> **Current Phase**: Phase 8: Problem Bank Expansion  
> **Status**: 💬 DISCUSSING / PLANNING (Execution Gated: Starts after Terracotta Phase 7 Shipped)

---

## Milestone 1: Premium UI Redesign (Status: ✅ Complete / Verified)

- [x] Phase 1: Static HTML Mockups & Design Tokens
- [x] Phase 2: Streamlit UI Implementation (10/10 Verification Gates Passed, Return Filed)

---

## Milestone 2: Make the Loop Smarter (Status: Complete — accepted with corrective (2026-11-07))

### Goal
Upgrade the learning loop with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review ladders with individualized memory modeling and non-adjacent topic sequencing to optimize retention.

### Must-Haves
- [x] **Dependency Gate**: `fsrs==6.3.2` installed and pinned in `requirements.txt`.
- [x] **FSRS Scheduler Swap (Workstream 1)**:
  - FSRS card state persistence table in SQLite (`coach.db`).
  - Strict judge-to-rating mapping (`Again`, `Hard`, `Good`; `Easy` omitted).
  - Default parameters with `desired_retention = 0.9` (optimizer forbidden).
  - Zero-loss, idempotent migration from historical attempts on DB copy with A1 last-attempt timestamps.
  - Retirement of old ladder function from scheduling path (0 callers).
  - Truth-in-copy: replace 21-day schedule text on Home with FSRS explanation.
- [x] **Interleaved Review Queue (Workstream 2)**:
  - Review and mock queue generators forbid adjacent same-topic problems when alternatives exist.
  - Topic sampling weighted by due-ness first, then weakest topic pass rate.
  - Free problem picker in Practice Arena remains untouched.
- [x] **Empirical Verification Suite**:
  - Rating mapping unit tests covering all outcome branches (15 tests).
  - Database migration idempotency and correctness tests.
  - Due-set equivalence check between old ladder and FSRS.
  - Interleaving adjacency test on multi-topic problem sets.
  - All 57 tests green in 17.22s.
  - Live 1450×900 browser capture of Home screen showing FSRS due chip and queue.

### Phases
- **Phase 3: FSRS + Interleaving** — Status: Complete — accepted with corrective (2026-11-07)
- **Phase 4: Per-Run Resource Measurement** (Milestone 2 Backlog) — Peak memory + CPU execution time instrumentation inside judge runner; unlock `Rating.Easy`.
- **Phase 5: Attempt History & Ruff Diagnostics Panel** (Milestone 2 Backlog) — Historical attempt timeline, code diffs, inline Ruff linting.

---

## Milestone 3: Terracotta Editorial Redesign (Status: ✅ Complete / Verified)

### Goal
Redesign the application visual identity and layouts into Option 3 — **TERRACOTTA EDITORIAL**, combining the "Terracota Mediterrâneo" color architecture with a "Bento Grid Tech Minimalist" layout structure, disciplined by strict frontend feasibility, matte surfaces, and 100% authentic data truth.

### Must-Haves
- [x] Design Tokens & System Sheet (`DESIGN.md`, self-hosted `.woff2` typography, matte surfaces).
- [x] Screen Layouts & Bento Structure (Home bento, Practice Arena, Mock Interview cycle, Dashboard pass-rate chart above table).
- [x] Preservations & Freezes (Topbars, streak/due live chips, FSRS integration, DB immutability).
- [x] Phase 6 (T1) Mockups & Phase 7 (T2) Streamlit implementation complete (71/71 tests green, 14 CDP captures, zero slop).

### Phases
- **Phase 6: Terracotta Static Mockups & Token Sheet (T1)** — Status: ✅ Complete (Owner Approved Mockups, Rounds 1–2 + Fix Round)
- **Phase 7: Terracotta Streamlit Implementation (T2)** — Status: ✅ Complete (Phase Return Filed, 71/71 Tests Green, 14 CDP Captures)

---

## Milestone 4: Problem Bank Expansion (20 Problems)

### Goal
Grow the problem bank of AI Prep Coach from 12 problems to 20 by authoring 8 new problems sourced from the internet's classic problem canon — 2 Easy, 3 Medium, and 3 Hard (introducing the "Hard" difficulty tier). Maintain strict Bank Law: 100% JSON schema conformance, original non-scraped descriptions, starter code signature doctrine (0 divergence), 3-level offline hints, judge-verified reference solutions, FSRS seed migration, and UI tier support.

### Must-Haves
- [ ] **8 New Problems** added to `data/problems/*.json`:
  - 2 Easy: Merge Sorted Array (`arrays`), Maximum Depth of Binary Tree (`tree-traversal`).
  - 3 Medium: Group Anagrams (`strings` / `dict-processing`), Coin Change (`dp`), Course Schedule (`graphs` / `recursion`).
  - 3 Hard: Trapping Rain Water (`two-pointers`), Median of Two Sorted Arrays (`binary-search`), Word Ladder (`strings` / `string-parsing`).
- [ ] **Bank Law Compliance**:
  - Same JSON schema as existing 12 problems, 0 missing fields across all 13 keys.
  - Each problem defines $\ge 2$ visible tests and $\ge 5$ hidden tests.
  - Reference solution passes 100% of its tests through the real judge (B1 standard).
  - Original wording in house style; no verbatim scraping or copying from LeetCode or public sites.
  - Starter code line 1 is single source of truth for signature (`STARTER FUNCTION SIGNATURE` == line 1, 0 divergence).
  - 3-level offline hint ladder (concept -> approach -> near-code) for Ollama-off operation.
- [ ] **UI Difficulty Tier Integration**:
  - "Hard" difficulty accepted and styled everywhere difficulty is rendered (`badge-terracotta`, picker `(Hard)`, queue colored text, problem cards).
- [ ] **Integration Proofs**:
  - Judge battery on new 8: reference PASS on all tests, defective solution FAIL with expected/got.
  - Full-bank census re-run: 20/20 parse, 0 missing fields, 0 divergence.
  - FSRS scratch migration: seeds cards for all 20 problems, idempotent on re-run; real `coach.db` SHA256 untouched.
  - Existing test suite (71 baseline) remains 100% green + new bank tests.
  - Live count refresh across UI: Home queue "1 / 20", Problem Card "Problem 1 of 20", Dashboard coverage, mockup specimens refreshed.
  - Interleaving verification: queue generation preserves zero same-topic adjacency over the 20-problem bank.
- [ ] **Freezes Maintained**:
  - Judge runner semantics untouched.
  - FSRS engine and rating map untouched.
  - Terracotta tokens and CSS styles untouched.
  - Existing 12 problem JSON files strictly read-only.

### Phases
- **Phase 8: Problem Bank Expansion (8 New Problems: 2 Easy, 3 Medium, 3 Hard)**
  - Status: 💬 DISCUSSING / PLANNING
  - Objective: Author 8 original problem JSONs, implement "Hard" UI tier handling, run judge battery and census validation, test FSRS seed migration on scratch DB, and verify UI count refresh.

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
| **M4** | Phase 8 | 💬 Discussing | Problem Bank Expansion (8 new problems: 2E, 3M, 3H) |

---

*Last updated: 2026-11-07*
