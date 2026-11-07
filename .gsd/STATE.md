---
updated: 2026-11-08
---

# Project State

## Current Position

**Milestone:** Milestone 5 — MCQ Practice (180 Questions across 10 Categories)  
**Phase:** Phase 9: MCQ Bank (Authoring, Schema & Verification)  
**Status:** 💬 REGISTERED / DISCUSSING (Execution Gated: Starts after Windup Closing)  
**Active Plan:** Pending Phase 9 discuss alignment  

---

## Milestone Relationship & Status

- **Milestone 1 (Premium UI Redesign)**: ✅ Complete & Closed.
- **Milestone 2 (Make the Loop Smarter)**: 
  - **Phase 3 (FSRS + Interleaving)**: ✅ Complete — accepted with corrective (64/64 tests green, live capture verified). Intact and unedited.
  - **Phases 4 & 5 (Resource Measurement, Attempt History + Ruff)**: Maintained in Milestone 2 backlog.
- **Milestone 3 (Terracotta Editorial Redesign)**:
  - **Phase 6 (T1)**: ✅ Complete (Owner Approved Mockups, Rounds 1–2 + Fix Round, 7 screens).
  - **Phase 7 (T2)**: ✅ Complete (Terracotta Editorial in Live App, Phase Return filed, Fix Round closed, 82/82 tests green, Visual Captures verified).
- **Milestone 4 (Problem Bank Expansion)**:
  - **Phase 8**: ✅ Complete (8 new problems authored: 2 Easy, 3 Medium, 3 Hard; 100% reference pass; full suite 82/82 passing).
- **Milestone 5 (MCQ Practice)**:
  - **Phase 9**: 💬 DISCUSSING / PLANNING (Data layer: 180 MCQs across 10 categories, machine-verified output questions, independent audit).
  - **Phase 10**: 🔒 GATED (Terracotta Mockup Gate `mockups/terracotta/mcq.html` at 1450×900, owner approval, Streamlit screen).

---

## Last Action

- Completed Phase 7 Fix Round: Added `import os` to `app.py`, resolved duplicate registration UX with friendly warning and Resend button, restored Home third bento card to "Problems Solved" (`1 / 20`), confirmed signed-in topbar Logout button, verified 82/82 tests, captured visual proofs, and committed (`6822e43`).
- Registered Milestone 5 (MCQ Practice) with Phases 9 and 10 per owner instruction Block Q.
- Surveyed machine runtimes: Python 3.12 and Node.js exist; gcc/g++/clang/java/javac are absent. Formulated verification doctrine accordingly.

---

## Gates for Milestone 5

| Gate | Requirement | Status | Action Needed |
| :--- | :--- | :--- | :--- |
| **G-WINDUP** | Current Windup Closure (Phase 7 fix filed + final verification accepted) | ⏳ ACTIVE | Owner acceptance of windup |
| **G-DISCUSS9** | Phase 9 MCQ Bank Discussion & Scope Alignment | ⏳ ACTIVE | Return Block Q discuss output |
| **G-PLAN9** | Phase 9 Plan Set Authoring & Audit | 🔒 PENDING | Author wave plans and submit for owner/Milo audit |
| **G-MOCK10** | Phase 10 Terracotta Static Mockup Approval | 🔒 PENDING | Author `mockups/terracotta/mcq.html` and secure owner signoff |
| **G-EXEC10** | Phase 10 Screen Execution Authorization | 🔒 LOCKED | Implementation starts only after mockup approval |

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
| **[DECISION-019]** | Milestone 5 Scope: MCQ Practice (10 categories, 180 questions, No-Copy Law, Mockup Gate) | 2026-11-08 | Milestone 5 |

---

## Blockers & Freezes

- **Freezes during Milestone 5**:
  - `coach/fsrs_engine.py`, `coach/judge.py`, and rating mapping strictly frozen.
  - Terracotta tokens and CSS classes strictly frozen.
  - Existing 20 coding problem JSON files in `data/problems/` strictly read-only.
  - Real `coach.db` SHA256 preserved.
  - Execution of Milestone 5 is gated on owner acceptance of current windup.
