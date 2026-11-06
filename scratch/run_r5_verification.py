r"""
scratch/run_r5_verification.py

Comprehensive Verification and Screenshot Capture Battery for Topbar Workbench Implementation (Round 5):
- 1450x900 (PRIMARY OWNER VIEWPORT)
- 1920x1080
- 1600x1000

Screens:
- Home: Today's Practice (de-slopped queue, clean stat cards)
- Practice: Topbar Workbench (two panes 42/58, filter strip, One Problem Card, butter hint ladder, 450px editor, One Output Card)
- Practice Stress: log-timestamp-filter (79-char signature on 1 line)
- Practice Demo Fail: longest-substring defect execution with verdict & test cases
- Mock Unstarted: Technical Interview Simulation (rules card full width, no void)
- Mock Running: Sub-strip countdown timer & problem tabs, workspace
- Mock Completed: Final Scorecard with session-scoped results & export
- Dashboard: Performance Analytics (de-slopped topic table, unattempted NOT STARTED with no bar/pct, no 80% header)
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
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r5"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9280

RESOLUTIONS = [
    (1450, 900),   # PRIMARY OWNER VIEWPORT
    (1920, 1080),  # Secondary
    (1600, 1000),  # Secondary
]

PAGES = [
    ("home", "http://127.0.0.1:8501/?screen=home", True),
    ("practice", "http://127.0.0.1:8501/?screen=practice", True),
    ("practice_stress", "http://127.0.0.1:8501/?screen=practice&problem=log-timestamp-filter", True),
    ("practice_demo_fail", "http://127.0.0.1:8501/?screen=practice&problem=longest-substring-without-repeating&demo_fail=true", True),
    ("mock_unstarted", "http://127.0.0.1:8501/?screen=mock", False),
    ("mock_running", "http://127.0.0.1:8501/?screen=mock&mock_state=running", True),
    ("mock_completed", "http://127.0.0.1:8501/?screen=mock&mock_state=completed", False),
    ("dashboard", "http://127.0.0.1:8501/?screen=dashboard", False),
]

def is_server_running(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

PAGE_SELECTORS = {
    "home": ".st-key-home_card_streak",
    "practice": ".st-key-practice_problem_card",
    "practice_stress": ".st-key-practice_problem_card",
    "practice_demo_fail": ".st-key-practice_output_card .verdict-band",
    "mock_unstarted": ".st-key-mock_rules_card",
    "mock_running": ".mock-timer-pill",
    "mock_completed": ".st-key-mock_scorecard_card",
    "dashboard": ".st-key-dashboard_mastery_card",
}

async def run():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    if not is_server_running(f"http://127.0.0.1:{STREAMLIT_PORT}/_stcore/health"):
        raise RuntimeError(f"Streamlit not running on port {STREAMLIT_PORT}")

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_r5_")
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
            await send("Runtime.enable")
            await send("DOM.enable")

            async def eval_js(expr):
                r = await send("Runtime.evaluate", {
                    "expression": expr,
                    "returnByValue": True,
                    "awaitPromise": True
                })
                return r.get("result", {}).get("value")

            async def wait_for_selector(sel, timeout=10.0):
                start = time.time()
                while time.time() - start < timeout:
                    found = await eval_js(f"Boolean(document.querySelector('{sel}'))")
                    if found:
                        return True
                    await asyncio.sleep(0.2)
                return False

            async def capture_png(full_page=False):
                params = {"format": "png"}
                if full_page:
                    params["captureBeyondViewport"] = True
                res = await send("Page.captureScreenshot", params)
                return base64.b64decode(res.get("data", ""))

            def save_screenshot(img_bytes, filename):
                doc_path = DOCS_DIR / filename
                doc_path.write_bytes(img_bytes)
                brain_path = BRAIN_DIR / filename
                brain_path.write_bytes(img_bytes)
                print(f"  [Saved] {filename} ({len(img_bytes)} bytes)")

            all_metrics = {}

            for width, height in RESOLUTIONS:
                res_str = f"{width}x{height}"
                print(f"\n=======================================================")
                print(f"  TESTING RESOLUTION: {res_str}")
                print(f"=======================================================")

                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False
                })

                res_metrics = {}

                for page_name, url, has_editor in PAGES:
                    print(f"\n--- Loading {page_name} ({url}) ---")
                    await send("Page.navigate", {"url": url})
                    target_sel = PAGE_SELECTORS.get(page_name, ".topbar")
                    await wait_for_selector(target_sel, timeout=12.0)

                    if has_editor:
                        # Wait for iframe to mount
                        for _ in range(30):
                            ready = await eval_js("""
                                (() => {
                                    const iframes = Array.from(document.querySelectorAll('iframe'));
                                    return iframes.length > 0 && iframes[0].getBoundingClientRect().height > 50;
                                })()
                            """)
                            if ready:
                                break
                            await asyncio.sleep(0.3)

                    await asyncio.sleep(1.2)

                    # Viewport capture
                    vp_png = await capture_png(full_page=False)
                    save_screenshot(vp_png, f"{page_name}_{res_str}.png")

                    # Primary 1450x900 fullpage captures
                    if width == 1450:
                        fp_png = await capture_png(full_page=True)
                        save_screenshot(fp_png, f"{page_name}_fullpage_{res_str}.png")

                    # Page measurements
                    if page_name == "practice":
                        measurements = await eval_js("""
                            (() => {
                                const topbar = document.querySelector('.topbar');
                                const cols = Array.from(document.querySelectorAll('[data-testid="stColumn"], [data-testid="column"], [data-testid="stHorizontalBlock"] > div'));
                                // Filter to the two main workbench columns (height > 300)
                                const wbCols = cols.filter(c => c.getBoundingClientRect().height > 200);
                                const leftCol = wbCols.length >= 2 ? wbCols[0] : null;
                                const rightCol = wbCols.length >= 2 ? wbCols[1] : null;
                                const iframe = document.querySelector('.st-key-practice_editor_card iframe') || document.querySelector('iframe');
                                const probCard = document.querySelector('.st-key-practice_problem_card');
                                const hintLadder = document.querySelector('.st-key-practice_hint_ladder');
                                const editorCard = document.querySelector('.st-key-practice_editor_card');
                                const outputCard = document.querySelector('.st-key-practice_output_card');

                                return {
                                    topbar_height: topbar ? Math.round(topbar.getBoundingClientRect().height) : null,
                                    left_col_width: leftCol ? Math.round(leftCol.getBoundingClientRect().width) : null,
                                    right_col_width: rightCol ? Math.round(rightCol.getBoundingClientRect().width) : null,
                                    editor_iframe_height: iframe ? Math.round(iframe.getBoundingClientRect().height) : null,
                                    has_one_problem_card: Boolean(probCard),
                                    has_hint_ladder_butter: Boolean(hintLadder),
                                    has_editor_card: Boolean(editorCard),
                                    has_one_output_card: Boolean(outputCard),
                                };
                            })()
                        """)
                        res_metrics["practice"] = measurements
                        print(f"  [Practice Metrics]: {measurements}")

                    elif page_name == "practice_stress":
                        sig_metrics = await eval_js("""
                            (() => {
                                const pre = document.querySelector('.st-key-practice_problem_card pre:last-of-type') || document.querySelector('pre');
                                return {
                                    pre_scroll_width: pre ? pre.scrollWidth : null,
                                    pre_client_width: pre ? pre.clientWidth : null,
                                    no_horizontal_overflow: pre ? pre.scrollWidth <= pre.clientWidth + 2 : null,
                                };
                            })()
                        """)
                        res_metrics["signature_stress"] = sig_metrics
                        print(f"  [Signature Stress]: {sig_metrics}")

                    elif page_name == "home":
                        home_metrics = await eval_js("""
                            (() => {
                                const h1 = document.querySelector('h1');
                                const queueTable = document.querySelector('.queue-table');
                                const rows = document.querySelectorAll('.queue-row');
                                const firstRowBadges = rows.length > 0 ? rows[0].querySelectorAll('.stat-badge') : [];
                                return {
                                    h1_text: h1 ? h1.innerText.trim() : null,
                                    queue_row_count: rows.length,
                                    first_row_badge_count: firstRowBadges.length,
                                    has_queue_table: Boolean(queueTable),
                                };
                            })()
                        """)
                        res_metrics["home"] = home_metrics
                        print(f"  [Home Metrics]: {home_metrics}")

                    elif page_name == "dashboard":
                        dash_metrics = await eval_js("""
                            (() => {
                                const h1 = document.querySelector('h1');
                                const masteryItems = document.querySelectorAll('.mastery-item');
                                const table = document.querySelector('.queue-table');
                                const pageText = document.body.innerText;
                                return {
                                    h1_text: h1 ? h1.innerText.trim() : null,
                                    mastery_items_count: masteryItems.length,
                                    has_table: Boolean(table),
                                    has_unsourced_80_percent: pageText.includes("Target Threshold: 80%"),
                                };
                            })()
                        """)
                        res_metrics["dashboard"] = dash_metrics
                        print(f"  [Dashboard Metrics]: {dash_metrics}")

                    elif page_name == "mock_running":
                        mock_metrics = await eval_js("""
                            (() => {
                                const timerPill = document.querySelector('.mock-timer-pill');
                                const buttons = Array.from(document.querySelectorAll('button'));
                                const endBtn = buttons.find(b => b.innerText.includes("End Interview"));
                                const probCard = document.querySelector('.st-key-mock_problem_card');
                                return {
                                    timer_pill_text: timerPill ? timerPill.innerText.trim() : null,
                                    has_end_button: Boolean(endBtn),
                                    has_mock_problem_card: Boolean(probCard),
                                };
                            })()
                        """)
                        res_metrics["mock_running"] = mock_metrics
                        print(f"  [Mock Running Metrics]: {mock_metrics}")

                    elif page_name == "mock_completed":
                        sc_metrics = await eval_js("""
                            (() => {
                                const pageText = document.body.innerText;
                                const has178 = pageText.includes("178 ms");
                                const downloadBtn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes("Export"));
                                return {
                                    has_scorecard: pageText.includes("Final Interview Scorecard"),
                                    has_178_leak: has178,
                                    has_export_button: Boolean(downloadBtn),
                                };
                            })()
                        """)
                        res_metrics["mock_completed"] = sc_metrics
                        print(f"  [Mock Completed Metrics]: {sc_metrics}")

                all_metrics[res_str] = res_metrics

            # Save full metrics JSON
            metrics_path = BRAIN_DIR / "r5_measurements.json"
            metrics_path.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
            (DOCS_DIR / "r5_measurements.json").write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
            print(f"\n[Done] All metrics saved to {metrics_path}")

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(run())
