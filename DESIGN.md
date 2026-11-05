---
name: "AI Coding Prep Coach"
description: "Dark coding-practice workbench and analytics dashboard"
style: "Dark Mode (OLED)"
colors:
  primary: "#1E293B"
  on-primary: "#FFFFFF"
  secondary: "#334155"
  on-secondary: "#FFFFFF"
  accent: "#22C55E"
  on-accent: "#0F172A"
  background: "#0F172A"
  foreground: "#F8FAFC"
  card: "#1B2336"
  card-foreground: "#F8FAFC"
  muted: "#272F42"
  muted-foreground: "#94A3B8"
  border: "#475569"
  destructive: "#EF4444"
  on-destructive: "#000000"
  warning: "#F59E0B"
  info: "#38BDF8"
  info-bg: "#1E293B"
  violet: "#A855F7"
typography:
  headingFont: "JetBrains Mono"
  bodyFont: "IBM Plex Sans"
  codeFont: "JetBrains Mono"
rounded:
  base: "8px"
  button: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
---

# Design System Specification — AI Coding Prep Coach

## 1. Overview & Direction

> **Direction Statement:**
> *"Quiet panels, aligned figures, colour spent on data and on pass/fail state — nothing decorative competes with the code."*

This design system establishes a high-contrast, distraction-free OLED dark workbench for software engineers practicing algorithmic problem solving under timed constraints. Every pixel is purposeful; decorative flourishes, unstyled voids, and generic stream-of-consciousness layouts are forbidden.

---

## 2. Colors & Token Mapping

All colors are strictly sourced from the UI-UX Pro Max `Dark Mode (OLED)` generation and mapped to Streamlit 1.66.1 theme tokens and UI constructs.

| Token Name | Hex Code | Streamlit 1.66.1 Mapping | Usage / Role | Contrast Ratio (WCAG) |
|---|---|---|---|---|
| `background` | `#0F172A` | `theme.backgroundColor` | Global canvas root background | — |
| `foreground` | `#F8FAFC` | `theme.textColor` | Primary body copy & prominent headers | 17.06:1 on `#0F172A` (AAA) |
| `secondary` | `#1E293B` | `theme.secondaryBackgroundColor` | Sidebar background, secondary container panels | — |
| `card` | `#1B2336` | `st.container(border=True)` | Surface background for cards, editor surround | — |
| `border` | `#475569` | `theme.borderColor`, `theme.dataframeBorderColor` | Card outlines, dividers, table gridlines | 3.2:1 against bg |
| `muted-foreground` | `#94A3B8` | `theme.grayTextColor` | Secondary labels, difficulty tags, captions | 6.96:1 on `#0F172A` (AAA) |
| `accent` / `primary` | `#22C55E` | `theme.primaryColor`, `theme.greenColor` | CTA buttons, Run Code, PASS verdicts | 7.83:1 on `#0F172A` (AAA) |
| `destructive` | `#EF4444` | `theme.redColor`, `theme.redTextColor` | FAIL verdicts, syntax/runtime errors | 4.74:1 on `#0F172A` (AA) |
| `destructive-bg` | `#7F1D1D` | `theme.redBackgroundColor` | Error banner/card tint | — |
| `warning` | `#F59E0B` | `theme.yellowColor`, `theme.yellowTextColor` | TIMEOUT verdicts, review notices | 8.31:1 on `#0F172A` (AAA) |
| `warning-bg` | `#78350F` | `theme.yellowBackgroundColor` | Warning banner/card tint | — |
| `info-text` | `#38BDF8` | `theme.blueTextColor`, `theme.blueColor` | Info callouts, streak badges, hints | 6.83:1 on `#1E293B` (AAA) |
| `info-bg` | `#1E293B` | `theme.blueBackgroundColor` | Info callout card background | 8.23:1 vs text |
| `code-bg` | `#1B2336` | `theme.codeBackgroundColor` | Code block background, Ace editor bg | — |
| `code-text` | `#F8FAFC` | `theme.codeTextColor` | Monospace code text | 17.06:1 |
| `chart-seq-1` | `#22C55E` | `theme.chartCategoricalColors[0]` | Completed / Passing tests | — |
| `chart-seq-2` | `#38BDF8` | `theme.chartCategoricalColors[1]` | Active / In-progress topic volume | — |
| `chart-seq-3` | `#F59E0B` | `theme.chartCategoricalColors[2]` | Due for review | — |
| `chart-seq-4` | `#EF4444` | `theme.chartCategoricalColors[3]` | Failed attempts | — |
| `chart-seq-5` | `#A855F7` | `theme.chartCategoricalColors[4]` | Supplementary category volume | — |

> **Contrast Verification Note:**
> - Muted text (`#94A3B8`) on root background (`#0F172A`) delivers **6.96:1** (exceeds the 4.5:1 requirement).
> - New Info alert pair (`#38BDF8` on `#1E293B`) delivers **6.83:1** (eliminates the owner-reported unreadable dark blue box).

---

## 3. Typography

