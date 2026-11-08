#!/usr/bin/env node
// Điều khiển thư ký ảo: setup | start | open | stop | status | config
//   node thu-ky.js setup --linhx                 cấu hình mặc định cho máy của Linh (D:/LINHX)
//   node thu-ky.js setup --roots "D:/A;D:/B" --character <emily.json> --env <.env>
//   node thu-ky.js open                          bật server (nếu chưa) và mở trình duyệt

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const config = require('../server/config');

const SERVER = path.join(__dirname, '..', 'server', 'server.js');
const LINHX = {
  roots: ['D:/LINHX/LAB', 'D:/LINHX/PRJ'],
  character: { config: 'D:/LINHX/PRJ/IFAGENT-LIVE-CHARACTER-DEMO/configs/emily.json', videoDir: '' },
  envFile: 'D:/LINHX/PRJ/IFAGENT-LIVE-CHARACTER-DEMO/.env',
};

function arg(name) { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : undefined; }

function readCfg() { try { return JSON.parse(fs.readFileSync(config.CONFIG_FILE, 'utf8')); } catch { return {}; } }

function setup() {
  let c = readCfg();
  if (process.argv.includes('--linhx')) c = { ...c, ...LINHX, character: { ...LINHX.character, ...(c.character || {}) } };
  if (arg('roots')) c.roots = arg('roots').split(/[;,]/).map((s) => s.trim()).filter(Boolean);
  if (arg('character')) c.character = { ...(c.character || {}), config: arg('character') };
  if (arg('videos')) c.character = { ...(c.character || {}), videoDir: arg('videos') };
  if (arg('env')) c.envFile = arg('env');
  if (arg('port')) c.port = Number(arg('port'));
  if (arg('permission')) c.permissionMode = arg('permission');
  fs.mkdirSync(config.HOME_DIR, { recursive: true });
  fs.writeFileSync(config.CONFIG_FILE, JSON.stringify(c, null, 2));
  const cfg = config.load();
  const ch = config.loadCharacter(cfg);
  console.log(`Đã ghi ${config.CONFIG_FILE}`);
  console.log(`- Thư mục dự án: ${(cfg.roots || []).join(', ') || '(chưa có)'}`);
  console.log(`- Nhân vật: ${ch ? `${ch.name}, clip ở ${ch.videoDir}${fs.existsSync(ch.videoDir || '') ? '' : ' (KHÔNG THẤY THƯ MỤC)'}` : 'chưa cấu hình hoặc không đọc được file'}`);
  console.log(`- Gemini: ${cfg.geminiApiKey ? 'đã có khoá' : 'chưa có khoá (chạy chế độ gõ chữ)'}`);
}

async function health(port) {
  try { const r = await fetch(`http://127.0.0.1:${port}/health`, { signal: AbortSignal.timeout(800) }); return await r.json(); } catch { return null; }
}

async function start() {
  const cfg = config.load();
  const h = await health(cfg.port);
  if (h && h.name === 'linhx-thu-ky') return { cfg, h };
  fs.mkdirSync(config.HOME_DIR, { recursive: true });
  const out = fs.openSync(path.join(config.HOME_DIR, 'server.log'), 'a');
  const p = spawn(process.execPath, [SERVER], { detached: true, stdio: ['ignore', out, out], windowsHide: true });
  p.unref();
  for (let i = 0; i < 25; i++) {
    await new Promise((r) => setTimeout(r, 200));
    const h2 = await health(cfg.port);
    if (h2) return { cfg, h: h2 };
  }
  throw new Error(`Server không lên, xem ${path.join(config.HOME_DIR, 'server.log')}`);
}

function openBrowser(url) {
  const cmd = process.platform === 'win32' ? ['cmd', ['/c', 'start', '', url]] : process.platform === 'darwin' ? ['open', [url]] : ['xdg-open', [url]];
  try { spawn(cmd[0], cmd[1], { detached: true, stdio: 'ignore', windowsHide: true }).unref(); } catch {}
}

async function main() {
  const cmd = process.argv[2] || 'status';
  if (cmd === 'setup') return setup();
  if (cmd === 'config') return console.log(JSON.stringify({ file: config.CONFIG_FILE, ...readCfg() }, null, 2));
  if (cmd === 'start' || cmd === 'open') {
    const { cfg, h } = await start();
    const url = `http://127.0.0.1:${cfg.port}/`;
    console.log(`Thư ký đang chạy: ${url} (Gemini: ${h.gemini ? 'có' : 'chưa có khoá, gõ chữ'}; nhân vật: ${h.character || 'chưa cấu hình'})`);
    if (cmd === 'open') openBrowser(url);
    return;
  }
  if (cmd === 'stop') {
    let info;
    try { info = JSON.parse(fs.readFileSync(path.join(config.HOME_DIR, 'server.json'), 'utf8')); } catch { return console.log('Không thấy server đang chạy.'); }
    try { process.kill(info.pid); console.log(`Đã tắt server (pid ${info.pid}).`); } catch { console.log('Server đã tắt từ trước.'); }
    return;
  }
  if (cmd === 'status') {
    const cfg = config.load();
    const h = await health(cfg.port);
    console.log(h ? `Đang chạy ở http://127.0.0.1:${cfg.port}/ (Gemini: ${h.gemini ? 'có' : 'chưa'}; nhân vật: ${h.character || 'chưa'})` : 'Chưa chạy. Gõ /thu-ky open.');
    return;
  }
  console.log('Lệnh: setup | start | open | stop | status | config');
}

main().catch((e) => { console.error(e.message); process.exit(1); });
