#!/usr/bin/env node
// Hook SessionStart của linhx-core: bơm luật LINHX LAB, các lab gần đây và PLAN.md của lab đang đứng.
// Chỉ bơm khi thư mục làm việc nằm trong LINHX (hoặc có biến LINHX_HOME). Luôn exit 0.
const path = require('path');
const { readStdin, parseJson, locate, recentLabs, rulesText, dataBlock, planHead, emit } = require('./lib');

function buildContext(cwd) {
  const where = locate(cwd);
  if (!where.linhx) return '';
  const parts = [rulesText()];

  const labs = recentLabs(where.labRoot);
  if (labs.length) {
    parts.push('## Các lab gần đây\n' + labs.map((l) => `- ${l.name} (${l.status})`).join('\n'));
  }

  if (where.lab) {
    const name = path.basename(where.lab);
    const plan = planHead(where.lab);
    if (plan) {
      parts.push(`## Lab đang làm: ${name}\n` + dataBlock('PLAN.md', plan) +
        '\nĐọc toàn bộ PLAN.md và phần cuối LOG.md trước khi làm tiếp.');
    } else {
      parts.push(`## Lab đang làm: ${name}\nLab này chưa có PLAN.md. Nếu việc có từ 3 bước trở lên, dùng skill ke-hoach-lab để tạo.`);
    }
  }
  return parts.join('\n\n');
}

module.exports = { buildContext };

if (require.main === module) {
  setTimeout(() => { process.stdout.write('{}\n'); process.exit(0); }, 4000).unref();
  (async () => {
    const input = parseJson(await readStdin());
    try { emit('SessionStart', buildContext(input.cwd || process.cwd())); } catch { emit('SessionStart', ''); }
  })();
}
