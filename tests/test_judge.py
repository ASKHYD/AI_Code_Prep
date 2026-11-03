import time

from coach.judge import run_solution

SAMPLE_PROBLEM = {
    "id": "two-sum",
    "function_name": "two_sum",
    "visible_tests": [
        {"input_args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
        {"input_args": [[3, 2, 4], 6], "expected": [1, 2]},
    ],
    "hidden_tests": [
        {"input_args": [[3, 3], 6], "expected": [0, 1]},
        {"input_args": [[-1, -2, -3, -4, -5], -8], "expected": [2, 4]},
        {"input_args": [[0, 4, 3, 0], 0], "expected": [0, 3]},
        {"input_args": [[1, 5, 2, 7, 8], 15], "expected": [3, 4]},
        {"input_args": [[10, 20, 30, 40], 50], "expected": [1, 2]},
    ],
    "time_limit_sec": 3.0,
}

def test_judge_correct_solution_passes():
    correct_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    result = run_solution(correct_code, SAMPLE_PROBLEM)
    assert result["status"] == "pass"
    assert result["passed"] == 7
    assert result["total"] == 7
    assert len(result["failed_cases"]) == 0
    assert result["runtime_ms"] >= 0

def test_judge_wrong_solution_fails_with_cases():
    wrong_code = """
def two_sum(nums, target):
    return [0, 0]
"""
    result = run_solution(wrong_code, SAMPLE_PROBLEM)
    assert result["status"] == "fail"
    assert result["passed"] < result["total"]
    assert len(result["failed_cases"]) > 0
    first_fail = result["failed_cases"][0]
    assert "input_args" in first_fail
    assert "expected" in first_fail
    assert "got" in first_fail
    assert first_fail["got"] == [0, 0]

def test_judge_infinite_loop_timeout():
    infinite_loop_code = """
def two_sum(nums, target):
    while True:
        pass
"""
    start_time = time.time()
    result = run_solution(infinite_loop_code, SAMPLE_PROBLEM)
    elapsed = time.time() - start_time
    assert result["status"] == "timeout"
    assert 2.5 <= elapsed <= 6.0
    assert "timed out" in result["stderr"].lower()

def test_judge_syntax_error_returns_error_status():
    syntax_error_code = """
def two_sum(nums, target
    return 1
"""
    result = run_solution(syntax_error_code, SAMPLE_PROBLEM)
    assert result["status"] == "error"
    assert len(result["stderr"]) > 0

def test_judge_runtime_exception_returns_error_status():
    exception_code = """
def two_sum(nums, target):
    raise ValueError("Deliberate test explosion")
"""
    result = run_solution(exception_code, SAMPLE_PROBLEM)
    assert result["status"] == "error"
    assert "Deliberate test explosion" in result["stderr"]

def test_judge_sandbox_strips_api_keys():
    sandbox_code = """
import os
def two_sum(nums, target):
    # Verify no OPENAI_API_KEY, ANTHROPIC_API_KEY, etc. in env
    for k in os.environ:
        if "API_KEY" in k.upper() or "SECRET" in k.upper():
            raise RuntimeError(f"Found sensitive key in sandbox: {k}")
    return [0, 1]
"""
    result = run_solution(sandbox_code, SAMPLE_PROBLEM)
    assert result["status"] in ("pass", "fail")
    assert "Found sensitive key" not in result.get("stderr", "")

def test_judge_outside_file_read_fails_gracefully():
    file_code = """
import os
def two_sum(nums, target):
    # Attempt to read a file outside cwd
    with open("../secret_flag_nonexistent_xyz.txt", "r") as f:
        return f.read()
"""
    result = run_solution(file_code, SAMPLE_PROBLEM)
    assert result["status"] == "error"
    assert "FileNotFoundError" in result["stderr"] or "secret_flag" in result["stderr"]

