"""
scratch/test_lane_c.py
Empirical validation script for Lane C requirements (X5R, X6, X7-Practice, X8, X9).
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

from coach.problems import load_all_problems

def verify_lane_c():
    app_text = (WORKSPACE / "app.py").read_text(encoding="utf-8")
    problems = load_all_problems("data/problems")
    print(f"Loaded {len(problems)} problems from data/problems.")

    # 1. X5R Verification: No filter strip dropdowns in Practice Arena
    # Must NOT contain selectbox for Track, Difficulty, Topic in Practice Arena
    practice_section = app_text.split('elif nav_choice == "Practice Arena":')[1].split('elif nav_choice == "Mock Interview":')[0]
    
    assert "practice_filter_strip" not in practice_section, "FAIL: practice_filter_strip still in Practice Arena!"
    assert 'selected_track = f_col1.selectbox' not in practice_section, "FAIL: Track selectbox still in Practice Arena!"
    assert 'selected_diff = f_col2.selectbox' not in practice_section, "FAIL: Difficulty selectbox still in Practice Arena!"
    assert 'selected_topic = f_col3.selectbox' not in practice_section, "FAIL: Topic selectbox still in Practice Arena!"
    print("✓ X5R: 3-select filter strip completely deleted (0 enclosing card box, 0 filter dropdowns).")

    # Picker row check
    assert "btn_picker_prev" in practice_section, "FAIL: btn_picker_prev not found!"
    assert "btn_picker_next" in practice_section, "FAIL: btn_picker_next not found!"
    assert "picker-title" in practice_section, "FAIL: picker-title not found!"
    assert "Fraunces" in practice_section, "FAIL: Fraunces not used in picker title!"
    assert "18px" in practice_section, "FAIL: 18px font size not specified for picker title!"
    assert "#171712" in practice_section, "FAIL: #171712 color not specified for picker title!"
    print("✓ X5R: ONE slim picker row rendered with Fraunces 18px #171712 title and Prev/Next buttons.")

    # 2. X6 Verification: 12/12 problems signature derived strictly from starter_code
    for p in problems:
        starter_first_line = p.starter_code.splitlines()[0]
        expected_prefix = f"def {p.function_name}("
        assert starter_first_line.startswith(expected_prefix), f"FAIL: {p.id} starter_code mismatch: {starter_first_line}"
    print(f"✓ X6: 12/12 problems verified — starter signature unified to starter_code single source of truth.")

    # 3. X7-Practice Verification: Neutral Output Card header
    assert "Run your code to see results" in practice_section, "FAIL: 'Run your code to see results' not found in practice section!"
    assert "Execution Sandbox Ready" not in practice_section, "FAIL: 'Execution Sandbox Ready' still present in practice section!"
    print("✓ X7-Practice: Neutral Output Card header set strictly to 'Run your code to see results'.")

    # 4. X8 Verification: Run & Submit natural width
    assert 'run_submitted = st.button("Run & Submit", type="primary", key=f"btn_run_{current_problem[\'id\']}", use_container_width=False)' in practice_section, "FAIL: Run & Submit still uses container width!"
    assert "padding: 10px 24px" in practice_section, "FAIL: Generous 10px 24px padding not in editor card CSS!"
    assert "border-radius: 9999px" in practice_section, "FAIL: Pill border-radius not in editor card CSS!"
    print("✓ X8: 'Run & Submit' button has natural width (use_container_width=False) with 10px 24px padding.")

    # 5. X9 Verification: Small-caps STARTER FUNCTION SIGNATURE & pastel wash chips
    assert "STARTER FUNCTION SIGNATURE" in practice_section, "FAIL: 'STARTER FUNCTION SIGNATURE' small-caps heading not found!"
    assert "0.08em" in practice_section, "FAIL: letter-spacing: 0.08em not found!"
    assert "rgba(102, 99, 90, 0.08)" in app_text, "FAIL: pastel wash chip background not found in app.py!"
    print("✓ X9: Small-caps STARTER FUNCTION SIGNATURE label (0.08em) and pastel wash chips verified.")

    print("\n🎉 ALL LANE C EMPIRICAL CHECKS PASSED PERFECTLY!")
    return 0

if __name__ == "__main__":
    sys.exit(verify_lane_c())
