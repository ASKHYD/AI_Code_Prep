# SPEC.md — Project Specification

> **Status**: `MILESTONE 2 REGISTERED`
>
> ⚠️ **Planning Lock**: Milestone 1 complete & verified; Milestone 2 Phase 3 defined.

---

## Vision
AI Coding Prep Coach is a local, zero-cost coding-interview practice platform built with Streamlit.

- **Milestone 1 (Complete)**: Transformed the visual experience from an uninspired dark UI into a warm, delightful, Brilliant-style light learning environment ("Direction A") featuring a warm paper background, ink typography (Fraunces headings + Inter body), pastel topic tints, tactile rounded cards, and pill buttons.
- **Milestone 2 (Current)**: "Make the Loop Smarter." Upgrades the learning engine with modern adaptive spaced repetition (FSRS) and cognitive interleaving, replacing static review intervals with individualized memory modeling and interleaving problem topics to optimize retention for coding interviews.

---

## Milestone 1: Premium UI Redesign (Status: Complete / Verified)
1. **Design System & Token Specification** — Direction A design tokens established in `DESIGN.md`.
2. **Phase 1: High-Fidelity Static Mockups** — Standalone HTML mockups and dual-resolution captures approved.
3. **Phase 2: Streamlit Theme & UI Implementation** — Topbar workbench and responsive layout implemented, 10/10 verification gates passed, verified 31/31 pytest.

---

## Milestone 2: Make the Loop Smarter

### Phase 3: FSRS + Interleaving
The first phase of Milestone 2 contains exactly two sequential workstreams:

#### Workstream 1 — FSRS Scheduler Swap
- **Dependency**: `fsrs` (py-fsrs, MIT) via pip, pinned in `requirements.txt`. Load-or-report-MISSING gate before any code. Fully offline after install.
- **Data Model**: One FSRS Card per problem; card state (JSON from py-fsrs) stored in SQLite alongside existing store (`coach.db`). The `attempts` table remains the immutable history of record and is NOT rewritten.
- **Judge-to-Rating Mapping** (Binding):
  - `FAIL` or `TIMEOUT` $\rightarrow$ `Rating.Again`
  - `PASS` with `hints_used > 0` OR `attempts_on_problem > 1` $\rightarrow$ `Rating.Hard`
  - Clean first-attempt `PASS` with no hints $\rightarrow$ `Rating.Good`
  - `Rating.Easy` is **NOT emitted** in this phase (no trustworthy execution speed signal exists until resource measurement lands in a later phase).
- **Scheduler Configuration**: py-fsrs default parameters only; `desired_retention = 0.9`. The FSRS optimizer is **FORBIDDEN** in this phase (review volume is too small for empirical parameter optimization).
- **Due Semantics**: A problem is due when its card's due timestamp $\le$ `now`. Home screen due count/chip, the practice queue, and Dashboard read from FSRS state. Streak semantics remain activity-based and unchanged.
- **Migration & Idempotency** (Critical):
  - Existing attempt data carries over with zero loss.
  - For each problem with historical attempts, seed its FSRS card from attempt history (last outcome drives initial review: e.g. a passed problem receives a `Good` review at its last attempt timestamp; a failed one receives `Again`).
  - Migration must be verified on a copy of `coach.db` first.
  - Real database SHA256 recorded before and after the phase; real DB is migrated strictly via the shipped code path once.
  - Migration is strictly idempotent: running it multiple times produces identical state.
- **Rollback & Old Ladder Disposition**: The old ladder function (`coach.repetition.calculate_due_date` / `calculate_next_due`) is retired from the scheduling path. Git history serves as rollback; tasks executed as atomic commits.
- **Truth-in-Copy**: No UI copy may describe the old ladder. Replace Home subline `"Interview-targeted spaced repetition schedule (1 / 1 / 3 / 7 / 21 days)..."` with truthful FSRS copy: `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`

#### Workstream 2 — Interleaved Review Queue
- **Interleaving Invariant**: The review queue (Home daily queue + SRS-driven practice order) and mock problem selection must never place two problems of the same topic adjacently when an alternative topic exists.
- **Topic Sampling**: Selection samples across topics weighted by due-ness first, then weakest topic (from `topic_stats`).
- **Free Picking Intact**: Practice Arena problem picker remains free — candidates can pick and solve any problem in any order. Interleaving applies strictly to system-generated review/mock queues.
- **First Exposure**: Brand-new topic introductions may remain in roadmap order (blocked first exposure); interleaving applies to review and consolidation.

---

## Milestone 2 Backlog (Later Phases)
1. **Per-Run Resource Measurement**: Peak memory allocation and precise CPU execution time instrumentation inside the judge runner; generates trustworthy execution speed signals to unlock `Rating.Easy`.
2. **Attempt History & Ruff Diagnostics Panel**: Historical timeline of attempts with diff view, code evolution, and live Ruff lint/style feedback in the Practice Arena.

---

## Entry Gates (Binding)
- **Gate G1**: Backend verification battery (`BACKEND_VERIFICATION.md`) filed and triaged (Filed: all 12 reference solutions pass, database SHA256 verified 100% untouched).
- **Gate G2**: Phase 2 formally closed: owner live approval + pre-authorized closure bookkeeping complete. (Execution of Phase 3 code waits for G2).

---

## Constraints & Freezes
- **Problem Bank Content Frozen**: `data/problems/*.json` statements, starter code, and test cases untouched.
- **Judge Execution Semantics Frozen**: `coach.judge` test execution rules and timeout limits untouched.
- **UI Design System Frozen**: Direction A tokens (`DESIGN.md`), fonts, colors, and layout untouched, except the truth-in-copy line on Home.

---

*Last updated: 2026-11-06*
