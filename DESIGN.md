---
name: "AI Coding Prep Coach"
description: "Terracotta Editorial Redesign (Bento Grid Tech Minimalist + Terracota Mediterrâneo)"
style: "Option 3 — Terracotta Editorial"
colors:
  canvas: "#FFF8F0"
  panel-quiet: "#E8D5B7"
  terracotta-primary: "#C2452D"
  olive-success: "#6B7F3B"
  blue-info: "#1565C0"
  clay-accent: "#D4956B"
  fig-deep: "#4A1942"
  seafoam-fresh: "#A8D8C8"
  ink-primary: "#2C1810"
  ink-muted: "#735A50"
  hairline-warm: "rgba(74, 25, 66, 0.10)"
  code-bg: "#1E1E1E"
  code-text: "#F8F8F2"
typography:
  displayFont: "DM Serif Display"
  bodyFont: "Plus Jakarta Sans"
  codeFont: "JetBrains Mono"
  metricNumeralStyle: "tabular-semibold"
surfaces:
  finish: "matte-only"
  border: "1px warm hairline"
  shadows: "none"
  cardRadius: "24px"
  buttonRadius: "9999px"
  motion: "hover/press only (~150ms ease-out, press scale 0.97)"
---

# Design System Specification — Terracotta Editorial

## 1. Governing System: Option 3 — Terracotta Editorial (Milestone 3)

> **Direction Statement:**  
> *"Terracota Mediterrâneo palette meets Bento Grid Tech Minimalist structure. Sun-white paper foundation, deep warm-ink typography with DM Serif Display headlines, tactile 24px matte bento tiles framed by 1px warm hairlines, terracotta primary pill actions, olive success and streak accents, Mediterranean blue info and simulation accents, and sandy beige explanatory strips. Strict frontend feasibility: zero gradients, zero glass, zero arch containers, zero entrance animation, and 100% authentic data truth."*

---

### Core Palette & Contrast Specification

| Token Name | Hex Code | Role / Usage | WCAG Contrast |
| :--- | :--- | :--- | :--- |
| `canvas` | `#FFF8F0` | Sun-white global page canvas | Base background |
| `panel-quiet` | `#E8D5B7` | Sandy beige quiet panel / tile (used sparingly for summary, format, and timer strips; never as page background) | 1.25:1 on canvas |
| `terracotta` | `#C2452D` | Primary action buttons, active nav underline/indicator, critical prompts | 5.24:1 on canvas (AA) |
| `olive` | `#6B7F3B` | Success state, PASS badges, active streak counter | 4.68:1 on canvas (AA) |
| `med-blue` | `#1565C0` | Info callouts, mock interview simulation mode, external links | 6.82:1 on canvas (AAA) |
| `clay` | `#D4956B` | Secondary warm accent, chart series, warm dividers | 2.14:1 on canvas |
| `deep-fig` | `#4A1942` | Deep accent (used sparingly for high-contrast emphasis, hairline alpha source) | 12.18:1 on canvas (AAA) |
| `sea-foam` | `#A8D8C8` | Fresh zone accent (used sparingly in multi-category chart palettes) | 1.52:1 on canvas |
| `ink-primary` | `#2C1810` | Display headlines, body text, card headers | 14.85:1 on canvas (AAA) |
| `ink-muted` | `#735A50` | Metadata, difficulty indicators, sublines | 5.38:1 on canvas (AA) |
| `hairline` | `rgba(74, 25, 66, 0.10)` | 1px warm hairline card and panel boundary | Subtle structure |
| `code-bg` | `#1E1E1E` | Code editor dark anchor inset | Dark anchor |
| `code-text` | `#F8F8F2` | Code text inside editor inset | 15.3:1 on code-bg (AAA) |

---

### Functional Color Jobs (Binding)

- **Terracotta (`#C2452D`)**: Primary action pill buttons ("Start Daily Practice", "Run Code", "Submit Solution", "Begin Mock Interview", "Download Assessment Report"), active nav pill indicator/underline.
- **Olive (`#6B7F3B`)**: Success confirmations, PASS badges, streak counter tiles, mastered topic bars.
- **Mediterranean Blue (`#1565C0`)**: Info chips, mock interview simulation banners, candidate switchers, technical links.
- **Sandy Beige (`#E8D5B7`)**: Explanatory panels, mock interview format facts strip, session timer band, scorecard summary metrics container.
- **Clay / Deep Fig / Sea Foam**: Supporting accents and multi-topic chart differentiation only; never competing primaries.

