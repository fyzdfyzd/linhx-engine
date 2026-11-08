#!/usr/bin/env node
// linhx-tu-duy: thư viện thẻ mental model + nhật ký quyết định + thẻ của ngày + chấm tuần.
// Không phụ thuộc thư viện ngoài. Dữ liệu cá nhân là file text trong một thư mục của Linh.
'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');

const ROOT = path.resolve(__dirname, '..');
const THE_GOC = path.join(ROOT, 'the');
const CAU_HINH = path.join(os.homedir(), '.linhx-tu-duy.json');
const THE_DAO_NGUOC = ['B5', 'M8', 'C6']; // nhóm "tìm cách thất bại", luôn có một thẻ khi quyết định

// ---------- tiện ích ----------
const homNay = () => new Date().toISOString().slice(0, 10);
const soNgay = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);
function loi(msg) { console.error('LỖI: ' + msg); process.exit(1); }

function thamSo(argv) {
  const pos = [], opt = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      opt[k] = v;
    } else pos.push(a);
  }
  return { pos, opt };
}

function thuMucDuLieu(opt) {
  if (opt.dir) return path.resolve(opt.dir);
  if (process.env.LINHX_TU_DUY_DIR) return path.resolve(process.env.LINHX_TU_DUY_DIR);
  if (fs.existsSync(CAU_HINH)) return JSON.parse(fs.readFileSync(CAU_HINH, 'utf8')).dir;
  return path.join(os.homedir(), 'linhx-tu-duy');
}

