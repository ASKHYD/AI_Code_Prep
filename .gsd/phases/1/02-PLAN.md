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
    - "Practice mockup displays genuine starter signature def longest_substring(s: str) -> int:"
    - "Practice mockup contains dark code inset (#14161A), primary green pill CTA (#15803D), and Rose-tinted test verdict panel (#FFE0E0 / #C5221F) showing real visible test failure from problem file without invented runtimes or pass counts"
    - "Mock interview mockup displays live countdown timer state at 44:41 in Peach-tint capsule (#FFE8D1 / #B93815)"
    - "Mock interview scorecard includes the locked authentic result Question 1 Binary Search PASS (178ms) without invented runtimes or pass counts"
    - "Zero application code files (app.py, config.toml, coach/*, data/problems/*, tests/*) are modified"
  artifacts:
    - mockups/practice.html
    - mockups/mock.html
---

# Plan 1.2: Core Workspace Mockups (Practice Arena & Mock Interview)

<objective>
Refine the core interactive workspace static HTML mockups (`mockups/practice.html` and `mockups/mock.html`) to strictly implement Direction A aesthetics, authentic problem starter signatures (`longest_substring`), traceable visible test cases from `data/problems/*.json`, the 44:41 live countdown timer, and the locked authentic result (Binary Search PASS 178ms) with ZERO invented numbers.
</objective>

<context>
Load for context:
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/DECISIONS.md
- data/problems/longest-substring-without-repeating.json
- data/problems/binary-search.json
- mockups/style.css
- mockups/practice.html
- mockups/mock.html
- agent-resources/lucide/icons/
</context>

<tasks>

<task type="auto">
  <name>Refine Practice Arena Mockup with Authentic Signature and Grounded Failure Panel</name>
  <files>
    mockups/practice.html
  </files>
  <action>
    Refine `mockups/practice.html` with Direction A styling and strictly traceable coding-arena data:
    1. Filter & Metadata Bar:
       - DSA / Strings / Medium badges with "Problem 4 of 12 in Library".
    2. Problem Statement Column (Left 4 cols / 35%):
       - Title: "Longest Substring Without Repeating Characters" in Fraunces serif.
       - Problem description and constraints.
       - Explicit function signature box displaying the EXACT starter signature from `data/problems/longest-substring-without-repeating.json`:
         `def longest_substring(s: str) -> int:`
       - Visible test case card #1 in Mint wash (`#DFF3E4`) showing real visible test: input `s = "abcabcbb"`, expected `3`.
       - Progressive hint ladder in Butter wash (`#FFF0C4`, `#9A3412` text) showing Hint 1 of 3.
    3. Code Editor & Execution Column (Right 7 cols / 65%):
       - Editor card with Lilac/Violet header strip (`Solution Editor · Python 3.12`, Subprocess Sandbox 3.0s Timeout).
       - Deep ink code inset (`#14161A` background, `#F2F2ED` text, JetBrains Mono font, min-height 440px).
       - Code editor content displaying the Python sliding-window solution using the authentic function signature `def longest_substring(s: str) -> int:`.
       - Run action bar with saturated emerald green pill button (`#15803D`, white text, 9999px radius) for "Run & Submit".
    4. Execution Verdict Card (Zero Invented Numbers):
       - Saturated Rose tint wash (`#FFE0E0` wash, `#C5221F` partner text, `#D92D20` fill).
       - Badge: `FAIL`.
       - Verdict text: `Visible Test Case 1 Failed` (NO invented pass counts, NO invented runtimes).
       - Input / expected diff showing a real visible test case from `data/problems/longest-substring-without-repeating.json`:
         `Input: s = "abcabcbb"`, `Expected: 3`, `Got: 2`.
    5. Iconography:
       - Verify all inline SVGs are Lucide SVGs exclusively from `agent-resources/lucide/icons`.

    AVOID: Modifying any application code or problem JSON files.
    AVOID: Using LeetCode camelCase method names; use the authentic starter signature `def longest_substring(s: str) -> int:`.
    AVOID: Invented runtimes or invented pass counts.
    USE: Exact visible test cases from `data/problems/longest-substring-without-repeating.json`.
  </action>
  <verify>
    python -c "prac=open('mockups/practice.html', encoding='utf-8').read(); assert 'def longest_substring(s: str) -> int:' in prac; assert 'Visible Test Case 1 Failed' in prac; assert 'abcabcbb' in prac; print('PASS: Practice arena authentic signature and test case verified without invented numbers')"
  </verify>
  <done>
    `mockups/practice.html` renders authentic `longest_substring` starter signature, dark editor inset, and Rose-tinted verdict card based on real visible test data without invented numbers.
  </done>
