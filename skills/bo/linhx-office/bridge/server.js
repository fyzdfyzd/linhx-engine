#!/usr/bin/env node
// Bridge của văn phòng ảo LINHX: nhận sự kiện hook, giữ trạng thái các agent,
// đẩy cho trang 2D/3D qua Server-Sent Events. Không cần thư viện ngoài, chỉ nghe 127.0.0.1.

const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { fromClaude, fromAgy } = require('./normalize');

const PORT = Number(process.env.LINHX_OFFICE_PORT || 4848);
const HOST = process.env.LINHX_OFFICE_HOST || '127.0.0.1';
const WEB = path.join(__dirname, '..', 'web');
const HOME_DIR = path.join(os.homedir(), '.linhx-office');
const PID_FILE = path.join(HOME_DIR, 'server.json');

const CLASH_MS = 5 * 60 * 1000;      // hai agent sửa cùng file trong khoảng này
const STUCK_AFTER = 3;               // cùng một lệnh lỗi liên tiếp chừng này lần
const IDLE_REMOVE_MS = 30 * 60 * 1000; // agent im lặng lâu thì rời văn phòng
const LEAVE_MS = 6000;               // thời gian cho nhân vật đi ra cửa

const agents = new Map();
const log = [];
const clients = new Set();
const edits = new Map();             // file -> Map(agentId -> ts)

function publicAgent(a) {
  const { fails, ...rest } = a;
  return rest;
}

function broadcast(type, data) {
  const msg = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of clients) res.write(msg);
}

function addLog(a, text, level = 'info') {
  const item = { ts: Date.now(), agent: a.id, name: a.name, source: a.source, text, level };
  log.push(item);
  if (log.length > 200) log.shift();
  broadcast('log', item);
}

let counter = { claude: 0, agy: 0, sub: 0 };
function nameFor(e) {
  if (e.source === 'agy') return `Worker ${++counter.agy}`;
  if (e.parent) return `${e.role || 'Sub'} ${++counter.sub}`;
  return `Claude ${++counter.claude}`;
}

function ensureAgent(e) {
  let a = agents.get(e.agent);
  if (!a) {
    a = {
      id: e.agent, parent: e.parent || null, source: e.source, role: e.role, name: nameFor(e),
      project: e.project, cwd: e.cwd, title: e.title || '', state: 'idle', detail: '', tool: '',
      since: Date.now(), lastAt: Date.now(), leaving: false, stuck: null, clash: null, fails: new Map(),
    };
    agents.set(a.id, a);
    if (a.parent && !agents.has(a.parent)) {
      // agy được gọi từ một phiên Claude chưa kịp báo SessionStart
      ensureAgent({ agent: a.parent, source: 'claude', role: 'Claude', project: e.project, cwd: e.cwd });
    }
    addLog(a, a.parent ? `vào làm cho ${agents.get(a.parent)?.name || 'Claude'}` : 'vào văn phòng');
  }
  return a;
}

function noteEdit(a, file) {
  if (!file) return;
  const now = Date.now();
  const m = edits.get(file) || new Map();
  edits.set(file, m);
  for (const [id, t] of m) if (now - t > CLASH_MS || !agents.has(id)) m.delete(id);
  m.set(a.id, now);
  const others = [...m.keys()].filter((id) => id !== a.id);
  if (others.length) {
    const b = agents.get(others[0]);
    a.clash = { with: b.id, file: path.basename(file) };
    b.clash = { with: a.id, file: path.basename(file) };
    addLog(a, `cùng sửa ${path.basename(file)} với ${b.name}`, 'warn');
    broadcast('agent', publicAgent(b));
  }
}

function noteResult(a, e) {
  if (!e.key) return;
  if (!e.failed) {
    a.fails.delete(e.key);
    if (a.stuck && a.stuck.key === e.key) a.stuck = null;
    return;
  }
  const n = (a.fails.get(e.key) || 0) + 1;
  a.fails.set(e.key, n);
  if (n >= STUCK_AFTER) {
    a.stuck = { key: e.key, n };
    addLog(a, `có vẻ đi vòng: "${e.key}" lỗi ${n} lần`, 'warn');
  }
}

