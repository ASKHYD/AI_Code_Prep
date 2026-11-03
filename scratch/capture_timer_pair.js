const fs = require('fs');
const http = require('http');

async function getWsUrl(port) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const list = JSON.parse(data);
          const page = list.find(item => item.type === 'page') || list[0];
          resolve(page.webSocketDebuggerUrl);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function capturePair() {
  const wsUrl = await getWsUrl(9222);
  const ws = new WebSocket(wsUrl);

  return new Promise((resolve, reject) => {
    let id = 1;
    const callbacks = {};

    function send(method, params = {}) {
      return new Promise((res) => {
        const msgId = id++;
        callbacks[msgId] = res;
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    }

    ws.onopen = async () => {
      try {
        await send('Page.enable');
        console.log("Navigating to mock interview session...");
        await send('Page.navigate', { url: 'http://127.0.0.1:8501/?screen=mock&mock_state=running' });
        
        // Wait 4 seconds for initial render
        await new Promise(r => setTimeout(r, 4000));
        
        // Capture T1
        const t1_stamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        console.log(`Taking Screenshot T1 at wall-clock: ${t1_stamp}`);
        const res1 = await send('Page.captureScreenshot', { format: 'png' });
        fs.writeFileSync('E:/resume_project/docs/screenshots/03_mock_timer_t1.png', Buffer.from(res1.result.data, 'base64'));
        console.log("Saved 03_mock_timer_t1.png");

        // Wait 15 seconds while page stays open and timer ticks
        console.log("Waiting 15 seconds while timer ticks live...");
        await new Promise(r => setTimeout(r, 15000));

        // Capture T2
        const t2_stamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        console.log(`Taking Screenshot T2 at wall-clock: ${t2_stamp}`);
        const res2 = await send('Page.captureScreenshot', { format: 'png' });
        fs.writeFileSync('E:/resume_project/docs/screenshots/04_mock_timer_t2.png', Buffer.from(res2.result.data, 'base64'));
        console.log("Saved 04_mock_timer_t2.png");

        ws.close();
        resolve({ t1: t1_stamp, t2: t2_stamp });
      } catch (e) {
        ws.close();
        reject(e);
      }
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && callbacks[msg.id]) {
        callbacks[msg.id](msg);
        delete callbacks[msg.id];
      }
    };

    ws.onerror = reject;
  });
}

capturePair().then(({ t1, t2 }) => {
  console.log(`SUCCESS: T1 captured at ${t1}, T2 captured at ${t2}`);
}).catch(err => {
  console.error("Timer pair capture error:", err);
  process.exit(1);
});
