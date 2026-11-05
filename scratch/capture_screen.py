"""
scratch/capture_screen.py

Captures real application screenshots of the Streamlit app at:
  - 1920x1080 -> docs/screenshots/r3/{screen}_real_1920x1080.png
  - 1600x1000 -> docs/screenshots/r3/{screen}_real_1600x1000.png

Uses Chrome DevTools Protocol over WebSockets and headless Chrome.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(
    r"C:\Users\MS Computer\.gemini\antigravity\brain\2a609fd9-9a02-4521-a182-3a1389f8099d\screenshots\r3"
)
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9226


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


async def capture_screenshots(screen: str = "practice"):
    st_proc = start_streamlit()
    profile_dir = tempfile.mkdtemp(prefix=f"chrome_cdp_{screen}_")

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
        # Connect to Chrome CDP
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

            # Determine target URL and output names based on screen
            if screen == "practice":
                target_url = f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice&problem=longest-substring&demo_fail=true"
                targets = [
                    ("practice_real_1920x1080.png", 1920, 1080),
                    ("practice_real_1600x1000.png", 1600, 1000),
                ]
            elif screen == "home":
                target_url = f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=home"
                targets = [
                    ("home_real_1920x1080.png", 1920, 1080),
                    ("home_real_1600x1000.png", 1600, 1000),
                ]
            else:
                target_url = f"http://127.0.0.1:{STREAMLIT_PORT}/?screen={screen}"
                targets = [
                    (f"{screen}_real_1920x1080.png", 1920, 1080),
                    (f"{screen}_real_1600x1000.png", 1600, 1000),
                ]

            print(f"[CDP] Navigating to {target_url}...", flush=True)
            await send_cmd("Page.navigate", {"url": target_url})

            # Wait for Streamlit to render components and execution to complete
            print("[CDP] Waiting for Streamlit page elements to settle...", flush=True)
            await asyncio.sleep(6.0)

            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            if BRAIN_DIR.parent.exists():
                BRAIN_DIR.mkdir(parents=True, exist_ok=True)

            for filename, width, height in targets:
                print(f"[CDP] Setting viewport to {width}x{height}...", flush=True)
                await send_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": width,
                        "height": height,
                        "deviceScaleFactor": 1,
                        "mobile": False,
                    },
                )
                await asyncio.sleep(1.5)

                print(f"[CDP] Capturing screenshot: {filename}...", flush=True)
                res = await send_cmd("Page.captureScreenshot", {"format": "png"})
                b64_data = res.get("data")
                if not b64_data:
                    raise RuntimeError(f"Failed to capture screenshot for {filename}")

                img_bytes = base64.b64decode(b64_data)
                out_path = DOCS_DIR / filename
                out_path.write_bytes(img_bytes)
                print(f"[CDP] Successfully wrote {out_path} ({len(img_bytes)} bytes)", flush=True)

                if BRAIN_DIR.exists():
                    brain_file = BRAIN_DIR / filename
                    brain_file.write_bytes(img_bytes)
                    print(f"[CDP] Mirrored to {brain_file}", flush=True)

    finally:
        try:
            chrome_proc.terminate()
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)

        if st_proc:
            print("[Streamlit] Shutting down spawned Streamlit process...", flush=True)
            try:
                st_proc.terminate()
                st_proc.wait(timeout=3)
            except Exception:
                st_proc.kill()


def main():
    parser = argparse.ArgumentParser(description="Capture Streamlit screen screenshots.")
    parser.add_argument("--screen", default="practice", help="Screen to capture (default: practice)")
    args = parser.parse_args()

    print(f"Capturing Direction A {args.screen} real app screenshots...", flush=True)
    asyncio.run(capture_screenshots(screen=args.screen))
    print("Capture complete!", flush=True)


if __name__ == "__main__":
    main()
