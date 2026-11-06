"""
Cognitive Interleaving Engine for AI Coding Prep Coach.
Milestone 2 Phase 3: Workstream 2.

Ensures that app-generated problem queues (Home daily review queue and mock interview selection)
never place two problems of the same topic consecutively when an alternative topic is available.
Topics are sampled weighted by due-ness first (remaining count), then by weakest topic (pass rate).
Free picking in the Practice Arena remains completely unrestricted.
"""

from __future__ import annotations
from typing import Any


def is_first_exposure(topic: str, attempted_topics: set[str] | list[str]) -> bool:
    """
    Returns True if the topic has never been attempted before (zero previous attempts).
    Brand-new topics may be introduced in roadmap/curriculum order.
    """
    return topic not in attempted_topics


def build_interleaved_queue(
    problems: list[dict[str, Any]],
    topic_stats: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Reorders a list of problems so that no two problems of the same topic appear adjacently,
    whenever an alternative topic exists.

    Ranking:
    1. Topic due-ness / frequency (topics with more problems get prioritized to avoid starvation).
    2. Weakest topic pass rate (lowest pass rate from topic_stats is prioritized).
    """
    if not problems or len(problems) <= 2:
        return list(problems)

    # 1. Bucket problems by topic
    topic_buckets: dict[str, list[dict[str, Any]]] = {}
    for p in problems:
        if isinstance(p, dict):
            t = p.get("topic", "general")
        else:
            t = getattr(p, "topic", "general")
        topic_buckets.setdefault(t, []).append(p)

    stats = topic_stats or {}
    all_topics = list(topic_buckets.keys())

    # 2. Interleaving selection loop
    interleaved: list[dict[str, Any]] = []
    last_topic: str | None = None

    while any(len(b) > 0 for b in topic_buckets.values()):
        # Find available topics that are NOT the last_topic
        candidates = [t for t in all_topics if t != last_topic and len(topic_buckets[t]) > 0]

        if candidates:
            # Re-rank candidate topics by current remaining count (desc) and pass rate (asc -> weaker first)
            candidates.sort(
                key=lambda t: (-len(topic_buckets[t]), stats.get(t, {}).get("pass_rate", 100.0))
            )
            chosen_topic = candidates[0]
        else:
            # Only the last_topic has remaining items (or no other options exist)
            remaining_topics = [t for t in all_topics if len(topic_buckets[t]) > 0]
            if not remaining_topics:
                break
            chosen_topic = max(remaining_topics, key=lambda t: len(topic_buckets[t]))

        item = topic_buckets[chosen_topic].pop(0)
        interleaved.append(item)
        last_topic = chosen_topic

    return interleaved
