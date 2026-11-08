#!/usr/bin/env node
// Server thư ký ảo LINHX: phục vụ trang nhân vật, clip video, WebSocket nói chuyện, và chạy việc giao cho Claude.
// Không thư viện ngoài (Node 22+ có sẵn WebSocket client). Chỉ nghe 127.0.0.1.

const http = require('http');
const fs = require('fs');
const path = require('path');
const config = require('./config');
const ws = require('./ws');
const live = require('./live');
const projects = require('./projects');
const { Jobs } = require('./jobs');

const cfg = config.load();
const character = config.loadCharacter(cfg);
const jobs = new Jobs(cfg);
const WEB = path.join(__dirname, '..', 'web');
const HOST = '127.0.0.1';
const PID_FILE = path.join(config.HOME_DIR, 'server.json');

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.mp4': 'video/mp4', '.webm': 'video/webm', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp' };

function sendFile(req, res, file) {
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404); return res.end('not found'); }
    const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
    const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
    if (range) { // video cần Range để tua và lặp mượt
      const start = range[1] ? Number(range[1]) : 0;
      const end = range[2] ? Math.min(Number(range[2]), st.size - 1) : st.size - 1;
      res.writeHead(206, { 'Content-Type': type, 'Content-Range': `bytes ${start}-${end}/${st.size}`, 'Accept-Ranges': 'bytes', 'Content-Length': end - start + 1 });
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
    res.writeHead(200, { 'Content-Type': type, 'Content-Length': st.size, 'Accept-Ranges': 'bytes', 'Cache-Control': type.startsWith('video') ? 'max-age=3600' : 'no-cache' });
    fs.createReadStream(file).pipe(res);
  });
}

function json(res, obj, code = 200) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-cache' });
  res.end(JSON.stringify(obj));
}

const localOrigin = (o) => !o || /^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/.test(o);

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://local');
  const p = decodeURIComponent(url.pathname);
  if (!localOrigin(req.headers.origin)) { res.writeHead(403); return res.end(); }
  if (p === '/health') return json(res, { ok: true, name: 'linhx-thu-ky', pid: process.pid, port: cfg.port, gemini: Boolean(cfg.geminiApiKey), character: character ? character.name : null });
  if (p === '/api/character') {
    if (!character) return json(res, { assetType: 'none', name: cfg.name });
    const { videoDir, ...pub } = character;
    return json(res, pub);
  }
  if (p === '/api/jobs') return json(res, { jobs: jobs.list() });
  if (p === '/api/projects') return json(res, { projects: projects.list(cfg).map((x) => x.ten) });
  if (p.startsWith('/clips/')) {
    if (!character || !character.videoDir) { res.writeHead(404); return res.end(); }
    return sendFile(req, res, path.join(character.videoDir, path.basename(p)));
  }
  const rel = p === '/' ? 'index.html' : p.replace(/^\/+/, '');
  const file = path.normalize(path.join(WEB, rel));
  if (!file.startsWith(WEB)) { res.writeHead(403); return res.end(); }
  return sendFile(req, res, file);
});

server.on('upgrade', (req, socket) => {
  const url = new URL(req.url, 'http://local');
  if (url.pathname !== '/ws' || !localOrigin(req.headers.origin)) { socket.end('HTTP/1.1 403 Forbidden\r\n\r\n'); return; }
  const conn = ws.accept(req, socket);
  if (conn) live.session(conn, { cfg, character, jobs });
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') { console.log(`[linhx-thu-ky] cổng ${cfg.port} đã có server chạy`); process.exit(0); }
  throw err;
});

server.listen(cfg.port, HOST, () => {
  fs.mkdirSync(config.HOME_DIR, { recursive: true });
  fs.writeFileSync(PID_FILE, JSON.stringify({ pid: process.pid, port: cfg.port, startedAt: Date.now() }));
  console.log(`[linhx-thu-ky] mở ở http://${HOST}:${cfg.port}/  (Gemini: ${cfg.geminiApiKey ? 'có khoá' : 'chưa có khoá, chạy chế độ gõ chữ'}; nhân vật: ${character ? character.name : 'chưa cấu hình'}; dự án: ${projects.list(cfg).length})`);
});

function cleanup() {
  try { const cur = JSON.parse(fs.readFileSync(PID_FILE, 'utf8')); if (cur.pid === process.pid) fs.unlinkSync(PID_FILE); } catch {}
  process.exit(0);
}
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
