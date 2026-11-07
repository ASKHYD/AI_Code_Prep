# Phase 7 Plan Contract & Plan-Checker Validation

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Date**: 2026-11-07  
**Scope Source**: Block P7 (`PHASE 7 DISCUSS BLOCK`), `DESIGN.md`, Approved Mockups (`mockups/terracotta/`)  
**Status**: PLANNING COMPLETE — READY FOR AUDIT  

---

## 1. Execution Gate (Verbatim Binding)

> **EXECUTION GATE: Phase 7 is gated by audit. No tasks in Plans 7.0–7.4 may be executed until the plan set has been reviewed and audited by the owner / Milo. Furthermore, during execution, `coach/*.py` and `data/problems/*.json` remain strictly FROZEN. Existing database tables in `coach.db` (`attempts`, `problem_fsrs_cards`) are untouched in schema and data. Pytest baseline invariant (64/64) must be preserved, with new auth tests adding to the count.**

---

## 2. Wave Structure & Plan Breakdown

```
Wave 0: Foundations, Offline Typography & Functional Auth Storage
└── 00-PLAN.md: Baseline pytest (64/64), coach.db SHA256 audit, .gitignore & .env.example,
                 FONT GATE resolution (self-host DM Serif Display & Plus Jakarta Sans woff2),
                 auth_store.py module (PBKDF2 salt, token hashing, SMTP STARTTLS),
                 and test_auth.py suite.

Wave 1: Streamlit Configuration, Core Shell & Login Gate
└── 01-PLAN.md: .streamlit/config.toml Terracotta palette, get_global_css() offline base64 fonts
                 and keyed CSS, render_topbar() with Logo Variant A, live streak/due chips,
                 text logout button, and render_login() with email confirm/reset flow.

Wave 2: Home Bento & Dashboard Implementation
└── 02-PLAN.md: Home screen restyle (DM Serif headline, olive streak tile, due tile,
                 90% retention tabular numeral, verbatim FSRS copy, due-first interleaved
                 problem queue with amber due pills and computed deltas), and Dashboard restyle
                 (attempted-only Plotly chart above full 11-topic table with NOT STARTED).

Wave 3: Practice Arena & Mock Interview Simulation
└── 03-PLAN.md: Practice Arena restyle (Round 2 slim picker "N. Title · Topic (Difficulty)",
                 padded prev/next buttons, signature from starter_code.splitlines()[0],
                 small-caps signature label, dark 450px editor card, natural-width button,
                 authentic Output Card per F1 without memory metrics), and Mock Interview
                 restyling (sandy facts panel, 2-place MM:SS countdown timer, scorecard).

Wave 4: Verification, CDP Captures & Plan Audit Gate Return
└── 04-PLAN.md: Automated anti-slop audit (0 tropes), numeral tracing to store/JSON,
                 14 Chrome CDP captures (7 views @ 1450×900 primary, 7 views @ 1920×1080),
                 64+N pytest pass, coach.db immutability audit, Impeccable critique,
                 finish gate review, and PHASE_RETURN.md with full resources exercised table.
```

---

## 3. Plan-Checker Coverage Matrix (18/18 Dimensions)

