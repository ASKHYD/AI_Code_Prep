"""
Sandboxed Code Judge Engine.
Executes candidate solutions against test cases in an isolated subprocess.
Uses Python Standard Library ONLY (subprocess, tempfile, json, time).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Any


def _build_runner_script(user_code: str, function_name: str, tests: list[dict[str, Any]]) -> str:
    """Builds the standalone python script executed inside the sandbox."""
    tests_json = json.dumps(tests)
    return f"""import json
import sys
import copy

# User code injection
{user_code}

tests = json.loads({json.dumps(tests_json)})
fn_name = {json.dumps(function_name)}

if fn_name not in globals():
    sys.stderr.write(f"Function '{{fn_name}}' was not defined in the submitted code.\\n")
    sys.exit(1)

func = globals()[fn_name]
failed_cases = []
passed = 0

for test in tests:
    input_args = copy.deepcopy(test.get("input_args", []))
    expected = test.get("expected")
    try:
        got = func(*input_args)
        if got == expected:
            passed += 1
        else:
            failed_cases.append({{
                "input_args": test.get("input_args"),
                "expected": expected,
                "got": got
            }})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        sys.stderr.write(f"Runtime Exception in test: {{tb}}\\n")
        print(json.dumps({{
            "status": "error",
            "passed": passed,
            "total": len(tests),
            "failed_cases": [{{
                "input_args": test.get("input_args"),
                "expected": expected,
                "got": f"Exception: {{type(e).__name__}}: {{e}}"
            }}],
            "error_message": f"{{type(e).__name__}}: {{e}}"
        }}))
        sys.exit(0)

status = "pass" if passed == len(tests) else "fail"
print(json.dumps({{
    "status": status,
    "passed": passed,
    "total": len(tests),
    "failed_cases": failed_cases
}}))
"""


def run_solution(code: str, problem: dict[str, Any]) -> dict[str, Any]:
    """
    Executes user code against test cases in a subprocess sandbox.
    Constraints:
    - 3s timeout (or problem["time_limit_sec"])
    - Empty temporary directory as cwd
    - Stripped environment (no API keys, minimal system vars)
    """
    tests = list(problem.get("visible_tests", [])) + list(problem.get("hidden_tests", []))
    function_name = problem.get("function_name", "solution")
    time_limit_sec = float(problem.get("time_limit_sec", 3.0))

    # Strip environment: only keep safe Windows system essentials
    safe_keys = {"PATH", "SYSTEMROOT", "COMSPEC", "TEMP", "TMP"}
    sandboxed_env = {k: os.environ[k] for k in safe_keys if k in os.environ}
    sandboxed_env["PYTHONPATH"] = ""
    sandboxed_env["PYTHONNOUSERSITE"] = "1"

    runner_code = _build_runner_script(code, function_name, tests)

    start_time = time.perf_counter()
    with tempfile.TemporaryDirectory() as temp_dir:
        runner_path = os.path.join(temp_dir, "solution_runner.py")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(runner_code)

        try:
            proc = subprocess.run(
                [sys.executable, runner_path],
                cwd=temp_dir,
                env=sandboxed_env,
                capture_output=True,
                text=True,
                timeout=time_limit_sec,
            )
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            if proc.returncode != 0:
                return {
                    "status": "error",
                    "passed": 0,
                    "total": len(tests),
                    "failed_cases": [],
                    "runtime_ms": elapsed_ms,
                    "stderr": proc.stderr or proc.stdout,
                }

            try:
                # Output might have stray prints before json
                lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
                payload_line = lines[-1] if lines else "{}"
                data = json.loads(payload_line)
                data["runtime_ms"] = elapsed_ms
                data["stderr"] = proc.stderr
                return data
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "passed": 0,
                    "total": len(tests),
                    "failed_cases": [],
                    "runtime_ms": elapsed_ms,
                    "stderr": f"Failed to parse test runner output:\\n{proc.stdout}",
                }

        except subprocess.TimeoutExpired:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return {
                "status": "timeout",
                "passed": 0,
                "total": len(tests),
                "failed_cases": [],
                "runtime_ms": elapsed_ms,
                "stderr": f"Execution timed out after {time_limit_sec:.1f} seconds.",
            }
