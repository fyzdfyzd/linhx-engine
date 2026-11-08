#!/usr/bin/env node
// Kiểm trang phim trước khi render: tất định, đứng hình, khung trống, chữ tràn, font thiếu dấu.
// Dùng: node kiem_khung.mjs <trang.html> [--goc <thư-mục-phục-vụ>] [--size 960x540] [--buoc 0.5] [--dur 30] [--out <thư-mục>]
// Trang phải có một trong: window.renderAt(t) | window.render(t) | window.seek(t) | window.anim.seek(t) | window.__timelines (GSAP).
// Thoát 1 nếu có LỖI. CẢNH BÁO thì sửa hoặc ghi lý do một dòng.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const trang = args.find(a => a.endsWith('.html'));
if (!trang) { console.error('Dùng: node kiem_khung.mjs <trang.html> [--goc dir] [--size WxH] [--buoc 0.5] [--dur s] [--out dir]'); process.exit(2); }
const goc = path.resolve(opt('--goc', path.dirname(trang)));
const [W, H] = opt('--size', '960x540').split('x').map(Number);
const buoc = Number(opt('--buoc', '0.5'));
const out = path.resolve(opt('--out', path.join(path.dirname(trang), 'kiem')));
fs.mkdirSync(path.join(out, 'khung'), { recursive: true });

