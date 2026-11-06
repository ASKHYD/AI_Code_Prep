import asyncio
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.request
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9298

async def main():
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_v2_")
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
            raise RuntimeError("Could not connect to Chrome CDP")

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
            await send("DOM.enable")

            # Test problem binary-search
            url = "http://127.0.0.1:8501/?screen=practice&problem=binary-search"
            await send("Page.navigate", {"url": url})
            await asyncio.sleep(3.0)

            # Check statement sig vs editor line 1
            js = """
            (() => {
                const sigPre = document.querySelector('.signature-pre');
                const sigText = sigPre ? sigPre.textContent.trim() : null;

                let editorLine1 = null;
                const iframe = document.querySelector('iframe[title="code_editor.code_editor"]');
                if (iframe && iframe.contentDocument) {
                    const aceEl = iframe.contentDocument.querySelector('.ace_editor');
                    if (aceEl && iframe.contentWindow && iframe.contentWindow.ace) {
                        try {
                            const ed = iframe.contentWindow.ace.edit(aceEl);
                            editorLine1 = ed.getSession().getLine(0).trim();
                        } catch(e) {}
                    }
                    if (!editorLine1) {
                        const lineEl = iframe.contentDocument.querySelector('.ace_line');
                        if (lineEl) editorLine1 = lineEl.textContent.trim();
                    }
                }

                // Check headings in problem card
                const card = document.querySelector('.st-key-practice_problem_card');
                const headings = card ? Array.from(card.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim()
                })) : [];

                return {
                    sigText,
                    editorLine1,
                    match: (sigText === editorLine1),
                    headings
                };
            })()
            """
            res = await send("Runtime.evaluate", {"expression": js, "returnByValue": True})
            print(json.dumps(res.get("result", {}).get("value", {}), indent=2))

    finally:
        chrome_proc.terminate()

asyncio.run(main())

