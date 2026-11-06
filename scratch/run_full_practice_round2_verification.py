r"""
scratch/run_full_practice_round2_verification.py

Executes full automated CDP verification and screenshot capture for Corrective Round 2:
- P1 Editor Height (CDP rect of iframe, check >= 440px)
- P2 Longest Signature (log-timestamp-filter 79 chars on 1 line, wrap:false, no h-scroll)
- P3 Recomposed Layout (Left: filter+statement; Right: editor+verdict+tests+hint, balance <=20%, no doc overflow)
- P4 Broken Signature Box (broken after commas, scrollWidth <= clientWidth)
- P5 Single-line Test Case Headings (TEST CASE #n)
- Font checks (Fraunces, Inter, JetBrains Mono)
- Viewports, fullpage tall, statement closeups, longest signature editor closeups
- Dual-resolution side-by-side comparisons with mockups/practice.html
- Artifact mirroring
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
from PIL import Image

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9260

def is_server_running(url):
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def ensure_streamlit():
    if is_server_running(f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"):
        print(f"[Streamlit] Already healthy on port {STREAMLIT_PORT}")
        return None
    print(f"[Streamlit] Starting on port {STREAMLIT_PORT}...")
    proc = subprocess.Popen([
        str(WORKSPACE_ROOT / ".venv" / "Scripts" / "streamlit.exe"),
        "run",
        "app.py",
        "--server.headless", "true",
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", "127.0.0.1",
    ], cwd=str(WORKSPACE_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        time.sleep(0.5)
        if is_server_running(f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"):
            print(f"[Streamlit] Up and running on port {STREAMLIT_PORT}")
            return proc
    raise RuntimeError("Failed to start Streamlit server")

def create_side_by_side(real_path, mockup_path, out_path):
    img_real = Image.open(real_path)
    img_mockup = Image.open(mockup_path)
    
    target_height = max(img_real.height, img_mockup.height)
    header_height = 50
    comb_width = img_mockup.width + img_real.width + 20
    comb_height = target_height + header_height
    
    combined = Image.new("RGB", (comb_width, comb_height), (245, 243, 238))
    combined.paste(img_mockup, (0, header_height))
    combined.paste(img_real, (img_mockup.width + 20, header_height))
    combined.save(out_path)
    print(f"[Comparison] Created {out_path}")

async def run_verification():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    
    st_proc = ensure_streamlit()
    
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_r2_")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1920,1080",
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

            async def eval_js(expr):
                r = await send("Runtime.evaluate", {
                    "expression": expr,
                    "returnByValue": True,
                    "awaitPromise": True
                })
                return r.get("result", {}).get("value")

            async def wait_for_editor():
                for _ in range(40):
                    ready = await eval_js("""
                        (() => {
                            const iframes = Array.from(document.querySelectorAll('.st-key-practice_editor_card iframe'));
                            if (!iframes.length) return false;
                            const rect = iframes[0].getBoundingClientRect();
                            return rect.height > 100 && rect.width > 200;
                        })()
                    """)
                    if ready:
                        await asyncio.sleep(1.0)
                        return True
                    await asyncio.sleep(0.3)
                return False

            async def capture_png(clip=None, full_page=False):
                params = {"format": "png"}
                if clip:
                    params["clip"] = clip
                if full_page:
                    params["captureBeyondViewport"] = True
                res = await send("Page.captureScreenshot", params)
                return base64.b64decode(res.get("data", ""))

            def save_screenshot(img_bytes, filename):
                doc_path = DOCS_DIR / filename
                doc_path.write_bytes(img_bytes)
                brain_path = BRAIN_DIR / filename
                brain_path.write_bytes(img_bytes)
                print(f"[Screenshot] Saved {filename} ({len(img_bytes)} bytes)")

            all_results = {}

            for width, height in [(1920, 1080), (1600, 1000)]:
                res_str = f"{width}x{height}"
                print(f"\n=======================================================")
                print(f"  TESTING RESOLUTION {res_str}")
                print(f"=======================================================")
                
                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False
                })

                # 1. Load Practice Default Page
                await send("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice"})
                await wait_for_editor()
                await asyncio.sleep(1.5)

                # Capture viewport
                vp_bytes = await capture_png(full_page=False)
                save_screenshot(vp_bytes, f"practice_viewport_{res_str}.png")

                # Capture full page
                fp_bytes = await capture_png(full_page=True)
                save_screenshot(fp_bytes, f"practice_fullpage_{res_str}.png")

                # Measure P1: Editor iframe element
                p1 = await eval_js("""
                    (() => {
                        const iframe = document.querySelector('.st-key-practice_editor_card iframe');
                        if (!iframe) return { error: "iframe not found" };
                        const r = iframe.getBoundingClientRect();
                        const cs = window.getComputedStyle(iframe);
                        return {
                            selector: ".st-key-practice_editor_card iframe",
                            elementDescription: "HTMLIFrameElement rendered by streamlit-code-editor component",
                            renderedWidth: Math.round(r.width),
                            renderedHeight: Math.round(r.height),
                            top: Math.round(r.top),
                            bottom: Math.round(r.bottom),
                            computedHeight: cs.height,
                            isGte440: r.height >= 440
                        };
                    })()
                """)
                print(f"P1 Measurement ({res_str}): {json.dumps(p1, indent=2)}")

                # Measure P3: Two-column balance & scrollWidth
                p3 = await eval_js("""
                    (() => {
                        const leftCard = document.querySelector('.st-key-practice_statement_card');
                        const rightCard = document.querySelector('.st-key-practice_hint_card');
                        const doc = document.documentElement;

                        const leftBottom = leftCard ? Math.round(leftCard.getBoundingClientRect().bottom) : null;
                        const rightBottom = rightCard ? Math.round(rightCard.getBoundingClientRect().bottom) : null;
                        
                        let diffPct = null;
                        let diffPx = null;
                        if (leftBottom && rightBottom) {
                            diffPx = Math.abs(leftBottom - rightBottom);
                            const maxBottom = Math.max(leftBottom, rightBottom);
                            diffPct = Number(((diffPx / maxBottom) * 100).toFixed(1));
                        }

                        return {
                            leftCardBottom: leftBottom,
                            rightCardBottom: rightBottom,
                            diffPx: diffPx,
                            diffPct: diffPct,
                            isWithin20Pct: diffPct !== null ? diffPct <= 20.0 : false,
                            scrollWidth: doc.scrollWidth,
                            clientWidth: doc.clientWidth,
                            noHorizontalOverflow: doc.scrollWidth <= doc.clientWidth + 1
                        };
                    })()
                """)
                print(f"P3 Measurement ({res_str}): {json.dumps(p3, indent=2)}")

                # Measure P4: Signature Box
                p4 = await eval_js("""
                    (() => {
                        const box = document.querySelector('.signature-display-box');
                        if (!box) return { error: "No signature-display-box" };
                        const rect = box.getBoundingClientRect();
                        return {
                            selector: ".signature-display-box pre",
                            elementDescription: "HTMLPreElement displaying broken function signature",
                            scrollWidth: box.scrollWidth,
                            clientWidth: box.clientWidth,
                            noHorizontalScrollbar: box.scrollWidth <= box.clientWidth,
                            lines: box.innerText.trim().split('\\n')
                        };
                    })()
                """)
                print(f"P4 Measurement ({res_str}): {json.dumps(p4, indent=2)}")

                # Statement close-up screenshot
                stmt_clip = await eval_js("""
                    (() => {
                        const el = document.querySelector('.st-key-practice_statement_card');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left, y: r.top, width: r.width, height: r.height, scale: 1 };
                    })()
                """)
                if stmt_clip:
                    stmt_bytes = await capture_png(clip=stmt_clip)
                    save_screenshot(stmt_bytes, f"practice_statement_closeup_{res_str}.png")

                # Measure P5: Test case headers
                p5 = await eval_js("""
                    (() => {
                        const headings = Array.from(document.querySelectorAll('.test-case-card-title'));
                        return headings.map((h, i) => {
                            const r = h.getBoundingClientRect();
                            return {
                                index: i + 1,
                                text: h.innerText.trim(),
                                whiteSpace: window.getComputedStyle(h).whiteSpace,
                                heightPx: Math.round(r.height),
                                isSingleLine: r.height < 30
                            };
                        });
                    })()
                """)
                print(f"P5 Measurement ({res_str}): {json.dumps(p5, indent=2)}")

                # Measure Computed Fonts
                fonts = await eval_js("""
                    (() => {
                        const h = document.querySelector('.st-key-practice_filter_card h3, .st-key-practice_statement_card h3, h1');
                        const body = document.querySelector('.st-key-practice_statement_card p, body');
                        const code = document.querySelector('.signature-display-box, pre, code');
                        return {
                            headingFamily: h ? window.getComputedStyle(h).fontFamily : null,
                            bodyFamily: body ? window.getComputedStyle(body).fontFamily : null,
                            codeFamily: code ? window.getComputedStyle(code).fontFamily : null
                        };
                    })()
                """)
                print(f"Fonts ({res_str}): {json.dumps(fonts, indent=2)}")

                # 2. Load Longest Problem: log-timestamp-filter
                print(f"\n--- Testing P2 on log-timestamp-filter ({res_str}) ---")
                await send("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice&problem=log-timestamp-filter"})
                await wait_for_editor()
                await asyncio.sleep(2.0)

                # Capture editor close-up
                editor_clip = await eval_js("""
                    (() => {
                        const el = document.querySelector('.st-key-practice_editor_card');
                        if (!el) return null;
                        const r = el.getBoundingClientRect();
                        return { x: r.left, y: r.top, width: r.width, height: r.height, scale: 1 };
                    })()
                """)
                if editor_clip:
                    ed_bytes = await capture_png(clip=editor_clip)
                    save_screenshot(ed_bytes, f"practice_longest_signature_{res_str}.png")

                # Measure P2 inside Ace iframe
                p2 = await eval_js("""
                    (() => {
                        const iframe = document.querySelector('.st-key-practice_editor_card iframe');
                        if (!iframe) return { error: "No editor iframe" };
                        const r = iframe.getBoundingClientRect();
                        let inner = {};
                        try {
                            const doc = iframe.contentDocument || iframe.contentWindow.document;
                            const line1 = doc.querySelector('.ace_line');
                            const hScroll = doc.querySelector('.ace_scrollbar-h');
                            const scroller = doc.querySelector('.ace_scroller');
                            const content = doc.querySelector('.ace_content');
                            inner = {
                                line1Text: line1 ? line1.innerText : null,
                                line1WidthPx: line1 ? Math.round(line1.getBoundingClientRect().width) : null,
                                hScrollDisplay: hScroll ? window.getComputedStyle(hScroll).display : null,
                                hScrollHeight: hScroll ? Math.round(hScroll.getBoundingClientRect().height) : null,
                                scrollerClientWidth: scroller ? scroller.clientWidth : null,
                                scrollerScrollWidth: scroller ? scroller.scrollWidth : null,
                                contentWidth: content ? content.clientWidth : null,
                                hasHorizontalOverflow: scroller ? (scroller.scrollWidth > scroller.clientWidth + 1) : false,
                                isHScrollHidden: hScroll ? (window.getComputedStyle(hScroll).display === 'none' || hScroll.clientHeight === 0) : true
                            };
                        } catch (e) {
                            inner = { error: e.message };
                        }
                        return {
                            selector: ".st-key-practice_editor_card iframe -> .ace_line",
                            elementDescription: "First line of starter code inside Ace Editor iframe",
                            iframeWidth: Math.round(r.width),
                            iframeHeight: Math.round(r.height),
                            ace: inner
                        };
                    })()
                """)
                print(f"P2 Measurement ({res_str}): {json.dumps(p2, indent=2)}")

                # 3. Load Mockup for side-by-side comparison
                mockup_file_url = f"file:///{WORKSPACE_ROOT.as_posix()}/mockups/practice.html"
                await send("Page.navigate", {"url": mockup_file_url})
                await asyncio.sleep(1.0)
                mockup_bytes = await capture_png(full_page=False)
                save_screenshot(mockup_bytes, f"practice_mockup_{res_str}.png")

                # Create side-by-side
                real_vp_file = DOCS_DIR / f"practice_viewport_{res_str}.png"
                mockup_file = DOCS_DIR / f"practice_mockup_{res_str}.png"
                comp_file = DOCS_DIR / f"practice_comparison_{res_str}.png"
                create_side_by_side(real_vp_file, mockup_file, comp_file)
                # Mirror to brain
                shutil.copy2(comp_file, BRAIN_DIR / f"practice_comparison_{res_str}.png")

                all_results[res_str] = {
                    "p1": p1,
                    "p2": p2,
                    "p3": p3,
                    "p4": p4,
                    "p5": p5,
                    "fonts": fonts
                }

            # Save full measurements JSON
            summary_path = DOCS_DIR / "practice_round2_measurements.json"
            summary_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
            shutil.copy2(summary_path, BRAIN_DIR / "practice_round2_measurements.json")
            print(f"[Done] Written all measurements to {summary_path}")

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(run_verification())

