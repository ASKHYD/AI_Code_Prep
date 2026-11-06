import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from coach.judge import run_solution
from coach.problems import load_problem

p_bs = load_problem("binary-search").model_dump()

# Case 1: Wrong solution
code_wrong = """
def binary_search(nums: list, target: int) -> int:
    return -1
"""
res_wrong = run_solution(code_wrong, p_bs)
print("Case 1 (Wrong):", res_wrong)

# Case 2: Infinite loop
code_loop = """
def binary_search(nums: list, target: int) -> int:
    while True:
        pass
"""
t0 = time.perf_counter()
res_loop = run_solution(code_loop, p_bs)
wall_time = time.perf_counter() - t0
print(f"Case 2 (Timeout): status={res_loop['status']}, wall_time={wall_time:.2f}s, runtime_ms={res_loop.get('runtime_ms')}")

# Case 3: Syntax error
code_syntax = """
def binary_search(nums: list, target: int) -> int:
    this is invalid syntax !!!
"""
res_syntax = run_solution(code_syntax, p_bs)
print("Case 3 (Syntax error):", res_syntax)

# Case 4: Network access attempt
code_network = """
import socket
def binary_search(nums: list, target: int) -> int:
    s = socket.socket()
    s.settimeout(1.0)
    s.connect(("8.8.8.8", 53))
    return 0
"""
res_network = run_solution(code_network, p_bs)
print("Case 4 (Network access):", res_network)

