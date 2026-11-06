"""
scratch/run_r6_verification.py
Comprehensive Wave 2 Evidence & Verification Suite:
- Multi-resolution captures (1450x900, 1920x1080, 1600x1000)
- X1 Top void killed & sticky topbar rect check
- X2 Dynamic runtime Python version chip check
- X3 Dashboard Plotly horizontal bar chart check
- X4 Primary green pill CTA buttons check
- X5R Slim problem picker row check (0 dropdowns)
- X6 Unified signature check & 0 horizontal overflow
- X7 Home mockup subtexts & Practice neutral output header
- X8 Run & Submit natural width check
- X9 Small-caps signature label & inline code wash chips check
- E1 Impeccable review captures
- E2 Offline base64 font proofs (Fraunces, Inter, JetBrains Mono)
- E8 Hint ladder expander empirical capture
- E9 Pill-tint computed CDP hex colors
"""

import asyncio
import base64
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.request
import websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r6"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9296

RESOLUTIONS = [
    (1450, 900),   # Primary owner viewport
    (1920, 1080),  # Secondary
    (1600, 1000),  # Secondary
]

PAGES = [
    ("home", "http://127.0.0.1:8501/?screen=home"),
    ("practice", "http://127.0.0.1:8501/?screen=practice"),
    ("practice_stress", "http://127.0.0.1:8501/?screen=practice&problem=log-timestamp-filter"),
    ("practice_hint_expanded", "http://127.0.0.1:8501/?screen=practice"),
    ("dashboard", "http://127.0.0.1:8501/?screen=dashboard"),
    ("mock_unstarted", "http://127.0.0.1:8501/?screen=mock"),
    ("mock_running", "http://127.0.0.1:8501/?screen=mock&mock_state=running"),
    ("mock_completed", "http://127.0.0.1:8501/?screen=mock&mock_state=completed"),
]

PAGE_WAIT_SELECTORS = {
    "home": ".queue-row",
    "practice": ".st-key-practice_problem_card",
    "practice_stress": ".st-key-practice_problem_card",
    "practice_hint_expanded": ".st-key-practice_problem_card",
    "dashboard": ".js-plotly-plot, .mastery-item",
    "mock_unstarted": ".st-key-mock_rules_card",
    "mock_running": ".mock-timer-pill",
    "mock_completed": ".st-key-mock_scorecard_card",
}

def rgb_to_hex(rgb_str):
    if not rgb_str or "rgb" not in rgb_str:
        return rgb_str
    import re
    m = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02X}{g:02X}{b:02X}"
    return rgb_str

