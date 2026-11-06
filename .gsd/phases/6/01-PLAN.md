---
phase: 6
plan: "01"
wave: 1
depends_on: ["00"]
---

# Plan 6.1: Design Tokens Specification & Base Terracotta Stylesheet

## Objective
Author the definitive Terracotta Editorial design token specification in `DESIGN.md` and implement the foundational CSS stylesheet (`mockups/terracotta/style.css`) and visual token specimen page (`mockups/terracotta/tokens.html`). Establish the "Terracota Mediterrâneo" color architecture, DM Serif Display and humanist sans typography, 24px matte bento surfaces, 1px warm hairlines, and hover/press micro-interactions.

## Context
- `.gsd/SPEC.md`
- `.gsd/phases/6/DISCUSS.md`
- `DESIGN.md`
- `mockups/style.css` (Phase 1 reference)
- `mockups/tokens.html` (Phase 1 reference)

---

## Tasks

<task type="auto">
  <name>Task 1.1: Author Terracotta Editorial Token Specification in DESIGN.md</name>
  <files>DESIGN.md</files>
  <action>
    <!-- Skill binding: /design-system + /design + /brand -->
    1. Define the complete Terracotta Editorial design token sheet in `DESIGN.md`:
       - **Canvas / Paper**: Sun-white `#FFF8F0`
       - **Quiet Panel / Tile**: Sandy beige `#E8D5B7` (sparingly for summary/format panels, never as page background)
       - **Primary Action / Terracotta**: `#C2452D` (primary CTAs, active nav underline)
       - **Success / Streak / PASS Zone**: Olive `#6B7F3B` (PASS badges, streak counters)
       - **Info / Mock / Links Zone**: Mediterranean blue `#1565C0` (mock interview badges, links)
       - **Secondary Warm Accent**: Clay `#D4956B`
       - **Deep Accent**: Deep fig `#4A1942` (sparingly)
       - **Fresh Zone Accent**: Sea foam `#A8D8C8` (sparingly)
       - **Verdict Colors**: PASS olive `#6B7F3B`, FAIL terracotta-red `#C2452D`, TIMEOUT neutral warm gray.
    2. Specify the Typography hierarchy:
       - Headlines & Wordmark: `DM Serif Display`, serif, high contrast, warm editorial feel.
       - Body & UI: Humanist Sans (`Plus Jakarta Sans` or `Source Sans 3`), readable, balanced tracking.
       - Code, Editor Strip, Mock Timer: `JetBrains Mono` only.
       - Metric Numerals: Tabular semibold Inter-style per DECISION-007 (never monospace numerals).
    3. Specify Surfaces, Geometry & Motion:
       - Matte surfaces only, flat color fills.
       - Borders over shadows: 1px warm hairline (`rgba(74, 25, 66, 0.08)` / warm clay border). No drop shadows.
       - 24px corner radius for bento cards, 9999px for pill buttons.
       - Motion: hover/press states only (~150ms ease-out, press scale 0.97).
       - Explicitly state banned tropes: golden-hour gradients, plaster/stone textures, arch containers, entrance animations, glass, glow, shimmer, independent pane scrolling.
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('DESIGN.md').read(); assert '#C2452D' in content and '#FFF8F0' in content and '#6B7F3B' in content; print('DESIGN.md tokens valid')"</verify>
  <done>`DESIGN.md` contains the complete approved Terracotta Editorial token architecture and design rules.</done>
</task>

<task type="auto">
  <name>Task 1.2: Implement Base Stylesheet & Visual Token Specimen Page</name>
  <files>mockups/terracotta/style.css, mockups/terracotta/tokens.html</files>
  <action>
    <!-- Skill binding: /ui-styling + /agency-frontend-developer -->
    1. Create `mockups/terracotta/style.css`:
       - Define CSS variables for all Terracotta tokens (`--color-canvas: #FFF8F0;`, `--color-panel-quiet: #E8D5B7;`, `--color-terracotta: #C2452D;`, `--color-olive: #6B7F3B;`, `--color-blue: #1565C0;`, `--color-clay: #D4956B;`, `--color-fig: #4A1942;`, `--color-seafoam: #A8D8C8;`, etc.).
       - Import Google Fonts for `DM Serif Display`, `Plus Jakarta Sans`, and `JetBrains Mono`.
       - Implement base layout styles, 24px rounded card styles, 1px hairline border styles, and hover/press button micro-interactions.
       - Implement badge and chip styles: de-slopped status pills, verdict pills (PASS olive, FAIL terracotta, TIMEOUT neutral).
    2. Create `mockups/terracotta/tokens.html`:
       - Interactive/visual specimen page displaying all color swatches with hex codes, typography specimens (DM Serif Display vs Humanist Sans vs JetBrains Mono), card containers, button variants (terracotta primary pill, outline Back, subtle ghost), and verdict chips.
  </action>
  <verify>.venv\Scripts\python.exe -c "import os; assert os.path.isfile('mockups/terracotta/style.css') and os.path.isfile('mockups/terracotta/tokens.html'); print('Token assets exist')"</verify>
  <done>`mockups/terracotta/style.css` and `mockups/terracotta/tokens.html` created and validated.</done>
</task>

---

## Must-Haves
After all tasks complete, verify:
- [ ] `DESIGN.md` contains all approved hexes, typography rules, surface constraints, and banned trope list.
- [ ] `mockups/terracotta/style.css` correctly declares all CSS custom properties and component rules.
- [ ] `mockups/terracotta/tokens.html` renders valid HTML visual specimens.

## Success Criteria
- [ ] Tokens specified without gradients, glass, glow, or arch containers.
- [ ] Color jobs unambiguous: olive = success/PASS/streak, terracotta = primary/fail, blue = info/mock.

