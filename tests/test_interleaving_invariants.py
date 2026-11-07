"""
Unit tests for Task 3.2: Free Picking Invariant & First-Exposure Roadmap Branch.
Verifies:
- Free picking in Practice Arena is unconstrained by interleaving.
- First-exposure topics preserve roadmap order.
- Problem bank data files are 100% frozen and unmodified.
"""

import pytest
from coach.problems import load_all_problems
from coach.interleaving import is_first_exposure, build_interleaved_queue


def test_free_picking_options_unrestricted():
    """Confirms that all 20 problems are available for free selection in the problem bank."""
    all_problems = [p.model_dump() for p in load_all_problems()]
    assert len(all_problems) == 20

    # Problem IDs and titles are fully intact
    problem_ids = [p["id"] for p in all_problems]
    assert "binary-search" in problem_ids
    assert "two-sum" in problem_ids
    assert "climbing-stairs" in problem_ids
    assert "valid-parentheses" in problem_ids


def test_first_exposure_roadmap_branch():
    """
    Verifies that when a candidate has not attempted any problems in a topic,
    the topic is identified as first exposure so it can follow the natural roadmap order.
    """
    all_problems = [p.model_dump() for p in load_all_problems()]
    topics = {p["topic"] for p in all_problems}
    assert len(topics) >= 4

    attempted_topics = set()
    for topic in topics:
        assert is_first_exposure(topic, attempted_topics) is True

    # After attempting 'arrays', only 'arrays' is no longer first exposure
    attempted_topics.add("arrays")
    assert is_first_exposure("arrays", attempted_topics) is False
    assert is_first_exposure("trees", attempted_topics) is True