async def run():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_r6_")
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

            async def wait_for_selector(sel, timeout=12.0):
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
                (DOCS_DIR / filename).write_bytes(img_bytes)
                (BRAIN_DIR / filename).write_bytes(img_bytes)
                print(f"  [Saved] {filename} ({len(img_bytes)} bytes)")

            all_measurements = {}

            for width, height in RESOLUTIONS:
                res_str = f"{width}x{height}"
                print(f"\n=======================================================")
                print(f"  RUNNING R6 BATTERY: {res_str}")
                print(f"=======================================================")

                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False
                })

                res_metrics = {}

                for page_name, url in PAGES:
                    print(f"\n--- Loading {page_name} ({url}) ---")
                    await send("Page.navigate", {"url": url})
                    target_sel = PAGE_WAIT_SELECTORS.get(page_name, ".topbar")
                    await wait_for_selector(target_sel, timeout=12.0)

                    # For editor pages, wait for iframe
                    if "practice" in page_name or "mock_running" in page_name:
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

                    # For hint expanded, click the hint expander
                    if page_name == "practice_hint_expanded":
                        await eval_js("""
                            (() => {
                                const details = document.querySelector('.st-key-practice_hint_ladder details, [data-testid="stExpander"] details');
                                if (details && !details.open) {
                                    details.querySelector('summary')?.click();
                                }
                            })()
                        """)
                        await asyncio.sleep(0.8)

                    await asyncio.sleep(1.2)

                    # Capture viewport
                    vp_png = await capture_png(full_page=False)
                    save_screenshot(vp_png, f"{page_name}_{res_str}.png")

                    # For primary 1450x900, capture fullpage
                    if width == 1450:
                        fp_png = await capture_png(full_page=True)
                        save_screenshot(fp_png, f"{page_name}_fullpage_{res_str}.png")

                    # Collect metrics per page
                    if page_name == "home":
                        home_metrics = await eval_js("""
                            (() => {
                                const topbar = document.querySelector('.topbar');
                                const tbRect = topbar ? topbar.getBoundingClientRect() : null;
                                const pyChip = document.querySelector('.status-chip-py span');
                                const h1 = document.querySelector('h1');
                                const rows = document.querySelectorAll('.queue-row');
                                const pillBtns = Array.from(document.querySelectorAll('button, a')).filter(b => b.innerText.includes("Practice"));
                                const streakTag = document.querySelector('.st-key-home_card_streak .stat-badge');
                                const streakCaption = document.querySelector('.st-key-home_card_streak .stat-desc');

                                // Computed fonts
                                const h1Font = h1 ? window.getComputedStyle(h1).fontFamily : null;
                                const bodyFont = window.getComputedStyle(document.body).fontFamily;

                                return {
                                    topbar_height: tbRect ? Math.round(tbRect.height) : null,
                                    topbar_top: tbRect ? Math.round(tbRect.top) : null,
                                    py_chip_version: pyChip ? pyChip.innerText.trim() : null,
                                    h1_text: h1 ? h1.innerText.trim() : null,
                                    h1_font: h1Font,
                                    body_font: bodyFont,
                                    queue_row_count: rows.length,
                                    has_pill_cta: pillBtns.length > 0,
                                    streak_badge_text: streakTag ? streakTag.innerText.trim() : null,
                                    streak_caption: streakCaption ? streakCaption.innerText.trim() : null
                                };
                            })()
                        """)
                        res_metrics["home"] = home_metrics
                        print(f"  [Home Metrics]: {home_metrics}")

                    elif page_name == "practice":
                        prac_metrics = await eval_js("""
                            (() => {
                                const topbar = document.querySelector('.topbar');
                                const tbRect = topbar ? topbar.getBoundingClientRect() : null;
                                const pickerRow = document.querySelector('.problem-picker-row');
                                const pickerTitle = document.querySelector('.picker-title, .problem-picker-row [style*="Fraunces"]');
                                const pickerBtns = document.querySelectorAll('.picker-arrow-btn, .problem-picker-row button');
                                const filterDropdowns = document.querySelectorAll('.stSelectbox, [data-testid="stSelectbox"]');
                                const cols = Array.from(document.querySelectorAll('[data-testid="stColumn"], [data-testid="column"], [data-testid="stHorizontalBlock"] > div'));
                                const wbCols = cols.filter(c => c.getBoundingClientRect().height > 200);
                                const leftCol = wbCols.length >= 2 ? wbCols[0] : null;
                                const rightCol = wbCols.length >= 2 ? wbCols[1] : null;
                                const iframe = document.querySelector('.st-key-practice_editor_card iframe') || document.querySelector('iframe');
                                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes("Run & Submit"));
                                const runBtnRect = runBtn ? runBtn.getBoundingClientRect() : null;
                                const rightColRect = rightCol ? rightCol.getBoundingClientRect() : null;
                                const outputHdr = document.querySelector('.st-key-practice_output_card [style*="font-family"]');
                                const subhead = document.querySelector('.signature-subhead');
                                const codeChips = document.querySelectorAll('.problem-statement code, .stMarkdown code');
                                const pre = document.querySelector('.signature-pre, .st-key-practice_problem_card pre:last-of-type');

                                return {
                                    topbar_top: tbRect ? Math.round(tbRect.top) : null,
                                    topbar_height: tbRect ? Math.round(tbRect.height) : null,
                                    left_col_width: leftCol ? Math.round(leftCol.getBoundingClientRect().width) : null,
                                    right_col_width: rightCol ? Math.round(rightCol.getBoundingClientRect().width) : null,
                                    editor_iframe_height: iframe ? Math.round(iframe.getBoundingClientRect().height) : null,
                                    has_picker_row: Boolean(pickerRow),
                                    picker_title_text: pickerTitle ? pickerTitle.innerText.trim() : null,
                                    picker_button_count: pickerBtns.length,
                                    filter_dropdown_count: filterDropdowns.length,
                                    is_filter_strip_deleted: filterDropdowns.length === 0,
                                    run_btn_natural_width: runBtnRect && rightColRect ? runBtnRect.width < (rightColRect.width * 0.6) : null,
                                    run_btn_width: runBtnRect ? Math.round(runBtnRect.width) : null,
                                    output_header_text: outputHdr ? outputHdr.innerText.trim() : null,
                                    has_smallcaps_signature_label: Boolean(subhead) || (document.body.innerText.includes("STARTER FUNCTION SIGNATURE")),
                                    code_chips_count: codeChips.length,
                                    sig_scroll_width: pre ? pre.scrollWidth : null,
                                    sig_client_width: pre ? pre.clientWidth : null,
                                    sig_no_overflow: pre ? pre.scrollWidth <= pre.clientWidth + 2 : null
                                };
                            })()
                        """)
                        res_metrics["practice"] = prac_metrics
                        print(f"  [Practice Metrics]: {prac_metrics}")

                    elif page_name == "practice_stress":
                        stress_metrics = await eval_js("""
                            (() => {
                                const pre = document.querySelector('.signature-pre, .st-key-practice_problem_card pre:last-of-type') || document.querySelector('pre');
                                return {
                                    scroll_width: pre ? pre.scrollWidth : null,
                                    client_width: pre ? pre.clientWidth : null,
                                    no_overflow: pre ? pre.scrollWidth <= pre.clientWidth + 2 : null
                                };
                            })()
                        """)
                        res_metrics["signature_stress"] = stress_metrics
                        print(f"  [Signature Stress Metrics]: {stress_metrics}")

                    elif page_name == "dashboard":
                        dash_metrics = await eval_js("""
                            (() => {
                                const h1 = document.querySelector('h1');
                                const plotlyChart = document.querySelector('.js-plotly-plot');
                                const bars = document.querySelectorAll('.js-plotly-plot .bars path');
                                const masteryItems = document.querySelectorAll('.mastery-item');
                                const table = document.querySelector('.queue-table');
                                const pageText = document.body.innerText;

                                return {
                                    h1_text: h1 ? h1.innerText.trim() : null,
                                    has_plotly_chart: Boolean(plotlyChart),
                                    plotly_bars_count: bars.length,
                                    mastery_items_count: masteryItems.length,
                                    has_table: Boolean(table),
                                    has_unsourced_80_percent: pageText.includes("Target Threshold: 80%")
                                };
                            })()
                        """)
                        res_metrics["dashboard"] = dash_metrics
                        print(f"  [Dashboard Metrics]: {dash_metrics}")

                    elif page_name == "mock_running":
                        mock_r_metrics = await eval_js("""
                            (() => {
                                const pill = document.querySelector('.mock-timer-pill');
                                const endBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes("End Interview"));
                                return {
                                    timer_text: pill ? pill.innerText.trim() : null,
                                    has_end_btn: Boolean(endBtn)
                                };
                            })()
                        """)
                        res_metrics["mock_running"] = mock_r_metrics
                        print(f"  [Mock Running Metrics]: {mock_r_metrics}")

                    elif page_name == "mock_completed":
                        mock_c_metrics = await eval_js("""
                            (() => {
                                const pageText = document.body.innerText;
                                const exportBtn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes("Export") || b.innerText.includes("Markdown"));
                                return {
                                    has_scorecard: pageText.includes("Final Interview Scorecard"),
                                    has_178_leak: pageText.includes("178 ms"),
                                    has_export_btn: Boolean(exportBtn)
                                };
                            })()
                        """)
                        res_metrics["mock_completed"] = mock_c_metrics
                        print(f"  [Mock Completed Metrics]: {mock_c_metrics}")

                # Capture Pill-Tint Computed Hex Colors (E9)
                if width == 1450:
                    pill_hex_data = await eval_js("""
                        (() => {
                            function getHex(el, prop) {
                                if (!el) return null;
                                return window.getComputedStyle(el).getPropertyValue(prop);
                            }
                            const pyChip = document.querySelector('.status-chip-py');
                            const streakChip = document.querySelector('.status-chip-streak');
                            const dueChip = document.querySelector('.status-chip-due');
                            const navHome = document.querySelector('.nav-pill.active, .nav-pill');
                            const queueBadge = document.querySelector('.queue-row .stat-badge');

                            return {
                                py_chip: { bg: getHex(pyChip, 'background-color'), color: getHex(pyChip, 'color') },
                                streak_chip: { bg: getHex(streakChip, 'background-color'), color: getHex(streakChip, 'color') },
                                due_chip: { bg: getHex(dueChip, 'background-color'), color: getHex(dueChip, 'color') },
                                nav_pill: { bg: getHex(navHome, 'background-color'), color: getHex(navHome, 'color') },
                                queue_badge: { bg: getHex(queueBadge, 'background-color'), color: getHex(queueBadge, 'color') }
                            };
                        })()
                    """)
                    # Convert to hex
                    hex_clean = {}
                    for k, v in (pill_hex_data or {}).items():
                        hex_clean[k] = {
                            "bg_raw": v["bg"],
                            "color_raw": v["color"],
                            "bg_hex": rgb_to_hex(v["bg"]),
                            "color_hex": rgb_to_hex(v["color"]),
                        }
                    res_metrics["pill_hexes"] = hex_clean
                    print(f"\n  [E9 Pill Hexes]: {hex_clean}")

                all_measurements[res_str] = res_metrics

            # Save full measurements
            out_file = DOCS_DIR / "r6_measurements.json"
            out_file.write_text(json.dumps(all_measurements, indent=2), encoding="utf-8")
            (BRAIN_DIR / "r6_measurements.json").write_text(json.dumps(all_measurements, indent=2), encoding="utf-8")
            print(f"\n[All R6 Measurements Saved] -> {out_file}")

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())

