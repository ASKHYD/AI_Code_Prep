# Phase 6 Plan Contract & Plan-Checker Validation

**Phase**: Milestone 3, Phase 6: Terracotta Static Mockups & Token Sheet (T1)  
**Date**: 2026-11-07  
**Scope Source**: Block T (`MILESTONE-3-TERRACOTTA-BLOCK.md`) & Phase 6 Discussion (`.gsd/phases/6/DISCUSS.md`)  
**Status**: PLANNING COMPLETE — READY FOR EXECUTION  

---

## 1. Execution Gate (Verbatim Binding)

> **EXECUTION GATE: Phase 6 touches ZERO application code (`app.py`, `coach/*.py`, `data/problems/*.json`, `tests/*`). All deliverables are static HTML/CSS mockups and token sheets. Terracotta Streamlit implementation (Phase 7 / T2) may NOT start until Gate G-T1 holds (owner approval of Phase 6 mockups) AND Milestone 2 Phase 3 receives owner live acceptance (or explicit owner order in chat).**

---

## 2. Wave Structure & Plan Breakdown

```
Wave 0: Baseline & Code Quarantine
└── 00-PLAN.md: Test baseline (57/57 pytest), application code quarantine, and resource load-or-report-MISSING gate.

Wave 1: Token Architecture & Foundational Styling
└── 01-PLAN.md: Update DESIGN.md with Terracotta Editorial tokens; create mockups/terracotta/style.css and tokens.html specimen page.

Wave 2: Core Screen & Simulation Mockups (Parallelizable)
├── 02-PLAN.md: Home, Practice Arena, and Dashboard mockups with 100% authentic data (12 problems, store metrics, Plotly chart above table).
└── 03-PLAN.md: Mock Interview simulation mockups (Start screen, Active session screen with 2-place mono timer, Scorecard screen).

Wave 3: Verification, CDP Captures & Gate Return
└── 04-PLAN.md: Automated anti-slop audit (0 tropes), 14 Chrome CDP captures (7 @ 1450×900 primary, 7 @ 1920×1080), quarantine verification, and PHASE_RETURN.md.
```

---

## 3. Plan-Checker Coverage Matrix (14/14 Dimensions)

| Dimension | Scope Item | Covering Plan & Task | Verification Mechanism |
| :--- | :--- | :--- | :--- |
| **1** | Code quarantine invariant | Plan 6.0, Task 0.1; Plan 6.4, Task 4.2 | Git diff verifying 0 changes outside `mockups/terracotta/`, `DESIGN.md`, and docs |
| **2** | Pytest baseline & regression | Plan 6.0, Task 0.1; Plan 6.4, Task 4.2 | 57/57 tests passing in `tests/` |
| **3** | Resource load-or-report-MISSING | Plan 6.0, Task 0.2 | Verification of `Lucide`, `awesome-design-md`, and skill availability |
| **4** | Terracotta token sheet | Plan 6.1, Task 1.1 | `DESIGN.md` updated with all 8 palette colors, typography, and constraints |
| **5** | Base CSS stylesheet | Plan 6.1, Task 1.2 | `mockups/terracotta/style.css` with CSS custom properties, 24px radius, 1px hairlines |
| **6** | Visual tokens specimen | Plan 6.1, Task 1.2 | `mockups/terracotta/tokens.html` rendered and validated |
| **7** | Home screen bento mockup | Plan 6.2, Task 2.1 | `mockups/terracotta/home.html` (DM Serif headline, 3 stat tiles, de-slopped queue, FSRS copy) |
| **8** | Practice Arena workbench | Plan 6.2, Task 2.1 | `mockups/terracotta/practice.html` (slim picker, dark editor anchor, small-caps label) |
| **9** | Dashboard bento + chart | Plan 6.2, Task 2.2 | `mockups/terracotta/dashboard.html` (Plotly topic chart ABOVE table, authentic store data) |
| **10** | Mock Start & Session screens | Plan 6.3, Task 3.1 | `mock_start.html` (sandy panel, 45m facts), `mock_session.html` (2-place timer `MM:SS`) |
| **11** | Mock Scorecard screen | Plan 6.3, Task 3.2 | `mock_scorecard.html` (PASS olive, FAIL terracotta, sandy summary, real session metrics) |
| **12** | Anti-slop audit (5 tropes) | Plan 6.4, Task 4.1 | Automated audit script asserting 0 chip soup, 0 generator fiction, 0 gradients/glass/glow |
| **13** | Dual-resolution CDP captures | Plan 6.4, Task 4.2 | Headless Chrome CDP capturing all 7 mockups at 1450×900 and 1920×1080 (14 files) |
| **14** | Resources exercised accounting | Plan 6.4, Task 4.2 | Full accounting table covering all 12 named resources |

---

## 4. Skill Bindings

- **Phase Orchestration & Plan Validation**: `/planner`, `/plan-checker`
- **Execution & Isolation**: `/executor`
- **Baseline & Data Truth Verification**: `/empirical-validation`
- **Token System & Typography**: `/design-system`, `/design`, `/brand`
- **HTML/CSS Component Implementation**: `/agency-frontend-developer`, `/ui-styling`, `/ui-ux-pro-max`
- **Anti-Slop Audit & Design Critique**: `/impeccable`, `/agency-ui-finish-gate-reviewer`
- **CDP Evidence Capture**: `/agency-evidence-collector`

---

## 5. Anti-Slop Audit Invariants (T1 Pre-Capture Gate)

1. **Chip Soup Elimination**: In problem tables and queues, at most ONE status pill is allowed per row. Difficulty and topic are rendered as clean, colored text without bounding pills.
2. **Generator Fiction Elimination**: Problem names must belong strictly to the 12 problems in `data/problems/*.json`. User metrics must match real store data (2 attempts, 1 solved).
3. **Surfaces & Effects**: Zero gradients across card surfaces, zero glassmorphism, zero drop-shadow glows, zero arch-shaped containers. Matte surfaces only with 1px warm hairlines.
4. **Typography Discipline**: DM Serif Display used strictly for display headlines and wordmarks. Body and UI elements use Humanist Sans.
5. **Numeral Formatting**: Metric numbers never use monospace fonts (Inter-style tabular semibold only). JetBrains Mono is strictly confined to code, the editor strip, and the mock timer.

---

## 6. Plan-Checker Verdict

```text
Dimension 1: Atomicity & Scope — PASSED (all plans contain 2 tasks max; zero app.py code).
Dimension 2: Dependency Acyclicity — PASSED (Wave 0 -> Wave 1 -> Wave 2 -> Wave 3).
Dimension 3: Test Quality & Regressions — PASSED (all verify commands executable, 57/57 invariant).
Dimension 4: Data Truth & Quarantine — PASSED (real store data, problem bank frozen, app code untouched).
Dimension 5: Visual Proof Standards — PASSED (14 CDP captures: 1450×900 PRIMARY, 1920×1080 secondary).
Dimension 6: Stop Line & Gates — PASSED (exact stop sentence specified).

Blockers: 0
Warnings: 0
Status: APPROVED FOR EXECUTION (/executor 6)
```
