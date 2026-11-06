import asyncio
import json
import urllib.request
import websockets

async def measure():
    # Discover Chrome debugging page
    req = urllib.request.urlopen("http://127.0.0.1:9296/json/list")
    tabs = json.loads(req.read().decode())
    page_tabs = [t for t in tabs if t.get("type") == "page"]
    if not page_tabs:
        print("No open page tabs found")
        return
    
    ws_url = page_tabs[0]["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            await ws.send(json.dumps(payload))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        # Set viewport to 1450x900
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 1450,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })

        # Navigate to practice page
        await call("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=practice"})
        await asyncio.sleep(3.0)

        # Run DOM measurements
        expr = """
        (() => {
            const docWidth = document.documentElement.clientWidth;
            const docScroll = document.documentElement.scrollWidth;
            
            // Picker buttons
            const prevBtn = document.querySelector('button[key="btn_picker_prev"]') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Prev') || b.textContent.includes('←'));
            const nextBtn = document.querySelector('button[key="btn_picker_next"]') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next') || b.textContent.includes('→'));
            
            // Editor strip
            const editorStrip = document.querySelector('.editor-strip');
            const editorStripRight = document.querySelector('.editor-strip-right');
            
            // Headings in problem card
            const problemCard = document.querySelector('.st-key-practice_problem_card');
            const headings = problemCard ? Array.from(problemCard.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({ tag: h.tagName, text: h.textContent.trim() })) : [];
            
            return {
                docWidth,
                docScroll,
                hasOverflow: docScroll > docWidth,
                prevBtn: prevBtn ? { text: prevBtn.textContent.trim(), clientWidth: prevBtn.clientWidth, scrollWidth: prevBtn.scrollWidth } : null,
                nextBtn: nextBtn ? { text: nextBtn.textContent.trim(), clientWidth: nextBtn.clientWidth, scrollWidth: nextBtn.scrollWidth } : null,
                editorStripRight: editorStripRight ? { text: editorStripRight.textContent.trim(), clientWidth: editorStripRight.clientWidth, scrollWidth: editorStripRight.scrollWidth } : null,
                headings
            };
        })()
        """
        res = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        print(json.dumps(res.get("result", {}).get("value", {}), indent=2))

asyncio.run(measure())

