import asyncio, json, urllib.request, websockets, subprocess, time, tempfile

profile_dir = tempfile.mkdtemp()
proc = subprocess.Popen([
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9286',
    f'--user-data-dir={profile_dir}',
])
time.sleep(1.5)
try:
    with urllib.request.urlopen('http://127.0.0.1:9286/json/list') as resp:
        ws_url = json.loads(resp.read().decode())[0]['webSocketDebuggerUrl']

    async def test():
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': 'http://127.0.0.1:8501/?screen=practice'}}))
            for i in range(20):
                await asyncio.sleep(0.5)
                await ws.send(json.dumps({'id': 100 + i, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.readyState', 'returnByValue': True}}))
                res = json.loads(await ws.recv())
                while res.get('id') != 100 + i:
                    res = json.loads(await ws.recv())
                print('Ready state:', res['result']['result']['value'])
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': '({url: location.href, title: document.title, htmlLen: document.documentElement.outerHTML.length})', 'returnByValue': True}}))
            res = json.loads(await ws.recv())
            while res.get('id') != 2:
                res = json.loads(await ws.recv())
            print('Info:', res['result']['result']['value'])

    asyncio.run(test())
finally:
    proc.terminate()
