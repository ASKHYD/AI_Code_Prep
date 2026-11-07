# Wave 0 Implementation Summary: Foundations, Typography & Auth Storage

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Wave**: Wave 0  
**Completed**: 2026-11-07  
**Status**: COMPLETE (Tasks 0.1, 0.2, 0.3)

---

## 1. Accomplishments

1. **Task 0.1 — Baseline & Secret Hygiene**:
   - Pytest baseline confirmed: 64/64 passing in 8.92s.
   - `coach.db` SHA-256 recorded: `8a709dc1b1304de1b78d9762e17188b19bfaf6c8d56e08e59c6c42d54356b75c`.
   - SQLite pre-existing row counts audited: `attempts` = 2, `problem_fsrs_cards` = 1.
   - `.gitignore` updated with `.env` (verified via `git check-ignore -v .env`).
   - `.env.example` created with template for `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_APP_PASSWORD`.
   - Commit: `4331be5`.

2. **Task 0.2 — Font Gate Resolution**:
   - Downloaded and self-hosted project-local `.woff2` font files into `assets/fonts/`:
     - `dm-serif-display-latin-400-normal.woff2` (24,744 bytes)
     - `plus-jakarta-sans-latin-400-normal.woff2` (11,816 bytes)
     - `plus-jakarta-sans-latin-500-normal.woff2` (12,312 bytes)
     - `plus-jakarta-sans-latin-600-normal.woff2` (12,188 bytes)
     - `plus-jakarta-sans-latin-700-normal.woff2` (12,244 bytes)
   - Magic headers validated (`b'wOF2'`). No external CDN links required at runtime.
   - Commit: `f824363`.

3. **Task 0.3 — Auth Module & Unit Test Battery**:
   - Implemented `auth_store.py` in project root (quarantined outside frozen `coach/*.py`):
     - `user_profile` schema in SQLite.
     - PBKDF2-HMAC-SHA256 password hashing with 600,000 iterations and unique random salts (`secrets.token_hex(16)`).
     - Raw verification & reset tokens via `secrets.token_urlsafe(32)` with SHA-256 token hashing.
     - Profile lifecycle: pending registration, token verification & activation, pending login rejection, resend verification token, password reset request and completion.
     - SMTP delivery helper using Python standard library `smtplib` + STARTTLS with honest delivery failure reporting.
   - Authored unit test battery `tests/test_auth.py` (7 tests).
   - Test suite expanded to **71/71 passing in 11.74s** (64 baseline + 7 auth).
   - Commit: `fa06216`.

---

## 2. Invariants Maintained
- `coach/*.py` strictly frozen (0 diffs).
- `data/problems/*.json` strictly frozen (0 diffs).
- All pre-existing test suites 100% green.
