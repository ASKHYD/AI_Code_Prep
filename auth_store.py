"""
auth_store.py — Functional authentication and user profile management.

Owns the `user_profile` table in coach.db for the single-user application.
Strictly quarantines auth logic outside coach/*.py to preserve backend freeze.
Security:
- PBKDF2-HMAC-SHA256 with 600,000 iterations and per-profile salt (secrets.token_hex(16)).
- Raw activation/reset tokens are secrets.token_urlsafe(32).
- Only SHA-256 token hashes are stored in SQLite.
- SMTP delivery via standard library smtplib with STARTTLS.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import smtplib
import sqlite3
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path("coach.db")
PBKDF2_ITERATIONS = 600_000
VERIFY_TOKEN_TTL_HOURS = 24
RESET_TOKEN_TTL_HOURS = 1


def _load_env_file() -> None:
    """Loads key-value pairs from .env into os.environ if present without printing credentials."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    try:
        content = env_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# Load local .env on import
_load_env_file()


def get_db_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Connects to SQLite with row factory and WAL mode."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_auth_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Initializes user_profile table in coach.db idempotently without altering existing tables."""
    with get_db_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profile (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                status TEXT NOT NULL,
                verify_token_hash TEXT,
                verify_expires_at TEXT,
                reset_token_hash TEXT,
                reset_expires_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes password with PBKDF2-HMAC-SHA256 using 600,000 iterations and a unique salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return dk.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verifies a password attempt in constant time."""
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return secrets.compare_digest(dk.hex(), expected_hash)


def hash_token(raw_token: str) -> str:
    """Computes SHA-256 digest of a raw token."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class AuthStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = db_path
        init_auth_db(self.db_path)

    def get_profile(self) -> Optional[dict[str, Any]]:
        """Returns the single user profile if one exists."""
        with get_db_connection(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM user_profile LIMIT 1")
            row = cur.fetchone()
            return dict(row) if row else None

    def create_pending_profile(self, email: str, password: str) -> tuple[bool, str, str]:
        """
        Registers a new profile in pending state and mints a 24-hour verification token.
        Returns: (success, raw_token_or_empty, message)
        """
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            return False, "", "A valid email address is required."
        if len(password) < 8:
            return False, "", "Password must be at least 8 characters."

        now_utc = datetime.now(timezone.utc)
        expires_at = (now_utc + timedelta(hours=VERIFY_TOKEN_TTL_HOURS)).isoformat()
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token)
        pwd_hash, salt = hash_password(password)

        with get_db_connection(self.db_path) as conn:
            # Check if any profile already exists (single user application)
            cur = conn.execute("SELECT email, status FROM user_profile WHERE email != ?", (clean_email,))
            existing_other = cur.fetchone()
            if existing_other:
                return False, "", "This installation already has an owner profile configured."

            # Upsert pending record
            conn.execute(
                """
                INSERT INTO user_profile (
                    email, password_hash, salt, status,
                    verify_token_hash, verify_expires_at,
                    reset_token_hash, reset_expires_at, created_at
                ) VALUES (?, ?, ?, 'pending', ?, ?, NULL, NULL, ?)
                ON CONFLICT(email) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    salt = excluded.salt,
                    status = CASE WHEN user_profile.status = 'active' THEN 'active' ELSE 'pending' END,
                    verify_token_hash = excluded.verify_token_hash,
                    verify_expires_at = excluded.verify_expires_at
                """,
                (clean_email, pwd_hash, salt, token_hash, expires_at, now_utc.isoformat()),
            )
            conn.commit()

        return True, raw_token, "Account created in pending verification status."

    def verify_email_token(self, raw_token: str) -> tuple[bool, str]:
        """Validates a raw verification token and activates the profile."""
        if not raw_token:
            return False, "Verification token is missing."

        token_hash = hash_token(raw_token.strip())
        now_utc = datetime.now(timezone.utc)

        with get_db_connection(self.db_path) as conn:
            cur = conn.execute(
                "SELECT email, verify_expires_at, status FROM user_profile WHERE verify_token_hash = ?",
                (token_hash,),
            )
            row = cur.fetchone()
            if not row:
                return False, "Invalid or expired verification token."

            expires_at = datetime.fromisoformat(row["verify_expires_at"])
            if now_utc > expires_at:
                return False, "Verification link has expired. Please request a new confirmation email."

            conn.execute(
                """
                UPDATE user_profile
                SET status = 'active', verify_token_hash = NULL, verify_expires_at = NULL
                WHERE email = ?
                """,
                (row["email"],),
            )
            conn.commit()

        return True, "Email confirmed — you can log in now."

    def authenticate_user(self, email: str, password: str) -> tuple[bool, str, Optional[dict[str, Any]]]:
        """
        Authenticates an email and password.
        Returns (success, reason_code, profile_dict_or_none)
        Reason codes: 'ok', 'not_found', 'pending', 'invalid_password'
        """
        clean_email = email.strip().lower()
        with get_db_connection(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM user_profile WHERE email = ?", (clean_email,))
            row = cur.fetchone()
            if not row:
                return False, "not_found", None

            profile = dict(row)
            if not verify_password(password, profile["salt"], profile["password_hash"]):
                return False, "invalid_password", None

            if profile["status"] == "pending":
                return False, "pending", profile

            return True, "ok", profile

    def resend_verification(self, email: str) -> tuple[bool, str, str]:
        """Mints a fresh 24h verification token and returns (success, raw_token, message)."""
        clean_email = email.strip().lower()
        now_utc = datetime.now(timezone.utc)
        expires_at = (now_utc + timedelta(hours=VERIFY_TOKEN_TTL_HOURS)).isoformat()
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token)

        with get_db_connection(self.db_path) as conn:
            cur = conn.execute("SELECT status FROM user_profile WHERE email = ?", (clean_email,))
            row = cur.fetchone()
            if not row:
                return False, "", "No profile found for this email address."
            if row["status"] == "active":
                return False, "", "This account is already active. Please log in directly."

            conn.execute(
                """
                UPDATE user_profile
                SET verify_token_hash = ?, verify_expires_at = ?
                WHERE email = ?
                """,
                (token_hash, expires_at, clean_email),
            )
            conn.commit()

        return True, raw_token, "Fresh confirmation link minted."

    def request_password_reset(self, email: str) -> tuple[bool, str, str]:
        """Mints a 1-hour password reset token and returns (success, raw_token, message)."""
        clean_email = email.strip().lower()
        now_utc = datetime.now(timezone.utc)
        expires_at = (now_utc + timedelta(hours=RESET_TOKEN_TTL_HOURS)).isoformat()
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token)

        with get_db_connection(self.db_path) as conn:
            cur = conn.execute("SELECT email FROM user_profile WHERE email = ?", (clean_email,))
            row = cur.fetchone()
            if not row:
                return False, "", "No profile found for this email address."

            conn.execute(
                """
                UPDATE user_profile
                SET reset_token_hash = ?, reset_expires_at = ?
                WHERE email = ?
                """,
                (token_hash, expires_at, clean_email),
            )
            conn.commit()

        return True, raw_token, "Password reset token minted."

    def reset_password(self, raw_token: str, new_password: str) -> tuple[bool, str]:
        """Validates reset token and sets new password."""
        if not raw_token:
            return False, "Reset token is missing."
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters."

        token_hash = hash_token(raw_token.strip())
        now_utc = datetime.now(timezone.utc)

        with get_db_connection(self.db_path) as conn:
            cur = conn.execute(
                "SELECT email, reset_expires_at FROM user_profile WHERE reset_token_hash = ?",
                (token_hash,),
            )
            row = cur.fetchone()
            if not row:
                return False, "Invalid or expired reset token."

            expires_at = datetime.fromisoformat(row["reset_expires_at"])
            if now_utc > expires_at:
                return False, "Password reset link has expired. Please request a new one."

            pwd_hash, salt = hash_password(new_password)
            conn.execute(
                """
                UPDATE user_profile
                SET password_hash = ?, salt = ?, reset_token_hash = NULL, reset_expires_at = NULL
                WHERE email = ?
                """,
                (pwd_hash, salt, row["email"]),
            )
            conn.commit()

        return True, "Password has been successfully reset. You can log in now."


def send_smtp_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Sends an email using standard library smtplib with STARTTLS using credentials in os.environ.
    Returns: (success: bool, user_facing_message: str)
    Failure honesty: if SMTP credentials are missing or connection fails, returns False with honest message.
    NEVER logs or prints credentials.
    """
    _load_env_file()
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_APP_PASSWORD", "").strip()

    if not user or not password:
        return False, "SMTP credentials not configured in .env file. Please check your setup."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_email

    part1 = MIMEText(text_content, "plain", "utf-8")
    msg.attach(part1)

    if html_content:
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part2)

    try:
        with smtplib.SMTP(host, port, timeout=12) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())
        return True, "Email delivered successfully."
    except Exception as e:
        err_msg = str(e)
        # Avoid leaking raw exception if it contains secrets
        return False, f"Email delivery failed: {type(e).__name__} ({err_msg[:60]})"
