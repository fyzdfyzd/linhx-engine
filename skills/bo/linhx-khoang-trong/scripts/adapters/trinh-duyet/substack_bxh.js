// substack_bxh.js: adapter B1 cho Substack, chạy trong Chrome của Linh (Claude in Chrome → javascript_tool).
// Khác substack_scan.js của vault: lấy MỌI chủ đề (không lọc theo angle của Linh) để mẫu không lệch,
// và xuất thẳng JSONL theo schema LAB029 (references/schema.md).
//
// Cách chạy: mở https://substack.com trong Chrome, dán file này, rồi:
//   SB.start({trang: 4, baiMoiKenh: 12})   chạy nền (bảng xếp hạng all + paid của mọi chủ đề, rồi bài top mỗi kênh)
//   SB.start({vn: true})                    thêm tìm bản tin/bài tiếng Việt theo từ khoá (mặc định bật)
//   SB.status()                             gọi lại đến khi done: true
//   SB.copyButton()                         nút phủ trang; bấm để chép JSONL vào clipboard
//   SB.chunk(i)                             dự phòng: lấy JSONL theo khúc 40k ký tự
// Rồi PowerShell trong thư mục lượt chạy:
//   Get-Clipboard -Raw | Out-File -Encoding utf8 b1-substack.jsonl ; python gapscan.py nhap b1-substack.jsonl
// Chỉ đọc. Không follow, subscribe, like. Không gửi dữ liệu ra ngoài substack.com. Nhịp chậm (4 luồng, nghỉ khi 429).

