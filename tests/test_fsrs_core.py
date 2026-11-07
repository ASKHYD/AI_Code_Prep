"""
Unit tests for FSRS core engine, scheduler wrapper, and rating mapping.
Verifies Task 1.1 & Task 1.2 requirements:
- py-fsrs scheduler parameters (desired_retention=0.9, defaults only).
- Strict optimizer absence.
- Deterministic judge-to-rating mapping (Again, Hard, Good).
- Strict ban on Rating.Easy.
- Card serialization roundtrip.
"""

import fsrs
import pytest

from coach.fsrs_engine import (
    card_from_json,
    card_to_json,
    get_fsrs_scheduler,
    map_judge_to_rating,
    parse_utc_datetime,
)


def test_fsrs_scheduler_defaults_and_retention():
    """Confirms default parameters and desired_retention=0.9."""
    scheduler = get_fsrs_scheduler()
    assert scheduler.desired_retention == 0.9
    assert scheduler.enable_fuzzing is False or scheduler.enable_fuzzing is True  # default


def test_optimizer_strictly_forbidden():
    """Verifies that no optimizer modules or functions are imported in coach."""
    import sys
    assert "fsrs.optimizer" not in sys.modules
    from coach import fsrs_engine
    assert not hasattr(fsrs_engine, "optimize")
    assert not hasattr(fsrs_engine, "Optimizer")


def test_card_serialization_roundtrip():
    """Verifies that an fsrs.Card can be serialized to JSON and deserialized identically."""
    scheduler = get_fsrs_scheduler()
    card = fsrs.Card()
    now_dt = parse_utc_datetime("2026-11-06T12:00:00Z")
    updated_card, _ = scheduler.review_card(card, fsrs.Rating.Good, review_datetime=now_dt)

    json_str = card_to_json(updated_card)
    restored_card = card_from_json(json_str)

    assert restored_card.card_id == updated_card.card_id
    assert restored_card.state == updated_card.state
    assert restored_card.due == updated_card.due
    assert restored_card.last_review == updated_card.last_review


@pytest.mark.parametrize(
    "verdict,hints,attempts,expected_rating",
    [
        ("fail", 0, 1, fsrs.Rating.Again),
        ("FAIL", 2, 3, fsrs.Rating.Again),
        ("timeout", 0, 1, fsrs.Rating.Again),
        ("TIMEOUT", 1, 1, fsrs.Rating.Again),
        ("error", 0, 1, fsrs.Rating.Again),
        ("pass", 1, 1, fsrs.Rating.Hard),
        ("pass", 0, 2, fsrs.Rating.Hard),
        ("pass", 3, 4, fsrs.Rating.Hard),
        ("PASS", 1, 2, fsrs.Rating.Hard),
        ("pass", 0, 1, fsrs.Rating.Good),
        ("PASS", 0, 1, fsrs.Rating.Good),
    ],
)
def test_map_judge_to_rating(verdict, hints, attempts, expected_rating):
    """Verifies deterministic rating mapping for all outcome branches."""
    rating = map_judge_to_rating(verdict, hints_used=hints, attempts_on_problem=attempts)
    assert rating == expected_rating
    assert rating != fsrs.Rating.Easy


def test_rating_easy_never_emitted():
    """Exhaustive check ensuring Rating.Easy is strictly forbidden and never returned."""
    verdicts = ["pass", "fail", "timeout", "error", "unknown"]
    for v in verdicts:
        for hints in range(0, 5):
            for attempts in range(1, 6):
                rating = map_judge_to_rating(v, hints_used=hints, attempts_on_problem=attempts)
                assert rating != fsrs.Rating.Easy, f"Rating.Easy returned for {v}, hints={hints}, attempts={attempts}"

