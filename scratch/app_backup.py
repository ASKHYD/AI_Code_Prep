"""
AI Coding Prep Coach — Streamlit Application (R1 Corrective).
Zero-cost, local-only coding interview preparation platform.
The judge is CODE, not AI.
"""

from __future__ import annotations

import base64
import re
import time
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit as st

from coach.judge import run_solution
from coach.llm_hints import explain_hint, review_code
from coach.problems import load_all_problems
from coach.review import run_ruff_lint
from coach.store import CoachStore
from coach.timer import calculate_remaining_time

# Page configuration
st.set_page_config(
    page_title="AI Coding Prep Coach",
    layout="wide",
    initial_sidebar_state="expanded"
)

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
ICONS_DIR = Path(__file__).parent / "assets" / "icons"

FONT_DEFINITIONS = [
    ("Fraunces", "normal", 500, "fraunces-latin-500-normal.woff2"),
    ("Fraunces", "normal", 600, "fraunces-latin-600-normal.woff2"),
    ("Fraunces", "normal", 700, "fraunces-latin-700-normal.woff2"),
    ("Fraunces", "normal", 800, "fraunces-latin-800-normal.woff2"),
    ("Inter", "normal", 400, "inter-latin-400-normal.woff2"),
    ("Inter", "normal", 500, "inter-latin-500-normal.woff2"),
    ("Inter", "normal", 600, "inter-latin-600-normal.woff2"),
    ("Inter", "normal", 700, "inter-latin-700-normal.woff2"),
    ("JetBrains Mono", "normal", 400, "jetbrains-mono-latin-400-normal.woff2"),
    ("JetBrains Mono", "normal", 500, "jetbrains-mono-latin-500-normal.woff2"),
    ("JetBrains Mono", "normal", 600, "jetbrains-mono-latin-600-normal.woff2"),
    ("JetBrains Mono", "normal", 700, "jetbrains-mono-latin-700-normal.woff2"),
]


NAV_TINTS = {
    "Home": ("#DFF3E4", "#167B48"),
    "Practice Arena": ("#E8E2FF", "#5932EA"),
    "Mock Interview": ("#FFE8D1", "#B93815"),
    "Dashboard": ("#DCEBFF", "#1D5EC2"),
}

nav_options = ["Home", "Practice Arena", "Mock Interview", "Dashboard"]
screen_to_nav = {
    "home": "Home",
    "practice": "Practice Arena",
    "mock": "Mock Interview",
    "dashboard": "Dashboard",
}
nav_to_screen = {v: k for k, v in screen_to_nav.items()}


def get_mock_problem_evaluation(
    problem_id: str,
    session_start_iso: str | None,
    session_state_result: dict[str, Any] | None = None,
    session_hints: int = 0,
    store_instance: Any = None,
) -> dict[str, Any]:
    """
    Evaluates a problem within the strict temporal boundary of the active mock session.
    If no attempt was submitted within the current mock session (since session_start_iso),
    it returns status='not_attempted' with runtime_ms=None and hints_used=session_hints,
    never borrowing historical verdicts, runtimes, or pass/fail states from prior sessions.
    """
    if session_state_result is not None and isinstance(session_state_result, dict):
        status = session_state_result.get("status", "not_attempted")
        return {
            "status": status,
            "runtime_ms": session_state_result.get("runtime_ms"),
            "hints_used": session_hints,
            "is_pass": status == "pass",
            "passed": session_state_result.get("passed", 0),
            "total": session_state_result.get("total", 0),
        }

    if store_instance is not None and session_start_iso:
        try:
            with store_instance._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT status, runtime_ms, hints_used, created_at
                    FROM attempts
                    WHERE problem_id = ? AND mode = 'mock' AND created_at >= ?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (problem_id, session_start_iso)
                )
                row = cur.fetchone()
                if row:
                    return {
                        "status": row["status"],
                        "runtime_ms": row["runtime_ms"],
                        "hints_used": row["hints_used"],
                        "is_pass": row["status"] == "pass",
                        "passed": None,
                        "total": None,
                    }
        except Exception:
            pass

    return {
        "status": "not_attempted",
        "runtime_ms": None,
        "hints_used": session_hints,
        "is_pass": False,
        "passed": 0,
        "total": 0,
    }


