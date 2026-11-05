import os
import subprocess
import importlib.util

print("--- RESOURCE GATE LOAD LINES ---")
skills = ['ui-ux-pro-max', 'ui-styling', 'design-system', 'brand', 'banner-design', 'slides', 'design']
for s in skills:
    p = os.path.join(r'e:\resume_project\.agents\skills', s)
    status = 'LOADED' if os.path.exists(p) else 'MISSING'
    print(f"Skill .agents/skills/{s}: {status} at {p}")

try:
    res = subprocess.run(['npx', 'impeccable', '--version'], capture_output=True, text=True, shell=True)
    ver = res.stdout.strip() or res.stderr.strip()
    imp_status = f"LOADED (impeccable@{ver})" if res.returncode == 0 else f"ERROR {res.returncode}"
except Exception as e:
    imp_status = f"MISSING ({e})"
print(f"Impeccable: {imp_status}")

st_skills_path = r'C:\Users\MS Computer\agent-resources\agent-skills\developing-with-streamlit'
st_status = "LOADED" if os.path.exists(st_skills_path) else "MISSING"
print(f"streamlit/agent-skills (developing-with-streamlit): {st_status} at {st_skills_path}")

extras_found = importlib.util.find_spec('streamlit_extras') is not None
extras_status = "LOADED" if extras_found else "MISSING (native fallback st.container(border=True) + st.metric applies)"
print(f"streamlit-extras: {extras_status}")
