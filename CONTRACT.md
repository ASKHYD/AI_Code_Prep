# INTERFACE CONTRACT: AI Coding Prep Coach MVP

Frozen on 2026-11-04. Every lane must implement against these exact interfaces.

---

## 1. Problem JSON Schema (Pydantic / Storage)
Each problem is stored as a single JSON file under `data/problems/<id>.json`.

```python
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

class TestCase(BaseModel):
    input_args: List[Any]  # Positional arguments passed to the function (*input_args)
    expected: Any          # Expected return value

class ProblemSchema(BaseModel):
    id: str                                                 # Unique slug e.g. "two-sum"
    title: str                                              # Human-readable title
    topic: str                                              # e.g. "arrays", "strings", "data-processing"
    difficulty: Literal["easy", "medium", "hard"]
    track: Literal["dsa", "python"]
    statement_md: str                                       # Markdown problem description
    function_name: str                                      # Entrypoint name in user code
    starter_code: str                                       # Starter template for editor
    visible_tests: List[TestCase] = Field(min_length=2)     # Minimum 2 visible tests
    hidden_tests: List[TestCase] = Field(min_length=5)      # Minimum 5 hidden test cases
    hints: List[str] = Field(min_length=3, max_length=3)    # Level 1, Level 2, Level 3
    reference_solution: str                                 # Working implementation passing 100% of tests
    time_limit_sec: float = 3.0                             # Default 3.0 seconds
```

---

## 2. Judge Engine API (`coach/judge.py`)

```python
def run_solution(code: str, problem: dict) -> dict:
    """
    Executes user solution inside a secure subprocess sandbox.
    
    Sandbox constraints:
    - 3-second timeout per run (customizable via problem.time_limit_sec)
    - Temp directory as cwd (no access to repository or local workspace)
    - Stripped environment (PATH, SYSTEMROOT only; no API keys)
    - Network disabled / blocked
    
    Returns:
    {
        "status": "pass" | "fail" | "timeout" | "error",
        "passed": int,
        "total": int,
        "failed_cases": [
            {
                "input_args": list,
                "expected": any,
                "got": any
            }
        ],
        "runtime_ms": int,
        "stderr": str
    }
    """
```

---

## 3. Storage & Spaced Repetition API (`coach/store.py` & `coach/repetition.py`)

### Repetition Rule Table
The schedule is deterministic based on consecutive passes since the last failure:
- Any failed attempt (`fail`, `timeout`, `error`): due in **1 day**; consecutive passes resets to 0.
- If failed again: due in **1 day**.
- First pass after failure (consecutive_passes == 1): due in **3 days**.
- Second consecutive pass (consecutive_passes == 2): due in **7 days**.
- Third consecutive pass or higher (consecutive_passes >= 3): due in **21 days**.

```python
def next_due_date(consecutive_passes: int, status: str, from_date: Optional[str] = None) -> str:
    """Calculates ISO date (YYYY-MM-DD) for next review."""
```

### Store API (`coach/store.py`)
Backing store: SQLite single file database `coach.db`.

```python
class CoachStore:
    def __init__(self, db_path: str = "coach.db"):
        ...
        
    def record_attempt(
        self,
        problem_id: str,
        status: str,             # "pass" | "fail" | "timeout" | "error"
        runtime_ms: int,
        hints_used: int,         # 0, 1, 2, or 3
        mode: str = "practice"   # "practice" | "mock"
    ) -> int:
        """Records attempt and updates repetition schedule for problem_id."""
        ...
        
    def due_problems(self, today: Optional[str] = None) -> List[dict]:
        """Returns list of problem IDs and metadata due on or before today."""
        ...
        
    def topic_stats(self) -> dict:
        """
        Returns stats aggregated by topic:
        {
            topic_name: {
                "attempts": int,
                "passed": int,
                "pass_rate": float  # 0.0 to 100.0
            }
        }
        """
        ...
        
    def current_streak(self, today: Optional[str] = None) -> int:
        """Returns consecutive days with at least 1 attempt leading up to today."""
        ...
```

---

## 4. Local AI & Static Review API (`coach/llm_hints.py` & `coach/review.py`)

Neither LLM function is ever called by the judge. Both return safe fallbacks when Ollama is unreachable.

```python
def explain_hint(problem: dict, user_code: str, hint_level: int) -> str:
    """
    Calls local Ollama (qwen2.5-coder:3b) to explain stored hint at requested level (1-3).
    Fallback if Ollama is unreachable or error:
    "Local AI is off — here is the stored hint: <stored_hint>"
    """

def review_code(problem: dict, user_code: str) -> str:
    """
    Calls local Ollama for code review suggestions.
    Fallback if Ollama is unreachable or error:
    "Local AI is off — AI code review unavailable."
    """

def run_ruff_lint(code: str) -> dict:
    """
    Runs Ruff static analysis on submitted code via subprocess.
    Returns:
    {
        "findings": [
            {
                "line": int,
                "col": int,
                "code": str,
                "message": str
            }
        ],
        "summary": str
    }
    """
```
