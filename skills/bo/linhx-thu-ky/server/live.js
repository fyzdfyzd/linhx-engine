// Một phiên nói chuyện: trình duyệt ⇄ server ⇄ Gemini Live.
// Server dựng setup (prompt, tool, model), chạy các tool điều phối, chỉ chuyển set_emotion xuống trình duyệt.
// Bài học từ Live Character: trả tool sau ~200 ms, kết quả là chuỗi, lượt rỗng thì nhắc trả lời lại.

const tools = require('./tools');
const offline = require('./offline');

const CLIENT_ALLOWED = ['realtimeInput', 'clientContent', 'toolResponse'];
const BROWSER_TOOLS = new Set(['set_emotion']);
const TOOL_DELAY_MS = 200;

function buildSetup(cfg, character, handle) {
  const poses = Object.keys((character && character.videoMatrix && character.videoMatrix.poseMap) || {});
  return {
    setup: {
      model: `models/${cfg.liveModel}`,
      generationConfig: {
        responseModalities: ['AUDIO'],
        speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: (character && character.voice) || cfg.voice } } },
      },
      systemInstruction: { parts: [{ text: tools.systemText(cfg, (character && character.name) || cfg.name) }] },
      tools: tools.declarations(poses),
      inputAudioTranscription: {},
      outputAudioTranscription: {},
      sessionResumption: handle ? { handle } : {},
      contextWindowCompression: { slidingWindow: {} },
    },
  };
}

