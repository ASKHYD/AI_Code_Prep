---
phase: 2
plan: 7
wave: 7
depends_on: [6]
---

# Plan 2.7: Quality Gates, Impeccable Audit & §5 Return Handoff

## Objective
Execute the full post-implementation gate battery: 26/26 backend pytest regression guard, git quarantine verification, Impeccable live UI accessibility/polish detection across all 4 screens, zero-hex-drift audit, computed-font proof verification, dual-resolution side-by-side mockup comparisons, and compile the mandatory §5 Return for owner sign-off.

## Context
- app.py
- .streamlit/config.toml
- DESIGN.md
- mockups/
- docs/screenshots/r3/

## Tasks

<task type="auto">
  <name>Execute Full Post-Implementation Quality & Gate Battery</name>
  <files>scratch/audit_hex_drift.py, scratch/run_impeccable_audit.py, scratch/verify_fonts_cdp.js</files>
  <action>
    1. Gate 1: Regression Guard AFTER:
       - Run full pytest test suite with PYTHONPATH set: powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -m pytest tests/"
       - Assert exactly 26 passed, specifically citing the R1 longest_substring fixture.
    2. Gate 2: Quarantine Assertion:
       - Run git status --porcelain and assert zero changes under coach/, data/problems/, or tests/.
    3. Gate 3: Impeccable Detection:
       - Run npx impeccable detect --json against the live app for all 4 states (Home, Practice with problem loaded, Mock in progress, Dashboard).
       - Log exit codes, commands, and findings by severity; fix all P0/P1 and primary findings; confirm final scan has zero primary findings.
    4. Gate 4: Hex Drift Audit:
       - Run scratch/audit_hex_drift.py checking every hex code in app.py, config.toml, and CSS against the frozen Direction A tokens in DESIGN.md. Assert zero uncataloged hex values.
    5. Gate 5: Computed-Font Proof:
       - Run scratch/verify_fonts_cdp.js to verify computed font-family for heading (Fraunces), body (Inter), metric numeral, and code editor (JetBrains Mono).
  </action>
  <verify>powershell -Command "$env:PYTHONPATH='.'; .venv\Scripts\python.exe -m pytest tests/"; git status --porcelain coach/ data/problems/ tests/</verify>
  <done>All 5 quality gates verified with clean passing results.</done>
</task>

<task type="auto">
  <name>Generate Side-by-Side Comparisons & Compile §5 Return</name>
  <files>scratch/build_side_by_side.py, docs/screenshots/r3/, .gsd/phases/2/RETURN.md</files>
  <action>
    1. Generate dual-resolution side-by-side comparison images placing each real app screenshot next to its corresponding Phase 1 mockup:
       - Home: docs/screenshots/r3/home_real_1920x1080.png vs mockups/home.html
       - Practice: docs/screenshots/r3/practice_real_1920x1080.png vs mockups/practice.html
       - Mock: docs/screenshots/r3/mock_real_1920x1080.png vs mockups/mock.html
       - Dashboard: docs/screenshots/r3/dashboard_real_1920x1080.png vs mockups/dashboard.html
       - Repeat at 1600x1000 viewport.
    2. Catalog all visual approximations vs mockups with justifications in KNOWN LIMITS.
    3. Compile the full §5 Return artifact in .gsd/phases/2/RETURN.md structured with all 7 mandatory sections:
       - §5.1 SUMMARY: Shell gate outcome, numeral A/B winner, per-screen changelog.
       - §5.2 TOKENS & FONTS: config.toml mapping, @font-face assets, computed-font proof output.
       - §5.3 RESOURCES EXERCISED: All 7 Pro Max skills + developing-with-streamlit accounting and evidence.
       - §5.4 GATES: Pytest before/after, quarantine status, Impeccable detect results, hex drift list, font proof.
       - §5.5 UI RESOURCE MAP & SCREENSHOTS: Per-element component/token/key map, dual-res before/after screenshots, side-by-side difference enumeration.
       - §5.6 KNOWN LIMITS: Every approximation vs mockup, deferred P2/P3 items, CSS budget justification.
       - §5.7 STOP: "Stopped at Phase 2 implementation gate, awaiting owner approval of the real app screenshots."
  </action>
  <verify>Test-Path .gsd/phases/2/RETURN.md</verify>
  <done>Comprehensive §5 Return compiled and side-by-side comparison images generated for owner review.</done>
</task>

## Success Criteria
- [ ] Pytest passes 26/26 with R1 fixture green
- [ ] Backend quarantine 100% clean
- [ ] Impeccable detect clean across all 4 screens
- [ ] Zero hex drift verified against DESIGN.md
- [ ] Computed-font proof confirms Fraunces, Inter, JetBrains Mono
- [ ] Dual-resolution side-by-side images produced
- [ ] Complete §5 Return documented in .gsd/phases/2/RETURN.md