| Dimension | Scope Item | Covering Plan & Task | Verification Mechanism |
| :--- | :--- | :--- | :--- |
| **1** | Baseline Pytest & Code Quarantine | Plan 7.0, Task 0.1; Plan 7.4, Task 4.1 | 64/64 baseline tests green; git diff confirms `coach/*.py` and problem JSONs untouched |
| **2** | SQLite Existing Tables Immutability | Plan 7.0, Task 0.1; Plan 7.4, Task 4.1 | Row counts for `attempts` and `problem_fsrs_cards` identical before and after |
| **3** | Secret Hygiene (.env & .gitignore) | Plan 7.0, Task 0.1 | `.env` added to `.gitignore`, `.env.example` created, 0 credentials printed or committed |
| **4** | Font Gate Offline Self-Hosting | Plan 7.0, Task 0.2 | `DM Serif Display` and `Plus Jakarta Sans` woff2 files downloaded to `assets/fonts/` |
| **5** | Auth Store & Password Security | Plan 7.0, Task 0.3 | `auth_store.py` with PBKDF2-HMAC-SHA256, 600k iterations, per-profile salt, SHA-256 tokens |
| **6** | SMTP Real Confirmation Flow | Plan 7.0, Task 0.3; Plan 7.1, Task 1.4 | Standard library `smtplib` STARTTLS; honest error handling; activation via `?verify=<token>` |
| **7** | Streamlit Theme Configuration | Plan 7.1, Task 1.1 | `.streamlit/config.toml` updated with Terracotta primary, canvas, and text tokens |
| **8** | Global Keyed CSS & Offline Typography | Plan 7.1, Task 1.2 | `get_global_css()` embeds base64 woff2 for all 3 families; keyed CSS `.st-key-*` |
| **9** | Topbar Shell & Brand Lockup | Plan 7.1, Task 1.3 | Logo Variant A 28×28 inline SVG, serif wordmark "AI Prep Coach", live chips, text logout |
| **10** | Login Screen Presentation | Plan 7.1, Task 1.4 | Mirrors `login.html`: 44×44 Logo Variant A, 24px card, hairline border, tabs for login/signup/reset |
| **11** | Home Bento & FSRS Copy | Plan 7.2, Task 2.1 | 3 stat tiles (olive streak, due, 90.0% retention), verbatim FSRS text, primary pill CTA |
| **12** | Due-First Queue Table (C1, C2, C3) | Plan 7.2, Task 2.2 | `build_interleaved_queue` due-first, amber `DUE FOR REVIEW` pill, computed next due deltas |
| **13** | Dashboard Chart & Full Topic Table | Plan 7.2, Task 2.3 | Plotly chart for ATTEMPTED topics only ABOVE full table; unattempted rows `NOT STARTED` |
| **14** | Practice Slim Picker & Signature | Plan 7.3, Task 3.1 & 3.2 | Format `"N. Title · Topic (Difficulty)"`, signature from `starter_code.splitlines()[0]` |
| **15** | Output Card Honesty (F1 Invariant) | Plan 7.3, Task 3.3 | Verdict, visible tests with expected/got, real attempt runtime; 0 invented telemetry/memory |
| **16** | Mock Facts Panel & 2-Place Timer | Plan 7.3, Task 3.4 | 45-min facts strip, countdown timer strictly at two display places (`MM:SS`), scorecard |
| **17** | Anti-Slop Audit & Numeral Tracing | Plan 7.4, Task 4.2 | DOM audit verifying 0 forbidden tropes; every numeral traced to SQLite/JSON |
| **18** | Dual-Resolution CDP Captures | Plan 7.4, Task 4.3 | Headless Chrome CDP captures of 7 views at 1450×900 primary and 1920×1080 |

---

## 4. Per-Wave Skill Bindings Matrix

- **Wave 0 (Foundations & Auth Storage)**:
  - `/test-driven-development`: Auth module testing (`tests/test_auth.py`).
  - `/empirical-validation`: Pytest 64/64 baseline and SQLite SHA256 audit.
- **Wave 1 (Streamlit Config, Core Shell & Login Gate)**:
  - `developing-with-streamlit`: Streamlit config theming, session-state auth guard, keyed CSS.
  - `/ui-styling`: Translation of Terracotta tokens to Streamlit styling rules.
  - `/design-system`: Token hierarchy consistency across config, base64 `@font-face`, and components.
  - `/brand`: Brand enforcement (official name "AI Prep Coach", Logo Variant A SVGs).
- **Wave 2 (Home Bento & Dashboard Implementation)**:
  - `developing-with-streamlit`: Multi-column bento layouts, Plotly integration, dynamic queue rows.
  - `/ui-styling`: Bento card aesthetics, status badge styling, Plotly palette tuning.
- **Wave 3 (Practice Arena & Mock Interview Simulation)**:
  - `developing-with-streamlit`: Ace code editor integration, countdown loops, Output Card layout.
  - `/ui-styling`: Slim picker row styling, dark editor container, Output Card verdict styling.
- **Wave 4 (Verification, CDP Captures & Gate Return)**:
  - `/empirical-validation`: Test suite pass (64+N) and database immutability verification.
  - `/agency-evidence-collector`: Dual-resolution headless Chrome CDP captures (1450×900 primary & 1920×1080).
  - `/agency-ui-finish-gate-reviewer`: Anti-slop DOM audit, forbidden trope detection, visual finish review.
  - `/impeccable`: Contrast compliance, typography hierarchy, and layout anomaly critique.