#### Verdict Matrix
- **PASS**: Olive `#6B7F3B` fill or border with dark olive text (`#3B471F`).
- **FAIL**: Terracotta `#C2452D` fill or border with deep rust text (`#7A1E0D`).
- **TIMEOUT / NOT ATTEMPTED**: Neutral warm gray (`#8A7D75`).

---

### Typography Hierarchy

1. **Display Headlines & Wordmark**:
   - Family: `DM Serif Display`, serif.
   - Usage: App wordmark ("Coach"), page hero titles ("Today's Practice", "Coding Interview Simulation", "Performance Scorecard"), prominent section titles.
   - Styling: Normal style, generous line height (1.2), high contrast, warm editorial feel.
2. **Body & General UI**:
   - Family: Humanist Sans (`Plus Jakarta Sans` or `Source Sans 3`).
   - Usage: Navigation links, statement markdown, problem descriptions, instructions, button labels.
   - Styling: 400 (regular), 500 (medium), 600 (semibold). Letter-spacing: -0.01em.
3. **Code, Editor Strip & Timer**:
   - Family: `JetBrains Mono`, monospace.
   - Usage: Code blocks, starter code, test cases, editor sandbox strip, mock countdown timer.
   - Styling: 500 (medium).
4. **Metric Numerals (DECISION-007 Binding)**:
   - Family: Tabular semibold Inter-style humanist sans (`Plus Jakarta Sans` with `font-feature-settings: "tnum"`).
   - Monospace is **STRICTLY FORBIDDEN** for general metric numbers (e.g. "1 Day", "1 Due", "90%"). Numbers remain clean, proportional, and tabular.

---

### Surfaces, Geometry & Micro-Interactions

- **Matte Surfaces Only**: Flat color fills (`#FFFFFF` on `#FFF8F0` canvas, or `#E8D5B7` for quiet panels). No gloss, no gradients, no texture simulations.
- **Borders Over Shadows**: Elevation is created via 1px warm hairlines (`rgba(74, 25, 66, 0.10)` or `#E8D5B7`). Heavy drop shadows and blur effects are eliminated.
- **Card Radius**: `24px` corner radius for all bento cards, problem cards, and editor containers.
- **Button Radius**: `9999px` full pill radius for interactive action buttons.
- **Allowed Micro-Interactions**: Hover and press states only (`transition: all 150ms ease-out; transform: translateY(-1px)` on hover, `transform: scale(0.97)` on press).
- **Streamlit Invariant**: No entrance animations, no sliding carousels, no cinematic fades (Streamlit rerun cycle would cause uncontrolled replay).

---

### Prohibited Tropes (Anti-Slop Ban List)

The following AI-generator tropes are explicitly stripped and banned:
1. **Chip Soup**: Overflowing nested badge pills. In problem lists, queues, and tables, at most ONE status pill is allowed per row. Difficulty and topic are styled as colored text.
2. **Generator Fiction**: Placeholder percentages, sample rows, "320+ solved" invented counts. All numbers derive strictly from real store data (2 attempts, 1 solved) and the real 12 problem bank.
3. **Gradients, Glass & Glow**: No linear-gradient card backgrounds, no `backdrop-filter: blur()`, no glowing neon borders.
4. **Serif Body Copy**: DM Serif Display is strictly reserved for display headlines. Body copy must use clean Humanist Sans.
5. **Arch Containers & Textures**: No faux stone, no architectural arches, no plaster textures. Clean geometric bento boxes only.
6. **Independent Pane Scrolling**: Streamlit cannot support independent dual-pane scroll without fragile hacks. The Practice Arena uses clean full-page scroll.

---

## 2. Superseded System: Direction A (Milestone 1 — 2026-11-05)

> **Status:** `SUPERSEDED` for Milestone 3 by Option 3 Terracotta Editorial. Preserved for implementation reference.

- **Canvas:** Paper `#FBFAF7`
- **Primary CTA:** Green `#15803D`
- **Display Font:** Fraunces
- **Body Font:** Inter
- **Accent System:** 6-part pastel wash tints (Mint, Butter, Sky, Lilac, Peach, Rose).

---

## 3. Superseded System: OLED Dark Mode (R2 — Historical)

> **Status:** `ARCHIVED`. Rejected 2026-11-05.
- Background `#0F172A`, foreground `#F8FAFC`.
