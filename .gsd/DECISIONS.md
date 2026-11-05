# DECISIONS.md — Architecture Decision Records

> **Purpose**: Log significant technical and design decisions and their rationale.

---

## Decisions

### [DECISION-001] Design Direction Selection: Direction A (Brilliant-Style)

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
The original dark OLED theme was rejected by the owner as generic AI slop. An inspiring, polished visual identity was needed for the coding-interview practice platform.

#### Decision
Adopt Direction A: a colourful light learning app inspired by Brilliant. Key elements include warm paper canvas, rich ink typography with Fraunces serif headings and Inter sans-serif body, tinted pastel accent system per problem category, large rounded cards (16-24px), and pill-shaped action buttons.

#### Rationale
Creates an inviting, premium educational atmosphere that minimizes eye fatigue and feels intentional rather than boilerplate.

#### Consequences
Requires custom CSS injection and tailored component markup when translating to Streamlit in Phase 2.

---

### [DECISION-002] Two-Phase Implementation Gate

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
Risk of premature coding or unaligned visual rework in Streamlit before the aesthetic is validated.

#### Decision
Enforce a two-phase protocol:
- **Phase 1**: Produce static HTML/CSS mockups of all 4 views (Home, Practice, Mock, Dashboard) and a design token sheet. Capture screenshots and require explicit owner sign-off. Zero production application code changes allowed.
- **Phase 2**: Only after visual approval, implement the approved styling into the Streamlit app.

#### Rationale
Eliminates thrash in Streamlit code and ensures 100% aesthetic alignment before touching app files.

---

### [DECISION-003] Strict Backend and Problem Bank Freeze

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
The core backend execution sandbox, judge engine, spaced repetition scheduler, timer, and problem definitions are complete and tested (26 tests passing).

#### Decision
All files in `coach/*.py` and `data/problems/*.json` are strictly frozen. No refactoring, additions, or modifications are permitted.

#### Rationale
Ensures zero regression in working judge and evaluation functionality while focusing 100% of effort on the UI overhaul.

---

## Phase 1 Decisions

**Date:** 2026-11-05

### Scope
- **Visual Mockups Only**: Deliver static HTML mockups for Home, Practice, Mock, and Dashboard plus a Direction A Token Sheet.
- **Strict Code Quarantine**: Zero edits to `app.py`, `.streamlit/config.toml`, `coach/*.py`, `data/problems/*.json`, or `tests/`.
- **R3 Specification Integration**: Full Direction A tokens, area tint palette, typography rules (Fraunces/Inter/JetBrains Mono), and anti-slop rules will be injected directly from the owner's R3 handoff at planning.

### Approach
- **Authentic Content Grounding**: Mockups must display actual app data and signatures:
  - Daily streak: "1 day"
  - Spaced repetition queue: "0 due"
  - Total problem inventory: 12 problems
  - Solved problem: Binary Search PASS (178ms)
  - Active unsolved problem: Longest Substring Without Repeating Characters with genuine starter signature (`longest_substring(s: str) -> int`)
  - Mock countdown timer state: "44:41"
- **Dual-Resolution Evidence Capture**: Screen captures rendered and captured at both `1600x1000` (compact desktop) and `1920x1080` (full HD) for owner verification.

### Constraints & Finish Gate
- **Deliverable Gate**: Phase 1 is complete ONLY when the owner explicitly reviews and approves the rendered mockup screenshots. (PASSED: Approved by owner on 2026-11-05).
- **Zero Implementation**: No Streamlit code or application CSS is written until Phase 2 is unlocked following Phase 1 approval.

---

### [DECISION-004] Phase 1 Owner Acceptance & Phase 2 Directives

**Date**: 2026-11-05  
**Status**: Accepted  

#### Context
Owner completed live browser and dual-resolution screenshot inspection of the Direction A mockups (`mockups/` on port 8085, `docs/screenshots/r3/`) and officially approved Phase 1.

#### Directives for Phase 2 Implementation:
1. **Unattempted Topic Mastery Bars**: Dashboard mastery bars must use `"NOT STARTED"` for unattempted topics (matching the table), never `"0% (0/0)"`.
2. **Mock Screen Timer Redundancy**: The Mock view shows the countdown timer three times in various places — consolidate and reduce to two placements.
3. **Metric Numeral Typography**: The Fraunces zero glyph reads like a lowercase "o" in large metric values (e.g. `"0 problems"`) — evaluate Inter or tabular monospace figures for primary metric numerals during Streamlit implementation.
4. **Button Whitespace Handling**: All button elements must strictly enforce `white-space: nowrap` with adequate horizontal padding to ensure labels never wrap unexpectedly on compact layouts.

---

*Last updated: 2026-11-05*

