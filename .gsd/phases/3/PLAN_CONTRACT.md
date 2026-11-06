# Phase 3 Plan Contract & Plan-Checker Validation

**Phase**: Milestone 2, Phase 3: FSRS + Interleaving  
**Date**: 2026-11-07  
**Scope Source**: Block M2 (`MILESTONE-2-DISCUSS-BLOCK.md`) & Milo Audit Briefing (`BLOCK P3`)  
**Status**: PLANNING COMPLETE — GATED BEFORE EXECUTION  

---

## 1. Execution Gate (Verbatim Binding)

> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**

- **Gate G1 Status**: **VERIFIED**. Backend verification battery audited by Milo 2026-11-07: B1–B7 pass, real-DB SHA256 identical (`ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`), defects NONE functional. The B6 signature divergence finding belongs to Phase 2 Addendum V2 and is strictly excluded from Phase 3 scope.
- **Gate G2 Status**: **PENDING**. Phase 2 live approval on `http://localhost:8501` and pre-authorized closure bookkeeping required before `/execute 3`.

---

## 2. Audit Corrections & Scope Reconciliation

Where the Phase 3 discussion output and Block M2 differed, Block M2 governs:
1. **Milo Audit Correction A1 (Migration Timestamp)**:
   - *Resolution*: A seeded card's initial review is recorded strictly **at the problem's last attempt timestamp** (`attempts.created_at`), NOT at migration time. This ensures due dates are modeled continuously from real historical practice rather than resetting to `now + interval`. Planned in Plan 3.1 Task 1.3 and verified in Plan 3.4 Task 4.1.
2. **Milo Audit Correction A2 (Gate State Representation)**:
   - *Resolution*: G1 is accurately acknowledged as verified/triaged, while G2 is explicitly designated as the hard execution blocker. The verbatim gate text is embedded in every plan file.
3. **Exclusion of B6 Signature Divergences**:
   - *Resolution*: The 7 problem JSON signature divergences identified in battery check B6 are strictly managed by Phase 2 Addendum V2 and are not modified in Phase 3.

---

## 3. Plan-Checker Coverage Matrix (17/17 Dimensions)

| Dimension | Scope Item | Covering Plan & Task | Verification Mechanism |
| :--- | :--- | :--- | :--- |
| **1** | `fsrs` load/pin gate | Plan 3.0, Task 0.1 | Pip install `fsrs==6.3.2`, offline import check |
| **2** | Card-per-problem JSON storage | Plan 3.1, Task 1.1 | `problem_fsrs_cards` table creation in `coach.db` |
| **3** | `attempts` table untouched | Plan 3.1, Task 1.1, 1.3; Plan 3.4, Task 4.2 | Row count and checksum assertions on `attempts` |
| **4** | Rating map (3 rules) | Plan 3.1, Task 1.2 | Pure function `map_judge_to_rating` in `coach/fsrs_engine.py` |
| **5** | `Rating.Easy` ban assertion | Plan 3.1, Task 1.2; Plan 3.4, Task 4.1 | Automated test asserting `Easy` is never emitted |
| **6** | Defaults + `desired_retention = 0.9` | Plan 3.1, Task 1.1 | Assert `s.p.request_retention == 0.9` on `FSRS()` instance |
| **7** | Optimizer grep proof | Plan 3.1, Task 1.1 | Git grep asserting 0 optimizer imports across codebase |
| **8** | Due semantics at 4 consumers | Plan 3.2, Task 2.1 | Home chip, Home queue, Practice chip, Dashboard state |
| **9** | Migration (history, A1, copy, idempotent) | Plan 3.1, Task 1.3; Plan 3.4, Task 4.2 | Last attempt timestamp derivation, dry run on copy DB |
| **10** | Ladder removal + call-site dispositions + grep | Plan 3.2, Task 2.2 | Grep proof verifying 0 runtime callers of `calculate_due_date` |
| **11** | Truth-in-copy line + sweep dispositions | Plan 3.2, Task 2.3 | Replace line 1164; grep sweep for `21 days` and ladder copy |
| **12** | Streak regression | Plan 3.2, Task 2.3; Plan 3.4, Task 4.1 | `tests/test_streak_regression.py` pinning `current_streak` |
| **13** | Interleaving constraint, sampling, free pick, 1st exposure | Plan 3.3, Task 3.1, 3.2 | Non-adjacent topics algorithm, free picker untouched |
| **14** | 5 test kinds | Plan 3.4, Task 4.1 | Rating map, migration, due equivalence, interleaving, streak |
| **15** | Captures at 1450×900 | Plan 3.4, Task 4.3 | Chrome CDP capture of Home screen (due chip + queue) |
| **16** | Resources exercised accounting | Plan 3.4, Task 4.3 | Formal table accounting for all active and parked skills |
| **17** | Freezes + Gate A2 in contract | Plans 3.0–3.4 headers | Explicit freezes for problems, judge, and Direction A tokens |