// ---------- 1. Soát mã nguồn ----------
const loi = [], canh = [];
const ghi = (muc, ma, t, msg) => (muc === 'LOI' ? loi : canh).push({ ma, t, msg });
const nguon = fs.readFileSync(trang, 'utf8');
const scripts = [nguon];
for (const m of nguon.matchAll(/<script[^>]+src=["']([^"']+)["']/g)) {
  const src = m[1];
  if (/^https?:/.test(src)) { ghi('CANH', 'mang', null, `script tải từ mạng: ${src} (chép về thư mục phim)`); continue; }
  const p = src.startsWith('/') ? path.join(goc, src) : path.join(path.dirname(trang), src);
  if (fs.existsSync(p) && !/gsap|three|p5|min\.js/.test(p)) scripts.push(fs.readFileSync(p, 'utf8'));
}
for (const m of nguon.matchAll(/<link[^>]+href=["'](https?:[^"']+)["']/g)) ghi('CANH', 'mang', null, `tài nguyên từ mạng: ${m[1]}`);
const cam = [
  [/Math\.random\s*\(/, 'Math.random (dùng PRNG có seed, vd mulberry32)'],
  [/Date\.now\s*\(|new Date\s*\(/, 'Date (thời gian thật)'],
  [/performance\.now\s*\(/, 'performance.now'],
  [/setTimeout\s*\(|setInterval\s*\(/, 'setTimeout/setInterval'],
  [/@keyframes|animation\s*:|transition\s*:/, 'CSS animation/transition'],
];
for (const s of scripts) for (const [re, ten] of cam) if (re.test(s)) ghi('CANH', 'nguon', null, `mã có ${ten}; chỉ được dùng ngoài hàm vẽ theo t`);

// ---------- 2. Máy chủ tĩnh + trình duyệt ----------
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff2': 'font/woff2', '.woff': 'font/woff', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4' };
const sv = http.createServer((req, res) => {
  const p = path.join(goc, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(goc) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = sv.address().port;
const url = `http://127.0.0.1:${port}/${path.relative(goc, path.resolve(trang)).split(path.sep).join('/')}`;

const req = createRequire(import.meta.url);
let pw;
for (const m of ['playwright', 'playwright-core', process.env.PLAYWRIGHT_MODULE].filter(Boolean)) { try { pw = req(m); break; } catch {} }
if (!pw) { try { pw = req(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'playwright')); } catch {} }
if (!pw) { console.error('Thiếu playwright: npm i -g playwright (hoặc đặt PLAYWRIGHT_MODULE)'); process.exit(2); }
const browser = await pw.chromium.launch(process.env.PLAYWRIGHT_CHROME ? { executablePath: process.env.PLAYWRIGHT_CHROME } : {});
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 0.5 });
const loiTrang = [];
page.on('pageerror', e => loiTrang.push(String(e.message || e)));
page.on('console', m => { if (m.type() === 'error') loiTrang.push(m.text()); });
page.on('requestfailed', r => loiTrang.push('tải hỏng: ' + r.url()));
await page.addInitScript(() => {
  window.__QA = true;
  window.requestAnimationFrame = () => 0;           // không cho trang tự chạy đồng hồ
  const dem = window.__dem = { random: 0, gio: 0, hen: 0, dangSeek: false };
  const r = Math.random; Math.random = () => { if (dem.dangSeek) dem.random++; return r(); };
  const dn = Date.now; Date.now = () => { if (dem.dangSeek) dem.gio++; return dn(); };
  const pn = performance.now.bind(performance); performance.now = () => { if (dem.dangSeek) dem.gio++; return pn(); };
  const st = window.setTimeout; window.setTimeout = (...a) => { if (dem.dangSeek) dem.hen++; return st(...a); };
});
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.READY === true || window.READY === undefined, null, { timeout: 15000 }).catch(() => ghi('CANH', 'ready', null, 'window.READY không thành true sau 15 giây'));
await page.evaluate(() => document.fonts.ready);

const kieu = await page.evaluate(() => {
  const a = window.anim;
  const f = window.renderAt || window.render || window.seek || (a && a.seek && (t => a.seek(t))) ||
    (window.__timelines && (t => Object.values(window.__timelines).forEach(tl => tl.seek(t, false))));
  if (!f) return null;
  window.__seek = f;
  const tls = window.__timelines ? Object.values(window.__timelines) : [];
  const dur = window.DUR || window.DURATION || (a && a.duration) || (tls.length ? Math.max(...tls.map(tl => tl.duration())) : 0);
  return { ten: window.renderAt ? 'renderAt' : window.render ? 'render' : window.seek ? 'seek' : a ? 'anim.seek' : '__timelines', dur };
});
if (!kieu) { console.error('LỖI: trang không có renderAt/render/seek/anim.seek/__timelines, không kiểm được.'); await browser.close(); sv.close(); process.exit(1); }
const DUR = Number(opt('--dur', kieu.dur));
if (!(DUR > 0)) { console.error('LỖI: không biết độ dài phim, thêm window.DUR hoặc --dur'); await browser.close(); sv.close(); process.exit(1); }

// ---------- 3. Giải mã PNG (không cần thư viện) ----------
function docPNG(buf) {
  let o = 8, w, h, ct, idat = [];
  while (o < buf.length) {
    const len = buf.readUInt32BE(o), type = buf.toString('ascii', o + 4, o + 8), d = buf.subarray(o + 8, o + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; }
    if (type === 'IDAT') idat.push(d);
    o += 12 + len;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat)), bpp = ct === 6 ? 4 : 3, st = w * bpp;
  const px = Buffer.alloc(h * st);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (st + 1)], r = raw.subarray(y * (st + 1) + 1, (y + 1) * (st + 1)), row = px.subarray(y * st, (y + 1) * st), up = y ? px.subarray((y - 1) * st, y * st) : null;
    for (let x = 0; x < st; x++) {
      const a = x >= bpp ? row[x - bpp] : 0, b = up ? up[x] : 0, c = up && x >= bpp ? up[x - bpp] : 0;
      let v = r[x];
      if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      row[x] = v & 255;
    }
  }
  return { w, h, bpp, px };
}
const nen = (im) => { // màu nền = màu hay gặp nhất (lượng tử 16 mức)
  const m = new Map(); for (let i = 0; i < im.px.length; i += im.bpp * 7) { const k = (im.px[i] >> 4) << 8 | (im.px[i + 1] >> 4) << 4 | im.px[i + 2] >> 4; m.set(k, (m.get(k) || 0) + 1); }
  return [...m.entries()].sort((a, b) => b[1] - a[1])[0][0];
};
const phu = (im) => { const k = nen(im); let n = 0, t = 0; for (let i = 0; i < im.px.length; i += im.bpp * 3) { t++; if (((im.px[i] >> 4) << 8 | (im.px[i + 1] >> 4) << 4 | im.px[i + 2] >> 4) !== k) n++; } return n / t; };
const khac = (a, b) => { let n = 0, t = 0; for (let i = 0; i < a.px.length; i += a.bpp * 2) { t++; if (Math.abs(a.px[i] - b.px[i]) + Math.abs(a.px[i + 1] - b.px[i + 1]) + Math.abs(a.px[i + 2] - b.px[i + 2]) > 24) n++; } return n / t; };

// ---------- 4. Đo chữ trong DOM / TEXTS ----------
const doChu = (t) => page.evaluate((t) => {
  const W = innerWidth, H = innerHeight, kq = [];
  if (typeof window.TEXTS === 'function') for (const b of window.TEXTS(t) || []) kq.push({ id: b.id || b.text, x0: b.x0, y0: b.y0, x1: b.x1, y1: b.y1, co: null });
  const mo = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden') return 0; o *= +s.opacity; } return o; };
  for (const el of document.body.querySelectorAll('*')) {
    if (el.closest('[data-qa-bo-qua],script,style')) continue;
    const coChu = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!coChu || mo(el) < 0.05) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    kq.push({ id: el.id || el.dataset.id || el.textContent.trim().slice(0, 24), x0: r.left, y0: r.top, x1: r.right, y1: r.bottom, co: parseFloat(getComputedStyle(el).fontSize), choPhep: !!el.closest('[data-qa-cho-phep]') });
  }
  return { W, H, kq };
}, t);

