---
phase: 1
plan: 1
wave: 1
depends_on: []
files_modified:
  - mockups/style.css
  - mockups/tokens.html
  - mockups/home.html
autonomous: true
gap_closure: false

must_haves:
  truths:
    - "Direction A design tokens are completely defined in style.css and documented in tokens.html"
    - "Paper canvas (#FBFAF7), ink typography (#171712), hairline borders (#E7E1D6), and six-part area tints meet WCAG contrast requirements"
    - "Home screen mockup displays authentic app data: active streak 1 day, 0 due, 12 problems library, Binary Search PASS 178ms"
    - "Zero application code files (app.py, config.toml, coach/*, data/problems/*, tests/*) are modified"
  artifacts:
    - mockups/style.css
    - mockups/tokens.html
    - mockups/home.html
---

# Plan 1.1: Design Tokens Foundation & Home Screen Mockup

<objective>
Establish the Direction A (Brilliant-style) design token foundation in `mockups/style.css` and `mockups/tokens.html`, and refine the Home screen static mockup in `mockups/home.html` using authentic content and exclusive Lucide SVG iconography.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/DECISIONS.md
- mockups/style.css
- mockups/tokens.html
- mockups/home.html
- agent-resources/lucide/icons/
</context>

<tasks>

<task type="auto">
  <name>Finalize Direction A Design Tokens and Token Spec Sheet</name>
  <files>
    mockups/style.css
    mockups/tokens.html
  </files>
  <action>
    Audit and align `mockups/style.css` and `mockups/tokens.html` to strictly implement the Direction A design system specifications:
    1. Base Canvas & Ink:
       - App canvas paper: `#FBFAF7` (`--paper`)
       - Surface card: `#FFFFFF` (`--surface`), 24px corner radius (`--radius-card: 24px`), soft elevation shadow (`--shadow-soft: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06)`)
       - Hairline border: 1px solid `#E7E1D6` (`--hairline`)
       - Deep ink text: `#171712` (17.23:1 AAA contrast on paper)
       - Muted warm grey text: `#66635A` (5.75:1 AA contrast on paper)
    2. Primary Action CTA:
       - Saturated emerald green `#15803D` with white `#FFFFFF` text (5.02:1 AA contrast), pill radius `999px`
    3. Six-Part Area Tint Matrix:
       - Mint & Green (Streak / PASS): Wash `#DFF3E4`, text `#167B48` (4.56:1), fill `#1F9D63`
       - Butter & Amber (Library / TIMEOUT): Wash `#FFF0C4`, text `#9A3412` (6.44:1), fill `#B45309`
       - Sky & Blue (Due / Analytics): Wash `#DCEBFF`, text `#1D5EC2` (5.06:1), fill `#2273E6`
       - Lilac & Violet (Practice Area): Wash `#E8E2FF`, text `#5932EA` (5.46:1), fill `#6C4CF1`
       - Peach & Coral (Mock Interview / Timer): Wash `#FFE8D1`, text `#B93815` (4.87:1), fill `#E4572E`
       - Rose & Red (FAIL / Errors): Wash `#FFE0E0`, text `#C5221F` (4.69:1), fill `#D92D20`
    4. Code Inset Anchor:
       - Surface `#14161A`, text `#F2F2ED`, syntax highlights (`#7DD3FC`, `#86EFAC`, `#FDE047`, `#94A3B8`)
    5. Typography:
       - Headings: Fraunces serif
       - UI & Body: Inter sans-serif
       - Code & tabular metrics: JetBrains Mono
    6. Ensure `mockups/tokens.html` showcases swatches, contrast badges, typography scale, and code inset using exact Lucide SVG icons from `agent-resources/lucide/icons`.

    AVOID: Modifying any application files (app.py, coach/*, data/problems/*) because Phase 1 has a strict app code quarantine.
    USE: Exact hex tokens specified in Direction A design system.
  </action>
  <verify>
    python -c "style=open('mockups/style.css', encoding='utf-8').read(); tokens=open('mockups/tokens.html', encoding='utf-8').read(); assert all(k in style for k in ['#FBFAF7','#171712','#66635A','#E7E1D6','#15803D','#DFF3E4','#FFF0C4','#DCEBFF','#E8E2FF','#FFE8D1','#FFE0E0','#14161A']); assert 'Direction A' in tokens; print('PASS: Tokens and style.css validated')"
  </verify>
  <done>
    `mockups/style.css` contains all Direction A CSS variables and utility classes; `mockups/tokens.html` visually documents the entire token matrix with verified contrast ratios.
  </done>
</task>

<task type="auto">
  <name>Refine Home Screen Mockup with Authentic Grounded Content</name>
  <files>
    mockups/home.html
  </files>
  <action>
    Refine `mockups/home.html` to present the polished Direction A home dashboard view with authentic application content:
    1. Shell & Header:
       - Sidebar navigation with brand title "AI Coding Prep Coach", tagline "Zero Cost · Code-Judged · Offline-Ready", and Lucide SVGs (home, code-2, clock, bar-chart-2).
       - Sidebar stats displaying singular "1 day" active streak and "0 problems" due for review.
       - Page header with Fraunces title "Today's Practice", subtitle, and primary emerald green pill CTA "Start Practice".
    2. Three Saturated Tint Cards:
       - Card 1 (Mint `#DFF3E4`): Active Streak "1 day", caption "Practice tomorrow to reach a 2-day streak."
       - Card 2 (Sky `#DCEBFF`): Due for Review "0 problems" (or "0 due"), badge "On Schedule", caption "All scheduled reviews are completely caught up."
       - Card 3 (Butter `#FFF0C4`): Total Problems "12 problems", badge "Library", caption "Curated across DSA, Strings, and Practical Python."
    3. Due for Review Queue Section:
       - Sky tint wash card displaying clear status ("Queue Status: Clear") with ink copy explaining zero decay and inviting user to explore new problems.
    4. Recent Practice Attempts:
       - White surface card showing the latest attempt: Binary Search with mint PASS badge, runtime "178 ms", date "2026-11-04", 0 Hints, and secondary "Review" button.
    5. Iconography:
       - Verify all inline SVGs are drawn strictly from `agent-resources/lucide/icons` (no emoji icons, no font icons).

    AVOID: Invented metrics or plural "1 days".
    USE: Grounded data (1 day streak, 0 due, 12 problems, Binary Search PASS 178ms) with Fraunces headers and Inter body.
  </action>
  <verify>
    python -c "home=open('mockups/home.html', encoding='utf-8').read(); assert '1 day' in home; assert '0 problems' in home or '0 due' in home; assert '12 problems' in home; assert 'Binary Search' in home and '178 ms' in home; print('PASS: Home mockup authentic data verified')"
  </verify>
  <done>
    `mockups/home.html` accurately renders Direction A visual styling with all authentic data metrics verified.
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
- [ ] `mockups/style.css` contains all Direction A token values
- [ ] `mockups/tokens.html` accurately displays swatches and contrast proofs
- [ ] `mockups/home.html` displays authentic metrics (1 day streak, 0 due, 12 problems, Binary Search PASS 178ms)
- [ ] No application code files (`app.py`, `coach/*`, etc.) were edited
</verification>

<success_criteria>
- [ ] All tasks verified passing
- [ ] Must-haves confirmed
- [ ] Zero app code modified
</success_criteria>
