// Danh bạ dự án: quét các thư mục gốc, đọc OVERVIEW/README/LOG và phiên Claude Code gần nhất của từng thư mục.

const fs = require('fs');
const os = require('os');
const path = require('path');

const SUMMARY_FILES = ['OVERVIEW.md', 'README.md', 'CLAUDE.md', 'AGENTS.md', 'INDEX.md'];
const SKIP = /^(\.|_|node_modules$|ARCHIVE$|BACKUP$)/i;

function fold(s) {
  return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/gi, 'd').toLowerCase();
}
// "LAB 25", "lab025", "Lab hai mươi lăm" (không hỗ trợ chữ số đọc) → so khớp theo chữ + số bỏ số 0 đầu
function key(s) { return fold(s).replace(/\d+/g, (n) => String(Number(n))).replace(/[^a-z0-9]/g, ''); }

function readHead(file, max) {
  try { return fs.readFileSync(file, 'utf8').slice(0, max); } catch { return ''; }
}
function readTail(file, max) {
  try { const s = fs.readFileSync(file, 'utf8'); return s.slice(Math.max(0, s.length - max)); } catch { return ''; }
}
function clean(md) { return md.replace(/```[\s\S]*?```/g, '').replace(/[#>*`|]/g, ' ').replace(/\s+/g, ' ').trim(); }

function list(cfg) {
  const out = [];
  const seen = new Set();
  const add = (ten, dir) => {
    const k = path.resolve(dir).toLowerCase();
    if (seen.has(k)) return;
    seen.add(k);
    out.push({ ten, thu_muc: dir });
  };
  for (const p of cfg.projects || []) if (p && p.thu_muc) add(p.ten || path.basename(p.thu_muc), p.thu_muc);
  for (const root of cfg.roots || []) {
    let names = [];
    try { names = fs.readdirSync(root, { withFileTypes: true }); } catch { continue; }
    for (const d of names) if (d.isDirectory() && !SKIP.test(d.name)) add(d.name, path.join(root, d.name));
  }
  return out;
}

function find(cfg, name) {
  const all = list(cfg);
  const k = key(name);
  if (!k) return null;
  return all.find((p) => key(p.ten) === k)
    || all.find((p) => key(p.ten).startsWith(k))
    || all.find((p) => key(p.ten).includes(k))
    || all.find((p) => k.includes(key(p.ten).slice(0, 6)) && key(p.ten).length >= 6)
    || null;
}

// Thư mục transcript của Claude Code cho một cwd: mọi ký tự không phải chữ/số thành '-'
function sessionsDir(dir) {
  const enc = path.resolve(dir).replace(/[^a-zA-Z0-9]/g, '-');
  return path.join(process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude'), 'projects', enc);
}

function lastSession(dir) {
  const sd = sessionsDir(dir);
  let files = [];
  try { files = fs.readdirSync(sd).filter((f) => f.endsWith('.jsonl')).map((f) => ({ f, t: fs.statSync(path.join(sd, f)).mtimeMs })); } catch { return null; }
  if (!files.length) return null;
  files.sort((a, b) => b.t - a.t);
  const { f, t } = files[0];
  const tail = readTail(path.join(sd, f), 200000).split('\n').filter(Boolean);
  let lastText = '';
  let lastAsk = '';
  for (let i = tail.length - 1; i >= 0 && (!lastText || !lastAsk); i--) {
    let ev;
    try { ev = JSON.parse(tail[i]); } catch { continue; }
    const m = ev.message;
    if (!m) continue;
    const text = typeof m.content === 'string' ? m.content
      : Array.isArray(m.content) ? m.content.filter((c) => c.type === 'text').map((c) => c.text).join(' ') : '';
    if (!text.trim()) continue;
    if (ev.type === 'assistant' && !lastText) lastText = text;
    if (ev.type === 'user' && !lastAsk && !text.startsWith('<')) lastAsk = text;
  }
  return { session_id: f.replace(/\.jsonl$/, ''), luc: new Date(t).toISOString(), cau_hoi_cuoi: clean(lastAsk).slice(0, 300), tra_loi_cuoi: clean(lastText).slice(0, 600) };
}

function summary(p) {
  let tom_tat = '';
  for (const f of SUMMARY_FILES) {
    const s = readHead(path.join(p.thu_muc, f), 1500);
    if (s) { tom_tat = clean(s).slice(0, 700); break; }
  }
  const log = clean(readTail(path.join(p.thu_muc, 'LOG.md'), 900)).slice(-600);
  let sua_luc = null;
  try { sua_luc = new Date(fs.statSync(p.thu_muc).mtimeMs).toISOString(); } catch {}
  return { ten: p.ten, tom_tat, nhat_ky_cuoi: log, sua_luc, phien_claude: lastSession(p.thu_muc) };
}

module.exports = { list, find, summary, lastSession, key, fold };
