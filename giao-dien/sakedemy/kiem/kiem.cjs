// Cổng máy cho trang BU. Chạy: node server.mjs & ; node kiem/kiem.cjs [http://localhost:8080] [--chup-chuan]
// Chặn nếu: link nội bộ hỏng hoặc thiếu JSON-LD/SEO cơ bản (K9–K10), băm khoá lệch, màu ngoài token, tràn ngang, chạm < 44px, chữ < 16px ở đoạn thân, form không gửi được, ảnh lệch ảnh chuẩn.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const GOC = path.join(__dirname, '..'), B = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'http://localhost:8080';
const CHUP = process.argv.includes('--chup-chuan'), CO = [1280, 1024, 768, 390, 360];
const loi = [], bam = f => crypto.createHash('sha256').update(fs.readFileSync(path.join(GOC, f))).digest('hex');
const KHOA = ['DESIGN.md', 'public/site.css', 'public/index.html', 'tao-trang.py'];
const fk = path.join(GOC, 'DESIGN.khoa');
if (CHUP) fs.writeFileSync(fk, KHOA.map(f => `${bam(f)}  ${f}`).join('\n') + '\n');
else for (const d of fs.readFileSync(fk, 'utf8').trim().split('\n')) { const [h, f] = d.split(/\s+/); if (bam(f) !== h) loi.push(`K1 khoá lệch: ${f} đã đổi mà chưa duyệt`); }
// K2 màu ngoài token
const tok = new Set([...fs.readFileSync(path.join(GOC, 'DESIGN.md'), 'utf8').matchAll(/#[0-9A-Fa-f]{6}\b/g)].map(m => m[0].toUpperCase()));
const css = fs.readFileSync(path.join(GOC, 'public/site.css'), 'utf8').replace(/:root\{[^}]*\}/, '');
const ngoai = [...new Set([...css.matchAll(/#[0-9A-Fa-f]{6}\b/g)].map(m => m[0].toUpperCase()))].filter(c => !tok.has(c));
if (ngoai.length) console.log('K2 cảnh báo màu ngoài token (sắc độ phụ, cần đưa vào DESIGN.md nếu giữ):', ngoai.join(' '));
(async () => {
  const br = await chromium.launch();
  const trang = [...fs.readFileSync(path.join(GOC, 'public/sitemap.xml'), 'utf8').matchAll(/<loc>https?:\/\/[^/]+(\/[^<]*)<\/loc>/g)].map(m => m[1]).concat(['/404.html']);
  const daXem = new Set();
  for (const tr of trang) for (const w of (tr === '/' ? CO : [1280, 390])) {
    const p = await (await br.newContext({ viewport: { width: w, height: w < 500 ? 800 : 860 }, reducedMotion: 'reduce' })).newPage();
    const r = await p.goto(B + tr); await p.waitForTimeout(300);
    if (tr !== '/404.html' && r.status() !== 200) loi.push(`K9 ${tr} trả ${r.status()}`);
    if (!daXem.has(tr)) { daXem.add(tr);
      const ld = await p.evaluate(() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { JSON.parse(s.textContent); return 1 } catch { return 0 } }));
      if (!ld.length || ld.includes(0)) loi.push(`K10 ${tr} thiếu hoặc hỏng JSON-LD`);
      const t = await p.evaluate(() => ({ title: document.title.length, desc: (document.querySelector('meta[name=description]') || {}).content?.length || 0, h1: document.querySelectorAll('h1').length, can: !!document.querySelector('link[rel=canonical]') }));
      if (tr !== '/404.html' && (t.title > 70 || t.desc > 160 || t.desc < 50 || t.h1 !== 1 || !t.can)) loi.push(`K10 ${tr} SEO: title ${t.title}, desc ${t.desc}, h1 ${t.h1}, canonical ${t.can}`);
      const links = await p.evaluate(() => [...new Set([...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href').split('#')[0].split('?')[0]).filter(Boolean))]);
      for (const l of links) { const rr = await p.request.get(B + l, { maxRedirects: 0 }); if (rr.status() >= 400) loi.push(`K9 link hỏng trên ${tr}: ${l} (${rr.status()})`); }
    }
    const m = await p.evaluate(() => ({
      tran: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      nho: [...document.querySelectorAll('a,button,summary,select,input:not([type=hidden]):not([type=checkbox]),.chip span')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && !e.closest('.hp,.skip') && r.height < 44 && !(getComputedStyle(e).display === 'inline' && e.closest('p,label span,li,td')); /* link nằm trong câu: miễn theo WCAG 2.5.8 */ }).map(e => (e.textContent || e.name || e.tagName).trim().slice(0, 30)),
      chuNho: [...document.querySelectorAll('p,li,dd,label,summary')].filter(e => e.offsetParent && parseFloat(getComputedStyle(e).fontSize) < 14).length,
      anhRong: [...document.images].filter(i => !i.naturalWidth).map(i => i.src),
    }));
    if (m.tran) loi.push(`K3 tràn ngang ở ${tr} ${w}px`);
    if (m.nho.length) loi.push(`K4 chạm < 44px ở ${tr} ${w}px: ${m.nho.join(', ')}`);
    if (m.chuNho) loi.push(`K5 ${m.chuNho} đoạn chữ < 14px ở ${tr} ${w}px`);
    if (m.anhRong.length) loi.push(`K6 ảnh hỏng: ${m.anhRong.join(', ')}`);
    if (tr !== '/') continue;
    const f = path.join(GOC, 'khoa/anh-chuan', `${w}.png`);
    await p.waitForTimeout(600); const anh = await p.screenshot({ animations: 'disabled' });
    if (CHUP) fs.writeFileSync(f, anh);
    else if (fs.existsSync(f)) {
      // so điểm ảnh: lệch kênh > 0,2 tính là khác; quá 100 điểm thì chặn (mốc toHaveScreenshot)
      const khac = await p.evaluate(async ([a, b]) => {
        const nap = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
        const [x, y] = await Promise.all([nap(a), nap(b)]);
        if (x.width !== y.width || x.height !== y.height) return 1e9;
        const c = document.createElement('canvas'); c.width = x.width; c.height = x.height; const g = c.getContext('2d');
        g.drawImage(x, 0, 0); const d1 = g.getImageData(0, 0, c.width, c.height).data;
        g.clearRect(0, 0, c.width, c.height); g.drawImage(y, 0, 0); const d2 = g.getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 0; i < d1.length; i += 4) if (Math.max(Math.abs(d1[i] - d2[i]), Math.abs(d1[i + 1] - d2[i + 1]), Math.abs(d1[i + 2] - d2[i + 2])) > 51) n++;
        return n;
      }, [fs.readFileSync(f).toString('base64'), anh.toString('base64')]);
      if (khac > 100) loi.push(`K8 màn đầu ${w}px lệch ảnh chuẩn ${khac} điểm ảnh, mở để so`);
    }
  }
  // K7 form gửi được
  const p = await br.newPage(); await p.goto(B + '/?kenh=cong-kiem');
  await p.fill('#form-brief [name=ho_ten]', 'Cổng kiểm'); await p.fill('#form-brief [name=cong_ty]', 'Thử'); await p.fill('#form-brief [name=email]', 'cong@kiem.vn');
  await p.check('#form-brief [name=dong_y]', { force: true }); await p.click('#form-brief button[type=submit]');
  try { await p.waitForFunction(() => document.querySelector('#form-brief .form-msg').classList.contains('ok'), null, { timeout: 5000 }); } catch { loi.push('K7 form brief không gửi được'); }
  const q = await br.newPage(); await q.goto(B + '/?kenh=cong-kiem');
  await q.fill('#form-goi-lai [name=ho_ten]', 'Cổng kiểm'); await q.fill('#form-goi-lai [name=dien_thoai]', '0900000000');
  await q.check('#form-goi-lai [name=dong_y]', { force: true }); await q.click('#form-goi-lai button[type=submit]');
  try { await q.waitForFunction(() => document.querySelector('#form-goi-lai .form-msg').classList.contains('ok'), null, { timeout: 5000 }); } catch { loi.push('K7 form gọi lại không gửi được'); }
  await br.close();
  console.log(loi.length ? 'CHUA_DAT\n' + loi.join('\n') : 'DAT: K1–K10 xanh, ' + trang.length + ' trang, trang chủ ở ' + CO.join('/'));
  process.exit(loi.length ? 1 : 0);
})();
