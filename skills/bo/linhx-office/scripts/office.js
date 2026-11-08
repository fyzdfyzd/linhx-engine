#!/usr/bin/env node
// Điều khiển văn phòng ảo LINHX.
//   node office.js start | stop | status | open [2d|3d] | demo | install-agy | uninstall-agy

const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname, '..');
const PORT = Number(process.env.LINHX_OFFICE_PORT || 4848);
const HOME_DIR = path.join(os.homedir(), '.linhx-office');
const AGY_HOOKS = path.join(os.homedir(), '.gemini', 'config', 'hooks.json');
const AGY_GROUP = 'linhx-office';
const AGY_EVENTS = ['PreInvocation', 'PostToolUse', 'PostInvocation', 'Stop'];

function health() {
  return new Promise((resolve) => {
    const req = http.get({ host: '127.0.0.1', port: PORT, path: '/health', timeout: 800 }, (res) => {
      let s = ''; res.on('data', (c) => (s += c)); res.on('end', () => { try { resolve(JSON.parse(s)); } catch { resolve(null); } });
    });
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.on('error', () => resolve(null));
  });
}

async function start() {
  const h = await health();
  if (h) return console.log(`Văn phòng đang chạy: http://127.0.0.1:${PORT}/2d  ·  http://127.0.0.1:${PORT}/3d  (${h.agents} agent)`);
  const child = spawn(process.execPath, [path.join(ROOT, 'bridge', 'server.js')], { detached: true, stdio: 'ignore', windowsHide: true });
  child.unref();
  for (let i = 0; i < 20; i++) {
    await new Promise((r) => setTimeout(r, 150));
    if (await health()) return console.log(`Đã mở văn phòng: http://127.0.0.1:${PORT}/2d  ·  http://127.0.0.1:${PORT}/3d`);
  }
  console.log('Không bật được server. Thử chạy trực tiếp: node ' + path.join(ROOT, 'bridge', 'server.js'));
  process.exitCode = 1;
}

async function stop() {
  const h = await health();
  if (!h) return console.log('Văn phòng không chạy.');
  try { process.kill(h.pid); console.log('Đã tắt văn phòng (pid ' + h.pid + ').'); }
  catch (e) { console.log('Không tắt được: ' + e.message); }
}

async function status() {
  const h = await health();
  console.log(h ? `Đang chạy ở cổng ${h.port}, pid ${h.pid}, ${h.agents} agent.` : 'Văn phòng không chạy.');
  const agy = readJson(AGY_HOOKS);
  console.log(agy && agy[AGY_GROUP] ? `Hook Antigravity: đã cài (${AGY_HOOKS})` : 'Hook Antigravity: chưa cài');
}

function openUrl(url) {
  const cmd = process.platform === 'win32' ? ['cmd', ['/c', 'start', '""', url]]
    : process.platform === 'darwin' ? ['open', [url]] : ['xdg-open', [url]];
  try { spawn(cmd[0], cmd[1], { detached: true, stdio: 'ignore', windowsHide: true }).unref(); } catch {}
  console.log('Mở ' + url);
}

async function open(mode = '2d') {
  await start();
  openUrl(`http://127.0.0.1:${PORT}/${mode === '3d' ? '3d' : '2d'}`);
}

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    if (e.isDirectory()) copyDir(s, d); else fs.copyFileSync(s, d);
  }
}

// agy cần đường dẫn cố định, nên chép phần chạy được ra ~/.linhx-office/app
function installAgy() {
  const app = path.join(HOME_DIR, 'app');
  for (const d of ['hooks', 'bridge', 'web']) copyDir(path.join(ROOT, d), path.join(app, d));
  const script = path.join(app, 'hooks', 'send.js').replace(/\\/g, '/');
  // "node" để trần ở đầu lệnh: chạy được trong cmd, PowerShell và sh
  const cmd = (ev) => ({ type: 'command', command: `node "${script}" agy ${ev}`, timeout: 5 });
  const group = {
    PreInvocation: [cmd('PreInvocation')],
    PostToolUse: [{ matcher: '*', hooks: [cmd('PostToolUse')] }],
    PostInvocation: [cmd('PostInvocation')],
    Stop: [cmd('Stop')],
  };
  fs.mkdirSync(path.dirname(AGY_HOOKS), { recursive: true });
  const cur = readJson(AGY_HOOKS) || {};
  if (fs.existsSync(AGY_HOOKS)) fs.copyFileSync(AGY_HOOKS, AGY_HOOKS + '.bak-linhx-office');
  cur[AGY_GROUP] = group;
  fs.writeFileSync(AGY_HOOKS, JSON.stringify(cur, null, 2));
  console.log(`Đã cài hook Antigravity vào ${AGY_HOOKS} (bản cũ lưu ở .bak-linhx-office). Mở phiên agy mới để có hiệu lực.`);
}

