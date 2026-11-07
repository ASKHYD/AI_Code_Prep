---
updated: 2026-11-07
---

# Project State

## Current Position

**Milestone:** Milestone 4 — Problem Bank Expansion (20 Problems)  
**Phase:** Phase 8: Problem Bank Expansion (8 New Problems: 2 Easy, 3 Medium, 3 Hard)  
**Status:** 💬 DISCUSSING / PLANNING (Execution Gated: Starts after Terracotta Phase 7 Shipped)  
**Active Plan:** Pending Phase 8 discuss & plan authoring  

---

## Milestone Relationship & Status

- **Milestone 1 (Premium UI Redesign)**: ✅ Complete & Closed.
- **Milestone 2 (Make the Loop Smarter)**: 
  - **Phase 3 (FSRS + Interleaving)**: ✅ Complete — accepted with corrective (64/64 tests green, live capture verified). Intact and unedited.
  - **Phases 4 & 5 (Resource Measurement, Attempt History + Ruff)**: Maintained in Milestone 2 backlog.
- **Milestone 3 (Terracotta Editorial Redesign)**:
  - **Phase 6 (T1)**: ✅ Complete (Owner Approved Mockups, Rounds 1–2 + Fix Round, 7 screens).
  - **Phase 7 (T2)**: ✅ Complete (Terracotta Editorial in Live App, 71/71 tests green, 14 CDP captures, Phase Return filed).
- **Milestone 4 (Problem Bank Expansion)**:
  - **Phase 8**: 💬 DISCUSSING / PLANNING. Authoring 8 new problems (2 Easy, 3 Medium, 3 Hard) to grow bank from 12 to 20.

---

## Last Action

- Completed Phase 7 (Terracotta Streamlit Implementation) with 71/71 tests passing, 0 database disruptions, and 14 dual-resolution CDP captures.
- Registered Milestone 4 (Problem Bank Expansion) and Phase 8 (8 New Problems: 2 Easy, 3 Medium, 3 Hard) per owner instruction Block B.
- Confirmed Bank Law requirements (JSON schema completeness, B1 reference test pass, X6 signature single-source-of-truth, 3-level offline hints, "Hard" UI tier support, scratch FSRS migration test, and UI count refresh).

---

## Gates for Milestone 4

| Gate | Requirement | Status | Action Needed |
| :--- | :--- | :--- | :--- |
| **G-SHIP7** | Phase 7 Terracotta Implementation Shipped in App | ✅ MET | Phase 7 completed, 71/71 tests green, Return filed |
| **G-DISCUSS8** | Phase 8 Discussion & Scope Alignment | ⏳ ACTIVE | Align on 8 problem specs, topics, and difficulty tier handling |
| **G-PLAN8** | Phase 8 Plan Set Authoring & Audit | 🔒 PENDING | Author wave plans and submit for owner/Milo audit |
| **G-EXEC8** | Phase 8 Execution Authorization | 🔒 LOCKED | Authorise execution after plan audit approval |

---

## Active Decisions

| Decision | Choice | Made | Affects |
| :--- | :--- | :--- | :--- |
| **[DECISION-001]** | Direction A: Brilliant-style colorful light learning theme | 2026-11-05 | Milestone 1 |
| **[DECISION-002]** | Two-Phase Redesign Gate: mockups first, Streamlit second | 2026-11-05 | Milestones 1 & 3 |
| **[DECISION-003]** | Frozen backend & problems during UI redesigns | 2026-11-05 | Milestones 1 & 3 |
| **[DECISION-011]** | Wave 1 subagent parallelism & Wave 2 evidence fan-out | 2026-11-06 | Execution harness |
| **[DECISION-012]** | Runtime-derived Python version chip (`3.12`) | 2026-11-06 | App navbar |
| **[DECISION-013]** | Functional email confirmation with PBKDF2 600k & SMTP STARTTLS | 2026-11-07 | Phase 7 Auth |
| **[DECISION-014]** | py-fsrs default parameters, retention 0.9, optimizer forbidden | 2026-11-06 | Phase 3 FSRS |
| **[DECISION-015]** | Judge Rating Mapping: FAIL/TIMEOUT $\rightarrow$ Again; PASS+hints/tries $\rightarrow$ Hard; Clean PASS $\rightarrow$ Good; Easy omitted | 2026-11-06 | Phase 3 FSRS |
| **[DECISION-016]** | Milestone 3 Scope: Option 3 Terracotta Editorial (Bento grid + Terracota Mediterrâneo) | 2026-11-07 | Milestone 3 |
| **[DECISION-017]** | Official Brand Name: AI Prep Coach | 2026-11-07 | Milestone 3 |
| **[DECISION-018]** | Milestone 4 Scope: Bank Expansion to 20 problems (8 new: 2E, 3M, 3H) | 2026-11-07 | Milestone 4 |

---

## Blockers & Freezes

- **Freezes during Milestone 4**:
  - `coach/fsrs_engine.py`, `coach/judge.py`, and rating mapping strictly frozen.
  - Terracotta tokens and CSS classes in `app.py` strictly frozen (data growth must not restyle components).
  - Existing 12 problem JSON files in `data/problems/` strictly read-only.
  - Real `coach.db` SHA256 preserved (all migration test runs must execute on a scratch DB copy).
