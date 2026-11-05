---
phase: 1
plan: 2
wave: 2
depends_on: ["01"]
files_modified:
  - mockups/practice.html
  - mockups/mock.html
autonomous: true
gap_closure: false

must_haves:
  truths:
    - "Practice mockup displays genuine starter signature def lengthOfLongestSubstring(s: str) -> int:"
    - "Practice mockup contains dark code inset (#14161A), primary green pill CTA (#15803D), and Rose-tinted test verdict panel (#FFE0E0 / #C5221F)"
    - "Mock interview mockup displays live countdown timer state at 44:41 in Peach-tint capsule (#FFE8D1 / #B93815)"
    - "Mock interview scorecard includes Question 1 Binary Search PASS (178ms)"
    - "Zero application code files (app.py, config.toml, coach/*, data/problems/*, tests/*) are modified"
  artifacts:
    - mockups/practice.html
    - mockups/mock.html
---

# Plan 1.2: Core Workspace Mockups (Practice Arena & Mock Interview)

<objective>
Refine the core interactive workspace static HTML mockups (`mockups/practice.html` and `mockups/mock.html`) to strictly implement Direction A aesthetics, authentic problem signatures, the 44:41 live countdown timer, and genuine evaluation scorecards.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/DECISIONS.md
- mockups/style.css
- mockups/practice.html
- mockups/mock.html
- agent-resources/lucide/icons/
</context>

<tasks>

<task type="auto">
  <name>Refine Practice Arena Mockup with Authentic Signature and Sandbox Panel</name>
  <files>
    mockups/practice.html
  </files>
  <action>
    Refine `mockups/practice.html` with Direction A styling and authentic coding-arena data:
    1. Filter & Metadata Bar:
       - DSA / Strings / Medium badges with "Problem 4 of 12 in Library".
    2. Problem Statement Column (Left 4 cols / 35%):
       - Title: "Longest Substring Without Repeating Characters" in Fraunces serif.
       - Problem description and constraints (O(n) time complexity).
       - Explicit function signature box displaying the EXACT starter signature:
         `def lengthOfLongestSubstring(s: str) -> int:`
       - Visible test case card #1 in Mint wash (`#DFF3E4`).
       - Progressive hint ladder in Butter wash (`#FFF0C4`, `#9A3412` text) showing Hint 1 of 3.
    3. Code Editor & Execution Column (Right 7 cols / 65%):
       - Editor card with Lilac/Violet header strip (`Solution Editor · Python 3.12`, Subprocess Sandbox 3.0s Timeout).
       - Deep ink code inset (`#14161A` background, `#F2F2ED` text, JetBrains Mono font, min-height 440px).
       - Code editor content displaying the Python sliding-window solution using the exact function signature `def lengthOfLongestSubstring(s: str) -> int:`.
       - Run action bar with saturated emerald green pill button (`#15803D`, white text, 9999px radius) for "Run & Submit".
    4. Execution Verdict Card:
       - Saturated Rose tint wash (`#FFE0E0` wash, `#C5221F` partner text, `#D92D20` fill).
       - Badge: `FAIL`.
       - Verdict text: `7 / 8 Hidden Tests Passed (142 ms)`.
       - Input / expected diff: `Input: s = "dvdf"`, `Expected: 3 (substring "vdf")`, `Got: 2`.
    5. Iconography:
       - Verify all inline SVGs are Lucide SVGs exclusively from `agent-resources/lucide/icons`.

    AVOID: Modifying any backend judge or application code.
    AVOID: Using the generic name `longest_substring`; use the genuine starter signature `def lengthOfLongestSubstring(s: str) -> int:`.
    USE: Direction A card radius (24px) and soft shadows.
  </action>
  <verify>
    python -c "prac=open('mockups/practice.html', encoding='utf-8').read(); assert 'def lengthOfLongestSubstring(s: str) -> int:' in prac; assert 'Longest Substring Without Repeating Characters' in prac; assert 'Run & Submit' in prac; assert '7 / 8 Hidden Tests Passed' in prac; print('PASS: Practice arena authentic signature and elements verified')"
  </verify>
  <done>
    `mockups/practice.html` renders authentic `lengthOfLongestSubstring` starter signature, dark editor inset, and Rose-tinted verdict card.
  </done>
</task>

<task type="auto">
  <name>Refine Mock Interview Arena with Live 44:41 Timer and Grounded Scorecard</name>
  <files>
    mockups/mock.html
  </files>
  <action>
    Refine `mockups/mock.html` with Direction A styling and grounded simulation elements:
    1. Header & Live Countdown Capsule:
       - Fraunces heading "Technical Interview Simulation", subtitle describing 45:00 countdown constraint.
       - Live timer capsule in Peach wash (`#FFE8D1` wash, `#B93815` coral partner text, hairline border `rgba(185, 56, 21, 0.25)`).
       - Timer display showing EXACT countdown state: `44:41` in JetBrains Mono with tabular numbers.
       - White capsule badge "Ticking Live" with coral text `#B93815`.
    2. Problem Navigation Strip:
       - Pill buttons for active Problem 1 and Problem 2.
    3. Mock Interview Scorecard Card:
       - White surface card with 24px radius and soft shadow.
       - Mint badge "Round Complete", Fraunces title "Mock Interview Scorecard".
       - Overall outcome: "2 / 2 Problems Solved".
       - Question 1 Summary Card:
         * Title: "Problem 1: Binary Search"
         * Badge: Mint "PASS"
         * Metadata: "Track: DSA · Topic: binary-search · Easy"
         * Runtime: "178 ms", Hints Used: 0
       - Question 2 Summary Card:
         * Title: "Problem 2: Flatten Nested Dictionary"
         * Badge: Mint "PASS"
         * Metadata: "Track: Python · Topic: recursion · Medium"
         * Runtime: "8 ms", Hints Used: 0
       - Elapsed time summary: "Total elapsed time: 25.0 minutes (Well under the 45:00 limit)".
       - Actions: Secondary pill button "Download Scorecard (Markdown)", Primary green pill button "Start New Mock Session".
    4. Iconography:
       - Verify all inline SVGs are Lucide SVGs exclusively from `agent-resources/lucide/icons`.

    AVOID: Arbitrary ungrounded problem names in Question 1; Question 1 must be "Binary Search PASS (178ms)".
    USE: Direction A typography and color tokens throughout.
  </action>
  <verify>
    python -c "mock=open('mockups/mock.html', encoding='utf-8').read(); assert '44:41' in mock; assert 'Binary Search' in mock and '178' in mock; assert 'Mock Interview Scorecard' in mock; print('PASS: Mock arena timer and scorecard verified')"
  </verify>
  <done>
    `mockups/mock.html` displays the 44:41 Peach-tint countdown timer and the Binary Search PASS (178ms) scorecard in full Direction A styling.
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
- [ ] `mockups/practice.html` contains `def lengthOfLongestSubstring(s: str) -> int:`
- [ ] `mockups/practice.html` renders dark code inset and Rose-tinted verdict
- [ ] `mockups/mock.html` contains `44:41` timer countdown capsule
- [ ] `mockups/mock.html` contains Question 1 Binary Search PASS (178ms)
- [ ] No application code files (`app.py`, `coach/*`, etc.) were edited
</verification>

<success_criteria>
- [ ] All tasks verified passing
- [ ] Must-haves confirmed
- [ ] Zero app code modified
</success_criteria>
