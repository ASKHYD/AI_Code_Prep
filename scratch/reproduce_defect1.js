
const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');

async function main() {
    // 1. Launch Chrome
    const chrome = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
        '--headless=new',
        '--remote-debugging-port=9222',
        '--disable-gpu',
        '--no-sandbox',
        '--window-size=1920,1080'
    ]);
    await new Promise(r => setTimeout(r, 1500));

    const targets = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9222/json', (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
    });

    const WebSocket = require('ws');
    const ws = new WebSocket(targets[0].webSocketDebuggerUrl);
    await new Promise(r => ws.on('open', r));

    let id = 1;
    function send(method, params = {}) {
        return new Promise((resolve) => {
            const msgId = id++;
            const handler = (data) => {
                const res = JSON.parse(data);
                if (res.id === msgId) {
                    ws.off('message', handler);
                    resolve(res.result);
                }
            };
            ws.on('message', handler);
            ws.send(JSON.stringify({ id: msgId, method, params }));
        });
    }

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', {
        width: 1920,
        height: 1080,
        deviceScaleFactor: 1,
        mobile: false
    });

    // Navigate to Mock Interview
    console.log('Navigating to Mock Interview...');
    await send('Page.navigate', { url: 'http://127.0.0.1:8501/?screen=mock' });
    await new Promise(r => setTimeout(r, 4000));

    // Click "Start 45-Minute Mock Interview" if unstarted
    console.log('Clicking Start Mock if available...');
    await send('Runtime.evaluate', {
        expression: `
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start 45-Minute Mock'));
            if (btn) btn.click();
        `
    });
    await new Promise(r => setTimeout(r, 3000));

    // Now click "End Interview Early" without submitting anything!
    console.log('Clicking End Interview Early...');
    await send('Runtime.evaluate', {
        expression: `
            const endBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('End Interview Early'));
            if (endBtn) endBtn.click();
        `
    });
    await new Promise(r => setTimeout(r, 4000));

    // Inspect scorecard content
    const scorecardText = await send('Runtime.evaluate', {
        expression: `
            const sc = document.querySelector('.st-key-mock_scorecard_card');
            sc ? sc.innerText : 'NO SCORECARD FOUND'
        `
    });
    console.log('SCORECARD RENDERED TEXT:');
    console.log(scorecardText.result.value);

    // Capture screenshot
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync('scratch/defect1_reproduced.png', Buffer.from(shot.data, 'base64'));
    console.log('Screenshot saved to scratch/defect1_reproduced.png');

    ws.close();
    chrome.kill();
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
