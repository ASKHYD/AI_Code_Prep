# Phase 7 Discussion: Terracotta Editorial in the Live App (T2)

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Date**: 2026-11-07  
**Authorization Source**: Block P7 (`PHASE 7 DISCUSS BLOCK`)  
**Status**: DISCUSS & PLAN AUTHORIZED — AWAITING PLAN AUDIT  

---

## 1. Executive Summary

Milestone 3 Phase 7 translates the approved static HTML/CSS mockups from Phase 6 (`mockups/terracotta/`) into the live Streamlit application (`app.py`), retiring the legacy Direction A styling and establishing the official "AI Prep Coach" brand identity.

Crucially, per owner windup decisions on 2026-11-07, Phase 7 also implements a functional entry gate: single-user authentication with real confirmation emails on account creation via Python standard library `smtplib` + STARTTLS, local `.env` credentials, and full password recovery flow.

All underlying learning engine algorithms, FSRS card scheduling, topic interleaving logic, and frozen SQLite attempt history from Phase 3 remain 100% untouched.

---

## 2. Font Gate Audit (Binding Pre-Condition)

Per Block P7 instruction:
> *"FONT GATE: before planning tasks that depend on fonts, list the actual woff2 files on disk for all three families (assets/fonts/) with names and sizes; if Plus Jakarta Sans is absent, the plan's first task is self-hosting it (project-local, no CDN at runtime — the app is offline)."*

### Disk Inspection of `assets/fonts/` (2026-11-07):
| Family | Files Found | Status |
| :--- | :--- | :--- |
| **Fraunces** | `fraunces-latin-500-normal.woff2` (18,000 B)<br>`fraunces-latin-600-normal.woff2` (18,096 B)<br>`fraunces-latin-700-normal.woff2` (18,212 B)<br>`fraunces-latin-800-normal.woff2` (18,224 B) | Legacy Direction A font (preserved on disk) |
| **Inter** | `inter-latin-400-normal.woff2` (23,664 B)<br>`inter-latin-500-normal.woff2` (24,272 B)<br>`inter-latin-600-normal.woff2` (24,452 B)<br>`inter-latin-700-normal.woff2` (24,356 B) | Legacy Direction A font (preserved on disk) |
| **JetBrains Mono** | `jetbrains-mono-latin-400-normal.woff2` (21,168 B)<br>`jetbrains-mono-latin-500-normal.woff2` (21,832 B)<br>`jetbrains-mono-latin-600-normal.woff2` (21,860 B)<br>`jetbrains-mono-latin-700-normal.woff2` (21,908 B) | **PRESENT** (Code & timer font ready) |
| **DM Serif Display** | *None* | **ABSENT** |
| **Plus Jakarta Sans** | *None* | **ABSENT** |

### Font Gate Finding & Remediation:
Both `DM Serif Display` and `Plus Jakarta Sans` are absent from `assets/fonts/`.  
**Remediation in Plan 7.0 (Wave 0 Task 0.2)**: Download and self-host project-local `.woff2` files for `DM Serif Display` and `Plus Jakarta Sans` into `assets/fonts/` so the application runs 100% offline with zero external CDN dependencies.

---

## 3. Architecture & Functional Specification

### 3.1 Brand Identity & Chrome
- **App Name**: `AI Prep Coach` (owner binding decision; replaces "Coach" and "AI Coding Prep Coach").
- **Topbar Lockup**:
  - Logo Variant A: 28×28 inline SVG (rounded terracotta tile `#C2452D`, sun-white serif "A", olive `#6B7F3B` dot).
  - Wordmark: `AI Prep Coach` rendered in `DM Serif Display`, 22px, `#2C1810`.
  - Navigation: Pill items (`Home`, `Practice Arena`, `Mock Interview`, `Dashboard`).
  - Active Streak Chip: Live read from `store.current_streak()` with yesterday-anchored semantics (C1).
  - Due Chip: Live read from `store.due_problems()` (C2).
  - Logout Action: Text button placed at the far right of the topbar after the due chip.
  - Eliminated: Legacy "3.11/3.12" runtime version chip and "Offline · Code-Judged" tag (both dropped during Phase 6 mockup sign-off).