const fontThieu = await page.evaluate(() => {
  const fams = new Set();
  for (const el of document.body.querySelectorAll('*')) if ([...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) fams.add(getComputedStyle(el).fontFamily.split(',')[0].trim());
  const c = document.createElement('canvas').getContext('2d'), w = (f, s) => { c.font = `40px ${f}`; return c.measureText(s).width; };
  const bad = [];
  for (const f of fams) {
    if (/^(serif|sans-serif|monospace|system-ui)$/i.test(f)) { bad.push({ f, ly: 'font chung của hệ thống, không chắc có dấu' }); continue; }
    if (w(`${f}, monospace`, 'Hamburgefonts') !== w(`${f}, serif`, 'Hamburgefonts')) bad.push({ f, ly: 'chưa tải được' });
    else if (w(`${f}, monospace`, 'ẩặễờữỹđ') !== w(`${f}, serif`, 'ẩặễờữỹđ')) bad.push({ f, ly: 'thiếu dấu tiếng Việt' });
  }
  return bad;
});
for (const b of fontThieu) ghi(b.ly === 'chưa tải được' || b.ly.startsWith('thiếu') ? 'LOI' : 'CANH', 'font', null, `font ${b.f}: ${b.ly}`);

// ---------- 5. Chụp từng mốc ----------
const seek = async (t) => {
  await page.evaluate(async (t) => { window.__dem.dangSeek = true; try { await window.__seek(t); } finally { window.__dem.dangSeek = false; } }, t);
  return page.screenshot({ type: 'png' });
};
const ts = []; for (let t = 0; t <= DUR + 1e-6; t += buoc) ts.push(+t.toFixed(3));
if (ts[ts.length - 1] < DUR - 0.05) ts.push(DUR);
const anh = [], so = [];
let tranDaBao = new Set(), nhoDaBao = new Set(), deDaBao = new Set();
for (const [i, t] of ts.entries()) {
  const png = await seek(t);
  fs.writeFileSync(path.join(out, 'khung', `k${String(i).padStart(4, '0')}.png`), png);
  const im = docPNG(png); anh.push(im);
  const p = phu(im), d = i ? khac(anh[i - 1], im) : 1;
  so.push({ t, phu: +p.toFixed(4), doi: +d.toFixed(4), hash: crypto.createHash('sha1').update(im.px).digest('hex').slice(0, 10) });
  const { W: w, H: h, kq } = await doChu(t);
  for (const b of kq) {
    if (b.choPhep) continue;
    if ((b.x0 < -2 || b.y0 < -2 || b.x1 > w + 2 || b.y1 > h + 2) && !tranDaBao.has(b.id)) { tranDaBao.add(b.id); ghi('LOI', 'tran', t, `chữ "${b.id}" ra ngoài khung`); }
    if (b.co && b.co < h / 54 && !nhoDaBao.has(b.id)) { nhoDaBao.add(b.id); ghi('CANH', 'nho', t, `chữ "${b.id}" ${b.co}px < ${Math.round(h / 54)}px (khó đọc trên điện thoại)`); }
  }
  for (let a = 0; a < kq.length; a++) for (let b = a + 1; b < kq.length; b++) {
    const A = kq[a], B = kq[b]; if (A.choPhep || B.choPhep) continue;
    const ix = Math.max(0, Math.min(A.x1, B.x1) - Math.max(A.x0, B.x0)), iy = Math.max(0, Math.min(A.y1, B.y1) - Math.max(A.y0, B.y0));
    const nho = Math.min((A.x1 - A.x0) * (A.y1 - A.y0), (B.x1 - B.x0) * (B.y1 - B.y0));
    const chua = (P, Q) => P.x0 <= Q.x0 && P.y0 <= Q.y0 && P.x1 >= Q.x1 && P.y1 >= Q.y1;
    if (nho > 0 && ix * iy / nho > 0.2 && !chua(A, B) && !chua(B, A) && !deDaBao.has(A.id + '|' + B.id) && deDaBao.add(A.id + '|' + B.id)) ghi('CANH', 'de', t, `chữ "${A.id}" đè "${B.id}"`);
  }
}
const dem = await page.evaluate(() => window.__dem);
if (dem.random) ghi('LOI', 'tatdinh', null, `Math.random được gọi ${dem.random} lần trong lúc vẽ theo t`);
if (dem.gio) ghi('CANH', 'tatdinh', null, `đồng hồ thật (Date/performance.now) được đọc ${dem.gio} lần trong lúc vẽ`);
if (dem.hen) ghi('CANH', 'tatdinh', null, `setTimeout được gọi ${dem.hen} lần trong lúc vẽ`);

// ---------- 6. Tất định: tua ngược, nhảy cóc ----------
const mau = ts.filter((_, i) => i % Math.max(1, Math.floor(ts.length / 8)) === 0).reverse();
const lech = [];
for (const t of mau) {
  const im = docPNG(await seek(t)), i = ts.indexOf(t), d = khac(anh[i], im);
  if (d > 0.002) lech.push(`${t}s (${(d * 100).toFixed(2)}%)`);
}
if (lech.length) ghi('LOI', 'tatdinh', null, `tua lại ra hình khác lần đầu ở ${lech.length}/${mau.length} mốc: ${lech.slice(0, 4).join(', ')}${lech.length > 4 ? '…' : ''}. Trạng thái đang phụ thuộc khung trước`);

// ---------- 7. Nhịp: trống, đứng hình, khung đầu ----------
if (so[0].phu < 0.015) ghi('CANH', 'khung0', 0, 'khung đầu gần như trống: nền tảng lấy khung đầu làm ảnh bìa');
let dung = 0;
for (let i = 1; i < so.length; i++) {
  if (so[i].doi < 0.0005) dung += buoc; else dung = 0;
  if (dung > 3 && dung - buoc <= 3) ghi('CANH', 'dung', so[i].t, `đứng hình hơn 3 giây tới giây ${so[i].t}`);
  if (so[i].phu < 0.015 && i < so.length - 1) ghi('CANH', 'trong', so[i].t, `khung gần như trống (phủ ${(so[i].phu * 100).toFixed(1)}%)`);
}
const last = so[so.length - 1], prev = so[so.length - 2];
if (prev && last.doi > 0.05) ghi('CANH', 'ket', last.t, 'khung cuối còn đang chuyển động mạnh: nên có 1 giây dừng ở cuối');
for (const e of [...new Set(loiTrang)].slice(0, 10)) ghi('LOI', 'trang', null, e);

// ---------- 8. Contact sheet + báo cáo ----------
let sheet = null;
try {
  const cot = 6, hang = Math.ceil(ts.length / cot);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(out, 'khung', 'k%04d.png'), '-vf', `scale=320:-2,tile=${cot}x${hang}:padding=4:color=gray`, '-frames:v', '1', path.join(out, 'sheet.jpg')]);
  sheet = path.join(out, 'sheet.jpg');
} catch { ghi('CANH', 'sheet', null, 'không có ffmpeg, bỏ qua contact sheet'); }
const bc = { trang, kieu: kieu.ten, dur: DUR, buoc, loi, canh, so, sheet };
fs.writeFileSync(path.join(out, 'bao-cao.json'), JSON.stringify(bc, null, 1));
const dong = (x) => `- ${x.t != null ? `[${x.t}s] ` : ''}${x.ma}: ${x.msg}`;
const md = `# Kiểm khung: ${path.basename(trang)}\n\nHàm: ${kieu.ten}, dài ${DUR}s, mốc mỗi ${buoc}s, ${ts.length} khung. Contact sheet: ${sheet || 'không có'}\n\n## LỖI (${loi.length})\n${loi.map(dong).join('\n') || '- không'}\n\n## CẢNH BÁO (${canh.length})\n${canh.map(dong).join('\n') || '- không'}\n`;
fs.writeFileSync(path.join(out, 'bao-cao.md'), md);
console.log(md);
await browser.close(); sv.close();
process.exit(loi.length ? 1 : 0);
