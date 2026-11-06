import asyncio, json, urllib.request, websockets, subprocess, tempfile, time

async def test():
    profile_dir = tempfile.mkdtemp()
    proc = subprocess.Popen([
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        '--headless=new',
        '--remote-debugging-port=9298',
        f'--user-data-dir={profile_dir}',
    ])
    time.sleep(1.5)
    with urllib.request.urlopen('http://127.0.0.1:9298/json/list') as r:
        tabs = json.loads(r.read().decode())
        page = [t for t in tabs if t.get('type') == 'page'][0]
        ws_url = page['webSocketDebuggerUrl']
    
    async with websockets.connect(ws_url) as ws:
        async def send(method, params=None):
            msg = {'id': 1, 'method': method, 'params': params or {}}
            await ws.send(json.dumps(msg))
            while True:
                d = json.loads(await ws.recv())
                if d.get('id') == 1:
                    return d.get('result', {})

        await send('Page.enable')
        await send('Runtime.enable')
        await send('Page.navigate', {'url': 'http://127.0.0.1:8501/?screen=mock&mock_state=running'})
        await asyncio.sleep(2.5)
        t1 = await send('Runtime.evaluate', {'expression': "document.querySelector('.mock-timer-pill')?.innerText", 'returnByValue': True})
        val1 = t1.get('result', {}).get('value')
        print(f"T1 timer: {val1}")
        
        await asyncio.sleep(11.0)
        t2 = await send('Runtime.evaluate', {'expression': "document.querySelector('.mock-timer-pill')?.innerText", 'returnByValue': True})
        val2 = t2.get('result', {}).get('value')
        print(f"T2 timer: {val2}")
    proc.kill()

asyncio.run(test())

