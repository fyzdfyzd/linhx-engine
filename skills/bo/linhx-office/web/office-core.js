// Phần chung của văn phòng 2D và 3D: nhận sự kiện, bố trí phòng, luật đi lại, bảng bên.
// Toạ độ thế giới tính bằng ô: x 0..W (trái→phải), y 0..H (trên→dưới). 3D dùng y làm trục z.

(function () {
  const W = 30, H = 20;

  // ---------- Bố trí phòng ----------
  const CLAUDE_DESKS = [], AGY_DESKS = [];
  for (const y of [6, 10]) for (const x of [3, 7, 11]) CLAUDE_DESKS.push({ x, y });
  for (const y of [6, 10]) for (const x of [19, 23, 27]) AGY_DESKS.push({ x, y });
  // bàn dự phòng khi đông, chỉ vẽ khi có người ngồi
  for (const x of [7, 11]) CLAUDE_DESKS.push({ x, y: 14, spare: true });
  for (const x of [19, 23]) AGY_DESKS.push({ x, y: 13.5, spare: true });

  const LAYOUT = {
    W, H,
    claudeDesks: CLAUDE_DESKS, agyDesks: AGY_DESKS,
    shelves: [{ x: 2.5, y: 1.2, w: 3 }, { x: 6, y: 1.2, w: 3 }, { x: 9.5, y: 1.2, w: 3 }],
    librarySpots: [3, 4.5, 6, 7.5, 9, 10.5, 12].map((x) => ({ x, y: 2.8 })),
    meeting: { x: 15, y: 9, w: 3, h: 2 },
    meetingSpots: [{ x: 13.3, y: 8.4 }, { x: 13.3, y: 9.6 }, { x: 16.7, y: 8.4 }, { x: 16.7, y: 9.6 }, { x: 14.4, y: 7.3 }, { x: 15.6, y: 7.3 }, { x: 14.4, y: 10.7 }, { x: 15.6, y: 10.7 }],
    lounge: { x: 24.5, y: 16.5 },
    loungeSpots: [{ x: 22.8, y: 16 }, { x: 23.8, y: 17.6 }, { x: 25.2, y: 17.6 }, { x: 26.3, y: 16 }, { x: 24.5, y: 15.2 }],
    coffee: { x: 4.5, y: 18 },
    coffeeSpots: [{ x: 3, y: 16.8 }, { x: 4.2, y: 16.6 }, { x: 5.4, y: 16.8 }, { x: 6.6, y: 16.6 }, { x: 2.4, y: 15.6 }, { x: 7.4, y: 15.6 }],
    door: { x: 15, y: 19.6 },
    board: { x: 21, y: 1.2, w: 6 },
    plants: [{ x: 1, y: 1.5 }, { x: 28.8, y: 1.5 }, { x: 1, y: 18.5 }, { x: 28.8, y: 18.5 }, { x: 13.2, y: 1.5 }, { x: 16.8, y: 1.5 }],
  };

  const STATE_VI = {
    idle: 'Rảnh', thinking: 'Đang nghĩ', reading: 'Đọc code', research: 'Tra cứu web', writing: 'Viết file',
    running: 'Chạy lệnh', delegating: 'Giao việc', waiting: 'Cần bạn', done: 'Xong', error: 'Lỗi',
  };
  const BUBBLE = {
    idle: 'z', thinking: '…', reading: '📖', research: '🌐', writing: '✎', running: '>_',
    delegating: '📋', waiting: '!', done: '☕', error: '✖',
  };
  const COLORS = { claude: '#d97757', agy: '#4b8bf5', sub: '#9b6dd6' };

  function colorOf(a) { return a.source === 'agy' ? COLORS.agy : a.parent ? COLORS.sub : COLORS.claude; }
  function hash(s) { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) | 0; return Math.abs(h); }

  // ---------- Trạng thái phía trình duyệt ----------
  const agents = new Map();     // id -> agent (dữ liệu server + vị trí vẽ)
  const listeners = [];
  const seats = { claude: new Map(), agy: new Map() }; // deskIndex -> agentId

  function takeSeat(a) {
    if (a.parent && a.source !== 'agy') return null;   // subagent đứng cạnh bàn của cha
    const kind = a.source === 'agy' ? 'agy' : 'claude';
    const desks = kind === 'agy' ? AGY_DESKS : CLAUDE_DESKS;
    for (let i = 0; i < desks.length; i++) if (!seats[kind].has(i)) { seats[kind].set(i, a.id); return { kind, i }; }
    return { kind, i: hash(a.id) % desks.length };
  }
  function freeSeat(a) { if (a.seat && seats[a.seat.kind].get(a.seat.i) === a.id) seats[a.seat.kind].delete(a.seat.i); }

  function deskOf(a) {
    if (!a.seat) return null;
    return (a.seat.kind === 'agy' ? AGY_DESKS : CLAUDE_DESKS)[a.seat.i];
  }

  function homeOf(a) {
    const d = deskOf(a);
    if (d) return { x: d.x, y: d.y + 1.1, face: 'up' };
    const p = a.parent && agents.get(a.parent);
    const pd = p && deskOf(p);
    if (pd) {
      const kids = [...agents.values()].filter((k) => k.parent === a.parent && !k.seat);
      const n = Math.max(0, kids.indexOf(a));
      return { x: pd.x + (n % 2 ? -1.5 : 1.5), y: pd.y + 1.2 + Math.floor(n / 2) * 0.9, face: 'up' };
    }
    return { x: 15, y: 13, face: 'down' };
  }

  function slot(list, a) { return list[hash(a.id) % list.length]; }

  // Luật đi lại: trạng thái nào thì đứng ở đâu
  function targetOf(a) {
    if (a.leaving) return { ...LAYOUT.door, face: 'down' };
    switch (a.state) {
      case 'reading': return a.streak >= 2 ? { ...slot(LAYOUT.librarySpots, a), face: 'up' } : homeOf(a);
      case 'research': return { ...slot(LAYOUT.loungeSpots, a), face: 'down' };
      case 'delegating': return { ...slot(LAYOUT.meetingSpots, a), face: 'center' };
      case 'done': return { ...slot(LAYOUT.coffeeSpots, a), face: 'down' };
      case 'thinking': // nghĩ giữa chừng thì đứng yên chỗ đang làm
        if (a.lastWork === 'reading' && a.streak >= 2) return { ...slot(LAYOUT.librarySpots, a), face: 'up' };
        if (a.lastWork === 'research') return { ...slot(LAYOUT.loungeSpots, a), face: 'down' };
        if (a.lastWork === 'delegating') return { ...slot(LAYOUT.meetingSpots, a), face: 'center' };
        return homeOf(a);
      default: return homeOf(a);
    }
  }

  function upsert(data) {
    let a = agents.get(data.id);
    if (!a) {
      a = { ...data, x: LAYOUT.door.x, y: LAYOUT.door.y, streak: 0, walking: false, born: performance.now() };
      a.seat = takeSeat(a);
      a.color = colorOf(a);
      a.hue = hash(a.id) % 6;
      agents.set(a.id, a);
    } else {
      Object.assign(a, data);
      // "Đang nghĩ" giữa hai lần gọi tool không cắt mạch: vẫn tính là đọc liên tiếp
      if (data.state === 'reading') a.streak = a.lastWork === 'reading' ? a.streak + 1 : 1;
      if (data.state !== 'thinking') { if (data.state !== 'reading') a.streak = 0; a.lastWork = data.state; }
      if (data.detail === 'Đang nghĩ') { a.lastWork = 'thinking'; a.streak = 0; }
    }
    a.target = targetOf(a);
    a.stateAt = performance.now();
    emit('agent', a);
  }

  function remove(id) {
    const a = agents.get(id);
    if (!a) return;
    freeSeat(a);
    agents.delete(id);
    emit('remove', a);
  }

  function emit(type, a) { for (const f of listeners) f(type, a); renderPanel(); }

  // Di chuyển thẳng tới đích, tốc độ ô/giây
  function step(dt) {
    for (const a of agents.values()) {
      if (!a.target) a.target = targetOf(a);
      const dx = a.target.x - a.x, dy = a.target.y - a.y, d = Math.hypot(dx, dy);
      const sp = 4.2 * dt;
      if (d > 0.04) {
        a.walking = true;
        const k = Math.min(1, sp / d);
        a.x += dx * k; a.y += dy * k;
        a.dir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'down' : 'up';
      } else {
        a.walking = false;
        a.dir = a.target.face === 'center' ? (a.x < LAYOUT.meeting.x ? 'right' : 'left') : a.target.face || 'down';
      }
    }
  }

  // ---------- Kết nối server ----------
  const logItems = [];
  function connect() {
    const es = new EventSource('/events');
    es.addEventListener('snapshot', (e) => {
      const d = JSON.parse(e.data);
      for (const id of [...agents.keys()]) if (!d.agents.find((x) => x.id === id)) remove(id);
      // cha trước, con sau, để subagent tìm được bàn của cha
      d.agents.sort((p, q) => (p.parent ? 1 : 0) - (q.parent ? 1 : 0)).forEach(upsert);
      logItems.length = 0; logItems.push(...d.log); renderLog();
      setConn(true);
    });
    es.addEventListener('agent', (e) => upsert(JSON.parse(e.data)));
    es.addEventListener('remove', (e) => remove(JSON.parse(e.data).id));
    es.addEventListener('log', (e) => { logItems.push(JSON.parse(e.data)); if (logItems.length > 80) logItems.shift(); renderLog(); });
    es.onerror = () => setConn(false);
  }

  // ---------- Bảng bên ----------
  const css = `
  :root{--bg:#f6f1e7;--panel:rgba(255,252,246,.94);--ink:#2b2622;--muted:#7a6f64;--line:#e4d9c8;--claude:${COLORS.claude};--agy:${COLORS.agy};--sub:${COLORS.sub}}
  @media (prefers-color-scheme:dark){:root{--bg:#1b1a1f;--panel:rgba(32,30,36,.94);--ink:#f1ece4;--muted:#a59c90;--line:#3a3640}}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;overflow:hidden}
  #stage{position:fixed;inset:0}
  .lo-top{position:fixed;left:12px;top:12px;display:flex;gap:8px;align-items:center;z-index:5}
  .lo-chip{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:6px 10px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
  .lo-chip b{font-weight:650}.lo-chip a{color:inherit;text-decoration:none;padding:2px 8px;border-radius:6px}.lo-chip a.on{background:var(--ink);color:var(--bg)}
  .lo-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#c33;margin-right:6px}.lo-dot.on{background:#2a9d5c}
  .lo-side{position:fixed;right:12px;top:12px;bottom:12px;width:300px;display:flex;flex-direction:column;gap:8px;z-index:5}
  .lo-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.08);overflow:auto}
  .lo-agents{flex:1 1 60%;padding:6px 0}.lo-log{flex:1 1 40%;padding:6px 10px;font-size:12.5px}
  .lo-h{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:6px 12px 2px}
  .lo-row{display:grid;grid-template-columns:12px minmax(0,1fr) auto;gap:8px;align-items:start;padding:6px 12px;cursor:pointer}
  .lo-row:hover{background:rgba(127,127,127,.08)}.lo-row.child{padding-left:28px}
  .lo-sw{width:10px;height:10px;border-radius:3px;margin-top:5px}
  .lo-name{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lo-det{color:var(--muted);font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .lo-st{font-size:11.5px;padding:2px 7px;border-radius:999px;background:rgba(127,127,127,.14);white-space:nowrap}
  .lo-st.waiting{background:#f5c04a;color:#3a2a00}.lo-st.error{background:#e5534b;color:#fff}.lo-st.done{background:#cfe8d6;color:#16432a}
  .lo-flag{font-size:11.5px;color:#c0392b}
  .lo-li{padding:3px 0;border-bottom:1px dashed var(--line)}.lo-li.warn{color:#b7791f}.lo-li.error{color:#c0392b}
  .lo-t{color:var(--muted);font-variant-numeric:tabular-nums;margin-right:6px}
  .lo-empty{padding:10px 12px;color:var(--muted)}
  .lo-legend{position:fixed;left:12px;bottom:12px;z-index:5;font-size:12px}
  @media (max-width:760px){.lo-side{top:auto;height:38%;left:12px;width:auto}}
  `;

  let side, logBox, connDot, countBox;
  function buildUI(mode) {
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    const top = document.createElement('div'); top.className = 'lo-top';
    top.innerHTML = `<div class="lo-chip"><span class="lo-dot" id="lo-conn"></span><b>Văn phòng LINHX</b></div>
      <div class="lo-chip" id="lo-count">0 agent</div>
      <div class="lo-chip"><a href="/2d" class="${mode === '2d' ? 'on' : ''}">2D</a><a href="/3d" class="${mode === '3d' ? 'on' : ''}">3D</a></div>`;
    document.body.appendChild(top);
    const s = document.createElement('div'); s.className = 'lo-side';
    s.innerHTML = `<div class="lo-card lo-agents" id="lo-agents"></div><div class="lo-card lo-log"><div class="lo-h" style="padding-left:0">Nhật ký</div><div id="lo-logs"></div></div>`;
    document.body.appendChild(s);
    const lg = document.createElement('div'); lg.className = 'lo-legend lo-chip';
    lg.innerHTML = `<span style="color:var(--claude)">■</span> Claude &nbsp; <span style="color:var(--sub)">■</span> Subagent &nbsp; <span style="color:var(--agy)">■</span> Antigravity &nbsp;·&nbsp; Thư viện = đọc nhiều file, Sofa = tra web, Bàn họp = giao việc, Quầy cà phê = xong việc`;
    document.body.appendChild(lg);
    side = document.getElementById('lo-agents'); logBox = document.getElementById('lo-logs');
    connDot = document.getElementById('lo-conn'); countBox = document.getElementById('lo-count');
    side.addEventListener('click', (e) => { const r = e.target.closest('[data-id]'); if (r && api.onSelect) api.onSelect(agents.get(r.dataset.id)); });
  }

  function setConn(on) { if (connDot) connDot.classList.toggle('on', on); }
  function esc(s) { return String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  let panelQueued = false;
  function renderPanel() {
    if (!side || panelQueued) return;
    panelQueued = true;
    requestAnimationFrame(() => {
      panelQueued = false;
      const list = [...agents.values()];
      const need = list.filter((a) => a.state === 'waiting').length;
      countBox.innerHTML = `<b>${list.length}</b> agent · <b>${list.filter((a) => a.source === 'agy').length}</b> Antigravity${need ? ` · <b style="color:#b7791f">${need} cần bạn</b>` : ''}`;
      if (!list.length) { side.innerHTML = '<div class="lo-empty">Chưa có agent nào. Mở một phiên Claude Code mới, hoặc chạy <code>/office demo</code>.</div>'; return; }
      const byProject = new Map();
      for (const a of list.filter((a) => !a.parent || !agents.has(a.parent))) {
        if (!byProject.has(a.project)) byProject.set(a.project, []);
        byProject.get(a.project).push(a);
      }
      let html = '';
      for (const [proj, roots] of byProject) {
        html += `<div class="lo-h">${esc(proj)}</div>`;
        for (const r of roots) {
          html += row(r, false);
          for (const k of list.filter((x) => x.parent === r.id)) html += row(k, true);
        }
      }
      side.innerHTML = html;
    });
  }
  function row(a, child) {
    const flags = [a.stuck ? `↻ đi vòng: ${esc(a.stuck.key)}` : '', a.clash ? `⚠ cùng sửa ${esc(a.clash.file)}` : ''].filter(Boolean).join(' · ');
    return `<div class="lo-row${child ? ' child' : ''}" data-id="${esc(a.id)}"><div class="lo-sw" style="background:${a.color}"></div>
      <div><div class="lo-name">${esc(a.name)}${a.title ? ` <span class="lo-det" style="font-weight:400">· ${esc(a.title)}</span>` : ''}</div>
      <div class="lo-det" title="${esc(a.detail)}">${esc(a.detail)}</div>${flags ? `<div class="lo-flag">${flags}</div>` : ''}</div>
      <div class="lo-st ${a.state}">${STATE_VI[a.state] || a.state}</div></div>`;
  }
  function renderLog() {
    if (!logBox) return;
    logBox.innerHTML = logItems.slice(-40).reverse().map((l) => {
      const t = new Date(l.ts).toTimeString().slice(0, 5);
      return `<div class="lo-li ${l.level}"><span class="lo-t">${t}</span><b>${esc(l.name)}</b> ${esc(l.text)}</div>`;
    }).join('');
  }

  const api = { LAYOUT, STATE_VI, BUBBLE, COLORS, agents, step, deskOf, buildUI, connect, onSelect: null,
    on(f) { listeners.push(f); }, hash };
  window.Office = api;
})();
