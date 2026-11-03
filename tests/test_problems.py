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
