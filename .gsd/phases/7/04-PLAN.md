# Wave 4: Verification, CDP Captures & Plan Audit Gate Return

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.4 (Wave 4)  
**Status**: DRAFT — READY FOR AUDIT  

---

## 1. Plan Overview

Wave 4 provides the exhaustive empirical evidence and design finish audit for Phase 7:
1. Validates test suite integrity (asserts 64 baseline tests + all new auth tests green).
2. Verifies `coach.db` immutability for pre-existing tables (`attempts`, `problem_fsrs_cards`).
3. Executes the automated anti-slop audit and traces all live numerals to the database and problem catalogs.
4. Captures dual-resolution Chrome CDP screenshots for all 7 application views at 1450×900 primary and 1920×1080.
5. Runs Impeccable critique and `/agency-ui-finish-gate-reviewer` over live captures.
6. Conducts or documents the E2E email confirmation proof (confirming real receipt or marking WAITING ON OWNER if Gmail app password is not yet configured).
7. Files the comprehensive `.gsd/phases/7/PHASE_RETURN.md` with full resources exercised accounting.

---

## 2. Tasks

### Task 4.1: Test Suite Regression & Database Immutability Audit
- **Actions**:
  - Run full test suite via `.venv/Scripts/python -m pytest tests/`.
  - Assert that all 64 baseline tests pass, and all new `tests/test_auth.py` tests pass (e.g. 70+/70+ passing).
  - Verify SQLite database immutability:
    - Query `coach.db` for row counts of `attempts` and `problem_fsrs_cards`.
    - Assert that row counts exactly match the Task 0.1 pre-implementation baseline.
    - Confirm that only the new `user_profile` table was added.
- **Verification**:
  - Console test report: 100% green.
  - SQLite query outputs quoted in return.

### Task 4.2: Automated Anti-Slop Audit & Live Numeral Tracing
- **Actions**:
  - Author and run `scratch/audit_live_terracotta.py`:
    - Checks live Streamlit DOM across all views for:
      - 0 CSS gradients (`linear-gradient`, `radial-gradient`).
      - 0 backdrop filters / frosted glass (`backdrop-filter: blur`).
      - 0 glowing drop shadows (`box-shadow` with spread/color glow).
      - 0 arch containers or decorative pseudo-elements.
      - 0 meta-captions or developer specimen notes in product copy.
      - 0 invented memory metrics or telemetry in Output Cards.
    - Numeral Tracing:
      - Traces Home active streak, due count, target retention to database/engine.
      - Traces Dashboard attempt count, pass rate, and topic metrics to `store.topic_stats()`.
- **Verification**:
  - Audit output: 0 violations detected.
  - Numeral trace log verified and quoted.

### Task 4.3: Dual-Resolution Chrome CDP Captures (1450×900 & 1920×1080)
- **Actions**:
  - Author and run `scratch/capture_live_terracotta.py` using Chrome DevTools Protocol (CDP):
    - Captures at **1450×900** (Primary Viewport) and **1920×1080** (Desktop Viewport):
      1. `login_1450x900.png` & `login_1920x1080.png`
      2. `home_1450x900.png` & `home_1920x1080.png`
      3. `practice_1450x900.png` & `practice_1920x1080.png`
      4. `mock_start_1450x900.png` & `mock_start_1920x1080.png`
      5. `mock_session_1450x900.png` & `mock_session_1920x1080.png`
      6. `mock_scorecard_1450x900.png` & `mock_scorecard_1920x1080.png`
      7. `dashboard_1450x900.png` & `dashboard_1920x1080.png`
    - Saves all 14 images to `docs/screenshots/live_terracotta/` and copies them to the artifact directory.
    - Verifies zero horizontal overflow (`scrollWidth == clientWidth`) at 1450px across all views.
- **Verification**:
  - 14 image files exist with non-zero byte size.
  - Visual inspection confirms exact alignment with `mockups/terracotta/`.

### Task 4.4: Impeccable Critique, E2E Proof Status & Phase Return
- **Actions**:
  - Run Impeccable critique and `/agency-ui-finish-gate-reviewer` on captured live screens.
  - Validate E2E Authentication Flow:
    - If owner `.env` has active Gmail credentials: capture live proof of account creation, activation via emailed link, login success, resend, and password reset.
    - If owner has not yet configured `.env`: report the SMTP live delivery proof as **WAITING ON OWNER** (never simulated, never faked).
  - Author `.gsd/phases/7/PHASE_RETURN.md`:
    - Executive summary.
    - Side-by-side comparison matrix (mockups vs live Streamlit implementation).
    - Pytest results and DB immutability audit.
    - Anti-slop audit report and numeral tracing table.
    - Full **RESOURCES EXERCISED** accounting table covering:
      `/developing-with-streamlit`, `/ui-ux-pro-max`, `/ui-styling`, `/design-system`, `/brand`, `/design`, `/impeccable`, `/agency-frontend-developer`, `/agency-ui-finish-gate-reviewer`, `/empirical-validation`.
- **Verification**:
  - `.gsd/phases/7/PHASE_RETURN.md` authored and complete.
