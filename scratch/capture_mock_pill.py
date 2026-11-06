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
CDP_PORT = 9293
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r6"

def rgb_to_hex(rgb_str):
    if not rgb_str or "rgb" not in rgb_str:
        return rgb_str
    import re
    m = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02X}{g:02X}{b:02X}"
    return rgb_str

async def main():
    profile_dir = tempfile.mkdtemp(prefix="chrome_mock_pill_")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1450,900",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        time.sleep(1.5)
        with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list") as resp:
            tabs = json.loads(resp.read().decode())
            ws_url = [t for t in tabs if t.get("type") == "page"][0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            async def send(method, params=None):
                await ws.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
                while True:
                    data = json.loads(await ws.recv())
                    if data.get("id") == 1:
                        return data.get("result", {})

            await send("Page.enable")
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1450,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            # Navigate to Mock
            await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=mock"})
            # Wait for topbar
            for _ in range(30):
                await asyncio.sleep(0.2)
                chk = await send("Runtime.evaluate", {
                    "expression": "!!document.querySelector('.topbar')",
                    "returnByValue": True
                })
                if chk.get("result", {}).get("value") is True:
                    break
            
            await asyncio.sleep(1.0)

            js = """
            (() => {
                const el = document.querySelector('.nav-pill.active-mock');
                const allPills = Array.from(document.querySelectorAll('.nav-pill')).map(p => ({
                    text: p.textContent.trim(),
                    classes: p.className,
                    bg: window.getComputedStyle(p).backgroundColor
                }));
                if (!el) return { found: false, allPills };
                const style = window.getComputedStyle(el);
                return {
                    found: true,
                    selector: '.nav-pill.active-mock',
                    text: el.textContent.trim(),
                    bgColor: style.backgroundColor,
                    color: style.color
                };
            })()
            """
            res = (await send("Runtime.evaluate", {"expression": js, "returnByValue": True})).get("result", {}).get("value", {})
            if res.get("found"):
                res["bgHex"] = rgb_to_hex(res.get("bgColor"))
                res["colorHex"] = rgb_to_hex(res.get("color"))
            print(json.dumps(res, indent=2))

            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "nav_active_mock_1450x900.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # Update results json
            out_file = DOCS_DIR / "addendum_v2_results.json"
            if out_file.exists():
                curr = json.loads(out_file.read_text(encoding="utf-8"))
                curr["v2_mock_pill"] = res
                out_file.write_text(json.dumps(curr, indent=2), encoding="utf-8")

    finally:
        chrome_proc.terminate()

asyncio.run(main())

