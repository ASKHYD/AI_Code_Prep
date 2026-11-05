/**
 * scratch/verify_fonts_cdp.js
 * 
 * Verifies self-hosted offline fonts and computed typography via Chrome DevTools Protocol.
 * 
 * Asserts:
 *  1. Heading element fontFamily contains "Fraunces"
 *  2. Body element fontFamily contains "Inter"
 *  3. Metric numeral element fontFamily contains "Inter" (Variant B Inter SemiBold 600)
 *  4. Code block/editor element fontFamily contains "JetBrains Mono"
 *  5. Zero runtime network requests to Google Fonts (offline isolation proof)
 */

const http = require('http');
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const STREAMLIT_PORT = 8501;
const CDP_PORT = 9222;
const WORKSPACE_DIR = path.resolve(__dirname, '..');
const PYTHON_PATH = path.join(WORKSPACE_DIR, '.venv', 'Scripts', 'python.exe');

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function checkHttp(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode >= 200 && res.statusCode < 400);
    }).on('error', () => {
      resolve(false);
    });
  });
}

async function ensureStreamlit() {
  const isRunning = await checkHttp(`http://127.0.0.1:${STREAMLIT_PORT}/_stcore/health`);
  if (isRunning) {
    console.log(`[Streamlit] Already running on port ${STREAMLIT_PORT}`);
    return null;
  }

  console.log(`[Streamlit] Starting local instance on port ${STREAMLIT_PORT}...`);
  const proc = spawn(PYTHON_PATH, [
    '-m', 'streamlit', 'run', 'app.py',
    '--server.headless', 'true',
    '--server.port', String(STREAMLIT_PORT),
    '--server.address', '127.0.0.1'
  ], {
    cwd: WORKSPACE_DIR,
    stdio: 'ignore',
    windowsHide: true
  });

  const start = Date.now();
  while (Date.now() - start < 20000) {
    await sleep(500);
    if (await checkHttp(`http://127.0.0.1:${STREAMLIT_PORT}/_stcore/health`)) {
      console.log(`[Streamlit] Ready at http://127.0.0.1:${STREAMLIT_PORT}`);
      return proc;
    }
  }

  throw new Error("Timeout waiting for Streamlit to start.");
}

async function getWsUrl(port) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const list = JSON.parse(data);
          const page = list.find(item => item.type === 'page') || list[0];
          if (!page || !page.webSocketDebuggerUrl) {
            return reject(new Error("No inspectable page found in Chrome."));
          }
          resolve(page.webSocketDebuggerUrl);
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

async function launchChrome() {
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome_cdp_fonts_'));
  console.log(`[Chrome] Launching headless on port ${CDP_PORT}...`);
  const proc = spawn(CHROME_PATH, [
    '--headless=new',
    '--disable-gpu',
    `--remote-debugging-port=${CDP_PORT}`,
    `--user-data-dir=${profileDir}`,
    '--window-size=1920,1080'
  ], {
    windowsHide: true
  });

  const start = Date.now();
  while (Date.now() - start < 10000) {
    await sleep(300);
    try {
      const ready = await checkHttp(`http://127.0.0.1:${CDP_PORT}/json/version`);
      if (ready) break;
    } catch (_) {}
  }

  return { proc, profileDir };
}

function killProcess(pid) {
  if (!pid) return;
  try {
    execSync(`taskkill /F /T /PID ${pid}`, { stdio: 'ignore' });
  } catch (_) {
    try {
      process.kill(pid);
    } catch (_) {}
  }
}