def get_global_css(active_nav: str = "Home") -> str:
    """Builds offline base64 @font-face rules and Direction A typography rules."""
    font_faces = []
    for family, style, weight, filename in FONT_DEFINITIONS:
        path = FONTS_DIR / filename
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            font_faces.append(
                f"@font-face {{\n"
                f"  font-family: '{family}';\n"
                f"  font-style: {style};\n"
                f"  font-weight: {weight};\n"
                f"  font-display: swap;\n"
                f"  src: url(data:font/woff2;base64,{encoded}) format('woff2');\n"
                f"}}"
            )

    font_css = "\n".join(font_faces)
    active_bg, active_fg = NAV_TINTS.get(active_nav, ("#DFF3E4", "#167B48"))

    rules_css = """
    /* Body & UI defaults */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        font-family: 'Inter', sans-serif !important;
    }

    /* Display headings in Fraunces */
    h1, h2, h3, h4, .stTitle, .stSubheader, [data-testid="stHeader"],
    h1 *, h2 *, h3 *, h4 *, .stTitle *, .stSubheader * {
        font-family: 'Fraunces', serif !important;
    }

    /* Monospace for code literals, editors, and syntax */
    code, pre, .stCode, code *, pre * {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Direction A Variant B: Metric numerals in Inter SemiBold 600 with tabular figures */
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *, .stat-number, .stat-number * {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-variant-numeric: tabular-nums !important;
        letter-spacing: -0.025em;
    }

    /* Action buttons: Direction A pill geometry and typography */
    button[kind="primary"], .stButton > button {
        border-radius: 999px !important;
        white-space: nowrap !important;
        padding: 10px 24px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    button[kind="primary"] {
        background-color: #15803D !important;
        border-color: #15803D !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"] p, button[kind="primary"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        background-color: #167B48 !important;
        border-color: #167B48 !important;
    }

    /* Sidebar border separation against canvas (#E7E1D6) */
    div[data-testid="stSidebar"] {
        border-right: 1px solid #E7E1D6 !important;
        background-color: #FBFAF7 !important;
    }

    /* Direction A Sidebar Navigation: Keyed Radio Pills with Area-Specific Tints */
    .st-key-nav_sidebar_radio div[role="radiogroup"] {
        gap: 6px !important;
        display: flex !important;
        flex-direction: column !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label {
        border-radius: 999px !important;
        padding: 10px 18px !important;
        margin: 4px 0 !important;
        cursor: pointer !important;
        transition: background-color 150ms ease, color 150ms ease !important;
        width: 100% !important;
        box-sizing: border-box !important;
        border: 1px solid transparent !important;
        background-color: transparent !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label span {
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #66635A !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:hover {
        background-color: #E7E1D6 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:hover p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:hover span {
        color: #171712 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked),
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) {
        background-color: __NAV_ACTIVE_BG__ !important;
        color: __NAV_ACTIVE_FG__ !important;
        font-weight: 600 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) span,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) span {
        color: __NAV_ACTIVE_FG__ !important;
        font-weight: 600 !important;
    }
    /* Hide the default radio circle indicator */
    .st-key-nav_sidebar_radio div[role="radiogroup"] label > div:first-child,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label > div > div:first-child:not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }

    /* Metric mini-card keyed container */
    .st-key-sidebar_summary_card,
    .st-key-sidebar_summary_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        border: 1px solid #E7E1D6 !important;
        border-radius: 16px !important;
        background-color: #FFFFFF !important;
        padding: 16px !important;
    }
    .st-key-sidebar_summary_card [data-testid="stMetricLabel"] p,
    .st-key-sidebar_summary_card [data-testid="stMetricLabel"] span {
        color: #66635A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .st-key-sidebar_summary_card [data-testid="stMetricValue"] {
        color: #171712 !important;
        font-size: 20px !important;
    }

    /* Direction A Keyed Tinted Stat Cards (Home Screen) */
    div.st-key-home_card_streak:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-home_card_due:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-home_card_library:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .st-key-home_card_streak,
    .st-key-home_card_streak [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DFF3E4 !important;
        border: 1px solid rgba(22, 123, 72, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    .st-key-home_card_due,
    .st-key-home_card_due [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DCEBFF !important;
        border: 1px solid rgba(29, 94, 194, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    .st-key-home_card_library,
    .st-key-home_card_library [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFF0C4 !important;
        border: 1px solid rgba(154, 52, 18, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    /* Stat Cards Shared Styling */
    .stat-icon-tile {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .tile-green {
        background-color: #1F9D63 !important;
    }
    .tile-blue {
        background-color: #2273E6 !important;
    }
    .tile-amber {
        background-color: #B45309 !important;
    }
    .tile-violet {
        background-color: #6C4CF1 !important;
    }
    .tile-coral {
        background-color: #E4572E !important;
    }

    .stat-badge {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 4px 12px !important;
        border-radius: 999px !important;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.02em;
    }
    .badge-mint {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(22, 123, 72, 0.25) !important;
        color: #167B48 !important;
    }
    .badge-sky {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(29, 94, 194, 0.25) !important;
        color: #1D5EC2 !important;
    }
    .badge-butter {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(180, 83, 9, 0.25) !important;
        color: #9A3412 !important;
    }
    .badge-rose {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(197, 34, 31, 0.25) !important;
        color: #C5221F !important;
    }
    .badge-lilac {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(89, 50, 234, 0.25) !important;
        color: #5932EA !important;
    }

    .stat-content {
        display: flex;
        flex-direction: column;
    }
    .stat-label {
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #66635A !important;
        display: block;
    }
    .stat-numeral {
        font-family: 'Inter', sans-serif !important;
        font-size: 36px !important;
        font-weight: 600 !important;
        color: #171712 !important;
        line-height: 1.15 !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
        font-variant-numeric: tabular-nums !important;
        letter-spacing: -0.025em !important;
        display: block;
    }
    .stat-caption {
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        color: #66635A !important;
        display: block;
        line-height: 1.4 !important;
    }

    /* Direction A Home Due & Recent Sections */
    div.st-key-home_due_section:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-home_recent_section:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .st-key-home_due_section,
    .st-key-home_due_section [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-home_recent_section,
    .st-key-home_recent_section [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    /* Direction A Empty Queue Sky Wash Card */
    div.st-key-home_caught_up:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .st-key-home_caught_up,
    .st-key-home_caught_up [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DCEBFF !important;
        border: 1px solid rgba(29, 94, 194, 0.25) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
    }

    /* Saturated Status Tint Chips */
    .chip-pass {
        background-color: #DFF3E4 !important;
        color: #167B48 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        border-radius: 999px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        letter-spacing: 0.04em !important;
    }
    .chip-timeout {
        background-color: #FFF0C4 !important;
        color: #9A3412 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        border-radius: 999px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        letter-spacing: 0.04em !important;
    }
    .chip-fail {
        background-color: #FFE0E0 !important;
        color: #C5221F !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        border-radius: 999px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        letter-spacing: 0.04em !important;
    }

    .attempt-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 8px;
        background-color: transparent;
        border-bottom: 1px solid #E7E1D6;
    }
    .attempt-row:last-child {
        border-bottom: none;
    }

    /* Monospace Light Code Block */
    .code-block-light {
        background-color: #FBFAF7 !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        color: #171712 !important;
        line-height: 1.5 !important;
    }

    /* =========================================================================
       DIRECTION A: PRACTICE ARENA STYLING
       ========================================================================= */

    /* Filter Card */
    div.st-key-practice_filter_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-practice_filter_card,
    .st-key-practice_filter_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 20px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 16px 24px !important;
    }
    .st-key-practice_filter_card div[data-baseweb="select"] > div {
        border-radius: 999px !important;
        border: 1px solid #E7E1D6 !important;
        background-color: #FBFAF7 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .st-key-practice_filter_card label p {
        font-size: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #66635A !important;
    }

    /* Problem Statement Card (Single Named Mechanism) */
    div.st-key-practice_statement_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-practice_statement_card,
    .st-key-practice_statement_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }
    .st-key-practice_statement_card h2,
    .st-key-practice_statement_card .problem-title {
        font-family: 'Fraunces', serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #171712 !important;
        line-height: 1.25 !important;
        margin-top: 4px !important;
        margin-bottom: 12px !important;
    }
    .st-key-practice_statement_card code,
    .st-key-practice_statement_card pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Editor Card (Single Named Mechanism) */
    div.st-key-practice_editor_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-practice_editor_card,
    .st-key-practice_editor_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
        overflow: hidden !important;
    }
    .st-key-practice_editor_card iframe {
        background-color: #14161A !important;
        border-radius: 12px !important;
    }
    .st-key-practice_editor_card textarea {
        background-color: #14161A !important;
        color: #F2F2ED !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: 12px !important;
    }

    /* Hint Ladder Card */
    div.st-key-practice_hint_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-practice_hint_card,
    .st-key-practice_hint_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFF0C4 !important;
        border: 1px solid rgba(180, 83, 9, 0.25) !important;
        border-radius: 20px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05) !important;
        padding: 20px 24px !important;
    }

    /* Visible Test Case Cards */
    div[class*="st-key-visible_test_card"]:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    div[class*="st-key-visible_test_card"],
    div[class*="st-key-visible_test_card"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.04) !important;
        padding: 16px 20px !important;
    }

    /* Verdict Banners */
    div.st-key-verdict_pass_card:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-verdict_fail_card:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-verdict_timeout_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-verdict_pass_card,
    .st-key-verdict_pass_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DFF3E4 !important;
        border: 1px solid rgba(22, 123, 72, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05) !important;
        padding: 18px 24px !important;
    }
    .st-key-verdict_fail_card,
    .st-key-verdict_fail_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFE0E0 !important;
        border: 1px solid rgba(197, 34, 31, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05) !important;
        padding: 18px 24px !important;
    }
    .st-key-verdict_timeout_card,
    .st-key-verdict_timeout_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFF0C4 !important;
        border: 1px solid rgba(180, 83, 9, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05) !important;
        padding: 18px 24px !important;
    }

    /* Failed Case Card (Single Named Mechanism) */
    div.st-key-failed_case_card:has([data-testid="stVerticalBlockBorderWrapper"]),
    div[class*="st-key-failed_case_card"]:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-failed_case_card,
    .st-key-failed_case_card [data-testid="stVerticalBlockBorderWrapper"] > div,
    div[class*="st-key-failed_case_card"],
    div[class*="st-key-failed_case_card"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFE0E0 !important;
        border: 1px solid rgba(197, 34, 31, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 22px 24px !important;
    }

    /* Ruff Code Quality Card & Post Pass Card */
    div.st-key-ruff_quality_card:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-post_pass_review_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-ruff_quality_card,
    .st-key-ruff_quality_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.04) !important;
        padding: 20px 24px !important;
    }
    .st-key-post_pass_review_card,
    .st-key-post_pass_review_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #E8E2FF !important;
        border: 1px solid rgba(89, 50, 234, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.04) !important;
        padding: 20px 24px !important;
    }

    /* Lilac secondary action buttons */
    div[class*="st-key-btn_hint"] button,
    div[class*="st-key-btn_ai_hint"] button,
    div[class*="st-key-btn_code_review"] button,
    div[class*="st-key-btn_reveal"] button {
        background-color: #E8E2FF !important;
        border: 1px solid rgba(89, 50, 234, 0.25) !important;
        color: #5932EA !important;
        border-radius: 999px !important;
        white-space: nowrap !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
    }
    div[class*="st-key-btn_hint"] button:hover,
    div[class*="st-key-btn_ai_hint"] button:hover,
    div[class*="st-key-btn_code_review"] button:hover,
    div[class*="st-key-btn_reveal"] button:hover {
        background-color: #E8E2FF !important;
        border-color: #5932EA !important;
        color: #5932EA !important;
    }
    div[class*="st-key-btn_hint"] button p,
    div[class*="st-key-btn_ai_hint"] button p,
    div[class*="st-key-btn_code_review"] button p,
    div[class*="st-key-btn_reveal"] button p,
    div[class*="st-key-btn_hint"] button span,
    div[class*="st-key-btn_ai_hint"] button span,
    div[class*="st-key-btn_code_review"] button span,
    div[class*="st-key-btn_reveal"] button span {
        color: #5932EA !important;
        font-weight: 600 !important;
    }

    /* Mock Timer Card (Setup & Session Control Card) */
    div.st-key-mock_timer_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-mock_timer_card,
    .st-key-mock_timer_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFE8D1 !important;
        border: 1px solid rgba(185, 56, 21, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.04) !important;
        padding: 20px 24px !important;
    }

    /* Danger Pill Button: End Interview Early */
    div.st-key-btn_end_mock button {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(185, 56, 21, 0.35) !important;
        color: #B93815 !important;
        border-radius: 999px !important;
        white-space: nowrap !important;
        padding: 8px 22px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.04) !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-btn_end_mock button:hover {
        background-color: #FFE0E0 !important;
        border-color: #B93815 !important;
        color: #C5221F !important;
    }
    div.st-key-btn_end_mock button p,
    div.st-key-btn_end_mock button span {
        color: #B93815 !important;
        font-weight: 600 !important;
    }

    /* Primary Pill Button: Start Mock Interview */
    div.st-key-btn_start_mock button {
        background-color: #167B48 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        white-space: nowrap !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05) !important;
    }
    div.st-key-btn_start_mock button:hover {
        background-color: #167B48 !important;
    }
    div.st-key-btn_start_mock button p,
    div.st-key-btn_start_mock button span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Problem Tabs Styling (Direction A with React Aria + BaseWeb) */
    div[data-baseweb="tab-list"],
    div[role="tablist"],
    div[data-testid="stTabs"] div[role="tablist"] {
        background-color: transparent !important;
        border-bottom: 1px solid #E7E1D6 !important;
        gap: 12px !important;
        padding-bottom: 6px !important;
    }
    button[data-baseweb="tab"],
    div[data-testid="stTab"],
    div[data-testid="stTabs"] button[role="tab"] {
        background-color: #FBFAF7 !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 999px !important;
        padding: 6px 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #66635A !important;
        transition: all 0.15s ease !important;
        white-space: nowrap !important;
        cursor: pointer !important;
    }
    button[data-baseweb="tab"]:hover,
    div[data-testid="stTab"]:hover,
    div[data-testid="stTabs"] button[role="tab"]:hover {
        background-color: #FBFAF7 !important;
        color: #171712 !important;
        border-color: #E7E1D6 !important;
    }
    div[data-testid="stTab"] p,
    button[data-baseweb="tab"] p {
        color: #66635A !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    /* Active tab indicator in coral (#B93815) with soft peach highlight */
    button[data-baseweb="tab"][aria-selected="true"],
    div[data-testid="stTab"][aria-selected="true"],
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: #FFE8D1 !important;
        border: 1px solid rgba(185, 56, 21, 0.35) !important;
        border-bottom: 2px solid #B93815 !important;
        color: #B93815 !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 2px rgba(185, 56, 21, 0.08) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span,
    div[data-testid="stTab"][aria-selected="true"] p,
    div[data-testid="stTab"][aria-selected="true"] span,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span {
        color: #B93815 !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="tab-highlight"],
    div[data-testid="stTabsHighlight"] {
        background-color: #B93815 !important;
        height: 2px !important;
    }

    /* Mock Scorecard Card (Scorecard Summary Card) */
    div.st-key-mock_scorecard_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .st-key-mock_scorecard_card,
    .st-key-mock_scorecard_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px 28px !important;
    }

    /* Export Results Pill Button with Lucide Download Icon */
    div.st-key-btn_export_markdown button {
        background-color: #FBFAF7 !important;
        border: 1px solid #E7E1D6 !important;
        color: #171712 !important;
        border-radius: 999px !important;
        white-space: nowrap !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.04) !important;
        transition: all 0.15s ease !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div.st-key-btn_export_markdown button::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23171712' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 15V3'/%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpath d='m7 10 5 5 5-5'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        background-position: center;
        vertical-align: -2px;
    }
    div.st-key-btn_export_markdown button:hover {
        background-color: #FBFAF7 !important;
        border-color: #E7E1D6 !important;
        color: #171712 !important;
    }
    div.st-key-btn_export_markdown button p,
    div.st-key-btn_export_markdown button span {
        color: #171712 !important;
        font-weight: 600 !important;
    }

    /* Direction A Keyed Tinted Stat Cards & Containers (Dashboard Screen) */
    div.st-key-dash_card_solved:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-dash_card_sessions:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-dash_card_hints:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-dashboard_chart_card:has([data-testid="stVerticalBlockBorderWrapper"]),
    div.st-key-dashboard_table_card:has([data-testid="stVerticalBlockBorderWrapper"]) {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .st-key-dash_card_solved,
    .st-key-dash_card_solved [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DFF3E4 !important;
        border: 1px solid rgba(22, 123, 72, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    .st-key-dash_card_sessions,
    .st-key-dash_card_sessions [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #DCEBFF !important;
        border: 1px solid rgba(29, 94, 194, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    .st-key-dash_card_hints,
    .st-key-dash_card_hints [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFF0C4 !important;
        border: 1px solid rgba(154, 52, 18, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px !important;
    }

    .st-key-dash_card_solved .stat-label {
        color: #167B48 !important;
    }
    .st-key-dash_card_sessions .stat-label {
        color: #1D5EC2 !important;
    }
    .st-key-dash_card_hints .stat-label {
        color: #9A3412 !important;
    }

    .st-key-dashboard_chart_card,
    .st-key-dashboard_chart_card [data-testid="stVerticalBlockBorderWrapper"] > div,
    .st-key-dashboard_table_card,
    .st-key-dashboard_table_card [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E7E1D6 !important;
        border-radius: 24px !important;
        box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05), 0 8px 24px rgba(23, 23, 18, 0.06) !important;
        padding: 24px 28px !important;
    }

    /* Topic Breakdown Table in Dashboard */
    .dashboard-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .dashboard-table th {
        text-align: left;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #66635A;
        border-bottom: 1px solid #E7E1D6;
    }
    .dashboard-table td {
        padding: 16px;
        border-bottom: 1px solid #E7E1D6;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: #171712;
        vertical-align: middle;
    }
    .dashboard-table tr:last-child td {
        border-bottom: none;
    }
    .dashboard-table th:last-child,
    .dashboard-table td:last-child {
        white-space: nowrap !important;
        min-width: 140px !important;
    }
    .stat-badge {
        white-space: nowrap !important;
        display: inline-block !important;
    }
    """

    rules_css = rules_css.replace("__NAV_ACTIVE_BG__", active_bg).replace("__NAV_ACTIVE_FG__", active_fg)

    return f"<style>\n{font_css}\n{rules_css}\n</style>"


current_active_nav = st.session_state.get("nav_sidebar_radio")
if not current_active_nav:
    qp = st.query_params.get("screen", "").lower()
    current_active_nav = screen_to_nav.get(qp, "Home")

st.html(get_global_css(current_active_nav))


@lru_cache(maxsize=128)
def get_svg_icon(
    name: str,
    width: int = 18,
    height: int = 18,
    stroke: str | None = None,
    stroke_width: float | None = None,
    extra_class: str = "",
) -> str:
    """
    Loads an SVG icon from assets/icons/ and returns inline SVG markup.
    Allows overriding width, height, stroke color, and stroke-width.
    """
    filename = name if name.endswith(".svg") else f"{name}.svg"
    icon_path = ICONS_DIR / filename
    if not icon_path.exists():
        return ""
    svg = icon_path.read_text(encoding="utf-8").strip()
    svg = re.sub(r'width="[^"]*"', f'width="{width}"', svg, count=1)
    svg = re.sub(r'height="[^"]*"', f'height="{height}"', svg, count=1)
    if stroke:
        svg = re.sub(r'stroke="[^"]*"', f'stroke="{stroke}"', svg, count=1)
    if stroke_width is not None:
        svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg, count=1)
    if extra_class:
        svg = re.sub(r'<svg\b', f'<svg class="{extra_class}"', svg, count=1)
    return svg


# Initialize database store
@st.cache_resource
def get_store() -> CoachStore:
    return CoachStore(db_path="coach.db")


store = get_store()

# Load all problems
@st.cache_data
def get_problems() -> list[dict[str, Any]]:
    problems = load_all_problems("data/problems")
    return [p.model_dump() for p in problems]