</task>

<task type="auto">
  <name>Refine Mock Interview Arena with Live 44:41 Timer and Locked Authentic Result</name>
  <files>
    mockups/mock.html
  </files>
  <action>
    Refine `mockups/mock.html` with Direction A styling and strictly grounded simulation data:
    1. Header & Live Countdown Capsule:
       - Fraunces heading "Technical Interview Simulation", subtitle describing 45:00 countdown constraint.
       - Live timer capsule in Peach wash (`#FFE8D1` wash, `#B93815` coral partner text, hairline border `rgba(185, 56, 21, 0.25)`).
       - Timer display showing EXACT countdown state: `44:41` in JetBrains Mono with tabular numbers.
       - White capsule badge "Ticking Live" with coral text `#B93815`.
    2. Problem Navigation Strip:
       - Pill buttons for active Problem 1 (Binary Search) and Problem 2 (Longest Substring Without Repeating Characters).
    3. Mock Interview Evaluation Card (Zero Invented Numbers):
       - White surface card with 24px radius and soft shadow.
       - Badge "Session In Progress", Fraunces title "Mock Interview Evaluation".
       - Question 1 Summary Card (using the one locked authentic result from SQLite):
         * Title: "Problem 1: Binary Search"
         * Badge: Mint "PASS"
         * Metadata: "Track: DSA · Topic: binary-search · Easy"
         * Runtime: "178 ms", Hints Used: 0
       - Question 2 Summary Card:
         * Title: "Problem 2: Longest Substring Without Repeating Characters"
         * Badge: Sky "In Progress"
         * Metadata: "Track: DSA · Topic: strings · Medium"
         * Visible Test Data: Input `s = "abcabcbb"`, Expected `3`
         * ZERO invented pass counts and ZERO invented runtimes.
       - Actions: Secondary pill button "Download Scorecard (Markdown)", Primary green pill button "Submit Solution".
    4. Iconography:
       - Verify all inline SVGs are Lucide SVGs exclusively from `agent-resources/lucide/icons`.

    AVOID: Invented runtimes, invented pass counts, or unrecorded problem passes.
    USE: The one locked authentic result: `Binary Search · PASS · 178 ms` (Hints: 0) and real problem definitions from `data/problems/*.json`.
  </action>
  <verify>
    python -c "mock=open('mockups/mock.html', encoding='utf-8').read(); assert '44:41' in mock; assert 'Binary Search' in mock and '178 ms' in mock; print('PASS: Mock arena timer and authentic scorecard verified without invented numbers')"
  </verify>
  <done>
    `mockups/mock.html` displays the 44:41 Peach-tint countdown timer and the locked authentic result (Binary Search PASS 178ms) in full Direction A styling without invented metrics.
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
- [ ] `mockups/practice.html` contains `def longest_substring(s: str) -> int:`
- [ ] `mockups/practice.html` contains authentic function signature `longest_substring`
- [ ] `mockups/practice.html` contains no invented pass counts or runtimes
- [ ] `mockups/mock.html` contains `44:41` timer countdown capsule
- [ ] `mockups/mock.html` contains Question 1 Binary Search PASS (178 ms) with zero invented runtimes
- [ ] No application code files (`app.py`, `coach/*`, etc.) were edited
</verification>

<success_criteria>
- [ ] All tasks verified passing
- [ ] Must-haves confirmed
- [ ] Zero app code modified
</success_criteria>