- **Heading Font:** `JetBrains Mono`, monospace (precise, technical, hacker discipline)
- **Body Font:** `IBM Plex Sans`, sans-serif (clean, humanist, high legibility)
- **Code Font:** `JetBrains Mono`, monospace

### Heading Scale
- **H1 (Page Title):** 28px (`1.75rem`), weight 700. Used once per screen.
- **H2 (Section Header):** 20px (`1.25rem`), weight 600. Used for major functional regions.
- **H3 (Card / Metric Title):** 16px (`1.0rem`), weight 600. Used inside containers and table headers.
- **Body Text:** 16px (`1.0rem`), weight 400.
- **Microcopy / Meta:** 13px (`0.8125rem`), weight 400, color `#94A3B8`.

---

## 4. Layout & Spacing Scale

### Spacing Scale
- `xs` (4px): Icon-to-text spacing, inline tag padding.
- `sm` (8px): Gaps between badge items, button internal vertical padding.
- `md` (16px): Standard container internal padding, form input spacing.
- `lg` (24px): Card margin, gutter between sidebar and main column.
- `xl` (32px): Separation between major screen sections.

### Content Grouping Rule
Every screen must be explicitly partitioned into cards using `st.container(border=True)`:
1. **No full-canvas text dumping:** Uncontained markdown paragraphs on the root background are prohibited.
2. **Viewport height discipline (Home):** Home screen consists of:
   - Header summary banner card.
   - Row of 3 bordered metric cards (Streak, Due Today, Total Library).
   - "Due for Review" dedicated card with empty state styled in token info colors.
   - Recent attempts table card.
   This cleanly fills the desktop viewport without a bottom void.
3. **Practice Workbench:**
   - Left column (ratio 4): Problem statement, constraints, signature block, visible test cases.
   - Right column (ratio 7): Full-height Ace editor (min 420px), Run Button, structured verdict / failure cards.

---

## 5. Elevation & Shapes

- **Radius:** All cards, buttons, inputs, and modals use a uniform **8px** radius (`baseRadius = 8`, `buttonRadius = 8`).
- **Borders:** Border width is 1px solid `#475569`.
- **Shadows:** Minimal elevation (`box-shadow: 0 1px 3px rgba(0,0,0,0.4)`). Flat dark panels with border delineation take precedence over noisy dropped shadows.

---

## 6. Components & State Representation

- **Verdict Badges:**
  - `PASS`: Background `#14532D`, Border `#22C55E`, Text `#22C55E`.
  - `FAIL`: Background `#7F1D1D`, Border `#EF4444`, Text `#EF4444`.
  - `TIMEOUT`: Background `#78350F`, Border `#F59E0B`, Text `#F59E0B`.
- **Timer Fragment:**
  - Top-right monospace countdown (`JetBrains Mono`, 22px, tabular numbers).
  - Ticks live via `@st.fragment(run_every=1.0)` without full-page rerun.
- **Icons:**
  - Streamlit native Material Symbols only (`:material/timer:`, `:material/bolt:`, `:material/check_circle:`).
  - Zero raw emojis in UI headings, metrics, or sidebar labels.

---

## 7. Do's and Don'ts

### Do
- Group every related set of controls/metrics inside `st.container(border=True)`.
- Use the exact token hexes for Plotly charts, badge highlights, and text colors.
- Maintain $\ge 4.5:1$ contrast on every informational block.
- Keep the editor wide, tall (min 420px), and central.

### Don't
- ❌ Do NOT use default unstyled Streamlit metric widgets on root background.
- ❌ Do NOT use raw emojis as UI icons.
- ❌ Do NOT leave huge vertical empty spaces on the Home screen.
- ❌ Do NOT use the default Streamlit `#262730` unreadable blue alert box.

---

## Direction A — PROPOSED, awaiting owner approval

> **Status:** Proposed design language for Round 3 (Mockup approval gate). The R2 OLED Dark workbench specification above remains active for current app implementation until the owner formally approves Direction A.

### 1. Vision & Design Philosophy

- **Inspiration:** Colourful light learning app (Brilliant-style visual language).
- **Core Philosophy:** Paper-white foundation, deep ink typography, hairline warm borders, big soft-rounded cards (24px radius), fully pill-shaped buttons and badges (9999px), generous breathing room, and an authoritative six-part functional tint system where color acts as structure rather than arbitrary decoration.
- **Code Anchor:** Dark surfaces are contained strictly to the code editor inset (`#14161A`), framed by an area-tinted header strip within a crisp white container card.

### 2. Direction A Palette & Token Specifications

| Token Role | Hex Code | Purpose / Context | Contrast Ratio (WCAG) | Compliance |
|---|---|---|---|---|
| **App Canvas Paper** | `#FBFAF7` | Global canvas root background | — | Base |
| **Surface Card** | `#FFFFFF` | Elevated container cards, panels | 1.05:1 on paper | Base |
| **Deep Ink Text** | `#171712` | Primary headings, body copy, strong labels | 17.23:1 on paper | AAA |
| **Muted Warm Grey** | `#66635A` | Secondary text, difficulty captions, metadata | 5.75:1 on paper | AA ($\ge 4.5:1$) |
| **Hairline Border** | `#E7E1D6` | Card outlines, tab dividers, table separators | 1.25:1 on paper | Non-text |
| **Primary CTA Button** | `#15803D` | Primary action pills (Run Code, Submit Solution) | 5.02:1 with white text | AA ($\ge 4.5:1$) |
| **Code Inset Surface** | `#14161A` | Solution code editor surface | — | Base |
| **Code Foreground** | `#F2F2ED` | Monospace code text inside editor | 16.13:1 on `#14161A` | AAA |