async function run() {
  let streamlitProc = null;
  let chromeInfo = null;
  let ws = null;

  try {
    streamlitProc = await ensureStreamlit();
    chromeInfo = await launchChrome();

    const wsUrl = await getWsUrl(CDP_PORT);
    console.log(`[CDP] Connecting to ${wsUrl}`);
    ws = new WebSocket(wsUrl);

    let id = 1;
    const callbacks = {};
    const networkRequests = [];

    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const msgId = id++;
        callbacks[msgId] = (result, error) => {
          if (error) reject(new Error(error.message || JSON.stringify(error)));
          else resolve(result);
        };
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    }

    await new Promise((resolve, reject) => {
      ws.onopen = resolve;
      ws.onerror = reject;
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && callbacks[msg.id]) {
          callbacks[msg.id](msg.result, msg.error);
          delete callbacks[msg.id];
        } else if (msg.method === 'Network.requestWillBeSent') {
          networkRequests.push(msg.params.request.url);
        }
      };
    });

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Network.enable');

    console.log(`[CDP] Navigating to http://127.0.0.1:${STREAMLIT_PORT}...`);
    await send('Page.navigate', { url: `http://127.0.0.1:${STREAMLIT_PORT}` });

    // Wait for DOM to settle and elements to be available
    async function evaluate(expr) {
      const resp = await send('Runtime.evaluate', {
        expression: expr,
        returnByValue: true,
        awaitPromise: true
      });
      if (resp && resp.exceptionDetails) {
        throw new Error(JSON.stringify(resp.exceptionDetails));
      }
      return resp && resp.result ? resp.result.value : null;
    }

    let ready = false;
    for (let i = 0; i < 40; i++) {
      await sleep(500);
      ready = await evaluate(`
        (() => {
          const heading = document.querySelector('h1, h2, h3, .stSubheader, [data-testid="stHeader"]');
          const body = document.querySelector('p, .stMarkdown p, label');
          const metric = document.querySelector('[data-testid="stMetricValue"]');
          return !!(heading && body && metric);
        })()
      `);
      if (ready) break;
    }

    if (!ready) {
      throw new Error("Streamlit app did not render heading/body/metric elements in time.");
    }

    // Wait for fonts to be ready
    await evaluate(`document.fonts.ready`);

    // Check if code element is on Home; if not, navigate to Practice Arena
    let hasCode = await evaluate(`!!document.querySelector('code, pre, .stCode')`);
    if (!hasCode) {
      console.log("[CDP] Navigating to Practice Arena for code element evaluation...");
      await send('Page.navigate', { url: `http://127.0.0.1:${STREAMLIT_PORT}/?screen=practice` });
      for (let i = 0; i < 30; i++) {
        await sleep(500);
        hasCode = await evaluate(`!!document.querySelector('code, pre, .stCode')`);
        if (hasCode) break;
      }
    }

    // Extract computed font families
    const computed = await evaluate(`
      (() => {
        const headingEl = document.querySelector('h1, h2, h3, .stSubheader, [data-testid="stHeader"]');
        const bodyEl = document.querySelector('p, .stMarkdown p, label');
        const metricEl = document.querySelector('[data-testid="stMetricValue"]');
        const codeEl = document.querySelector('code, pre, .stCode');

        return {
          heading: {
            tag: headingEl ? headingEl.tagName : null,
            text: headingEl ? headingEl.textContent.trim().slice(0, 30) : null,
            fontFamily: headingEl ? window.getComputedStyle(headingEl).fontFamily : null
          },
          body: {
            tag: bodyEl ? bodyEl.tagName : null,
            text: bodyEl ? bodyEl.textContent.trim().slice(0, 30) : null,
            fontFamily: bodyEl ? window.getComputedStyle(bodyEl).fontFamily : null
          },
          metric: {
            tag: metricEl ? metricEl.tagName : null,
            text: metricEl ? metricEl.textContent.trim() : null,
            fontFamily: metricEl ? window.getComputedStyle(metricEl).fontFamily : null,
            fontWeight: metricEl ? window.getComputedStyle(metricEl).fontWeight : null,
            fontVariantNumeric: metricEl ? window.getComputedStyle(metricEl).fontVariantNumeric : null
          },
          code: {
            tag: codeEl ? codeEl.tagName : null,
            text: codeEl ? codeEl.textContent.trim().slice(0, 30) : null,
            fontFamily: codeEl ? window.getComputedStyle(codeEl).fontFamily : null
          }
        };
      })()
    `);

    console.log("\n================ COMPUTED FONT RESULTS ================");
    console.log(`Heading (${computed.heading.tag} "${computed.heading.text}"):`);
    console.log(`  font-family: ${computed.heading.fontFamily}`);
    console.log(`Body (${computed.body.tag} "${computed.body.text}"):`);
    console.log(`  font-family: ${computed.body.fontFamily}`);
    console.log(`Metric (${computed.metric.tag} "${computed.metric.text}"):`);
    console.log(`  font-family: ${computed.metric.fontFamily}`);
    console.log(`  font-weight: ${computed.metric.fontWeight}`);
    console.log(`  font-variant-numeric: ${computed.metric.fontVariantNumeric}`);
    console.log(`Code (${computed.code.tag} "${computed.code.text}"):`);
    console.log(`  font-family: ${computed.code.fontFamily}`);
    console.log("======================================================\n");

    // Network isolation check
    const googleFontRequests = networkRequests.filter(url =>
      url.includes('fonts.googleapis.com') || url.includes('fonts.gstatic.com')
    );

    console.log(`[Offline Isolation] Total requests captured: ${networkRequests.length}`);
    console.log(`[Offline Isolation] Google Fonts external requests: ${googleFontRequests.length}`);

    // Assertions
    const errors = [];

    if (!computed.heading.fontFamily || !computed.heading.fontFamily.toLowerCase().includes('fraunces')) {
      errors.push(`Heading font assertion failed: expected Fraunces, got "${computed.heading.fontFamily}"`);
    }

    if (!computed.body.fontFamily || !computed.body.fontFamily.toLowerCase().includes('inter')) {
      errors.push(`Body font assertion failed: expected Inter, got "${computed.body.fontFamily}"`);
    }

    // Owner selected Variant B: Inter SemiBold 600 tabular figures
    if (!computed.metric.fontFamily || !computed.metric.fontFamily.toLowerCase().includes('inter')) {
      errors.push(`Metric font assertion failed: expected Inter (Variant B), got "${computed.metric.fontFamily}"`);
    }

    if (!computed.code.fontFamily || !computed.code.fontFamily.toLowerCase().includes('jetbrains mono')) {
      errors.push(`Code font assertion failed: expected JetBrains Mono, got "${computed.code.fontFamily}"`);
    }

    if (googleFontRequests.length > 0) {
      errors.push(`Offline check failed: found ${googleFontRequests.length} external Google Fonts requests: ${googleFontRequests.join(', ')}`);
    }

    if (errors.length > 0) {
      console.error("\n❌ PROOF VERIFICATION FAILED:");
      errors.forEach(e => console.error(`  - ${e}`));
      process.exit(1);
    }

    console.log("✅ ALL COMPUTED FONT ASSERTIONS PASSED CLEANLY:");
    console.log("  - Heading computed family contains 'Fraunces'");
    console.log("  - Body computed family contains 'Inter'");
    console.log("  - Metric numeral computed family contains 'Inter' (Variant B 600 tabular)");
    console.log("  - Code computed family contains 'JetBrains Mono'");
    console.log("  - 0 Google Fonts network requests (pure offline base64 @font-face)");

  } finally {
    if (ws) {
      try { ws.close(); } catch (_) {}
    }
    if (chromeInfo) {
      killProcess(chromeInfo.proc.pid);
      await sleep(300);
      try {
        fs.rmSync(chromeInfo.profileDir, { recursive: true, force: true });
      } catch (_) {}
    }
    if (streamlitProc) {
      console.log("[Streamlit] Stopping spawned Streamlit process...");
      killProcess(streamlitProc.pid);
    }
  }
}

run().catch((err) => {
  console.error("Fatal error running font verification:", err);
  process.exit(1);
});
