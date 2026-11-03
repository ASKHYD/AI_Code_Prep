// Minimal CDP screenshot script using Node.js built-in fetch and WebSocket
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

async function capture(url, outputPath, waitMs = 4000) {
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
        await send('Page.navigate', { url });
        await new Promise(r => setTimeout(r, waitMs));
        const result = await send('Page.captureScreenshot', { format: 'png' });
        if (result && result.result && result.result.data) {
          fs.writeFileSync(outputPath, Buffer.from(result.result.data, 'base64'));
          console.log(`Saved screenshot to ${outputPath} (${result.result.data.length} bytes base64)`);
        } else {
          console.error("No screenshot data in response:", result);
        }
        ws.close();
        resolve();
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

const args = process.argv.slice(2);
const url = args[0] || 'http://127.0.0.1:8501/?screen=home';
const out = args[1] || 'E:/resume_project/docs/screenshots/01_home_screen.png';
const waitMs = parseInt(args[2] || '4000', 10);

capture(url, out, waitMs).catch(err => {
  console.error("Capture error:", err);
  process.exit(1);
});
