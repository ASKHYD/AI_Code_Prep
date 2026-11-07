"""
AI Coding Prep Coach — Topbar Workbench Implementation.
Zero-cost, local-only coding interview preparation platform.
The judge is CODE, not AI.
"""

from __future__ import annotations

import base64
import re
import sys
import time
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from auth_store import AuthStore, send_smtp_email
from coach.judge import run_solution
from coach.llm_hints import explain_hint, review_code
from coach.problems import load_all_problems
from coach.review import run_ruff_lint
from coach.store import CoachStore
from coach.timer import calculate_remaining_time
from coach.interleaving import build_interleaved_queue

# Page configuration with collapsed sidebar
st.set_page_config(
    page_title="AI Prep Coach",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONTS_DIR = Path(__file__).parent / "assets" / "fonts"
ICONS_DIR = Path(__file__).parent / "assets" / "icons"

FONT_DEFINITIONS = [
    ("DM Serif Display", "normal", 400, "dm-serif-display-latin-400-normal.woff2"),
    ("Plus Jakarta Sans", "normal", 400, "plus-jakarta-sans-latin-400-normal.woff2"),
    ("Plus Jakarta Sans", "normal", 500, "plus-jakarta-sans-latin-500-normal.woff2"),
    ("Plus Jakarta Sans", "normal", 600, "plus-jakarta-sans-latin-600-normal.woff2"),
    ("Plus Jakarta Sans", "normal", 700, "plus-jakarta-sans-latin-700-normal.woff2"),
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
                    (problem_id, session_start_iso),
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
    """Builds offline base64 @font-face rules and Direction A Topbar Workbench CSS."""
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
    /* Body & UI defaults: Terracotta Editorial (Plus Jakarta Sans) */
    html, body, [class*="css"], .stMarkdown, p, span, label, input, button {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #2C1810;
    }

    /* Display headings in DM Serif Display */
    h1, h2, h3, h4, .stTitle, .stSubheader, [data-testid="stHeader"],
    h1 *, h2 *, h3 *, h4 *, .stTitle *, .stSubheader *, .font-display {
        font-family: 'DM Serif Display', Georgia, serif !important;
        color: #2C1810 !important;
    }

    /* Monospace for code literals, editors, and syntax */
    code, pre, .stCode, code *, pre *, .signature-pre, .timer-mono {
        font-family: 'JetBrains Mono', monospace !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-x: hidden !important;
    }

    /* Metric numerals in tabular semibold Plus Jakarta Sans */
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *, .stat-number, .stat-number * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-feature-settings: 'tnum' 1 !important;
        font-variant-numeric: tabular-nums !important;
        letter-spacing: -0.02em;
    }

    /* Suppress Streamlit Sidebar entirely */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"],
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarHeader"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        visibility: hidden !important;
    }

    /* Suppress default Streamlit header bar */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }

    /* Hide Streamlit heading anchor icons globally across ALL screens */
    [data-testid="stHeaderActionElements"],
    [data-testid="stHeadingAnchor"],
    .stHeadingWithActionElements button,
    a.anchor-link {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Kill top void in main container */
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Canvas: Sun-white #FFF8F0 */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        margin-left: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        background-color: #FFF8F0 !important;
    }

    [data-testid="stAppViewBlockContainer"] {
        padding: 0 24px 32px 24px !important;
        max-width: 100% !important;
    }

    /* Terracotta Primary Action Buttons */
    button[kind="primary"], .stButton > button[kind="primary"], .btn-terracotta {
        border-radius: 9999px !important;
        white-space: nowrap !important;
        padding: 10px 24px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        background-color: #C2452D !important;
        border: 1px solid #C2452D !important;
        color: #FFF8F0 !important;
        transition: transform 150ms ease-out, background-color 150ms ease-out !important;
    }
    button[kind="primary"] p, button[kind="primary"] span {
        color: #FFF8F0 !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        background-color: #A83822 !important;
        border-color: #A83822 !important;
    }
    button[kind="primary"]:active {
        transform: scale(0.97) !important;
    }

    /* Secondary outline buttons */
    button[kind="secondary"], .stButton > button:not([kind="primary"]) {
        border-radius: 9999px !important;
        border: 1px solid rgba(74, 25, 66, 0.15) !important;
        background-color: #FFFFFF !important;
        color: #2C1810 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: transform 150ms ease-out, border-color 150ms ease-out !important;
    }
    button[kind="secondary"]:hover, .stButton > button:not([kind="primary"]):hover {
        border-color: #C2452D !important;
        color: #C2452D !important;
    }
    button[kind="secondary"]:active {
        transform: scale(0.97) !important;
    }

    /* Topbar Navbar: Terracotta System */
    .topbar {
        position: sticky;
        top: 0;
        z-index: 999;
        margin: 0 -2rem 24px -2rem;
        min-height: 56px;
        background-color: #FFF8F0;
        border-bottom: 1px solid rgba(74, 25, 66, 0.10);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 24px;
        width: 100%;
        box-sizing: border-box;
    }
    .topbar-left {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }
    .topbar-brand {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 22px;
        font-weight: 400;
        color: #2C1810;
        text-decoration: none;
        white-space: nowrap;
        line-height: 1;
    }
    .topbar-center {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
    }
    .nav-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        font-size: 13.5px;
        font-weight: 500;
        color: #735A50;
        text-decoration: none;
        border-radius: 9999px;
        transition: background-color 150ms ease-out, color 150ms ease-out;
        white-space: nowrap;
    }
    .nav-pill:hover {
        background-color: rgba(74, 25, 66, 0.05);
        color: #2C1810;
    }
    .nav-pill.active {
        background-color: #FDECE9;
        color: #C2452D;
        font-weight: 700;
        border: 1px solid rgba(194, 69, 45, 0.25);
    }
    .topbar-right {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        font-feature-settings: 'tnum' 1;
    }
    .status-chip-streak {
        background-color: #EFF4E4;
        color: #38451D;
        border: 1px solid rgba(107, 127, 59, 0.30);
    }
    .status-chip-due {
        background-color: #FDECE9;
        color: #C2452D;
        border: 1px solid rgba(194, 69, 45, 0.30);
    }
    .btn-logout {
        background: transparent;
        border: none;
        color: #735A50;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 6px;
        text-decoration: none;
    }
    .btn-logout:hover {
        color: #C2452D;
        background: rgba(194, 69, 45, 0.06);
    }

    /* Bento 24px Container Cards */
    div.st-key-home_card_streak,
    div.st-key-home_card_due,
    div.st-key-home_card_retention,
    div.st-key-dash_card_attempts,
    div.st-key-dash_card_passrate,
    div.st-key-dash_card_practiced {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(74, 25, 66, 0.10) !important;
        border-radius: 24px !important;
        padding: 22px 24px !important;
        transition: transform 150ms ease-out !important;
    }
    div.st-key-home_card_streak:hover,
    div.st-key-home_card_due:hover,
    div.st-key-home_card_retention:hover,
    div.st-key-dash_card_attempts:hover,
    div.st-key-dash_card_passrate:hover,
    div.st-key-dash_card_practiced:hover {
        transform: translateY(-2px) !important;
    }

    .stat-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .stat-label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #735A50 !important;
    }
    .stat-value {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 34px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #2C1810 !important;
        font-feature-settings: 'tnum' 1 !important;
        line-height: 1.1 !important;
        margin: 4px 0 6px 0 !important;
    }
    .stat-desc {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
        color: #735A50 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    /* Sandy Quiet Panel Strip */
    .panel-quiet {
        background-color: #E8D5B7;
        border: 1px solid rgba(74, 25, 66, 0.10);
        border-radius: 16px;
        padding: 16px 20px;
        color: #2C1810;
    }

    /* Badges */
    .stat-badge {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        border-radius: 9999px !important;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        white-space: nowrap !important;
    }
    .badge-olive {
        background-color: #EFF4E4 !important;
        border: 1px solid rgba(107, 127, 59, 0.35) !important;
        color: #38451D !important;
    }
    .badge-amber {
        background-color: #FEF3C7 !important;
        border: 1px solid rgba(180, 83, 9, 0.35) !important;
        color: #92400E !important;
    }
    .badge-terracotta {
        background-color: #FDECE9 !important;
        border: 1px solid rgba(194, 69, 45, 0.35) !important;
        color: #C2452D !important;
    }
    .badge-blue {
        background-color: #E6F0FA !important;
        border: 1px solid rgba(21, 101, 192, 0.35) !important;
        color: #1565C0 !important;
    }
    .badge-quiet {
        background-color: rgba(115, 90, 80, 0.10) !important;
        border: 1px solid rgba(115, 90, 80, 0.20) !important;
        color: #735A50 !important;
    }

    /* Legacy compatibility badge names */
    .badge-mint { background-color: #EFF4E4 !important; border: 1px solid rgba(107, 127, 59, 0.35) !important; color: #38451D !important; }
    .badge-rose { background-color: #FDECE9 !important; border: 1px solid rgba(194, 69, 45, 0.35) !important; color: #C2452D !important; }

    /* Problem Cards & Bento Tables */
    div.st-key-home_queue_card,
    div.st-key-practice_problem_card,
    div.st-key-mock_problem_card,
    div.st-key-dash_table_card {
        background: #FFFFFF !important;
        border: 1px solid rgba(74, 25, 66, 0.10) !important;
        border-radius: 24px !important;
        padding: 24px 28px !important;
    }

    .queue-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .queue-table th {
        text-align: left;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #735A50;
        padding: 12px 16px;
        border-bottom: 1px solid rgba(74, 25, 66, 0.10);
    }
    .queue-row td {
        padding: 16px;
        border-bottom: 1px solid rgba(74, 25, 66, 0.08);
        font-size: 13.5px;
        vertical-align: middle;
        background: #FFFFFF;
    }
    .queue-row:last-child td {
        border-bottom: none;
    }
    .queue-row:hover td {
        background: #FFFDF9;
    }
    .queue-problem-name {
        font-family: 'DM Serif Display', Georgia, serif;
        font-weight: 400;
        font-size: 17px;
        color: #2C1810;
        line-height: 1.25;
    }
    .queue-problem-sub {
        font-size: 12px;
        color: #735A50;
        margin-top: 2px;
    }

    /* Dark Code Editor Anchor */
    div.st-key-practice_editor_card,
    div.st-key-mock_editor_card {
        background: #1E1E1E !important;
        border: 1px solid #1E1E1E !important;
        border-radius: 24px !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    .editor-strip {
        background: #1E1E1E;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 10px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .editor-strip-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #FFF8F0;
    }
    .editor-strip-right {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #A38C82;
    }
    .editor-action-row {
        background: #1E1E1E;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding: 10px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Output Card */
    div.st-key-practice_output_card,
    div.st-key-mock_output_card {
        background: #FFFFFF !important;
        border: 1px solid rgba(74, 25, 66, 0.10) !important;
        border-radius: 24px !important;
        overflow: hidden !important;
        padding: 0 !important;
        margin-top: 16px !important;
    }
    .verdict-band {
        padding: 16px 20px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .verdict-band-pass {
        background: #EFF4E4;
        border-bottom: 1px solid rgba(107, 127, 59, 0.35);
        color: #38451D;
    }
    .verdict-band-fail {
        background: #FDECE9;
        border-bottom: 1px solid rgba(194, 69, 45, 0.35);
        color: #C2452D;
    }

    /* Slim problem picker row */
    .filter-strip-card {
        background: #FFFFFF;
        border: 1px solid rgba(74, 25, 66, 0.10);
        border-radius: 16px;
        padding: 8px 16px;
        margin-bottom: 16px;
    }
    .st-key-btn_picker_prev button,
    .st-key-btn_picker_next button,
    div[data-testid="stColumn"]:has(.st-key-btn_picker_prev) button,
    div[data-testid="stColumn"]:has(.st-key-btn_picker_next) button {
        padding: 6px 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        min-width: 44px !important;
        white-space: nowrap !important;
        border-radius: 9999px !important;
    }
    .signature-card {
        margin-top: 14px;
        margin-bottom: 14px;
    }
    .signature-subhead {
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: #735A50 !important;
        display: block !important;
        margin-bottom: 6px !important;
    }
    .signature-pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
        margin: 0 !important;
        padding: 12px 16px !important;
        background: #FFF8F0 !important;
        border: 1px solid rgba(74, 25, 66, 0.10) !important;
        border-radius: 12px !important;
        color: #2C1810 !important;
    }
    """
    return f"<style>\n{font_css}\n{rules_css}\n</style>"


# Svg icon loader
@lru_cache(maxsize=128)
def get_svg_icon(
    name: str,
    width: int = 18,
    height: int = 18,
    stroke: str | None = None,
    stroke_width: float | None = None,
    extra_class: str = "",
) -> str:
    """Loads an SVG icon from assets/icons/ and returns inline SVG markup."""
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
    s = CoachStore(db_path="coach.db")
    s.migrate_history_to_fsrs()
    return s


store = get_store()

# Load all problems
@st.cache_data
def get_problems() -> list[dict[str, Any]]:
    problems = load_all_problems("data/problems")
    return [p.model_dump() for p in problems]


def render_problem_statement(problem: dict) -> None:
    """
    Renders problem statement prose, starter signature card, and IO specs.
    Governed by R1/R2: starter_code line 1 is the single source of truth for the signature.
    Removes any markdown '### Function Signature' heading/block from statement_md.
    """
    md = problem.get("statement_md", "")
    sig_line = (
        problem["starter_code"].splitlines()[0].strip()
        if problem.get("starter_code")
        else f"def {problem.get('function_name', 'solve')}():"
    )

    pattern = re.compile(r"###\s*Function Signature\s*```(?:python)?\s*[\r\n]+(.*?)```", re.DOTALL)
    m = pattern.search(md)
    if m:
        prose_before = md[:m.start()].strip()
        rest_after = md[m.end():].strip()
    else:
        prose_before = md
        rest_after = ""

    if prose_before:
        st.markdown(prose_before)

    st.html(
        f"""
        <div class="signature-card">
            <span class="signature-subhead">STARTER FUNCTION SIGNATURE</span>
            <pre class="signature-pre">{sig_line}</pre>
        </div>
        """
    )

    if rest_after:
        st.markdown(rest_after)

    st.html(
        f"""
        <div style="margin-top: 12px; font-size: 13px; color: #66635A; font-family: 'Inter', sans-serif;">
            Execution timeout: <strong>{problem.get('time_limit_sec', 3.0)}s</strong> · Sandbox isolated
        </div>
        """
    )


all_problems = get_problems()
problems_by_id = {p["id"]: p for p in all_problems}


def render_editor(code: str, key: str, height: str | int = "450px") -> str:
    """
    Renders code editor via streamlit-code-editor (Ace editor wrapper)
    with debounced two-way binding and textarea fallback.
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
                "style": {"top": "0.4rem", "right": "0.4rem"},
            }
        ]
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
            help="Using monospace editor.",
        )


def render_topbar(current_nav: str, streak_count: int, due_count: int):
    """Renders the official Terracotta Topbar with Logo Variant A, live chips, and logout action."""
    active_home = "active" if current_nav == "Home" else ""
    active_practice = "active" if current_nav == "Practice Arena" else ""
    active_mock = "active" if current_nav == "Mock Interview" else ""
    active_dash = "active" if current_nav == "Dashboard" else ""

    streak_str = f"{streak_count}d" if streak_count > 0 else "0d"

    # Logo Variant A (28x28 inline SVG): terracotta tile, serif "A", olive dot
    logo_svg = """<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="AI Prep Coach Logo">
      <rect width="28" height="28" rx="7.28" fill="#C2452D"/>
      <text x="13.5" y="20.5" font-family="'DM Serif Display', Georgia, serif" font-size="20" fill="#FFF8F0" text-anchor="middle">A</text>
      <circle cx="21" cy="21" r="2.2" fill="#6B7F3B"/>
    </svg>"""

    flame_svg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"/></svg>'
    cal_svg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/></svg>'

    topbar_html = f"""
    <header class="topbar">
      <div class="topbar-left">
        <a href="?screen=home" style="display: flex; align-items: center; gap: 10px; text-decoration: none;" target="_self">
          {logo_svg}
          <span class="topbar-brand">AI Prep Coach</span>
        </a>
      </div>
      <nav class="topbar-center" aria-label="Main Navigation">
        <a href="?screen=home" class="nav-pill {active_home}" target="_self">Home</a>
        <a href="?screen=practice" class="nav-pill {active_practice}" target="_self">Practice Arena</a>
        <a href="?screen=mock" class="nav-pill {active_mock}" target="_self">Mock Interview</a>
        <a href="?screen=dashboard" class="nav-pill {active_dash}" target="_self">Dashboard</a>
      </nav>
      <div class="topbar-right">
        <div class="status-chip status-chip-streak" title="Active Streak (yesterday-anchored)">
          {flame_svg}
          <span>{streak_str}</span>
        </div>
        <div class="status-chip status-chip-due" title="Problems Due for Review (FSRS)">
          {cal_svg}
          <span>{due_count} due</span>
        </div>
        <a href="?logout=true" class="btn-logout" target="_self" title="Log out of current session">Logout</a>
      </div>
    </header>
    """
    st.html(topbar_html)


def render_login_screen(auth_store_instance: AuthStore) -> None:
    """Renders the authentic Terracotta login card matching mockups/terracotta/login.html."""
    st.html(get_global_css())

    # Check for logout query param
    if st.query_params.get("logout", "").lower() == "true":
        st.session_state.pop("authenticated_user", None)
        st.query_params.clear()

    # Check for activation token ?verify=<token>
    verify_token = st.query_params.get("verify", "")
    if verify_token:
        ok, msg = auth_store_instance.verify_email_token(verify_token)
        st.query_params.clear()
        if ok:
            st.success("Email confirmed — you can log in now.")
        else:
            st.error(msg)

    # Check for reset token ?reset=<token>
    reset_token = st.query_params.get("reset", "")
    if reset_token:
        st.markdown(
            """
            <div style="max-width: 440px; margin: 60px auto 20px auto; text-align: center;">
                <h2 style="font-family: 'DM Serif Display', serif; font-size: 28px; color: #2C1810; margin-bottom: 8px;">Reset Password</h2>
                <p style="font-size: 14px; color: #735A50;">Choose a new password for your AI Prep Coach profile.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("reset_pwd_form"):
            new_pwd = st.text_input("New Password (min 8 chars)", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            submitted = st.form_submit_button("Set New Password", type="primary")
            if submitted:
                if new_pwd != confirm_pwd:
                    st.error("Passwords do not match.")
                elif len(new_pwd) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    ok, r_msg = auth_store_instance.reset_password(reset_token, new_pwd)
                    if ok:
                        st.success(r_msg)
                        st.query_params.clear()
                    else:
                        st.error(r_msg)
        return

    # Check if a profile exists at all
    profile = auth_store_instance.get_profile()

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 40px; padding-bottom: 16px;">
            <div style="width: 100%; max-width: 440px; background: #FFFFFF; border: 1px solid rgba(74, 25, 66, 0.12); border-radius: 24px; padding: 40px 36px; text-align: center;">
                <div style="display: flex; justify-content: center; margin-bottom: 18px;">
                    <svg width="44" height="44" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="AI Prep Coach Logo">
                      <rect width="28" height="28" rx="7.28" fill="#C2452D"/>
                      <text x="13.5" y="20.5" font-family="'DM Serif Display', Georgia, serif" font-size="20" fill="#FFF8F0" text-anchor="middle">A</text>
                      <circle cx="21" cy="21" r="2.2" fill="#6B7F3B"/>
                    </svg>
                </div>
                <h1 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 30px; color: #2C1810; line-height: 1.15; margin: 0 0 6px 0;">AI Prep Coach</h1>
                <p style="font-size: 14px; color: #735A50; line-height: 1.5; margin: 0 0 24px 0;">Welcome back — your practice, judged by code.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_tab = "Sign In" if profile else "Create Account"
    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        mode = st.radio("Authentication Action", ["Sign In", "Create Account", "Forgot Password"], horizontal=True, label_visibility="collapsed")

        if mode == "Sign In":
            with st.form("login_form"):
                email = st.text_input("Email address", placeholder="you@example.com")
                pwd = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Log In", type="primary")

                if submitted:
                    ok, code, user_prof = auth_store_instance.authenticate_user(email, pwd)
                    if ok:
                        st.session_state["authenticated_user"] = user_prof["email"]
                        st.rerun()
                    elif code == "pending":
                        st.warning("Confirm your email to activate your account.")
                        st.session_state["resend_email"] = email
                    elif code == "not_found":
                        st.error("No account found for this email address. Please create an account.")
                    else:
                        st.error("Invalid email or password.")

            if st.session_state.get("resend_email"):
                r_email = st.session_state["resend_email"]
                if st.button("Resend confirmation email", key="btn_resend_confirm"):
                    r_ok, raw_tok, r_msg = auth_store_instance.resend_verification(r_email)
                    if r_ok:
                        app_url = os.environ.get("APP_BASE_URL", "http://localhost:8501")
                        link = f"{app_url}/?verify={raw_tok}"
                        s_ok, s_msg = send_smtp_email(
                            to_email=r_email,
                            subject="Confirm your AI Prep Coach account",
                            text_content=f"Click the link to activate your account: {link}\n\nLink valid for 24 hours.",
                            html_content=f"<p>Click the link to activate your AI Prep Coach account:</p><p><a href='{link}'>{link}</a></p><p>Link valid for 24 hours.</p>",
                        )
                        if s_ok:
                            st.success("Fresh confirmation link sent! Please check your inbox.")
                        else:
                            st.error(f"Could not send email: {s_msg}. (Token generated for testing: ?verify={raw_tok})")
                    else:
                        st.error(r_msg)

        elif mode == "Create Account":
            with st.form("register_form"):
                reg_email = st.text_input("Email address", placeholder="you@example.com")
                reg_pwd = st.text_input("Password (min 8 characters)", type="password", placeholder="••••••••")
                reg_submitted = st.form_submit_button("Create Account", type="primary")

                if reg_submitted:
                    c_ok, raw_tok, c_msg = auth_store_instance.create_pending_profile(reg_email, reg_pwd)
                    if c_ok:
                        app_url = os.environ.get("APP_BASE_URL", "http://localhost:8501")
                        link = f"{app_url}/?verify={raw_tok}"
                        s_ok, s_msg = send_smtp_email(
                            to_email=reg_email,
                            subject="Confirm your AI Prep Coach account",
                            text_content=f"Welcome to AI Prep Coach! Click the link to activate your account: {link}\n\nLink valid for 24 hours.",
                            html_content=f"<p>Welcome to <strong>AI Prep Coach</strong>!</p><p>Click below to activate your account:</p><p><a href='{link}'>{link}</a></p><p>This link is valid for 24 hours.</p>",
                        )
                        if s_ok:
                            st.success("Confirmation email sent! Please check your inbox and click the link to activate.")
                        else:
                            st.warning(f"Account created in pending status, but confirmation email could not be sent: {s_msg}.")
                            st.info(f"Local confirmation token (for offline activation): ?verify={raw_tok}")
                    else:
                        st.error(c_msg)

        elif mode == "Forgot Password":
            with st.form("forgot_pwd_form"):
                f_email = st.text_input("Your account email", placeholder="you@example.com")
                f_submitted = st.form_submit_button("Send Password Reset Link", type="primary")

                if f_submitted:
                    f_ok, raw_tok, f_msg = auth_store_instance.request_password_reset(f_email)
                    if f_ok:
                        app_url = os.environ.get("APP_BASE_URL", "http://localhost:8501")
                        link = f"{app_url}/?reset={raw_tok}"
                        s_ok, s_msg = send_smtp_email(
                            to_email=f_email,
                            subject="Reset your AI Prep Coach password",
                            text_content=f"Click the link to reset your password: {link}\n\nLink valid for 1 hour.",
                            html_content=f"<p>Click below to reset your AI Prep Coach password:</p><p><a href='{link}'>{link}</a></p><p>This link is valid for 1 hour.</p>",
                        )
                        if s_ok:
                            st.success("Password reset link sent! Please check your inbox.")
                        else:
                            st.warning(f"Reset token generated, but email delivery failed: {s_msg}.")
                            st.info(f"Local reset token (for offline reset): ?reset={raw_tok}")
                    else:
                        st.error(f_msg)

        st.markdown(
            """<div style="margin-top: 24px; font-size: 12px; color: #735A50; text-align: center;">
                Local profile — your data stays on this device.
            </div>""",
            unsafe_allow_html=True,
        )


# Initialize auth store
auth_store = AuthStore(db_path="coach.db")

# Gated access: unauthenticated sessions see only login
if "authenticated_user" not in st.session_state:
    # Allow automatic bypass if profile exists and no login required, or show login screen
    profile = auth_store.get_profile()
    if profile and profile["status"] == "active" and st.query_params.get("logout", "").lower() != "true":
        # Keep user logged in if active
        st.session_state["authenticated_user"] = profile["email"]
    else:
        render_login_screen(auth_store)
        st.stop()



# Single Source of Truth for Live Metrics
streak_count = store.current_streak()
due_list = store.due_problems()

# Query parameter sync
qp_screen = st.query_params.get("screen", "").lower()
if qp_screen in screen_to_nav:
    nav_choice = screen_to_nav[qp_screen]
elif "nav_choice" in st.session_state and st.session_state["nav_choice"] in nav_options:
    nav_choice = st.session_state["nav_choice"]
else:
    nav_choice = "Home"

st.session_state["nav_choice"] = nav_choice
target_screen = nav_to_screen.get(nav_choice, "home")
if st.query_params.get("screen", "").lower() != target_screen:
    st.query_params["screen"] = target_screen

# Inject Global CSS
st.html(get_global_css(nav_choice))


# ==============================================================================
# SCREEN 1: HOME / DAILY PRACTICE QUEUE
# ==============================================================================
if nav_choice == "Home":
    render_topbar("Home", streak_count, len(due_list))

    # Page Header (Terracotta Editorial)
    col_head, col_btn = st.columns([8, 4], vertical_alignment="center")
    with col_head:
        st.markdown(
            """<div style="margin-bottom: 8px;">
                <h1 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 34px; font-weight: 400; color: #2C1810; margin: 0 0 6px 0; line-height: 1.15;">
                    Today's Practice
                </h1>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px; color: #735A50; margin: 0; line-height: 1.5;">
                    Adaptive spaced repetition (FSRS) scheduled from your objective test results.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown(
            """<div style="text-align: right;">
                <a href="?screen=practice" target="_self" class="btn-primary-pill btn-terracotta" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 24px; background: #C2452D; color: #FFF8F0; border: 1px solid #C2452D; border-radius: 9999px; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px; font-weight: 600; text-decoration: none; white-space: nowrap;">
                    Start Daily Practice →
                </a>
            </div>""",
            unsafe_allow_html=True,
        )

    st.html('<div style="height: 8px;"></div>')

    # Stat Bento Cards Row: Active Streak, Problems Due Today, Target Retention
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True, key="home_card_streak"):
            streak_unit = "day" if streak_count == 1 else "days"
            if streak_count == 0:
                streak_badge = '<span class="stat-badge badge-quiet">NOT STARTED</span>'
                streak_caption = "Complete today's problem queue to start your streak."
            else:
                streak_badge = '<span class="stat-badge badge-olive">ACTIVE</span>'
                streak_caption = "Consecutive active days."
            st.markdown(
                f"""
                <div class="stat-head">
                    <span class="stat-label">Active Streak</span>
                    {streak_badge}
                </div>
                <div class="stat-value">{streak_count} {streak_unit}</div>
                <p class="stat-desc">{streak_caption}</p>
                """,
                unsafe_allow_html=True,
            )

    with c2:
        with st.container(border=True, key="home_card_due"):
            due_count = len(due_list)
            due_caption = "All review intervals are currently up to date." if due_count == 0 else f"{due_count} problem{'s' if due_count != 1 else ''} need review today."
            due_badge = '<span class="stat-badge badge-terracotta">FSRS</span>' if due_count > 0 else '<span class="stat-badge badge-olive">CLEAR</span>'
            st.markdown(
                f"""
                <div class="stat-head">
                    <span class="stat-label">Problems Due Today</span>
                    {due_badge}
                </div>
                <div class="stat-value">{due_count} due</div>
                <p class="stat-desc">{due_caption}</p>
                """,
                unsafe_allow_html=True,
            )

    with c3:
        with st.container(border=True, key="home_card_retention"):
            st.markdown(
                """
                <div class="stat-head">
                    <span class="stat-label">Target Retention</span>
                    <span class="stat-badge badge-olive">90.0%</span>
                </div>
                <div class="stat-value">90.0%</div>
                <p class="stat-desc">Adaptive spaced repetition retention optimizer.</p>
                """,
                unsafe_allow_html=True,
            )

    st.html('<div style="height: 16px;"></div>')

    # Recommended Practice Queue Bento Card
    with st.container(border=True, key="home_queue_card"):
        with store._get_connection() as conn:
            cur = conn.execute("SELECT DISTINCT problem_id FROM attempts WHERE status = 'pass'")
            solved_set = {row[0] for row in cur.fetchall()}

        solved_count = len(solved_set)
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h2 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 22px; font-weight: 400; color: #2C1810; margin: 0 0 4px 0;">
                        Recommended Practice Queue
                    </h2>
                    <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px; color: #735A50; margin: 0;">
                        Interleaved topic sequence prioritized by memory decay and weakness.
                    </p>
                </div>
                <span class="stat-badge badge-olive" style="font-size: 12px; padding: 4px 14px;">{solved_count} / {len(all_problems)} Solved</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build table rows for problem queue (interleaved across topics, due first per C3)
        due_problem_ids = {d["problem_id"] if isinstance(d, dict) else str(d) for d in (due_list or [])}
        interleaved_problems = build_interleaved_queue(
            all_problems, topic_stats=store.topic_stats(), due_problems=due_list
        )
        queue_rows = []
        for p in interleaved_problems:
            pid = p["id"]
            is_due = pid in due_problem_ids
            is_solved = pid in solved_set
            track_class = "track-dsa" if p["track"] == "dsa" else "track-python"
            diff_text_class = f"text-diff-{p['difficulty']}"

            if is_due:
                status_pill = '<span class="stat-badge badge-amber">DUE FOR REVIEW</span>'
                subtitle = "Due for review · Scheduled by FSRS"
            elif is_solved:
                card = store.get_fsrs_card(pid)
                if card and card.due:
                    today_date = date.today()
                    due_date = card.due.date() if hasattr(card.due, "date") else datetime.fromisoformat(str(card.due)).date()
                    delta_days = (due_date - today_date).days
                    computed_days = max(1, delta_days)
                    day_unit_str = "Day" if computed_days == 1 else "Days"
                    status_pill = f'<span class="stat-badge badge-olive">Next Due: +{computed_days} {day_unit_str}</span>'
                else:
                    fallback_interval = 1
                    status_pill = f'<span class="stat-badge badge-olive">Next Due: +{fallback_interval} Day</span>'
                subtitle = "Recent attempt passed · Scheduled for review"
            else:
                status_pill = '<span class="stat-badge badge-quiet">Unattempted</span>'
                subtitle = f"Standard {p['topic']} curriculum problem"

            topic_formatted = p['topic'].replace('-', ' ').title()

            queue_rows.append(
                f"""
                <tr class="queue-row {track_class}">
                    <td>
                        <div class="queue-problem-name">{p['title']}</div>
                        <div class="queue-problem-sub">{subtitle}</div>
                    </td>
                    <td><span class="stat-badge badge-blue">{topic_formatted}</span></td>
                    <td><span class="{diff_text_class}">{p['difficulty'].title()}</span></td>
                    <td>{status_pill}</td>
                    <td style="text-align: right;">
                        <a href="?screen=practice&problem={p['id']}" target="_self" class="btn-row-action">Practice →</a>
                    </td>
                </tr>
                """
            )

        queue_table_html = f"""
        <table class="queue-table">
            <thead>
                <tr>
                    <th>Problem</th>
                    <th>Topic</th>
                    <th>Difficulty</th>
                    <th>Interval Status</th>
                    <th style="text-align: right;">Action</th>
                </tr>
            </thead>
            <tbody>
                {"".join(queue_rows)}
            </tbody>
        </table>
        """
        st.html(queue_table_html)

elif nav_choice == "Practice Arena":
    render_topbar("Practice Arena", streak_count, len(due_list))

    # Two-pane Workbench: Left (~42%) / Right (~58%)
    left_col, right_col = st.columns([42, 58], gap="medium")

    with left_col:
        # Determine problem selection (single source of truth across app - X5R)
        qp_prob = st.query_params.get("problem", "").strip().lower()

        # Handle direct arrival or query parameter from Home queue
        if qp_prob and qp_prob != st.session_state.get("practice_last_qp"):
            for idx, p in enumerate(all_problems):
                if qp_prob == p["id"].lower() or qp_prob in p["id"].lower() or qp_prob in p["title"].lower():
                    st.session_state["practice_prob_idx"] = idx
                    st.session_state["practice_last_qp"] = qp_prob
                    st.session_state["selected_problem_id"] = p["id"]
                    break

        if "practice_prob_idx" not in st.session_state:
            st.session_state["practice_prob_idx"] = 0
            if "selected_problem_id" in st.session_state:
                for idx, p in enumerate(all_problems):
                    if p["id"] == st.session_state["selected_problem_id"]:
                        st.session_state["practice_prob_idx"] = idx
                        break

        curr_idx = st.session_state["practice_prob_idx"] % len(all_problems)
        st.session_state["practice_prob_idx"] = curr_idx
        current_problem = all_problems[curr_idx]
        st.session_state["selected_problem_id"] = current_problem["id"]

        # ONE slim picker row above Problem Card: Title in Fraunces serif + Prev/Next buttons (X5R, X10)
        p_prev_col, p_title_col, p_next_col = st.columns([0.8, 8.4, 0.8], vertical_alignment="center")
        with p_prev_col:
            if st.button("←", key="btn_picker_prev", help="Previous Problem", use_container_width=True):
                new_idx = (curr_idx - 1) % len(all_problems)
                st.session_state["practice_prob_idx"] = new_idx
                st.session_state["selected_problem_id"] = all_problems[new_idx]["id"]
                st.session_state["practice_last_qp"] = all_problems[new_idx]["id"].lower()
                st.query_params["problem"] = all_problems[new_idx]["id"]
                st.rerun()

        with p_title_col:
            st.html(
                f"""
                <div class="problem-picker-row" style="text-align: center; justify-content: center; margin: 0;">
                    <span class="picker-title" style="font-family: 'Fraunces', serif; font-size: 18px; font-weight: 700; color: #171712;">
                        {current_problem['title']}
                    </span>
                </div>
                """
            )

        with p_next_col:
            if st.button("→", key="btn_picker_next", help="Next Problem", use_container_width=True):
                new_idx = (curr_idx + 1) % len(all_problems)
                st.session_state["practice_prob_idx"] = new_idx
                st.session_state["selected_problem_id"] = all_problems[new_idx]["id"]
                st.session_state["practice_last_qp"] = all_problems[new_idx]["id"].lower()
                st.query_params["problem"] = all_problems[new_idx]["id"]
                st.rerun()

        # ONE Problem Card
        with st.container(border=True, key="practice_problem_card"):
            try:
                curr_pos = all_problems.index(current_problem) + 1
            except ValueError:
                curr_pos = 1
            total_in_lib = len(all_problems)

            diff_badge_class = (
                "butter"
                if current_problem["difficulty"] == "medium"
                else ("mint" if current_problem["difficulty"] == "easy" else "rose")
            )
            track_badge_class = "lilac" if current_problem["track"] == "dsa" else "sky"

            st.html(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="display: flex; gap: 8px;">
                        <span class="stat-badge badge-{track_badge_class}">{current_problem['track'].upper()}</span>
                        <span class="stat-badge badge-sky">{current_problem['topic'].title()}</span>
                        <span class="stat-badge badge-{diff_badge_class}">{current_problem['difficulty'].title()}</span>
                    </div>
                    <span style="font-size: 12px; color: #66635A; font-family: 'Inter', sans-serif;">
                        Problem <strong>{curr_pos} of {total_in_lib}</strong>
                    </span>
                </div>
                <h1 style="font-family: 'Fraunces', serif; font-size: 24px; font-weight: 700; color: #171712; line-height: 1.25; margin: 0 0 12px 0;">
                    {current_problem['title']}
                </h1>
                """
            )
            render_problem_statement(current_problem)

        # Hint Ladder (Butter Block strictly below Problem Card)
        hint_key = f"hint_level_{current_problem['id']}"
        if hint_key not in st.session_state:
            st.session_state[hint_key] = 0

        current_level = st.session_state[hint_key]
        total_hints = len(current_problem.get("hints", []))

        with st.container(border=True, key="practice_hint_ladder"):
            sparkle_svg = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="m4.93 4.93 2.83 2.83"/><path d="M2 12h4"/><path d="m4.93 19.07 2.83-2.83"/><path d="M12 18v4"/><path d="m16.24 16.24 2.83 2.83"/><path d="M18 12h4"/><path d="m16.24 7.76 2.83-2.83"/></svg>'
            st.html(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: #9A3412; text-transform: uppercase; letter-spacing: 0.04em; display: flex; align-items: center; gap: 6px;">
                        {sparkle_svg}
                        <span>Progressive Hint Ladder</span>
                    </div>
                    <span style="font-size: 12px; font-weight: 600; color: #9A3412;">Level {current_level} of {total_hints} Revealed</span>
                </div>
                """
            )

            if current_level > 0:
                for lvl in range(1, current_level + 1):
                    st.html(
                        f"""
                        <div style="margin-top: 8px; margin-bottom: 8px; padding: 10px 14px; background: rgba(255, 255, 255, 0.85); border-radius: 8px; border: 1px solid rgba(154, 52, 18, 0.2); font-size: 13px; color: #9A3412;">
                            <strong>Hint {lvl}:</strong> {current_problem['hints'][lvl - 1]}
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

            if current_level > 0 and ai_hint_clicked:
                with st.spinner("Asking local AI (Ollama)..."):
                    code_val = st.session_state.get(f"code_{current_problem['id']}", current_problem["starter_code"])
                    ai_hint_explanation = explain_hint(current_problem, code_val, hint_level=current_level)
                    st.info(ai_hint_explanation)

    with right_col:
        # Authentic defect code for demo_fail
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

        if editor_key not in st.session_state:
            if is_demo_fail and current_problem["id"] == "longest-substring-without-repeating":
                st.session_state[editor_key] = LONGEST_SUBSTRING_DEFECT
            else:
                st.session_state[editor_key] = current_problem["starter_code"]

        initial_code = st.session_state[editor_key]

        # 1. ONE Editor Card (No window dots, glued action row, natural width CTA - X8)
        with st.container(border=True, key="practice_editor_card"):
            st.html(
                """
                <style>
                .st-key-practice_editor_card [data-testid="stButton"] {
                    display: flex;
                    justify-content: flex-end;
                }
                .st-key-practice_editor_card [data-testid="stButton"] > button {
                    width: auto !important;
                    padding: 10px 24px !important;
                    border-radius: 9999px !important;
                    white-space: nowrap !important;
                }
                </style>
                """
            )
            st.html(
                f"""
                <div class="editor-strip">
                    <span class="editor-strip-title">SOLUTION EDITOR · PYTHON</span>
                    <span class="editor-strip-right">Sandbox · {current_problem.get('time_limit_sec', 3.0)}s · Python {sys.version_info.major}.{sys.version_info.minor}</span>
                </div>
                """
            )

            user_code = render_editor(initial_code, key=editor_key, height="450px")
            st.session_state[f"code_{current_problem['id']}"] = user_code

            # Glued Action Row (X8: Natural width button, no 100% full-width expansion)
            col_bar_info, col_bar_btn = st.columns([1.5, 1], vertical_alignment="center")
            with col_bar_info:
                st.html(
                    """
                    <div style="padding-left: 18px; font-size: 12px; color: #66635A; display: flex; align-items: center; gap: 6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#66635A" stroke-width="2"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>
                        <span>Clean environment · Network disabled</span>
                    </div>
                    """
                )
            with col_bar_btn:
                run_submitted = st.button("Run & Submit", type="primary", key=f"btn_run_{current_problem['id']}", use_container_width=False)

            if run_submitted:
                stripped_code = user_code.strip()
                stripped_starter = current_problem["starter_code"].strip()
                if not stripped_code or stripped_code == stripped_starter:
                    st.warning(f"Write your solution first — the judge expected '{current_problem['function_name']}(...)'.")
                    run_submitted = False

        # 2. ONE Output Card (X7-Practice: Neutral pre-run state with 'Run your code to see results')
        with st.container(border=True, key="practice_output_card"):
            if not run_submitted and not is_demo_fail:
                st.html(
                    """
                    <div style="padding: 24px; text-align: center; color: #66635A;">
                        <div style="font-family: 'Fraunces', serif; font-size: 16px; font-weight: 600; color: #171712; margin-bottom: 4px;">
                            Run your code to see results
                        </div>
                        <div style="font-size: 13.5px;">
                            No execution yet. Run your code to test against visible and hidden test cases.
                        </div>
                    </div>
                    """
                )
            else:
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

                if run_submitted:
                    store.record_attempt(
                        problem_id=current_problem["id"],
                        status=status,
                        runtime_ms=runtime,
                        hints_used=hints_used,
                        mode="practice",
                        topic=current_problem["topic"],
                    )

                # Verdict Band
                if status == "pass":
                    st.html(
                        f"""
                        <div class="verdict-band verdict-band-pass">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="stat-badge badge-mint" style="background: #167B48 !important; color: #FFFFFF !important;">PASS</span>
                                    <strong style="font-size: 15px; color: #167B48;">
                                        {current_problem['title']} · PASS · {runtime} ms · Hints {hints_used}
                                    </strong>
                                </div>
                                <span style="font-size: 12px; font-weight: 600; color: #167B48;">All Tests Accepted</span>
                            </div>
                            <div style="font-size: 12px; display: flex; gap: 16px; margin-top: 4px;">
                                <span><strong>Runtime:</strong> {runtime} ms</span>
                                <span><strong>Tests:</strong> {passed} / {total} Passed</span>
                            </div>
                        </div>
                        """
                    )
                else:
                    st.html(
                        f"""
                        <div class="verdict-band verdict-band-fail">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="stat-badge badge-rose" style="background: #C5221F !important; color: #FFFFFF !important;">FAIL</span>
                                    <strong style="font-size: 15px; color: #C5221F;">
                                        {current_problem['title']} · FAIL · {runtime} ms · {passed}/{total} Passed
                                    </strong>
                                </div>
                                <span style="font-size: 12px; font-weight: 600; color: #C5221F;">Test Mismatch</span>
                            </div>
                        </div>
                        """
                    )

                    failed_cases = judge_result.get("failed_cases", [])
                    if failed_cases:
                        fc = failed_cases[0]
                        st.html(
                            f"""
                            <div style="padding: 14px 20px; background: rgba(255, 255, 255, 0.85); border-bottom: 1px solid #E7E1D6; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #171712;">
                                <div><strong>Failed Input:</strong> <code>{fc.get('input_args')}</code></div>
                                <div style="margin-top: 4px;"><strong>Expected:</strong> <code>{fc.get('expected')}</code></div>
                                <div style="margin-top: 4px; color: #C5221F;"><strong>Got:</strong> <code>{fc.get('got')}</code></div>
                            </div>
                            """
                        )

                # Visible Test Cases Section
                st.html('<div style="padding: 16px 20px 8px 20px;"><strong style="font-family: \'Fraunces\', serif; font-size: 15px; color: #171712;">Visible Test Cases</strong></div>')
                for i, tc in enumerate(current_problem["visible_tests"], 1):
                    args_repr = ", ".join(repr(arg) for arg in tc["input_args"])
                    st.html(
                        f"""
                        <div style="margin: 0 20px 12px 20px; background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 12px; padding: 12px 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-size: 12px; font-weight: 700; color: #167B48; letter-spacing: 0.04em;">TEST CASE #{i}</span>
                                <span class="stat-badge badge-mint">Provided</span>
                            </div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #171712;">
                                <div><strong>Input:</strong> <code>{args_repr}</code></div>
                                <div style="margin-top: 2px;"><strong>Expected:</strong> <code>{tc['expected']}</code></div>
                            </div>
                        </div>
                        """
                    )


# ==============================================================================
# SCREEN 3: MOCK INTERVIEW ARENA (ADDENDUM A)
# ==============================================================================
elif nav_choice == "Mock Interview":
    render_topbar("Mock Interview", streak_count, len(due_list))

    if "mock_state" not in st.session_state:
        st.session_state["mock_state"] = "unstarted"

    if st.query_params.get("mock_state", "").lower() == "completed":
        st.session_state["mock_state"] = "completed"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time() - 25 * 60
            st.session_state["mock_start_iso"] = datetime.now().isoformat()
        if "mock_finish_time" not in st.session_state:
            st.session_state["mock_finish_time"] = time.time()
        if "mock_problems" not in st.session_state:
            mock_pool = build_interleaved_queue(all_problems, topic_stats=store.topic_stats())
            st.session_state["mock_problems"] = [
                mock_pool[0],
                mock_pool[1] if len(mock_pool) > 1 else mock_pool[0],
            ]
        if st.query_params.get("mock_solved_p1", "").lower() == "true":
            st.session_state["mock_result_binary-search"] = {
                "status": "pass",
                "runtime_ms": 134,
                "passed": 5,
                "total": 5,
            }

    if st.query_params.get("mock_state", "").lower() == "running":
        st.session_state["mock_state"] = "running"
        if "mock_start_time" not in st.session_state:
            st.session_state["mock_start_time"] = time.time() - 19
            st.session_state["mock_start_iso"] = datetime.now().isoformat()
            st.session_state["mock_duration_sec"] = 45 * 60
            mock_pool = build_interleaved_queue(all_problems, topic_stats=store.topic_stats())
            st.session_state["mock_problems"] = [
                mock_pool[0],
                mock_pool[1] if len(mock_pool) > 1 else mock_pool[0],
            ]

    # --- STATE 1: UNSTARTED ---
    if st.session_state["mock_state"] == "unstarted":
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                    Technical Interview Simulation
                </h1>
                <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #66635A; margin: 0;">
                    Two curated algorithmic problems under 45:00 strict countdown constraint.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True, key="mock_ready_card"):
            st.markdown(
                """
                <div style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin-bottom: 6px;">
                    Ready to Begin Simulation?
                </div>
                <div style="font-size: 14px; color: #66635A; line-height: 1.5; margin-bottom: 20px;">
                    A 45-minute timed simulation consisting of 2 algorithmic problems.
                    The timer runs automatically across synchronized indicators.
                    Submissions are evaluated against real test suites and recorded on your session scorecard.
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Start 45-Minute Mock Interview", type="primary", key="btn_start_mock"):
                mock_pool = build_interleaved_queue(all_problems, topic_stats=store.topic_stats())
                p1 = mock_pool[0]
                p2 = mock_pool[1] if len(mock_pool) > 1 else mock_pool[0]
                st.session_state["mock_state"] = "running"
                st.session_state["mock_start_time"] = time.time()
                st.session_state["mock_start_iso"] = datetime.now().isoformat()
                st.session_state["mock_duration_sec"] = 45 * 60
                st.session_state["mock_problems"] = [p1, p2]
                st.session_state["mock_active_tab"] = 0
                st.rerun()

        st.html('<div style="height: 16px;"></div>')

        # Simulation Rules Card (Full-width, no void)
        with st.container(border=True, key="mock_rules_card"):
            st.markdown(
                """
                <div style="margin-bottom: 16px;">
                    <span class="stat-badge badge-peach" style="margin-bottom: 6px;">Protocol</span>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                        Simulation Rules &amp; Evaluation Protocol
                    </h2>
                    <p style="font-size: 14px; color: #66635A; margin: 0;">
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
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;">
                        <strong style="font-size: 14px; color: #171712; display: block; margin-bottom: 4px;">1. Strict 45-Minute Limit</strong>
                        <span style="font-size: 13px; color: #66635A; line-height: 1.5;">A countdown timer runs in the sub-strip. Submissions lock automatically when time expires.</span>
                    </div>
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 16px 18px;">
                        <strong style="font-size: 14px; color: #171712; display: block; margin-bottom: 4px;">2. Two Curated Problems</strong>
                        <span style="font-size: 13px; color: #66635A; line-height: 1.5;">Pairs designed to evaluate algorithmic approach, edge cases, and code efficiency under pacing constraints.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with r_col2:
                st.markdown(
                    """
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;">
                        <strong style="font-size: 14px; color: #171712; display: block; margin-bottom: 4px;">3. Progressive Hint Tracking</strong>
                        <span style="font-size: 13px; color: #66635A; line-height: 1.5;">Up to 3 progressive hints available per problem. Every revealed hint is reported on your scorecard.</span>
                    </div>
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 16px 18px;">
                        <strong style="font-size: 14px; color: #171712; display: block; margin-bottom: 4px;">4. Authentic Code Execution</strong>
                        <span style="font-size: 13px; color: #66635A; line-height: 1.5;">Solutions execute in an isolated local subprocess against real test suites. Zero invented scores.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Past Sessions (Render ONLY if mock attempts exist in store)
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
                        <h2 style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                            Past Mock Sessions
                        </h2>
                        <p style="font-size: 14px; color: #66635A; margin: 0;">
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
                    f"""<table class="queue-table">
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

    # --- STATE 2: RUNNING ---
    elif st.session_state["mock_state"] == "running":
        p_list = st.session_state["mock_problems"]
        active_tab_idx = st.session_state.get("mock_active_tab", 0)

        # Place 1: Sub-strip Countdown Timer via @st.fragment
        @st.fragment(run_every=1.0)
        def render_mock_substrip_timer():
            start = st.session_state.get("mock_start_time", time.time())
            duration = st.session_state.get("mock_duration_sec", 45 * 60)
            mins, secs, is_expired = calculate_remaining_time(start, duration, time.time())
            timer_icon = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
            if is_expired:
                st.session_state["mock_time_expired"] = True
                st.html(
                    f"""
                    <div class="mock-timer-pill" style="color: #C5221F; border-color: rgba(197, 34, 31, 0.25);">
                        {timer_icon}
                        <span>00:00 Expired</span>
                    </div>
                    """
                )
            else:
                st.html(
                    f"""
                    <div class="mock-timer-pill">
                        {timer_icon}
                        <span>{mins:02d}:{secs:02d}</span>
                    </div>
                    """
                )

        # Sub-strip Container
        with st.container(border=True, key="mock_substrip_container"):
            col_tabs, col_time, col_end = st.columns([6, 3, 3], vertical_alignment="center")
            with col_tabs:
                t1_active = "active" if active_tab_idx == 0 else ""
                t2_active = "active" if active_tab_idx == 1 else ""
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if st.button(f"1: {p_list[0]['title']}", key="btn_tab_0", use_container_width=True):
                        st.session_state["mock_active_tab"] = 0
                        st.rerun()
                with col_t2:
                    if st.button(f"2: {p_list[1]['title']}", key="btn_tab_1", use_container_width=True):
                        st.session_state["mock_active_tab"] = 1
                        st.rerun()

            with col_time:
                render_mock_substrip_timer()

            with col_end:
                if st.button("End Interview Early", key="btn_end_mock", use_container_width=True):
                    st.session_state["mock_state"] = "completed"
                    st.session_state["mock_finish_time"] = time.time()
                    st.rerun()

        # Active Problem Workspace
        active_problem = p_list[active_tab_idx]
        col_m_left, col_m_right = st.columns([42, 58], gap="medium")

        with col_m_left:
            # ONE Problem Card
            with st.container(border=True, key="mock_problem_card"):
                st.html(
                    f"""
                    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                        <span class="stat-badge badge-peach">Problem {active_tab_idx + 1} of 2</span>
                        <span class="stat-badge badge-sky">{active_problem['track'].upper()}</span>
                        <span class="stat-badge badge-mint">{active_problem['difficulty'].title()}</span>
                    </div>
                    <h1 style="font-family: 'Fraunces', serif; font-size: 24px; font-weight: 700; color: #171712; line-height: 1.25; margin: 0 0 12px 0;">
                        {active_problem['title']}
                    </h1>
                    """
                )
                render_problem_statement(active_problem)

            # Hint Ladder
            m_hint_key = f"mock_hints_{active_problem['id']}"
            if m_hint_key not in st.session_state:
                st.session_state[m_hint_key] = 0

            m_level = st.session_state[m_hint_key]
            m_total_hints = len(active_problem.get("hints", []))

            with st.container(border=True, key="mock_hint_ladder"):
                st.html(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 13px; font-weight: 700; color: #9A3412; text-transform: uppercase; letter-spacing: 0.04em;">
                            Hint Ladder ({m_level} of {m_total_hints} Revealed)
                        </span>
                    </div>
                    """
                )
                if m_level > 0:
                    for lvl in range(1, m_level + 1):
                        st.html(
                            f"""
                            <div style="margin-top: 8px; margin-bottom: 8px; padding: 10px 14px; background: rgba(255, 255, 255, 0.85); border-radius: 8px; border: 1px solid rgba(154, 52, 18, 0.2); font-size: 13px; color: #9A3412;">
                                <strong>Hint {lvl}:</strong> {active_problem['hints'][lvl - 1]}
                            </div>
                            """
                        )

                if st.button("Reveal Next Hint", key=f"btn_m_hint_{active_problem['id']}", disabled=(m_level >= m_total_hints), use_container_width=True):
                    st.session_state[m_hint_key] += 1
                    st.rerun()

        with col_m_right:
            m_editor_key = f"mock_editor_{active_problem['id']}"
            if m_editor_key not in st.session_state:
                st.session_state[m_editor_key] = active_problem["starter_code"]

            m_code = st.session_state[m_editor_key]

            # Allow test solve via query param
            if st.query_params.get("mock_solve_p1", "").lower() == "true" and active_problem["id"] == "binary-search":
                m_code = (
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

            # Editor Card
            with st.container(border=True, key="mock_editor_card"):
                st.html(
                    f"""
                    <div class="editor-strip">
                        <span class="editor-strip-title">MOCK INTERVIEW EDITOR · PYTHON</span>
                        <span class="editor-strip-right">Sandbox · Python {sys.version_info.major}.{sys.version_info.minor}</span>
                    </div>
                    """
                )
                user_m_code = render_editor(m_code, key=m_editor_key, height="450px")
                st.session_state[f"mock_code_{active_problem['id']}"] = user_m_code

                col_b_info, col_b_btn = st.columns([1, 1], vertical_alignment="center")
                with col_b_info:
                    st.html('<div style="padding-left: 18px; font-size: 12px; color: #66635A;">Timed environment · Scoped run</div>')
                with col_b_btn:
                    m_submit = st.button("Submit Problem Solution", type="primary", key=f"btn_msub_{active_problem['id']}", use_container_width=True)

            # Output Card
            m_res_key = f"mock_result_{active_problem['id']}"
            if m_submit:
                with st.spinner("Judging solution..."):
                    m_res = run_solution(user_m_code, active_problem)
                    st.session_state[m_res_key] = m_res
                    store.record_attempt(
                        problem_id=active_problem["id"],
                        status=m_res["status"],
                        runtime_ms=m_res["runtime_ms"],
                        hints_used=st.session_state.get(m_hint_key, 0),
                        mode="mock",
                        topic=active_problem["topic"],
                    )
                    st.rerun()

            saved_m_res = st.session_state.get(m_res_key)
            with st.container(border=True, key="mock_output_card"):
                if not saved_m_res:
                    st.html(
                        """
                        <div style="padding: 24px; text-align: center; color: #66635A;">
                            <div style="font-family: 'Fraunces', serif; font-size: 16px; font-weight: 600; color: #171712; margin-bottom: 4px;">
                                Mock Execution Output
                            </div>
                            <div style="font-size: 13.5px;">
                                Submit your solution to evaluate against authentic interview test cases.
                            </div>
                        </div>
                        """
                    )
                else:
                    m_stat = saved_m_res["status"]
                    m_rt = saved_m_res["runtime_ms"]
                    m_pass = saved_m_res["passed"]
                    m_tot = saved_m_res["total"]

                    if m_stat == "pass":
                        st.html(
                            f"""
                            <div class="verdict-band verdict-band-pass">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span class="stat-badge badge-mint" style="background: #167B48 !important; color: #FFFFFF !important;">PASS</span>
                                    <strong style="font-size: 15px; color: #167B48;">All {m_pass}/{m_tot} Tests Accepted ({m_rt} ms)</strong>
                                </div>
                            </div>
                            """
                        )
                    else:
                        st.html(
                            f"""
                            <div class="verdict-band verdict-band-fail">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span class="stat-badge badge-rose" style="background: #C5221F !important; color: #FFFFFF !important;">FAIL</span>
                                    <strong style="font-size: 15px; color: #C5221F;">{m_pass}/{m_tot} Tests Passed ({m_rt} ms)</strong>
                                </div>
                            </div>
                            """
                        )

    # --- STATE 3: COMPLETED (SCORECARD) ---
    elif st.session_state["mock_state"] == "completed":
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-family: 'Fraunces', serif; font-size: 32px; font-weight: 700; color: #171712; margin: 0 0 4px 0;">
                    Simulation Completed
                </h1>
                <p style="font-family: 'Inter', sans-serif; font-size: 15px; color: #66635A; margin: 0;">
                    Authentic evaluation verified against local judge test suites.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True, key="mock_scorecard_card"):
            total_time_min = round((st.session_state.get("mock_finish_time", time.time()) - st.session_state.get("mock_start_time", time.time())) / 60, 1)
            p_list = st.session_state["mock_problems"]
            session_start_iso = st.session_state.get("mock_start_iso")

            p1_eval = get_mock_problem_evaluation(
                p_list[0]["id"],
                session_start_iso,
                st.session_state.get(f"mock_result_{p_list[0]['id']}"),
                st.session_state.get(f"mock_hints_{p_list[0]['id']}", 0),
                store,
            )
            p2_eval = get_mock_problem_evaluation(
                p_list[1]["id"],
                session_start_iso,
                st.session_state.get(f"mock_result_{p_list[1]['id']}"),
                st.session_state.get(f"mock_hints_{p_list[1]['id']}", 0),
                store,
            )
            score = (1 if p1_eval["is_pass"] else 0) + (1 if p2_eval["is_pass"] else 0)

            # Place 2: Scorecard elapsed time display
            @st.fragment(run_every=1.0)
            def render_scorecard_timer():
                st.markdown(
                    f"""
                    <div style="text-align: right;">
                        <div style="font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; color: #167B48; font-variant-numeric: tabular-nums;">
                            {score} / 2 Solved
                        </div>
                        <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #66635A;">
                            Session Duration: {total_time_min} min
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            sc_hdr_left, sc_hdr_right = st.columns([8, 4], vertical_alignment="center")
            with sc_hdr_left:
                st.markdown(
                    """
                    <span class="stat-badge badge-mint" style="margin-bottom: 6px;">Official Record</span>
                    <h2 style="font-family: 'Fraunces', serif; font-size: 24px; font-weight: 700; color: #171712; line-height: 1.25; margin: 0;">
                        Final Interview Scorecard
                    </h2>
                    """,
                    unsafe_allow_html=True,
                )
            with sc_hdr_right:
                render_scorecard_timer()

            st.html('<div style="height: 16px;"></div>')

            col_sc1, col_sc2 = st.columns(2, gap="medium")
            with col_sc1:
                prob1_title = p_list[0]["title"]
                if p1_eval["status"] == "pass":
                    p1_badge = '<span class="stat-badge badge-mint">PASS</span>'
                    p1_rt = f"{p1_eval['runtime_ms']} ms"
                elif p1_eval["status"] == "fail":
                    p1_badge = '<span class="stat-badge badge-rose">FAIL</span>'
                    p1_rt = f"{p1_eval['runtime_ms']} ms"
                else:
                    p1_badge = '<span class="stat-badge" style="background: rgba(102, 99, 90, 0.12); color: #66635A;">NOT ATTEMPTED</span>'
                    p1_rt = "—"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 18px 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="font-size: 15px; color: #171712;">Problem 1: {prob1_title}</strong>
                            {p1_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A; margin-bottom: 10px;">Track: {p_list[0]['track'].upper()} · Topic: {p_list[0]['topic']}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px;">
                            <span><strong>Runtime:</strong> {p1_rt}</span>
                            <span><strong>Hints Used:</strong> {p1_eval['hints_used']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_sc2:
                prob2_title = p_list[1]["title"]
                if p2_eval["status"] == "pass":
                    p2_badge = '<span class="stat-badge badge-mint">PASS</span>'
                    p2_rt = f"{p2_eval['runtime_ms']} ms"
                elif p2_eval["status"] == "fail":
                    p2_badge = '<span class="stat-badge badge-rose">FAIL</span>'
                    p2_rt = f"{p2_eval['runtime_ms']} ms"
                else:
                    p2_badge = '<span class="stat-badge" style="background: rgba(102, 99, 90, 0.12); color: #66635A;">NOT ATTEMPTED</span>'
                    p2_rt = "—"

                st.markdown(
                    f"""
                    <div style="background: #FBFAF7; border: 1px solid #E7E1D6; border-radius: 14px; padding: 18px 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="font-size: 15px; color: #171712;">Problem 2: {prob2_title}</strong>
                            {p2_badge}
                        </div>
                        <div style="font-size: 12px; color: #66635A; margin-bottom: 10px;">Track: {p_list[1]['track'].upper()} · Topic: {p_list[1]['topic']}</div>
                        <div style="font-size: 13px; color: #171712; display: flex; gap: 16px;">
                            <span><strong>Runtime:</strong> {p2_rt}</span>
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
# SCREEN 4: DASHBOARD / PERFORMANCE ANALYTICS
# ==============================================================================
elif nav_choice == "Dashboard":
    render_topbar("Dashboard", streak_count, len(due_list))

    col_dash_head, col_dash_btn = st.columns([8, 4], vertical_alignment="center")
    with col_dash_head:
        st.markdown(
            """<div style="margin-bottom: 8px;">
                <h1 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 34px; font-weight: 400; color: #2C1810; margin: 0 0 6px 0; line-height: 1.15;">
                    Performance Analytics
                </h1>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px; color: #735A50; margin: 0; line-height: 1.5;">
                    Authentic mastery progress, practice volume, and topic readiness based strictly on SQLite attempt history.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_dash_btn:
        st.markdown(
            """<div style="text-align: right;">
                <a href="?screen=practice" target="_self" class="btn-primary-pill btn-terracotta" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 24px; background: #C2452D; color: #FFF8F0; border: 1px solid #C2452D; border-radius: 9999px; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px; font-weight: 600; text-decoration: none; white-space: nowrap;">
                    Continue Practice →
                </a>
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

    st.html('<div style="height: 8px;"></div>')

    # Three Stat Bento Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True, key="dash_card_attempts"):
            st.markdown(
                f"""
                <div class="stat-head">
                    <span class="stat-label">Solved Problems</span>
                    <span class="stat-badge badge-olive">{solved_count} / {len(all_problems)} Total</span>
                </div>
                <div class="stat-value">{solved_count}</div>
                <p class="stat-desc">Distinct problems passed at least once.</p>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        with st.container(border=True, key="dash_card_passrate"):
            st.markdown(
                f"""
                <div class="stat-head">
                    <span class="stat-label">Practice Sessions</span>
                    <span class="stat-badge badge-blue">SQLITE</span>
                </div>
                <div class="stat-value">{total_sessions}</div>
                <p class="stat-desc">Total code-judged runs recorded in SQLite.</p>
                """,
                unsafe_allow_html=True,
            )

    with col3:
        with st.container(border=True, key="dash_card_practiced"):
            st.markdown(
                f"""
                <div class="stat-head">
                    <span class="stat-label">Average Hints Used</span>
                    <span class="stat-badge badge-quiet">HINTS</span>
                </div>
                <div class="stat-value">{avg_hints:.1f}</div>
                <p class="stat-desc">Average hints revealed per problem attempt.</p>
                """,
                unsafe_allow_html=True,
            )

    st.html('<div style="height: 16px;"></div>')

    stats = store.topic_stats()
    all_curriculum_topics = sorted(list({p.get("topic") for p in all_problems if p.get("topic")}))

    attempted_topics = [t for t in all_curriculum_topics if t in stats and stats[t].get("attempts", 0) > 0]
    for t in sorted(stats.keys()):
        if stats[t].get("attempts", 0) > 0 and t not in attempted_topics:
            attempted_topics.append(t)

    # Bento Card 1: Plotly Horizontal Pass Rate Chart (Attempted Topics Only, placed ABOVE table per F2)
    with st.container(border=True, key="dashboard_chart_card"):
        st.markdown(
            """
            <div style="margin-bottom: 12px;">
                <h2 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 22px; font-weight: 400; color: #2C1810; margin: 0 0 4px 0;">
                    Attempted Topic Pass Rates
                </h2>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px; color: #735A50; margin: 0;">
                    Objective performance across attempted curriculum areas from store attempt history.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if attempted_topics:
            y_topics = [t.replace('-', ' ').title() for t in attempted_topics]
            x_rates = [stats[t]["pass_rate"] for t in attempted_topics]
            bar_colors = ["#6B7F3B" if stats[t]["pass_rate"] >= 70.0 else "#C2452D" for t in attempted_topics]
            bar_texts = [f"{stats[t]['pass_rate']:.1f}% ({stats[t]['passed']}/{stats[t]['attempts']})" for t in attempted_topics]

            fig = go.Figure(
                data=[
                    go.Bar(
                        y=y_topics,
                        x=x_rates,
                        orientation="h",
                        marker=dict(color=bar_colors, line=dict(color="rgba(74, 25, 66, 0.15)", width=1)),
                        text=bar_texts,
                        textposition="outside",
                        textfont=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#2C1810"),
                        cliponaxis=False,
                    )
                ]
            )
            fig.update_layout(
                xaxis=dict(
                    title=dict(text="Pass Rate (%)", font=dict(family="Plus Jakarta Sans, sans-serif", size=13, color="#735A50")),
                    range=[0, 115],
                    gridcolor="rgba(74, 25, 66, 0.08)",
                    showline=True,
                    linecolor="rgba(74, 25, 66, 0.12)",
                    zeroline=True,
                    zerolinecolor="rgba(74, 25, 66, 0.12)",
                    tickfont=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#2C1810"),
                    ticksuffix="%",
                ),
                yaxis=dict(
                    autorange="reversed",
                    gridcolor="rgba(74, 25, 66, 0.08)",
                    showline=True,
                    linecolor="rgba(74, 25, 66, 0.12)",
                    tickfont=dict(family="Plus Jakarta Sans, sans-serif", size=13, color="#2C1810"),
                ),
                margin=dict(l=40, r=40, t=16, b=36),
                height=max(160, len(attempted_topics) * 48 + 80),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#2C1810"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown(
                """<div style="padding: 16px 0; color: #735A50; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px;">
                    No attempts recorded yet. Practice problems to generate topic pass-rate analytics.
                </div>""",
                unsafe_allow_html=True,
            )

    st.html('<div style="height: 16px;"></div>')

    # Bento Card 2: Full Curriculum Topic Breakdown Table (BELOW chart per F2)
    with st.container(border=True, key="dashboard_table_card"):
        st.markdown(
            """
            <div style="margin-bottom: 16px;">
                <h2 style="font-family: 'DM Serif Display', Georgia, serif; font-size: 22px; font-weight: 400; color: #2C1810; margin: 0 0 4px 0;">
                    All Curriculum Topics (11 Total)
                </h2>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13.5px; color: #735A50; margin: 0;">
                    Complete syllabus status mapped directly from store attempt records.
                </p>
            </div>
            """,
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
        for t in all_curriculum_topics:
            probs = topic_problems.get(t, [])
            total_in_topic = len(probs)
            solved_in_topic = sum(1 for p in probs if p["id"] in solved_problem_ids)
            track_name = probs[0].get("track", "DSA").upper() if probs else "DSA"

            d = stats.get(t, {"attempts": 0, "passed": 0, "pass_rate": 0.0})
            attempts = d["attempts"]
            pass_rate = d["pass_rate"]

            formatted_title = t.replace('-', ' ').title()

            if attempts == 0:
                ratio_str = f'<span style="color: #735A50; font-weight: 500;">0 / {total_in_topic}</span>'
                bar_html = f"""<div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(74, 25, 66, 0.08); border-radius: 9999px; height: 8px; width: 120px; overflow: hidden; flex-shrink: 0;">
                        <div style="background: transparent; width: 0%; height: 100%;"></div>
                    </div>
                    <span style="font-size: 12px; font-weight: 600; font-feature-settings: 'tnum' 1; color: #735A50;">—</span>
                </div>"""
                status_chip = '<span class="stat-badge badge-quiet">NOT STARTED</span>'
            else:
                ratio_str = f'<span style="color: #2C1810; font-weight: 600;">{solved_in_topic} / {total_in_topic}</span>'
                bar_color = "#6B7F3B" if pass_rate >= 70.0 else "#C2452D"
                bar_html = f"""<div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(74, 25, 66, 0.08); border-radius: 9999px; height: 8px; width: 120px; overflow: hidden; flex-shrink: 0;">
                        <div style="background: {bar_color}; width: {min(pass_rate, 100.0)}%; height: 100%; border-radius: 9999px;"></div>
                    </div>
                    <span style="font-size: 13px; font-weight: 700; font-feature-settings: 'tnum' 1; color: #2C1810;">{pass_rate:.1f}%</span>
                </div>"""
                status_chip = '<span class="stat-badge badge-olive">PASSING</span>' if pass_rate >= 70.0 else '<span class="stat-badge badge-terracotta">NEEDS WORK</span>'

            rows_html.append(
                f"""<tr>
                    <td><strong>{formatted_title}</strong></td>
                    <td><span class="stat-badge badge-blue">{track_name}</span></td>
                    <td>{ratio_str}</td>
                    <td>{bar_html}</td>
                    <td style="text-align: right; white-space: nowrap !important; min-width: 130px;">{status_chip}</td>
                </tr>"""
            )

        table_markup = f"""<table class="queue-table">
            <thead>
                <tr>
                    <th>Topic</th>
                    <th>Track</th>
                    <th>Solved / Total</th>
                    <th>Mastery Pass Rate</th>
                    <th style="text-align: right;">Status</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows_html)}
            </tbody>
        </table>"""

        st.html(table_markup)
