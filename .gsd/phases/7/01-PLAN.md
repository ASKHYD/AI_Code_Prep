# Wave 1: Streamlit Configuration, Core Shell & Login Gate

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Plan**: 7.1 (Wave 1)  
**Status**: DRAFT — READY FOR AUDIT  

---

## 1. Plan Overview

Wave 1 establishes the Terracotta visual foundation and entry gate in the live Streamlit application:
1. Reconfigures `.streamlit/config.toml` with the Terracotta palette.
2. Rewrites `get_global_css()` in `app.py` to embed base64 offline woff2 fonts (`DM Serif Display`, `Plus Jakarta Sans`, `JetBrains Mono`), defining the complete Terracotta design tokens, 24px bento containers, 1px warm hairlines, and keyed CSS (`.st-key-*`).
3. Rebuilds `render_topbar()` with the official Logo Variant A inline SVG (28×28), the serif wordmark "AI Prep Coach", navigation pills, live store streak and due chips, and a right-aligned text Logout action button (retiring the version chip and offline tag).
4. Implements `render_login()` and the session-state auth guard, matching `mockups/terracotta/login.html` with real email confirmation links and password reset flows.

---

## 2. Tasks

### Task 1.1: Streamlit Theme Configuration (`.streamlit/config.toml`)
- **Actions**:
  - Update `.streamlit/config.toml` theme variables:
    ```toml
    [theme]
    base = "light"
    primaryColor = "#C2452D"
    backgroundColor = "#FFF8F0"
    secondaryBackgroundColor = "#FFFFFF"
    textColor = "#2C1810"
    font = "sans serif"
    ```
- **Verification**:
  - Inspect config file and verify Streamlit starts without syntax errors.

### Task 1.2: Terracotta Global CSS & Offline Typography (`app.py`)
- **Actions**:
  - Update `FONT_DEFINITIONS` in `app.py` to map:
    - `DM Serif Display` $\rightarrow$ `dm-serif-display-latin-400-normal.woff2`
    - `Plus Jakarta Sans` $\rightarrow$ weights 400, 500, 600, 700 `.woff2` files
    - `JetBrains Mono` $\rightarrow$ weights 400, 500, 600, 700 `.woff2` files
  - Rewrite `get_global_css()`:
    - Base typography: `html, body, p, span, label, button, .stMarkdown` use `'Plus Jakarta Sans', sans-serif`.
    - Display typography: `h1, h2, h3, .wordmark` use `'DM Serif Display', Georgia, serif`.
    - Code & timer: `code, pre, .timer-mono, .stCode` use `'JetBrains Mono', monospace`.
    - Tabular numerals: `div[data-testid="stMetricValue"], .stat-number` use `'Plus Jakarta Sans', sans-serif` with `font-feature-settings: 'tnum' 1; font-weight: 700;`.
    - Tokens:
      - Canvas: `#FFF8F0`
      - Bento cards: `background: #FFFFFF; border: 1px solid rgba(74, 25, 66, 0.10); border-radius: 24px;`
      - Quiet panel / strip: `background: #E8D5B7; border: 1px solid rgba(74, 25, 66, 0.10);`
      - Primary action: `background: #C2452D; color: #FFF8F0; border-radius: 9999px;`
      - Olive accent: `#6B7F3B` (fill/badge for PASS and active streaks)
      - Med-blue accent: `#1565C0` (chips and simulation indicators)
      - Hairline: `rgba(74, 25, 66, 0.10)`
    - Micro-interactions: hover/press ~150ms ease-out, press scale 0.97.
- **Verification**:
  - Verify DOM in live browser contains `@font-face` definitions for all 3 families with base64 data URIs.

### Task 1.3: Topbar Shell & Official Brand Lockup (`app.py`)
- **Actions**:
  - Rewrite `render_topbar()` in `app.py`:
    - Brand Lockup (left):
      - 28×28 inline SVG Logo Variant A (terracotta tile `#C2452D`, sun-white serif "A", olive `#6B7F3B` dot).
      - Wordmark: `AI Prep Coach` in `DM Serif Display`, 22px, `#2C1810`.
    - Navigation Pills (center):
      - `Home`, `Practice Arena`, `Mock Interview`, `Dashboard`.
      - Active item: terracotta pill / underline indicator matching `DESIGN.md`.
    - Live Store Chips & Actions (right):
      - Active Streak Chip: live read from `store.current_streak()` (`{N}d` in olive).
      - Due Chip: live read from `store.due_problems()` (`{N} due` in terracotta/amber).
      - Logout text button: styled minimally (`color: #735A50; font-size: 13px; cursor: pointer;`), triggers session logout.
    - Dropped: Version chip and "Offline · Code-Judged" tag permanently removed.
- **Verification**:
  - Inspect topbar in live Chrome: Logo Variant A renders cleanly at 28×28, brand reads "AI Prep Coach", version chip absent.

### Task 1.4: Login Gate & Confirmation Screen (`app.py`)
- **Actions**:
  - Implement authentication gate at entry of `app.py`:
    - Check `st.session_state.get("authenticated_user")`.
    - Handle URL query parameters via `st.query_params`:
      - `?verify=<token>`: Calls `auth_store.verify_email_token(token)` $\rightarrow$ sets success banner "Email confirmed — you can log in now."
      - `?reset=<token>`: Renders Set New Password form.
    - If unauthenticated, render `render_login()` and halt further page rendering (`st.stop()`).
  - Implement `render_login()`:
    - Centered 24px white card with 1px warm hairline on `#FFF8F0` canvas matching `mockups/terracotta/login.html`.
    - 44×44 inline SVG Logo Variant A.
    - Serif headline `AI Prep Coach`, subline "Welcome back — your practice, judged by code."
    - Mode toggle: "Sign In", "Create Account", "Forgot Password".
    - Sign In form: Email & Password, Terracotta pill submit button.
      - If user is `pending`: shows honest alert "Confirm your email to activate your account" + "Resend confirmation email" button.
      - If credentials invalid: shows "Invalid email or password."
    - Create Account form: Email & Password.
      - On submit: calls `auth_store.create_pending_profile()`, triggers `auth_store.send_smtp_email()`.
      - If send succeeds: shows "Confirmation email sent! Please check your inbox and click the link to activate."
      - If send fails: honest failure alert "Account created, but confirmation email could not be sent. Please click Resend or check your SMTP settings."
    - Forgot Password form: Email field $\rightarrow$ sends reset link with 1-hour expiry.
- **Verification**:
  - Live browser test: Unauthenticated view displays Terracotta login card matching `login.html`.
  - Logging in with valid active account admits user to Home.
  - Logging out returns user to login card.

---

## 3. Skill Bindings

- `developing-with-streamlit`: Governs Streamlit config theming, session-state authentication guarding, and keyed component styling.
- `/ui-styling`: Guides translation of Terracotta design tokens into Streamlit CSS rules, button micro-interactions, and 24px bento containers.
- `/design-system`: Governs token hierarchy consistency across `.streamlit/config.toml`, `@font-face` base64 embedding, and custom UI components.
- `/brand`: Enforces exact brand application: official wordmark "AI Prep Coach", Logo Variant A (28×28 and 44×44 inline SVGs), and color discipline.


