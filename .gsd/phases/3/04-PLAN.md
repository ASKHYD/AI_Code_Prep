---
phase: 3
plan: "04"
wave: 4
depends_on: ["03"]
---

# Plan 3.4: Verification Suite, Dry-Run Evidence & Phase Return

## Objective
Execute the full verification protocol for Phase 3: run the comprehensive test suite (all 5 required test categories + 31 baseline tests), verify migration dry-run and database isolation on copy DB, capture live browser proof of the updated Home screen at 1450×900, record resource accounting, and file the Phase 3 return.

## Context
- `tests/`
- `scratch/verify_coach.db`
- `coach.db`
- `docs/screenshots/`
- `.gsd/phases/3/PHASE_RETURN.md`

## Execution Gate
> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**

---

## Tasks

<task type="auto">
  <name>Task 4.1: Comprehensive Unit & Regression Test Suite</name>
  <files>tests/test_fsrs_core.py, tests/test_fsrs_migration.py, tests/test_fsrs_equivalence.py, tests/test_interleaving.py, tests/test_streak_regression.py</files>
  <action>
    <!-- Skill bindings: /agency-test-automation-engineer, /empirical-validation -->
    1. Run and verify all 5 required test categories:
       - **Category 1 (Rating Mapper)**: Exhaustive test matrix for `FAIL/TIMEOUT/ERROR` $\rightarrow$ `Again`, `PASS` + hints/multiple attempts $\rightarrow$ `Hard`, clean first `PASS` $\rightarrow$ `Good`, and strict assertion that `Easy` is NEVER returned.
       - **Category 2 (Migration & A1 Timestamp)**: Proof that historical attempts initialize cards with due timestamps derived from `last_attempt_date` (A1), and that running migration multiple times is 100% idempotent.
       - **Category 3 (Due-Set Equivalence)**: Compare the set of problems marked due by the old ladder vs FSRS on identical datasets. List every difference with an explicit technical explanation (e.g. FSRS continuous interval modeling vs discrete 1/3/7/21 days). Assert zero unexplained omissions (silent loss fails the phase).
       - **Category 4 (Interleaving Adjacency)**: Prove that multi-topic queues never have adjacent same-topic problems when an alternative topic is available.
       - **Category 5 (Streak Invariant)**: Prove that `CoachStore.current_streak` matches baseline behavior.
    2. Run full pytest suite across all 31 baseline tests + new Phase 3 tests.
    3. Capture and paste the full test summary line.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/ --tb=short</verify>
  <done>Full test suite green (31 baseline + all Phase 3 tests); all 5 test categories verified with 0 failures.</done>
</task>

<task type="auto">
  <name>Task 4.2: Migration Dry-Run & Production Database Isolation Proof</name>
  <files>scratch/verify_coach.db, coach.db</files>
  <action>
    <!-- Skill binding: /empirical-validation -->
    1. Execute migration dry-run on `scratch/verify_coach.db` (seeded copy of production database).
    2. Verify that `problem_fsrs_cards` is created and correctly populated.
    3. Assert that the `attempts` table in `scratch/verify_coach.db` is 100% identical before and after migration (`SELECT COUNT(*)` and checksum identical).
    4. Record the SHA256 of the real production `coach.db` before and after the execution of the phase:
       - Before: `ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`.
       - After: must match exactly.
       - The real production database is migrated ONLY once via the shipped production code path on candidate startup.
  </action>
  <verify>.venv\Scripts\python.exe -c "import hashlib; h = hashlib.sha256(open('coach.db', 'rb').read()).hexdigest(); assert h == 'ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79', f'Pollution detected: {h}'; print('Isolation OK:', h)"</verify>
  <done>Migration dry-run succeeds on copy DB with 0 writes to `attempts`; production `coach.db` SHA256 is verified 100% untouched.</done>
</task>

<task type="auto">
  <name>Task 4.3: Live 1450×900 Capture, Resource Accounting & Phase Return</name>
  <files>docs/screenshots/m2_p3_home_1450x900.png, .gsd/phases/3/PHASE_RETURN.md</files>
  <action>
    <!-- Skill bindings: /agency-evidence-collector, /agency-test-automation-engineer -->
    1. Invoke `/agency-evidence-collector` to capture live Chrome CDP screenshot of Home screen at 1450×900 viewport:
       - Save to `docs/screenshots/m2_p3_home_1450x900.png`.
       - Prove that the topbar due chip shows the FSRS due count and the Home daily section displays the interleaved queue with truthful copy.
    2. Compile the RESOURCES EXERCISED accounting block covering all named skills:
       - USED with evidence: `/agency-senior-developer`, `/agency-test-automation-engineer`, `/agency-minimal-change-engineer`, `/empirical-validation`, `/agency-evidence-collector`.
       - PARKED with technical reason: `/impeccable`, `/ui-ux-pro-max`, `/ui-styling`, `/design-system`, `/design`, `/brand`, `/agency-frontend-developer`, `/speckit-*`.
    3. Run `/verify 3` as the final internal verification step and quote its verdict and tally verbatim.
    4. File comprehensive report at `.gsd/phases/3/PHASE_RETURN.md`.
  </action>
  <verify>powershell -Command "Test-Path 'docs/screenshots/m2_p3_home_1450x900.png'; Test-Path '.gsd/phases/3/PHASE_RETURN.md'"</verify>
  <done>Live 1450×900 screenshot captured, resource accounting completed, `/verify 3` verdict quoted, and phase return filed.</done>
</task>

---

## Success Criteria
- [ ] All 5 test categories pass alongside 31 baseline tests.
- [ ] Database isolation proof verifies production `coach.db` is 100% untouched.
- [ ] Live 1450×900 screenshot confirms FSRS due chip and interleaved queue display.
- [ ] Phase return filed with full resource accounting and `/verify 3` verdict.

