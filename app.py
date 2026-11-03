"""
AI Coding Prep Coach — Streamlit Application.
Zero-cost, local-only coding interview preparation platform.
The judge is CODE, not AI.
"""

from __future__ import annotations

import time
from datetime import date, datetime
from typing import Any

import streamlit as st

from coach.judge import run_solution
from coach.llm_hints import explain_hint, review_code
from coach.problems import load_all_problems
from coach.review import run_ruff_lint
from coach.store import CoachStore

# Page configuration
st.set_page_config(
    page_title="AI Coding Prep Coach",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Custom CSS for clean UI density and monospace font
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .badge-pass { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-fail { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-timeout { background-color: #fd7e14; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .badge-error { background-color: #6f42c1; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
    .failed-case-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffeeba;
        padding: 12px;
        margin-top: 8px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


# Code Editor helper with graceful fallback
def render_editor(code: str, key: str, height: int = 350) -> str:
    """Renders Monaco code editor via streamlit-code-editor with text_area fallback."""
    try:
        from code_editor import code_editor
        editor_custom_btns = [
            {
                "name": "Copy",
                "feather": "Copy",
                "hasText": True,
                "alwaysOn": True,
                "commands": ["copyAll"],
                "style": {"top": "0.46rem", "right": "0.4rem"}
            }
        ]
        editor_response = code_editor(
            code,
            lang="python",
            height=height,
            key=key,
            buttons=editor_custom_btns,
            options={"wrap": True, "showLineNumbers": True}
        )
        # Handle dict or string response
        if isinstance(editor_response, dict) and "text" in editor_response:
            return editor_response["text"]
        elif isinstance(editor_response, str) and editor_response.strip():
            return editor_response
        return code
    except Exception:
        # Monospace fallback
        return st.text_area(
            "Code Editor (Fallback Mode)",
            value=code,
            height=height,
            key=f"{key}_textarea",
            help="Using standard monospace editor fallback."
        )


# Sidebar Navigation
qp_screen = st.query_params.get("screen", "").lower()
nav_options = ["🏠 Home / Due Review", "💻 Practice Mode", "⏱️ Mock Interview", "📊 Dashboard"]
default_nav_idx = 0
if qp_screen == "practice":
    default_nav_idx = 1
elif qp_screen == "mock":
    default_nav_idx = 2
elif qp_screen == "dashboard":
    default_nav_idx = 3

st.sidebar.title("⚡ AI Coding Prep Coach")
st.sidebar.caption("Zero Cost • Code-Judged • Offline-Ready")

nav_choice = st.sidebar.radio(
    "Navigation",
    nav_options,
    index=default_nav_idx
)

st.sidebar.markdown("---")
streak_count = store.current_streak()
st.sidebar.metric("🔥 Active Streak", f"{streak_count} days")
due_list = store.due_problems()
st.sidebar.metric("📅 Due for Review", f"{len(due_list)} problems")


# ==============================================================================
# SCREEN 1: HOME / DUE REVIEW
# ==============================================================================
if nav_choice == "🏠 Home / Due Review":
    st.header("🏠 Daily Review & Preparation Queue")
    st.write(
        "Welcome to your AI Coding Prep Coach. Problems are scheduled using an interview-targeted "
        "spaced repetition schedule (1 / 1 / 3 / 7 / 21 days) based strictly on objective test results."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔥 Current Streak", f"{streak_count} days")
    with c2:
        st.metric("📅 Problems Due Today", len(due_list))
    with c3:
        st.metric("📚 Total Problems Available", len(all_problems))

    st.subheader("🎯 Due for Review Today")
    if not due_list:
        st.success("🎉 You are all caught up! No problems due for review today.")
        st.info("Head over to **Practice Mode** in the sidebar to solve a new problem.")
    else:
        for item in due_list:
            prob = problems_by_id.get(item["problem_id"])
            if not prob:
                continue
            with st.container():
                cols = st.columns([3, 1, 1, 1, 2])
                cols[0].markdown(f"**{prob['title']}** (`{prob['topic']}`)")
                cols[1].caption(f"Track: {prob['track'].upper()}")
                cols[2].caption(f"Difficulty: {prob['difficulty'].title()}")
                cols[3].caption(f"Passes: {item['consecutive_passes']}")
                if cols[4].button("Practice Now", key=f"due_btn_{prob['id']}"):
                    st.session_state["selected_problem_id"] = prob["id"]
                    st.session_state["nav_switch"] = "💻 Practice Mode"
                    st.rerun()

    st.subheader("📜 Recent Practice Attempts")
    recents = store.get_recent_attempts(limit=5)
    if recents:
        for r in recents:
            prob_title = problems_by_id.get(r["problem_id"], {}).get("title", r["problem_id"])
            st.markdown(
                f"- **{r['attempt_date']}** | Problem: **{prob_title}** | "
                f"Result: `{r['status'].upper()}` | Runtime: `{r['runtime_ms']}ms` | Hints: `{r['hints_used']}`"
            )
    else:
        st.write("No attempts recorded yet. Start practicing!")


# ==============================================================================
# SCREEN 2: PRACTICE MODE
# ==============================================================================
elif nav_choice == "💻 Practice Mode":
    st.header("💻 Practice Arena")

    # Filter controls
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

    # Two column layout: Left = Description & Tests, Right = Editor & Judge
    left_col, right_col = st.columns([1, 1], gap="medium")

    with left_col:
        st.subheader(current_problem["title"])
        badge_color = "green" if current_problem["difficulty"] == "easy" else ("orange" if current_problem["difficulty"] == "medium" else "red")
        st.markdown(
            f"**Track**: `{current_problem['track'].upper()}` | "
            f"**Topic**: `{current_problem['topic']}` | "
            f"**Difficulty**: :{badge_color}[{current_problem['difficulty'].title()}]"
        )
        st.markdown("---")
        st.markdown(current_problem["statement_md"])

        st.subheader("🔍 Visible Test Cases")
        for i, tc in enumerate(current_problem["visible_tests"], 1):
            with st.expander(f"Visible Test Case #{i}", expanded=True):
                st.code(f"Input: {tc['input_args']}\nExpected: {tc['expected']}", language="python")

        # Progressive Hint Ladder
        st.subheader("💡 Progressive Hint Ladder")
        hint_key = f"hint_level_{current_problem['id']}"
        if hint_key not in st.session_state:
            st.session_state[hint_key] = 0

        current_level = st.session_state[hint_key]
        h_col1, h_col2 = st.columns([1, 1])
        if h_col1.button("Reveal Next Hint", key=f"btn_hint_{current_problem['id']}"):
            if current_level < 3:
                st.session_state[hint_key] += 1
                st.rerun()

        if current_level > 0:
            for lvl in range(1, current_level + 1):
                st.info(f"**Hint {lvl}**: {current_problem['hints'][lvl - 1]}")

            if st.button("🤖 Ask AI to Explain Hint", key=f"btn_ai_hint_{current_problem['id']}"):
                with st.spinner("Asking local AI (Ollama)..."):
                    # Use current editor code if available
                    code_val = st.session_state.get(f"code_{current_problem['id']}", current_problem["starter_code"])
                    ai_hint_explanation = explain_hint(current_problem, code_val, hint_level=current_level)
                    st.markdown(ai_hint_explanation)

    with right_col:
        st.subheader("📝 Python Solution")
        editor_key = f"code_editor_{current_problem['id']}"
        initial_code = current_problem["starter_code"]

        user_code = render_editor(initial_code, key=editor_key, height=380)
        st.session_state[f"code_{current_problem['id']}"] = user_code

        col_act1, col_act2 = st.columns([1, 2])
        run_submitted = col_act1.button("🚀 Run & Submit", type="primary", key=f"btn_run_{current_problem['id']}")
        is_demo_fail = st.query_params.get("demo_fail", "").lower() == "true"

        if run_submitted or is_demo_fail:
            exec_code = (
                f"def {current_problem['function_name']}(*args, **kwargs):\n    return None\n"
                if (is_demo_fail and not run_submitted)
                else user_code
            )
            with st.spinner("Executing solution inside secure sandbox..."):
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

            st.markdown("---")
            st.subheader("⚖️ Judge Results")

            if status == "pass":
                st.markdown(f'<span class="badge-pass">PASS</span> **{passed}/{total} tests passed** ({runtime} ms)', unsafe_allow_html=True)
                st.balloons()
            elif status == "fail":
                st.markdown(f'<span class="badge-fail">FAIL</span> **{passed}/{total} tests passed** ({runtime} ms)', unsafe_allow_html=True)
                st.error("Some test cases failed.")
                for fc in judge_result.get("failed_cases", []):
                    st.markdown(f"""
                    <div class="failed-case-card">
                        <b>Input:</b> {fc.get('input_args')}<br>
                        <b>Expected:</b> {fc.get('expected')}<br>
                        <b>Got:</b> {fc.get('got')}
                    </div>
                    """, unsafe_allow_html=True)
            elif status == "timeout":
                st.markdown('<span class="badge-timeout">TIMEOUT</span> Execution exceeded 3.0s time limit.', unsafe_allow_html=True)
                st.warning(judge_result.get("stderr", "Execution timed out."))
            elif status == "error":
                st.markdown('<span class="badge-error">ERROR</span> Runtime or Syntax Exception', unsafe_allow_html=True)
                st.code(judge_result.get("stderr", "Unknown execution error"), language="text")

            # Post-Submission Static Code Review (Ruff)
            st.markdown("---")
            st.subheader("🔍 Static Code Quality (Ruff)")
            with st.spinner("Running Ruff static analysis..."):
                ruff_res = run_ruff_lint(user_code)
                if not ruff_res["findings"]:
                    st.success("✅ Clean code: Ruff found 0 style/correctness diagnostics.")
                else:
                    st.info(f"Ruff Diagnostic Summary: {ruff_res['summary']}")
                    for finding in ruff_res["findings"]:
                        st.markdown(f"- **Line {finding['line']}, Col {finding['col']}** `[{finding['code']}]`: {finding['message']}")

            # Post-Pass Optional AI Review
            if status == "pass":
                st.markdown("---")
                st.subheader("🤖 Post-Pass AI Review (Ollama)")
                with st.spinner("Generating conceptual review..."):
                    review_text = review_code(current_problem, user_code)
                    st.info(review_text)


# ==============================================================================
# SCREEN 3: MOCK INTERVIEW MODE
# ==============================================================================
elif nav_choice == "⏱️ Mock Interview":
    st.header("⏱️ Mock Interview Arena")
    st.write(
        "A 45-minute timed simulation of a technical coding round. "
        "Consists of **2 problems** (1 Medium DSA + 1 Hard or Python Practical). "
        "You can use progressive hints, but hints used and completion time are tracked on your final scorecard."
    )

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

    if st.session_state["mock_state"] == "unstarted":
        if st.button("🚀 Start 45-Minute Mock Interview", type="primary"):
            # Select 2 problems: 1 medium DSA + 1 practical or hard
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
            st.rerun()

    elif st.session_state["mock_state"] == "running":
        elapsed_sec = time.time() - st.session_state["mock_start_time"]
        remaining_sec = max(0, int(st.session_state["mock_duration_sec"] - elapsed_sec))
        minutes = remaining_sec // 60
        seconds = remaining_sec % 60

        col_t1, col_t2 = st.columns([3, 1])
        col_t1.subheader("In Progress: Mock Technical Session")
        col_t2.markdown(f"### ⏳ `{minutes:02d}:{seconds:02d}`")

        p_list = st.session_state["mock_problems"]
        mock_tab1, mock_tab2 = st.tabs([f"Problem 1: {p_list[0]['title']}", f"Problem 2: {p_list[1]['title']}"])

        with mock_tab1:
            prob1 = p_list[0]
            st.markdown(f"**{prob1['title']}** (`{prob1['topic']}` | {prob1['difficulty'].title()})")
            st.markdown(prob1["statement_md"])
            code1 = render_editor(prob1["starter_code"], key="mock_editor_p1", height=280)

            c_h1, c_r1 = st.columns([1, 1])
            if c_h1.button("💡 Reveal Hint (Problem 1)"):
                if st.session_state["mock_p1_hints"] < 3:
                    st.session_state["mock_p1_hints"] += 1
                    st.rerun()
            if st.session_state["mock_p1_hints"] > 0:
                for h in range(st.session_state["mock_p1_hints"]):
                    st.info(f"Hint {h+1}: {prob1['hints'][h]}")

            if c_r1.button("Submit Problem 1", type="primary"):
                res1 = run_solution(code1, prob1)
                st.session_state["mock_p1_status"] = res1["status"]
                store.record_attempt(prob1["id"], res1["status"], res1["runtime_ms"], st.session_state["mock_p1_hints"], mode="mock")
                if res1["status"] == "pass":
                    st.success("✅ Problem 1 Passed!")
                else:
                    st.error(f"Problem 1: {res1['status'].upper()}")

        with mock_tab2:
            prob2 = p_list[1]
            st.markdown(f"**{prob2['title']}** (`{prob2['topic']}` | {prob2['difficulty'].title()})")
            st.markdown(prob2["statement_md"])
            code2 = render_editor(prob2["starter_code"], key="mock_editor_p2", height=280)

            c_h2, c_r2 = st.columns([1, 1])
            if c_h2.button("💡 Reveal Hint (Problem 2)"):
                if st.session_state["mock_p2_hints"] < 3:
                    st.session_state["mock_p2_hints"] += 1
                    st.rerun()
            if st.session_state["mock_p2_hints"] > 0:
                for h in range(st.session_state["mock_p2_hints"]):
                    st.info(f"Hint {h+1}: {prob2['hints'][h]}")

            if c_r2.button("Submit Problem 2", type="primary"):
                res2 = run_solution(code2, prob2)
                st.session_state["mock_p2_status"] = res2["status"]
                store.record_attempt(prob2["id"], res2["status"], res2["runtime_ms"], st.session_state["mock_p2_hints"], mode="mock")
                if res2["status"] == "pass":
                    st.success("✅ Problem 2 Passed!")
                else:
                    st.error(f"Problem 2: {res2['status'].upper()}")

        st.markdown("---")
        if st.button("🏁 Finish Mock Interview & Generate Scorecard"):
            st.session_state["mock_state"] = "completed"
            st.session_state["mock_finish_time"] = time.time()
            st.rerun()

    elif st.session_state["mock_state"] == "completed":
        st.subheader("🎯 Mock Interview Scorecard")
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
            label="📥 Download Scorecard (Markdown)",
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
elif nav_choice == "📊 Dashboard":
    st.header("📊 Performance & Analytics Dashboard")
    st.caption("All metrics computed strictly from SQLite history. Zero invented metrics.")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Current Streak", f"{streak_count} Days")
    col2.metric("📅 Due for Review", len(due_list))

    stats = store.topic_stats()
    total_attempts = sum(s["attempts"] for s in stats.values())
    total_passed = sum(s["passed"] for s in stats.values())
    overall_rate = round((total_passed / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
    col3.metric("🎯 Overall Pass Rate", f"{overall_rate}% ({total_passed}/{total_attempts})")

    st.markdown("---")
    st.subheader("Topic Mastery & Pass Rates")

    if not stats:
        st.info("No practice data available yet. Solve problems in Practice Mode to populate your dashboard!")
    else:
        try:
            import plotly.graph_objects as go
            topics_list = list(stats.keys())
            pass_rates = [stats[t]["pass_rate"] for t in topics_list]
            attempts_counts = [stats[t]["attempts"] for t in topics_list]

            fig = go.Figure(data=[
                go.Bar(
                    x=topics_list,
                    y=pass_rates,
                    text=[f"{rate}% ({stats[t]['passed']}/{stats[t]['attempts']})" for t, rate in zip(topics_list, pass_rates)],
                    textposition="auto",
                    marker_color="#4361ee"
                )
            ])
            fig.update_layout(
                title="Pass Rate by Topic (%)",
                xaxis_title="Topic",
                yaxis_title="Pass Rate (%)",
                yaxis={"range": [0, 105]},
                margin={"l": 40, "r": 40, "t": 40, "b": 40},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            # Fallback to Streamlit native chart
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
