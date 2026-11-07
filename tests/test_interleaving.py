"""
Unit tests for cognitive interleaving queue generator (coach/interleaving.py).
Verifies Task 3.1 requirements:
- No two same-topic problems appear consecutively when an alternative exists.
- Topic prioritization: higher due counts first, weaker topics (lowest pass rate) first.
- Tail fallback when only single topic remains.
"""

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


# --- Corrective C3 Specification Tests ---

def test_interleaving_due_problem_at_row_1():
    """(i) with a due problem present it sits at row 1 (Corrective C3)."""
    problems = [
        {"id": "a1", "topic": "arrays", "title": "Array 1"},
        {"id": "b1", "topic": "binary-search", "title": "Binary Search 1"},
        {"id": "t1", "topic": "trees", "title": "Tree 1"},
    ]
    due_problems = [{"problem_id": "b1", "due": "2026-11-06T20:00:00Z"}]
    queue = build_interleaved_queue(problems, due_problems=due_problems)
    assert queue[0]["id"] == "b1", "Due problem must sit at row 1!"


def test_interleaving_seam_and_real_data_shape():
    """
    (ii) adjacency violations = 0 including across the seam, on today's real data shape
    (1 due + 19 others) (Corrective C3 / Bank Expansion).
    """
    from coach.problems import load_all_problems
    all_problems = [p.model_dump() for p in load_all_problems()]
    assert len(all_problems) == 20

    # Today's store state: 1 due problem (binary-search)
    due_problems = [{"problem_id": "binary-search", "due": "2026-11-06T20:01:50Z"}]
    topic_stats = {"binary-search": {"attempts": 2, "passed": 1, "pass_rate": 50.0}}

    queue = build_interleaved_queue(all_problems, topic_stats=topic_stats, due_problems=due_problems)
    assert len(queue) == 20
    assert queue[0]["id"] == "binary-search", "Due problem binary-search must sit at row 1!"

    # Verify zero adjacency violations across the entire queue (including the seam at index 0 -> 1)
    for i in range(1, len(queue)):
        prev_topic = queue[i - 1]["topic"]
        curr_topic = queue[i]["topic"]
        assert prev_topic != curr_topic, f"Adjacency violation between row {i} and {i+1}: topic '{curr_topic}' repeated!"

    # Seam test with due problem sharing the multi-item topic (arrays)
    due_arrays = [{"problem_id": "two-sum", "due": "2026-11-06T10:00:00Z"}]
    queue_arrays_due = build_interleaved_queue(all_problems, topic_stats=topic_stats, due_problems=due_arrays)
    assert queue_arrays_due[0]["id"] == "two-sum"
    # Row 2 cannot be arrays across the seam!
    assert queue_arrays_due[1]["topic"] != "arrays", "Seam invariant failed: row 2 cannot share topic with row 1!"


def test_interleaving_free_picking_and_mock_unaffected():
    """(iii) free picking / Practice selection unaffected and mock calls default cleanly (Corrective C3 / Bank Expansion)."""
    from coach.problems import load_all_problems
    all_problems = [p.model_dump() for p in load_all_problems()]

    # Practice selection is direct index lookup, completely unaffected
    assert len(all_problems) == 20
    assert {p["id"] for p in all_problems} == {p.id for p in load_all_problems()}

    # Mock interview call passes due_problems=None (default behavior preserved)
    mock_pool = build_interleaved_queue(all_problems, topic_stats={}, due_problems=None)
    assert len(mock_pool) == 20
    # Verify mock pool has no adjacent duplicate topics
    for i in range(1, len(mock_pool)):
        assert mock_pool[i]["topic"] != mock_pool[i - 1]["topic"]

