r"""
scratch/inspect_iframe_ace.py
"""
import asyncio, json, urllib.request, websockets

async def inspect():
    with urllib.request.urlopen("http://127.0.0.1:9246/json/list") as r:
        tabs = json.loads(r.read().decode())
    
    print("ALL TARGETS:")
    for t in tabs:
        print(f"  type={t.get('type')}, url={t.get('url')[:60]}")

    # Connect to the page
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

        await send("Page.enable")
        await send("Runtime.enable")
        
        # Get frame tree
        tree = await send("Page.getFrameTree")
        print("Frame tree retrieved.")
        child_frames = tree.get("frameTree", {}).get("childFrames", [])
        print("Child frames count:", len(child_frames))
        for cf in child_frames:
            f = cf.get("frame", {})
            print(f"  Frame ID={f.get('id')}, url={f.get('url')[:60]}")

        # Let's inspect execution contexts
        contexts = []
        # We can enable Runtime and listen for executionContextCreated or evaluate in page
        # In modern Chrome, iframes from same origin (or components on localhost) can be accessed
        res = await send("Runtime.evaluate", {
            "expression": """
            (() => {
                const iframe = document.querySelector('iframe');
                if (!iframe) return 'no iframe';
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const lines = Array.from(doc.querySelectorAll('.ace_line'));
                    const hScroll = doc.querySelector('.ace_scrollbar-h');
                    const editor = doc.querySelector('.ace_editor');
                    return {
                        linesCount: lines.length,
                        line1Text: lines[0] ? lines[0].innerText : null,
                        line1Width: lines[0] ? lines[0].getBoundingClientRect().width : null,
                        hScrollDisplay: hScroll ? window.getComputedStyle(hScroll).display : null,
                        hScrollHeight: hScroll ? hScroll.getBoundingClientRect().height : null,
                        editorWidth: editor ? editor.getBoundingClientRect().width : null,
                        editorHeight: editor ? editor.getBoundingClientRect().height : null,
                    };
                } catch (e) {
                    return 'cross-origin: ' + e.message;
                }
            })()
            """,
            "returnByValue": True
        })
        print("IFRAME INTERNAL INSPECTION:")
        print(json.dumps(res.get("result", {}).get("value"), indent=2))

if __name__ == "__main__":
    asyncio.run(inspect())

