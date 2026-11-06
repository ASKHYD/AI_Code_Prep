r"""
scratch/test_editor_height.py
"""
import streamlit as st
from code_editor import code_editor

st.set_page_config(layout="wide")

st.write("### Testing Editor Height")
test_variant = st.query_params.get("variant", "string")

code = """def longest_substring(s: str) -> int:
    # Sliding window
    last_seen = {}
    return 0
"""

if test_variant == "string":
    st.write("Variant: height='450px'")
    res = code_editor(code, lang="python", theme="one_dark", height="450px", key="ed_str", options={"wrap": False, "showLineNumbers": True, "fontSize": 14})
elif test_variant == "tuple":
    st.write("Variant: height=[24, 35]")
    res = code_editor(code, lang="python", theme="one_dark", height=[24, 35], key="ed_tup", options={"wrap": False, "showLineNumbers": True, "fontSize": 14})
elif test_variant == "int":
    st.write("Variant: height=440")
    res = code_editor(code, lang="python", theme="one_dark", height=440, key="ed_int", options={"wrap": False, "showLineNumbers": True, "fontSize": 14})

