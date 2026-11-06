"""
FSRS Engine Wrapper for AI Coding Prep Coach.
Provides adaptive spaced repetition using py-fsrs (default parameters, desired_retention=0.9).
Optimizer is strictly forbidden per Milestone 2 specifications.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import fsrs


def get_fsrs_scheduler() -> fsrs.Scheduler:
    """
    Returns an FSRS Scheduler configured with default parameters
    and desired_retention = 0.9.
    The FSRS optimizer is strictly forbidden in this phase.
    """
    return fsrs.Scheduler(desired_retention=0.9)


def parse_utc_datetime(val: str | datetime | None = None) -> datetime:
    """
    Normalizes a string or datetime into a UTC-aware datetime required by py-fsrs.
    If val is None, returns current UTC time.
    """
    if val is None:
        return datetime.now(timezone.utc)
    if isinstance(val, str):
        # Handle trailing 'Z' if present
        clean_val = val.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(clean_val)
        except ValueError:
            dt = datetime.strptime(val, "%Y-%m-%d")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)
    raise TypeError(f"Cannot parse datetime from type {type(val)}")


def card_to_json(card: fsrs.Card) -> str:
    """Serializes an fsrs.Card instance to a JSON string."""
    return card.to_json()


def card_from_json(json_str: str) -> fsrs.Card:
    """Deserializes an fsrs.Card instance from a JSON string."""
    return fsrs.Card.from_json(json_str)


def map_judge_to_rating(
    verdict: str,
    hints_used: int = 0,
    attempts_on_problem: int = 1,
) -> fsrs.Rating:
    """
    Deterministic judge metadata to FSRS Rating mapping.
    Binding rules:
    - FAIL, TIMEOUT, ERROR -> Rating.Again (1)
    - PASS with hints_used > 0 OR attempts_on_problem > 1 -> Rating.Hard (2)
    - Clean first-attempt PASS with no hints -> Rating.Good (3)
    - Rating.Easy (4) is STRICTLY FORBIDDEN and never emitted in this phase.
    """
    v = verdict.strip().lower()
    if v in ("fail", "timeout", "error"):
        rating = fsrs.Rating.Again
    elif v == "pass":
        if hints_used > 0 or attempts_on_problem > 1:
            rating = fsrs.Rating.Hard
        else:
            rating = fsrs.Rating.Good
    else:
        # Default safety fallback
        rating = fsrs.Rating.Again

    # Enforce binding ban on Rating.Easy
    if rating == fsrs.Rating.Easy:
        raise ValueError("Rating.Easy is strictly forbidden in Milestone 2 Phase 3.")

    return rating

