"""
Unit tests for coach/timer.py pure time calculation functions.
"""

from coach.timer import calculate_remaining_time


def test_timer_normal_countdown():
    start = 1000.0
    duration = 45 * 60  # 2700 seconds
    now = 1300.0  # 300 seconds elapsed -> 2400 seconds remaining = 40 min 0 sec

    minutes, seconds, is_expired = calculate_remaining_time(start, duration, now)
    assert minutes == 40
    assert seconds == 0
    assert is_expired is False


def test_timer_with_odd_seconds():
    start = 1000.0
    duration = 2700.0
    now = 1075.0  # 75s elapsed -> 2625s remaining = 43 min 45 sec

    minutes, seconds, is_expired = calculate_remaining_time(start, duration, now)
    assert minutes == 43
    assert seconds == 45
    assert is_expired is False


def test_timer_exact_zero_boundary():
    start = 1000.0
    duration = 2700.0
    now = 3700.0  # Exactly 2700s elapsed -> 0s remaining

    minutes, seconds, is_expired = calculate_remaining_time(start, duration, now)
    assert minutes == 0
    assert seconds == 0
    assert is_expired is True


def test_timer_already_expired():
    start = 1000.0
    duration = 2700.0
    now = 4000.0  # 3000s elapsed -> 300s past expiration

    minutes, seconds, is_expired = calculate_remaining_time(start, duration, now)
    assert minutes == 0
    assert seconds == 0
    assert is_expired is True


def test_timer_clock_skew_now_before_start():
    start = 1000.0
    duration = 2700.0
    now = 990.0  # Clock skew: now < start

    minutes, seconds, is_expired = calculate_remaining_time(start, duration, now)
    assert minutes == 45
    assert seconds == 0
    assert is_expired is False
