---
phase: 2
plan: 1
wave: 1
depends_on: [0]
---

# Plan 2.1: Base Theme Configuration, Offline @font-face & Computed-Font Proof

## Objective
Establish the foundational styling layer in Streamlit by applying frozen Direction A design tokens to `.streamlit/config.toml`, embedding offline `@font-face` definitions for Fraunces, Inter, and JetBrains Mono directly from `assets/fonts/`, and verifying with an automated Chrome CDP test that the rendered page computes the genuine font families.

## Context
- DESIGN.md
- assets/fonts/
- .streamlit/config.toml
- app.py

## Tasks

<task type="auto">
  <name>Configure Base Theme Tokens in config.toml</name>
  <files>.streamlit/config.toml, DESIGN.md</files>
  <action>
    1. Update .streamlit/config.toml [theme] section using frozen Direction A tokens:
       - primaryColor = "#15803D" (CTA green)
       - backgroundColor = "#FBFAF7" (Paper)
       - secondaryBackgroundColor = "#FFFFFF" (Surface)
       - textColor = "#171712" (Ink)
       - font = "sans serif" (Streamlit config base)
    2. Confirm DESIGN.md has Direction A as governing section and R2 OLED marked SUPERSEDED.
    3. Ensure no unmapped or generic fallback colors exist in config.toml.
  </action>
  <verify>Get-Content .streamlit/config.toml | Select-String "#FBFAF7", "#15803D", "#FFFFFF", "#171712"</verify>
  <done>.streamlit/config.toml reflects Direction A base tokens exactly.</done>
</task>

<task type="auto">
  <name>Self-Hosted @font-face Injection & Computed-Font Verification</name>
  <files>app.py, scratch/verify_fonts_cdp.js</files>
  <action>
    1. Read the 12 verified .woff2 files in assets/fonts/ and encode them into base64 data URIs within a scoped @font-face CSS stylesheet injected via st.html() at the top of app.py.
    2. Define font families:
       - 'Fraunces': weights 500, 600, 700, 800
       - 'Inter': weights 400, 500, 600, 700
       - 'JetBrains Mono': weights 400, 500, 600, 700
    3. Add named global exceptions in CSS budget for typography:
       - h1, h2, h3, h4, .stTitle, .stSubheader { font-family: 'Fraunces', serif !important; }
       - html, body, [class*="css"], .stMarkdown, p, span, label { font-family: 'Inter', sans-serif !important; }
       - code, pre, .stCode { font-family: 'JetBrains Mono', monospace !important; }
       - button[kind="primary"], .stButton > button { font-family: 'Inter', sans-serif !important; white-space: nowrap !important; padding: 10px 24px !important; border-radius: 999px !important; }
    4. Implement scratch/verify_fonts_cdp.js to connect to the live Streamlit app via Chrome DevTools Protocol and extract window.getComputedStyle(el).fontFamily for:
       - A heading element (assert contains "Fraunces")
       - A body text paragraph (assert contains "Inter")
       - A metric numeral element (assert contains owner's chosen font)
       - A code block or editor element (assert contains "JetBrains Mono")
    5. Run the CDP proof script and log the four actual computed family names.
  </action>
  <verify>node scratch/verify_fonts_cdp.js</verify>
  <done>All four computed font families verified as genuine offline families (Fraunces, Inter, JetBrains Mono) with zero runtime Google Fonts network requests.</done>
</task>

## Success Criteria
- [ ] .streamlit/config.toml matches Direction A tokens
- [ ] @font-face correctly serves assets/fonts/ offline via base64 data URIs
- [ ] Computed-font proof script verifies real font families rendered in Chrome
- [ ] Action button global nowrap and 999px radius rule active
