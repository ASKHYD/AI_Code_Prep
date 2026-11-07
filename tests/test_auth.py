"""
Unit tests for auth_store.py — Functional authentication & security.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from auth_store import (
    AuthStore,
    hash_password,
    verify_password,
    hash_token,
    init_auth_db,
    get_db_connection,
)


@pytest.fixture
def auth_store(tmp_path: Path):
    db_file = tmp_path / "test_auth.db"
    return AuthStore(db_path=db_file)


def test_password_hashing_and_salt_uniqueness():
    pwd = "SecretPassword123!"
    h1, s1 = hash_password(pwd)
    h2, s2 = hash_password(pwd)
    assert s1 != s2, "Salts must be randomly generated per hash"
    assert h1 != h2, "Hashes with distinct salts must differ"
    assert verify_password(pwd, s1, h1) is True
    assert verify_password("WrongPassword!", s1, h1) is False


def test_create_pending_profile_and_status(auth_store: AuthStore):
    ok, token, msg = auth_store.create_pending_profile("owner@example.com", "CorrectHorseBattery99")
    assert ok is True
    assert len(token) > 20
    assert "pending" in msg.lower()

    profile = auth_store.get_profile()
    assert profile is not None
    assert profile["email"] == "owner@example.com"
    assert profile["status"] == "pending"
    assert profile["verify_token_hash"] == hash_token(token)


def test_authenticate_pending_rejection(auth_store: AuthStore):
    auth_store.create_pending_profile("owner@example.com", "CorrectHorseBattery99")
    ok, reason, prof = auth_store.authenticate_user("owner@example.com", "CorrectHorseBattery99")
    assert ok is False
    assert reason == "pending"


def test_verify_email_token_activation(auth_store: AuthStore):
    ok, token, _ = auth_store.create_pending_profile("owner@example.com", "CorrectHorseBattery99")
    v_ok, v_msg = auth_store.verify_email_token(token)
    assert v_ok is True
    assert "confirmed" in v_msg.lower()

    # Authenticate should now succeed
    auth_ok, reason, prof = auth_store.authenticate_user("owner@example.com", "CorrectHorseBattery99")
    assert auth_ok is True
    assert reason == "ok"
    assert prof["status"] == "active"


def test_expired_verification_token_rejected(auth_store: AuthStore):
    ok, token, _ = auth_store.create_pending_profile("owner@example.com", "CorrectHorseBattery99")
    # Manually expire token in DB
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    with get_db_connection(auth_store.db_path) as conn:
        conn.execute("UPDATE user_profile SET verify_expires_at = ?", (past_iso,))
        conn.commit()

    v_ok, v_msg = auth_store.verify_email_token(token)
    assert v_ok is False
    assert "expired" in v_msg.lower()


def test_resend_verification_mints_fresh_token(auth_store: AuthStore):
    ok, token1, _ = auth_store.create_pending_profile("owner@example.com", "CorrectHorseBattery99")
    r_ok, token2, r_msg = auth_store.resend_verification("owner@example.com")
    assert r_ok is True
    assert token1 != token2

    # Old token fails, new token activates
    v1_ok, _ = auth_store.verify_email_token(token1)
    assert v1_ok is False
    v2_ok, _ = auth_store.verify_email_token(token2)
    assert v2_ok is True


def test_password_reset_flow(auth_store: AuthStore):
    ok, token, _ = auth_store.create_pending_profile("owner@example.com", "InitialPassword123")
    auth_store.verify_email_token(token)

    req_ok, reset_token, _ = auth_store.request_password_reset("owner@example.com")
    assert req_ok is True
    assert len(reset_token) > 20

    reset_ok, msg = auth_store.reset_password(reset_token, "BrandNewPassword456!")
    assert reset_ok is True

    # Old password fails, new password succeeds
    ok_old, _, _ = auth_store.authenticate_user("owner@example.com", "InitialPassword123")
    assert ok_old is False
    ok_new, _, _ = auth_store.authenticate_user("owner@example.com", "BrandNewPassword456!")
    assert ok_new is True