### 3.2 Authentication & Real Confirmation Email Flow
- **Module Quarantine**: Auth logic lives in a dedicated root module `auth_store.py`, preserving the freeze on `coach/*.py`.
- **Database Schema**: New SQLite table `user_profile` in `coach.db`:
  ```sql
  CREATE TABLE IF NOT EXISTS user_profile (
      email TEXT PRIMARY KEY,
      password_hash TEXT NOT NULL,
      salt TEXT NOT NULL,
      status TEXT NOT NULL,           -- 'pending' | 'active'
      verify_token_hash TEXT,
      verify_expires_at TEXT,
      reset_token_hash TEXT,
      reset_expires_at TEXT,
      created_at TEXT NOT NULL
  );
  ```
- **Password Security**: PBKDF2-HMAC-SHA256 with 600,000 iterations and per-profile salt (`secrets.token_hex(16)`). Never plaintext.
- **Email Delivery via SMTP**:
  - Standard library `smtplib` with `STARTTLS`.
  - Configuration via `.env` file (gitignored):
    - `SMTP_HOST` (default: `smtp.gmail.com`)
    - `SMTP_PORT` (default: `587`)
    - `SMTP_USER` (owner's Gmail address)
    - `SMTP_APP_PASSWORD` (Google account 16-character App Password)
  - Security invariant: Code checks presence of keys only; never logs or prints credentials.
- **Confirmation Lifecycle**:
  1. **Signup**: User submits email + password $\rightarrow$ profile inserted with status `pending`.
  2. **Token Minting**: Raw token generated via `secrets.token_urlsafe(32)`. SHA-256 hash stored in DB with 24-hour expiration.
  3. **Email Dispatch**: Sends HTML/text email containing link `http://localhost:8501/?verify=<raw_token>`.
  4. **Activation**: Opening link loads Streamlit with query parameter `verify` $\rightarrow$ verifies raw token against stored hash, checks timestamp $\le$ expiry $\rightarrow$ updates status to `active`, clears token, displays "Email confirmed — you can log in now."
  5. **Pending Guard**: Attempting to log in while status is `pending` is rejected with message "Confirm your email to activate your account" and displays a "Resend confirmation email" button (invalidates prior token, issues fresh 24h token).
  6. **Password Recovery**: "Forgot password?" form accepts email $\rightarrow$ mints reset token (1-hour expiry) $\rightarrow$ emails `http://localhost:8501/?reset=<raw_token>` $\rightarrow$ opening link renders in-app new password form.
  7. **Failure Honesty**: If SMTP fails (offline network, invalid credentials), profile remains `pending`, UI states delivery failure honestly and provides "Resend confirmation email". UI NEVER claims email was sent when SMTP raised an exception.
- **Session State Gating**: Streamlit `st.session_state["authenticated_user"]` controls rendering. Unauthenticated sessions see ONLY the login / register / verify / reset surfaces.
- **Single-User Scope**: Access gate only. All practice attempts, FSRS cards, and learning metrics in `coach.db` remain global.

### 3.3 Preserved Learning Loop Invariants (Post-Corrective)
- **Home Queue Order**: Generated via `build_interleaved_queue` with due-first partition (C3).
- **Home Queue Rows**: Amber `DUE FOR REVIEW` pill from `store.due_problems()` and dynamically computed `Next Due: +N Day(s)` delta from `card.due` (C2). Zero hardcoded `"Next Due: +1"`.
- **Active Streak**: Computed from `store.current_streak()` with yesterday-anchored logic (C1).
- **FSRS Copy**: Exact verbatim line preserved:
  `"Adaptive spaced repetition (FSRS) scheduled from your objective test results."`
- **Practice Arena**:
  - Slim picker row formatted as `N. Title · Topic (Difficulty)`.
  - Prev/Next arrow buttons padded to prevent clipping at 1450px viewport (no X10).
  - Problem Card signature block displays small-caps `STARTER FUNCTION SIGNATURE` label (X9), signature extracted from `starter_code.splitlines()[0]` for all 12 problems (X6).
  - Editor: dark anchor card (450px height, JetBrains Mono, iframe internals untouched).
  - Output Card: F1 invariant strictly enforced (verdict, visible test cases with expected/got, real attempt runtime; zero invented telemetry, zero memory metrics).
- **Dashboard**:
  - Plotly horizontal pass-rate chart of ATTEMPTED topics only placed ABOVE the full topic table.
  - Table below lists all 11 topics; unattempted rows read `NOT STARTED` (never 0%).
  - Figures strictly sourced from `store.topic_stats()`.
- **Mock Interview**:
  - Start facts panel: 45 min, 2 interleaved problems, hints allowed.
  - Session countdown timer: formatted to exactly TWO display places (`MM:SS`) in JetBrains Mono.
  - Session-scoped scoring with zero-write unsolved end.

---

## 4. Wave Decomposition & Execution Strategy

```
Wave 0: Foundations, Offline Typography & Functional Auth Storage
├── Task 0.1: Baseline Pytest (64/64), coach.db SHA256 audit, .gitignore & .env.example
├── Task 0.2: FONT GATE: Download & self-host DM Serif Display & Plus Jakarta Sans woff2
└── Task 0.3: Auth Module (auth_store.py), SQLite user_profile, SMTP STARTTLS, unit tests

Wave 1: Streamlit Configuration, Core Shell & Login Gate
├── Task 1.1: Update .streamlit/config.toml with Terracotta palette
├── Task 1.2: Global CSS (get_global_css) with base64 offline fonts & Terracotta tokens
├── Task 1.3: Topbar lockup (render_topbar) with Logo Variant A, live chips, logout button
└── Task 1.4: Login Gate & Screen (render_login) with confirm/reset flow (login.html contract)

Wave 2: Home Bento & Dashboard Implementation
├── Task 2.1: Home screen bento tiles (Streak olive, Due, Target Retention) & FSRS copy
├── Task 2.2: Home problem queue table (due-first per C3, amber pills per C2, computed deltas)
└── Task 2.3: Dashboard view (Plotly attempted chart above full topic table with NOT STARTED)

Wave 3: Practice Arena & Mock Interview Simulation
├── Task 3.1: Practice Arena slim picker (Round 2 format) & prev/next buttons
├── Task 3.2: Problem card signature block (X6 starter line, X9 label) & dark editor
├── Task 3.3: Output Card rebuild per F1 (real verdict, visible tests, real runtime, no memory)
└── Task 3.4: Mock Interview views (Start facts panel, 2-place MM:SS timer session, scorecard)

Wave 4: Verification, CDP Captures & Plan Audit Gate Return
├── Task 4.1: Test suite pass (64 baseline + new auth tests) & coach.db immutability audit
├── Task 4.2: Automated anti-slop audit (0 tropes) & numeral tracing against live store
├── Task 4.3: Dual-resolution Chrome CDP captures (1450×900 primary & 1920×1080) for all 7 screens
└── Task 4.4: Impeccable critique, finish gate review, E2E auth proof status, PHASE_RETURN.md
```

---

## 5. Freezes & Invariants
- `coach/*.py` (`store.py`, `fsrs_engine.py`, `interleaving.py`, `judge.py`, `problems.py`, `timer.py`) strictly **FROZEN**.
- `data/problems/*.json` strictly **FROZEN**.
- Existing SQLite tables in `coach.db` (`attempts`, `problem_fsrs_cards`, `streaks`, `problem_notes`) have schema and contents preserved.
- Suite baseline: 64/64 pytest passing; new auth tests expand the count.

