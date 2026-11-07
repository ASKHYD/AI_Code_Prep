# Wave 0: Foundations, Offline Typography & Functional Auth Storage

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.0 (Wave 0)  
**Status**: DRAFT — READY FOR AUDIT  

---

## 1. Plan Overview

Wave 0 establishes the unbreakable baseline for Phase 7:
1. Verifies the existing 64/64 pytest suite and audits `coach.db` integrity before any modifications.
2. Resolves the Font Gate by downloading and self-hosting `DM Serif Display` and `Plus Jakarta Sans` woff2 files in `assets/fonts/` for 100% offline capability.
3. Adds `.env` to `.gitignore` and creates `.env.example` for secure SMTP configuration.
4. Implements `auth_store.py` in the root directory (preserving the freeze on `coach/*.py`) with PBKDF2 password hashing, SHA-256 token hashing, SQLite `user_profile` persistence, and standard library `smtplib` STARTTLS integration.
5. Authors a dedicated unit test battery `tests/test_auth.py` covering all registration, hashing, expiration, activation, recovery, and SMTP error pathways.

---

## 2. Tasks

### Task 0.1: Test Baseline, Database Audit & Secret Hygiene
- **Actions**:
  - Run `.venv/Scripts/python -m pytest tests/` and record the baseline (assert 64/64 passing).
  - Compute initial SHA256 of `coach.db` and record exact row counts for existing tables:
    `SELECT count(*) FROM attempts;`
    `SELECT count(*) FROM problem_fsrs_cards;`
  - Update `.gitignore` to append `.env` (ensuring credentials are never committed).
  - Create `.env.example` with documented keys:
    ```
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=your_email@gmail.com
    SMTP_APP_PASSWORD=your_16_char_google_app_password
    ```
- **Verification**:
  - `git check-ignore -v .env` confirms `.env` is ignored.
  - Pytest baseline recorded at 64 passing.
  - Table row counts recorded.

### Task 0.2: Font Gate Resolution — Self-Host DM Serif Display & Plus Jakarta Sans
- **Actions**:
  - Download project-local `.woff2` font files for:
    - `DM Serif Display` (regular / 400)
    - `Plus Jakarta Sans` (weights: 400, 500, 600, 700)
  - Place them into `assets/fonts/`:
    - `dm-serif-display-latin-400-normal.woff2`
    - `plus-jakarta-sans-latin-400-normal.woff2`
    - `plus-jakarta-sans-latin-500-normal.woff2`
    - `plus-jakarta-sans-latin-600-normal.woff2`
    - `plus-jakarta-sans-latin-700-normal.woff2`
  - Verify file sizes on disk (> 15 KB each, valid woff2 magic header).
- **Verification**:
  - Powershell `Get-ChildItem -Path assets/fonts` lists all 5 new woff2 files alongside existing JetBrains Mono, Inter, and Fraunces files.
  - No remote URL or external CDN link used.

### Task 0.3: Auth Module (`auth_store.py`) & Auth Test Suite (`tests/test_auth.py`)
- **Actions**:
  - Create `auth_store.py` (outside `coach/`):
    - Table creation: `user_profile (email TEXT PRIMARY KEY, password_hash TEXT, salt TEXT, status TEXT, verify_token_hash TEXT, verify_expires_at TEXT, reset_token_hash TEXT, reset_expires_at TEXT, created_at TEXT)`.
    - Password hashing: `hash_password(password, salt=None) -> (hash, salt)` using `hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 600000)`.
    - Token helpers: `generate_token() -> (raw_token, token_hash)` using `secrets.token_urlsafe(32)` and `hashlib.sha256`.
    - Profile operations:
      - `create_pending_profile(email, password) -> raw_token`
      - `verify_email_token(raw_token) -> (bool, str)` (activates profile if valid and unexpired)
      - `authenticate_user(email, password) -> (bool, str)` (returns success, reason, e.g. "pending_verification")
      - `resend_verification_email(email) -> (bool, raw_token, str)`
      - `request_password_reset(email) -> (bool, raw_token, str)`
      - `reset_password_with_token(raw_token, new_password) -> (bool, str)`
    - SMTP Mailer: `send_smtp_email(to_email, subject, body_text, body_html) -> (bool, str)` using `smtplib.SMTP(host, port)` + `starttls()`. Honest error handling catching `smtplib.SMTPException`, socket errors, and missing `.env` configuration without crashing.
  - Create `tests/test_auth.py`:
    - Unit tests for password hashing & unique per-user salts.
    - Profile creation and status `pending`.
    - Token generation and verification with expiration edge cases (active vs expired).
    - Authentication rejection when status is `pending` vs wrong password vs success.
    - Resend verification token invalidating previous token.
    - Password reset flow end-to-end.
    - Mocked SMTP delivery success and mocked delivery failure handling.
- **Verification**:
  - Run `.venv/Scripts/python -m pytest tests/test_auth.py` — all new tests pass.
  - Run full suite `.venv/Scripts/python -m pytest tests/` — 64 baseline + new auth tests all pass.
