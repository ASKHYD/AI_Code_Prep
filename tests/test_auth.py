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


def test_create_account_apptest_ui_guard(tmp_path):
    """
    UI-layer regression guard using Streamlit AppTest (streamlit.testing.v1):
    Drives the unauthenticated app up to the login view, switches to Create Account,
    and submits the form in an isolated process (preventing layout pollution from test_mock_session_scoping).
    Verifies that the exact path in app.py (including os.environ access) executes without throwing
    NameError or any unhandled exception, displaying the honest unconfigured SMTP warning.
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
os.environ.pop('SMTP_USER', None)
os.environ.pop('SMTP_APP_PASSWORD', None)

at = AppTest.from_file('{app_path}')
at.query_params['screen'] = 'login'
at.run()
assert len(at.exception) == 0, f"App crashed on login view: {{at.exception}}"

at.radio[0].set_value('Create Account').run()
assert len(at.exception) == 0, f"App crashed on radio switch: {{at.exception}}"

at.text_input[0].input('ui_test_user@example.com')
at.text_input[1].input('ValidPass1234!')
at.button[0].click().run()

assert len(at.exception) == 0, f"App crashed on submit: {{at.exception}}"
assert len(at.warning) > 0, "Expected warning for unconfigured SMTP"
assert "pending" in at.warning[0].value.lower() or "smtp credentials" in at.warning[0].value.lower()
print("APPTEST_OK")
"""

    res = subprocess.run([sys.executable, "-c", runner_script], capture_output=True, text=True)
    assert res.returncode == 0, f"AppTest UI guard failed (exit {res.returncode}):\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "APPTEST_OK" in res.stdout



