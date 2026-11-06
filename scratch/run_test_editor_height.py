r"""
scratch/run_test_editor_height.py
"""
import asyncio, base64, json, pathlib, subprocess, tempfile, time, urllib.request, websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8505
CDP_PORT = 9245

def run():
    # Start streamlit on 8505
    st_proc = subprocess.Popen([
        str(WORKSPACE_ROOT / ".venv" / "Scripts" / "streamlit.exe"),
        "run",
        "scratch/test_editor_height.py",
        "--server.headless", "true",
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", "127.0.0.1",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for _ in range(30):
        time.sleep(0.3)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health", timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            pass

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_h_")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1920,1080",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    async def check():
        ws_url = None
        for _ in range(30):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list") as r:
                    tabs = json.loads(r.read().decode())
                    pages = [t for t in tabs if t.get("type") == "page"]
                    if pages:
                        ws_url = pages[0]["webSocketDebuggerUrl"]
                        break
            except Exception:
                pass
        
        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            async def send(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    res = json.loads(raw)
                    if res.get("id") == cid:
                        return res.get("result", {})

            for var in ["int", "string", "tuple"]:
                await send("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?variant={var}"})
                await asyncio.sleep(3.0)

                eval_res = await send("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const iframe = document.querySelector('iframe');
                        if (!iframe) return { error: 'no iframe' };
                        const r = iframe.getBoundingClientRect();
                        return {
                            variant: '""" + var + """',
                            iframeWidth: r.width,
                            iframeHeight: r.height,
                            styleHeight: iframe.style.height,
                            computedHeight: window.getComputedStyle(iframe).height,
                        };
                    })()
                    """,
                    "returnByValue": True
                })
                print("RESULT FOR VARIANT", var, ":", eval_res.get("result", {}).get("value"))

                # Capture screenshot
                shot = await send("Page.captureScreenshot", {"format": "png"})
                b64 = shot.get("data")
                if b64:
                    pathlib.Path(f"scratch/test_{var}.png").write_bytes(base64.b64decode(b64))
                    print(f"Saved scratch/test_{var}.png")

    try:
        asyncio.run(check())
    finally:
        chrome_proc.terminate()
        st_proc.terminate()

if __name__ == "__main__":
    run()