### 3. Six-Part Structure Tint System

Each functional zone pairs an ultra-pale tint wash background with a saturated partner color for badges, active states, and alert text ($\ge 4.5:1$ contrast against the wash):

1. **Mint & Green (Streak / PASS / Mastery):**
   - Wash: `#DFF3E4`
   - Partner Text / Accent: `#167B48` (Contrast on Wash: **4.56:1**, AA)
   - Partner Fill: `#1F9D63` (Contrast with ink text: **5.19:1**, AA)
   - Usage: Active streak counter, passed test cases, 100% mastery bars, success badges.
2. **Butter & Amber (Library / TIMEOUT / In-Progress):**
   - Wash: `#FFF0C4`
   - Partner Text / Accent: `#9A3412` (Contrast on Wash: **6.44:1**, AAA)
   - Partner Fill: `#B45309` (Contrast with white text: **5.02:1**, AA)
   - Usage: Problem bank total stat card, execution timeout notices, partial progress.
3. **Sky & Blue (Due / Review Queue / Analytics):**
   - Wash: `#DCEBFF`
   - Partner Text / Accent: `#1D5EC2` (Contrast on Wash: **5.06:1**, AA)
   - Partner Fill: `#2273E6` (Contrast with white text: **4.50:1**, AA)
   - Usage: Spaced repetition due card ("0 Due for Review"), Dashboard summary cards.
4. **Lilac & Violet (Practice Arena):**
   - Wash: `#E8E2FF`
   - Partner Text / Accent: `#5932EA` (Contrast on Wash: **5.46:1**, AA)
   - Partner Fill: `#6C4CF1` (Contrast with white text: **5.33:1**, AA)
   - Usage: Practice area active navigation pill, editor header strip, topic badges.
5. **Peach & Coral (Mock Interview / Timer):**
   - Wash: `#FFE8D1`
   - Partner Text / Accent: `#B93815` (Contrast on Wash: **4.87:1**, AA)
   - Partner Fill: `#E4572E` (Contrast with ink text: **4.88:1**, AA)
   - Usage: Mock interview active tab, countdown timer capsule pill (`44:41`).
6. **Rose & Red (FAIL / Errors):**
   - Wash: `#FFE0E0`
   - Partner Text / Accent: `#C5221F` (Contrast on Wash: **4.69:1**, AA)
   - Partner Fill: `#D92D20` (Contrast with white text: **4.83:1**, AA)
   - Usage: Failed test case cards, syntax and runtime error containers.

### 4. Typography Hierarchy

- **Display & Headings:** `Fraunces`, optical size 144, serif with warmth, editorial confidence, and distinctive curves.
  - H1 (Screen Titles): 36px (`2.25rem`), weight 700.
  - H2 (Section Titles): 22px (`1.375rem`), weight 700.
  - H3 / Card Titles: 17px (`1.0625rem`), weight 600.
  - Metric Values: 38px (`2.375rem`), weight 700, tabular figures. Monospace metric numbers are strictly prohibited.
- **Body & Controls:** `Inter`, humanist sans-serif, high legibility.
  - Body Copy: 15px (`0.9375rem`), regular 400 or medium 500.
  - Microcopy / Metadata: 13px (`0.8125rem`), regular 400.
  - Buttons & Navigation: 14px (`0.875rem`), semibold 600.
- **Monospace (Strictly Restricted):** `JetBrains Mono`
  - Allowed ONLY in: (a) Code editor, (b) Inline code literals, (c) Timed countdown ticker (`44:41`).
  - Prohibited in: Metric displays, standard buttons, section headers, card titles.

### 5. Geometry & Elevation

- **Card Radius:** `24px` (`var(--radius-card)`).
- **Control & Badge Radius:** `9999px` (`var(--radius-pill)`).
- **Inner Tiles & Inputs:** `12px` (`var(--radius-tile)`).
- **Hairline Borders:** `1px solid #E7E1D6`.
- **Soft Shadows:** `0 4px 16px rgba(23, 23, 18, 0.04), 0 1px 2px rgba(23, 23, 18, 0.06)`. Flat, elegant, never muddy.

### 6. Real-Content Rules

All mockups and subsequent implementations strictly reflect live production state:
- **Active Streak:** `1 day` (singular, never "1 days").
- **Due for Review:** `0` (clean empty state styled in Sky/Blue wash).
- **Problem Library:** `12` total problems across 4 topics.
- **Featured / Test Problem:** `Longest Substring Without Repeating Characters` (strings, Medium).
- **Recent Attempt:** `2026-11-04 · Binary Search · PASS · 178 ms · Hints: 0`.
- **Mock Timer:** `44:41` countdown.