all_problems = get_problems()
problems_by_id = {p["id"]: p for p in all_problems}


def render_editor(code: str, key: str, height: str | int = "450px") -> str:
    """
    Renders code editor via streamlit-code-editor (Ace editor wrapper)
    with debounced two-way binding and textarea fallback.
    Always ensures prefilled code is preserved.
    Uses the component's own height parameter (string e.g. '450px') so react-ace
    receives height directly and ResizeObserver sizes the rendered iframe to >= 440px.
    """
    try:
        from code_editor import code_editor
        editor_custom_btns = [
            {
                "name": "Copy",
                "feather": "Copy",
                "hasText": True,
                "alwaysOn": True,
                "commands": ["copyAll"],
                "style": {"top": "0.4rem", "right": "0.4rem"}
            }
        ]
        # Component requires string height e.g. "450px" to set CSS height directly in react-ace
        if isinstance(height, int):
            str_height = f"{max(height, 440)}px"
        else:
            str_height = str(height)

        editor_response = code_editor(
            code,
            lang="python",
            theme="one_dark",
            height=str_height,
            key=key,
            buttons=editor_custom_btns,
            options={
                "wrap": False,
                "showLineNumbers": True,
                "fontSize": 13,
            },
            props={"style": {"backgroundColor": "#14161A", "color": "#F2F2ED", "borderRadius": "8px"}},
            response_mode="debounce",
        )
        if isinstance(editor_response, dict) and editor_response.get("text", "").strip():
            return editor_response["text"]
        elif isinstance(editor_response, str) and editor_response.strip():
            return editor_response
        return code
    except Exception:
        int_height = int(str(height).replace("px", "")) if "px" in str(height) else int(height)
        return st.text_area(
            "Code Editor",
            value=code,
            height=max(int_height, 440),
            key=f"{key}_textarea",
            help="Using monospace editor."
        )


# Single Source of Truth for Sidebar Metrics
streak_count = store.current_streak()
due_list = store.due_problems()

# Screen options and two-way query parameter sync
nav_options = ["Home", "Practice Arena", "Mock Interview", "Dashboard"]
screen_to_nav = {
    "home": "Home",
    "practice": "Practice Arena",
    "mock": "Mock Interview",
    "dashboard": "Dashboard",
}
nav_to_screen = {v: k for k, v in screen_to_nav.items()}

# Sidebar Header: Fraunces serif wordmark and Inter quiet tagline
st.sidebar.html(
    """
    <div style="margin-bottom: 24px; padding: 4px 0 0 0;">
        <div style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; line-height: 1.25; letter-spacing: -0.02em;">AI Coding Prep Coach</div>
        <div style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #66635A; margin-top: 4px;">Zero Cost • Code-Judged • Offline-Ready</div>
    </div>
    """
)

# Query parameter sync with session state
qp_screen = st.query_params.get("screen", "").lower()
if "last_screen_param" not in st.session_state:
    st.session_state["last_screen_param"] = qp_screen
    if qp_screen in screen_to_nav:
        st.session_state["nav_sidebar_radio"] = screen_to_nav[qp_screen]
elif qp_screen != st.session_state["last_screen_param"]:
    st.session_state["last_screen_param"] = qp_screen
    if qp_screen in screen_to_nav:
        st.session_state["nav_sidebar_radio"] = screen_to_nav[qp_screen]

# Determine default index
current_idx = 0
current_nav = st.session_state.get("nav_sidebar_radio")
if current_nav in nav_options:
    current_idx = nav_options.index(current_nav)
elif qp_screen in screen_to_nav:
    current_idx = nav_options.index(screen_to_nav[qp_screen])

# Navigation mechanism: Keyed CSS radio pill
nav_choice = st.sidebar.radio(
    "Navigation",
    nav_options,
    index=current_idx,
    key="nav_sidebar_radio",
    label_visibility="collapsed",
)

# Enforce Area-Specific Tint on Active Nav Pill (DEFECT 3)
nav_tint_bg, nav_tint_fg = NAV_TINTS.get(nav_choice, ("#DFF3E4", "#167B48"))
st.sidebar.html(
    f"""
    <style>
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked),
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) {{
        background-color: {nav_tint_bg} !important;
        color: {nav_tint_fg} !important;
        font-weight: 600 !important;
    }}
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) span,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) span {{
        color: {nav_tint_fg} !important;
        font-weight: 600 !important;
    }}
    </style>
    """
)

# Keep query params in sync with user's selection
target_screen = nav_to_screen.get(nav_choice, "home")
if st.query_params.get("screen", "").lower() != target_screen:
    st.query_params["screen"] = target_screen
    st.session_state["last_screen_param"] = target_screen

# Metric mini-card with keyed container
st.sidebar.html('<div style="height: 16px;"></div>')
with st.sidebar.container(border=True, key="sidebar_summary_card"):
    st.metric("Active Streak", f"{streak_count} days")
    st.metric("Due for Review", f"{len(due_list)} problems")


