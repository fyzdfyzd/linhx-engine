#!/usr/bin/env node
// Hook UserPromptSubmit của linhx-core: nhắc 20 dòng đầu PLAN.md của lab đang đứng.
// Chỉ nhắc khi PLAN.md vừa đổi, hoặc sau mỗi LINHX_PLAN_EVERY lượt (mặc định 6), để tiết kiệm token.
// Tắt hẳn bằng LINHX_PLAN_NHAC=0. Luôn exit 0.
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { readStdin, parseJson, locate, dataBlock, planHead, emit } = require('./lib');

const EVERY = Math.max(1, Number(process.env.LINHX_PLAN_EVERY || 6));

function cacheFile(sessionId) {
  const dir = path.join(os.tmpdir(), 'linhx-core');
  try { fs.mkdirSync(dir, { recursive: true }); } catch {}
  const key = String(sessionId || 'khong-ro').replace(/[^\w-]/g, '').slice(0, 64) || 'khong-ro';
  return path.join(dir, key + '.json');
}

setTimeout(() => { process.stdout.write('{}\n'); process.exit(0); }, 4000).unref();

(async () => {
  try {
    if (process.env.LINHX_PLAN_NHAC === '0') return emit('UserPromptSubmit', '');
    const input = parseJson(await readStdin());
    const where = locate(input.cwd || process.cwd());
    const plan = where.lab ? planHead(where.lab, 20) : '';
    if (!plan) return emit('UserPromptSubmit', '');

    const hash = crypto.createHash('sha256').update(where.lab + '\n' + plan).digest('hex');
    const file = cacheFile(input.session_id);
    let st = {};
    try { st = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
    const count = (st.count || 0) + 1;
    const due = st.hash !== hash || count >= EVERY;
    try { fs.writeFileSync(file, JSON.stringify({ hash, count: due ? 0 : count })); } catch {}
    if (!due) return emit('UserPromptSubmit', '');

    emit('UserPromptSubmit', `Nhắc kế hoạch của ${path.basename(where.lab)}:\n` + dataBlock('PLAN.md', plan) +
      '\nNếu lượt này làm xong một bước hoặc có quyết định mới, cập nhật PLAN.md và LOG.md.');
  } catch {
    emit('UserPromptSubmit', '');
  }
})();
