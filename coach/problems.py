"""
Problem Schema and Loader using Pydantic.
Validates problem structure against the frozen CONTRACT.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    input_args: list[Any] = Field(description="Positional arguments passed to the function")
    expected: Any = Field(description="Expected return value")


class ProblemSchema(BaseModel):
    id: str = Field(description="Unique slug identifier")
    title: str = Field(description="Human-readable problem title")
    topic: str = Field(description="Problem category / topic")
    difficulty: Literal["easy", "medium", "hard"]
    track: Literal["dsa", "python"]
    statement_md: str = Field(description="Markdown problem statement")
    function_name: str = Field(description="Name of the entrypoint function in user code")
    starter_code: str = Field(description="Starter boilerplate code shown in editor")
    visible_tests: list[TestCase] = Field(min_length=2, description="At least 2 visible test cases")
    hidden_tests: list[TestCase] = Field(min_length=5, description="At least 5 hidden test cases")
    hints: list[str] = Field(min_length=3, max_length=3, description="Exact 3 progressive hint strings")
    reference_solution: str = Field(description="Working reference code that passes 100% of tests")
    time_limit_sec: float = Field(default=3.0, description="Per-run timeout in seconds")


def load_problem_from_file(file_path: Path | str) -> ProblemSchema:
    """Loads and validates a single problem JSON file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Problem file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProblemSchema(**data)


def load_problem(problem_id: str, dir_path: Path | str = "data/problems") -> ProblemSchema:
    """Loads a problem by id from the problems directory."""
    path = Path(dir_path) / f"{problem_id}.json"
    return load_problem_from_file(path)


def load_all_problems(dir_path: Path | str = "data/problems") -> list[ProblemSchema]:
    """Loads and validates all problem JSON files in dir_path."""
    folder = Path(dir_path)
    if not folder.exists():
        return []
    problems = []
    for file_path in sorted(folder.glob("*.json")):
        problems.append(load_problem_from_file(file_path))
    return problems
