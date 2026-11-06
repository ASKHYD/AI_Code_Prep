r"""
scratch/capture_corrective_pass.py

Comprehensive verification and screenshot capture for Phase 2 Corrective Round:
- Live computed editor height via CDP
- Practice screen captures at 1920x1080 and 1600x1000 (tall fullpage)
- Dashboard table nowrap check & captures
- Home streak honesty check & captures
- Mock start view rules check & captures
- Direct mirroring to artifact directory C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144
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
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_PORT = 8501
CDP_PORT = 9235

def is_streamlit_running(port: int = STREAMLIT_PORT) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_streamlit() -> subprocess.Popen | None:
    if is_streamlit_running(STREAMLIT_PORT):
        print(f"[Streamlit] Already running on port {STREAMLIT_PORT}", flush=True)
        return None

    print(f"[Streamlit] Launching local Streamlit on port {STREAMLIT_PORT}...", flush=True)
    python_exe = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    proc = subprocess.Popen(
        [
            str(python_exe),
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(STREAMLIT_PORT),
            "--server.address",
            "127.0.0.1",
        ],
        cwd=str(WORKSPACE_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(40):
        time.sleep(0.5)
        if is_streamlit_running(STREAMLIT_PORT):
            print(f"[Streamlit] Server ready at http://127.0.0.1:{STREAMLIT_PORT}", flush=True)
            return proc

    raise RuntimeError("Failed to start Streamlit server within 20 seconds.")

async def run_captures():
    st_proc = start_streamlit()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_corr_")
    chrome_proc = subprocess.Popen(
        [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={profile_dir}",
            "--window-size=1920,1080",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ws_url = None
        for _ in range(30):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list", timeout=1) as resp:
                    tabs = json.loads(resp.read().decode("utf-8"))
                    page_tabs = [t for t in tabs if t.get("type") == "page"]
                    if page_tabs:
                        ws_url = page_tabs[0].get("webSocketDebuggerUrl")
                        if ws_url:
                            break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError(f"Could not connect to Chrome debugging port {CDP_PORT}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == cid:
                        return data.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("DOM.enable")

            # Helper to save screenshot
            def save_img(img_bytes, filename):
                out_path = DOCS_DIR / filename
                out_path.write_bytes(img_bytes)
                print(f"[CDP] Saved {out_path} ({len(img_bytes)} bytes)", flush=True)
                brain_path = BRAIN_DIR / filename
                brain_path.write_bytes(img_bytes)
                print(f"[CDP] Mirrored to {brain_path}", flush=True)

            # -------------------------------------------------------------
            # 1. PRACTICE ARENA: MEASUREMENTS & CAPTURES
            # -------------------------------------------------------------
            print("\n=== VERIFYING DEFECT 2: PRACTICE ARENA LAYOUT & EDITOR HEIGHT ===", flush=True)
            for width, height in [(1920, 1080), (1600, 1000)]:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                # Navigate to practice with demo_fail=true so verdict card also renders
                await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=practice&demo_fail=true"})
                await asyncio.sleep(4.0)

                # Query live computed editor dimensions
                dim_eval = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const iframe = document.querySelector('.st-key-practice_editor_card iframe');
                        const textarea = document.querySelector('.st-key-practice_editor_card textarea');
                        const card = document.querySelector('.st-key-practice_editor_card');
                        const headerStrip = document.querySelector('.editor-header-strip');
                        const sigBox = document.querySelector('.code-block-light');
                        const hintBtns = Array.from(document.querySelectorAll('.st-key-practice_hint_card button'));

                        const result = {};
                        if (iframe) {
                            const cs = window.getComputedStyle(iframe);
                            const r = iframe.getBoundingClientRect();
                            result.iframe = {
                                computedHeight: cs.height,
                                computedMinHeight: cs.minHeight,
                                rectHeight: r.height,
                                rectWidth: r.width,
                            };
                        }
                        if (textarea) {
                            const cs = window.getComputedStyle(textarea);
                            const r = textarea.getBoundingClientRect();
                            result.textarea = {
                                computedHeight: cs.height,
                                computedMinHeight: cs.minHeight,
                                rectHeight: r.height,
                                rectWidth: r.width,
                            };
                        }
                        if (card) {
                            const r = card.getBoundingClientRect();
                            result.card = { rectHeight: r.height, rectWidth: r.width };
                        }
                        if (headerStrip) {
                            const cs = window.getComputedStyle(headerStrip);
                            result.headerStrip = {
                                whiteSpace: cs.whiteSpace,
                                display: cs.display,
                                backgroundColor: cs.backgroundColor
                            };
                        }
                        if (sigBox) {
                            const cs = window.getComputedStyle(sigBox);
                            result.sigBox = {
                                whiteSpace: cs.whiteSpace,
                                overflowX: cs.overflowX
                            };
                        }
                        result.hintButtonCount = hintBtns.length;
                        result.hintButtonFullWidth = hintBtns.map(b => b.classList.contains('st-key-btn_hint') || b.style.width === '100%' || window.getComputedStyle(b).width);
                        return result;
                    })()
                    """,
                    "returnByValue": True,
                })
                dims = dim_eval.get("result", {}).get("value", {})
                print(f"[CDP {width}x{height}] Live Practice Arena Measurements:\n{json.dumps(dims, indent=2)}", flush=True)

                # Capture tall full-page screenshot
                # Get scroll height
                layout_eval = await send_cmd("Page.getLayoutMetrics")
                content_size = layout_eval.get("cssContentSize", {})
                doc_height = int(content_size.get("height", height))
                print(f"[CDP {width}x{height}] Document full height = {doc_height}px", flush=True)

                # Set metrics to full doc height to capture whole tall page
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": max(height, doc_height),
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await asyncio.sleep(0.5)

                res = await send_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                b64 = res.get("data")
                if b64:
                    save_img(base64.b64decode(b64), f"practice_real_{width}x{height}.png")

            # -------------------------------------------------------------
            # 2. DASHBOARD: VERIFY NOWRAP BADGES & CAPTURES
            # -------------------------------------------------------------
            print("\n=== VERIFYING DEFECT 4: DASHBOARD NOWRAP BADGES ===", flush=True)
            for width, height in [(1920, 1080), (1600, 1000)]:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=dashboard"})
                await asyncio.sleep(4.0)

                # Check table badge styles
                badge_eval = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const badges = Array.from(document.querySelectorAll('.dashboard-table .stat-badge'));
                        const lastTh = document.querySelector('.dashboard-table th:last-child');
                        const lastTd = document.querySelector('.dashboard-table td:last-child');
                        return {
                            thLastChild: lastTh ? {
                                whiteSpace: window.getComputedStyle(lastTh).whiteSpace,
                                minWidth: window.getComputedStyle(lastTh).minWidth,
                            } : null,
                            tdLastChild: lastTd ? {
                                whiteSpace: window.getComputedStyle(lastTd).whiteSpace,
                                minWidth: window.getComputedStyle(lastTd).minWidth,
                            } : null,
                            badgeCount: badges.length,
                            badges: badges.map(b => ({
                                text: b.innerText,
                                whiteSpace: window.getComputedStyle(b).whiteSpace,
                                clientHeight: b.clientHeight,
                                clientWidth: b.clientWidth,
                            }))
                        };
                    })()
                    """,
                    "returnByValue": True,
                })
                badge_info = badge_eval.get("result", {}).get("value", {})
                print(f"[CDP {width}x{height}] Dashboard Badges:\n{json.dumps(badge_info, indent=2)}", flush=True)

                # Capture full-page / tall screenshot
                layout_eval = await send_cmd("Page.getLayoutMetrics")
                content_size = layout_eval.get("cssContentSize", {})
                doc_height = int(content_size.get("height", height))

                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": max(height, doc_height),
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await asyncio.sleep(0.5)

                res = await send_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                b64 = res.get("data")
                if b64:
                    save_img(base64.b64decode(b64), f"dashboard_real_{width}x{height}.png")

            # -------------------------------------------------------------
            # 3. HOME: VERIFY STREAK HONESTY & CAPTURES
            # -------------------------------------------------------------
            print("\n=== VERIFYING DEFECT 5: HOME STREAK HONESTY ===", flush=True)
            for width, height in [(1920, 1080), (1600, 1000)]:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=home"})
                await asyncio.sleep(4.0)

                streak_eval = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const card = document.querySelector('.st-key-home_card_streak');
                        return card ? card.innerText : 'CARD NOT FOUND';
                    })()
                    """
                })
                print(f"[CDP {width}x{height}] Home Streak Card Text:\n{streak_eval.get('result', {}).get('value')}", flush=True)

                res = await send_cmd("Page.captureScreenshot", {"format": "png"})
                b64 = res.get("data")
                if b64:
                    save_img(base64.b64decode(b64), f"home_real_{width}x{height}.png")

            # -------------------------------------------------------------
            # 4. MOCK INTERVIEW START VIEW: RULES & PAST SESSIONS CHECK
            # -------------------------------------------------------------
            print("\n=== VERIFYING DEFECT 5: MOCK START VIEW PROTOCOL & EMPTY PAST SESSIONS ===", flush=True)
            for width, height in [(1920, 1080), (1600, 1000)]:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen=mock"})
                await asyncio.sleep(4.0)

                mock_eval = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const rulesCard = document.querySelector('.st-key-mock_rules_card');
                        const pastCard = document.querySelector('.st-key-mock_past_sessions_card');
                        const pastTable = document.querySelector('.dashboard-table');
                        return {
                            hasRulesCard: !!rulesCard,
                            rulesCardHeading: rulesCard ? rulesCard.querySelector('h3')?.innerText : null,
                            hasPastSessionsCard: !!pastCard,
                            hasPastTable: !!pastTable
                        };
                    })()
                    """,
                    "returnByValue": True,
                })
                print(f"[CDP {width}x{height}] Mock Start View Elements:\n{json.dumps(mock_eval.get('result', {}).get('value'), indent=2)}", flush=True)

                layout_eval = await send_cmd("Page.getLayoutMetrics")
                content_size = layout_eval.get("cssContentSize", {})
                doc_height = int(content_size.get("height", height))

                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": max(height, doc_height),
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                await asyncio.sleep(0.5)

                res = await send_cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                b64 = res.get("data")
                if b64:
                    save_img(base64.b64decode(b64), f"mock_real_{width}x{height}.png")

            # -------------------------------------------------------------
            # 5. DEFECT 3: VERIFY SIDEBAR NAV PILL TINT PER AREA
            # -------------------------------------------------------------
            print("\n=== VERIFYING DEFECT 3: SIDEBAR NAV PILL TINTS PER AREA ===", flush=True)
            nav_screens = [
                ("home", "Home", "rgb(223, 243, 228)", "#DFF3E4", "rgb(22, 123, 72)", "#167B48"),
                ("practice", "Practice Arena", "rgb(232, 226, 255)", "#E8E2FF", "rgb(89, 50, 234)", "#5932EA"),
                ("mock", "Mock Interview", "rgb(255, 232, 209)", "#FFE8D1", "rgb(185, 56, 21)", "#B93815"),
                ("dashboard", "Dashboard", "rgb(220, 235, 255)", "#DCEBFF", "rgb(29, 94, 194)", "#1D5EC2"),
            ]
            for s_param, label, expected_rgb_bg, hex_bg, expected_rgb_fg, hex_fg in nav_screens:
                await send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{STREAMLIT_PORT}/?screen={s_param}"})
                await asyncio.sleep(3.5)

                tint_eval = await send_cmd("Runtime.evaluate", {
                    "expression": """
                    (() => {
                        const checkedLabel = document.querySelector('.st-key-nav_sidebar_radio label:has(input:checked)') ||
                                             document.querySelector('.st-key-nav_sidebar_radio label:has(div[aria-checked="true"])');
                        if (!checkedLabel) return null;
                        const cs = window.getComputedStyle(checkedLabel);
                        const p = checkedLabel.querySelector('p') || checkedLabel.querySelector('span');
                        const p_cs = p ? window.getComputedStyle(p) : cs;
                        return {
                            labelText: checkedLabel.innerText.trim(),
                            backgroundColor: cs.backgroundColor,
                            color: p_cs.color,
                        };
                    })()
                    """,
                    "returnByValue": True,
                })
                t_val = tint_eval.get("result", {}).get("value")
                print(f"[CDP Nav Tint] Screen '{s_param}' ({label}):", t_val, flush=True)

    finally:
        chrome_proc.terminate()
        try:
            shutil.rmtree(profile_dir, ignore_errors=True)
        except Exception:
            pass
        if st_proc:
            st_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_captures())
