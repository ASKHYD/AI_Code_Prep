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
    due_problems: list[dict[str, Any]] | list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Reorders a list of problems so that no two problems of the same topic appear adjacently,
    whenever an alternative topic exists.

    Corrective C3 (Due-First Interleaving):
    - When due_problems is provided (e.g. from store.due_problems()), due problems are
      placed first, ordered among themselves by due timestamp (earliest due first).
    - Remaining problems follow the depth-then-weakness topic interleaving.
    - The no-same-topic-adjacency invariant holds across the seam: the interleaver initializes
      last_topic to the final due problem's topic, excluding that topic from the first remaining pick.
    """
    if not problems:
        return []

    # 1. Separate due problems (if provided) from remaining problems
    interleaved: list[dict[str, Any]] = []
    seen_due_ids: set[str] = set()

    if due_problems:
        prob_map: dict[str, dict[str, Any]] = {}
        for p in problems:
            pid = p.get("id") if isinstance(p, dict) else getattr(p, "id", None)
            if pid:
                prob_map[pid] = p

        # Order due problems by due timestamp (earliest due first)
        sorted_due = sorted(
            due_problems,
            key=lambda x: str(x.get("due", "")) if isinstance(x, dict) else ""
        )
        for item in sorted_due:
            pid = item.get("problem_id", "") if isinstance(item, dict) else str(item)
            if pid in prob_map and pid not in seen_due_ids:
                interleaved.append(prob_map[pid])
                seen_due_ids.add(pid)

    remaining_problems = [
        p for p in problems
        if (p.get("id") if isinstance(p, dict) else getattr(p, "id", None)) not in seen_due_ids
    ]

    if not remaining_problems:
        return interleaved

    if not interleaved and len(remaining_problems) <= 2:
        return list(remaining_problems)

    # 2. Bucket remaining problems by topic
    topic_buckets: dict[str, list[dict[str, Any]]] = {}
    for p in remaining_problems:
        if isinstance(p, dict):
            t = p.get("topic", "general")
        else:
            t = getattr(p, "topic", "general")
        topic_buckets.setdefault(t, []).append(p)

    stats = topic_stats or {}
    all_topics = list(topic_buckets.keys())

    # 3. Interleaving selection loop (maintaining seam invariant from last due problem)
    last_topic: str | None = None
    if interleaved:
        last_item = interleaved[-1]
        last_topic = last_item.get("topic") if isinstance(last_item, dict) else getattr(last_item, "topic", None)

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
