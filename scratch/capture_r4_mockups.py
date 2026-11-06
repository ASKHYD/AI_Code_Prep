r"""
scratch/capture_r4_mockups.py

Captures static HTML mockups in mockups/topbar/ across 3 resolutions:
- 1450x900 (PRIMARY OWNER VIEWPORT)
- 1920x1080
- 1600x1000

Measures:
- Left pane width (>= 500px at 1450)
- Right pane width (>= 800px at 1450)
- Editor dark field height (~450px)
- Signature pre scrollWidth <= clientWidth
- Anti-crush items (a-h)
- Longest signature on 1 line in practice_stress.html

Saves screenshots to docs/screenshots/r4/ and mirrors to brain artifacts directory.
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
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r4"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9270

RESOLUTIONS = [
    (1450, 900),   # PRIMARY
    (1920, 1080),  # Secondary
    (1600, 1000),  # Secondary
]

PAGES = [
    ("practice.html", "practice"),
    ("practice_stress.html", "practice_stress"),
    ("home.html", "home"),
    ("dashboard.html", "dashboard"),
    ("navbar-states.html", "navbar_states"),
]

async def run():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_r4_")
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

            async def capture_png(full_page=False):
                params = {"format": "png"}
                if full_page:
                    params["captureBeyondViewport"] = True
                res = await send("Page.captureScreenshot", params)
                return base64.b64decode(res.get("data", ""))

            async def capture_clip(clip_rect):
                params = {"format": "png", "clip": clip_rect}
                res = await send("Page.captureScreenshot", params)
                return base64.b64decode(res.get("data", ""))

            def save_screenshot(img_bytes, filename):
                doc_path = DOCS_DIR / filename
                doc_path.write_bytes(img_bytes)
                brain_path = BRAIN_DIR / filename
                brain_path.write_bytes(img_bytes)
                print(f"[Screenshot] Saved {filename} ({len(img_bytes)} bytes)")

            all_measurements = {}

            for width, height in RESOLUTIONS:
                res_str = f"{width}x{height}"
                print(f"\n=======================================================")
                print(f"  TESTING & CAPTURING RESOLUTION {res_str}")
                print(f"=======================================================")

                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False
                })

                all_measurements[res_str] = {}

                for html_file, label in PAGES:
                    file_url = f"file:///{WORKSPACE_ROOT.as_posix()}/mockups/topbar/{html_file}"
                    await send("Page.navigate", {"url": file_url})
                    await asyncio.sleep(1.0)

                    # Viewport capture
                    vp_name = f"{label}_{res_str}.png"
                    vp_bytes = await capture_png(full_page=False)
                    save_screenshot(vp_bytes, vp_name)

                    # Full page capture for primary resolution practice
                    if label == "practice" and width == 1450:
                        fp_name = f"{label}_fullpage_{res_str}.png"
                        fp_bytes = await capture_png(full_page=True)
                        save_screenshot(fp_bytes, fp_name)

                    # Close-up capture of redesigned queue for primary resolution home
                    if label == "home" and width == 1450:
                        queue_rect = await eval_js("""
                            (() => {
                                const card = document.querySelector('.home-card');
                                if (!card) return null;
                                const r = card.getBoundingClientRect();
                                return {x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), scale: 1};
                            })()
                        """)
                        if queue_rect:
                            q_bytes = await capture_clip(queue_rect)
                            save_screenshot(q_bytes, f"home_queue_closeup_{res_str}.png")

                    # Close-up capture of State 6 verdict specimens for navbar_states
                    if label == "navbar_states" and width == 1450:
                        await eval_js("""
                            (() => {
                                const sec = document.querySelector('.specimen-section:last-of-type');
                                if (sec) sec.scrollIntoView();
                            })()
                        """)
                        await asyncio.sleep(0.5)
                        specimen_rect = await eval_js("""
                            (() => {
                                const sec = document.querySelector('.specimen-section:last-of-type');
                                if (!sec) return null;
                                const r = sec.getBoundingClientRect();
                                return {x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), scale: 1};
                            })()
                        """)
                        if specimen_rect:
                            sp_bytes = await capture_clip(specimen_rect)
                            save_screenshot(sp_bytes, f"navbar_states_specimens_{res_str}.png")

                    await asyncio.sleep(0.5)

                    if label == "dashboard":
                        m_dash = await eval_js("""
                            (() => {
                                const statVals = Array.from(document.querySelectorAll('.stat-value')).map(el => el.innerText.trim());
                                const tableRows = Array.from(document.querySelectorAll('.queue-table tbody tr, .dashboard-table tbody tr'));
                                const masteryItems = Array.from(document.querySelectorAll('.mastery-item'));
                                const doc = document.documentElement;

                                return {
                                    statCardsValues: statVals,
                                    masteryItemsCount: masteryItems.length,
                                    tableRowsCount: tableRows.length,
                                    docScrollWidth: doc.scrollWidth,
                                    docClientWidth: doc.clientWidth,
                                    noDocOverflow: doc.scrollWidth <= doc.clientWidth
                                };
                            })()
                        """)
                        all_measurements[res_str]["dashboard"] = m_dash
                        print(f"Dashboard Measurements ({res_str}): {json.dumps(m_dash, indent=2)}")

                    # Specific measurements for Practice
                    if label == "practice":
                        m = await eval_js("""
                            (() => {
                                const leftPane = document.querySelector('.left-pane');
                                const rightPane = document.querySelector('.right-pane');
                                const problemCard = document.querySelector('.problem-card');
                                const outputCard = document.querySelector('.output-card');
                                const editorField = document.querySelector('.editor-dark-field');
                                const sigPre = document.querySelector('.signature-pre');
                                const title = document.querySelector('.problem-title');
                                const testHeaders = Array.from(document.querySelectorAll('.test-case-title'));
                                const filterLabels = Array.from(document.querySelectorAll('.filter-label'));
                                const filterItems = Array.from(document.querySelectorAll('.filter-item'));
                                const hintBtns = Array.from(document.querySelectorAll('.btn-hint-outline, .btn-hint-solid'));
                                const navPills = Array.from(document.querySelectorAll('.nav-pill'));
                                const statusChips = Array.from(document.querySelectorAll('.status-chip'));
                                const doc = document.documentElement;

                                const leftRect = leftPane ? leftPane.getBoundingClientRect() : null;
                                const rightRect = rightPane ? rightPane.getBoundingClientRect() : null;
                                const editorRect = editorField ? editorField.getBoundingClientRect() : null;
                                const sigRect = sigPre ? sigPre.getBoundingClientRect() : null;

                                return {
                                    leftPaneWidth: leftRect ? Math.round(leftRect.width) : null,
                                    rightPaneWidth: rightRect ? Math.round(rightRect.width) : null,
                                    isLeftPaneGte500: leftRect ? leftRect.width >= 500 : false,
                                    isRightPaneGte800: rightRect ? rightRect.width >= 800 : false,
                                    hasProblemCard: problemCard !== null,
                                    hasOutputCard: outputCard !== null,
                                    editorHeight: editorRect ? Math.round(editorRect.height) : null,
                                    isEditorTall: editorRect ? editorRect.height >= 440 : false,
                                    sigScrollWidth: sigPre ? sigPre.scrollWidth : null,
                                    sigClientWidth: sigPre ? sigPre.clientWidth : null,
                                    sigNoOverflow: sigPre ? sigPre.scrollWidth <= sigPre.clientWidth : false,
                                    titleOnOneLine: title ? title.clientHeight < 36 : false,
                                    docScrollWidth: doc.scrollWidth,
                                    docClientWidth: doc.clientWidth,
                                    noDocOverflow: doc.scrollWidth <= doc.clientWidth,
                                    testCasesSingleLine: testHeaders.every(h => h.clientHeight < 26),
                                    filterLabelsSingleLine: filterLabels.every(l => l.clientHeight < 20),
                                    filterItemsCount: filterItems.length,
                                    hintButtonsLabels: hintBtns.map(b => b.innerText.trim()),
                                    navPillsLabels: navPills.map(p => p.innerText.trim()),
                                    statusChipsLabels: statusChips.map(c => c.innerText.trim())
                                };
                            })()
                        """)
                        all_measurements[res_str]["practice"] = m
                        print(f"Practice Measurements ({res_str}): {json.dumps(m, indent=2)}")

                    elif label == "practice_stress":
                        m_stress = await eval_js("""
                            (() => {
                                const editorLines = document.querySelector('.editor-lines');
                                const lines = editorLines ? editorLines.innerText.trim().split('\\n') : [];
                                const firstLine = lines.length ? lines[0].trim() : null;
                                const sigPre = document.querySelector('.signature-pre');
                                const leftPane = document.querySelector('.left-pane');
                                const rightPane = document.querySelector('.right-pane');
                                const doc = document.documentElement;

                                return {
                                    firstLineText: firstLine,
                                    firstLineLength: firstLine ? firstLine.length : 0,
                                    sigScrollWidth: sigPre ? sigPre.scrollWidth : null,
                                    sigClientWidth: sigPre ? sigPre.clientWidth : null,
                                    sigNoOverflow: sigPre ? sigPre.scrollWidth <= sigPre.clientWidth : false,
                                    docScrollWidth: doc.scrollWidth,
                                    docClientWidth: doc.clientWidth,
                                    noDocOverflow: doc.scrollWidth <= doc.clientWidth,
                                    leftPaneWidth: leftPane ? Math.round(leftPane.getBoundingClientRect().width) : null,
                                    rightPaneWidth: rightPane ? Math.round(rightPane.getBoundingClientRect().width) : null
                                };
                            })()
                        """)
                        all_measurements[res_str]["practice_stress"] = m_stress
                        print(f"Stress Measurements ({res_str}): {json.dumps(m_stress, indent=2)}")

            # Save full measurements JSON
            summary_path = DOCS_DIR / "r4_measurements.json"
            summary_path.write_text(json.dumps(all_measurements, indent=2), encoding="utf-8")
            shutil.copy2(summary_path, BRAIN_DIR / "r4_measurements.json")
            print(f"[Done] Written all R4 measurements to {summary_path}")

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(run())
