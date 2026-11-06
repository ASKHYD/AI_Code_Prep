import subprocess
import json
import pathlib

SCREENS = [
    ("Home", "http://127.0.0.1:8501/?screen=home"),
    ("Practice", "http://127.0.0.1:8501/?screen=practice"),
    ("Mock", "http://127.0.0.1:8501/?screen=mock"),
    ("Dashboard", "http://127.0.0.1:8501/?screen=dashboard"),
]

results = {}

for name, url in SCREENS:
    print(f"Scanning {name}: {url} ...")
    cmd = ["npx", "impeccable", "detect", url]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    results[name] = {
        "url": url,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip()
    }
    print(f"  {name} Exit Code: {proc.returncode}")
    if proc.stderr:
        print(f"  {name} Stderr:\n{proc.stderr.strip()}")
    if proc.stdout:
        print(f"  {name} Stdout:\n{proc.stdout.strip()}")

out_path = pathlib.Path("docs/screenshots/r6/impeccable_all4_results.json")
out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"Results saved to {out_path}")

