# Feature Specification: AI Coding Prep Coach MVP

- **Feature Directory**: `specs/001-coding-prep-coach/`
- **Target Audience**: Software engineers preparing for technical coding interviews (DSA & Python practical)
- **Status**: Draft -> Frozen for MVP Implementation

## 1. Overview & Vision
AI Coding Prep Coach is a local, zero-cost, privacy-first technical interview practice tool built with Python and Streamlit.
The core philosophy is: **THE JUDGE IS CODE, NOT AI**.
- User solutions are judged strictly and deterministically by executing against hidden unit tests in a secure subprocess sandbox.
- An optional local LLM (via Ollama, defaulting to `qwen2.5-coder:3b`) provides progressive explanations of stored hints and code reviews, but never scores solutions, never invents tests, and never affects the pass/fail determination.
- The app operates fully offline with Ollama switched off.

## 2. Hard Constraints & Boundaries
1. **Zero Cost / Zero Paid APIs**: Strictly no external LLM APIs (OpenAI, Anthropic, Gemini, Groq, etc.).
2. **Original / Open-Licensed Content**: No LeetCode scraping. 12 original problems shaped after Exercism problem specifications with author-written reference solutions passing 100% of tests.
3. **Subprocess Sandbox**: User code runs in an isolated subprocess with 3s timeout, empty temp working directory, no network access, and stripped environment variables.
4. **No Invented Metrics**: All reported pass rates, streaks, and runtimes derive strictly from SQLite database records.
5. **MVP Gate**: Strictly in-scope: Practice Mode, Hint Ladder, Spaced Repetition, Dashboard, Mock Interview, Ruff static review, and offline Ollama fallbacks. Out of scope: accounts/auth, cloud hosting, Explain-Back mode, voice.

## 3. User Stories & Priority Lanes

### User Story 1 (P1) - Deterministic Sandboxed Code Execution (Lane A)
As a candidate, I want my submitted Python solution to be executed against hidden tests inside a timeout-enforced, stripped sandbox so that I get fast, reliable, objective pass/fail results without risk of hanging or app crashes.
- **Acceptance Criteria**:
  - `run_solution(code, problem)` executes within 3s (+ slack).
  - Infinite loops terminate with `status: timeout` in ~3s.
  - Syntax/Runtime exceptions return `status: error` with captured stderr.
  - Test mismatches return `status: fail` with specific `failed_cases: [{input_args, expected, got}]`.
  - Solutions passing all visible and hidden tests return `status: pass`.

### User Story 2 (P2) - Validated Problem Bank & Reference Solutions (Lane B)
As a candidate, I want a curated collection of at least 12 coding problems (9 DSA, 3 Python practical) with visible and hidden test cases and verified reference solutions so that I can practice across core interview topics.
- **Acceptance Criteria**:
  - Minimum 12 JSON problem files validated against Pydantic schema.
  - Minimum 2 visible tests and 5 hidden edge cases per problem.
  - 100% of reference solutions pass all test cases through the sandbox judge.

### User Story 3 (P3) - Spaced Repetition & History Persistence (Lane C)
As a candidate, I want my practice attempts persisted locally in SQLite and scheduled for review using an interview-tailored repetition schedule so that I reinforce concepts over time.
- **Acceptance Criteria**:
  - SQLite persistence in `coach.db`.
  - Deterministic interval schedule:
    - Failed attempt: due in 1 day (subsequent fails remain 1 day).
    - 1st consecutive pass after fail: due in 3 days.
    - 2nd consecutive pass: due in 7 days.
    - 3rd+ consecutive pass: due in 21 days.
  - Due problem listing and topic statistics calculation.

### User Story 4 (P4) - Interactive Streamlit UI & Code Editor (Lane D)
As a candidate, I want a responsive, clear web UI with a home dashboard, problem selector, Monaco/code editor with syntax highlighting, and clear pass/fail/error/timeout visual feedback.
- **Acceptance Criteria**:
  - Streamlit application (`app.py`) with clean sidebar navigation.
  - Code editor via `streamlit-code-editor` with monospace `st.text_area` fallback.
  - Visually distinct badges and diff cards for PASS, FAIL, TIMEOUT, and ERROR states.
  - Due review queue displayed on Home screen.

### User Story 5 (P5) - Offline-First AI Hint Ladder & Static Code Review (Lane E)
As a candidate, I want a 3-level progressive hint ladder and static style analysis via Ruff, plus optional local AI explanation that safely degrades to stored hints when Ollama is offline.
- **Acceptance Criteria**:
  - Progressive hint revelation (Level 1 -> 2 -> 3).
  - `explain_hint()` and `review_code()` degrade gracefully without throwing exceptions when Ollama is unreachable.
  - Ruff runs as a subprocess and outputs linting diagnostics on submitted solutions.

### User Story 6 (P6) - 45-Minute Mock Interview Simulation (Lane F)
As a candidate, I want to take a timed 45-minute mock interview session consisting of 2 problems (1 medium DSA + 1 hard DSA or practical) that generates a final performance scorecard with markdown export.
- **Acceptance Criteria**:
  - Session-state 45-minute countdown timer.
  - Scorecard tracking problems solved, total time taken, and hints used.
  - Downloadable Markdown scorecard report.
