r"""
scratch/capture_practice_1920.py
"""

import asyncio
import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import urllib.request
import websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9240

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

async def run():
    st_proc = start_streamlit()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_p1920_")
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

            # Navigate to practice arena with demo_fail
            await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice&demo_fail=true"})

            # Wait for iframe to mount
            print("[CDP] Waiting for Ace editor iframe...", flush=True)
            for _ in range(25):
                await asyncio.sleep(0.4)
                chk = await send_cmd("Runtime.evaluate", {
                    "expression": "!!document.querySelector('.st-key-practice_editor_card iframe') || !!document.querySelector('.st-key-practice_editor_card textarea')"
                })
                if chk.get("result", {}).get("value") is True:
                    print("[CDP] Editor element detected in DOM!", flush=True)
                    break

            await asyncio.sleep(2.0)

            # Query dimensions
            dim_eval = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const iframe = document.querySelector('.st-key-practice_editor_card iframe');
                    const textarea = document.querySelector('.st-key-practice_editor_card textarea');
                    const card = document.querySelector('.st-key-practice_editor_card');
                    const headerStrip = document.querySelector('.editor-header-strip');
                    const sigBox = document.querySelector('.code-block-light');
                    const hintBtns = Array.from(document.querySelectorAll('.st-key-practice_hint_card button'));

                    const result = {};
                    if (iframe) {
                        const cs = window.getComputedStyle(iframe);
                        const r = iframe.getBoundingClientRect();
                        result.iframe = {
                            computedHeight: cs.height,
                            computedMinHeight: cs.minHeight,
                            rectHeight: r.height,
                            rectWidth: r.width,
                        };
                    }
                    if (textarea) {
                        const cs = window.getComputedStyle(textarea);
                        const r = textarea.getBoundingClientRect();
                        result.textarea = {
                            computedHeight: cs.height,
                            computedMinHeight: cs.minHeight,
                            rectHeight: r.height,
                            rectWidth: r.width,
                        };
                    }
                    if (card) {
                        const r = card.getBoundingClientRect();
                        result.card = { rectHeight: r.height, rectWidth: r.width };
                    }
                    if (headerStrip) {
                        const cs = window.getComputedStyle(headerStrip);
                        result.headerStrip = {
                            whiteSpace: cs.whiteSpace,
                            display: cs.display,
                            backgroundColor: cs.backgroundColor
                        };
                    }
                    if (sigBox) {
                        const cs = window.getComputedStyle(sigBox);
                        result.sigBox = {
                            whiteSpace: cs.whiteSpace,
                            overflowX: cs.overflowX
                        };
                    }
                    result.hintButtonCount = hintBtns.length;
                    result.hintButtonFullWidth = hintBtns.map(b => window.getComputedStyle(b).width);
                    return result;
                })()
                """,
                "returnByValue": True,
            })
            dims = dim_eval.get("result", {}).get("value", {})
            print(f"[CDP 1920x1080] Live Practice Arena Measurements:\n{json.dumps(dims, indent=2)}", flush=True)

            layout_eval = await send_cmd("Page.getLayoutMetrics")
            content_size = layout_eval.get("cssContentSize", {})
            doc_height = int(content_size.get("height", 1080))
            print(f"[CDP 1920x1080] Document full height = {doc_height}px", flush=True)

            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": max(1080, doc_height),
                "deviceScaleFactor": 1,
                "mobile": False,
            })
            await asyncio.sleep(0.5)

            res = await send_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
            b64 = res.get("data")
            if b64:
                img_bytes = base64.b64decode(b64)
                out_path = DOCS_DIR / "practice_real_1920x1080.png"
                out_path.write_bytes(img_bytes)
                print(f"[CDP] Wrote {out_path} ({len(img_bytes)} bytes)", flush=True)
                brain_path = BRAIN_DIR / "practice_real_1920x1080.png"
                brain_path.write_bytes(img_bytes)
                print(f"[CDP] Mirrored to {brain_path}", flush=True)

    finally:
        chrome_proc.terminate()
        try:
            shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass
        if st_proc:
            st_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())

