"""
Local AI Hint and Review Engine via Ollama.
Zero-cost, local-only client.
Falls back safely to stored hints when Ollama is offline or unavailable.
"""

from __future__ import annotations

from typing import Any


def explain_hint(problem: dict[str, Any], user_code: str, hint_level: int = 1) -> str:
    """
    Explains the stored hint at requested level (1, 2, or 3) using local Ollama.
    Never invents new hints; elaborates only on stored problem hints.
    Degrades to stored hint string if Ollama is unreachable.
    """
    hints = problem.get("hints", [])
    idx = max(0, min(hint_level - 1, len(hints) - 1)) if hints else 0
    stored_hint = hints[idx] if hints else "No hint available for this problem."

    # Offline / pending fallback string
    fallback_msg = f"Local AI is off — here is the stored hint:\n{stored_hint}"

    try:
        import ollama
        client = ollama.Client(timeout=2.0)
        prompt = (
            f"You are a coding interview coach. Explain this hint for '{problem.get('title', '')}' "
            f"to the candidate without giving away the full solution code.\n\n"
            f"Stored Hint (Level {hint_level}): {stored_hint}\n\n"
            f"Candidate's current code:\n```python\n{user_code}\n```\n\n"
            f"Provide a brief, encouraging, 2-3 sentence conceptual explanation."
        )
        response = client.chat(
            model="qwen2.5-coder:3b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        content = response["message"]["content"].strip()
        return f"💡 **Coach Hint (Level {hint_level})**:\n{content}" if content else fallback_msg
    except Exception:
        return fallback_msg


def review_code(problem: dict[str, Any], user_code: str) -> str:
    """
    Provides conceptual code review suggestions after a solution passes.
    Degrades gracefully if Ollama is unreachable.
    """
    fallback_msg = "Local AI is off — AI code review unavailable."

    try:
        import ollama
        client = ollama.Client(timeout=2.0)
        prompt = (
            f"You are a technical interview code reviewer. The candidate's solution for '{problem.get('title', '')}' "
            f"passed all tests.\n\n"
            f"Candidate's solution:\n```python\n{user_code}\n```\n\n"
            f"In 3 concise bullet points, discuss time complexity, space complexity, and any pythonic improvement."
        )
        response = client.chat(
            model="qwen2.5-coder:3b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        content = response["message"]["content"].strip()
        return content if content else fallback_msg
    except Exception:
        return fallback_msg