function uninstallAgy() {
  const cur = readJson(AGY_HOOKS);
  if (!cur || !cur[AGY_GROUP]) return console.log('Hook Antigravity chưa cài.');
  delete cur[AGY_GROUP];
  fs.writeFileSync(AGY_HOOKS, JSON.stringify(cur, null, 2));
  console.log('Đã gỡ hook Antigravity.');
}

// Kịch bản mẫu: 1 Claude quản lý, 1 subagent, 2 worker Antigravity
function postHook(src, payload, ev, parent) {
  return new Promise((resolve) => {
    const body = JSON.stringify(payload);
    const headers = { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) };
    if (parent) headers['x-parent-session'] = parent;
    const req = http.request({ host: '127.0.0.1', port: PORT, method: 'POST', path: `/hook?src=${src}${ev ? '&ev=' + ev : ''}`, headers }, (res) => { res.resume(); resolve(); });
    req.on('error', resolve);
    req.end(body);
  });
}

async function demo() {
  await start();
  const S = 'demo-' + Date.now().toString(36), cwd = 'D:/LINHX/LAB/LAB021-VAN-PHONG-AO-AGENT';
  const c = (hook_event_name, extra = {}) => postHook('claude', { session_id: S, cwd, hook_event_name, ...extra });
  const g = (n, ev, extra = {}) => postHook('agy', { conversationId: `${S}-w${n}`, workspacePaths: [cwd], hookEventName: ev, ...extra }, ev, S);
  const steps = [
    () => c('SessionStart', { source: 'startup' }),
    () => c('UserPromptSubmit', { prompt: 'Làm plugin văn phòng ảo, chia việc cho 2 worker Antigravity' }),
    () => c('PreToolUse', { tool_name: 'Read', tool_input: { file_path: `${cwd}/02-DE-XUAT-PHUONG-AN.md` } }),
    () => c('PreToolUse', { tool_name: 'Grep', tool_input: { pattern: 'hook' } }),
    () => c('PreToolUse', { tool_name: 'Grep', tool_input: { pattern: 'agy' } }),
    () => c('PreToolUse', { tool_name: 'Agent', tool_input: { description: 'Đọc code agent-office', subagent_type: 'Explore' } }),
    () => c('SubagentStart', { agent_id: 'sub1', agent_type: 'Explore' }),
    () => c('PreToolUse', { agent_id: 'sub1', agent_type: 'Explore', tool_name: 'Read', tool_input: { file_path: 'bridge/server.js' } }),
    () => c('PreToolUse', { tool_name: 'Bash', tool_input: { command: 'agy -p "Viết web/2d.html"', description: 'Giao việc cho worker 1' } }),
    () => g(1, 'PreInvocation'),
    () => c('PreToolUse', { tool_name: 'Bash', tool_input: { command: 'agy -p "Viết web/3d.html"', description: 'Giao việc cho worker 2' } }),
    () => g(2, 'PreInvocation'),
    () => g(1, 'PostToolUse', { toolCall: { name: 'view_file', args: { AbsolutePath: `${cwd}/src/office-core.js` } } }),
    () => g(2, 'PostToolUse', { toolCall: { name: 'search_web', args: { Query: 'three.js low poly office' } } }),
    () => c('PreToolUse', { agent_id: 'sub1', agent_type: 'Explore', tool_name: 'WebFetch', tool_input: { url: 'https://github.com/regisBafutwabo/agent-office' } }),
    () => g(1, 'PostToolUse', { toolCall: { name: 'write_to_file', args: { TargetFile: `${cwd}/web/2d.html` } } }),
    () => g(2, 'PostToolUse', { toolCall: { name: 'write_to_file', args: { TargetFile: `${cwd}/web/3d.html` } } }),
    () => c('PreToolUse', { tool_name: 'Write', tool_input: { file_path: `${cwd}/web/2d.html` } }),
    () => g(2, 'PostToolUse', { toolCall: { name: 'run_command', args: { CommandLine: 'npm test' } } }),
    () => c('SubagentStop', { agent_id: 'sub1', agent_type: 'Explore' }),
    () => c('PermissionRequest', { tool_name: 'Bash', tool_input: { command: 'git push' } }),
    () => g(1, 'Stop', { fullyIdle: true }),
  ];
  console.log('Đang chạy kịch bản mẫu (khoảng 40 giây). Mở http://127.0.0.1:' + PORT + '/2d hoặc /3d để xem.');
  for (const s of steps) { await s(); await new Promise((r) => setTimeout(r, 1800)); }
  console.log('Xong kịch bản mẫu.');
}

const [cmd, arg] = process.argv.slice(2);
const table = { start, stop, status, open: () => open(arg), demo, 'install-agy': installAgy, 'uninstall-agy': uninstallAgy };
(table[cmd] || (() => console.log('Dùng: node office.js start|stop|status|open [2d|3d]|demo|install-agy|uninstall-agy')))();
