---
milestone: Milestone 1 — UI Redesign
version: 1.0.0
updated: 2026-11-05
---

# ROADMAP.md

> **Current Phase**: Phase 1: Static HTML Mockups & Design Tokens
> **Status**: ⬜ Not Started

## Must-Haves (from SPEC)

- [x] Direction A Design Token Sheet (Warm paper, ink text, category tints, Fraunces + Inter, pill buttons)
- [x] 4 Static HTML Mockups: Home, Practice, Mock Interview, Dashboard
- [x] Visual owner approval of mockups via screenshots (no app code changes in Phase 1)
- [ ] Streamlit UI implementation of approved design in Phase 2
- [ ] 26/26 pytest tests pass with frozen backend

---

## Phases

### Phase 1: Static HTML Mockups & Design Tokens
**Status**: ✅ Complete  
**Objective**: Build pixel-perfect static HTML/CSS mockups of Home, Practice, Mock, and Dashboard along with a design token sheet implementing Direction A (Brilliant-style). Capture screenshots and obtain owner sign-off with NO changes to application code.  
**Requirements**: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, NFR-01  

**Plans:**
- [x] Plan 1.1: Design Tokens Foundation & Home Screen Mockup (wave 1)
- [x] Plan 1.2: Core Workspace Mockups - Practice Arena & Mock Interview (wave 2)
- [x] Plan 1.3: Analytics Dashboard Mockup, Dual-Resolution Capture & Visual Finish Gate (wave 3)

---

### Phase 2: Streamlit UI Implementation
**Status**: ⬜ Not Started  
**Objective**: Translate the approved Direction A mockups and tokens into the Streamlit application (`.streamlit/config.toml`, `app.py`, custom CSS/components) while keeping the backend (`coach/*.py`) and problem bank (`data/problems/*.json`) strictly frozen.  
**Depends on**: Phase 1 approval (Completed)  
**Requirements**: REQ-07, REQ-08, REQ-09, NFR-02, NFR-03  

---

## Progress Summary

| Phase | Status | Plans | Complete |
|-------|--------|-------|----------|
| 1 | ✅ Complete | 3/3 | 100% |
| 2 | ⬜ Not Started | 0/2 | — |

---

## Timeline

| Phase | Started | Completed | Duration |
|-------|---------|-----------|----------|
| 1 | 2026-11-05 | 2026-11-05 | ~2h |
| 2 | — | — | — |