function apply(e) {
  if (!e) return;
  const a = ensureAgent(e);
  a.lastAt = Date.now();
  if (e.title) a.title = e.title;
  // giữ dự án đầu tiên nhận được; chỉ điền khi agent chưa có
  if (e.project && e.project !== 'khác' && (!a.project || a.project === 'khác')) { a.project = e.project; a.cwd = e.cwd; }
  if (e.kind === 'end') {
    a.state = 'done'; a.detail = e.detail; a.leaving = true;
    addLog(a, e.detail);
    broadcast('agent', publicAgent(a));
    setTimeout(() => { agents.delete(a.id); broadcast('remove', { id: a.id }); }, LEAVE_MS);
    return;
  }
  a.leaving = false;
  const changed = a.state !== e.state || a.detail !== e.detail;
  a.state = e.state; a.detail = e.detail || ''; a.tool = e.tool || '';
  if (e.state === 'thinking' && e.title) a.stuck = null;
  if (e.state === 'writing') noteEdit(a, e.file);
  noteResult(a, e);
  if (changed && e.state !== 'thinking' && e.kind !== 'start') addLog(a, a.detail, e.state === 'error' ? 'error' : e.state === 'waiting' ? 'warn' : 'info');
  broadcast('agent', publicAgent(a));
}

// Dọn agent im lặng quá lâu
setInterval(() => {
  const now = Date.now();
  for (const a of agents.values()) {
    if (!a.leaving && now - a.lastAt > IDLE_REMOVE_MS) apply({ agent: a.id, source: a.source, kind: 'end', detail: 'Về nhà (im lặng lâu)' });
    if (a.clash && now - a.lastAt > CLASH_MS) { a.clash = null; broadcast('agent', publicAgent(a)); }
  }
}, 30000).unref();

function safeDecode(s) { try { return decodeURIComponent(s || ''); } catch { return ''; } }

function readBody(req) {
  return new Promise((resolve) => {
    let s = '';
    req.on('data', (c) => { s += c; if (s.length > 2e6) req.destroy(); });
    req.on('end', () => resolve(s));
  });
}

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css', '.png': 'image/png' };
function sendFile(res, file) {
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(buf);
  });
}

function snapshot() {
  return { agents: [...agents.values()].map(publicAgent), log: log.slice(-60) };
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  // Chỉ nhận trang do chính văn phòng phục vụ, để web lạ không bơm sự kiện giả
  const origin = req.headers.origin;
  if (req.method === 'POST' && origin && !/^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/.test(origin)) {
    res.writeHead(403); return res.end();
  }
  if (req.method === 'POST' && url.pathname === '/hook') {
    const body = await readBody(req);
    res.writeHead(204); res.end();
    let payload = {};
    try { payload = JSON.parse(body || '{}'); } catch { return; }
    const src = url.searchParams.get('src') || 'claude';
    const env = { CLAUDE_CODE_SESSION_ID: req.headers['x-parent-session'] || '', LINHX_OFFICE_PARENT: req.headers['x-office-parent'] || '', cwd: safeDecode(req.headers['x-cwd']) };
    try {
      apply(src === 'agy' ? fromAgy(payload, url.searchParams.get('ev'), env) : fromClaude(payload));
    } catch (err) { console.error('[linhx-office] lỗi xử lý sự kiện:', err.message); }
    return;
  }
  if (url.pathname === '/events') {
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    res.write(`event: snapshot\ndata: ${JSON.stringify(snapshot())}\n\n`);
    clients.add(res);
    const ping = setInterval(() => res.write(': ping\n\n'), 20000);
    req.on('close', () => { clearInterval(ping); clients.delete(res); });
    return;
  }
  if (url.pathname === '/api/state') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify(snapshot())); }
  if (url.pathname === '/health') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(JSON.stringify({ ok: true, name: 'linhx-office', pid: process.pid, port: PORT, agents: agents.size })); }
  if (url.pathname === '/' ) { res.writeHead(302, { Location: '/2d' }); return res.end(); }
  if (url.pathname === '/2d') return sendFile(res, path.join(WEB, '2d.html'));
  if (url.pathname === '/3d') return sendFile(res, path.join(WEB, '3d.html'));
  const rel = decodeURIComponent(url.pathname).replace(/^\/+/, '');
  const file = path.normalize(path.join(WEB, rel));
  if (!file.startsWith(WEB)) { res.writeHead(403); return res.end(); }
  return sendFile(res, file);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') { console.log(`[linhx-office] cổng ${PORT} đã có server chạy`); process.exit(0); }
  throw err;
});

server.listen(PORT, HOST, () => {
  fs.mkdirSync(HOME_DIR, { recursive: true });
  fs.writeFileSync(PID_FILE, JSON.stringify({ pid: process.pid, port: PORT, startedAt: Date.now() }));
  console.log(`[linhx-office] văn phòng mở ở http://${HOST}:${PORT}/2d và /3d`);
});

function cleanup() {
  try { const cur = JSON.parse(fs.readFileSync(PID_FILE, 'utf8')); if (cur.pid === process.pid) fs.unlinkSync(PID_FILE); } catch {}
  process.exit(0);
}
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
