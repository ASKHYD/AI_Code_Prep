"""
Tests for Milestone 4 Bank Expansion (8 new problems: 2 Easy, 3 Medium, 3 Hard).
Verifies:
- All 8 new problems exist, validate schema, and pass 100% of visible and hidden tests with reference solutions.
- Negative tests on a new Hard problem ('trapping-rain-water'):
  - Wrong logic fails with expected/got divergence.
  - Infinite loop times out cleanly at 3.0s boundary.
  - Syntax error raises clean error verdict.
"""

import pytest

from coach.judge import run_solution
from coach.problems import load_problem

NEW_PROBLEM_IDS = [
    "merge-sorted-array",
    "maximum-depth-of-binary-tree",
    "group-anagrams",
    "coin-change",
    "course-schedule",
    "trapping-rain-water",
    "median-of-two-sorted-arrays",
    "word-ladder",
]


@pytest.mark.parametrize("pid", NEW_PROBLEM_IDS)
def test_new_problem_schema_and_reference_pass(pid: str):
    p = load_problem(pid)
    data = p.model_dump()
    assert len(data["visible_tests"]) >= 2
    assert len(data["hidden_tests"]) >= 5
    assert len(data["hints"]) == 3

    # X6 signature doctrine
    first_line = data["starter_code"].splitlines()[0].strip()
    import re
    m = re.search(r"###\s*Function Signature\s*```(?:python)?\s*[\r\n]+(.*?)```", data["statement_md"], re.DOTALL)
    assert m, f"No signature block in {pid}"
    assert first_line == m.group(1).strip()

    # Reference execution passes 100%
    res = run_solution(data["reference_solution"], data)
    assert res["status"] == "pass"
    assert res["passed"] == len(data["visible_tests"]) + len(data["hidden_tests"])


def test_hard_problem_negative_proofs():
    """Negative proofs on 'trapping-rain-water' (Hard)."""
    p = load_problem("trapping-rain-water")
    data = p.model_dump()

    # 1. Logic failure
    wrong_code = (
        "def trap_rain_water(heights: list) -> int:\n"
        "    return 0  # wrong\n"
    )
    res_wrong = run_solution(wrong_code, data)
    assert res_wrong["status"] == "fail"
    assert len(res_wrong["failed_cases"]) > 0
    fc = res_wrong["failed_cases"][0]
    assert fc["expected"] == 6
    assert fc["got"] in (0, "0")

    # 2. Syntax error
    syntax_error_code = (
        "def trap_rain_water(heights: list) -> int:\n"
        "    return 0 + \n"
    )
    res_syntax = run_solution(syntax_error_code, data)
    assert res_syntax["status"] == "error"
    assert "SyntaxError" in res_syntax["stderr"]

    # 3. Timeout
    timeout_code = (
        "def trap_rain_water(heights: list) -> int:\n"
        "    while True:\n"
        "        pass\n"
    )
    res_timeout = run_solution(timeout_code, data)
    assert res_timeout["status"] == "timeout"
    assert "timed out" in res_timeout["stderr"].lower()
