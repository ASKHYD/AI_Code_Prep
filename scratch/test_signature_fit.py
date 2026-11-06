r"""
scratch/test_signature_fit.py
"""
import streamlit as st
from code_editor import code_editor

st.set_page_config(layout="wide")

st.markdown("""
<style>
div[data-testid="stSidebar"] {
    min-width: 336px !important;
    max-width: 336px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.write("Sidebar navigation")

col_ratio = st.query_params.get("ratio", "4_8")
font_sz = float(st.query_params.get("font_size", "13.5"))

if col_ratio == "4_8":
    ratios = [4, 8]
elif col_ratio == "3.8_8.2":
    ratios = [3.8, 8.2]
elif col_ratio == "3.5_8.5":
    ratios = [3.5, 8.5]
else:
    ratios = [4, 7]

left, right = st.columns(ratios, gap="large")

with left:
    st.info("Left column (Filter + Statement)")

with right:
    # Longest problem signature: log-timestamp-filter
    longest_code = '''def filter_log_events(log_lines: list, start_time: str, end_time: str) -> list:
    """Filter log entries between start_time and end_time inclusive."""
    # Filter log lines
    return []
'''
    res = code_editor(
        longest_code,
        lang="python",
        theme="one_dark",
        height="450px",
        key="test_editor",
        options={
            "wrap": False,
            "showLineNumbers": True,
            "fontSize": font_sz,
        },
        props={"style": {"backgroundColor": "#14161A", "color": "#F2F2ED", "borderRadius": "8px"}},
        response_mode="debounce",
    )

