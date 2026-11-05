const fs = require('fs');
const http = require('http');
const path = require('path');

async function getWsUrl(port = 9222) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const list = JSON.parse(data);
          const page = list.find(item => item.type === 'page') || list[0];
          if (!page) return reject(new Error("No page found in Chrome"));
          resolve(page.webSocketDebuggerUrl);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

const items = [
  { name: 'home_1600x1000.png', url: 'file:///E:/resume_project/mockups/home.html', width: 1600, height: 1000 },
  { name: 'home_1920x1080.png', url: 'file:///E:/resume_project/mockups/home.html', width: 1920, height: 1080 },
  { name: 'practice_1600x1000.png', url: 'file:///E:/resume_project/mockups/practice.html', width: 1600, height: 1000 },
  { name: 'practice_1920x1080.png', url: 'file:///E:/resume_project/mockups/practice.html', width: 1920, height: 1080 },
  { name: 'mock_1600x1000.png', url: 'file:///E:/resume_project/mockups/mock.html', width: 1600, height: 1000 },
  { name: 'mock_1920x1080.png', url: 'file:///E:/resume_project/mockups/mock.html', width: 1920, height: 1080 },
  { name: 'dashboard_1600x1000.png', url: 'file:///E:/resume_project/mockups/dashboard.html', width: 1600, height: 1000 },
  { name: 'dashboard_1920x1080.png', url: 'file:///E:/resume_project/mockups/dashboard.html', width: 1920, height: 1080 },
  { name: 'tokens_1600x1000.png', url: 'file:///E:/resume_project/mockups/tokens.html', width: 1600, height: 1000 },
  { name: 'tokens_1920x1080.png', url: 'file:///E:/resume_project/mockups/tokens.html', width: 1920, height: 1080 }
];

const docsDir = 'E:/resume_project/docs/screenshots/r3';
const brainDir = 'C:/Users/MS Computer/.gemini/antigravity/brain/93d59834-2449-4201-af32-3cbe9726591d/screenshots/r3';

if (!fs.existsSync(docsDir)) {
  fs.mkdirSync(docsDir, { recursive: true });
}
if (brainDir && !fs.existsSync(brainDir)) {
  try {
    fs.mkdirSync(brainDir, { recursive: true });
  } catch (e) {
    console.warn("Could not create brainDir:", e.message);
  }
}

async function run() {
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

        for (const item of items) {
          console.log(`Capturing ${item.name} (${item.width}x${item.height})...`);
          
          await send('Emulation.setDeviceMetricsOverride', {
            width: item.width,
            height: item.height,
            deviceScaleFactor: 1,
            mobile: false
          });

          await send('Page.navigate', { url: item.url });
          // Wait 2500ms for web fonts and layouts to settle
          await new Promise(r => setTimeout(r, 2500));

          const result = await send('Page.captureScreenshot', { format: 'png' });
          if (result && result.result && result.result.data) {
            const buf = Buffer.from(result.result.data, 'base64');
            const p1 = `${docsDir}/${item.name}`;
            fs.writeFileSync(p1, buf);
            if (brainDir && fs.existsSync(brainDir)) {
              const p2 = `${brainDir}/${item.name}`;
              fs.writeFileSync(p2, buf);
            }
            console.log(`Saved ${item.name} (${buf.length} bytes) to docs & brain`);
          } else {
            console.error(`Failed to capture ${item.name}:`, result);
          }
        }

        ws.close();
        resolve();
      } catch (err) {
        ws.close();
        reject(err);
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

run().then(() => {
  console.log("All 10 R3 screenshots captured successfully!");
  process.exit(0);
}).catch(err => {
  console.error("Fatal capture error:", err);
  process.exit(1);
});
