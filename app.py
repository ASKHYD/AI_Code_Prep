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
        editor_response = code_editor(
            code,
            lang="python",
            theme="dark",
            height=height,
            key=key,
            buttons=editor_custom_btns,
            options={"wrap": True, "showLineNumbers": True},
            response_mode="debounce",
        )
        if isinstance(editor_response, dict) and editor_response.get("text", "").strip():
            return editor_response["text"]
        elif isinstance(editor_response, str) and editor_response.strip():
            return editor_response
        return code
    except Exception:
        return st.text_area(
            "Code Editor",
            value=code,
            height=height,
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
    with st.container(border=True):
        st.subheader("Daily Review and Practice Queue")
        st.caption(
            "Problems are scheduled using an interview-targeted spaced repetition schedule "
            "(1 / 1 / 3 / 7 / 21 days) based strictly on objective test\u00A0results."
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.metric("Active Streak", f"{streak_count} days")
    with c2:
        with st.container(border=True):
            st.metric("Problems Due Today", f"{len(due_list)} problems")
    with c3:
        with st.container(border=True):
            st.metric("Total Library", f"{len(all_problems)} problems")

    with st.container(border=True):
        st.subheader("Due for Review Today")
        if not due_list:
            st.info("You are all caught up! No problems due for review today. Open Practice Arena to solve a new problem.")
        else:
            for item in due_list:
                prob = problems_by_id.get(item["problem_id"])
                if not prob:
                    continue
                with st.container(border=True):
                    cols = st.columns([4, 2, 2, 2, 2])
                    cols[0].markdown(f"**{prob['title']}**")
                    cols[1].caption(f"Track: {prob['track'].upper()}")
                    cols[2].caption(f"Topic: {prob['topic']}")
                    cols[3].caption(f"Passes: {item['consecutive_passes']}")
                    if cols[4].button("Practice", key=f"due_btn_{prob['id']}"):
                        st.session_state["selected_problem_id"] = prob["id"]
                        st.query_params["screen"] = "practice"
                        st.rerun()

    with st.container(border=True):
        st.subheader("Recent Practice Attempts")
        recents = store.get_recent_attempts(limit=5)
        if recents:
            for r in recents:
                prob_title = problems_by_id.get(r["problem_id"], {}).get("title", r["problem_id"])
                status_color = ":green[PASS]" if r['status'] == 'pass' else (":orange[TIMEOUT]" if r['status'] == 'timeout' else ":red[FAIL]")
                st.markdown(
                    f"- **{r['attempt_date']}** | **{prob_title}** | "
                    f"Result: {status_color} | Runtime: `{r['runtime_ms']}ms` | Hints: `{r['hints_used']}`"
                )
        else:
            st.caption("No attempts recorded yet. Launch Practice Arena to begin your first problem.")


# ==============================================================================
# SCREEN 2: PRACTICE ARENA
# ==============================================================================
elif nav_choice == "Practice Arena":
    with st.container(border=True):
        st.subheader("Practice Arena")
        col_f1, col_f2, col_f3 = st.columns(3)
        tracks = ["All"] + sorted({p["track"] for p in all_problems})
        difficulties = ["All", "easy", "medium", "hard"]
        topics = ["All"] + sorted({p["topic"] for p in all_problems})

        selected_track = col_f1.selectbox("Filter Track", tracks)
        selected_diff = col_f2.selectbox("Filter Difficulty", difficulties)
        selected_topic = col_f3.selectbox("Filter Topic", topics)

    filtered = [
        p for p in all_problems
        if (selected_track == "All" or p["track"] == selected_track)
        and (selected_diff == "All" or p["difficulty"] == selected_diff)
        and (selected_topic == "All" or p["topic"] == selected_topic)
    ]

    if not filtered:
        st.warning("No problems match the current filter selection.")
        st.stop()

    # Pre-select if redirected from Due list
    default_index = 0
    if "selected_problem_id" in st.session_state:
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

    # Workbench layout: Left narrower (4), Right wide & primary (7)
    left_col, right_col = st.columns([4, 7], gap="large")

    with left_col:
        with st.container(border=True):
            st.subheader(current_problem["title"])
            st.caption(
                f"Track: {current_problem['track'].upper()} | "
                f"Topic: {current_problem['topic']} | "
                f"Difficulty: {current_problem['difficulty'].title()}"
            )
            st.markdown("---")
            st.markdown(current_problem["statement_md"])

        st.subheader("Visible Test Cases")
        for i, tc in enumerate(current_problem["visible_tests"], 1):
            with st.expander(f"Visible Case #{i}", expanded=True):
                st.code(f"Input: {tc['input_args']}\nExpected: {tc['expected']}", language="python")

        # Progressive Hint Ladder
        with st.container(border=True):
            st.subheader("Hint Ladder")
            hint_key = f"hint_level_{current_problem['id']}"
            if hint_key not in st.session_state:
                st.session_state[hint_key] = 0

            current_level = st.session_state[hint_key]
            if st.button("Reveal Next Hint", key=f"btn_hint_{current_problem['id']}") and current_level < 3:
                st.session_state[hint_key] += 1
                st.rerun()

            if current_level > 0:
                for lvl in range(1, current_level + 1):
                    st.info(f"Hint {lvl}: {current_problem['hints'][lvl - 1]}")

                if st.button("Ask AI to Explain Hint", key=f"btn_ai_hint_{current_problem['id']}"):
                    with st.spinner("Asking local AI (Ollama)..."):
                        code_val = st.session_state.get(f"code_{current_problem['id']}", current_problem["starter_code"])
                        ai_hint_explanation = explain_hint(current_problem, code_val, hint_level=current_level)
                        st.markdown(ai_hint_explanation)

    with right_col:
        with st.container(border=True):
            st.subheader("Solution Editor")
            editor_key = f"practice_editor_{current_problem['id']}"
            initial_code = current_problem["starter_code"]

            # Ensure editor always opens prefilled with problem starter code
            if editor_key not in st.session_state:
                st.session_state[editor_key] = initial_code

            user_code = render_editor(initial_code, key=editor_key, height=440)
            st.session_state[f"code_{current_problem['id']}"] = user_code

            # Run action
            run_submitted = st.button("Run & Submit", type="primary", key=f"btn_run_{current_problem['id']}")
            is_demo_fail = st.query_params.get("demo_fail", "").lower() == "true"

            # Check empty or unchanged starter code guard (U1)
            if run_submitted:
                stripped_code = user_code.strip()
                stripped_starter = initial_code.strip()
                if not stripped_code or stripped_code == stripped_starter:
                    st.warning(
                        f"Write your solution first — the judge expected '{current_problem['function_name']}(...)'."
                    )
                    run_submitted = False

        if run_submitted or is_demo_fail:
            exec_code = (
                f"def {current_problem['function_name']}(*args, **kwargs):\n    return None\n"
                if (is_demo_fail and not run_submitted)
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

            with st.container(border=True):
                st.subheader("Judge Results")
                if status == "pass":
                    st.markdown(f":green-background[**PASS**] **{passed}/{total}** tests passed (`{runtime} ms`)")
                elif status == "fail":
                    st.markdown(f":red-background[**FAIL**] **{passed}/{total}** tests passed (`{runtime} ms`)")
                    st.markdown("##### Failed Cases:")
                    for fc in judge_result.get("failed_cases", []):
                        with st.container(border=True):
                            st.markdown(f"**Input:** `{fc.get('input_args')}`")
                            st.markdown(f"**Expected:** `{fc.get('expected')}`")
                            st.markdown(f"**Got:** `{fc.get('got')}`")
                elif status == "timeout":
                    st.markdown(":orange-background[**TIMEOUT**] Execution exceeded 3.0s time limit.")
                    st.warning(judge_result.get("stderr", "Execution timed out."))
                elif status == "error":
                    st.markdown(":red-background[**ERROR**] Execution error")
                    expected_fn = judge_result.get("expected_function")
                    found_fns = judge_result.get("found_functions")
                    if expected_fn and found_fns is not None:
                        st.error(f"Function definition mismatch: Expected '{expected_fn}', but found {found_fns}.")
                    st.code(judge_result.get("stderr", "Execution error"), language="text")

            # Static Code Quality (Ruff)
            with st.container(border=True):
                st.subheader("Static Code Quality (Ruff)")
                with st.spinner("Running Ruff static analysis..."):
                    ruff_res = run_ruff_lint(user_code)
                    if not ruff_res["findings"]:
                        st.success("Clean code: Ruff found 0 diagnostics.")
                    else:
                        st.info(f"Ruff Diagnostic Summary: {ruff_res['summary']}")
                        for finding in ruff_res["findings"]:
                            st.markdown(f"- Line {finding['line']}, Col {finding['col']} `[{finding['code']}]`: {finding['message']}")

            # Post-Pass Conceptual Review
            if status == "pass":
                with st.container(border=True):
                    st.subheader("Post-Pass AI Review (Ollama)")
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
