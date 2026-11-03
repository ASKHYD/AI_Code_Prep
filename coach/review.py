"""
Static Code Review Integration with Ruff.
Runs Ruff as a subprocess on candidate code and surfaces real lint diagnostics.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _find_ruff_executable() -> str:
    """Locates the ruff binary in venv or PATH."""
    venv_ruff = Path(sys.prefix) / "Scripts" / "ruff.exe"
    if venv_ruff.is_file():
        return str(venv_ruff)

    posix_ruff = Path(sys.prefix) / "bin" / "ruff"
    if posix_ruff.is_file():
        return str(posix_ruff)

    which_ruff = shutil.which("ruff")
    if which_ruff:
        return which_ruff

    return "ruff"


def run_ruff_lint(code: str) -> dict[str, Any]:
    """
    Executes Ruff static analysis on a string of python code.
    Returns:
    {
        "findings": [
            {
                "line": int,
                "col": int,
                "code": str,
                "message": str
            }
        ],
        "summary": str
    }
    """
    ruff_bin = _find_ruff_executable()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "submission.py"
        temp_file.write_text(code, encoding="utf-8")

        try:
            proc = subprocess.run(
                [
                    ruff_bin,
                    "check",
                    "--output-format",
                    "json",
                    str(temp_file)
                ],
                capture_output=True,
                text=True,
                timeout=5.0
            )
            raw_stdout = proc.stdout.strip()
            if not raw_stdout:
                return {"findings": [], "summary": "Clean code: no issues found."}

            items = json.loads(raw_stdout)
            findings = []
            for item in items:
                location = item.get("location", {})
                findings.append({
                    "line": location.get("row", 1),
                    "col": location.get("column", 1),
                    "code": item.get("code", ""),
                    "message": item.get("message", "")
                })

            summary = f"Found {len(findings)} style/correctness diagnostic(s)."
            return {"findings": findings, "summary": summary}
        except Exception as e:
            return {
                "findings": [],
                "summary": f"Static analysis unavailable: {type(e).__name__} ({e})"
            }
