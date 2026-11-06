---
updated: 2026-11-06
---

# Project State

## Current Position

**Milestone:** Milestone 2 — Make the Loop Smarter  
**Phase:** Phase 3: FSRS + Interleaving  
**Status:** 🚀 EXECUTING (Gates G1 & G2 Verified)  
**Active Plan:** `.gsd/phases/3/00-PLAN.md` (Wave 0 Execution)  

---

## Last Action

- Filed `BACKEND_VERIFICATION.md` proving 100% backend correctness (B1–B7) and zero database mutation (`coach.db` SHA256 verified untouched).
- Registered Milestone 2 ("Make the Loop Smarter") in `ROADMAP.md` and `SPEC.md`.
- Established Phase 3 scope: Workstream 1 (FSRS scheduler swap) and Workstream 2 (Interleaved review queue).
- Appended Milestone 2 future phases (Resource Measurement, Attempt History + Ruff) to `TODO.md` backlog.

---

## Entry Gates for Phase 3 Execution

| Gate | Requirement | Status | Action Needed |
| :--- | :--- | :--- | :--- |
| **G1** | Backend Verification Battery filed & triaged | ✅ VERIFIED | Audited by Milo 2026-11-07: B1–B7 pass, DB identical, defects none |
| **G2** | Phase 2 Closed (Owner Live Approval + Bookkeeping) | ✅ VERIFIED | Formal live approval granted; closure bookkeeping complete |

> **Note**: Both Entry Gates G1 and G2 are fully satisfied. Phase 3 execution authorized.

---

## Active Decisions

| Decision | Choice | Made | Affects |
| :--- | :--- | :--- | :--- |
| **[DECISION-001]** | Direction A: Brilliant-style colorful light learning theme | 2026-11-05 | All UI phases |
| **[DECISION-002]** | Two-Phase Redesign Gate: mockups first, Streamlit second | 2026-11-05 | Phases 1 & 2 |
| **[DECISION-003]** | Frozen backend & problems during Milestone 1 | 2026-11-05 | Milestone 1 |
| **[DECISION-004]** | Phase 1 Mockups Approved (Home, Practice, Mock, Dash) | 2026-11-05 | Phase 2 |
| **[DECISION-005]** | Streamlit Topbar Workbench Shell retained | 2026-11-05 | Phase 2 |
| **[DECISION-011]** | Wave 1 subagent parallelism & Wave 2 evidence fan-out | 2026-11-06 | Phase 2 Corrective |
| **[DECISION-012]** | Runtime-derived Python version chip (`3.12`) | 2026-11-06 | App navbar |
| **[DECISION-013]** | Milestone 2 Scope: FSRS + Interleaving first | 2026-11-06 | Phase 3 |
| **[DECISION-014]** | py-fsrs default parameters, retention 0.9, optimizer forbidden | 2026-11-06 | Phase 3 FSRS |
| **[DECISION-015]** | Judge Rating Mapping: FAIL/TIMEOUT $\rightarrow$ Again; PASS+hints/tries $\rightarrow$ Hard; Clean PASS $\rightarrow$ Good; Easy omitted | 2026-11-06 | Phase 3 FSRS |

---

## Blockers & Freezes

- **Freezes for Phase 3**:
  - `data/problems/*.json`: Statements, starter code, and test cases are untouched.
  - `coach.judge`: Execution semantics and timeout bounds are untouched.
  - Phase 2 UI Design: Direction A tokens, layout, and visual components are untouched except the truth-in-copy line on Home.
- **Execution Blocker**: Entry Gate G2 (Owner live approval of Phase 2 UI).

---

*Last updated: 2026-11-06*
