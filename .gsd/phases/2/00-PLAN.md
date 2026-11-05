---
phase: 2
plan: 0
wave: 0
depends_on: []
---

# Plan 2.0: Regression Guard & Metric-Numerals A/B Evaluation

## Objective
Establish the pre-implementation regression baseline by verifying that all 26 pytest tests pass with identical counts, confirm the Shell Gate recount outcome, and capture dual A/B comparison screenshots of the Home stat row (Fraunces Display numerals vs Inter SemiBold tabular numerals) for the project owner's selection before applying typography to metric cards.

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md
- tests/test_problems.py
- mockups/home.html

## Tasks

<task type="auto">
  <name>Pre-Implementation Regression Guard & Shell Gate Verification</name>
  <files>scratch/verify_regression.ps1</files>
  <action>
    1. Execute the full pytest test suite using PowerShell with PYTHONPATH set to root:
       powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -m pytest tests/"
    2. Verify all 26 tests pass, including the R1 longest_substring regression fixture.
    3. Confirm git status shows zero dirty files under coach/, data/problems/, or tests/.
    4. Confirm that the Shell Gate recount stands with 0 impossible elements.
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -m pytest tests/"</verify>
  <done>26 of 26 tests pass cleanly; backend files remain 100% quarantined.</done>
</task>

<task type="auto">
  <name>Generate Metric-Numerals A/B Evaluation Screenshots</name>
  <files>scratch/eval_metrics_ab.py, docs/screenshots/r3/metrics_ab_eval.png</files>
  <action>
    1. Create an isolated evaluation script in scratch/eval_metrics_ab.py that renders the 3 Home stat cards ("1 day", "0 due", "12 problems") in both typography variants using self-hosted fonts from assets/fonts/:
       - Variant A: Fraunces Display numerals (as approved in Phase 1 mockup)
       - Variant B: Inter SemiBold tabular figures (font-variant-numeric: tabular-nums)
       - Strictly avoid monospace (monospace metrics are banned as typewriter slop)
    2. Render the comparison at 1920x1080 and capture a clean side-by-side screenshot to docs/screenshots/r3/metrics_ab_eval.png.
    3. Present both variants to the owner for selection prior to Wave 3 execution.
  </action>
  <verify>Test-Path docs/screenshots/r3/metrics_ab_eval.png</verify>
  <done>docs/screenshots/r3/metrics_ab_eval.png exists displaying side-by-side comparisons of Fraunces vs Inter tabular numerals.</done>
</task>

## Success Criteria
- [ ] 26/26 backend pytest tests pass prior to any UI modification
- [ ] Git quarantine confirmed clean across coach/, data/problems/, tests/
- [ ] Metric numerals A/B evaluation screenshot captured and ready for owner selection
