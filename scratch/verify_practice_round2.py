"""
Phase 2 Corrective Round 2 Verification Script
Measures CDP metrics for P1, P2, P3, P4, P5 and captures screenshots for dual resolutions:
- 1920x1080
- 1600x1000

Also captures:
- Practice viewport screenshots
- Practice full-page tall screenshots
- Practice longest-signature editor close-up
- Practice signature-box close-up
- Dual-resolution side-by-side comparisons with mockups/practice.html
"""
import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACTS_DIR = r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144"
DOCS_DIR = r"e:\resume_project\docs\screenshots\r3"
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

RESOLUTIONS = [
    (1920, 1080),
    (1600, 1000)
]

async def wait_for_editor(page, timeout_ms=15000):
    start = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start) * 1000 < timeout_ms:
        res = await page.evaluate('''() => {
            const iframes = Array.from(document.querySelectorAll('.st-key-practice_editor_card iframe'));
            if (!iframes.length) return false;
            const r = iframes[0].getBoundingClientRect();
            return r.height > 100 && r.width > 200;
        }''')
        if res:
            await asyncio.sleep(1.0) # settle
            return True
        await asyncio.sleep(0.5)
    return False

async def measure_practice(page, res_str):
    print(f"\n--- Measuring Practice at {res_str} ---")
    
    # 1. Measure P1: Editor iframe element
    p1_data = await page.evaluate('''() => {
        const iframe = document.querySelector('.st-key-practice_editor_card iframe');
        if (!iframe) return { error: "No iframe found in .st-key-practice_editor_card" };
        const rect = iframe.getBoundingClientRect();
        const style = window.getComputedStyle(iframe);
        return {
            selector: ".st-key-practice_editor_card iframe",
            elementDescription: "HTMLIFrameElement rendered by streamlit-code-editor component",
            renderedWidth: Math.round(rect.width),
            renderedHeight: Math.round(rect.height),
            top: Math.round(rect.top),
            bottom: Math.round(rect.bottom),
            computedHeight: style.height,
            isGte440: rect.height >= 440
        };
    }''')
    print(f"P1 Measurement: {json.dumps(p1_data, indent=2)}")

    # 2. Measure P3: Column balance and scrollWidth
    p3_data = await page.evaluate('''() => {
        const leftCard = document.querySelector('.st-key-practice_statement_card');
        const rightCard = document.querySelector('.st-key-practice_hint_card');
        const docScrollWidth = document.documentElement.scrollWidth;
        const docClientWidth = document.documentElement.clientWidth;
        
        let leftBottom = leftCard ? Math.round(leftCard.getBoundingClientRect().bottom) : null;
        let rightBottom = rightCard ? Math.round(rightCard.getBoundingClientRect().bottom) : null;
        
        let diffPct = null;
        if (leftBottom && rightBottom) {
            const maxB = Math.max(leftBottom, rightBottom);
            const minB = Math.min(leftBottom, rightBottom);
            diffPct = Number(((maxB - minB) / maxB * 100).toFixed(1));
        }

        return {
            leftCardBottom: leftBottom,
            rightCardBottom: rightBottom,
            diffPct: diffPct,
            isWithin20Pct: diffPct !== null ? diffPct <= 20.0 : false,
            documentScrollWidth: docScrollWidth,
            documentClientWidth: docClientWidth,
            noHorizontalOverflow: docScrollWidth <= docClientWidth + 1
        };
    }''')
    print(f"P3 Measurement: {json.dumps(p3_data, indent=2)}")

    # 3. Measure P4: Signature Box
    p4_data = await page.evaluate('''() => {
        const sigBox = document.querySelector('.signature-display-box');
        if (!sigBox) return { error: "No .signature-display-box found" };
        const rect = sigBox.getBoundingClientRect();
        return {
            selector: ".signature-display-box pre",
            elementDescription: "HTMLPreElement displaying broken function signature",
            scrollWidth: sigBox.scrollWidth,
            clientWidth: sigBox.clientWidth,
            noHorizontalScrollbar: sigBox.scrollWidth <= sigBox.clientWidth,
            textContent: sigBox.textContent.trim(),
            lineCount: sigBox.textContent.trim().split('\\n').length
        };
    }''')
    print(f"P4 Measurement: {json.dumps(p4_data, indent=2)}")

    # 4. Measure P5: Test case headings
    p5_data = await page.evaluate('''() => {
        const titles = Array.from(document.querySelectorAll('.test-case-card-title'));
        return titles.map((el, idx) => {
            const rect = el.getBoundingClientRect();
            const parent = el.parentElement;
            return {
                index: idx + 1,
                text: el.textContent.trim(),
                whiteSpace: window.getComputedStyle(el).whiteSpace,
                isSingleLine: rect.height < 30
            };
        });
    }''')
    print(f"P5 Measurement: {json.dumps(p5_data, indent=2)}")

    # 5. Measure Computed Fonts
    font_data = await page.evaluate('''() => {
        const h1 = document.querySelector('h1, .st-key-practice_filter_card h3, .st-key-practice_statement_card h3');
        const body = document.querySelector('.st-key-practice_statement_card p, body');
        const code = document.querySelector('.signature-display-box code, pre code');
        return {
            headingFont: h1 ? window.getComputedStyle(h1).fontFamily : null,
            bodyFont: body ? window.getComputedStyle(body).fontFamily : null,
            codeFont: code ? window.getComputedStyle(code).fontFamily : null
        };
    }''')
    print(f"Fonts Measurement: {json.dumps(font_data, indent=2)}")

    return {
        "p1": p1_data,
        "p3": p3_data,
        "p4": p4_data,
        "p5": p5_data,
        "fonts": font_data
    }

