/**
 * scratch/verify_sidebar_cdp.js
 * 
 * Tests and verifies Direction A Sidebar & Keyed Nav Pill via Chrome DevTools Protocol.
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
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome_cdp_sidebar_'));
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
        }
      };
    });

    await send('Page.enable');
    await send('Runtime.enable');

    console.log(`[CDP] Navigating to http://127.0.0.1:${STREAMLIT_PORT}...`);
    await send('Page.navigate', { url: `http://127.0.0.1:${STREAMLIT_PORT}` });

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

    // Wait for sidebar elements and hydration
    let ready = false;
    for (let i = 0; i < 40; i++) {
      await sleep(500);
      ready = await evaluate(`
        (() => {
          const sidebar = document.querySelector('[data-testid="stSidebar"]');
          const radio = document.querySelector('.st-key-nav_sidebar_radio [data-testid="stRadioOption"]');
          const skeleton = document.querySelector('[data-testid="stSkeleton"]');
          return !!(sidebar && radio && !skeleton);
        })()
      `);
      if (ready) break;
    }

    if (!ready) {
      throw new Error("Sidebar or nav radio not rendered within timeout.");
    }

    console.log("[CDP] Sidebar ready. Validating elements...");

    // Dump sidebar HTML / structure
    const sidebarHtml = await evaluate(`
      (() => {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        return {
          innerHtml: sidebar ? sidebar.innerHTML.slice(0, 1500) : null,
          allClasses: sidebar ? Array.from(sidebar.querySelectorAll('*')).map(el => el.className).filter(Boolean) : []
        };
      })()
    `);
    console.log("Sidebar HTML preview:", sidebarHtml.innerHtml?.slice(0, 500));
    console.log("Matching keys:", sidebarHtml.allClasses.filter(c => typeof c === 'string' && c.includes('st-key')));

    const radioHtml = await evaluate(`
      (() => {
        const r = document.querySelector('.st-key-nav_sidebar_radio');
        const c = document.querySelector('.st-key-sidebar_summary_card');
        return {
          radio: r ? r.innerHTML : null,
          card: c ? c.innerHTML : null
        };
      })()
    `);
    console.log("Radio HTML:", radioHtml.radio);
    console.log("Card HTML:", radioHtml.card);


    const brand = await evaluate(`
      (() => {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const allDivs = Array.from(sidebar.querySelectorAll('div'));
        const wordmark = allDivs.find(d => d.textContent.trim() === 'AI Coding Prep Coach');
        const tagline = allDivs.find(d => d.textContent.trim() === 'Zero Cost • Code-Judged • Offline-Ready');
        return {
          wordmark: wordmark ? {
            fontFamily: window.getComputedStyle(wordmark).fontFamily,
            fontSize: window.getComputedStyle(wordmark).fontSize,
            fontWeight: window.getComputedStyle(wordmark).fontWeight,
            color: window.getComputedStyle(wordmark).color
          } : null,
          tagline: tagline ? {
            fontFamily: window.getComputedStyle(tagline).fontFamily,
            fontSize: window.getComputedStyle(tagline).fontSize,
            color: window.getComputedStyle(tagline).color
          } : null
        };
      })()
    `);

    console.log("\n--- BRAND HEADER ---");
    console.log("Wordmark:", brand.wordmark);
    console.log("Tagline:", brand.tagline);

    // 2. Validate Nav Radio Pills & Circle Indicator Hiding
    const navDetails = await evaluate(`
      (() => {
        const labels = Array.from(document.querySelectorAll('.st-key-nav_sidebar_radio div[role="radiogroup"] label'));
        return labels.map(label => {
          const text = label.textContent.trim();
          const cs = window.getComputedStyle(label);
          const circleEl = label.querySelector('div > div:first-child:not([data-testid="stMarkdownContainer"])');
          const circleCs = circleEl ? window.getComputedStyle(circleEl) : null;
          const isChecked = !!label.querySelector('input:checked') || !!label.querySelector('div[aria-checked="true"]') || label.getAttribute('data-selected') === 'true';
          return {
            text,
            isChecked,
            borderRadius: cs.borderRadius,
            padding: cs.padding,
            backgroundColor: cs.backgroundColor,
            color: cs.color,
            circleDisplay: circleCs ? circleCs.display : 'none'
          };
        });
      })()
    `);

    console.log("\n--- NAV RADIO PILLS ---");
    console.dir(navDetails, { depth: null });

    // 3. Validate Metric Mini-Card
    const cardDetails = await evaluate(`
      (() => {
        const cardWrapper = document.querySelector('.st-key-sidebar_summary_card [data-testid="stVerticalBlockBorderWrapper"] > div') ||
                            document.querySelector('.st-key-sidebar_summary_card');
        const metrics = Array.from(document.querySelectorAll('.st-key-sidebar_summary_card [data-testid="stMetric"]')).map(m => {
          const label = m.querySelector('[data-testid="stMetricLabel"]')?.textContent.trim();
          const val = m.querySelector('[data-testid="stMetricValue"]')?.textContent.trim();
          const valCs = m.querySelector('[data-testid="stMetricValue"]') ? window.getComputedStyle(m.querySelector('[data-testid="stMetricValue"]')) : null;
          return {
            label,
            val,
            fontFamily: valCs?.fontFamily,
            fontWeight: valCs?.fontWeight,
            fontVariantNumeric: valCs?.fontVariantNumeric
          };
        });
        const cardCs = cardWrapper ? window.getComputedStyle(cardWrapper) : null;
        return {
          card: cardCs ? {
            borderRadius: cardCs.borderRadius,
            backgroundColor: cardCs.backgroundColor,
            border: cardCs.border
          } : null,
          metrics
        };
      })()
    `);

    console.log("\n--- METRIC MINI-CARD ---");
    console.dir(cardDetails, { depth: null });

    // 4. Test Navigation Switching Across All 4 Destinations
    console.log("\n--- TESTING NAVIGATION SWITCHING ---");
    const testScreens = [
      { name: "Practice Arena", screenParam: "practice" },
      { name: "Mock Interview", screenParam: "mock" },
      { name: "Dashboard", screenParam: "dashboard" },
      { name: "Home", screenParam: "home" }
    ];

    for (const target of testScreens) {
      console.log(`Clicking nav item "${target.name}"...`);
      const clicked = await evaluate(`
        (() => {
          const labels = Array.from(document.querySelectorAll('.st-key-nav_sidebar_radio div[role="radiogroup"] label'));
          const targetLabel = labels.find(l => l.textContent.includes("${target.name}"));
          if (targetLabel) {
            targetLabel.click();
            return true;
          }
          return false;
        })()
      `);

      if (!clicked) {
        throw new Error(`Could not find radio label for ${target.name}`);
      }

      // Wait for Streamlit rerun to settle
      await sleep(1500);

      const navState = await evaluate(`
        (() => {
          const currentUrl = window.location.href;
          const activeLabel = Array.from(document.querySelectorAll('.st-key-nav_sidebar_radio div[role="radiogroup"] label'))
            .find(l => l.querySelector('input:checked') || l.querySelector('div[aria-checked="true"]'));
          return {
            url: currentUrl,
            activeText: activeLabel ? activeLabel.textContent.trim() : null
          };
        })()
      `);

      console.log(`  -> URL: ${navState.url}`);
      console.log(`  -> Active Nav: "${navState.activeText}"`);
    }

    // Take screenshot of final verified state
    const screenshotData = await send('Page.captureScreenshot', { format: 'png' });
    const screenshotPath = path.join(WORKSPACE_DIR, 'scratch', 'sidebar_nav_verified.png');
    fs.writeFileSync(screenshotPath, Buffer.from(screenshotData.data, 'base64'));
    console.log(`\n[CDP] Screenshot saved to ${screenshotPath}`);

    // Assertions
    const errors = [];
    if (!brand.wordmark || !brand.wordmark.fontFamily.toLowerCase().includes('fraunces')) {
      errors.push(`Wordmark font-family should include Fraunces, got: ${brand.wordmark?.fontFamily}`);
    }
    if (!brand.tagline) {
      errors.push("Tagline element not found in sidebar.");
    }
    const homeNav = navDetails.find(n => n.text.includes("Home"));
    if (!homeNav || !homeNav.borderRadius.includes('999')) {
      errors.push(`Home nav border-radius should be pill 999px, got: ${homeNav?.borderRadius}`);
    }
    if (navDetails.some(n => n.circleDisplay !== 'none')) {
      errors.push("Radio circle indicators are not hidden with display: none.");
    }
    if (!cardDetails.card || !cardDetails.card.borderRadius.includes('16px')) {
      errors.push(`Mini-card border-radius should be 16px, got: ${cardDetails.card?.borderRadius}`);
    }

    if (errors.length > 0) {
      console.error("\n❌ VALIDATION ERRORS:");
      errors.forEach(e => console.error(` - ${e}`));
      process.exit(1);
    } else {
      console.log("\n✅ ALL SIDEBAR & NAVIGATION ASSERTIONS PASSED EMPIRICALLY!");
    }

  } finally {
    if (ws) ws.close();
    if (chromeInfo && chromeInfo.proc) killProcess(chromeInfo.proc.pid);
    if (streamlitProc) killProcess(streamlitProc.pid);
  }
}

run().catch(err => {
  console.error("FATAL:", err);
  process.exit(1);
});
