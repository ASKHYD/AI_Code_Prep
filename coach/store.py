"""
SQLite Persistence Store for Candidate Attempts and Spaced Repetition.
Zero-cost, Python standard library sqlite3 only.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone
from typing import Any

import fsrs
from coach.fsrs_engine import (
    card_from_json,
    card_to_json,
    get_fsrs_scheduler,
    map_judge_to_rating,
    parse_utc_datetime,
)
from coach.repetition import calculate_due_date


class CoachStore:
    def __init__(self, db_path: str = "coach.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id TEXT NOT NULL,
                    topic TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    runtime_ms INTEGER NOT NULL DEFAULT 0,
                    hints_used INTEGER NOT NULL DEFAULT 0,
                    mode TEXT NOT NULL DEFAULT 'practice',
                    attempt_date TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS problem_reviews (
                    problem_id TEXT PRIMARY KEY,
                    consecutive_passes INTEGER NOT NULL DEFAULT 0,
                    last_status TEXT NOT NULL,
                    next_due_date TEXT NOT NULL,
                    last_attempt_date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS problem_fsrs_cards (
                    problem_id TEXT PRIMARY KEY,
                    card_json TEXT NOT NULL,
                    due TEXT NOT NULL,
                    state INTEGER NOT NULL,
                    last_review TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def record_attempt(
        self,
        problem_id: str,
        status: str,
        runtime_ms: int = 0,
        hints_used: int = 0,
        mode: str = "practice",
        topic: str = "",
        attempt_date: str | None = None
    ) -> int:
        """Records an attempt and updates the repetition schedule."""
        iso_today = attempt_date or date.today().isoformat()
        now_ts = datetime.now().isoformat()

        with self._get_connection() as conn:
            # 1. Fetch current consecutive passes for this problem
            cur = conn.execute(
                "SELECT consecutive_passes FROM problem_reviews WHERE problem_id = ?",
                (problem_id,)
            )
            row = cur.fetchone()
            current_passes = row["consecutive_passes"] if row else 0

            # 2. Compute updated schedule
            next_passes, next_due = calculate_due_date(current_passes, status, from_date=iso_today)

            # 3. Insert attempt record
            cur = conn.execute(
                """
                INSERT INTO attempts (problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (problem_id, topic, status.lower(), runtime_ms, hints_used, mode, iso_today, now_ts)
            )
            attempt_id = cur.lastrowid

            # 4. Upsert problem review record
            conn.execute(
                """
                INSERT INTO problem_reviews (problem_id, consecutive_passes, last_status, next_due_date, last_attempt_date)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(problem_id) DO UPDATE SET
                    consecutive_passes = excluded.consecutive_passes,
                    last_status = excluded.last_status,
                    next_due_date = excluded.next_due_date,
                    last_attempt_date = excluded.last_attempt_date
                """,
                (problem_id, next_passes, status.lower(), next_due, iso_today)
            )
            conn.commit()
            return attempt_id

    def due_problems(self, today: str | None = None) -> list[dict[str, Any]]:
        """Returns problems due on or before `today` (YYYY-MM-DD)."""
        target_date = today or date.today().isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT problem_id, consecutive_passes, last_status, next_due_date, last_attempt_date
                FROM problem_reviews
                WHERE next_due_date <= ?
                ORDER BY next_due_date ASC
                """,
                (target_date,)
            )
            return [dict(row) for row in cur.fetchall()]

    def topic_stats(self) -> dict[str, dict[str, Any]]:
        """Returns aggregate attempts and pass rates by topic."""
        with self._get_connection() as conn:
            cur = conn.execute("""
                SELECT
                    topic,
                    COUNT(*) as total_attempts,
                    SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed_attempts
                FROM attempts
                WHERE topic != ''
                GROUP BY topic
            """)
            stats = {}
            for row in cur.fetchall():
                topic = row["topic"]
                attempts = row["total_attempts"]
                passed = row["passed_attempts"] or 0
                pass_rate = round((passed / attempts) * 100.0, 1) if attempts > 0 else 0.0
                stats[topic] = {
                    "attempts": attempts,
                    "passed": passed,
                    "pass_rate": pass_rate
                }
            return stats

    def current_streak(self, today: str | None = None) -> int:
        """Calculates current consecutive days with at least 1 attempt leading to today."""
        curr = datetime.strptime(today, "%Y-%m-%d").date() if today else date.today()
        streak = 0

        with self._get_connection() as conn:
            cur = conn.execute("SELECT DISTINCT attempt_date FROM attempts ORDER BY attempt_date DESC")
            attempt_dates = {row["attempt_date"] for row in cur.fetchall()}

        # Count backwards from curr
        while curr.isoformat() in attempt_dates:
            streak += 1
            curr -= timedelta(days=1)

        return streak

    def get_recent_attempts(self, limit: int = 15) -> list[dict[str, Any]]:
        """Returns recent attempt history."""
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at
                FROM attempts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [dict(row) for row in cur.fetchall()]

    def get_fsrs_card(self, problem_id: str) -> fsrs.Card | None:
        """Fetches the serialized FSRS Card for a problem, or None if not found."""
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT card_json FROM problem_fsrs_cards WHERE problem_id = ?",
                (problem_id,)
            )
            row = cur.fetchone()
            if row:
                return card_from_json(row["card_json"])
        return None

    def save_fsrs_card(self, problem_id: str, card: fsrs.Card) -> None:
        """Upserts an FSRS Card into problem_fsrs_cards."""
        card_json = card_to_json(card)
        due_iso = card.due.isoformat()
        state_val = int(card.state)
        last_rev_iso = card.last_review.isoformat() if card.last_review else None
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO problem_fsrs_cards (problem_id, card_json, due, state, last_review, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(problem_id) DO UPDATE SET
                    card_json = excluded.card_json,
                    due = excluded.due,
                    state = excluded.state,
                    last_review = excluded.last_review,
                    updated_at = excluded.updated_at
                """,
                (problem_id, card_json, due_iso, state_val, last_rev_iso, now_iso)
            )
            conn.commit()

    def migrate_history_to_fsrs(self) -> dict[str, int]:
        """
        Idempotent migration: seeds FSRS cards from historical attempts in `attempts`.
        For each problem with attempt history:
          - Fetches the most recent attempt for that problem (status, created_at, hints_used).
          - Per Milo Audit Correction A1: Seeds a new fsrs.Card() and records the initial review
            strictly using the problem's LAST ATTEMPT TIMESTAMP (created_at), NOT migration time.
          - If last attempt was a pass: reviews with Rating.Good at last_attempt_ts.
          - If last attempt was fail/timeout/error: reviews with Rating.Again at last_attempt_ts.
          - Saves card to problem_fsrs_cards.
        Idempotency: If a problem already has a card in problem_fsrs_cards, it is skipped.
        Assertion: The `attempts` table is 100% UNTOUCHED (0 writes).
        Returns: {"migrated": count, "skipped": count}
        """
        scheduler = get_fsrs_scheduler()
        migrated = 0
        skipped = 0

        with self._get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) as cnt FROM attempts")
            attempts_count_before = cur.fetchone()["cnt"]

            cur = conn.execute("SELECT DISTINCT problem_id FROM attempts")
            problem_ids = [row["problem_id"] for row in cur.fetchall()]

            for pid in problem_ids:
                chk = conn.execute("SELECT 1 FROM problem_fsrs_cards WHERE problem_id = ?", (pid,)).fetchone()
                if chk:
                    skipped += 1
                    continue

                att_cur = conn.execute(
                    """
                    SELECT status, created_at, hints_used
                    FROM attempts
                    WHERE problem_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1
                    """,
                    (pid,)
                )
                last_attempt = att_cur.fetchone()
                if not last_attempt:
                    continue

                status = last_attempt["status"]
                created_at = last_attempt["created_at"]
                review_dt = parse_utc_datetime(created_at)

                if status.lower() == "pass":
                    rating = fsrs.Rating.Good
                else:
                    rating = fsrs.Rating.Again

                card = fsrs.Card()
                updated_card, _ = scheduler.review_card(card, rating, review_datetime=review_dt)

                card_json = card_to_json(updated_card)
                due_iso = updated_card.due.isoformat()
                state_val = int(updated_card.state)
                last_rev_iso = updated_card.last_review.isoformat() if updated_card.last_review else None
                now_iso = datetime.now(timezone.utc).isoformat()

                conn.execute(
                    """
                    INSERT INTO problem_fsrs_cards (problem_id, card_json, due, state, last_review, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (pid, card_json, due_iso, state_val, last_rev_iso, now_iso)
                )
                migrated += 1

            conn.commit()

            cur = conn.execute("SELECT COUNT(*) as cnt FROM attempts")
            attempts_count_after = cur.fetchone()["cnt"]
            assert attempts_count_before == attempts_count_after, "Invariant violation: attempts table mutated during migration!"

        return {"migrated": migrated, "skipped": skipped}