function docFrontmatter(file) {
  const txt = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
  const m = txt.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!m) return { meta: {}, body: txt };
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
    const k = line.match(/^([\w_]+):\s*(.*)$/);
    if (!k) continue;
    let v = k[2].trim();
    try { v = JSON.parse(v); } catch (_) { v = v.replace(/^["']|["']$/g, ''); }
    meta[k[1]] = v;
  }
  return { meta, body: m[2] };
}

// ---------- thẻ ----------
function napThe(dir) {
  const bo = new Map();
  const nap = (thuMuc, rieng) => {
    if (!fs.existsSync(thuMuc)) return;
    for (const f of fs.readdirSync(thuMuc)) {
      if (!f.endsWith('.md') || f.startsWith('_')) continue;
      const file = path.join(thuMuc, f);
      const { meta, body } = docFrontmatter(file);
      if (!meta.ma) continue;
      const ma = String(meta.ma).toUpperCase();
      bo.set(ma, { ...meta, ma, body, file, rieng }); // thẻ riêng đè thẻ gốc cùng mã
    }
  };
  nap(THE_GOC, false);
  nap(path.join(dir, 'the-rieng'), true);
  return bo;
}

// ---------- sự kiện (chỉ thêm, không sửa) ----------
const fileSuKien = (dir) => path.join(dir, 'su-kien.jsonl');
function docSuKien(dir) {
  const f = fileSuKien(dir);
  if (!fs.existsSync(f)) return [];
  return fs.readFileSync(f, 'utf8').split(/\r?\n/).filter(Boolean).map((l) => JSON.parse(l));
}
function ghiSuKien(dir, ev) {
  ev = { ts: new Date().toISOString(), ...ev };
  fs.appendFileSync(fileSuKien(dir), JSON.stringify(ev) + '\n', 'utf8');
  return ev;
}
function canThuMuc(dir) {
  if (!fs.existsSync(dir)) loi(`chưa có thư mục dữ liệu ${dir}. Chạy: tu-duy.js init --dir <thư mục>`);
}

// mã thẻ mà một sự kiện "đã dùng"
function theDaDung(ev) {
  if (ev.loai === 'ghi-ngay' || ev.loai === 'vi-du') return [ev.ma];
  if (ev.loai === 'quyet') return ev.the || [];
  if (ev.loai === 'cham') return ev.the_giup || [];
  return [];
}

function thongKe(dir, bo) {
  const evs = docSuKien(dir);
  const tk = {};
  for (const ma of bo.keys()) tk[ma] = { lan: 0, cuoi: null, lan30: 0 };
  const today = homNay();
  for (const ev of evs) {
    for (const ma0 of theDaDung(ev)) {
      const ma = String(ma0).toUpperCase();
      if (!tk[ma]) continue;
      tk[ma].lan++;
      const d = ev.ts.slice(0, 10);
      if (!tk[ma].cuoi || d > tk[ma].cuoi) tk[ma].cuoi = d;
      if (soNgay(d, today) <= 30) tk[ma].lan30++;
    }
  }
  return { evs, tk };
}

function quyetDinh(evs) {
  const ds = evs.filter((e) => e.loai === 'quyet');
  const cham = new Map(evs.filter((e) => e.loai === 'cham').map((e) => [e.id, e]));
  return ds.map((q) => ({ ...q, cham: cham.get(q.id) || null }));
}

// ---------- lệnh ----------
const LENH = {};

LENH.init = ({ opt }) => {
  let dir = opt.dir;
  if (opt.linhx) dir = 'D:/LINHX/MENTAL-MODEL';
  if (!dir) loi('cần --dir <thư mục> hoặc --linhx');
  dir = path.resolve(dir);
  fs.mkdirSync(path.join(dir, 'the-rieng'), { recursive: true });
  for (const [f, tieuDe] of [['nhat-ky-quyet-dinh.md', '# Nhật ký quyết định\n\nChỉ thêm, không sửa phần đã ghi.\n'],
                              ['the-hang-ngay.md', '# Thẻ của ngày\n'],
                              ['ngu-lap-lai.md', '# Ngu lặp lại (tối đa 7 dòng, xem thẻ M8)\n\n1. \n']]) {
    const p = path.join(dir, f);
    if (!fs.existsSync(p)) fs.writeFileSync(p, tieuDe, 'utf8');
  }
  if (!fs.existsSync(fileSuKien(dir))) fs.writeFileSync(fileSuKien(dir), '', 'utf8');
  fs.writeFileSync(CAU_HINH, JSON.stringify({ dir }, null, 2), 'utf8');
  console.log(`Đã tạo thư mục dữ liệu: ${dir}`);
  console.log(`Đã lưu cấu hình: ${CAU_HINH}`);
  console.log(`Thẻ gốc: ${napThe(dir).size} thẻ`);
};

LENH.index = ({ opt }) => {
  const dir = thuMucDuLieu(opt);
  const bo = napThe(dir);
  const { tk } = thongKe(dir, bo);
  const rows = [...bo.values()].filter((t) => !opt.bo || t.bo === opt.bo);
  console.log('| Mã | Tên | Bộ | Nhóm | Câu kích hoạt | Lần dùng | Lần cuối |');
  console.log('|---|---|---|---|---|---|---|');
  for (const t of rows) {
    const s = tk[t.ma] || {};
    console.log(`| ${t.ma}${t.rieng ? '*' : ''} | ${t.ten} | ${t.bo || 'rieng'} | ${t.nhom || ''} | ${t.cau_kich_hoat || ''} | ${s.lan || 0} | ${s.cuoi || '-'} |`);
  }
  console.log(`\n${rows.length} thẻ. Dấu * là thẻ riêng của Linh. Thẻ kiểu đảo ngược: ${THE_DAO_NGUOC.join(', ')}.`);
};

function inThe(dir, ma) {
  const bo = napThe(dir);
  const t = bo.get(String(ma).toUpperCase());
  if (!t) loi(`không có thẻ ${ma}`);
  console.log(t.body.trim());
  const vd = docSuKien(dir).filter((e) => (e.loai === 'vi-du' || e.loai === 'ghi-ngay') && String(e.ma).toUpperCase() === t.ma);
  const qd = quyetDinh(docSuKien(dir)).filter((q) => (q.the || []).map((x) => x.toUpperCase()).includes(t.ma));
  console.log('\n## Ví dụ của Linh');
  if (!vd.length && !qd.length) console.log('(chưa có, ghi bằng: tu-duy.js vi-du ' + t.ma + ' "...")');
  for (const e of vd) console.log(`- ${e.ts.slice(0, 10)} · ${e.noi_dung}`);
  for (const q of qd) console.log(`- ${q.ts.slice(0, 10)} · quyết định ${q.id}: ${q.cau_hoi} → ${q.quyet_dinh}${q.cham ? ` [chấm: ${q.cham.dung}]` : ''}`);
}
LENH.show = ({ pos, opt }) => { if (!pos[0]) loi('cần mã thẻ'); inThe(thuMucDuLieu(opt), pos[0]); };

LENH.ngay = ({ opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  const bo = napThe(dir);
  const { evs, tk } = thongKe(dir, bo);
  const today = homNay();
  const daBoc = evs.find((e) => e.loai === 'ngay' && e.ts.slice(0, 10) === today);
  let ma, lyDo;
  if (daBoc && !opt.lai) { ma = daBoc.ma; lyDo = 'đã bốc sáng nay'; }
  else {
    // 1) thẻ của quyết định tới hạn chấm
    const toiHan = quyetDinh(evs).filter((q) => !q.cham && q.ngay_cham && q.ngay_cham <= today);
    const ungVien = toiHan.flatMap((q) => q.the || []).map((x) => x.toUpperCase()).filter((x) => bo.has(x));
    // các thẻ bốc trong 7 ngày qua thì tránh
    const ganDay = new Set(evs.filter((e) => e.loai === 'ngay' && soNgay(e.ts.slice(0, 10), today) < 7).map((e) => e.ma));
    if (ungVien.length) { ma = ungVien.find((x) => !ganDay.has(x)) || ungVien[0]; lyDo = 'có quyết định dùng thẻ này đã tới hạn chấm'; }
    else {
      // 2) thẻ lâu chưa dùng nhất; chưa dùng bao giờ đứng đầu; hoà thì xáo theo ngày để mỗi ngày khác nhau
      const seed = [...today].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);
      const ds = [...bo.keys()].filter((x) => !ganDay.has(x) && (!opt.bo || bo.get(x).bo === opt.bo));
      ds.sort((a, b) => {
        const ca = tk[a].cuoi || '0000', cb = tk[b].cuoi || '0000';
        if (ca !== cb) return ca < cb ? -1 : 1;
        const h = (s) => { let x = seed ^ 0x9e3779b9; for (const c of s) { x = Math.imul(x ^ c.charCodeAt(0), 0x85ebca6b); x ^= x >>> 13; x = Math.imul(x, 0xc2b2ae35); x ^= x >>> 16; } return x >>> 0; };
        return h(a) - h(b);
      });
      ma = ds[0]; lyDo = tk[ma].cuoi ? `lâu chưa dùng (lần cuối ${tk[ma].cuoi})` : 'chưa dùng lần nào';
    }
    ghiSuKien(dir, { loai: 'ngay', ma });
    fs.appendFileSync(path.join(dir, 'the-hang-ngay.md'), `\n- ${today} · ${ma} ${bo.get(ma).ten} · tối: `, 'utf8');
  }
  console.log(`THẺ CỦA NGÀY ${today}: ${ma} (${lyDo})\n`);
  inThe(dir, ma);
  console.log(`\nTối ghi một câu: tu-duy.js ghi-ngay ${ma} "hôm nay thẻ này xuất hiện ở ..."`);
};

LENH['ghi-ngay'] = ({ pos, opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  const [ma, ...rest] = pos; const nd = rest.join(' ');
  if (!ma || !nd) loi('cần: ghi-ngay <mã> "<một câu>"');
  if (!napThe(dir).has(ma.toUpperCase())) loi(`không có thẻ ${ma}`);
  ghiSuKien(dir, { loai: 'ghi-ngay', ma: ma.toUpperCase(), noi_dung: nd });
  fs.appendFileSync(path.join(dir, 'the-hang-ngay.md'), `\n  - ${homNay()} · ${ma.toUpperCase()}: ${nd}`, 'utf8');
  console.log('Đã ghi.');
};

LENH['vi-du'] = ({ pos, opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  const [ma, ...rest] = pos; const nd = rest.join(' ');
  if (!ma || !nd) loi('cần: vi-du <mã> "<tình huống → cách dùng → kết quả>"');
  if (!napThe(dir).has(ma.toUpperCase())) loi(`không có thẻ ${ma}`);
  ghiSuKien(dir, { loai: 'vi-du', ma: ma.toUpperCase(), noi_dung: nd });
  console.log(`Đã thêm ví dụ vào thẻ ${ma.toUpperCase()}.`);
};

const TRUONG_QUYET = ['cau_hoi', 'boi_canh', 'lua_chon', 'the', 'lap_luan', 'quyet_dinh', 'do_chac', 'doi_y_neu', 'ngay_cham'];
LENH.quyet = ({ opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  let q;
  try { q = JSON.parse(opt.file ? fs.readFileSync(opt.file, 'utf8') : opt.json); }
  catch (e) { loi('cần --json \'{...}\' hoặc --file <file.json> hợp lệ: ' + e.message); }
  const thieu = TRUONG_QUYET.filter((k) => q[k] === undefined || q[k] === '' || (Array.isArray(q[k]) && !q[k].length));
  if (thieu.length) loi('thiếu trường: ' + thieu.join(', '));
  if (!Array.isArray(q.lua_chon) || q.lua_chon.length < 2) loi('lua_chon cần ít nhất 2 phương án (kể cả phương án tốt nhất bị bỏ, thẻ M6)');
  const bo = napThe(dir);
  q.the = q.the.map((x) => String(x).toUpperCase());
  const la = q.the.filter((x) => !bo.has(x));
  if (la.length) loi('mã thẻ không có: ' + la.join(', '));
  if (q.the.length > 3) loi('tối đa 3 thẻ cho một quyết định');
  const p = Number(q.do_chac); if (!(p > 0 && p <= 1)) loi('do_chac là số 0–1, ví dụ 0.7');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(q.ngay_cham)) loi('ngay_cham dạng YYYY-MM-DD');
  const today = homNay().replace(/-/g, '');
  const n = docSuKien(dir).filter((e) => e.loai === 'quyet' && e.id.startsWith('Q-' + today)).length + 1;
  const ev = ghiSuKien(dir, { loai: 'quyet', id: `Q-${today}-${n}`, ...Object.fromEntries(TRUONG_QUYET.map((k) => [k, q[k]])), do_chac: p });
  const md = `\n### ${ev.id} · ${homNay()} · ${q.cau_hoi}\n- Bối cảnh: ${q.boi_canh}\n- Lựa chọn: ${q.lua_chon.join(' / ')}\n- Thẻ dùng: ${q.the.map((x) => `${x} ${bo.get(x).ten}`).join(', ')}\n- Lập luận: ${q.lap_luan}\n- Quyết định: ${q.quyet_dinh}\n- Độ chắc: ${Math.round(p * 100)}%\n- Điều làm mình đổi ý: ${q.doi_y_neu}\n- Ngày chấm: ${q.ngay_cham}\n`;
  fs.appendFileSync(path.join(dir, 'nhat-ky-quyet-dinh.md'), md, 'utf8');
  console.log(`Đã ghi ${ev.id}, chấm vào ${q.ngay_cham}.`);
};

LENH.cham = ({ pos, opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  const id = pos[0]; if (!id) loi('cần mã quyết định, ví dụ Q-20261013-1');
  const evs = docSuKien(dir);
  const q = quyetDinh(evs).find((x) => x.id === id);
  if (!q) loi(`không có quyết định ${id}`);
  if (q.cham) loi(`${id} đã chấm rồi (không sửa). Muốn bổ sung thì dùng vi-du.`);
  if (!['dung', 'sai', 'mot-phan'].includes(opt.dung)) loi('--dung dung|sai|mot-phan');
  if (!opt['ket-qua']) loi('cần --ket-qua "..."');
  const giup = opt['the-giup'] && opt['the-giup'] !== true ? String(opt['the-giup']).split(',').map((x) => x.trim().toUpperCase()) : [];
  const nhieu = opt['the-nhieu'] && opt['the-nhieu'] !== true ? String(opt['the-nhieu']).split(',').map((x) => x.trim().toUpperCase()) : [];
  ghiSuKien(dir, { loai: 'cham', id, dung: opt.dung, ket_qua: opt['ket-qua'], bai_hoc: opt['bai-hoc'] || '', the_giup: giup, the_nhieu: nhieu });
  fs.appendFileSync(path.join(dir, 'nhat-ky-quyet-dinh.md'),
    `\n--- chấm ${id} ngày ${homNay()}\n- Kết quả: ${opt['ket-qua']}\n- Đúng/sai: ${opt.dung} (độ chắc lúc quyết: ${Math.round(q.do_chac * 100)}%)\n- Thẻ giúp: ${giup.join(', ') || '-'} · Thẻ gây nhiễu: ${nhieu.join(', ') || '-'}\n- Bài học: ${opt['bai-hoc'] || '-'}\n`, 'utf8');
  console.log(`Đã chấm ${id}.`);
};

LENH.tuan = ({ opt }) => {
  const dir = thuMucDuLieu(opt); canThuMuc(dir);
  const bo = napThe(dir);
  const { evs, tk } = thongKe(dir, bo);
  const today = homNay();
  const qs = quyetDinh(evs);
  console.log(`# Chấm tuần ${today}\n`);
  console.log('## 1. Chấm trước: quyết định đã tới hạn');
  const toiHan = qs.filter((q) => !q.cham && q.ngay_cham <= today);
  if (!toiHan.length) console.log('Không có quyết định nào tới hạn.');
  for (const q of toiHan) console.log(`- ${q.id} (hạn ${q.ngay_cham}, chắc ${Math.round(q.do_chac * 100)}%): ${q.cau_hoi} → ${q.quyet_dinh}. Đổi ý nếu: ${q.doi_y_neu}`);
  const sapToi = qs.filter((q) => !q.cham && q.ngay_cham > today).sort((a, b) => (a.ngay_cham < b.ngay_cham ? -1 : 1)).slice(0, 5);
  if (sapToi.length) console.log('Sắp tới hạn: ' + sapToi.map((q) => `${q.id} (${q.ngay_cham})`).join(', '));

  console.log('\n## 2. Thẻ dùng 7 ngày qua');
  const tuan = {};
  for (const ev of evs.filter((e) => soNgay(e.ts.slice(0, 10), today) < 7)) for (const ma of theDaDung(ev)) tuan[ma] = (tuan[ma] || 0) + 1;
  const dsTuan = Object.entries(tuan).sort((a, b) => b[1] - a[1]);
  console.log(dsTuan.length ? dsTuan.map(([m, n]) => `${m} ${bo.get(m) ? bo.get(m).ten : ''} ×${n}`).join(' · ') : 'Chưa dùng thẻ nào.');

  const tong = bo.size, phu = Object.values(tk).filter((s) => s.lan30 > 0).length;
  console.log(`\n## 3. Độ phủ 30 ngày: ${phu}/${tong} thẻ (${Math.round((phu / tong) * 100)}%, mục tiêu ≥ 60%)`);
  const quen = [...bo.keys()].sort((a, b) => ((tk[a].cuoi || '0') < (tk[b].cuoi || '0') ? -1 : 1)).slice(0, 5);
  console.log('Thẻ bị bỏ quên lâu nhất (ưu tiên bốc tuần sau): ' + quen.map((m) => `${m} ${bo.get(m).ten}${tk[m].cuoi ? ` (${tk[m].cuoi})` : ''}`).join(' · '));

  console.log('\n## 4. Hiệu chỉnh (quyết định đã chấm)');
  const daCham = qs.filter((q) => q.cham);
  if (!daCham.length) console.log('Chưa có quyết định nào được chấm.');
  else {
    const nhom = { 'dưới 60%': [], '60–79%': [], 'từ 80%': [] };
    for (const q of daCham) nhom[q.do_chac < 0.6 ? 'dưới 60%' : q.do_chac < 0.8 ? '60–79%' : 'từ 80%'].push(q);
    for (const [k, v] of Object.entries(nhom)) {
      if (!v.length) continue;
      const diem = v.reduce((s, q) => s + (q.cham.dung === 'dung' ? 1 : q.cham.dung === 'mot-phan' ? 0.5 : 0), 0) / v.length;
      console.log(`- Độ chắc ${k}: ${v.length} quyết định, đúng ${Math.round(diem * 100)}%`);
    }
    const giup = {}, nhieu = {};
    for (const q of daCham) { for (const m of q.cham.the_giup || []) giup[m] = (giup[m] || 0) + 1; for (const m of q.cham.the_nhieu || []) nhieu[m] = (nhieu[m] || 0) + 1; }
    if (Object.keys(giup).length) console.log('Thẻ hay giúp: ' + Object.entries(giup).sort((a, b) => b[1] - a[1]).map(([m, n]) => `${m}×${n}`).join(', '));
    if (Object.keys(nhieu).length) console.log('Thẻ hay gây nhiễu: ' + Object.entries(nhieu).sort((a, b) => b[1] - a[1]).map(([m, n]) => `${m}×${n}`).join(', '));
  }
};

LENH.help = () => {
  console.log(`tu-duy.js <lệnh>
  init --dir <thư mục> | --linhx     tạo thư mục dữ liệu (Linh: D:/LINHX/MENTAL-MODEL)
  index [--bo naval|munger-fs]       bảng mọi thẻ kèm câu kích hoạt và số lần dùng
  show <mã>                          in thẻ kèm ví dụ của Linh
  ngay [--lai]                       bốc thẻ của ngày
  ghi-ngay <mã> "<câu>"              tối ghi thẻ xuất hiện ở đâu
  vi-du <mã> "<ví dụ>"               thêm ví dụ thật vào thẻ
  quyet --json '{...}' | --file f    ghi quyết định (trường: ${TRUONG_QUYET.join(', ')})
  cham <id> --dung dung|sai|mot-phan --ket-qua "..." [--bai-hoc "..."] [--the-giup B3,C7] [--the-nhieu M5]
  tuan                               chấm tuần: tới hạn, độ phủ, thẻ bị quên, hiệu chỉnh
Thêm --dir <thư mục> vào bất kỳ lệnh nào để dùng thư mục khác.`);
};

const [cmd, ...rest] = process.argv.slice(2);
(LENH[cmd] || LENH.help)(thamSo(rest));