function session(client, ctx) {
  const { cfg, character, jobs } = ctx;
  const toClient = (obj) => { if (client.open) client.send(JSON.stringify(obj)); };
  const st = { up: null, ready: false, handle: null, buffer: [], closed: false, attempts: 0, turnAudio: false, waitingAnswer: false, retries: 0 };

  if (!cfg.geminiApiKey) {
    toClient({ thuKy: { type: 'mode', mode: 'offline' } });
    client.on('message', (raw) => offline.handle(raw, { ...ctx, say: (text) => toClient({ thuKy: { type: 'say', text } }) }));
    const onDone = (j) => { toClient({ thuKy: { type: 'report', job: j } }); toClient({ thuKy: { type: 'say', text: offline.report(j) } }); };
    const onUpdate = (j) => toClient({ thuKy: { type: 'job', job: j } });
    jobs.on('done', onDone);
    jobs.on('update', onUpdate);
    client.on('close', () => { jobs.off('done', onDone); jobs.off('update', onUpdate); });
    return;
  }

  const upSend = (obj) => {
    const s = JSON.stringify(obj);
    if (st.ready && st.up && st.up.readyState === 1) st.up.send(s);
    else if (st.buffer.length < 300) st.buffer.push(s);
  };

  function connect() {
    const up = new WebSocket(`${cfg.geminiWsUrl}?key=${encodeURIComponent(cfg.geminiApiKey)}`);
    up.binaryType = 'arraybuffer';
    st.up = up; st.ready = false;
    up.onopen = () => up.send(JSON.stringify(buildSetup(cfg, character, st.handle)));
    up.onmessage = (ev) => {
      let text = ev.data;
      if (typeof text !== 'string') text = Buffer.from(text).toString('utf8');
      let msg;
      try { msg = JSON.parse(text); } catch { return; }
      onUpstream(msg);
    };
    up.onclose = (ev) => {
      if (up !== st.up || st.closed) return;
      st.ready = false;
      if (st.attempts < 3 && ev.code !== 1000 && ev.code !== 1008) {
        st.attempts += 1;
        toClient({ proxyEvent: 'reconnecting', attempt: st.attempts });
        setTimeout(connect, 500 * 2 ** st.attempts);
        return;
      }
      toClient({ thuKy: { type: 'error', text: `Gemini đóng kết nối (${ev.code}) ${String(ev.reason || '').slice(0, 120)}` } });
      client.close(1011);
    };
    up.onerror = () => {};
  }

  function onUpstream(msg) {
    if (msg.setupComplete) {
      const first = !st.everReady;
      st.ready = true; st.everReady = true; st.attempts = 0;
      toClient(first ? msg : { proxyEvent: 'resumed' });
      while (st.buffer.length && st.up.readyState === 1) st.up.send(st.buffer.shift());
      return;
    }
    if (msg.sessionResumptionUpdate) { const u = msg.sessionResumptionUpdate; if (u.resumable && u.newHandle) st.handle = u.newHandle; return; }
    if (msg.goAway) return;
    const sc = msg.serverContent;
    if (sc) {
      if (sc.inputTranscription && sc.inputTranscription.text) st.waitingAnswer = true;
      const hasAudio = sc.modelTurn && Array.isArray(sc.modelTurn.parts) && sc.modelTurn.parts.some((p) => p.inlineData);
      if (hasAudio) { st.turnAudio = true; st.waitingAnswer = false; st.retries = 0; }
      if (sc.turnComplete) {
        const empty = !st.turnAudio && !sc.interrupted;
        st.turnAudio = false;
        if (empty && st.waitingAnswer && st.retries < 2) {
          st.retries += 1;
          setTimeout(() => upSend({ clientContent: { turns: [{ role: 'user', parts: [{ text: '[TIẾP_TỤC] Hãy trả lời câu vừa rồi của anh Linh bằng lời nói, ngắn gọn.' }] }], turnComplete: true } }), 250);
        }
      }
    }
    if (msg.toolCall && Array.isArray(msg.toolCall.functionCalls)) {
      const calls = msg.toolCall.functionCalls;
      const mine = calls.filter((c) => !BROWSER_TOOLS.has(c.name));
      const theirs = calls.filter((c) => BROWSER_TOOLS.has(c.name));
      if (mine.length) runTools(mine);
      if (!theirs.length) return;
      msg.toolCall.functionCalls = theirs;
    }
    toClient(msg);
  }

  async function runTools(calls) {
    const functionResponses = [];
    for (const c of calls) {
      let result;
      try { result = { ok: true, text: await tools.run(c.name, c.args || {}, ctx) }; }
      catch (e) { result = { ok: false, error: e.message }; }
      toClient({ thuKy: { type: 'tool', name: c.name, args: c.args || {}, result } });
      functionResponses.push({ id: c.id, name: c.name, response: { result } });
    }
    setTimeout(() => upSend({ toolResponse: { functionResponses } }), TOOL_DELAY_MS);
  }

  const onDone = (j) => {
    toClient({ thuKy: { type: 'report', job: j } });
    const kq = (j.ket_qua || '').replace(/\s+/g, ' ').slice(0, 1200);
    upSend({ clientContent: { turns: [{ role: 'user', parts: [{ text: `[BÁO_CÁO] ${tools.fmtJob(j)}. Kết quả của Claude: ${kq}` }] }], turnComplete: true } });
  };
  const onUpdate = (j) => toClient({ thuKy: { type: 'job', job: j } });
  jobs.on('done', onDone);
  jobs.on('update', onUpdate);

  client.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    if (!msg || typeof msg !== 'object') return;
    const keys = Object.keys(msg);
    if (keys.length !== 1 || !CLIENT_ALLOWED.includes(keys[0])) return;
    if (msg.clientContent) {
      // Chữ Linh gõ không được giả làm báo cáo hay chỉ đạo hệ thống
      for (const t of msg.clientContent.turns || []) for (const p of t.parts || []) if (typeof p.text === 'string') p.text = p.text.replace(/^\s*\[+/, '').slice(0, 2000);
      st.waitingAnswer = true;
    }
    upSend(msg);
  });

  client.on('close', () => {
    st.closed = true;
    jobs.off('done', onDone);
    jobs.off('update', onUpdate);
    if (st.up && st.up.readyState <= 1) st.up.close();
  });

  connect();
}

module.exports = { session, buildSetup };
