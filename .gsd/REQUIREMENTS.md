---
milestone: Milestone 1 — UI Redesign
updated: 2026-11-05
---

# REQUIREMENTS.md

## Overview
Requirements derived from SPEC.md for Milestone 1 (UI Redesign: Direction A).

---

## Functional & Design Requirements

| ID | Requirement | Source | Phase | Status |
|----|-------------|--------|-------|--------|
| REQ-01 | Define complete design token sheet for Direction A (Brilliant-style: warm paper bg, ink text, tinted accents per area, rounded corners, pill buttons, Fraunces/Inter fonts) | SPEC Goal 1 | 1 | Pending |
| REQ-02 | Create static HTML mockup for Home view (hero, streak banner, topic cards, CTA) | SPEC Goal 2 | 1 | Pending |
| REQ-03 | Create static HTML mockup for Practice view (problem description, code editor surround, test runner panel, hint reveal) | SPEC Goal 2 | 1 | Pending |
| REQ-04 | Create static HTML mockup for Mock Interview view (timed countdown, question stepper, submission, scorecard modal) | SPEC Goal 2 | 1 | Pending |
| REQ-05 | Create static HTML mockup for Dashboard view (spaced repetition queue, topic mastery badges, streak history, attempt analytics) | SPEC Goal 2 | 1 | Pending |
| REQ-06 | Capture screenshots of all 4 mockups and token sheet for owner review and formal sign-off | SPEC Goal 2 | 1 | Pending |
| REQ-07 | Update `.streamlit/config.toml` and custom CSS injecting Direction A tokens and styling | SPEC Goal 3 | 2 | Pending |
| REQ-08 | Refactor Streamlit view layouts in `app.py` to match the approved mockups without touching backend logic | SPEC Goal 3 | 2 | Pending |
| REQ-09 | Verify all 26 pytest tests continue to pass and application runs without errors | SPEC Goal 3 | 2 | Pending |

---

## Non-Functional Requirements & Constraints

| ID | Requirement | Category | Phase | Status |
|----|-------------|----------|-------|--------|
| NFR-01 | Phase 1 Isolation: Zero modifications to production app code (`app.py`, `coach/*`) during mockup phase | Governance | 1 | Pending |
| NFR-02 | Frozen Backend: No changes to `coach/*.py` or `data/problems/*.json` at any point | Integrity | All | Pending |
| NFR-03 | Visual Ergonomics: High contrast ratio for ink on warm paper meeting WCAG AA/AAA standards | Accessibility | All | Pending |

---

## Traceability Matrix

| Requirement | Plans | Tests | Status |
|-------------|-------|-------|--------|
| REQ-01 | Phase 1 | Token verification | Pending |
| REQ-02 | Phase 1 | Visual / Screenshot | Pending |
| REQ-03 | Phase 1 | Visual / Screenshot | Pending |
| REQ-04 | Phase 1 | Visual / Screenshot | Pending |
| REQ-05 | Phase 1 | Visual / Screenshot | Pending |
| REQ-06 | Phase 1 | Owner Approval | Pending |
| REQ-07 | Phase 2 | Config / CSS inspection | Pending |
| REQ-08 | Phase 2 | Visual / Screenshot | Pending |
| REQ-09 | Phase 2 | pytest runner (26 tests) | Pending |
