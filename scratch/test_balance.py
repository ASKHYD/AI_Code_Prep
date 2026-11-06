r"""
scratch/test_balance.py
"""
import asyncio, json, urllib.request, websockets

async def check():
    with urllib.request.urlopen("http://127.0.0.1:9250/json/list") as r:
        tabs = json.loads(r.read().decode())
    page_tab = [t for t in tabs if t.get("type") == "page"][0]
    async with websockets.connect(page_tab["webSocketDebuggerUrl"]) as ws:
        msg_id = 1
        async def send(method, params=None):
            nonlocal msg_id
            cid = msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == cid:
                    return res.get("result", {})

        await send("Emulation.setDeviceMetricsOverride", {
            "width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False
        })
        # Standard default practice page
        await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=practice"})
        await asyncio.sleep(4.0)

        eval_res = await send("Runtime.evaluate", {
            "expression": """
            (() => {
                const leftColLast = document.querySelector('.st-key-practice_statement_card');
                const rightColLast = document.querySelector('.st-key-practice_hint_card');
                const doc = document.documentElement;

                const leftBottom = leftColLast ? leftColLast.getBoundingClientRect().bottom : null;
                const rightBottom = rightColLast ? rightColLast.getBoundingClientRect().bottom : null;
                const diffPx = (leftBottom && rightBottom) ? Math.abs(leftBottom - rightBottom) : null;
                const maxBottom = Math.max(leftBottom || 0, rightBottom || 0);
                const pctDiff = maxBottom > 0 ? (diffPx / maxBottom) * 100 : null;

                const iframe = document.querySelector('.st-key-practice_editor_card iframe');

                return {
                    leftBottom,
                    rightBottom,
                    diffPx,
                    pctDiff: pctDiff ? pctDiff.toFixed(2) + '%' : null,
                    within20: pctDiff <= 20.0,
                    scrollWidth: doc.scrollWidth,
                    clientWidth: doc.clientWidth,
                    hasOverflow: doc.scrollWidth > doc.clientWidth,
                    iframeRect: iframe ? iframe.getBoundingClientRect() : null
                };
            })()
            """,
            "returnByValue": True
        })
        print(json.dumps(eval_res.get("result", {}).get("value"), indent=2))

if __name__ == "__main__":
    asyncio.run(check())

