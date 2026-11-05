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


@lru_cache(maxsize=1)
def get_global_css() -> str:
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
        background-color: #FAF8F5 !important;
    }

    /* Direction A Sidebar Navigation: Keyed Radio Pills */
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
        background-color: #EFECE6 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:hover p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:hover span {
        color: #171712 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked),
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) {
        background-color: #DFF3E4 !important;
        color: #167B48 !important;
        font-weight: 600 !important;
    }
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(input:checked) span,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) p,
    .st-key-nav_sidebar_radio div[role="radiogroup"] label:has(div[aria-checked="true"]) span {
        color: #167B48 !important;
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
        background-color: rgba(22, 123, 72, 0.15) !important;
        color: #167B48 !important;
    }
    .badge-sky {
        background-color: rgba(29, 94, 194, 0.15) !important;
        color: #1D5EC2 !important;
    }
    .badge-butter {
        background-color: rgba(180, 83, 9, 0.15) !important;
        color: #9A3412 !important;
    }
    .badge-rose {
        background-color: rgba(197, 34, 31, 0.15) !important;
        color: #C5221F !important;
    }
    .badge-lilac {
        background-color: rgba(89, 50, 234, 0.15) !important;
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
        padding: 14px 20px;
        background-color: #FBFAF7;
        border: 1px solid #E7E1D6;
        border-radius: 16px;
        margin-bottom: 8px;
    }

    /* Monospace Light Code Block */
    .code-block-light {
        background-color: #F4F1EA !important;
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
        background-color: #DDD6FE !important;
        border-color: #5932EA !important;
        color: #4C1D95 !important;
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
    """

    return f"<style>\n{font_css}\n{rules_css}\n</style>"


st.html(get_global_css())


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


def render_editor(code: str, key: str, height: int = 440) -> str:
    """
    Renders code editor via streamlit-code-editor (Ace editor wrapper)
    with debounced two-way binding and textarea fallback.
    Always ensures prefilled code is preserved.
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
        effective_height = max(height, 440)
        editor_response = code_editor(
            code,
            lang="python",
            theme="one_dark",
            height=effective_height,
            key=key,
            buttons=editor_custom_btns,
            options={"wrap": True, "showLineNumbers": True},
            props={"style": {"backgroundColor": "#14161A", "color": "#F2F2ED", "borderRadius": "8px"}},
            response_mode="debounce",
        )
        if isinstance(editor_response, dict) and editor_response.get("text", "").strip():
            return editor_response["text"]
        elif isinstance(editor_response, str) and editor_response.strip():
            return editor_response
        return code
    except Exception:
        effective_height = max(height, 440)
        return st.text_area(
            "Code Editor",
            value=code,
            height=effective_height,
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
            st.markdown(
                f"""<div class="stat-card-inner">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                        <div class="stat-icon-tile tile-green">
                            {flame_svg}
                        </div>
                        <span class="stat-badge badge-mint">Active</span>
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">Active Streak</span>
                        <span class="stat-numeral">{streak_count} {streak_unit}</span>
                        <span class="stat-caption">Practice tomorrow to reach a {streak_count + 1}-day streak.</span>
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
    # Filter Row Card using single named mechanism: st.container(border=True, key="practice_filter_card")
    with st.container(border=True, key="practice_filter_card"):
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 4])
        tracks = ["All"] + sorted({p["track"] for p in all_problems})
        difficulties = ["All", "easy", "medium", "hard"]
        topics = ["All"] + sorted({p["topic"] for p in all_problems})

        selected_track = col_f1.selectbox(
            "Track",
            tracks,
            format_func=lambda x: x.upper() if x != "All" else "All Tracks"
        )
        selected_diff = col_f2.selectbox(
            "Difficulty",
            difficulties,
            format_func=lambda x: x.title() if x != "All" else "All Difficulties"
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
        selected_id = col_f4.selectbox(
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
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid #E7E1D6;">
              <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">Track:</span>
                <span class="stat-badge badge-{track_badge_class}">{current_problem['track'].upper()}</span>
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">Topic:</span>
                <span class="stat-badge badge-sky">{current_problem['topic'].title()}</span>
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">Difficulty:</span>
                <span class="stat-badge badge-{diff_badge_class}">{current_problem['difficulty'].title()}</span>
              </div>
              <div style="font-size: 13px; color: #66635A; font-family: 'Inter', sans-serif;">
                Problem <strong>{curr_pos} of {total_in_lib}</strong> in Library
              </div>
            </div>
            """
        )

    # Workbench layout: Left narrower (4 cols), Right wide & primary (7 cols)
    left_col, right_col = st.columns([4, 7], gap="large")

    with left_col:
        # Problem Statement Card using single named mechanism: st.container(border=True, key="practice_statement_card")
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

            # Starter function signature box & constraints
            sig_line = current_problem["starter_code"].splitlines()[0] if current_problem.get("starter_code") else f"def {current_problem['function_name']}():"
            st.html(
                f"""
                <div style="margin-top: 14px;">
                  <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A; display: block; margin-bottom: 6px;">Starter Function Signature</span>
                  <div class="code-block-light">
                    {sig_line}
                  </div>
                </div>
                <div style="margin-top: 12px; font-size: 13px; color: #66635A; font-family: 'Inter', sans-serif;">
                  Execution timeout: <strong>{current_problem.get('time_limit_sec', 3.0)}s</strong> · Sandbox isolated
                </div>
                """
            )

        # Visible Test Cases
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
                      <div style="display: flex; align-items: center; gap: 8px;">
                        {check_icon_svg}
                        <span style="font-size: 13px; font-weight: 700; color: #167B48; text-transform: uppercase; letter-spacing: 0.04em;">
                          Visible Test Case #{i}
                        </span>
                      </div>
                      <span class="stat-badge badge-mint">Provided</span>
                    </div>
                    <div class="code-block-light" style="background: rgba(255, 255, 255, 0.7); border-color: rgba(22, 123, 72, 0.2);">
                      Input: {args_repr}<br>
                      Expected: {tc['expected']}
                    </div>
                    """
                )

        # Progressive Hint Ladder
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
                    <span style="font-size: 13px; font-weight: 700; color: #9A3412; text-transform: uppercase; letter-spacing: 0.04em;">
                      Hint Ladder ({current_level} of {total_hints} Revealed)
                    </span>
                  </div>
                </div>
                """
            )

            col_h1, col_h2 = st.columns(2)
            with col_h1:
                if st.button("Reveal Next Hint", key=f"btn_hint_{current_problem['id']}", disabled=(current_level >= total_hints), use_container_width=True):
                    st.session_state[hint_key] += 1
                    st.rerun()
            with col_h2:
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

        # Problem Editor Card using single named mechanism: st.container(border=True, key="practice_editor_card")
        with st.container(border=True, key="practice_editor_card"):
            # Lilac Header Strip
            st.html(
                """
                <div class="editor-header-strip" style="background-color: #E8E2FF; border-bottom: 1px solid rgba(89, 50, 234, 0.15); padding: 12px 20px; margin: -24px -24px 16px -24px; border-radius: 23px 23px 0 0; display: flex; justify-content: space-between; align-items: center;">
                  <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="display: flex; gap: 6px;">
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #EF4444; display: inline-block;"></span>
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
                      <span style="width: 10px; height: 10px; border-radius: 50%; background: #22C55E; display: inline-block;"></span>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: #5932EA; text-transform: uppercase; letter-spacing: 0.04em;">Solution Editor · Python 3.12</span>
                  </div>
                  <span style="font-family: 'Inter', sans-serif; font-size: 12px; color: #5932EA; font-weight: 600;">Subprocess Sandbox (3.0s Timeout)</span>
                </div>
                """
            )

            user_code = render_editor(initial_code, key=editor_key, height=440)
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


# ==============================================================================
# SCREEN 3: MOCK INTERVIEW ARENA (LANE T & U5)
# ==============================================================================
elif nav_choice == "Mock Interview":
    st.header("Mock Interview Arena")

    # Mock interview session state
    if "mock_state" not in st.session_state:
        st.session_state["mock_state"] = "unstarted"  # unstarted | running | completed

    if st.query_params.get("mock_state", "").lower() == "completed":
        st.session_state["mock_state"] = "completed"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time() - 25 * 60
            st.session_state["mock_finish_time"] = time.time()
            st.session_state["mock_problems"] = [problems_by_id["two-sum"], problems_by_id["flatten-nested-dict"]]
            st.session_state["mock_p1_status"] = "pass"
            st.session_state["mock_p2_status"] = "pass"
            st.session_state["mock_p1_hints"] = 1
            st.session_state["mock_p2_hints"] = 0

    if st.query_params.get("mock_state", "").lower() == "running":
        st.session_state["mock_state"] = "running"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time()
            st.session_state["mock_duration_sec"] = 45 * 60
            medium_dsas = [p for p in all_problems if p["track"] == "dsa" and p["difficulty"] == "medium"]
            practicals = [p for p in all_problems if p["track"] == "python"]
            p1 = medium_dsas[0] if medium_dsas else all_problems[0]
            p2 = practicals[0] if practicals else all_problems[1]
            st.session_state["mock_problems"] = [p1, p2]
            st.session_state["mock_p1_status"] = "unsolved"
            st.session_state["mock_p2_status"] = "unsolved"
            st.session_state["mock_p1_hints"] = 0
            st.session_state["mock_p2_hints"] = 0

    if st.session_state["mock_state"] == "unstarted":
        st.write(
            "A 45-minute timed simulation of a technical coding round consisting of 2 problems. "
            "The timer ticks down automatically in real time. Hints and time taken are tracked on your scorecard."
        )
        if st.button("Start 45-Minute Mock Interview", type="primary"):
            medium_dsas = [p for p in all_problems if p["track"] == "dsa" and p["difficulty"] == "medium"]
            practicals = [p for p in all_problems if p["track"] == "python"]

            p1 = medium_dsas[0] if medium_dsas else all_problems[0]
            p2 = practicals[0] if practicals else all_problems[1]

            st.session_state["mock_state"] = "running"
            st.session_state["mock_start_time"] = time.time()
            st.session_state["mock_duration_sec"] = 45 * 60
            st.session_state["mock_problems"] = [p1, p2]
            st.session_state["mock_p1_status"] = "unsolved"
            st.session_state["mock_p2_status"] = "unsolved"
            st.session_state["mock_p1_hints"] = 0
            st.session_state["mock_p2_hints"] = 0
            st.session_state["mock_p1_result"] = None
            st.session_state["mock_p2_result"] = None
            st.rerun()

    elif st.session_state["mock_state"] == "running":
        p_list = st.session_state["mock_problems"]

        # Header Row: Title on left, Autorefresh Timer Fragment on right
        col_hdr1, col_hdr2 = st.columns([7, 3])
        with col_hdr1:
            st.subheader("Technical Round in Progress")
            st.caption("Complete both problems before the timer expires.")

        # Native Streamlit fragment updating every 1 second (Lane T)
        @st.fragment(run_every=1.0)
        def render_live_timer():
            start = st.session_state.get("mock_start_time", time.time())
            duration = st.session_state.get("mock_duration_sec", 45 * 60)
            mins, secs, is_expired = calculate_remaining_time(start, duration, time.time())
            if is_expired:
                st.session_state["mock_time_expired"] = True
                st.markdown(
                    "<div style='font-family: monospace; font-size: 1.85rem; font-weight: 700; text-align: right; color: #EF4444;'>"
                    "00:00 (EXPIRED)</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='font-family: monospace; font-size: 1.85rem; font-weight: 700; text-align: right; color: #F8FAFC;'>"
                    f"TIME: {mins:02d}:{secs:02d}</div>",
                    unsafe_allow_html=True
                )

        with col_hdr2:
            render_live_timer()

        st.markdown("---")

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
        with st.container(border=True):
            st.subheader("Mock Interview Scorecard")
            total_time_min = round((st.session_state["mock_finish_time"] - st.session_state["mock_start_time"]) / 60, 1)
            p_list = st.session_state["mock_problems"]
            s1 = st.session_state["mock_p1_status"]
            s2 = st.session_state["mock_p2_status"]
            h1 = st.session_state["mock_p1_hints"]
            h2 = st.session_state["mock_p2_hints"]

            score = (1 if s1 == "pass" else 0) + (1 if s2 == "pass" else 0)

            st.markdown(f"""
            ### Overall Score: **{score} / 2 Problems Solved**
            - **Total Time Taken**: `{total_time_min} minutes`
            - **Problem 1 ({p_list[0]['title']})**: Status: `{s1.upper()}`, Hints Used: `{h1}`
            - **Problem 2 ({p_list[1]['title']})**: Status: `{s2.upper()}`, Hints Used: `{h2}`
            """)

            # Markdown export
            scorecard_md = f"""# Mock Interview Scorecard — AI Coding Prep Coach
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Time: {total_time_min} minutes
Overall Score: {score}/2 Solved

## Details
- **Problem 1**: {p_list[0]['title']} ({p_list[0]['topic']})
  - Status: {s1.upper()}
  - Hints Used: {h1}
- **Problem 2**: {p_list[1]['title']} ({p_list[1]['topic']})
  - Status: {s2.upper()}
  - Hints Used: {h2}

*Generated locally by AI Coding Prep Coach (Judge: Code, not AI).*
"""
            st.download_button(
                label="Download Scorecard (Markdown)",
                data=scorecard_md,
                file_name=f"mock_scorecard_{date.today().isoformat()}.md",
                mime="text/markdown"
            )

            if st.button("Start New Mock Session"):
                st.session_state["mock_state"] = "unstarted"
                st.rerun()


# ==============================================================================
# SCREEN 4: DASHBOARD
# ==============================================================================
elif nav_choice == "Dashboard":
    with st.container(border=True):
        st.subheader("Performance and Analytics")
        st.caption("All metrics computed strictly from SQLite history. Zero invented metrics.")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric("Current Streak", f"{streak_count} Days")
    with col2:
        with st.container(border=True):
            st.metric("Due for Review", f"{len(due_list)} Problems")

    stats = store.topic_stats()
    total_attempts = sum(s["attempts"] for s in stats.values())
    total_passed = sum(s["passed"] for s in stats.values())
    overall_rate = round((total_passed / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
    with col3:
        with st.container(border=True):
            st.metric("Overall Pass Rate", f"{overall_rate}% ({total_passed}/{total_attempts})")

    with st.container(border=True):
        st.subheader("Topic Mastery and Pass Rates")

        if not stats:
            st.info("No practice data available yet. Solve problems in Practice Arena to populate your dashboard!")
        else:
            try:
                import plotly.graph_objects as go
                topics_list = list(stats.keys())
                pass_rates = [stats[t]["pass_rate"] for t in topics_list]

                fig = go.Figure(data=[
                    go.Bar(
                        x=topics_list,
                        y=pass_rates,
                        text=[f"{rate}% ({stats[t]['passed']}/{stats[t]['attempts']})" for t, rate in zip(topics_list, pass_rates)],
                        textposition="auto",
                        marker_color="#22C55E"
                    )
                ])
                fig.update_layout(
                    title="Pass Rate by Topic (%)",
                    xaxis_title="Topic",
                    yaxis_title="Pass Rate (%)",
                    yaxis={"range": [0, 105], "gridcolor": "#334155"},
                    xaxis={"gridcolor": "#334155"},
                    margin={"l": 40, "r": 40, "t": 40, "b": 40},
                    height=400,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#F8FAFC"}
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                chart_data = {t: stats[t]["pass_rate"] for t in stats}
                st.bar_chart(chart_data)

    st.subheader("Topic Breakdown Table")
    if stats:
        table_rows = []
        for t, d in stats.items():
            table_rows.append({
                "Topic": t,
                "Attempts": d["attempts"],
                "Passed": d["passed"],
                "Pass Rate (%)": f"{d['pass_rate']}%"
            })
        st.table(table_rows)
    else:
        st.caption("No topic records found in database.")
