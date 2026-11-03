# Task List: AI Coding Prep Coach MVP

- **Feature**: `001-coding-prep-coach`
- **Spec**: `specs/001-coding-prep-coach/spec.md`
- **Status**: Ready for Implementation

## Phase 1: Setup & Foundational Contract (Phase 0)
- [x] **TASK-SETUP-1**: Establish project directory layout (`coach/`, `data/problems/`, `tests/`, `specs/`).
- [ ] **TASK-SETUP-2**: Write and freeze `CONTRACT.md` detailing:
  - Problem JSON Schema (Pydantic model)
  - Judge API: `run_solution(code, problem) -> dict`
  - Store API (SQLite): `record_attempt()`, `due_problems()`, `topic_stats()`
  - Repetition rule table (1 / 1 / 3 / 7 / 21 days)
  - LLM Hint & Review API with graceful offline fallbacks

## Phase 2: Parallel Lane Implementation

### Lane A: Sandbox Judge Engine (P1)
- [ ] **TASK-LANE-A1**: [TDD] Write `tests/test_judge.py` covering:
  - Correct code returns `status: pass` with runtime
  - Wrong output returns `status: fail` with failed test case details
  - Infinite loop terminates in ~3s with `status: timeout` (measure wall clock)
  - Syntax/Runtime exception returns `status: error` with stderr
  - Subprocess file isolation / security checks
- [ ] **TASK-LANE-A2**: Implement `coach/judge.py` using Python standard library subprocess, tempfile, json, time.

### Lane B: Problem Bank & Schema Validation (P2)
- [ ] **TASK-LANE-B1**: [TDD] Implement Pydantic schema in `coach/problems.py` with validation and file loading.
- [ ] **TASK-LANE-B2**: Author 12 original problems in `data/problems/*.json`:
  - 9 DSA: Two Sum (Arrays), Valid Parentheses (Stack), Longest Substring Without Repeating (Strings/Sliding Window), Reverse Linked List (Linked List), Binary Search (Binary Search), Maximum Subarray (Two Pointers/Greedy), Invert Binary Tree (Tree Traversal), Fibonacci/Climbing Stairs (DP), Permutations (Recursion/Backtracking).
  - 3 Python Practical: CSV Column Summarizer (Data Transformation), Log Timestamp Parser (String/Time Parsing), Nested Dict Flattener (Dict/List Processing).
- [ ] **TASK-LANE-B3**: Write `tests/test_problems.py` ensuring every problem validates against Pydantic schema and every `reference_solution` passes 100% of its tests via Lane A's judge.

### Lane C: Persistence Store & Spaced Repetition (P3)
- [ ] **TASK-LANE-C1**: [TDD] Write `tests/test_store.py` verifying round-trip persistence, streak calculation, topic stats, and exact 1/1/3/7/21-day spaced repetition schedule.
- [ ] **TASK-LANE-C2**: Implement `coach/repetition.py` (deterministic repetition interval calculation).
- [ ] **TASK-LANE-C3**: Implement `coach/store.py` (SQLite schema, record attempts, query due problems, compute stats).

### Lane D: Streamlit User Interface (P4)
- [ ] **TASK-LANE-D1**: Implement `app.py` with multi-screen navigation (Home/Due, Practice, Mock Interview, Dashboard).
- [ ] **TASK-LANE-D2**: Integrate `streamlit-code-editor` with automatic `st.text_area` monospace fallback.
- [ ] **TASK-LANE-D3**: Build Practice screen with problem description, visible test preview, hint ladder, judge feedback cards (Pass/Fail/Timeout/Error), and Ruff findings.
- [ ] **TASK-LANE-D4**: Build Dashboard with Plotly bar charts and topic proficiency metrics.

### Lane E: AI Hints & Static Code Review (P5)
- [ ] **TASK-LANE-E1**: [TDD] Write `tests/test_llm_fallback.py` asserting Ollama unreachable returns stored hint fallback and Ruff subprocess returns lint errors on messy code.
- [ ] **TASK-LANE-E2**: Implement `coach/llm_hints.py` (Ollama client with low temp, stored prompt format, and clean offline fallback).
- [ ] **TASK-LANE-E3**: Implement `coach/review.py` (Ruff subprocess execution and formatting).

### Lane F: Mock Interview & Integration Packaging (P6)
- [ ] **TASK-LANE-F1**: Implement Mock Interview mode in `app.py` (2-problem selection, 45-minute countdown, hint usage tracking, scorecard generation, and Markdown export).
- [ ] **TASK-LANE-F2**: Create `requirements.txt` pinned to packages actually imported.
- [ ] **TASK-LANE-F3**: Create `README.md` with one-command run, Ollama setup, architecture Mermaid diagram, sandbox rules, and project boundaries.

## Phase 3: Verification & Evidence Gathering
- [ ] **TASK-VERIFY-1**: Execute complete pytest suite across all tests.
- [ ] **TASK-VERIFY-2**: Run end-to-end verification and capture UI screenshots for Home, Practice, Dashboard, and Mock Scorecard.
- [ ] **TASK-VERIFY-3**: Perform Agency Finish Gate Review and Reality Check.
