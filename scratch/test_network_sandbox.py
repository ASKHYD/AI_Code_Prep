import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coach.judge import run_solution
from coach.problems import load_problem

p_bs = load_problem("binary-search").model_dump()

code_net = """
import urllib.request
def binary_search(nums: list, target: int) -> int:
    try:
        resp = urllib.request.urlopen("https://httpbin.org/get", timeout=1.0)
        return 999
    except Exception as e:
        raise RuntimeError(f"Network call blocked/failed: {e}")
"""
res = run_solution(code_net, p_bs)
print("Network test result:", res)

