/* Trang thư ký: nhân vật video (AvatarController + ClipPlan của Live Character), giọng Gemini Live qua /ws,
 * hoặc chế độ gõ chữ + giọng máy khi chưa có khoá Gemini. Mọi tool điều phối chạy ở server. */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const S = { ws: null, mode: null, connected: false, mic: null, player: null, avatar: null, holdUntil: 0, jobs: new Map(), aiLine: '' };

  // ---------- nhân vật ----------
  async function loadCharacter() {
    let ch = null;
    try { ch = await (await fetch('/api/character')).json(); } catch {}
    const name = (ch && ch.name) || 'Thư ký';
    $('char-name').textContent = `${name} · Thư ký LINHX`;
    $('ph-name').textContent = name;
    S.avatar = new AvatarController($('char-video'), $('char-video-b'), $('char-img'), $('char-placeholder'));
    if (ch && ch.assetType === 'video_matrix') S.avatar.loadCharacter(ch);
  }
  function pose(p, holdMs = 0) {
    if (!S.avatar || !S.avatar.assetType) return;
    if (!holdMs && Date.now() < S.holdUntil) return;
    S.avatar.setPose(p);
    if (holdMs) S.holdUntil = Date.now() + holdMs;
  }

  // ---------- hiển thị ----------
  function status(t) { $('status').textContent = t; }
  function log(html) {
    const li = document.createElement('li');
    const time = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    li.append(`${time} `);
    const b = document.createElement('b'); b.textContent = html.title; li.append(b, ` ${html.text || ''}`);
    $('log').prepend(li);
    while ($('log').children.length > 80) $('log').lastChild.remove();
  }
  function subtitle(text, you) {
    const el = $('subtitle');
    el.textContent = '';
    if (you) { const s = document.createElement('span'); s.className = 'you'; s.textContent = `Anh Linh: ${you}`; el.append(s); }
    if (text) el.append(text);
  }
  const ST = { dang_lam: 'đang làm', xong: 'xong', loi: 'lỗi' };
  function renderJobs() {
    const ul = $('jobs');
    ul.textContent = '';
    const list = [...S.jobs.values()].sort((a, b) => b.id - a.id);
    if (!list.length) { const li = document.createElement('li'); li.className = 'empty'; li.textContent = 'Chưa có việc nào.'; ul.append(li); return; }
    for (const j of list) {
      const li = document.createElement('li');
      const head = document.createElement('div'); head.className = 'head';
      const t = document.createElement('span'); t.textContent = `#${j.id} · ${j.du_an} · ${j.che_do === 'plan' ? 'hỏi' : 'làm'}`;
      const st = document.createElement('span'); st.className = `st ${j.trang_thai}`; st.textContent = ST[j.trang_thai] || j.trang_thai;
      head.append(t, st);
      const body = document.createElement('div'); body.className = 'body'; body.textContent = j.noi_dung;
      li.append(head, body);
      if (j.ket_qua) {
        const d = document.createElement('details'); const s = document.createElement('summary'); s.textContent = 'Kết quả của Claude';
        const pre = document.createElement('pre'); pre.textContent = j.ket_qua; d.append(s, pre); li.append(d);
      }
      ul.append(li);
    }
  }
  function upsertJob(j) { S.jobs.set(j.id, j); renderJobs(); }

  // ---------- giọng máy (chế độ gõ chữ) ----------
  function speak(text) {
    subtitle(text);
    if (!('speechSynthesis' in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'vi-VN';
    const vi = speechSynthesis.getVoices().find((v) => /^vi/i.test(v.lang));
    if (vi) u.voice = vi;
    u.onstart = () => pose('talking');
    u.onend = () => pose('idle');
    speechSynthesis.speak(u);
  }

  // ---------- WebSocket ----------
  function send(obj) { if (S.ws && S.ws.readyState === 1) S.ws.send(JSON.stringify(obj)); }
  function sendText(text) { send({ clientContent: { turns: [{ role: 'user', parts: [{ text }] }], turnComplete: true } }); }

  function connect() {
    if (S.ws) return;
    status('Đang kết nối…');
    S.ws = new WebSocket(`ws://${location.host}/ws`);
    S.ws.onmessage = (ev) => { let m; try { m = JSON.parse(ev.data); } catch { return; } onMessage(m); };
    S.ws.onclose = () => {
      S.ws = null; S.connected = false; stopMic();
      $('btn-connect').textContent = 'Kết nối'; $('btn-mic').disabled = true;
      status('Đã ngắt'); pose('idle');
    };
    $('btn-connect').textContent = 'Ngắt';
  }

  function onMessage(m) {
    if (m.setupComplete) {
      S.connected = true; S.mode = 'gemini';
      status('Đang nghe anh Linh'); $('mode').textContent = 'Gemini Live';
      $('btn-mic').disabled = false;
      sendText('Anh Linh vừa mở phòng chỉ huy. Chào anh thật ngắn và hỏi anh cần gì.');
      pose('greeting', 2500);
      return;
    }
    if (m.thuKy) return onThuKy(m.thuKy);
    if (m.proxyEvent) { if (m.proxyEvent === 'reconnecting') status('Đang nối lại Gemini…'); if (m.proxyEvent === 'resumed') status('Đã nối lại'); return; }
    const sc = m.serverContent;
    if (sc) {
      if (sc.modelTurn && sc.modelTurn.parts) for (const p of sc.modelTurn.parts) if (p.inlineData && p.inlineData.data) playAudio(p.inlineData.data);
      const clean = (t) => String(t).replace(/<ctrl\d+>|call:\w+\{[^}]*\}|\bemotion:[a-z_-]+/g, '');
      if (sc.inputTranscription && sc.inputTranscription.text) { S.you = (S.you || '') + clean(sc.inputTranscription.text); S.aiLine = ''; subtitle('', S.you); pose('listening'); }
      if (sc.outputTranscription && sc.outputTranscription.text) { S.aiLine += clean(sc.outputTranscription.text); subtitle(S.aiLine, S.you); }
      if (sc.interrupted && S.player) S.player.clearQueue();
      if (sc.turnComplete) { if (S.aiLine.trim()) log({ title: 'Thư ký:', text: S.aiLine.trim() }); S.aiLine = ''; S.you = ''; }
    }
    if (m.toolCall && m.toolCall.functionCalls) {
      const functionResponses = m.toolCall.functionCalls.map((fc) => {
        if (fc.name === 'set_emotion') pose(String((fc.args && fc.args.emotion) || 'idle'), 3000);
        return { id: fc.id, name: fc.name, response: { result: { ok: true } } };
      });
      setTimeout(() => send({ toolResponse: { functionResponses } }), 150);
    }
  }

  const TOOL_NAMES = { danh_sach_du_an: 'Xem danh sách dự án', tinh_hinh_du_an: 'Xem tình hình', agent_dang_chay: 'Xem ai đang làm', hoi_claude: 'Hỏi Claude', giao_viec: 'Giao việc', ket_qua_viec: 'Xem kết quả việc', dung_viec: 'Dừng việc' };
  function onThuKy(t) {
    if (t.type === 'mode' && t.mode === 'offline') {
      S.connected = true; S.mode = 'offline';
      $('mode').textContent = 'Chưa có Gemini: gõ chữ';
      status('Gõ lệnh ở ô dưới');
      speak('Chào anh Linh. Em chưa có khoá Gemini nên mình gõ chữ nhé. Anh gõ "dự án" để xem danh sách.');
      return;
    }
    if (t.type === 'say') { speak(t.text); log({ title: 'Thư ký:', text: t.text }); return; }
    if (t.type === 'tool') {
      log({ title: `${TOOL_NAMES[t.name] || t.name}${t.args.du_an ? ` · ${t.args.du_an}` : ''}`, text: t.result.ok ? '' : `(lỗi: ${t.result.error})` });
      if (t.name === 'giao_viec' || t.name === 'hoi_claude') pose('action', 2500); else pose('thinking', 1500);
      return;
    }
    if (t.type === 'job') return upsertJob(t.job);
    if (t.type === 'report') { upsertJob(t.job); log({ title: `Báo cáo việc #${t.job.id}:`, text: ST[t.job.trang_thai] }); return; }
    if (t.type === 'error') { status(t.text); log({ title: 'Lỗi', text: t.text }); }
  }

  // ---------- âm thanh ----------
  function playAudio(b64) {
    if (!S.player) {
      S.player = new AudioPlayer(24000);
      S.player.onPlaybackStart = () => { S.mic && S.mic.mute(); pose('talking'); };
      S.player.onPlaybackEnd = () => { S.mic && S.mic.unmute(); pose('idle'); };
    }
    const bin = atob(b64); const u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    S.player.addPCM16(u8.buffer);
  }
  async function startMic() {
    try {
      S.mic = new AudioCapture(16000);
      S.mic.onAudioData = (b64) => send({ realtimeInput: { mediaChunks: [{ mimeType: 'audio/pcm;rate=16000', data: b64 }] } });
      await S.mic.start();
      $('btn-mic').textContent = 'Micro: bật'; $('btn-mic').classList.add('on');
    } catch (e) { S.mic = null; log({ title: 'Micro', text: `không mở được: ${e.message}` }); }
  }
  function stopMic() {
    if (S.mic) { S.mic.stop(); S.mic = null; }
    $('btn-mic').textContent = 'Micro: tắt'; $('btn-mic').classList.remove('on');
  }

  // ---------- nút ----------
  $('btn-connect').onclick = () => { if (S.ws) S.ws.close(); else connect(); };
  $('btn-mic').onclick = () => { if (S.mic) stopMic(); else startMic(); };
  $('form').onsubmit = (e) => {
    e.preventDefault();
    const text = $('text').value.trim();
    if (!text) return;
    if (!S.ws) { connect(); setTimeout(() => sendText(text), 800); } else sendText(text);
    log({ title: 'Anh Linh:', text });
    subtitle('', text);
    pose('thinking', 1200);
    $('text').value = '';
  };

  fetch('/api/jobs').then((r) => r.json()).then((d) => { for (const j of d.jobs || []) S.jobs.set(j.id, j); renderJobs(); }).catch(() => {});
  loadCharacter();
  window.__thuKy = S; // để soi khi thử
  if (new URLSearchParams(location.search).has('auto')) connect();
})();
