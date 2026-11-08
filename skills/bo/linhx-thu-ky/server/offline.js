// Chế độ không có khoá Gemini: chỉ gõ chữ, hiểu vài mẫu câu cố định, trình duyệt tự đọc bằng giọng máy.
// Đủ để thử luồng giao việc cho Claude và xem nhân vật chuyển động khi chưa cấu hình Gemini.
//   "dự án"                         → danh sách dự án
//   "tình hình LAB025"              → tình hình một dự án
//   "ai đang làm"                   → agent đang chạy + việc đã giao
//   "hỏi LAB025: câu hỏi"           → hoi_claude
//   "giao LAB025: nội dung"         → giao_viec
//   "kết quả 3" / "dừng 3"          → ket_qua_viec / dung_viec

const tools = require('./tools');
const { fold } = require('./projects');

function parse(text) {
  const t = String(text || '').trim();
  const f = fold(t);
  let m;
  if ((m = /^(hoi|giao)\s+(.+?)\s*:\s*([\s\S]+)$/.exec(f))) {
    const head = t.slice(0, t.indexOf(':'));
    const du_an = head.replace(/^\S+\s+/, '').trim();
    const body = t.slice(t.indexOf(':') + 1).trim();
    return m[1] === 'hoi' ? ['hoi_claude', { du_an, cau_hoi: body }] : ['giao_viec', { du_an, noi_dung: body }];
  }
  if ((m = /^(ket qua|dung)\s*(?:viec\s*)?(?:so\s*)?(\d+)/.exec(f))) return [m[1] === 'dung' ? 'dung_viec' : 'ket_qua_viec', { so: Number(m[2]) }];
  if ((m = /^tinh hinh\s+(.+)$/.exec(f))) return ['tinh_hinh_du_an', { du_an: t.split(/\s+/).slice(2).join(' ') }];
  if (/ai dang|dang chay|dang lam/.test(f)) return ['agent_dang_chay', {}];
  if (/du an/.test(f)) return ['danh_sach_du_an', {}];
  return null;
}

async function handle(raw, ctx) {
  let msg;
  try { msg = JSON.parse(raw); } catch { return; }
  const parts = msg && msg.clientContent && msg.clientContent.turns && msg.clientContent.turns[0] && msg.clientContent.turns[0].parts;
  const text = parts && parts[0] && parts[0].text;
  if (!text) return;
  const cmd = parse(text);
  if (!cmd) {
    ctx.say('Chế độ chưa có Gemini nên em chỉ hiểu các câu: dự án; tình hình tên dự án; ai đang làm; hỏi tên dự án hai chấm câu hỏi; giao tên dự án hai chấm việc cần làm; kết quả số việc.');
    return;
  }
  try { ctx.say(await tools.run(cmd[0], cmd[1], ctx)); }
  catch (e) { ctx.say(e.message); }
}

function report(j) {
  return `Báo cáo anh Linh: ${tools.fmtJob(j)}. ${(j.ket_qua || '').replace(/\s+/g, ' ').slice(0, 400)}`;
}

module.exports = { handle, parse, report };