---

## 4. Frozen Boundaries & Invariants

1. **Problem Bank Freeze**: `data/problems/*.json` statements, starter code, and test cases are strictly frozen.
2. **Judge Execution Freeze**: `coach.judge` test runner, execution semantics, and timeout bounds are strictly frozen.
3. **UI System Freeze**: Direction A tokens (`DESIGN.md`), typography (Fraunces + Inter), colors, and layouts are frozen, with the sole exception of the truth-in-copy line on Home.
4. **Historical Attempt Freeze**: The `attempts` table in SQLite is immutable; no migration or card update may insert, delete, or modify attempt rows.

---

## 5. Skill Bindings & Resource Allocation

### Active Skill Bindings
- **Wave 0 (Baseline & Dependency Gate)**: `/empirical-validation` (baseline verification, pip pinning, and SHA256 hash discipline).
- **Wave 1 (FSRS Core & Migration)**: `/agency-senior-developer` (storage schema, rating mapper, scheduler wrapper, migration logic); `/agency-test-automation-engineer` (unit tests alongside code).
- **Wave 2 (Scheduling Integration & Copy)**: `/agency-minimal-change-engineer` (surgical UI integration, ladder disconnection, single copy line swap).
- **Wave 3 (Cognitive Interleaving)**: `/agency-senior-developer` (interleaving queue generator, constraint enforcement, first-exposure branch).
- **Wave 4 (Verification & Return)**: `/agency-test-automation-engineer` (5 test suites), `/empirical-validation` (migration proof & hash check), `/agency-evidence-collector` (1450×900 CDP capture).

### Parked Skills
- `/impeccable`, `/ui-ux-pro-max`, `/ui-styling`, `/design-system`, `/design`, `/brand`: **PARKED**. Direction A UI design is strictly frozen for Phase 3; only one sentence of text changes.
- `/agency-frontend-developer`: **PARKED**. No UI components or screens are constructed; all changes in `app.py` are logic-level wiring.
- `/speckit-*`: **PARKED**. GSD is the planning and execution system of record.
- `/teamwork`: **PARKED**. Standing owner instruction; subagents fan out via `/dispatching-parallel-agents` only.

---

## 6. Plan-Checker Verification Report

```text
## Plan Check Passed ✓

Phase: Phase 3 (FSRS + Interleaving)
Plans checked: 5 (Plans 3.0, 3.1, 3.2, 3.3, 3.4)
Tasks checked: 13 total across 5 waves (avg 2.6 tasks/plan)
Status: PASSED

Dimension 1: Requirement Coverage — PASSED (17/17 scope items mapped)
Dimension 2: Task Completeness — PASSED (all tasks have Files, Action, Verify, Done)
Dimension 3: Dependency Correctness — PASSED (acyclic wave dependencies: 00 -> 01 -> 02 -> 03 -> 04)
Dimension 4: Key Links Planned — PASSED (wrapper -> store -> app -> tests cleanly wired)
Dimension 5: Scope Sanity — PASSED (all plans contain <= 3 tasks, <= 5 files)
Dimension 6: Verification Derivation — PASSED (all must-haves trace directly to Block M2 & Milo audit)

Blockers: 0
Warnings: 0
```

