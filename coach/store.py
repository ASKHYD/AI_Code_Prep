"""
SQLite Persistence Store for Candidate Attempts and Spaced Repetition.
Zero-cost, Python standard library sqlite3 only.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from typing import Any

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