window.SB = (() => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  async function g(u, tries = 4) {
    for (let i = 0; i < tries; i++) {
      const r = await fetch(u, { credentials: 'include' });
      if (r.status === 429 || r.status >= 500) { await sleep(2000 * (i + 1)); continue; }
      if (!r.ok) return null;
      return r.json();
    }
    return null;
  }
  const D = window.SB_DATA ||= { PUB: {}, P: {}, log: [], done: false };
  const num = s => +String(s || '').replace(/[^\d]/g, '') || 0;
  const VN_CH = /[đơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]/i;
  const isVi = (lang, ...t) => /^vi/i.test(lang || '') || t.some(x => VN_CH.test(x || ''));
  const VN_Q = ['việt nam', 'người việt', 'kinh doanh', 'khởi nghiệp', 'tâm lý', 'tình yêu', 'hôn nhân', 'cuộc sống', 'công nghệ', 'trí tuệ nhân tạo',
    'giáo dục', 'đọc sách', 'tài chính', 'đầu tư', 'sức khỏe', 'não bộ', 'triết học', 'xã hội', 'nghề nghiệp', 'viết lách', 'trung niên', 'nuôi dạy con', 'lịch sử'];
  const pool = (n, fn) => { let i = 0; return Promise.all(Array.from({ length: n }, async () => { while (true) { const k = i++; if (!(await fn(k))) break; } })); };

  function addPub(p, nhan) {
    if (!p || !p.id) return null;
    const e = D.PUB[p.id] ||= { id: p.id, name: p.name, sub: p.subdomain, domain: p.custom_domain || '', author_id: p.author_id, author: p.author_name,
      lang: p.language, subs: 0, rank: '', hero: '', lb: [], vn: false };
    e.subs = Math.max(e.subs, num(p.freeSubscriberCount));
    e.rank ||= p.rankingDetail || ''; e.hero ||= (p.hero_text || p.author_bio || '').replace(/\s+/g, ' ').slice(0, 200);
    e.author ||= p.author_name; e.author_id ||= p.author_id;
    if (nhan) e.lb.push(nhan);
    if (isVi(p.language, p.name, p.author_name, p.hero_text)) e.vn = true;
    return e;
  }
  const addPost = (p, pubId) => { if (!p?.id) return; D.P[p.id] ||= { id: p.id, title: p.title || '', sub: (p.subtitle || '').slice(0, 200), url: p.canonical_url,
    date: (p.post_date || '').slice(0, 10), pub: pubId || p.publication_id, author: p.publishedBylines?.[0]?.name || '', lang: p.language,
    like: p.reaction_count || 0, comm: p.comment_count || 0, restack: p.restacks || 0, words: p.wordcount || 0, paid: p.audience === 'only_paid',
    tags: (p.postTags || []).map(t => t.name) }; };

  async function run({ trang = 4, baiMoiKenh = 12, vn = true, luong = 4 } = {}) {
    const cats = (await g('/api/v1/categories')) || [];
    const ds = cats.flatMap(c => [[c.id, c.slug || c.name, 'all'], [c.id, c.slug || c.name, 'paid']]);
    D.log.push(`chủ đề ${cats.length}`);
    await pool(luong, async k => {
      if (k >= ds.length) return false; const [cid, slug, kind] = ds[k];
      for (let pg = 0; pg < trang; pg++) {
        const d = await g(`/api/v1/category/public/${cid}/${kind}?page=${pg}`); if (!d) break;
        (d.publications || []).forEach((p, i) => addPub(p, `${slug}/${kind}#${pg * 25 + i + 1}`));
        if (!d.more) break;
      }
      return true;
    });
    D.log.push(`kênh bảng xếp hạng ${Object.keys(D.PUB).length}`);
    if (vn) {
      for (const q of VN_Q) {
        for (let pg = 0; pg < 3; pg++) {
          const d = await g(`/api/v1/publication/search?query=${encodeURIComponent(q)}&page=${pg}&limit=50`); if (!d) break;
          (d.results || []).forEach(p => isVi(p.language, p.name, p.author_name, p.hero_text) && addPub(p, 'vn-search'));
          if (!d.more) break;
        }
      }
      D.log.push(`sau tìm VN ${Object.keys(D.PUB).length}`);
    }
    const aids = [...new Set(Object.values(D.PUB).map(p => p.author_id).filter(Boolean))];
    await pool(luong, async k => {
      if (k >= aids.length) return false;
      const d = await g(`/api/v1/profile/posts?profile_user_id=${aids[k]}&limit=${baiMoiKenh}`);
      (d?.posts || []).forEach(p => addPost(p));
      return true;
    });
    D.log.push(`bài ${Object.keys(D.P).length}`);
    D.done = true;
  }
  const start = o => { D.done = false; D.log = []; run(o).catch(e => { D.log.push('EX ' + e); D.done = true; }); return 'started'; };
  const status = () => ({ done: D.done, kenh: Object.keys(D.PUB).length, bai: Object.keys(D.P).length, log: D.log.join(' | ') });

  function jsonl() {
    const day = new Date().toISOString().slice(0, 10), L = [];
    const pubs = D.PUB;
    Object.values(pubs).forEach(p => {
      const url = p.domain ? `https://${p.domain}` : `https://${p.sub}.substack.com`;
      L.push({ id: 'sub:' + (p.sub || p.id), nguon: 'substack', thi_truong: p.vn ? 'vn' : 'quoc-te', loai: 'kenh', tieu_de: p.name, kenh: p.name, kenh_id: p.sub,
        tac_gia: p.author, url, mo_ta: p.hero, the: [...new Set(p.lb.map(x => x.split('/')[0]).filter(x => x !== 'vn-search'))], hang: p.lb.join(' '),
        bac_tra_phi: /paid/i.test(p.rank) ? p.rank : '', so_do: { subscriber: p.subs }, ngay_quet: day });
    });
    Object.values(D.P).forEach(x => {
      const p = pubs[x.pub] || {};
      L.push({ id: 'subp:' + x.id, nguon: 'substack', thi_truong: (p.vn || isVi(x.lang, x.title)) ? 'vn' : 'quoc-te', loai: 'bai', tieu_de: x.title, mo_ta: x.sub,
        url: x.url, tac_gia: x.author, kenh: p.name || '', kenh_id: p.sub || '', ngay: x.date, the: x.tags.concat((p.lb || []).map(s => s.split('/')[0])).filter(t => t !== 'vn-search'),
        so_do: { like: x.like, comment: x.comm, share: x.restack, subscriber: p.subs || 0 }, tra_phi: x.paid, so_chu: x.words, ngay_quet: day });
    });
    return L.map(o => JSON.stringify(o)).join('\n');
  }
  function copyButton(text = jsonl()) {
    window.SB_TXT = text;
    document.body.innerHTML = ''; const b = document.createElement('button'); b.textContent = 'COPY ' + text.length;
    b.style.cssText = 'position:fixed;inset:0;font-size:80px;z-index:99999';
    b.onclick = async () => { await navigator.clipboard.writeText(text); b.textContent = 'COPIED ' + text.length; };
    document.body.appendChild(b); return text.length;
  }
  const chunk = i => (window.SB_TXT ||= jsonl()).slice(i * 40000, (i + 1) * 40000);
  return { start, status, jsonl, copyButton, chunk, data: D };
})();
