import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coach.llm_hints import explain_hint
from coach.problems import load_problem

p_bs = load_problem("binary-search").model_dump()

# Dead port
os.environ["OLLAMA_HOST"] = "http://127.0.0.1:54321"
res_fallback = explain_hint(p_bs, p_bs["starter_code"], hint_level=1)
print("Fallback response:")
print(repr(res_fallback))

