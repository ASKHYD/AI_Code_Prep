const http = require('http');

async function getWsUrl(port) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const list = JSON.parse(data);
        const page = list.find(item => item.type === 'page') || list[0];
        resolve(page.webSocketDebuggerUrl);
      });
    });
  });
}

async function inspect() {
  const wsUrl = await getWsUrl(9222);
  const ws = new WebSocket(wsUrl);

  let id = 1;
  const callbacks = {};
  function send(method, params = {}) {
    return new Promise(res => {
      const msgId = id++;
      callbacks[msgId] = res;
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  ws.onopen = async () => {
    await send('Runtime.enable');
    const evalRes = await send('Runtime.evaluate', {
      expression: 'document.querySelectorAll("iframe").length'
    });
    console.log("Iframes count:", evalRes.result.result.value);

    const textRes = await send('Runtime.evaluate', {
      expression: 'document.body.innerText.substring(0, 500)'
    });
    console.log("Body text:\n", textRes.result.result.value);

    ws.close();
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && callbacks[msg.id]) {
      callbacks[msg.id](msg);
      delete callbacks[msg.id];
    }
  };
}

inspect();