async def measure_p2_longest_problem(page, res_str):
    print(f"\n--- Measuring P2 on log-timestamp-filter at {res_str} ---")
    await page.goto("http://127.0.0.1:8501/?screen=practice&problem=log-timestamp-filter", wait_until="networkidle")
    await wait_for_editor(page)

    # Let Ace render fully
    await asyncio.sleep(2.0)

    p2_data = await page.evaluate('''() => {
        const iframe = document.querySelector('.st-key-practice_editor_card iframe');
        if (!iframe) return { error: "No iframe found" };
        const iframeRect = iframe.getBoundingClientRect();
        
        let aceData = null;
        try {
            const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
            const aceLine = innerDoc.querySelector('.ace_line');
            const hScrollBar = innerDoc.querySelector('.ace_scrollbar-h');
            const scroller = innerDoc.querySelector('.ace_scroller');
            const content = innerDoc.querySelector('.ace_content');
            
            aceData = {
                firstLineText: aceLine ? aceLine.textContent : null,
                hScrollVisible: hScrollBar ? (hScrollBar.style.display !== 'none' && hScrollBar.clientHeight > 0 && hScrollBar.scrollWidth > hScrollBar.clientWidth) : false,
                hScrollDisplay: hScrollBar ? hScrollBar.style.display : null,
                scrollerClientWidth: scroller ? scroller.clientWidth : null,
                scrollerScrollWidth: scroller ? scroller.scrollWidth : null,
                contentWidth: content ? content.clientWidth : null,
                hasOverflow: scroller ? scroller.scrollWidth > scroller.clientWidth + 2 : false
            };
        } catch(e) {
            aceData = { error: "Cross-origin or access error: " + e.message };
        }

        return {
            selector: ".st-key-practice_editor_card iframe -> .ace_line",
            elementDescription: "First line of starter code inside Ace Editor iframe",
            iframeWidth: Math.round(iframeRect.width),
            iframeHeight: Math.round(iframeRect.height),
            aceDetails: aceData
        };
    }''')
    print(f"P2 Measurement: {json.dumps(p2_data, indent=2)}")
    return p2_data

def create_side_by_side(real_path, mockup_path, out_path, label="PRACTICE ARENA"):
    img_real = Image.open(real_path)
    img_mockup = Image.open(mockup_path)
    
    # Height match
    target_height = max(img_real.height, img_mockup.height)
    
    # Create combined image with header
    header_height = 60
    comb_width = img_mockup.width + img_real.width + 20
    comb_height = target_height + header_height
    
    combined = Image.new("RGB", (comb_width, comb_height), (245, 243, 238))
    
    # Paste mockup on left, real on right
    combined.paste(img_mockup, (0, header_height))
    combined.paste(img_real, (img_mockup.width + 20, header_height))
    
    combined.save(out_path)
    print(f"Saved side-by-side comparison to {out_path}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        results = {}

        for width, height in RESOLUTIONS:
            res_str = f"{width}x{height}"
            await page.set_viewport_size({"width": width, "height": height})
            
            # --- Default Practice Screen (two-sum) ---
            await page.goto("http://127.0.0.1:8501/?screen=practice", wait_until="networkidle")
            await wait_for_editor(page)

            # Viewport screenshot
            vp_path = os.path.join(DOCS_DIR, f"practice_viewport_{res_str}.png")
            await page.screenshot(path=vp_path, full_page=False)
            print(f"Saved {vp_path}")
            
            # Full-page screenshot
            fp_path = os.path.join(DOCS_DIR, f"practice_fullpage_{res_str}.png")
            await page.screenshot(path=fp_path, full_page=True)
            print(f"Saved {fp_path}")
            
            # Close-up of statement card & signature box
            stmt_el = await page.query_selector('.st-key-practice_statement_card')
            if stmt_el:
                stmt_path = os.path.join(DOCS_DIR, f"practice_statement_closeup_{res_str}.png")
                await stmt_el.screenshot(path=stmt_path)
                print(f"Saved {stmt_path}")

            # Measurements
            measurements = await measure_practice(page, res_str)
            
            # --- Longest Problem (log-timestamp-filter) ---
            p2_measurements = await measure_p2_longest_problem(page, res_str)
            
            # Screenshot of editor with longest signature
            editor_el = await page.query_selector('.st-key-practice_editor_card')
            if editor_el:
                longest_path = os.path.join(DOCS_DIR, f"practice_longest_signature_{res_str}.png")
                await editor_el.screenshot(path=longest_path)
                print(f"Saved {longest_path}")

            measurements["p2"] = p2_measurements
            results[res_str] = measurements

            # Also capture Mockup for comparison
            mockup_page = await context.new_page()
            await mockup_page.set_viewport_size({"width": width, "height": height})
            await mockup_page.goto("http://127.0.0.1:8000/practice.html", wait_until="networkidle")
            mockup_path = os.path.join(DOCS_DIR, f"practice_mockup_{res_str}.png")
            await mockup_page.screenshot(path=mockup_path, full_page=False)
            await mockup_page.close()

            # Side-by-side comparison
            comp_path = os.path.join(DOCS_DIR, f"practice_comparison_{res_str}.png")
            create_side_by_side(vp_path, mockup_path, comp_path)

        # Mirror docs screenshots to artifact directory
        for f in os.listdir(DOCS_DIR):
            if f.startswith("practice_"):
                src = os.path.join(DOCS_DIR, f)
                dst = os.path.join(ARTIFACTS_DIR, f)
                with open(src, "rb") as sf, open(dst, "wb") as df:
                    df.write(sf.read())
        print(f"Mirrored practice screenshots to {ARTIFACTS_DIR}")

        # Save measurements JSON
        json_path = os.path.join(DOCS_DIR, "practice_round2_measurements.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Saved {json_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
