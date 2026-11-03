from coach.llm_hints import explain_hint, review_code
from coach.review import run_ruff_lint

SAMPLE_PROBLEM = {
    "id": "two-sum",
    "title": "Two Sum",
    "hints": [
        "Store visited numbers in a hash map.",
        "Check if target - num exists in map.",
        "Return the index pair [seen[target - num], i]."
    ]
}

def test_explain_hint_fallback_when_ollama_offline():
    # Model is pending download and Ollama daemon is offline
    user_code = "def two_sum(nums, target): return []"

    # Test level 1
    hint1 = explain_hint(SAMPLE_PROBLEM, user_code, hint_level=1)
    assert "Local AI is off" in hint1
    assert "Store visited numbers in a hash map." in hint1

    # Test level 2
    hint2 = explain_hint(SAMPLE_PROBLEM, user_code, hint_level=2)
    assert "Local AI is off" in hint2
    assert "Check if target - num exists in map." in hint2

    # Test level 3
    hint3 = explain_hint(SAMPLE_PROBLEM, user_code, hint_level=3)
    assert "Local AI is off" in hint3
    assert "Return the index pair" in hint3

def test_review_code_fallback_when_ollama_offline():
    user_code = "def two_sum(nums, target): return []"
    review = review_code(SAMPLE_PROBLEM, user_code)
    assert "Local AI is off" in review
    assert isinstance(review, str)

def test_ruff_lint_on_messy_fixture():
    # Code with intentional style/syntax issues: unused import, undefined variable
    messy_code = """
import sys
import os

def two_sum(nums, target):
    unused_var = 123
    return undefined_identifier_xyz
"""
    lint_result = run_ruff_lint(messy_code)
    assert isinstance(lint_result, dict)
    assert "findings" in lint_result
    assert len(lint_result["findings"]) > 0

    messages = [f["message"] for f in lint_result["findings"]]
    codes = [f["code"] for f in lint_result["findings"]]

    # Verify ruff caught unused import (F401) or undefined name (F821)
    assert any("F401" in c or "unused" in m.lower() for c, m in zip(codes, messages))
    assert any("F821" in c or "undefined" in m.lower() for c, m in zip(codes, messages))

def test_ruff_lint_on_clean_code():
    clean_code = """def add(a: int, b: int) -> int:
    return a + b
"""
    lint_result = run_ruff_lint(clean_code)
    assert isinstance(lint_result, dict)
    assert len(lint_result["findings"]) == 0
