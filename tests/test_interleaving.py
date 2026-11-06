"""
Unit tests for cognitive interleaving queue generator (coach/interleaving.py).
Verifies Task 3.1 requirements:
- No two same-topic problems appear consecutively when an alternative exists.
- Topic prioritization: higher due counts first, weaker topics (lowest pass rate) first.
- Tail fallback when only single topic remains.
"""

import pytest
from coach.interleaving import build_interleaved_queue, is_first_exposure


def test_interleaving_multi_topic_no_adjacent_neighbors():
    """Prove that multi-topic queues never place same-topic problems adjacently when alternatives exist."""
    problems = [
        {"id": "a1", "topic": "arrays", "title": "Array 1"},
        {"id": "a2", "topic": "arrays", "title": "Array 2"},
        {"id": "a3", "topic": "arrays", "title": "Array 3"},
        {"id": "t1", "topic": "trees", "title": "Tree 1"},
        {"id": "t2", "topic": "trees", "title": "Tree 2"},
        {"id": "s1", "topic": "strings", "title": "String 1"},
        {"id": "s2", "topic": "strings", "title": "String 2"},
    ]

    stats = {
        "arrays": {"pass_rate": 50.0},
        "trees": {"pass_rate": 75.0},
        "strings": {"pass_rate": 80.0},
    }

    queue = build_interleaved_queue(problems, topic_stats=stats)
    assert len(queue) == len(problems)

    # Check for no adjacent same topics
    for i in range(1, len(queue)):
        prev_topic = queue[i - 1]["topic"]
        curr_topic = queue[i]["topic"]
        # Can only be same topic if no other topics had remaining items at this point
        if prev_topic == curr_topic:
            # All other topics must have been exhausted
            remaining_other = [p for p in queue[i:] if p["topic"] != curr_topic]
            assert len(remaining_other) == 0, f"Adjacent duplicate topic '{curr_topic}' at index {i} while alternatives exist!"


def test_interleaving_weakest_topic_prioritized():
    """Weakest topic problems are scheduled ahead of stronger topics when counts are equal."""
    problems = [
        {"id": "t1", "topic": "trees", "title": "Tree 1"},
        {"id": "a1", "topic": "arrays", "title": "Array 1"},
        {"id": "s1", "topic": "strings", "title": "String 1"},
    ]

    # Arrays pass rate 20% (weakest), Strings 60%, Trees 90% (strongest)
    stats = {
        "arrays": {"pass_rate": 20.0},
        "strings": {"pass_rate": 60.0},
        "trees": {"pass_rate": 90.0},
    }

    queue = build_interleaved_queue(problems, topic_stats=stats)
    assert queue[0]["topic"] == "arrays", "Weakest topic should be scheduled first!"


def test_interleaving_edge_cases():
    """Tests empty, single-item, and single-topic queues."""
    assert build_interleaved_queue([]) == []

    single = [{"id": "a1", "topic": "arrays"}]
    assert build_interleaved_queue(single) == single

    all_same = [
        {"id": "a1", "topic": "arrays"},
        {"id": "a2", "topic": "arrays"},
        {"id": "a3", "topic": "arrays"},
    ]
    # When no alternatives exist, all items must still be returned
    assert len(build_interleaved_queue(all_same)) == 3


def test_first_exposure_detection():
    """Verifies that is_first_exposure accurately detects unattempted topics."""
    attempted = {"arrays", "strings"}
    assert is_first_exposure("trees", attempted) is True
    assert is_first_exposure("arrays", attempted) is False

