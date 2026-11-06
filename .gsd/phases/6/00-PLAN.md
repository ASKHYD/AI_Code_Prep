---
phase: 6
plan: "00"
wave: 0
depends_on: []
---

# Plan 6.0: Baseline, Quarantine Gate & Resource Audit

## Objective
Establish the execution baseline for Phase 6 (Terracotta Static Mockups & Token Sheet, T1). Verify the quarantine of application code (`app.py`, `coach/*.py`, `data/problems/*.json`, `tests/*`), record the 57/57 baseline pytest pass, execute the load-or-report-MISSING gate for all design resources, and affirm the execution locks for Phase 6 and Phase 7.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `.gsd/phases/6/DISCUSS.md`
- `agent-resources/lucide/`
- `agent-resources/awesome-design-md/`

## Execution Gate (Verbatim Binding)
> **EXECUTION GATE: Phase 6 touches ZERO application code (`app.py`, `coach/*.py`). All deliverables are static HTML/CSS mockups and tokens. Terracotta Streamlit implementation (Phase 7 / T2) may NOT start until Gate G-T1 holds (owner approval of Phase 6 mockups) AND Milestone 2 Phase 3 receives owner live acceptance (or explicit owner order in chat).**

---

## Tasks

<task type="auto">
  <name>Task 0.1: Test Suite Baseline & Code Quarantine Invariant</name>
  <files>.gsd/phases/6/00-SUMMARY.md</files>
  <action>
    <!-- Skill binding: /empirical-validation -->
    1. Run the full pytest test suite using `.venv\Scripts\pytest.exe -o pythonpath=. tests/` to confirm all 57 tests pass with 0 errors.
    2. Record git diff status to verify that `app.py`, `coach/*.py`, `data/problems/*.json`, and `tests/*` are completely clean and untouched.
    3. Document the Phase 6 quarantine invariant: Phase 6 deliverables are strictly contained within `DESIGN.md`, `mockups/terracotta/`, and `docs/screenshots/terracotta/`. No modifications to `app.py` or backend modules are permitted.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/ --tb=short</verify>
  <done>Pytest passes 57/57 without warnings, and code quarantine is verified.</done>
</task>

<task type="auto">
  <name>Task 0.2: Resource Load-or-Report-Missing Audit</name>
  <files>.gsd/phases/6/00-SUMMARY.md</files>
  <action>
    <!-- Skill binding: /empirical-validation -->
    1. Inspect `agent-resources/lucide/` to confirm local SVG icon availability.
    2. Inspect `agent-resources/awesome-design-md/` for design reference files. If specific files (`terracota`, `bento`) are absent, record them as MISSING in the resource audit (specs are fully provided in Block T / DISCUSS.md).
    3. Verify available design skills: `/ui-ux-pro-max`, `/ui-styling`, `/design-system`, `/design`, `/brand`, `/impeccable`, `/agency-frontend-developer`, `/agency-ui-finish-gate-reviewer`.
    4. Compile the Resource Gate Record into `00-SUMMARY.md`.
  </action>
  <verify>.venv\Scripts\python.exe -c "import os; print('Lucide exists:', os.path.isdir('agent-resources/lucide'))"</verify>
  <done>Resource audit completed with all items accounted as FOUND or MISSING with documented justification.</done>
</task>

---

## Must-Haves
After all tasks complete, verify:
- [ ] Pytest passes 57/57.
- [ ] Application code quarantine is verified with 0 diffs in `app.py` or `coach/`.
- [ ] Resource load-or-report-MISSING gate is recorded.

## Success Criteria
- [ ] Baseline test results recorded.
- [ ] Clean isolation confirmed.

