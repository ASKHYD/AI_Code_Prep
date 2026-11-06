import asyncio
import json
import urllib.request
import websockets
import tempfile
import subprocess
import time

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
CDP_PORT = 9299

async def main():
    profile_dir = tempfile.mkdtemp(prefix='chrome_layout_')
    chrome_proc = subprocess.Popen([
        CHROME_PATH, '--headless=new', '--disable-gpu', '--disable-extensions',
        f'--remote-debugging-port={CDP_PORT}', f'--user-data-dir={profile_dir}',
        '--window-size=1450,900'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.5)
        with urllib.request.urlopen(f'http://127.0.0.1:{CDP_PORT}/json/list') as resp:
            tabs = json.loads(resp.read().decode())
            ws_url = [t for t in tabs if t.get('type') == 'page'][0]['webSocketDebuggerUrl']
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            async def send(method, params=None):
                await ws.send(json.dumps({'id': 1, 'method': method, 'params': params or {}}))
                while True:
                    data = json.loads(await ws.recv())
                    if data.get('id') == 1:
                        return data.get('result', {})

            await send('Page.enable')
            await send('Emulation.setDeviceMetricsOverride', {'width': 1450, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
            await send('Page.navigate', {'url': 'http://127.0.0.1:8501/?screen=practice'})
            await asyncio.sleep(3.0)
            js = """
            (() => {
                const docWidth = document.documentElement.clientWidth;
                const docScroll = document.documentElement.scrollWidth;
                const prevBtn = document.querySelector('.st-key-btn_picker_prev button');
                const nextBtn = document.querySelector('.st-key-btn_picker_next button');
                const stripRight = document.querySelector('.editor-strip-right');
                const anchors = document.querySelectorAll('[data-testid="stHeaderActionElements"], [data-testid="stHeadingAnchor"], a.anchor-link');
                return {
                    docWidth, docScroll, overflow: docScroll > docWidth,
                    prevBtn: prevBtn ? { text: prevBtn.textContent.trim(), clientWidth: prevBtn.clientWidth, scrollWidth: prevBtn.scrollWidth, noClip: prevBtn.scrollWidth <= prevBtn.clientWidth } : null,
                    nextBtn: nextBtn ? { text: nextBtn.textContent.trim(), clientWidth: nextBtn.clientWidth, scrollWidth: nextBtn.scrollWidth, noClip: nextBtn.scrollWidth <= nextBtn.clientWidth } : null,
                    stripRight: stripRight ? { text: stripRight.textContent.trim(), clientWidth: stripRight.clientWidth, scrollWidth: stripRight.scrollWidth } : null,
                    anchorsVisible: Array.from(anchors).filter(a => a.offsetParent !== null).length
                };
            })()
            """
            res = await send('Runtime.evaluate', {'expression': js, 'returnByValue': True})
            print(json.dumps(res.get('result', {}).get('value', {}), indent=2))
    finally:
        chrome_proc.terminate()

asyncio.run(main())

