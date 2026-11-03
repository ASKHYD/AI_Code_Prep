import pytest

from coach.judge import run_solution
from coach.problems import ProblemSchema, load_all_problems


def test_problem_schema_validation_rejects_missing_fields():
    with pytest.raises(Exception):
        ProblemSchema(
            id="bad-prob",
            title="Incomplete",
            # missing topic, tracks, etc.
        )

def test_all_12_problems_exist_and_validate():
    problems = load_all_problems("data/problems")
    assert len(problems) >= 12

    topics = set()
    dsa_count = 0
    python_count = 0

    for p in problems:
        assert isinstance(p, ProblemSchema)
        assert len(p.visible_tests) >= 2
        assert len(p.hidden_tests) >= 5
        assert len(p.hints) == 3
        assert len(p.reference_solution.strip()) > 0
        topics.add(p.topic)
        if p.track == "dsa":
            dsa_count += 1
        elif p.track == "python":
            python_count += 1

    assert dsa_count >= 9
    assert python_count >= 3

def test_every_reference_solution_passes_100_percent():
    problems = load_all_problems("data/problems")
    for p in problems:
        p_dict = p.model_dump()
        result = run_solution(p.reference_solution, p_dict)
        assert result["status"] == "pass", f"Problem {p.id} reference solution failed: {result}"
        assert result["passed"] == result["total"]
        assert len(result["failed_cases"]) == 0


def test_all_problems_expose_signature_in_statement_and_starter():
    """
    Lane J Step 4 Generalisation:
    For EVERY problem in the bank, assert:
    1. The statement exposes the exact function_name in a signature block.
    2. The starter code exposes the exact function_name.
    """
    problems = load_all_problems("data/problems")
    for p in problems:
        assert p.function_name in p.statement_md, (
            f"Problem '{p.id}' does not expose function '{p.function_name}' in statement_md"
        )
        assert f"def {p.function_name}" in p.starter_code, (
            f"Problem '{p.id}' starter_code does not define 'def {p.function_name}'"
        )
        assert "### Function Signature" in p.statement_md, (
            f"Problem '{p.id}' missing '### Function Signature' block in statement_md"
        )


def test_alternative_solutions_pass_for_string_problems():
    """
    Lane J Step 4 Generalisation:
    Tests an independently-written second solution style for the 3 single-argument
    string problems to guarantee alternative valid coding styles pass through the judge.
    """
    from coach.problems import load_problem

    # 1. longest-substring-without-repeating (Alternative set-based sliding window)
    p_substr = load_problem("longest-substring-without-repeating").model_dump()
    alt_substr = """def longest_substring(s: str) -> int:
    seen = set()
    l = 0
    res = 0
    for r, c in enumerate(s):
        while c in seen:
            seen.remove(s[l])
            l += 1
        seen.add(c)
        res = max(res, r - l + 1)
    return res
"""
    res1 = run_solution(alt_substr, p_substr)
    assert res1["status"] == "pass", f"Alternative solution for longest-substring failed: {res1}"

    # 2. valid-parentheses (Alternative dict lookup stack)
    p_parens = load_problem("valid-parentheses").model_dump()
    alt_parens = """def is_valid_parentheses(s: str) -> bool:
    mapping = {')': '(', '}': '{', ']': '['}
    stack = []
    for char in s:
        if char in mapping.values():
            stack.append(char)
        elif char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            return False
    return len(stack) == 0
"""
    res2 = run_solution(alt_parens, p_parens)
    assert res2["status"] == "pass", f"Alternative solution for valid-parentheses failed: {res2}"

    # 3. string-permutations (Alternative recursive backtracking)
    p_perms = load_problem("string-permutations").model_dump()
    alt_perms = """def get_permutations(s: str) -> list[str]:
    if not s:
        return [""]
    chars = sorted(list(s))
    used = [False] * len(chars)
    result = []
    def backtrack(path):
        if len(path) == len(chars):
            result.append("".join(path))
            return
        for i in range(len(chars)):
            if used[i]:
                continue
            if i > 0 and chars[i] == chars[i-1] and not used[i-1]:
                continue
            used[i] = True
            path.append(chars[i])
            backtrack(path)
            path.pop()
            used[i] = False
    backtrack([])
    return result
"""
    res3 = run_solution(alt_perms, p_perms)
    assert res3["status"] == "pass", f"Alternative solution for string-permutations failed: {res3}"

