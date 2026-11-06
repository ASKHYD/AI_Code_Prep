import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coach.judge import run_solution
from coach.problems import load_problem

p_bs = load_problem("binary-search").model_dump()

code_sock = """
import socket
def binary_search(nums: list, target: int) -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    s.connect(("10.255.255.1", 80))  # unreachable route
    return 0
"""
res = run_solution(code_sock, p_bs)
print("Socket unreachable result:", res)

