---
updated: 2026-11-07
---

# Project State

## Current Position

**Milestone:** Milestone 3 — Terracotta Editorial Redesign  
**Phase:** Phase 6: Terracotta Static Mockups & Token Sheet (T1)  
**Status:** 📋 PLANNING COMPLETE — READY FOR EXECUTION (/executor 6)  
**Active Plan:** `.gsd/phases/6/PLAN_CONTRACT.md` (5 plans across 4 waves)  

---

## Milestone Relationship & Status

- **Milestone 1 (Premium UI Redesign)**: ✅ Complete & Closed.
- **Milestone 2 (Make the Loop Smarter)**: 
  - **Phase 3 (FSRS + Interleaving)**: Complete — accepted with corrective (2026-11-07) (64/64 tests green, corrective return filed). Intact and unedited.
  - **Phase 4 & 5 (Resource Measurement, Attempt History + Ruff)**: Maintained in Milestone 2 backlog.
- **Milestone 3 (Terracotta Editorial Redesign)**:
  - **Phase 6 (T1)**: Author token sheet, build 6 static HTML mockups with real data, anti-slop audit, dual captures (1450 & 1920). Stop for owner approval.
  - **Phase 7 (T2)**: Streamlit implementation (only after T1 approval + Phase 3 live acceptance).

---

## Last Action

- Completed Milestone 2 Phase 3 execution and verification: 57/57 pytest passed, live 1450×900 CDP capture of Home verified, return filed.
- Registered Milestone 3 ("Terracotta Editorial Redesign") with Phase 6 (T1 Mockups) and Phase 7 (T2 Streamlit Implementation).
- Retained Milestone 2 phases intact without renumbering.

---

## Gates for Milestone 3

| Gate | Requirement | Status | Action Needed |
| :--- | :--- | :--- | :--- |
| **G-T1** | Phase 6 Mockups & Token Sheet Owner Approval | ⏳ PENDING | Build static HTML mockups with real data; capture at 1450 & 1920 |
| **G-M2** | Milestone 2 Phase 3 Owner Live Acceptance | ⏳ PENDING | Awaiting owner live review on `http://localhost:8501` |
| **G-EXEC**| Phase 7 Streamlit Execution Authorization | 🔒 LOCKED | Requires both G-T1 and G-M2 (or explicit chat override) |

---

## Active Decisions

| Decision | Choice | Made | Affects |
| :--- | :--- | :--- | :--- |
| **[DECISION-001]** | Direction A: Brilliant-style colorful light learning theme | 2026-11-05 | Milestone 1 |
| **[DECISION-002]** | Two-Phase Redesign Gate: mockups first, Streamlit second | 2026-11-05 | Milestones 1 & 3 |
| **[DECISION-003]** | Frozen backend & problems during UI redesigns | 2026-11-05 | Milestones 1 & 3 |
| **[DECISION-011]** | Wave 1 subagent parallelism & Wave 2 evidence fan-out | 2026-11-06 | Execution harness |
| **[DECISION-012]** | Runtime-derived Python version chip (`3.12`) | 2026-11-06 | App navbar |
| **[DECISION-013]** | Milestone 2 Scope: FSRS + Interleaving first | 2026-11-06 | Milestone 2 |
| **[DECISION-014]** | py-fsrs default parameters, retention 0.9, optimizer forbidden | 2026-11-06 | Phase 3 FSRS |
| **[DECISION-015]** | Judge Rating Mapping: FAIL/TIMEOUT $\rightarrow$ Again; PASS+hints/tries $\rightarrow$ Hard; Clean PASS $\rightarrow$ Good; Easy omitted | 2026-11-06 | Phase 3 FSRS |
| **[DECISION-016]** | Milestone 3 Scope: Option 3 Terracotta Editorial (Bento grid + Terracota Mediterrâneo) | 2026-11-07 | Milestone 3 |

---

## Blockers & Freezes

- **Freezes for Milestone 3**:
  - `coach/*.py`: Engine, store, judge, FSRS, interleaving remain strictly frozen.
  - `data/problems/*.json`: Statements, starter code, and test cases remain strictly frozen.
  - `tests/*`: Verification test suite untouched; 57/57 invariant.
- **Phase 6 Scope Restriction**: No application code in `app.py` in Phase 6 (static mockups & tokens only).
- **Phase 7 Execution Blocker**: Gate G-T1 (Owner approval of Phase 6 mockups) and Gate G-M2 (Owner acceptance of Phase 3).

---

*Last updated: 2026-11-07*
