---
milestone: Milestone 2 — Make the Loop Smarter
version: 2.0.0
updated: 2026-11-06
---

# ROADMAP.md

> **Current Milestone**: Milestone 2 — Make the Loop Smarter  
> **Current Phase**: Phase 3: FSRS + Interleaving  
> **Status**: 💬 Discussing / Planning (Execution gated by G1 & G2)

---

## Milestone 1: Premium UI Redesign (Status: ✅ Complete / Verified)

- [x] Phase 1: Static HTML Mockups & Design Tokens
- [x] Phase 2: Streamlit UI Implementation (10/10 Verification Gates Passed, Return Filed)

---

## Milestone 2: Make the Loop Smarter

### Goal
Upgrade the learning loop with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review ladders with individualized memory modeling and non-adjacent topic sequencing to optimize retention.

### Must-Haves
- [ ] **Dependency Gate**: `fsrs` (py-fsrs) installed and pinned in `requirements.txt`.
- [ ] **FSRS Scheduler Swap (Workstream 1)**:
  - FSRS card state persistence table in SQLite (`coach.db`).
  - Strict judge-to-rating mapping (`Again`, `Hard`, `Good`; `Easy` omitted).
  - Default parameters with `desired_retention = 0.9` (optimizer forbidden).
  - Zero-loss, idempotent migration from historical attempts on DB copy.
  - Retirement of old ladder function from scheduling path.
  - Truth-in-copy: replace 21-day schedule text on Home with FSRS explanation.
- [ ] **Interleaved Review Queue (Workstream 2)**:
  - Review and mock queue generators forbid adjacent same-topic problems when alternatives exist.
  - Topic sampling weighted by due-ness first, then weakest topic pass rate.
  - Free problem picker in Practice Arena remains untouched.
- [ ] **Empirical Verification Suite**:
  - Rating mapping unit tests covering all outcome branches.
  - Database migration idempotency and correctness tests.
  - Due-set equivalence check between old ladder and FSRS.
  - Interleaving adjacency test on multi-topic problem sets.
  - All 31 existing tests + new tests green.
  - Live 1450×900 browser capture of Home screen showing FSRS due chip and queue.

---

## Phases

### Phase 1: Static HTML Mockups & Design Tokens
**Status**: ✅ Complete  
**Objective**: Build pixel-perfect static HTML/CSS mockups of Home, Practice, Mock, and Dashboard along with a design token sheet implementing Direction A.

---

### Phase 2: Streamlit UI Implementation
**Status**: ✅ Complete / Closed (Owner Live Approved)  
**Objective**: Implement approved Direction A topbar workbench, responsive layouts, Plotly dashboard chart, slim picker row, and design tokens in Streamlit. 10/10 verification gates passed, pytest 31/31. Formal live approval granted 2026-11-07.

---

### Phase 3: FSRS + Interleaving
**Status**: 💬 Discussing / Planning (Execution Gated by G1 & G2)  
**Objective**: Replace the deterministic 1/1/3/7/21-day review ladder with py-fsrs adaptive spaced repetition and implement cognitive topic interleaving for review and mock queues.  
**Depends on**: Entry Gate G1 (Backend Verification Battery triaged) & Gate G2 (Phase 2 Owner Live Approval).  
**Workstreams**:
1. *Workstream 1*: FSRS Scheduler Swap (Dependency, Card State SQLite, Rating Mapping, Idempotent Migration, Old Ladder Removal, Truth-in-Copy).
2. *Workstream 2*: Interleaved Review Queue (Non-adjacent topic sequencing, Due-weighted sampling, Practice picker preservation).

---

## Milestone 2 Backlog (Future Phases)

- **Phase 4**: Per-Run Resource Measurement (peak memory + CPU execution time instrumentation inside judge runner; unlock `Rating.Easy`).
- **Phase 5**: Attempt History & Ruff Diagnostics Panel (historical attempt timeline, code diffs, inline Ruff linting).

---

## Progress Summary

| Milestone | Phase | Status | Objective |
| :--- | :--- | :--- | :--- |
| **M1** | Phase 1 | ✅ Complete | Static HTML mockups & Direction A tokens |
| **M1** | Phase 2 | ✅ Verified | Streamlit UI implementation & 10-gate audit |
| **M2** | Phase 3 | 💬 Discussing | FSRS scheduler swap & interleaved review queue |
| **M2** | Phase 4 | ⏳ Backlog | Per-run resource measurement (memory & time) |
| **M2** | Phase 5 | ⏳ Backlog | Attempt history timeline & Ruff diagnostics panel |

---

*Last updated: 2026-11-06*
