"""
scratch/run_impeccable_audit.py

Executes Impeccable UI anti-pattern and quality detection across all 4 live application states:
  1. Home Screen: ?screen=home
  2. Practice Arena: ?screen=practice
  3. Mock Interview (Running): ?screen=mock
  4. Dashboard: ?screen=dashboard

Asserts zero primary (P0/P1) findings across all states.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
STREAMLIT_PORT = 8501
PYTHON_PATH = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"

SCREENS = [
    ("Home Screen", f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=home"),
    ("Practice Arena", f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice^&problem=longest-substring"),
    ("Mock Interview (Running)", f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=mock^&mock_state=running"),
    ("Dashboard", f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=dashboard"),
]


def is_streamlit_running(port: int = STREAMLIT_PORT) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_streamlit() -> subprocess.Popen | None:
    if is_streamlit_running():
        print(f"[Streamlit] Already running on port {STREAMLIT_PORT}", flush=True)
        return None

    print(f"[Streamlit] Launching local Streamlit on port {STREAMLIT_PORT}...", flush=True)
    proc = subprocess.Popen(
        [
            str(PYTHON_PATH),
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(STREAMLIT_PORT),
            "--server.address",
            "127.0.0.1",
        ],
        cwd=str(WORKSPACE_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(40):
        time.sleep(0.5)
        if is_streamlit_running():
            print(f"[Streamlit] Ready at http://127.0.0.1:{STREAMLIT_PORT}", flush=True)
            return proc

    raise RuntimeError("Streamlit failed to start within timeout.")


def run_impeccable_detect(url: str) -> tuple[int, dict | list | None, str, str]:
    cmd = f'npx impeccable detect "{url}" --json'
    print(f"\n[Impeccable] Running command: {cmd}", flush=True)
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=str(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    exit_code = result.returncode

    parsed_json = None
    if stdout:
        try:
            parsed_json = json.loads(stdout)
        except Exception as e:
            print(f"[Warning] Failed to parse JSON: {e}", flush=True)

    return exit_code, parsed_json, stdout, stderr


def main() -> int:
    st_proc = None
    total_primary_findings = 0
    all_findings_summary = []

    try:
        st_proc = start_streamlit()
        time.sleep(2)

        for name, url in SCREENS:
            print(f"\n========================================================", flush=True)
            print(f"Auditing State: {name}", flush=True)
            print(f"Target URL: {url}", flush=True)
            print(f"========================================================", flush=True)

            exit_code, data, stdout, stderr = run_impeccable_detect(url)
            print(f"[Result] Exit Code: {exit_code}", flush=True)
            if stdout:
                print(f"[Raw Output Preview]:\n{stdout[:1500]}\n...", flush=True)
            if stderr:
                print(f"[Raw Stderr]:\n{stderr[:1000]}", flush=True)

            findings = []
            if isinstance(data, list):
                findings = data
            elif isinstance(data, dict):
                findings = data.get("findings", [])

            print(f"Total Findings Count: {len(findings)}", flush=True)
            for f in findings:
                print(f"  Finding: {f}", flush=True)

            # Check if any finding has severity that is primary or not advisory
            primaries = [
                f for f in findings
                if isinstance(f, dict) and f.get("severity") != "advisory"
            ]
            advisories = [
                f for f in findings
                if isinstance(f, dict) and f.get("severity") == "advisory"
            ]

            total_primary_findings += len(primaries)

            all_findings_summary.append({
                "screen": name,
                "url": url,
                "exit_code": exit_code,
                "primary": len(primaries),
                "advisories": len(advisories),
                "findings": findings
            })

        print("\n================ FINAL IMPECCABLE AUDIT REPORT ================", flush=True)
        for s in all_findings_summary:
            status = "PASSED (0 Primary)" if s["primary"] == 0 else f"FAILED ({s['primary']} Primary)"
            print(f"  - {s['screen']:<26}: {status} (Advisories: {s['advisories']}, Exit Code: {s['exit_code']})", flush=True)

        if total_primary_findings > 0:
            print(f"\n❌ AUDIT FAILED: {total_primary_findings} primary finding(s) detected across screens.", flush=True)
            return 1

        print(f"\n✅ AUDIT PASSED: Zero primary findings across all 4 live states!", flush=True)
        return 0

    finally:
        if st_proc:
            print("\n[Streamlit] Terminating spawned Streamlit instance...", flush=True)
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(st_proc.pid)], capture_output=True)
            except Exception:
                try:
                    st_proc.kill()
                except Exception:
                    pass


if __name__ == "__main__":
    sys.exit(main())
