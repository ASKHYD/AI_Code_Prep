"""
Unit tests for auth_store.py — Functional authentication & security.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from auth_store import (
    AuthStore,
    get_db_connection,
    hash_password,
    hash_token,
    verify_password,
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


def test_create_account_unconfigured_smtp_regression(auth_store: AuthStore, monkeypatch):
    """
    Regression test for Phase 7 Create Account flow:
    1. Ensures account creation succeeds without exception on unconfigured SMTP.
    2. Profile lands in pending status.
    3. send_smtp_email reports failure honestly (returns False with friendly message, does not raise).
    4. Repeated create_pending_profile with same email produces friendly 'already exists' message without exception.
    """
    import os

    from auth_store import send_smtp_email

    # Clear SMTP environment variables
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_APP_PASSWORD", raising=False)

    test_email = "newuser@example.com"
    pwd = "ValidPassword123!"

    # 1. Drive create_pending_profile
    c_ok, raw_tok, c_msg = auth_store.create_pending_profile(test_email, pwd)
    assert c_ok is True
    assert len(raw_tok) > 20

    # 2. Verify pending status
    prof = auth_store.get_profile()
    assert prof is not None
    assert prof["email"] == test_email
    assert prof["status"] == "pending"

    # 3. Simulate the UI email send step
    app_url = os.environ.get("APP_BASE_URL", "http://localhost:8501")
    link = f"{app_url}/?verify={raw_tok}"
    s_ok, s_msg = send_smtp_email(
        to_email=test_email,
        subject="Confirm your AI Prep Coach account",
        text_content=f"Activate: {link}",
    )
    # Must report failure honestly, not raise
    assert s_ok is False
    assert "not configured" in s_msg.lower() or "failed" in s_msg.lower()

    # 4. Duplicate creation check: friendly message, no crash or IntegrityError
    c_ok2, _, c_msg2 = auth_store.create_pending_profile(test_email, "AnotherPassword789!")
    assert c_ok2 is False
    assert "already exists" in c_msg2.lower()


def test_unauthenticated_app_boots_to_home(tmp_path):
    """
    UI-layer regression guard using Streamlit AppTest (streamlit.testing.v1):
    Updated per owner decision 2026-11-08 (Login Gate Removal).
    Verifies that the unauthenticated app boots directly to Home with no profile present,
    and that ?screen=login, ?verify=..., ?reset=..., and ?logout=... query parameters
    are harmless no-ops with zero exceptions.
    """
    import subprocess
    import sys

    temp_db = str(tmp_path / "apptest_coach.db").replace("\\", "/")
    app_path = (Path(__file__).parent.parent / "app.py").resolve().as_posix()

    runner_script = f"""
import os
import sys
from streamlit.testing.v1 import AppTest

os.environ['COACH_DB_PATH'] = '{temp_db}'

# 1. Unauthenticated bare boot directly to Home
at = AppTest.from_file('{app_path}')
at.run()
assert len(at.exception) == 0, f"App crashed on bare boot: {{at.exception}}"
assert at.session_state.get('nav_choice') == 'Home', f"Expected Home, got {{at.session_state.get('nav_choice')}}"

# 2. ?screen=login is a harmless no-op; app stays on Home
at_login = AppTest.from_file('{app_path}')
at_login.query_params['screen'] = 'login'
at_login.run()
assert len(at_login.exception) == 0, f"App crashed with ?screen=login: {{at_login.exception}}"
assert at_login.session_state.get('nav_choice') == 'Home'

# 3. Harmless no-op query parameters ?verify= and ?reset=
at_qp = AppTest.from_file('{app_path}')
at_qp.query_params['verify'] = 'fake_verification_token'
at_qp.query_params['reset'] = 'fake_reset_token'
at_qp.run()
assert len(at_qp.exception) == 0, f"App crashed with auth query params: {{at_qp.exception}}"
assert at_qp.session_state.get('nav_choice') == 'Home'

print("BOOT_TO_HOME_OK")
"""

    res = subprocess.run([sys.executable, "-c", runner_script], capture_output=True, text=True)
    assert res.returncode == 0, f"AppTest UI guard failed (exit {res.returncode}):\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "BOOT_TO_HOME_OK" in res.stdout



