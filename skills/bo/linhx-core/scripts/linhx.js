#!/usr/bin/env node
// Công cụ dòng lệnh của linhx-core. Chỉ dùng thư viện chuẩn của Node.
//   node linhx.js context [thư-mục]   In đoạn luật mà hook mở phiên sẽ bơm (để xem thử)
//   node linhx.js lint                Kiểm mọi SKILL.md trong marketplace: có name, có "Dùng khi" trong description
//   node linhx.js agy-install         Chép skill sang Antigravity và ghi luật vào ~/.gemini/GEMINI.md
//   node linhx.js agy-uninstall       Gỡ những gì agy-install đã ghi
const fs = require('fs');
const os = require('os');
const path = require('path');
const { buildContext } = require('../hooks/khoi-dong');
const { rulesText } = require('../hooks/lib');

const PLUGIN_ROOT = path.join(__dirname, '..');
const MARKET_ROOT = path.join(PLUGIN_ROOT, '..');
const AGY_SKILLS = path.join(os.homedir(), '.gemini', 'antigravity', 'skills');
const GEMINI_MD = path.join(os.homedir(), '.gemini', 'GEMINI.md');
const MARK_A = '<!-- linhx-core:bat-dau -->';
const MARK_B = '<!-- linhx-core:ket-thuc -->';

function allSkills() {
  const out = [];
  let plugins = [];
  try { plugins = fs.readdirSync(MARKET_ROOT).filter((p) => p.startsWith('linhx-')); } catch {}
  for (const p of plugins) {
    const dir = path.join(MARKET_ROOT, p, 'skills');
    let names = [];
    try { names = fs.readdirSync(dir); } catch { continue; }
    for (const n of names) {
      const f = path.join(dir, n, 'SKILL.md');
      if (fs.existsSync(f)) out.push({ plugin: p, name: n, dir: path.join(dir, n), file: f });
    }
  }
  return out;
}

function frontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const fm = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^(\w[\w-]*):\s*(.*)$/);
    if (kv) fm[kv[1]] = kv[2].trim();
  }
  return fm;
}

function lint() {
  let bad = 0;
  const skills = allSkills();
  for (const s of skills) {
    const fm = frontmatter(fs.readFileSync(s.file, 'utf8'));
    const errs = [];
    if (!fm) errs.push('thiếu frontmatter');
    else {
      if (fm.name !== s.name) errs.push(`name "${fm.name}" khác tên thư mục "${s.name}"`);
      if (!fm.description) errs.push('thiếu description');
      else {
        if (!/Dùng khi/i.test(fm.description)) errs.push('description thiếu cụm "Dùng khi …"');
        if (fm.description.length > 1024) errs.push('description dài quá 1024 ký tự');
      }
    }
    if (errs.length) { bad++; console.log(`LỖI  ${s.plugin}/${s.name}: ${errs.join('; ')}`); }
    else console.log(`ĐẠT  ${s.plugin}/${s.name}`);
  }
  console.log(`${skills.length} skill, ${bad} lỗi`);
  process.exitCode = bad ? 1 : 0;
}

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const a = path.join(src, e.name), b = path.join(dst, e.name);
    if (e.isDirectory()) copyDir(a, b);
    else if (e.isFile()) fs.copyFileSync(a, b);
  }
}

function stripBlock(text) {
  const i = text.indexOf(MARK_A), j = text.indexOf(MARK_B);
  if (i < 0 || j < 0) return text;
  return (text.slice(0, i) + text.slice(j + MARK_B.length)).replace(/\n{3,}/g, '\n\n');
}

function agyInstall() {
  // Bỏ skill /linhx (chỉ dành cho Claude Code). Đổi name trong frontmatter cho khớp tên thư mục linhx-<tên>.
  const skills = allSkills().filter((s) => s.name !== 'linhx');
  for (const s of skills) {
    const dst = path.join(AGY_SKILLS, 'linhx-' + s.name);
    fs.rmSync(dst, { recursive: true, force: true });
    copyDir(s.dir, dst);
    const f = path.join(dst, 'SKILL.md');
    fs.writeFileSync(f, fs.readFileSync(f, 'utf8').replace(/^(---\r?\n[\s\S]*?)^name:\s*.*$/m, `$1name: linhx-${s.name}`));
    console.log(`Đã chép skill ${s.name} → ${dst}`);
  }
  fs.mkdirSync(path.dirname(GEMINI_MD), { recursive: true });
  let old = '';
  try { old = fs.readFileSync(GEMINI_MD, 'utf8'); } catch {}
  if (old && !fs.existsSync(GEMINI_MD + '.bak-linhx-core')) fs.writeFileSync(GEMINI_MD + '.bak-linhx-core', old);
  const block = `${MARK_A}\n${rulesText()}\n\nSkill LINHX nằm trong ${AGY_SKILLS} (tên bắt đầu bằng linhx-). Khi làm trong một lab, đọc PLAN.md và cuối LOG.md trước.\n${MARK_B}`;
  fs.writeFileSync(GEMINI_MD, (stripBlock(old).trimEnd() + '\n\n' + block + '\n').trimStart());
  console.log(`Đã ghi luật LINHX vào ${GEMINI_MD}`);
}

function agyUninstall() {
  for (const s of allSkills()) {
    const dst = path.join(AGY_SKILLS, 'linhx-' + s.name);
    if (fs.existsSync(dst)) { fs.rmSync(dst, { recursive: true, force: true }); console.log(`Đã gỡ ${dst}`); }
  }
  try {
    const old = fs.readFileSync(GEMINI_MD, 'utf8');
    fs.writeFileSync(GEMINI_MD, stripBlock(old));
    console.log(`Đã gỡ khối luật LINHX khỏi ${GEMINI_MD}`);
  } catch {}
}

const [cmd, arg] = process.argv.slice(2);
if (cmd === 'context') console.log(buildContext(arg || process.cwd()) || '(Không nằm trong LINHX: hook sẽ không bơm gì)');
else if (cmd === 'lint') lint();
else if (cmd === 'agy-install') agyInstall();
else if (cmd === 'agy-uninstall') agyUninstall();
else console.log('Dùng: node linhx.js context [thư-mục] | lint | agy-install | agy-uninstall');
