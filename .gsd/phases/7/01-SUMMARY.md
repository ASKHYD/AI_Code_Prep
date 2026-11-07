# Wave 1 Implementation Summary: Streamlit Configuration, Core Shell & Login Gate

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Wave**: Wave 1  
**Completed**: 2026-11-07  
**Status**: COMPLETE (Tasks 1.1, 1.2, 1.3, 1.4)

---

## 1. Accomplishments

1. **Task 1.1 — Theme Configuration (`.streamlit/config.toml`)**:
   - Replaced legacy Direction A palette with Terracotta Editorial:
     - `primaryColor = "#C2452D"`
     - `backgroundColor = "#FFF8F0"`
     - `textColor = "#2C1810"`
     - `secondaryBackgroundColor = "#FFFFFF"`
   - Commit: `0cdd191`.

2. **Task 1.2 — Global Keyed CSS & Offline Base64 Typography (`app.py`)**:
   - Updated `FONT_DEFINITIONS` to map `DM Serif Display` and `Plus Jakarta Sans` woff2 files in `assets/fonts/`.
   - Injected `@font-face` rules using base64 data URIs for 100% offline capability.
   - Set up base typography hierarchy:
     - Headlines: `DM Serif Display`
     - Body & UI: `Plus Jakarta Sans`
     - Code & timers: `JetBrains Mono`
     - Tabular semibold numerals: `Plus Jakarta Sans` with `font-feature-settings: 'tnum' 1`.
   - Defined 24px bento containers, 1px warm hairlines (`rgba(74, 25, 66, 0.10)`), sandy quiet panels (`#E8D5B7`), and 9999px pill action buttons.
   - Commit: `94e71a4`.

3. **Task 1.3 — Topbar Shell & Official Brand Lockup (`app.py`)**:
   - Integrated Logo Variant A inline SVG (28×28 terracotta tile `#C2452D`, serif "A", olive `#6B7F3B` dot).
   - Wordmark reads "AI Prep Coach" in `DM Serif Display` 22px `#2C1810`.
   - Live status chips: active streak (`store.current_streak()` with yesterday-anchored logic) and problems due (`store.due_problems()`).
   - Integrated minimal Logout text action button.
   - Permanently eliminated legacy version chip and "Offline · Code-Judged" tag.

4. **Task 1.4 — Functional Login Gate & Screen (`app.py`)**:
   - Guarded Streamlit entry with session-state authentication: unauthenticated users see only Login / Create Account / Forgot Password matching `mockups/terracotta/login.html`.
   - Centered 24px white card, 44×44 Logo Variant A, serif headline and subline.
   - Real email confirmation handling: URL param `?verify=<raw_token>` triggers account activation.
   - Password reset handling: URL param `?reset=<raw_token>` renders Set New Password form.
   - Integrated with `auth_store.py` and `send_smtp_email()` with honest delivery feedback.
   - Commit: `8a4c0f4`.

---

## 2. Invariants Maintained
- 71/71 tests green in 30.70s.
- `coach/*.py` and problem JSON files strictly frozen.
