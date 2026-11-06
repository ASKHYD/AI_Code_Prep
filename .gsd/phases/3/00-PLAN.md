---
phase: 3
plan: "00"
wave: 0
depends_on: []
---

# Plan 3.0: Baseline, Dependency Gate & Isolation Protocol

## Objective
Establish the execution baseline and dependency requirements for Phase 3 (FSRS + Interleaving) with zero production code changes. Verify that the `fsrs` package requirement is identified and pinned, record the baseline test suite results, enforce strict database isolation, and state all phase boundaries and freezes.

## Context
- `.gsd/SPEC.md`
- `.gsd/ROADMAP.md`
- `requirements.txt`
- `coach/store.py`
- `coach.db`

## Execution Gate (Verbatim Binding)
> **EXECUTION GATE: /execute 3 may not start until G2 holds — Phase 2 closed (owner live approval + closure bookkeeping).**
>
> *Gate G1 Status*: VERIFIED. Backend verification battery audited by Milo 2026-11-07: B1–B7 pass, real-DB SHA256 identical (`ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`), defects NONE functional. The B6 signature divergence finding belongs to Phase 2 Addendum V2 and is strictly excluded from Phase 3 scope.
> *Gate G2 Status*: PENDING. Phase 2 live approval on `http://localhost:8501` and closure bookkeeping required before `/execute 3`.

---

## Tasks

<task type="auto">
  <name>Task 0.1: FSRS Dependency Load-or-Report-Missing Gate</name>
  <files>requirements.txt</files>
  <action>
    <!-- Skill binding: /empirical-validation -->
    1. Invoke `/empirical-validation` to verify the presence or absence of the `fsrs` (py-fsrs) package in the current `.venv`.
    2. Check via python import: if `fsrs` is absent (verified `ModuleNotFoundError`), pin `fsrs==6.3.2` into `requirements.txt` as a required dependency.
    3. Install `fsrs==6.3.2` via `.venv\Scripts\pip.exe install fsrs==6.3.2`.
    4. Confirm that post-install, `import fsrs` succeeds completely offline with zero network calls at runtime.
    5. Output the exact installed version string.
  </action>
  <verify>.venv\Scripts\python.exe -c "import fsrs; print('FSRS OK:', fsrs.__version__ if hasattr(fsrs, '__version__') else 'installed')"</verify>
  <done>`fsrs==6.3.2` is pinned in `requirements.txt`, import succeeds in `.venv`, and offline operation is confirmed.</done>
</task>

<task type="auto">
  <name>Task 0.2: Baseline Test Suite & Database Isolation Invariant</name>
  <files>scratch/verify_coach.db, coach.db</files>
  <action>
    <!-- Skill binding: /empirical-validation -->
    1. Invoke `/empirical-validation` to record the read-only SHA256 of `coach.db` (`ac1d19de225221ed7c296604019d13f50bf52c9690c73063ac482f45b4770a79`).
    2. Record the baseline pytest summary line using `.venv\Scripts\pytest.exe -o pythonpath=. tests/` (31 passed expected).
    3. Restate the scratch-copy protocol: all migration development, dry runs, and integration experiments MUST run against `scratch/verify_coach.db` (or temporary copies). The production database `coach.db` is migrated ONLY once via the shipped production code path.
    4. Explicitly reaffirm exclusions: This phase does NOT touch the 7 problem signature divergences identified in B6 (owned by Phase 2 Addendum V2), does NOT modify problem JSON files in `data/problems/*.json`, and does NOT modify judge execution semantics.
  </action>
  <verify>.venv\Scripts\pytest.exe -o pythonpath=. tests/ --tb=short</verify>
  <done>Pytest passes 31/31, `coach.db` SHA256 is recorded, and database isolation protocol is established.</done>
</task>

---

## Success Criteria
- [ ] `fsrs==6.3.2` is pinned in `requirements.txt` and verified importable.
- [ ] Baseline test suite passes 31/31 without warnings.
- [ ] Database isolation protocol is established with recorded SHA256 hash.
- [ ] Gate G2 execution lock is prominently documented.
