r"""
scratch/capture_terracotta_mockups.py

Captures static HTML mockups in mockups/terracotta/ across 2 resolutions:
- 1450x900 (PRIMARY OWNER VIEWPORT)
- 1920x1080 (Secondary)

Pages:
- home.html
- practice.html
- mock_start.html
- mock_session.html
- mock_scorecard.html
- dashboard.html
- tokens.html

Outputs to docs/screenshots/terracotta/ and mirrors 1450x900 captures to brain directory.
"""
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
MOCKUP_DIR = WORKSPACE_ROOT / "mockups" / "terracotta"
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "terracotta"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9278

RESOLUTIONS = [
    (1450, 900),   # PRIMARY
    (1920, 1080),  # Secondary
]

PAGES = [
    ("login.html", "terracotta_login"),
    ("home.html", "terracotta_home"),
    ("practice.html", "terracotta_practice"),
    ("mock_start.html", "terracotta_mock_start"),
    ("mock_session.html", "terracotta_mock_session"),
    ("mock_scorecard.html", "terracotta_mock_scorecard"),
    ("dashboard.html", "terracotta_dashboard"),
    ("tokens.html", "terracotta_tokens"),
]

async def run():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_terracotta_")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1450,900",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    manifest = []

    try:
        ws_url = None
        for _ in range(40):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list", timeout=1) as resp:
                    tabs = json.loads(resp.read().decode())
                    pages = [t for t in tabs if t.get("type") == "page"]
                    if pages:
                        ws_url = pages[0].get("webSocketDebuggerUrl")
                        if ws_url:
                            break
            except Exception:
                pass
        
        if not ws_url:
            raise RuntimeError(f"Could not connect to Chrome CDP port {CDP_PORT}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1
            async def send(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == cid:
                        return data.get("result", {})

            await send("Page.enable")
            await send("Runtime.enable")
            await send("DOM.enable")

            async def capture_png(full_page=False):
                params = {"format": "png"}
                if full_page:
                    params["captureBeyondViewport"] = True
                res = await send("Page.captureScreenshot", params)
                return base64.b64decode(res.get("data", ""))

            for html_file, slug in PAGES:
                file_url = (MOCKUP_DIR / html_file).as_uri()
                print(f"Loading {file_url}...")

                for width, height in RESOLUTIONS:
                    await send("Emulation.setDeviceMetricsOverride", {
                        "width": width,
                        "height": height,
                        "deviceScaleFactor": 1,
                        "mobile": False,
                    })

                    await send("Page.navigate", {"url": file_url})
                    await send("Page.loadEventFired")
                    await asyncio.sleep(0.5)

                    # Viewport screenshot
                    png_data = await capture_png(full_page=False)
                    filename = f"{slug}_{width}x{height}.png"
                    out_path = DOCS_DIR / filename
                    with open(out_path, "wb") as f:
                        f.write(png_data)
                    
                    size_bytes = len(png_data)
                    print(f"Captured {filename}: {size_bytes:,} bytes")
                    manifest.append({
                        "file": filename,
                        "width": width,
                        "height": height,
                        "bytes": size_bytes,
                        "page": html_file
                    })

                    # Mirror primary 1450x900 to brain
                    if width == 1450:
                        brain_path = BRAIN_DIR / filename
                        shutil.copyfile(out_path, brain_path)

        with open(DOCS_DIR / "capture_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Saved manifest with {len(manifest)} captures.")

    finally:
        chrome_proc.terminate()
        chrome_proc.wait()
        try:
            shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(run())

