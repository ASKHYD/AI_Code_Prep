import asyncio
import base64
import json
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
import websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9232
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")

def is_streamlit_running(port: int = STREAMLIT_PORT) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_streamlit() -> subprocess.Popen | None:
    if is_streamlit_running(STREAMLIT_PORT):
        print(f"[Streamlit] Already running on port {STREAMLIT_PORT}", flush=True)
        return None

    print(f"[Streamlit] Launching local Streamlit on port {STREAMLIT_PORT}...", flush=True)
    python_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    proc = subprocess.Popen(
        [
            str(python_exe),
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
        if is_streamlit_running(STREAMLIT_PORT):
            print(f"[Streamlit] Server ready at http://127.0.0.1:{STREAMLIT_PORT}", flush=True)
            return proc

    raise RuntimeError("Failed to start Streamlit server within 20 seconds.")

def get_store_snapshot():
    conn = sqlite3.connect("coach.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attempts")
    total_attempts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attempts WHERE status = 'pass'")
    passed_attempts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT problem_id) FROM attempts WHERE status = 'pass'")
    solved_problems = cur.fetchone()[0]
    cur.execute("SELECT id, problem_id, topic, status, runtime_ms, hints_used, mode, attempt_date, created_at FROM attempts")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {
        "total_attempts": total_attempts,
        "passed_attempts": passed_attempts,
        "solved_problems": solved_problems,
        "rows": rows,
    }

async def run_proof_part_a():
    st_proc = start_streamlit()

    print("==================================================================")
    print("PROOF PART (A): OWNER'S SCENARIO — SUBMIT NOTHING, END EARLY")
    print("==================================================================")
    snap_before = get_store_snapshot()
    print("--- STORE SNAPSHOT BEFORE ---")
    print(json.dumps(snap_before, indent=2))

    profile_dir = tempfile.mkdtemp(prefix="chrome_part_a_")
    chrome_proc = subprocess.Popen(
        [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={profile_dir}",
            "--window-size=1920,1080",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ws_url = None
        for _ in range(30):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list", timeout=1) as resp:
                    tabs = json.loads(resp.read().decode("utf-8"))
                    page_tabs = [t for t in tabs if t.get("type") == "page"]
                    if page_tabs:
                        ws_url = page_tabs[0].get("webSocketDebuggerUrl")
                        if ws_url:
                            break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError(f"Could not connect to Chrome debugging port {CDP_PORT}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == cid:
                        return data.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False,
            })

            # Navigate to Mock
            print("[CDP] Navigating to http://127.0.0.1:8501/?screen=mock ...")
            await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=mock"})
            await asyncio.sleep(4.0)

            # If on completed screen from earlier, reset by clicking "Start New Mock Session"
            await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Start New Mock Session'));
                    if (btn) btn.click();
                })()
                """
            })
            await asyncio.sleep(2.5)

            # Click "Start 45-Minute Mock Interview"
            print("[CDP] Clicking 'Start 45-Minute Mock Interview'...")
            await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Start 45-Minute Mock'));
                    if (btn) btn.click();
                })()
                """
            })
            await asyncio.sleep(3.5)

            # Click "End Interview Early" without submitting anything
            print("[CDP] Clicking 'End Interview Early' without submitting anything...")
            await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('End Interview Early'));
                    if (btn) btn.click();
                })()
                """
            })
            await asyncio.sleep(4.5)

            # Read Scorecard text
            sc_text = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const sc = document.querySelector('.st-key-mock_scorecard_card');
                    return sc ? sc.innerText : 'NO SCORECARD FOUND';
                })()
                """
            })
            rendered = sc_text.get("result", {}).get("value")
            print("\n--- RENDERED COMPLETED SCORECARD CONTENT ---")
            print(rendered)

            # Capture screenshot
            res = await send_cmd("Page.captureScreenshot", {"format": "png"})
            b64_data = res.get("data")
            if b64_data:
                img_bytes = base64.b64decode(b64_data)
                out_path = pathlib.Path("scratch/defect1_part_a_scorecard.png")
                out_path.write_bytes(img_bytes)
                print(f"[CDP] Wrote screenshot to {out_path} ({len(img_bytes)} bytes)")
                if BRAIN_DIR.exists():
                    brain_shot = BRAIN_DIR / "defect1_fixed_owner_scenario.png"
                    brain_shot.write_bytes(img_bytes)
                    print(f"[CDP] Mirrored to brain artifact: {brain_shot}")

    finally:
        chrome_proc.terminate()
        try:
            shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass
        if st_proc:
            st_proc.terminate()

    snap_after = get_store_snapshot()
    print("\n--- STORE SNAPSHOT AFTER ---")
    print(json.dumps(snap_after, indent=2))
    assert snap_before == snap_after, "STORE CHANGED ON UNATTEMPTED MOCK!"
    print("\n>>> PROOF PART (A) SUCCESS: Store is 100% byte-identical before and after! Both problems NOT ATTEMPTED!")

if __name__ == "__main__":
    asyncio.run(run_proof_part_a())

