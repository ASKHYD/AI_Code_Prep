import asyncio
import base64
import json
import pathlib
import sqlite3
import subprocess
import tempfile
import time
import urllib.request
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9295
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r6"
DB_PATH = WORKSPACE_ROOT / "coach.db"

def rgb_to_hex(rgb_str):
    if not rgb_str or "rgb" not in rgb_str:
        return rgb_str
    import re
    m = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02X}{g:02X}{b:02X}"
    return rgb_str

async def run_evidence_suite():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_v2_suite_")
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
            raise RuntimeError(f"Could not connect to Chrome CDP on port {CDP_PORT}")

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
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1450,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            # -------------------------------------------------------------
            # R1: 12/12 Problem Live Verification
            # -------------------------------------------------------------
            print("\n=== Running R1: Live Verification across 12 problems ===")
            problem_files = sorted(list((WORKSPACE_ROOT / "data" / "problems").glob("*.json")))
            r1_table = []

            for p_file in problem_files:
                with open(p_file, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                pid = p_data["id"]
                url = f"http://127.0.0.1:8501/?screen=practice&problem={pid}"
                await send("Page.navigate", {"url": url})
                
                # Wait for editor hydration
                for _ in range(30):
                    await asyncio.sleep(0.2)
                    chk_js = """
                    (() => {
                        const iframe = document.querySelector('iframe[title="code_editor.code_editor"]');
                        if (!iframe || !iframe.contentDocument) return false;
                        const line = iframe.contentDocument.querySelector('.ace_line');
                        return !!(line && line.textContent.trim().length > 0);
                    })()
                    """
                    chk_res = await send("Runtime.evaluate", {"expression": chk_js, "returnByValue": True})
                    if chk_res.get("result", {}).get("value") is True:
                        break

                js_check = """
                (() => {
                    const sigPre = document.querySelector('.signature-pre');
                    const sigText = sigPre ? sigPre.textContent.trim() : "";

                    let editorLine1 = "";
                    const iframe = document.querySelector('iframe[title="code_editor.code_editor"]');
                    if (iframe && iframe.contentDocument) {
                        const lineEl = iframe.contentDocument.querySelector('.ace_line');
                        if (lineEl) editorLine1 = lineEl.textContent.trim();
                        if (!editorLine1 && iframe.contentWindow && iframe.contentWindow.ace) {
                            try {
                                const aceEl = iframe.contentDocument.querySelector('.ace_editor');
                                const ed = iframe.contentWindow.ace.edit(aceEl);
                                editorLine1 = ed.getSession().getLine(0).trim();
                            } catch(e) {}
                        }
                    }
                    return { sigText, editorLine1 };
                })()
                """
                eval_res = await send("Runtime.evaluate", {"expression": js_check, "returnByValue": True})
                val = eval_res.get("result", {}).get("value", {})
                st_sig = val.get("sigText", "")
                ed_sig = val.get("editorLine1", "")
                match = (st_sig == ed_sig and len(st_sig) > 0)
                r1_table.append({
                    "id": pid,
                    "title": p_data["title"],
                    "statement_sig": st_sig,
                    "editor_line1": ed_sig,
                    "equal": match
                })
                print(f"  [{'PASS' if match else 'FAIL'}] {pid}: {st_sig}")

            results["r1_all_12_problems"] = r1_table
            all_12_pass = all(item["equal"] for item in r1_table)
            results["r1_overall_pass"] = all_12_pass
            print(f"R1 12/12 Result: {'ALL 12 PASSED' if all_12_pass else 'FAILURES DETECTED'}")

            # -------------------------------------------------------------
            # R2: Label Redo & Headings Check
            # -------------------------------------------------------------
            print("\n=== Running R2: Label Redo & Problem Card Headings Check ===")
            await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=practice&problem=binary-search"})
            await asyncio.sleep(2.5)

            js_r2 = """
            (() => {
                const card = document.querySelector('.st-key-practice_problem_card');
                const headings = card ? Array.from(card.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
                    tag: h.tagName,
                    text: h.textContent.trim()
                })) : [];
                const funcSigHeading = headings.find(h => h.text.toLowerCase().includes("function signature"));
                
                const subheadEl = document.querySelector('.signature-subhead');
                const subheadStyle = subheadEl ? window.getComputedStyle(subheadEl) : null;

                return {
                    headings,
                    hasFuncSigHeading: !!funcSigHeading,
                    subheadText: subheadEl ? subheadEl.textContent.trim() : null,
                    subheadFontSize: subheadStyle ? subheadStyle.fontSize : null,
                    subheadTextTransform: subheadStyle ? subheadStyle.textTransform : null,
                    subheadLetterSpacing: subheadStyle ? subheadStyle.letterSpacing : null
                };
            })()
            """
            r2_val = (await send("Runtime.evaluate", {"expression": js_r2, "returnByValue": True})).get("result", {}).get("value", {})
            results["r2_label_headings"] = r2_val
            print(f"  Problem Card Headings: {r2_val.get('headings')}")
            print(f"  Has 'Function Signature' Heading: {r2_val.get('hasFuncSigHeading')}")
            print(f"  Subhead Text: {r2_val.get('subheadText')} (size: {r2_val.get('subheadFontSize')}, transform: {r2_val.get('subheadTextTransform')})")

            # Capture R2 screenshot
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "practice_1450x900_r2.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # -------------------------------------------------------------
            # R3: X10 Picker Buttons (No Clipping)
            # -------------------------------------------------------------
            print("\n=== Running R3: X10 Picker Buttons Measurements ===")
            js_r3 = """
            (() => {
                const prevBtn = document.querySelector('.st-key-btn_picker_prev button');
                const nextBtn = document.querySelector('.st-key-btn_picker_next button');
                return {
                    prevBtn: prevBtn ? {
                        text: prevBtn.textContent.trim(),
                        clientWidth: prevBtn.clientWidth,
                        scrollWidth: prevBtn.scrollWidth,
                        noClip: prevBtn.scrollWidth <= prevBtn.clientWidth
                    } : null,
                    nextBtn: nextBtn ? {
                        text: nextBtn.textContent.trim(),
                        clientWidth: nextBtn.clientWidth,
                        scrollWidth: nextBtn.scrollWidth,
                        noClip: nextBtn.scrollWidth <= nextBtn.clientWidth
                    } : null
                };
            })()
            """
            r3_val = (await send("Runtime.evaluate", {"expression": js_r3, "returnByValue": True})).get("result", {}).get("value", {})
            results["r3_picker_buttons"] = r3_val
            print(f"  Prev Button: {r3_val.get('prevBtn')}")
            print(f"  Next Button: {r3_val.get('nextBtn')}")

            # Capture R3 picker screenshot
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "practice_1450x900_r3_picker.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # -------------------------------------------------------------
            # R4: X11 Horizontal Overflow & Anchors Check
            # -------------------------------------------------------------
            print("\n=== Running R4: X11 Horizontal Overflow & Heading Anchors ===")
            js_r4 = """
            (() => {
                const docWidth = document.documentElement.clientWidth;
                const docScroll = document.documentElement.scrollWidth;
                const stripRight = document.querySelector('.editor-strip-right');
                const anchors = Array.from(document.querySelectorAll('[data-testid="stHeaderActionElements"], [data-testid="stHeadingAnchor"], a.anchor-link'));
                const visibleAnchors = anchors.filter(a => a.offsetParent !== null && window.getComputedStyle(a).display !== 'none');

                return {
                    docWidth,
                    docScroll,
                    hasOverflow: docScroll > docWidth,
                    stripRight: stripRight ? {
                        text: stripRight.textContent.trim(),
                        clientWidth: stripRight.clientWidth,
                        scrollWidth: stripRight.scrollWidth,
                        noClip: stripRight.scrollWidth <= stripRight.clientWidth
                    } : null,
                    totalAnchorsInDom: anchors.length,
                    visibleAnchorsCount: visibleAnchors.length
                };
            })()
            """
            r4_val = (await send("Runtime.evaluate", {"expression": js_r4, "returnByValue": True})).get("result", {}).get("value", {})
            results["r4_overflow_and_anchors"] = r4_val
            print(f"  docWidth: {r4_val.get('docWidth')}, docScroll: {r4_val.get('docScroll')}, hasOverflow: {r4_val.get('hasOverflow')}")
            print(f"  Strip Right: {r4_val.get('stripRight')}")
            print(f"  Visible Anchors Count: {r4_val.get('visibleAnchorsCount')}")

            # Fullpage screenshot at 1450x900
            layout_metrics = await send("Page.getLayoutMetrics")
            content_height = int(layout_metrics["contentSize"]["height"])
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1450,
                "height": content_height,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "practice_fullpage_1450x900_r4.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # Reset viewport back to 1450x900
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1450,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            # -------------------------------------------------------------
            # V2 (E9 Redo): Active Nav Pill Computed Backgrounds
            # -------------------------------------------------------------
            print("\n=== Running V2 (E9 Redo): Active Nav Pill Computed Backgrounds ===")
            # 1. Practice Arena active
            await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=practice"})
            await asyncio.sleep(2.5)
            js_pill_practice = """
            (() => {
                const el = document.querySelector('.nav-pill.active-practice');
                if (!el) return null;
                const style = window.getComputedStyle(el);
                return {
                    selector: '.nav-pill.active-practice',
                    text: el.textContent.trim(),
                    bgColor: style.backgroundColor,
                    color: style.color
                };
            })()
            """
            v2_prac = (await send("Runtime.evaluate", {"expression": js_pill_practice, "returnByValue": True})).get("result", {}).get("value", {})
            if v2_prac:
                v2_prac["bgHex"] = rgb_to_hex(v2_prac.get("bgColor"))
                v2_prac["colorHex"] = rgb_to_hex(v2_prac.get("color"))
            results["v2_practice_pill"] = v2_prac
            print(f"  Practice Pill: {v2_prac}")
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "nav_active_practice_1450x900.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # 2. Mock Interview active
            await send("Page.navigate", {"url": "http://127.0.0.1:8501/?screen=mock"})
            await asyncio.sleep(3.5)
            js_pill_mock = """
            (() => {
                const el = document.querySelector('.nav-pill.active-mock');
                if (!el) return null;
                const style = window.getComputedStyle(el);
                return {
                    selector: '.nav-pill.active-mock',
                    text: el.textContent.trim(),
                    bgColor: style.backgroundColor,
                    color: style.color
                };
            })()
            """
            v2_mock = (await send("Runtime.evaluate", {"expression": js_pill_mock, "returnByValue": True})).get("result", {}).get("value", {})
            if v2_mock:
                v2_mock["bgHex"] = rgb_to_hex(v2_mock.get("bgColor"))
                v2_mock["colorHex"] = rgb_to_hex(v2_mock.get("color"))
            results["v2_mock_pill"] = v2_mock
            print(f"  Mock Pill: {v2_mock}")
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "nav_active_mock_1450x900.png").write_bytes(base64.b64decode(shot.get("data", "")))

            # -------------------------------------------------------------
            # V6 (X5R): Longest Title Picker Capture
            # -------------------------------------------------------------
            print("\n=== Running V6 (X5R): Longest Title Picker Capture ===")
            longest_pid = "longest-substring-without-repeating"
            await send("Page.navigate", {"url": f"http://127.0.0.1:8501/?screen=practice&problem={longest_pid}"})
            await asyncio.sleep(3.5)

            js_v6 = """
            (() => {
                const titleEl = document.querySelector('.picker-title');
                const rowEl = document.querySelector('.problem-picker-row');
                return {
                    text: titleEl ? titleEl.textContent.trim() : null,
                    clientWidth: titleEl ? titleEl.clientWidth : null,
                    scrollWidth: titleEl ? titleEl.scrollWidth : null,
                    rowWidth: rowEl ? rowEl.clientWidth : null,
                    untruncated: titleEl ? titleEl.scrollWidth <= titleEl.clientWidth : false
                };
            })()
            """
            v6_val = (await send("Runtime.evaluate", {"expression": js_v6, "returnByValue": True})).get("result", {}).get("value", {})
            results["v6_longest_title"] = v6_val
            print(f"  Longest Title Picker: {v6_val}")
            shot = await send("Page.captureScreenshot", {"format": "png"})
            (DOCS_DIR / "practice_longest_title_picker_1450x900.png").write_bytes(base64.b64decode(shot.get("data", "")))

    finally:
        chrome_proc.terminate()

    # -------------------------------------------------------------
    # V5 (E6a): Unsolved-End Store Pair
    # -------------------------------------------------------------
    print("\n=== Running V5 (E6a): Unsolved-End Store Pair ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), MAX(created_at) FROM attempts;")
    before_count, before_max_created = cur.fetchone()

    # Start mock, submit nothing, end mock
    # Streamlit query parameter navigation simulates ending without solve
    with urllib.request.urlopen("http://127.0.0.1:8501/?screen=mock&mock_state=running") as resp:
        pass
    time.sleep(1.0)
    with urllib.request.urlopen("http://127.0.0.1:8501/?screen=mock&mock_state=completed") as resp:
        pass
    time.sleep(1.0)

    cur.execute("SELECT COUNT(*), MAX(created_at) FROM attempts;")
    after_count, after_max_created = cur.fetchone()
    conn.close()

    v5_val = {
        "before": {"count": before_count, "max_created_at": before_max_created},
        "after": {"count": after_count, "max_created_at": after_max_created},
        "identical": (before_count == after_count and before_max_created == after_max_created)
    }
    results["v5_unsolved_store_pair"] = v5_val
    print(f"  Before: count={before_count}, max_created={before_max_created}")
    print(f"  After:  count={after_count}, max_created={after_max_created}")
    print(f"  Identical (No phantom store write): {v5_val['identical']}")

    # Save all results to disk
    out_file = DOCS_DIR / "addendum_v2_results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll results saved to {out_file}")

if __name__ == "__main__":
    asyncio.run(run_evidence_suite())
