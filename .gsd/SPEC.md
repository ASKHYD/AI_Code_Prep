# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: Requirements and constraints are locked.

---

## Vision
AI Coding Prep Coach is a local, zero-cost coding-interview practice platform built with Streamlit. Milestone 1 completely transforms the visual experience from an uninspired, generic dark UI into a warm, delightful, Brilliant-style light learning environment ("Direction A") featuring a warm paper background, ink typography (Fraunces headings + Inter body), pastel/tinted color systems per topic area, tactile rounded cards, and pill buttons.

---

## Goals
1. **Design System & Token Specification** — Establish Direction A: a colourful light learning app inspired by Brilliant (warm paper background, rich ink text, tinted accents per functional zone, generous card corner radii, pill buttons, Fraunces serif headings, and Inter sans-serif body).
2. **Phase 1: High-Fidelity Static Mockups** — Build standalone, pixel-perfect static HTML mockups for all 4 primary views (Home, Practice, Mock Interview, Dashboard) alongside a design token sheet, verified and approved by the owner via screenshots with ZERO production application code changes.
3. **Phase 2: Streamlit Theme & UI Implementation** — Apply the approved design tokens, styling, and components to the Streamlit app (`app.py`, `.streamlit/config.toml`, custom CSS/components) while keeping the working backend logic (`coach/*.py`) and problem bank (`data/problems/*.json`) strictly frozen.

---

## Non-Goals (Out of Scope)
- Modifying or refactoring the backend logic (`coach/judge.py`, `coach/store.py`, `coach/repetition.py`, `coach/timer.py`, `coach/llm_hints.py`, `coach/problems.py`, `coach/review.py`).
- Modifying problem bank data (`data/problems/*.json`).
- Rewriting or scaffolding the project from scratch.
- Making application code changes during Phase 1 (mockups and screenshots only until owner approval).
- Adding new backend features, cloud syncing, user auth, or external database integrations.

---

## Users
Software engineers, students, and interview candidates looking for a clean, distraction-free, zero-cost, locally hosted practice environment for algorithmic problem-solving and Python programming.

---

## Constraints
- **Frozen Backend**: The backend modules (`coach/*.py`) and 12 problem JSON files (`data/problems/*.json`) are strictly frozen.
- **Test Integrity**: All 26 existing pytest tests must remain passing without modification.
- **Two-Phase Approval Gate**: Phase 1 is strictly static HTML mockups + token sheet with owner screenshot sign-off; NO app code changes until approved.
- **Design Direction Lock**: Direction A (Brilliant-style light theme):
  - Canvas: Warm paper background (`#FBF9F5` / `#F5F2EB`)
  - Typography: Ink text (`#1E1E24` / `#2D3142`), Fraunces serif headings, Inter body, JetBrains Mono for code
  - Zones: Tinted pastel colour system per area/topic (e.g. mint for arrays, lavender for trees, peach for strings, amber for review)
  - Components: Generous rounded cards (16px–24px), tactile pill buttons, clean elevation

---

## Success Criteria
- [ ] Comprehensive design token sheet created documenting Direction A palette, typography, radii, shadows, and spacing.
- [ ] High-fidelity static HTML mockups created for all 4 views: Home, Practice, Mock, and Dashboard.
- [ ] Screenshots captured and approved by project owner for all 4 mockups and token sheet.
- [ ] Streamlit application updated to reflect approved Direction A aesthetic in Phase 2.
- [ ] 26/26 pytest tests pass with zero regressions.

---

*Last updated: 2026-11-05*

