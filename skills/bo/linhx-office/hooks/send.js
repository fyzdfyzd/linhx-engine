#!/usr/bin/env node
// Hook của văn phòng ảo LINHX. Đọc JSON sự kiện từ stdin, gửi cho bridge, rồi thoát ngay.
//   Claude Code:     node send.js
//   Antigravity CLI: node send.js agy <TênSựKiện>
// Không bao giờ làm chậm hay chặn agent: timeout ngắn, lỗi thì bỏ qua, luôn exit 0.

const http = require('http');
const path = require('path');
const { spawn } = require('child_process');

const PORT = Number(process.env.LINHX_OFFICE_PORT || 4848);
const isAgy = process.argv[2] === 'agy';
const agyEvent = process.argv[3] || '';

// agy đọc stdout của hook làm quyết định; trả lời trung tính để không đổi hành vi agy
function agyStdout() {
  if (agyEvent === 'PreToolUse') return JSON.stringify({ decision: 'ask' });
  if (agyEvent === 'Stop') return JSON.stringify({ decision: 'allow' });
  return '{}';
}

function finish() {
  if (isAgy) process.stdout.write(agyStdout() + '\n');
  process.exit(0);
}

setTimeout(finish, 2500).unref(); // chốt chặn cuối cùng

function readStdin() {
  return new Promise((resolve) => {
    let s = '';
    const t = setTimeout(() => resolve(s), 1500);
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => { s += c; });
    process.stdin.on('end', () => { clearTimeout(t); resolve(s); });
    process.stdin.on('error', () => { clearTimeout(t); resolve(s); });
  });
}

function post(body) {
  return new Promise((resolve) => {
    const q = isAgy ? `?src=agy&ev=${encodeURIComponent(agyEvent)}` : '?src=claude';
    const headers = { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body), 'x-cwd': encodeURIComponent(process.cwd()) };
    if (isAgy && process.env.CLAUDE_CODE_SESSION_ID) headers['x-parent-session'] = process.env.CLAUDE_CODE_SESSION_ID;
    if (isAgy && process.env.LINHX_OFFICE_PARENT) headers['x-office-parent'] = process.env.LINHX_OFFICE_PARENT;
    const req = http.request({ host: '127.0.0.1', port: PORT, path: '/hook' + q, method: 'POST', headers, timeout: 800 }, (res) => {
      res.resume(); resolve(true);
    });
    req.on('timeout', () => { req.destroy(); resolve(false); });
    req.on('error', () => resolve(false));
    req.end(body);
  });
}

function startServer() {
  if (process.env.LINHX_OFFICE_AUTOSTART === '0') return;
  try {
    const child = spawn(process.execPath, [path.join(__dirname, '..', 'bridge', 'server.js')], {
      detached: true, stdio: 'ignore', windowsHide: true,
    });
    child.unref();
  } catch {}
}

(async () => {
  const body = await readStdin();
  if (!body.trim()) return finish();
  let ok = await post(body);
  if (!ok) {
    let ev = '';
    try { ev = JSON.parse(body).hook_event_name || ''; } catch {}
    // Mở phiên Claude mới hoặc agy nhận việc mà văn phòng chưa chạy: tự bật bridge rồi gửi lại một lần
    if (ev === 'SessionStart' || ev === 'UserPromptSubmit' || agyEvent === 'PreInvocation') {
      startServer();
      await new Promise((r) => setTimeout(r, 600));
      ok = await post(body);
    }
  }
  finish();
})();