# ==============================================================================
# SCREEN 1: HOME / DUE REVIEW
# ==============================================================================
if nav_choice == "Home":
    # Header banner with Fraunces serif heading and Start Practice primary CTA pill
    col_head, col_btn = st.columns([4, 1], vertical_alignment="center")
    with col_head:
        st.markdown(
            """<div style="margin-bottom: 8px;">
                <h1 style="font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; color: #171712; margin: 0 0 4px 0; letter-spacing: -0.025em; line-height: 1.2;">
                    Daily Review and Practice Queue
                </h1>
                <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #66635A; margin: 0; line-height: 1.5;">
                    Interview-targeted spaced repetition schedule (1 / 1 / 3 / 7 / 21 days) based strictly on objective test results.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("Start Practice", type="primary", key="home_start_practice_btn", use_container_width=True):
            st.session_state["nav_sidebar_radio"] = "Practice Arena"
            st.query_params["screen"] = "practice"
            st.session_state["last_screen_param"] = "practice"
            st.rerun()

    # Three category-tinted stat cards
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True, key="home_card_streak"):
            flame_svg = get_svg_icon("flame", width=22, height=22, stroke="#FFFFFF")
            streak_unit = "day" if streak_count == 1 else "days"
            if streak_count == 0:
                streak_badge_html = '<span class="stat-badge" style="background-color: rgba(102, 99, 90, 0.12); color: #171712; white-space: nowrap;">Not Started</span>'
                streak_caption = "Solve a problem today to start your streak."
            else:
                streak_badge_html = '<span class="stat-badge badge-mint">Active</span>'
                streak_caption = f"Practice tomorrow to reach a {streak_count + 1}-day streak."
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-green">
                            {flame_svg}
                        </div>
                        {streak_badge_html}
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Active Streak</span>
                        <span class="stat-numeral">{streak_count} {streak_unit}</span>
                        <span class="stat-caption">{streak_caption}</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with c2:
        with st.container(border=True, key="home_card_due"):
            calendar_svg = get_svg_icon("calendar", width=22, height=22, stroke="#FFFFFF")
            due_count = len(due_list)
            due_numeral = f"{due_count} due"
            due_badge = "On Schedule" if due_count == 0 else "Review Ready"
            due_caption = "All scheduled reviews are completely caught up." if due_count == 0 else f"{due_count} problem{'s' if due_count != 1 else ''} need review today."
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-blue">
                            {calendar_svg}
                        </div>
                        <span class="stat-badge badge-sky">{due_badge}</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Problems Due Today</span>
                        <span class="stat-numeral">{due_numeral}</span>
                        <span class="stat-caption">{due_caption}</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with c3:
        with st.container(border=True, key="home_card_library"):
            book_svg = get_svg_icon("book-open", width=22, height=22, stroke="#FFFFFF")
            total_count = len(all_problems)
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-amber">
                            {book_svg}
                        </div>
                        <span class="stat-badge badge-butter">Library</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Total Problem Bank</span>
                        <span class="stat-numeral">{total_count} problems</span>
                        <span class="stat-caption">Curated across DSA, Strings, and Practical Python.</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Due for Review section
    with st.container(border=True, key="home_due_section"):
        cal_blue = get_svg_icon("calendar", width=22, height=22, stroke="#1D5EC2")
        queue_text = "Queue Status: Clear" if not due_list else f"Queue Status: {len(due_list)} Due"
        queue_color = "#1D5EC2" if not due_list else "#9A3412"
        st.markdown(
            f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {cal_blue}
                    <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0;">
                        Due for Review Today
                    </h2>
                </div>
                <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: {queue_color};">
                    {queue_text}
                </span>
            </div>""",
            unsafe_allow_html=True,
        )
        if not due_list:
            with st.container(border=True, key="home_caught_up"):
                cal_big = get_svg_icon("calendar", width=22, height=22, stroke="#1D5EC2")
                st.markdown(
                    f"""<div style="display: flex; align-items: flex-start; gap: 14px;">
                        <div style="background-color: rgba(29, 94, 194, 0.12); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            {cal_big}
                        </div>
                        <div>
                            <div style="font-family: 'Fraunces', serif; font-size: 16px; font-weight: 700; color: #171712; margin-bottom: 2px;">
                                You are all caught up!
                            </div>
                            <div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #171712; line-height: 1.5;">
                                No problems due for review today. Open Practice Arena to solve a new problem.
                            </div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            for item in due_list:
                prob = problems_by_id.get(item["problem_id"])
                if not prob:
                    continue
                d_col1, d_col2 = st.columns([5, 1], vertical_alignment="center")
                diff = prob["difficulty"]
                diff_wash = "#DFF3E4" if diff == "easy" else ("#FFF0C4" if diff == "medium" else "#FFE0E0")
                diff_text = "#167B48" if diff == "easy" else ("#9A3412" if diff == "medium" else "#C5221F")
                with d_col1:
                    st.markdown(
                        f"""<div style="display: flex; align-items: center; gap: 12px; padding: 6px 0;">
                            <span style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; text-transform: uppercase; background-color: {diff_wash}; color: {diff_text}; padding: 3px 10px; border-radius: 999px;">
                                {diff}
                            </span>
                            <div>
                                <strong style="font-family: 'Inter', sans-serif; font-size: 15px; color: #171712;">{prob['title']}</strong>
                                <span style="font-family: 'Inter', sans-serif; font-size: 13px; color: #66635A; margin-left: 8px;">
                                    Track: {prob['track'].upper()} • Topic: {prob['topic']} • Passes: {item['consecutive_passes']}
                                </span>
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with d_col2:
                    if st.button("Practice", key=f"due_btn_{prob['id']}", use_container_width=True):
                        st.session_state["selected_problem_id"] = prob["id"]
                        st.session_state["nav_sidebar_radio"] = "Practice Arena"
                        st.query_params["screen"] = "practice"
                        st.session_state["last_screen_param"] = "practice"
                        st.rerun()

    # Recent Practice Attempts section
    with st.container(border=True, key="home_recent_section"):
        recents = store.get_recent_attempts(limit=5)
        st.markdown(
            f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0;">
                        Recent Practice Attempts
                    </h2>
                    <p style="font-family: 'Inter', sans-serif; font-size: 13px; color: #66635A; margin: 2px 0 0 0;">
                        Deterministic test verdicts recorded strictly in local SQLite.
                    </p>
                </div>
                <span style="font-family: 'Inter', sans-serif; font-size: 13px; color: #66635A; font-weight: 500;">
                    {'Showing last 5 attempts' if recents else 'No attempts recorded'}
                </span>
            </div>""",
            unsafe_allow_html=True,
        )
        if recents:
            for r in recents:
                prob = problems_by_id.get(r["problem_id"], {})
                prob_title = prob.get("title", r["problem_id"])
                prob_track = prob.get("track", "").upper()
                prob_topic = prob.get("topic", "")
                prob_diff = prob.get("difficulty", "medium").title()

                status_norm = (r.get("status") or "").lower()
                if status_norm == "pass":
                    chip_class = "chip-pass"
                    chip_label = "PASS"
                    chip_icon = get_svg_icon("circle-check-big", width=12, height=12, stroke="#167B48", stroke_width=3)
                elif status_norm == "timeout":
                    chip_class = "chip-timeout"
                    chip_label = "TIMEOUT"
                    chip_icon = get_svg_icon("clock", width=12, height=12, stroke="#9A3412", stroke_width=3)
                else:
                    chip_class = "chip-fail"
                    chip_label = "FAIL"
                    chip_icon = get_svg_icon("circle-x", width=12, height=12, stroke="#C5221F", stroke_width=3)

                r_col1, r_col2 = st.columns([5, 1], vertical_alignment="center")
                with r_col1:
                    st.markdown(
                        f"""<div class="attempt-row">
                            <div style="display: flex; align-items: center; gap: 14px;">
                                <span class="{chip_class}">
                                    {chip_icon}
                                    {chip_label}
                                </span>
                                <div>
                                    <strong style="font-family: 'Inter', sans-serif; font-size: 15px; color: #171712;">{prob_title}</strong>
                                    <div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #66635A; margin-top: 2px;">
                                        Track: {prob_track} · Topic: {prob_topic} · Difficulty: {prob_diff}
                                    </div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #66635A;">Date &amp; Runtime</div>
                                <div style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #171712; font-variant-numeric: tabular-nums;">
                                    {r['attempt_date']} · {r['runtime_ms']} ms · {r['hints_used']} Hints
                                </div>
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with r_col2:
                    if st.button("Review", key=f"recent_btn_{r.get('id', r['problem_id'])}_{r['attempt_date']}", use_container_width=True):
                        st.session_state["selected_problem_id"] = r["problem_id"]
                        st.session_state["nav_sidebar_radio"] = "Practice Arena"
                        st.query_params["screen"] = "practice"
                        st.session_state["last_screen_param"] = "practice"
                        st.rerun()
        else:
            st.markdown(
                """<div style="padding: 24px; background-color: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; text-align: center; color: #66635A; font-family: 'Inter', sans-serif; font-size: 14px;">
                    No attempts recorded yet. Launch Practice Arena to begin your first problem.
                </div>""",
                unsafe_allow_html=True,
            )


# ==============================================================================
# SCREEN 2: PRACTICE ARENA
# ==============================================================================
elif nav_choice == "Practice Arena":
    # Two-column workbench layout mirroring mockups/practice.html: Left (3.5 cols / 29%), Right (8.5 cols / 71%)
    left_col, right_col = st.columns([3.5, 8.5], gap="large")

    with left_col:
        # Filter Card (Practice Header Card)
        with st.container(border=True, key="practice_filter_card"):
            tracks = ["All"] + sorted({p["track"] for p in all_problems})
            difficulties = ["All", "easy", "medium", "hard"]
            topics = ["All"] + sorted({p["topic"] for p in all_problems})

            col_f1, col_f2, col_f3 = st.columns(3)
            selected_track = col_f1.selectbox(
                "Track",
                tracks,
                format_func=lambda x: x.upper() if x != "All" else "All Tracks"
            )
            selected_diff = col_f2.selectbox(
                "Difficulty",
                difficulties,
                format_func=lambda x: x.title() if x != "All" else "All Diff"
            )
            selected_topic = col_f3.selectbox(
                "Topic",
                topics,
                format_func=lambda x: x.title() if x != "All" else "All Topics"
            )

            filtered = [
                p for p in all_problems
                if (selected_track == "All" or p["track"] == selected_track)
                and (selected_diff == "All" or p["difficulty"] == selected_diff)
                and (selected_topic == "All" or p["topic"] == selected_topic)
            ]

            if not filtered:
                st.warning("No problems match the current filter selection.")
                st.stop()

            # Pre-select if redirected from Due list or via ?problem= query parameter
            default_index = 0
            qp_prob = st.query_params.get("problem", "").strip().lower()
            if qp_prob:
                for idx, p in enumerate(filtered):
                    if qp_prob in p["id"].lower() or qp_prob in p["title"].lower():
                        default_index = idx
                        break
            elif "selected_problem_id" in st.session_state:
                for idx, p in enumerate(filtered):
                    if p["id"] == st.session_state["selected_problem_id"]:
                        default_index = idx
                        break

            prob_options = {p["id"]: f"{p['title']} [{p['track'].upper()} | {p['difficulty'].title()}]" for p in filtered}
            selected_id = st.selectbox(
                "Choose Problem",
                options=list(prob_options.keys()),
                format_func=lambda x: prob_options[x],
                index=default_index
            )
            current_problem = problems_by_id[selected_id]

            try:
                curr_pos = all_problems.index(current_problem) + 1
            except ValueError:
                curr_pos = 1
            total_in_lib = len(all_problems)

            diff_badge_class = "butter" if current_problem["difficulty"] == "medium" else ("mint" if current_problem["difficulty"] == "easy" else "rose")
            track_badge_class = "lilac" if current_problem["track"] == "dsa" else "sky"

            st.html(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid #E7E1D6;">
                  <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span class="stat-badge badge-{track_badge_class}">{current_problem['track'].upper()}</span>
                    <span class="stat-badge badge-sky">{current_problem['topic'].title()}</span>
                    <span class="stat-badge badge-{diff_badge_class}">{current_problem['difficulty'].title()}</span>
                  </div>
                  <div style="font-size: 12px; color: #66635A; font-family: 'Inter', sans-serif; white-space: nowrap;">
                    Problem <strong>{curr_pos} of {total_in_lib}</strong>
                  </div>
                </div>
                """
            )

        # Problem Statement Card
        with st.container(border=True, key="practice_statement_card"):
            st.html(
                f"""
                <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                  <span class="stat-badge badge-{track_badge_class}">{current_problem['track'].upper()}</span>
                  <span class="stat-badge badge-{diff_badge_class}">{current_problem['difficulty'].title()}</span>
                </div>
                <h2 class="problem-title" style="font-family: 'Fraunces', serif; font-size: 26px; font-weight: 700; color: #171712; line-height: 1.25; margin-top: 0; margin-bottom: 12px;">
                  {current_problem['title']}
                </h2>
                """
            )
            st.markdown(current_problem["statement_md"])

            # Starter function signature box & constraints (P4: broken after each comma with 4-space indent)
            sig_line = current_problem["starter_code"].splitlines()[0] if current_problem.get("starter_code") else f"def {current_problem['function_name']}():"
            formatted_sig = sig_line.replace(", ", ",\n    ") if ("(" in sig_line and ")" in sig_line) else sig_line

            st.html(
                f"""
                <div style="margin-top: 14px;">
                  <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A; display: block; margin-bottom: 6px;">Starter Function Signature</span>
                  <pre class="code-block-light signature-display-box" style="font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; line-height: 1.5 !important; white-space: pre-wrap !important; word-break: break-word !important; margin: 0 !important; padding: 12px 16px !important; background: #FBFAF7 !important; border: 1px solid #E7E1D6 !important; border-radius: 12px !important; color: #171712 !important; overflow-x: hidden !important;">{formatted_sig}</pre>
                </div>
                <div style="margin-top: 12px; font-size: 13px; color: #66635A; font-family: 'Inter', sans-serif;">
                  Execution timeout: <strong>{current_problem.get('time_limit_sec', 3.0)}s</strong> · Sandbox isolated
                </div>
                """
            )

    with right_col:
        # Authentic defect code matching mockups/practice.html for live execution demonstration
        LONGEST_SUBSTRING_DEFECT = (
            "def longest_substring(s: str) -> int:\n"
            "    # Sliding window with last seen character indices\n"
            "    last_seen = {}\n"
            "    left = 0\n"
            "    max_len = 0\n"
            "    \n"
            "    for right, ch in enumerate(s):\n"
            "        if ch in last_seen and last_seen[ch] >= left:\n"
            "            left = last_seen[ch] + 1\n"
            "        last_seen[ch] = right\n"
            "        max_len = max(max_len, right - left)  # Defect: missing + 1 offset\n"
            "        \n"
            "    return max_len\n"
        )

        is_demo_fail = st.query_params.get("demo_fail", "").lower() == "true"
        editor_key = f"practice_editor_{current_problem['id']}"

        # Ensure editor opens prefilled with defect code if demo_fail requested, else starter code
        if editor_key not in st.session_state:
            if is_demo_fail and current_problem["id"] == "longest-substring-without-repeating":
                st.session_state[editor_key] = LONGEST_SUBSTRING_DEFECT
            else:
                st.session_state[editor_key] = current_problem["starter_code"]

        initial_code = st.session_state[editor_key]

        # 1. Problem Editor Card (Top of Right Column)
        with st.container(border=True, key="practice_editor_card"):
            # Lilac Header Strip
            st.html(
                """
                <div class="editor-header-strip" style="background-color: #E8E2FF; border-bottom: 1px solid rgba(89, 50, 234, 0.15); padding: 12px 20px; margin: -24px -24px 16px -24px; border-radius: 23px 23px 0 0; display: flex; justify-content: space-between; align-items: center; white-space: nowrap;">
                  <div style="display: flex; align-items: center; gap: 10px; white-space: nowrap;">
                    <div style="display: flex; gap: 6px;">
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #D92D20; display: inline-block;"></span>
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #B45309; display: inline-block;"></span>
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #1F9D63; display: inline-block;"></span>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: #5932EA; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap;">SOLUTION EDITOR · PYTHON</span>
                  </div>
                  <span style="font-family: 'Inter', sans-serif; font-size: 12px; color: #5932EA; font-weight: 600; white-space: nowrap;">Sandbox · 3.0s · Python 3.12</span>
                </div>
                """
            )

            user_code = render_editor(initial_code, key=editor_key, height="450px")
            st.session_state[f"code_{current_problem['id']}"] = user_code

            # Bottom Action Bar with Primary Run & Submit pill
            col_bar_info, col_bar_btn = st.columns([1, 1])
            with col_bar_info:
                st.html(
                    """
                    <div style="padding-top: 10px; font-size: 13px; color: #66635A; font-family: 'Inter', sans-serif;">
                      Clean environment · Network disabled
                    </div>
                    """
                )
            with col_bar_btn:
                run_submitted = st.button("Run & Submit", type="primary", key=f"btn_run_{current_problem['id']}", use_container_width=True)

            # Check empty or unchanged starter code guard
            if run_submitted:
                stripped_code = user_code.strip()
                stripped_starter = current_problem["starter_code"].strip()
                if not stripped_code or stripped_code == stripped_starter:
                    st.warning(
                        f"Write your solution first — the judge expected '{current_problem['function_name']}(...)'."
                    )
                    run_submitted = False

        # 2. Verdict Banners & Diagnostics (Directly beneath editor when present)
        if run_submitted or is_demo_fail:
            exec_code = (
                LONGEST_SUBSTRING_DEFECT
                if (is_demo_fail and not run_submitted and current_problem["id"] == "longest-substring-without-repeating")
                else user_code
            )
            with st.spinner("Executing solution inside sandbox..."):
                judge_result = run_solution(exec_code, current_problem)

            status = judge_result["status"]
            runtime = judge_result["runtime_ms"]
            passed = judge_result["passed"]
            total = judge_result["total"]
            hint_key = f"hint_level_{current_problem['id']}"
            hints_used = st.session_state.get(hint_key, 0)

            # Persist attempt to SQLite if manually submitted
            if run_submitted:
                store.record_attempt(
                    problem_id=current_problem["id"],
                    status=status,
                    runtime_ms=runtime,
                    hints_used=hints_used,
                    mode="practice",
                    topic=current_problem["topic"]
                )

            # Verdict Banners:
            if status == "pass":
                check_icon_svg = get_svg_icon("circle-check-big", width=18, height=18, stroke="#167B48")
                with st.container(border=True, key="verdict_pass_card"):
                    st.html(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                          <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="stat-badge badge-mint">PASS</span>
                            <strong style="font-size: 16px; color: #167B48; font-family: 'Inter', sans-serif;">
                              {passed}/{total} tests passed ({runtime} ms)
                            </strong>
                          </div>
                          <div style="display: flex; align-items: center; gap: 6px; color: #167B48;">
                            {check_icon_svg}
                            <span style="font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif;">All Tests Accepted</span>
                          </div>
                        </div>
                        """
                    )
            elif status == "fail":
                circle_x_svg = get_svg_icon("circle-x", width=18, height=18, stroke="#C5221F")
                with st.container(border=True, key="verdict_fail_card"):
                    st.html(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                          <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="stat-badge badge-rose">FAIL</span>
                            <strong style="font-size: 16px; color: #C5221F; font-family: 'Inter', sans-serif;">
                              {passed}/{total} tests passed ({runtime} ms)
                            </strong>
                          </div>
                          <div style="display: flex; align-items: center; gap: 6px; color: #C5221F;">
                            {circle_x_svg}
                            <span style="font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif;">Test Mismatch</span>
                          </div>
                        </div>
                        """
                    )

                # Failed Test Case Detail Card using single named mechanism: st.container(border=True, key="failed_case_card")
                failed_cases = judge_result.get("failed_cases", [])
                if failed_cases:
                    fc = failed_cases[0]
                    # Format authentic inputs cleanly
                    if isinstance(fc.get("input_args"), list) and len(fc.get("input_args")) == 1 and isinstance(fc["input_args"][0], str):
                        input_display = f's = "{fc["input_args"][0]}"'
                    else:
                        input_display = ", ".join(repr(arg) for arg in fc.get("input_args", []))

                    with st.container(border=True, key="failed_case_card"):
                        st.html(
                            f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                              <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="stat-badge badge-rose">FAIL</span>
                                <strong style="font-size: 16px; color: #C5221F; font-family: 'Inter', sans-serif;">
                                  Visible Test Case 1 Failed
                                </strong>
                              </div>
                              <div style="display: flex; align-items: center; gap: 6px; color: #C5221F;">
                                {circle_x_svg}
                                <span style="font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif;">Visible Test Mismatch</span>
                              </div>
                            </div>
                            <p style="font-size: 14px; color: #171712; margin-bottom: 12px; font-family: 'Inter', sans-serif;">
                              Your solution failed on visible test case:
                            </p>
                            <div class="code-block-light" style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(197, 34, 31, 0.25);">
                              <strong>Input:</strong> {input_display}<br>
                              <strong>Expected:</strong> {fc.get('expected')}<br>
                              <strong>Got:</strong> {fc.get('got')}
                            </div>
                            """
                        )
            elif status == "timeout":
                with st.container(border=True, key="verdict_timeout_card"):
                    st.markdown(":orange-background[**TIMEOUT**] Execution exceeded 3.0s time limit.")
                    st.warning(judge_result.get("stderr", "Execution timed out."))
            elif status == "error":
                with st.container(border=True, key="verdict_fail_card"):
                    st.markdown(":red-background[**ERROR**] Execution error")
                    expected_fn = judge_result.get("expected_function")
                    found_fns = judge_result.get("found_functions")
                    if expected_fn and found_fns is not None:
                        st.error(f"Function definition mismatch: Expected '{expected_fn}', but found {found_fns}.")
                    st.code(judge_result.get("stderr", "Execution error"), language="text")

            # Static Code Quality (Ruff)
            with st.container(border=True, key="ruff_quality_card"):
                st.html(
                    """
                    <div style="margin-bottom: 8px;">
                      <h4 style="font-family: 'Fraunces', serif; font-size: 16px; font-weight: 700; color: #171712; margin: 0;">
                        Static Code Quality (Ruff)
                      </h4>
                    </div>
                    """
                )
                with st.spinner("Running Ruff static analysis..."):
                    ruff_res = run_ruff_lint(user_code)
                    if not ruff_res["findings"]:
                        st.success("Clean code: Ruff found 0 diagnostics.")
                    else:
                        st.info(f"Ruff Diagnostic Summary: {ruff_res['summary']}")
                        for finding in ruff_res["findings"]:
                            st.markdown(f"- Line {finding['line']}, Col {finding['col']} `[{finding['code']}]`: {finding['message']}")

            # Post-Pass Conceptual Review or Manual Review Trigger
            with st.container(border=True, key="post_pass_review_card"):
                st.html(
                    """
                    <div style="margin-bottom: 8px;">
                      <h4 style="font-family: 'Fraunces', serif; font-size: 16px; font-weight: 700; color: #171712; margin: 0;">
                        AI Code Review (Local Ollama)
                      </h4>
                    </div>
                    """
                )
                review_requested = st.button("Request AI Code Review", key=f"btn_code_review_{current_problem['id']}", use_container_width=True)
                if status == "pass" or review_requested:
                    with st.spinner("Generating conceptual review..."):
                        review_text = review_code(current_problem, user_code)
                        st.info(review_text)

        # 3. Visible Test Cases (Right Column, after Editor & Verdicts)
        st.html(
            """
            <div style="margin-top: 16px; margin-bottom: 8px;">
              <h3 style="font-family: 'Fraunces', serif; font-size: 18px; font-weight: 700; color: #171712; margin: 0;">
                Visible Test Cases
              </h3>
            </div>
            """
        )
        for i, tc in enumerate(current_problem["visible_tests"], 1):
            with st.container(border=True, key=f"visible_test_card_{i}"):
                args_repr = ", ".join(repr(arg) for arg in tc["input_args"])
                check_icon_svg = get_svg_icon("circle-check-big", width=16, height=16, stroke="#167B48")
                st.html(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                      <div style="display: flex; align-items: center; gap: 8px; white-space: nowrap;">
                        {check_icon_svg}
                        <span style="font-size: 13px; font-weight: 700; color: #167B48; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap;">
                          TEST CASE #{i}
                        </span>
                      </div>
                      <span class="stat-badge badge-mint" style="white-space: nowrap;">Provided</span>
                    </div>
                    <div class="code-block-light" style="background: rgba(255, 255, 255, 0.7); border-color: rgba(22, 123, 72, 0.2);">
                      Input: {args_repr}<br>
                      Expected: {tc['expected']}
                    </div>
                    """
                )

        # 4. Progressive Hint Ladder (Right Column, after Test Cases)
        with st.container(border=True, key="practice_hint_card"):
            hint_key = f"hint_level_{current_problem['id']}"
            if hint_key not in st.session_state:
                st.session_state[hint_key] = 0

            current_level = st.session_state[hint_key]
            total_hints = len(current_problem.get("hints", []))

            amber_sparkle = get_svg_icon("sparkles", width=16, height=16, stroke="#9A3412")
            st.html(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    {amber_sparkle}
                    <span style="font-size: 13px; font-weight: 700; color: #9A3412; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap;">
                      Hint Ladder ({current_level} of {total_hints} Revealed)
                    </span>
                  </div>
                </div>
                """
            )

            if st.button("Reveal Next Hint", key=f"btn_hint_{current_problem['id']}", disabled=(current_level >= total_hints), use_container_width=True):
                st.session_state[hint_key] += 1
                st.rerun()

            ai_hint_clicked = st.button("Ask AI to Explain Hint", key=f"btn_ai_hint_{current_problem['id']}", disabled=(current_level == 0), use_container_width=True)

            if current_level > 0:
                for lvl in range(1, current_level + 1):
                    st.html(
                        f"""
                        <div style="margin-top: 10px; padding: 10px 14px; background: rgba(255, 255, 255, 0.7); border-radius: 10px; border: 1px solid rgba(180, 83, 9, 0.2); font-size: 14px; color: #171712;">
                          <strong>Hint {lvl}:</strong> {current_problem['hints'][lvl - 1]}
                        </div>
                        """
                    )

                if ai_hint_clicked:
                    with st.spinner("Asking local AI (Ollama)..."):
                        code_val = st.session_state.get(f"code_{current_problem['id']}", current_problem["starter_code"])
                        ai_hint_explanation = explain_hint(current_problem, code_val, hint_level=current_level)
                        st.markdown(ai_hint_explanation)


# ==============================================================================
# SCREEN 3: MOCK INTERVIEW ARENA (LANE T & U5)
# ==============================================================================
elif nav_choice == "Mock Interview":
    # Mock interview session state
    if "mock_state" not in st.session_state:
        st.session_state["mock_state"] = "unstarted"  # unstarted | running | completed

    if st.query_params.get("mock_state", "").lower() == "completed":
        st.session_state["mock_state"] = "completed"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time() - 25 * 60
            st.session_state["mock_start_iso"] = datetime.now().isoformat()
            st.session_state["mock_finish_time"] = time.time()
            st.session_state["mock_problems"] = [
                problems_by_id.get("binary-search", all_problems[0]),
                problems_by_id.get("longest-substring-without-repeating", all_problems[1]),
            ]
            st.session_state["mock_p1_status"] = "not_attempted"
            st.session_state["mock_p2_status"] = "not_attempted"
            st.session_state["mock_p1_hints"] = 0
            st.session_state["mock_p2_hints"] = 0
            st.session_state["mock_p1_result"] = None
            st.session_state["mock_p2_result"] = None

    if st.query_params.get("mock_state", "").lower() == "running":
        st.session_state["mock_state"] = "running"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time() - 19
            st.session_state["mock_start_iso"] = datetime.now().isoformat()
            st.session_state["mock_duration_sec"] = 45 * 60
            p1 = problems_by_id.get("binary-search", all_problems[0])
            p2 = problems_by_id.get("longest-substring-without-repeating", all_problems[1])
            st.session_state["mock_problems"] = [p1, p2]
            st.session_state["mock_p1_status"] = "not_attempted"
            st.session_state["mock_p1_hints"] = 0
            st.session_state["mock_p2_status"] = "not_attempted"
            st.session_state["mock_p2_hints"] = 0
            st.session_state["mock_p1_result"] = None
            st.session_state["mock_p2_result"] = None

    if st.session_state["mock_state"] == "unstarted":
        col_hdr1, col_hdr2 = st.columns([8, 4], vertical_alignment="center")
        with col_hdr1:
            st.markdown(
                """
                <div>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">Technical Interview Simulation</h2>
                    <p style="font-size: 14px; color: #66635A; margin: 0;">Two curated algorithmic problems under 45:00 strict countdown constraint.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.html('<div style="height: 16px;"></div>')

        with st.container(border=True, key="mock_timer_card"):
            st.markdown(
                """
                <div style="font-family: 'Fraunces', serif; font-size: 22px; font-weight: 700; color: #171712; margin-bottom: 6px;">
                    Ready to Begin Simulation?
                </div>
                <div style="font-size: 14px; color: #66635A; line-height: 1.5; margin-bottom: 20px;">
                    A 45-minute timed simulation of a technical coding round consisting of 2 curated problems.
                    The timer ticks down automatically in real time across two synchronized indicators.
                    Hints and execution metrics are tracked on your authentic scorecard.
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Start 45-Minute Mock Interview", type="primary", key="btn_start_mock"):
                p1 = problems_by_id.get("binary-search", all_problems[0])
                p2 = problems_by_id.get("longest-substring-without-repeating", all_problems[1])
                st.session_state["mock_state"] = "running"
                st.session_state["mock_start_time"] = time.time()
                st.session_state["mock_start_iso"] = datetime.now().isoformat()
                st.session_state["mock_duration_sec"] = 45 * 60
                st.session_state["mock_problems"] = [p1, p2]
                st.session_state["mock_p1_status"] = "not_attempted"
                st.session_state["mock_p2_status"] = "not_attempted"
                st.session_state["mock_p1_hints"] = 0
                st.session_state["mock_p2_hints"] = 0
                st.session_state["mock_p1_result"] = None
                st.session_state["mock_p2_result"] = None
                st.rerun()

        st.html('<div style="height: 16px;"></div>')

        # Simulation Rules Card (DEFECT 5)
        with st.container(border=True, key="mock_rules_card"):
            st.markdown(
                """
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="background: #FFE8D1; color: #B93815; border: 1px solid rgba(185, 56, 21, 0.25); border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                            Protocol
                        </span>
                    </div>
                    <h3 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                        Simulation Rules &amp; Evaluation Protocol
                    </h3>
                    <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #66635A; margin: 0;">
                        Standard technical coding round parameters enforced automatically by local judge.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            r_col1, r_col2 = st.columns(2, gap="medium")
            with r_col1:
                st.markdown(
                    """
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 16px 18px; margin-bottom: 12px;">
                        <div style="font-weight: 700; font-size: 14px; color: #171712; margin-bottom: 4px;">1. Strict 45-Minute Limit</div>
                        <div style="font-size: 13px; color: #66635A; line-height: 1.5;">A countdown timer runs across synchronized indicators. Submissions lock automatically when time expires.</div>
                    </div>
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 16px 18px;">
                        <div style="font-weight: 700; font-size: 14px; color: #171712; margin-bottom: 4px;">2. Two Curated Problems</div>
                        <div style="font-size: 13px; color: #66635A; line-height: 1.5;">Curated pairs designed to evaluate algorithmic approach, edge cases, and code efficiency under realistic interview pacing.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with r_col2:
                st.markdown(
                    """
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 16px 18px; margin-bottom: 12px;">
                        <div style="font-weight: 700; font-size: 14px; color: #171712; margin-bottom: 4px;">3. Progressive Hint Tracking</div>
                        <div style="font-size: 13px; color: #66635A; line-height: 1.5;">Up to 3 progressive hints available per problem. Every revealed hint is recorded and reported on your final scorecard.</div>
                    </div>
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 16px 18px;">
                        <div style="font-weight: 700; font-size: 14px; color: #171712; margin-bottom: 4px;">4. Authentic Code Execution</div>
                        <div style="font-size: 13px; color: #66635A; line-height: 1.5;">Solutions execute in an isolated local subprocess against real test suites. Zero invented scores or simulated verdicts.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Past Sessions (Render ONLY if mock sessions exist in store, omit completely if 0)
        with store._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, problem_id, topic, status, runtime_ms, hints_used, attempt_date, created_at
                FROM attempts
                WHERE mode = 'mock'
                ORDER BY id DESC
                """
            )
            past_mock_attempts = [dict(row) for row in cur.fetchall()]

        if past_mock_attempts:
            st.html('<div style="height: 16px;"></div>')
            with st.container(border=True, key="mock_past_sessions_card"):
                st.markdown(
                    """
                    <div style="margin-bottom: 16px;">
                        <h3 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                            Past Mock Sessions
                        </h3>
                        <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #66635A; margin: 0;">
                            Authentic interview simulation attempts recorded in local SQLite database.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                past_rows = []
                for a in past_mock_attempts:
                    status_badge = '<span class="stat-badge badge-mint">PASS</span>' if a['status'] == 'pass' else '<span class="stat-badge badge-rose">FAIL</span>'
                    past_rows.append(f"""<tr>
                        <td><strong>{a['problem_id']}</strong></td>
                        <td>{a['topic']}</td>
                        <td>{status_badge}</td>
                        <td style="font-variant-numeric: tabular-nums;">{a['runtime_ms']} ms</td>
                        <td>{a['hints_used']}</td>
                        <td style="color: #66635A; font-size: 13px;">{a['attempt_date']}</td>
                    </tr>""")
                st.markdown(
                    f"""<table class="dashboard-table">
                        <thead>
                            <tr>
                                <th>Problem</th>
                                <th>Topic</th>
                                <th>Status</th>
                                <th>Runtime</th>
                                <th>Hints</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(past_rows)}
                        </tbody>
                    </table>""",
                    unsafe_allow_html=True,
                )

    elif st.session_state["mock_state"] == "running":
        p_list = st.session_state["mock_problems"]

        # Header Row: Direction A Title on left, Display 1 (Autorefresh Timer Fragment) on right
        col_hdr1, col_hdr2 = st.columns([7, 5], vertical_alignment="center")
        with col_hdr1:
            st.markdown(
                """
                <div>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">Technical Interview Simulation</h2>
                    <p style="font-size: 14px; color: #66635A; margin: 0;">Two curated algorithmic problems under 45:00 strict countdown constraint.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Display 1: Header capsule in wash-peach #FFE8D1, text #B93815, 999px radius, Lucide timer icon, ticking mm:ss
        @st.fragment(run_every=1.0)
        def render_header_timer():
            start = st.session_state.get("mock_start_time", time.time())
            duration = st.session_state.get("mock_duration_sec", 45 * 60)
            mins, secs, is_expired = calculate_remaining_time(start, duration, time.time())
            timer_icon = get_svg_icon("timer", width=20, height=20, stroke="#B93815", stroke_width=2)
            if is_expired:
                st.session_state["mock_time_expired"] = True
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; align-items: center;">
                      <div style="background: #FFE8D1; border: 1px solid rgba(185, 56, 21, 0.25); border-radius: 999px; padding: 10px 22px; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05);">
                        {timer_icon}
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 700; color: #C5221F; font-variant-numeric: tabular-nums;">
                          00:00
                        </span>
                        <span style="background: #FFFFFF; border: 1px solid rgba(185, 56, 21, 0.25); color: #C5221F; padding: 3px 10px; border-radius: 999px; font-weight: 600; font-size: 12px;">Expired</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; align-items: center;">
                      <div style="background: #FFE8D1; border: 1px solid rgba(185, 56, 21, 0.25); border-radius: 999px; padding: 10px 22px; display: inline-flex; align-items: center; gap: 10px; box-shadow: 0 1px 2px rgba(23, 23, 18, 0.05);">
                        {timer_icon}
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 700; color: #171712; font-variant-numeric: tabular-nums;">
                          {mins:02d}:{secs:02d}
                        </span>
                        <span style="background: #FFFFFF; border: 1px solid rgba(185, 56, 21, 0.25); color: #B93815; padding: 3px 10px; border-radius: 999px; font-weight: 600; font-size: 12px;">Ticking Live</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_hdr2:
            render_header_timer()

        st.html('<div style="height: 12px;"></div>')

        # Display 2 & Setup & Session Control Card: st.container(border=True, key="mock_timer_card")
        with st.container(border=True, key="mock_timer_card"):
            c_time, c_progress, c_action = st.columns([4, 4, 3], vertical_alignment="center")

            with c_time:
                @st.fragment(run_every=1.0)
                def render_card_timer():
                    start = st.session_state.get("mock_start_time", time.time())
                    duration = st.session_state.get("mock_duration_sec", 45 * 60)
                    mins, secs, is_expired = calculate_remaining_time(start, duration, time.time())
                    disp = "00:00" if is_expired else f"{mins:02d}:{secs:02d}"
                    st.markdown(
                        f"""
                        <div>
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #9A3412;">
                                Time Remaining
                            </div>
                            <div style="font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; color: #B93815; font-variant-numeric: tabular-nums; line-height: 1.2; margin-top: 2px;">
                                {disp}
                            </div>
                            <div style="font-size: 12px; color: #9A3412; margin-top: 2px;">
                                45:00 strict countdown constraint
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                render_card_timer()

            with c_progress:
                session_start_iso = st.session_state.get("mock_start_iso")
                p1_eval = get_mock_problem_evaluation(
                    p_list[0]["id"],
                    session_start_iso,
                    st.session_state.get("mock_p1_result"),
                    st.session_state.get("mock_p1_hints", 0),
                    store
                )
                p2_eval = get_mock_problem_evaluation(
                    p_list[1]["id"],
                    session_start_iso,
                    st.session_state.get("mock_p2_result"),
                    st.session_state.get("mock_p2_hints", 0),
                    store
                )
                solved_count = (1 if p1_eval["is_pass"] else 0) + (1 if p2_eval["is_pass"] else 0)
                p1_prog_badge = "PASS" if p1_eval["is_pass"] else ("FAIL" if p1_eval["status"] == "fail" else "Not Attempted")
                p2_prog_badge = "PASS" if p2_eval["is_pass"] else ("FAIL" if p2_eval["status"] == "fail" else "Not Attempted")
                st.markdown(
                    f"""
                    <div>
                        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">
                            Session Progress
                        </div>
                        <div style="font-family: 'Inter', sans-serif; font-size: 26px; font-weight: 600; color: #171712; font-variant-numeric: tabular-nums; line-height: 1.2; margin-top: 2px;">
                            {solved_count} of 2 Solved
                        </div>
                        <div style="font-size: 12px; color: #66635A; margin-top: 2px;">
                            P1: {p1_prog_badge} · P2: {p2_prog_badge}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_action:
                st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                if st.button("End Interview Early", key="btn_end_mock", help="Conclude simulation and generate final scorecard"):
                    st.session_state["mock_state"] = "completed"
                    st.session_state["mock_finish_time"] = time.time()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.html('<div style="height: 16px;"></div>')

        # Scorecard Summary Card (Direction A Single Named Mechanism)
        with st.container(border=True, key="mock_scorecard_card"):
            sc_hdr_left, sc_hdr_right = st.columns([8, 4], vertical_alignment="center")
            with sc_hdr_left:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="background: #FFE8D1; color: #B93815; border: 1px solid rgba(185, 56, 21, 0.25); border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                            Session In Progress
                        </span>
                    </div>
                    <div style="font-family: 'Fraunces', serif; font-size: 24px; font-weight: 700; color: #171712; line-height: 1.25;">
                        Mock Interview Evaluation
                    </div>
                    <div style="font-size: 13px; color: #66635A; margin-top: 2px;">
                        Live simulation evaluated against authentic test suites under timed conditions.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with sc_hdr_right:
                st.markdown(
                    f"""
                    <div style="text-align: right;">
                        <div style="font-family: 'Inter', sans-serif; font-size: 20px; font-weight: 700; color: #171712; font-variant-numeric: tabular-nums;">
                            {solved_count} Solved, {2 - solved_count} In Progress
                        </div>
                        <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A; margin-top: 2px;">
                            Summary Metrics
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.html('<div style="height: 14px;"></div>')

            # Authentic Problems Evaluation Grid (2 columns matching mockups/mock.html)
            col_sc1, col_sc2 = st.columns(2, gap="medium")

            # Problem 1 Summary Box (Authentic session-scoped evaluation)
            with col_sc1:
                prob1_title = p_list[0]["title"]
                if p1_eval["status"] == "pass":
                    p1_badge = '<span style="background: #DFF3E4; color: #167B48; border: 1px solid rgba(22, 123, 72, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">PASS</span>'
                    p1_rt_str = f"<span><strong>Runtime:</strong> {p1_eval['runtime_ms']} ms</span>"
                elif p1_eval["status"] == "fail":
                    p1_badge = '<span style="background: #FFE0E0; color: #C5221F; border: 1px solid rgba(197, 34, 31, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">FAIL</span>'
                    p1_rt_str = f"<span><strong>Runtime:</strong> {p1_eval['runtime_ms']} ms</span>"
                else:
                    p1_badge = '<span style="background: rgba(102, 99, 90, 0.12); color: #66635A; border: 1px solid #E7E1D6; border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">NOT ATTEMPTED</span>'
                    p1_rt_str = "<span><strong>Runtime:</strong> —</span>"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 700; color: #171712;">Problem 1: {prob1_title}</strong>
                            {p1_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A;">Track: {p_list[0]['track'].upper()} · Topic: {p_list[0]['topic']} · {p_list[0]['difficulty'].title()}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px; margin-top: 4px;">
                            {p1_rt_str}
                            <span><strong>Hints Used:</strong> {p1_eval['hints_used']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Problem 2 Summary Box (Authentic session-scoped evaluation)
            with col_sc2:
                prob2_title = p_list[1]["title"]
                if p2_eval["status"] == "pass":
                    p2_badge = '<span style="background: #DFF3E4; color: #167B48; border: 1px solid rgba(22, 123, 72, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">PASS</span>'
                    p2_rt_str = f"<span><strong>Runtime:</strong> {p2_eval['runtime_ms']} ms</span>"
                elif p2_eval["status"] == "fail":
                    p2_badge = '<span style="background: #FFE0E0; color: #C5221F; border: 1px solid rgba(197, 34, 31, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">FAIL</span>'
                    p2_rt_str = f"<span><strong>Runtime:</strong> {p2_eval['runtime_ms']} ms</span>"
                else:
                    p2_badge = '<span style="background: rgba(102, 99, 90, 0.12); color: #66635A; border: 1px solid #E7E1D6; border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap;">NOT ATTEMPTED</span>'
                    p2_rt_str = "<span><strong>Runtime:</strong> —</span>"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 700; color: #171712;">Problem 2: {prob2_title}</strong>
                            {p2_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A;">Track: {p_list[1]['track'].upper()} · Topic: {p_list[1]['topic']} · {p_list[1]['difficulty'].title()}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px; margin-top: 4px;">
                            {p2_rt_str}
                            <span><strong>Hints Used:</strong> {p2_eval['hints_used']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.html('<div style="height: 14px;"></div>')

            # Footer of Scorecard Card: Status info and Secondary Pill Export Button
            sc_ft_left, sc_ft_right = st.columns([7, 5], vertical_alignment="center")
            with sc_ft_left:
                st.markdown(
                    """
                    <div style="font-size: 13px; color: #66635A;">
                        Authentic Evaluation · Single Named Mechanism · Zero Invented Metrics
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with sc_ft_right:
                scorecard_export_md = f"""# Mock Interview Scorecard — AI Coding Prep Coach
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Status: {'Completed' if st.session_state.get('mock_state') == 'completed' else 'In Progress'}
Time Elapsed: {round((time.time() - st.session_state.get('mock_start_time', time.time())) / 60, 1)} minutes
Summary: {solved_count} Solved, {2 - solved_count} In Progress

## Authentic Problem Results
- **Problem 1: {p_list[0]['title']}** ({p_list[0]['topic']} · {p_list[0]['difficulty'].title()})
  - Status: {p1_eval['status'].upper().replace('_', ' ')}
  - Runtime: {f"{p1_eval['runtime_ms']} ms" if p1_eval['runtime_ms'] is not None else "—"}
  - Hints Used: {p1_eval['hints_used']}
- **Problem 2: {p_list[1]['title']}** ({p_list[1]['topic']} · {p_list[1]['difficulty'].title()})
  - Status: {p2_eval['status'].upper().replace('_', ' ')}
  - Runtime: {f"{p2_eval['runtime_ms']} ms" if p2_eval['runtime_ms'] is not None else "—"}
  - Hints Used: {p2_eval['hints_used']}

*Generated locally by AI Coding Prep Coach (Judge: Code, not AI).*
"""
                st.download_button(
                    label="Export Results as Markdown",
                    data=scorecard_export_md,
                    file_name=f"mock_scorecard_{date.today().isoformat()}.md",
                    mime="text/markdown",
                    key="btn_export_markdown",
                )

        st.html('<div style="height: 20px;"></div>')

        time_expired = st.session_state.get("mock_time_expired", False)
        if time_expired:
            st.warning("Time limit expired. Submissions are now locked. Please click Finish to generate your scorecard.")

        mock_tab1, mock_tab2 = st.tabs([f"Problem 1: {p_list[0]['title']}", f"Problem 2: {p_list[1]['title']}"])

        # TAB 1
        with mock_tab1:
            prob1 = p_list[0]
            col_m1_left, col_m1_right = st.columns([4, 7], gap="large")

            with col_m1_left:
                with st.container(border=True):
                    st.subheader(prob1["title"])
                    st.caption(f"Track: {prob1['track'].upper()} | Topic: {prob1['topic']} | Difficulty:\u00A0{prob1['difficulty'].title()}")
                    st.markdown(prob1["statement_md"])

                st.subheader("Visible Test Cases")
                for i, tc in enumerate(prob1["visible_tests"], 1):
                    with st.expander(f"Visible Case #{i}", expanded=True):
                        st.code(f"Input: {tc['input_args']}\nExpected: {tc['expected']}", language="python")

                with st.container(border=True):
                    if st.button("Reveal Hint (Problem 1)", key="btn_m1_hint") and st.session_state["mock_p1_hints"] < 3:
                        st.session_state["mock_p1_hints"] += 1
                        st.rerun()

                    if st.session_state["mock_p1_hints"] > 0:
                        for h in range(st.session_state["mock_p1_hints"]):
                            st.info(f"Hint {h+1}: {prob1['hints'][h]}")

            with col_m1_right:
                with st.container(border=True):
                    st.subheader("Solution Editor")
                    code1 = render_editor(prob1["starter_code"], key="mock_editor_p1", height=440)
                    if st.query_params.get("mock_solve_p1", "").lower() == "true":
                        code1 = (
                            "def binary_search(nums: list, target: int) -> int:\n"
                            "    left, right = 0, len(nums) - 1\n"
                            "    while left <= right:\n"
                            "        mid = (left + right) // 2\n"
                            "        if nums[mid] == target:\n"
                            "            return mid\n"
                            "        elif nums[mid] < target:\n"
                            "            left = mid + 1\n"
                            "        else:\n"
                            "            right = mid - 1\n"
                            "    return -1\n"
                        )
                    st.session_state["mock_p1_code"] = code1

                    if st.button("Submit Problem 1", type="primary", disabled=time_expired, key="btn_sub_p1"):
                        res1 = run_solution(code1, prob1)
                        st.session_state["mock_p1_status"] = res1["status"]
                        st.session_state["mock_p1_result"] = res1
                        store.record_attempt(
                            prob1["id"], res1["status"], res1["runtime_ms"],
                            st.session_state["mock_p1_hints"], mode="mock", topic=prob1["topic"]
                        )
                        st.rerun()

                # Display stored result for Tab 1
                res1 = st.session_state.get("mock_p1_result")
                if res1:
                    with st.container(border=True):
                        st.subheader("Judge Results (Problem 1)")
                        if res1["status"] == "pass":
                            st.markdown(f':green-background[**PASS**] **{res1["passed"]}/{res1["total"]}** tests passed (`{res1["runtime_ms"]} ms`)')
                        elif res1["status"] == "fail":
                            st.markdown(f':red-background[**FAIL**] **{res1["passed"]}/{res1["total"]}** tests passed (`{res1["runtime_ms"]} ms`)')
                            for fc in res1.get("failed_cases", []):
                                with st.container(border=True):
                                    st.markdown(f"**Input:** `{fc.get('input_args')}`")
                                    st.markdown(f"**Expected:** `{fc.get('expected')}`")
                                    st.markdown(f"**Got:** `{fc.get('got')}`")
                        else:
                            st.markdown(f':orange-background[**{res1["status"].upper()}**]')
                            st.code(res1.get("stderr", ""), language="text")

        # TAB 2
        with mock_tab2:
            prob2 = p_list[1]
            col_m2_left, col_m2_right = st.columns([4, 7], gap="large")

            with col_m2_left:
                with st.container(border=True):
                    st.subheader(prob2["title"])
                    st.caption(f"Track: {prob2['track'].upper()} | Topic: {prob2['topic']} | Difficulty:\u00A0{prob2['difficulty'].title()}")
                    st.markdown(prob2["statement_md"])

                st.subheader("Visible Test Cases")
                for i, tc in enumerate(prob2["visible_tests"], 1):
                    with st.expander(f"Visible Case #{i}", expanded=True):
                        st.code(f"Input: {tc['input_args']}\nExpected: {tc['expected']}", language="python")

                with st.container(border=True):
                    if st.button("Reveal Hint (Problem 2)", key="btn_m2_hint") and st.session_state["mock_p2_hints"] < 3:
                        st.session_state["mock_p2_hints"] += 1
                        st.rerun()

                    if st.session_state["mock_p2_hints"] > 0:
                        for h in range(st.session_state["mock_p2_hints"]):
                            st.info(f"Hint {h+1}: {prob2['hints'][h]}")

            with col_m2_right:
                with st.container(border=True):
                    st.subheader("Solution Editor")
                    code2 = render_editor(prob2["starter_code"], key="mock_editor_p2", height=440)
                    st.session_state["mock_p2_code"] = code2

                    if st.button("Submit Problem 2", type="primary", disabled=time_expired, key="btn_sub_p2"):
                        res2 = run_solution(code2, prob2)
                        st.session_state["mock_p2_status"] = res2["status"]
                        st.session_state["mock_p2_result"] = res2
                        store.record_attempt(
                            prob2["id"], res2["status"], res2["runtime_ms"],
                            st.session_state["mock_p2_hints"], mode="mock", topic=prob2["topic"]
                        )
                        st.rerun()

                # Display stored result for Tab 2
                res2 = st.session_state.get("mock_p2_result")
                if res2:
                    with st.container(border=True):
                        st.subheader("Judge Results (Problem 2)")
                        if res2["status"] == "pass":
                            st.markdown(f':green-background[**PASS**] **{res2["passed"]}/{res2["total"]}** tests passed (`{res2["runtime_ms"]} ms`)')
                        elif res2["status"] == "fail":
                            st.markdown(f':red-background[**FAIL**] **{res2["passed"]}/{res2["total"]}** tests passed (`{res2["runtime_ms"]} ms`)')
                            for fc in res2.get("failed_cases", []):
                                with st.container(border=True):
                                    st.markdown(f"**Input:** `{fc.get('input_args')}`")
                                    st.markdown(f"**Expected:** `{fc.get('expected')}`")
                                    st.markdown(f"**Got:** `{fc.get('got')}`")
                        else:
                            st.markdown(f':orange-background[**{res2["status"].upper()}**]')
                            st.code(res2.get("stderr", ""), language="text")

        st.markdown("---")
        if st.button("Finish Mock Interview and Generate Scorecard", type="primary"):
            st.session_state["mock_state"] = "completed"
            st.session_state["mock_finish_time"] = time.time()
            st.rerun()

    elif st.session_state["mock_state"] == "completed":
        col_hdr1, col_hdr2 = st.columns([8, 4], vertical_alignment="center")
        with col_hdr1:
            st.markdown(
                """
                <div>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">Technical Interview Simulation</h2>
                    <p style="font-size: 14px; color: #66635A; margin: 0;">Two curated algorithmic problems under 45:00 strict countdown constraint.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.html('<div style="height: 16px;"></div>')

        with st.container(border=True, key="mock_scorecard_card"):
            total_time_min = round((st.session_state["mock_finish_time"] - st.session_state["mock_start_time"]) / 60, 1)
            p_list = st.session_state["mock_problems"]
            session_start_iso = st.session_state.get("mock_start_iso")
            p1_eval = get_mock_problem_evaluation(
                p_list[0]["id"],
                session_start_iso,
                st.session_state.get("mock_p1_result"),
                st.session_state.get("mock_p1_hints", 0),
                store
            )
            p2_eval = get_mock_problem_evaluation(
                p_list[1]["id"],
                session_start_iso,
                st.session_state.get("mock_p2_result"),
                st.session_state.get("mock_p2_hints", 0),
                store
            )
            score = (1 if p1_eval["is_pass"] else 0) + (1 if p2_eval["is_pass"] else 0)

            sc_hdr_left, sc_hdr_right = st.columns([8, 4], vertical_alignment="center")
            with sc_hdr_left:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="background: #DFF3E4; color: #167B48; border: 1px solid rgba(22, 123, 72, 0.25); border-radius: 999px; padding: 2px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                            Simulation Completed
                        </span>
                    </div>
                    <div style="font-family: 'Fraunces', serif; font-size: 26px; font-weight: 700; color: #171712; line-height: 1.25;">
                        Final Interview Scorecard
                    </div>
                    <div style="font-size: 13px; color: #66635A; margin-top: 2px;">
                        Authentic evaluation verified against local judge test suites.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with sc_hdr_right:
                st.markdown(
                    f"""
                    <div style="text-align: right;">
                        <div style="font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: #167B48; font-variant-numeric: tabular-nums;">
                            {score} / 2 Solved
                        </div>
                        <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">
                            Total Time: {total_time_min} min
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.html('<div style="height: 16px;"></div>')

            col_sc1, col_sc2 = st.columns(2, gap="medium")
            with col_sc1:
                prob1_title = p_list[0]["title"]
                if p1_eval["status"] == "pass":
                    p1_badge = '<span style="background: #DFF3E4; color: #167B48; border: 1px solid rgba(22, 123, 72, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">PASS</span>'
                    p1_rt_str = f"<span><strong>Runtime:</strong> {p1_eval['runtime_ms']} ms</span>"
                elif p1_eval["status"] == "fail":
                    p1_badge = '<span style="background: #FFE0E0; color: #C5221F; border: 1px solid rgba(197, 34, 31, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">FAIL</span>'
                    p1_rt_str = f"<span><strong>Runtime:</strong> {p1_eval['runtime_ms']} ms</span>"
                else:
                    p1_badge = '<span style="background: rgba(102, 99, 90, 0.12); color: #66635A; border: 1px solid #E7E1D6; border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">NOT ATTEMPTED</span>'
                    p1_rt_str = "<span><strong>Runtime:</strong> —</span>"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 700; color: #171712;">Problem 1: {prob1_title}</strong>
                            {p1_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A;">Track: {p_list[0]['track'].upper()} · Topic: {p_list[0]['topic']} · {p_list[0]['difficulty'].title()}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px; margin-top: 4px;">
                            {p1_rt_str}
                            <span><strong>Hints Used:</strong> {p1_eval['hints_used']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_sc2:
                prob2_title = p_list[1]["title"]
                if p2_eval["status"] == "pass":
                    p2_badge = '<span style="background: #DFF3E4; color: #167B48; border: 1px solid rgba(22, 123, 72, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">PASS</span>'
                    p2_rt_str = f"<span><strong>Runtime:</strong> {p2_eval['runtime_ms']} ms</span>"
                elif p2_eval["status"] == "fail":
                    p2_badge = '<span style="background: #FFE0E0; color: #C5221F; border: 1px solid rgba(197, 34, 31, 0.25); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">FAIL</span>'
                    p2_rt_str = f"<span><strong>Runtime:</strong> {p2_eval['runtime_ms']} ms</span>"
                else:
                    p2_badge = '<span style="background: rgba(102, 99, 90, 0.12); color: #66635A; border: 1px solid #E7E1D6; border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; white-space: nowrap;">NOT ATTEMPTED</span>'
                    p2_rt_str = "<span><strong>Runtime:</strong> —</span>"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 16px; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 700; color: #171712;">Problem 2: {prob2_title}</strong>
                            {p2_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A;">Track: {p_list[1]['track'].upper()} · Topic: {p_list[1]['topic']} · {p_list[1]['difficulty'].title()}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px; margin-top: 4px;">
                            {p2_rt_str}
                            <span><strong>Hints Used:</strong> {p2_eval['hints_used']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.html('<div style="height: 16px;"></div>')

            scorecard_md = f"""# Mock Interview Scorecard — AI Coding Prep Coach
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Time: {total_time_min} minutes
Overall Score: {score}/2 Solved

## Details
- **Problem 1**: {p_list[0]['title']} ({p_list[0]['topic']})
  - Status: {p1_eval['status'].upper().replace('_', ' ')}
  - Runtime: {f"{p1_eval['runtime_ms']} ms" if p1_eval['runtime_ms'] is not None else "—"}
  - Hints Used: {p1_eval['hints_used']}
- **Problem 2**: {p_list[1]['title']} ({p_list[1]['topic']})
  - Status: {p2_eval['status'].upper().replace('_', ' ')}
  - Runtime: {f"{p2_eval['runtime_ms']} ms" if p2_eval['runtime_ms'] is not None else "—"}
  - Hints Used: {p2_eval['hints_used']}

*Generated locally by AI Coding Prep Coach (Judge: Code, not AI).*
"""
            sc_act1, sc_act2 = st.columns([6, 6], vertical_alignment="center")
            with sc_act1:
                st.download_button(
                    label="Export Results as Markdown",
                    data=scorecard_md,
                    file_name=f"mock_scorecard_{date.today().isoformat()}.md",
                    mime="text/markdown",
                    key="btn_export_markdown",
                )
            with sc_act2:
                if st.button("Start New Mock Session", key="btn_new_mock"):
                    st.session_state["mock_state"] = "unstarted"
                    st.rerun()


# ==============================================================================
# SCREEN 4: DASHBOARD
# ==============================================================================
elif nav_choice == "Dashboard":
    col_dash_head, col_dash_badge = st.columns([8, 4], vertical_alignment="center")
    with col_dash_head:
        st.markdown(
            """<div style="margin-bottom: 8px;">
                <h1 style="font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; color: #171712; margin: 0 0 4px 0; letter-spacing: -0.025em; line-height: 1.2;">
                    Performance and Analytics
                </h1>
                <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #66635A; margin: 0; line-height: 1.5;">
                    Real-time mastery and pass rates derived objectively from SQLite attempts. Zero invented metrics.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_dash_badge:
        st.markdown(
            """<div style="text-align: right;">
                <span class="stat-badge badge-sky" style="font-size: 13px; padding: 6px 14px;">Zero Invented Metrics</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # SQLite metrics query
    with store._get_connection() as conn:
        cur = conn.execute("SELECT COUNT(DISTINCT problem_id) FROM attempts WHERE status = 'pass'")
        solved_count = cur.fetchone()[0] or 0
        cur = conn.execute("SELECT COUNT(*) FROM attempts")
        total_sessions = cur.fetchone()[0] or 0
        cur = conn.execute("SELECT AVG(hints_used) FROM attempts")
        avg_hints_raw = cur.fetchone()[0]
        avg_hints = round(avg_hints_raw, 1) if avg_hints_raw is not None else 0.0

    # Three category-tinted stat cards
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True, key="dash_card_solved"):
            check_svg = get_svg_icon("check", width=22, height=22, stroke="#FFFFFF")
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-green">
                            {check_svg}
                        </div>
                        <span class="stat-badge badge-mint">{solved_count} / {len(all_problems)}</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Solved Problems</span>
                        <span class="stat-numeral">{solved_count}</span>
                        <span class="stat-caption">{solved_count} of {len(all_problems)} curriculum problems solved.</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with col2:
        with st.container(border=True, key="dash_card_sessions"):
            chart_svg = get_svg_icon("bar-chart-3", width=22, height=22, stroke="#FFFFFF")
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-blue">
                            {chart_svg}
                        </div>
                        <span class="stat-badge badge-sky">Recorded</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Practice Sessions</span>
                        <span class="stat-numeral">{total_sessions}</span>
                        <span class="stat-caption">Total code-judged runs recorded in SQLite.</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with col3:
        with st.container(border=True, key="dash_card_hints"):
            sparkles_svg = get_svg_icon("sparkles", width=22, height=22, stroke="#FFFFFF")
            hints_badge = "Zero Hints" if avg_hints == 0 else f"{avg_hints} Avg"
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-amber">
                            {sparkles_svg}
                        </div>
                        <span class="stat-badge badge-butter">{hints_badge}</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Average Hints Used</span>
                        <span class="stat-numeral">{avg_hints:.1f}</span>
                        <span class="stat-caption">Average hints revealed per problem attempt.</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.html('<div style="height: 16px;"></div>')

    # Topic Mastery Chart Card
    with st.container(border=True, key="dashboard_chart_card"):
        st.markdown(
            """<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                        Topic Mastery &amp; Pass Rates
                    </h2>
                    <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #66635A; margin: 0;">
                        Per-category accuracy across DSA and Python tracks with topic-tinted bars.
                    </p>
                </div>
                <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #66635A;">Target Threshold: 80%</span>
            </div>""",
            unsafe_allow_html=True,
        )

        stats = store.topic_stats()
        all_curriculum_topics = sorted(list({p.get("topic") for p in all_problems if p.get("topic")}))
        # Sort attempted topics first, then unattempted alphabetically
        topics_list = sorted(
            all_curriculum_topics,
            key=lambda t: (0 if t in stats and stats[t]["attempts"] > 0 else 1, t),
        )

        tint_palette = ["#1F9D63", "#2273E6", "#B45309", "#6C4CF1", "#E4572E"]
        bar_colors = []
        y_vals = []
        bar_texts = []
        text_colors = []

        for i, t in enumerate(topics_list):
            d = stats.get(t, {"attempts": 0, "passed": 0, "pass_rate": 0.0})
            color = tint_palette[i % len(tint_palette)]
            bar_colors.append(color)
            if d["attempts"] > 0:
                y_vals.append(d["pass_rate"])
                bar_texts.append(f"{d['pass_rate']}% ({d['passed']}/{d['attempts']})")
                text_colors.append("#171712")
            else:
                y_vals.append(0)
                bar_texts.append("NOT STARTED")
                text_colors.append("#66635A")

        try:
            import plotly.graph_objects as go

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=topics_list,
                        y=y_vals,
                        text=bar_texts,
                        textposition="outside",
                        textfont=dict(family="Inter, sans-serif", size=11, color=text_colors),
                        marker_color=bar_colors,
                        cliponaxis=False,
                    )
                ]
            )
            fig.update_layout(
                xaxis=dict(
                    title=dict(text="Topic", font=dict(family="Inter, sans-serif", size=13, color="#66635A")),
                    gridcolor="#E7E1D6",
                    showline=True,
                    linecolor="#E7E1D6",
                    tickfont=dict(family="Inter, sans-serif", size=12, color="#171712"),
                    tickangle=-25,
                ),
                yaxis=dict(
                    title=dict(text="Pass Rate (%)", font=dict(family="Inter, sans-serif", size=13, color="#66635A")),
                    range=[0, 115],
                    gridcolor="#E7E1D6",
                    showline=True,
                    linecolor="#E7E1D6",
                    zeroline=True,
                    zerolinecolor="#E7E1D6",
                    tickfont=dict(family="Inter, sans-serif", size=12, color="#171712"),
                ),
                margin=dict(l=40, r=40, t=30, b=60),
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#171712"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            chart_data = {t: y for t, y in zip(topics_list, y_vals)}
            st.bar_chart(chart_data)

    st.html('<div style="height: 16px;"></div>')

    with st.container(border=True, key="dashboard_table_card"):
        st.markdown(
            """<div style="margin-bottom: 16px;">
                <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                    Topic Breakdown Table
                </h2>
                <p style="font-family: 'Inter', sans-serif; font-size: 14px; color: #66635A; margin: 0;">
                    Granular breakdown of curriculum topics, tracks, mastery progress, and readiness status.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

        with store._get_connection() as conn:
            cur = conn.execute("SELECT DISTINCT problem_id FROM attempts WHERE status = 'pass'")
            solved_problem_ids = {row[0] for row in cur.fetchall()}

        topic_problems: dict[str, list[dict[str, Any]]] = {}
        for p in all_problems:
            t = p.get("topic", "misc")
            if t not in topic_problems:
                topic_problems[t] = []
            topic_problems[t].append(p)

        rows_html = []
        for i, t in enumerate(topics_list):
            probs = topic_problems.get(t, [])
            total_in_topic = len(probs)
            solved_in_topic = sum(1 for p in probs if p["id"] in solved_problem_ids)
            track_name = probs[0].get("track", "DSA").upper() if probs else "DSA"
            track_badge_class = "badge-lilac" if track_name == "DSA" else "badge-butter"

            d = stats.get(t, {"attempts": 0, "passed": 0, "pass_rate": 0.0})
            attempts = d["attempts"]
            pass_rate = d["pass_rate"]
            bar_color = tint_palette[i % len(tint_palette)]

            if attempts == 0:
                ratio_str = f'<span style="color: #66635A; font-weight: 600;">0 / {total_in_topic}</span>'
                bar_html = f"""<div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: #E7E1D6; border-radius: 999px; height: 10px; width: 120px; overflow: hidden; flex-shrink: 0;">
                        <div style="background: #E7E1D6; width: 0%; height: 100%;"></div>
                    </div>
                    <span style="font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; color: #66635A;">—</span>
                </div>"""
                status_chip = '<span class="stat-badge" style="background-color: rgba(102, 99, 90, 0.12); color: #66635A; white-space: nowrap !important; display: inline-block;">NOT STARTED</span>'
            else:
                ratio_str = f'<span style="color: #171712; font-weight: 600;">{solved_in_topic} / {total_in_topic}</span>'
                bar_html = f"""<div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: #E7E1D6; border-radius: 999px; height: 10px; width: 120px; overflow: hidden; flex-shrink: 0;">
                        <div style="background: {bar_color}; width: {min(pass_rate, 100.0)}%; height: 100%; border-radius: 999px;"></div>
                    </div>
                    <span style="font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; color: #171712;">{pass_rate:.1f}%</span>
                </div>"""
                if pass_rate >= 80.0:
                    status_chip = '<span class="stat-badge badge-mint" style="white-space: nowrap !important; display: inline-block;">MASTERED</span>'
                else:
                    status_chip = '<span class="stat-badge badge-sky" style="white-space: nowrap !important; display: inline-block;">IN PROGRESS</span>'

            rows_html.append(f"""<tr>
                <td><strong>{t}</strong></td>
                <td><span class="stat-badge {track_badge_class}">{track_name}</span></td>
                <td style="font-variant-numeric: tabular-nums;">{ratio_str}</td>
                <td>{bar_html}</td>
                <td style="text-align: right; white-space: nowrap !important; min-width: 140px;">{status_chip}</td>
            </tr>""")

        table_markup = f"""<table class="dashboard-table">
            <thead>
                <tr>
                    <th>Topic</th>
                    <th>Track</th>
                    <th>Solved / Total</th>
                    <th>Mastery Progress</th>
                    <th style="text-align: right;">Status</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows_html)}
            </tbody>
        </table>"""

        st.markdown(table_markup, unsafe_allow_html=True)
