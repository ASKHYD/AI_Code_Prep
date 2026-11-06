import asyncio
import base64
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.request
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9311
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_IMAGE = WORKSPACE_ROOT / "docs" / "screenshots" / "m2_p3_home_1450x900.png"

async def main():
    OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    profile_dir = tempfile.mkdtemp(prefix="chrome_m2_p3_")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1450,900",
        "--force-device-scale-factor=1",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(2.0)
        with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list") as resp:
            tabs = json.loads(resp.read().decode())
            ws_url = [t for t in tabs if t.get("type") == "page"][0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                curr_id = msg_id
                await ws.send(json.dumps({"id": curr_id, "method": method, "params": params or {}}))
                while True:
                    data = json.loads(await ws.recv())
                    if data.get("id") == curr_id:
                        return data.get("result", {})

            await send("Page.enable")
            await send("DOM.enable")
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1450,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False,
            })

            # Navigate to Home screen
            nav_result = await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=home"})
            print("Navigated to Home:", nav_result)

            # Wait for Streamlit rendering to settle
            await asyncio.sleep(4.0)

            # Measure live DOM elements
            eval_copy = await send("Runtime.evaluate", {
                "expression": "document.body.innerText.includes('Adaptive spaced repetition (FSRS)')"
            })
            print("FSRS Truth-in-Copy verified in DOM:", eval_copy.get("result", {}).get("value"))

            eval_due_chip = await send("Runtime.evaluate", {
                "expression": "document.querySelector('.status-chip-due') ? document.querySelector('.status-chip-due').innerText : 'NOT FOUND'"
            })
            print("Due chip text:", eval_due_chip.get("result", {}).get("value"))

            # Capture screenshot
            ss = await send("Page.captureScreenshot", {"format": "png"})
            png_bytes = base64.b64decode(ss["data"])
            with open(OUTPUT_IMAGE, "wb") as f:
                f.write(png_bytes)
            print(f"Captured 1450x900 Home screenshot to: {OUTPUT_IMAGE} ({len(png_bytes)} bytes)")

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
