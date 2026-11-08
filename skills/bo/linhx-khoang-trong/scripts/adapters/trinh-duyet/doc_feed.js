// doc_feed.js: adapter B1 cho KÊNH QUAN ĐIỂM và nền tảng không có API mở: LinkedIn, Facebook, Threads, X, YouTube.
// Đọc những bài ĐANG HIỆN trên trang Linh mở (trang cá nhân, trang hoạt động, kết quả tìm kiếm, hashtag),
// cuộn chậm, gom bài, xuất JSONL theo schema LAB029. THỬ NGHIỆM: giao diện các mạng này đổi thường xuyên;
// nếu đọc ra 0 bài, dùng cách dự phòng trong skill hien-tuong (Claude đọc get_page_text và tự ghi JSONL).
//
// Cách chạy (Claude in Chrome → javascript_tool), trên trang đã mở và đã đăng nhập:
//   DF.cuon({lan: 20, thiTruong: 'vn'})   cuộn 20 lần, mỗi lần nghỉ 2 đến 4 giây, gom bài; gọi DF.status() đến khi done
//   DF.copyButton()                        bấm để chép JSONL; hoặc DF.chunk(i)
//   PowerShell: Get-Clipboard -Raw | Out-File -Encoding utf8 b1-linkedin-<tên>.jsonl ; python gapscan.py nhap b1-linkedin-<tên>.jsonl
// Chỉ đọc. Không like, comment, follow, kết bạn, nhắn tin. Không mở hồ sơ hàng loạt. Tối đa vài trang mỗi phiên.

window.DF = (() => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const D = window.DF_DATA ||= { P: {}, log: [], done: true };
  const host = location.hostname;
  const site = /linkedin/.test(host) ? 'linkedin' : /facebook/.test(host) ? 'facebook' : /threads\./.test(host) ? 'threads'
    : /(^|\.)x\.com|twitter/.test(host) ? 'x' : /youtube/.test(host) ? 'youtube' : 'khac';

  // "1,2K" "1.2K" "3,4 N" "2 Tr" "1,5 triệu" "12.345" → số
  function so(s) {
    if (!s) return 0;
    const m = String(s).replace(/ /g, ' ').match(/([\d.,]+)\s*(k|n|nghìn|ngàn|m|tr|triệu|b|tỷ)?/i);
    if (!m) return 0;
    let x = m[1], u = (m[2] || '').toLowerCase();
    if (u) x = x.replace(',', '.'); else x = x.replace(/[.,](?=\d{3}\b)/g, '').replace(',', '.');
    let v = parseFloat(x) || 0;
    if (/^(k|n|nghìn|ngàn)$/.test(u)) v *= 1e3; else if (/^(m|tr|triệu)$/.test(u)) v *= 1e6; else if (/^(b|tỷ)$/.test(u)) v *= 1e9;
    return Math.round(v);
  }
  const tim = (txt, re) => { const m = txt.match(re); return m ? so(m[1]) : 0; };
  const txt = el => (el?.innerText || '').trim();

  const CAU_HINH = {
    linkedin: {
      the: 'div.feed-shared-update-v2, li.profile-creator-shared-feed-update__container, div[data-urn^="urn:li:activity"]',
      doc: el => {
        const t = txt(el);
        const urn = el.getAttribute('data-urn') || el.querySelector('[data-urn]')?.getAttribute('data-urn') || '';
        return { id: urn || t.slice(0, 80), tac_gia: txt(el.querySelector('.update-components-actor__title span[aria-hidden="true"], .update-components-actor__name')),
          mo_ta_tg: txt(el.querySelector('.update-components-actor__description')),
          noi_dung: txt(el.querySelector('.update-components-text, .feed-shared-update-v2__description')),
          url: urn ? `https://www.linkedin.com/feed/update/${urn}/` : location.href,
          like: so(txt(el.querySelector('.social-details-social-counts__reactions-count'))) || tim(t, /([\d.,]+\s*[KkMm]?)\s*(reactions|lượt bày tỏ)/i),
          comment: tim(t, /([\d.,]+\s*[KkMm]?)\s*(comments?|bình luận)/i), share: tim(t, /([\d.,]+\s*[KkMm]?)\s*(reposts?|lượt đăng lại|chia sẻ)/i) };
      } },
    facebook: {
      the: 'div[role="article"]',
      doc: el => {
        const t = txt(el); const a = el.querySelector('a[href*="/posts/"], a[href*="/permalink/"], a[href*="story_fbid"]');
        return { id: a?.href?.split('?')[0] || t.slice(0, 80), tac_gia: txt(el.querySelector('h2, h3, strong')), noi_dung: txt(el.querySelector('div[data-ad-preview="message"], div[dir="auto"]')),
          url: a?.href?.split('?')[0] || location.href,
          like: tim(t, /(?:All reactions|Tất cả cảm xúc):?\s*\n?([\d.,]+\s*[KkMmNn]?)/i), comment: tim(t, /([\d.,]+\s*[KkMmNn]?)\s*(comments?|bình luận)/i),
          share: tim(t, /([\d.,]+\s*[KkMmNn]?)\s*(shares?|lượt chia sẻ)/i) };
      } },
    threads: {
      the: 'div[data-pressable-container="true"]',
      doc: el => {
        const t = txt(el); const a = el.querySelector('a[href*="/post/"]');
        const nums = [...el.querySelectorAll('svg[aria-label] ~ span, div[role="button"] span')].map(s => so(txt(s)));
        return { id: a?.href || t.slice(0, 80), tac_gia: txt(el.querySelector('a[href^="/@"] span')), noi_dung: t.split('\n').slice(2, 12).join(' '),
          url: a?.href || location.href, like: nums[0] || 0, comment: nums[1] || 0, share: (nums[2] || 0) + (nums[3] || 0) };
      } },
    x: {
      the: 'article[data-testid="tweet"]',
      doc: el => {
        const a = el.querySelector('a[href*="/status/"]'); const lab = s => el.querySelector(`[data-testid="${s}"]`)?.getAttribute('aria-label') || '';
        return { id: a?.href || '', tac_gia: txt(el.querySelector('[data-testid="User-Name"]')).split('\n')[0], noi_dung: txt(el.querySelector('[data-testid="tweetText"]')),
          url: a?.href || location.href, like: so(lab('like')), comment: so(lab('reply')), share: so(lab('retweet')),
          view: so(el.querySelector('a[href$="/analytics"]')?.getAttribute('aria-label')) };
      } },
    youtube: {
      the: 'ytd-video-renderer, ytd-rich-item-renderer, ytd-grid-video-renderer',
      doc: el => {
        const a = el.querySelector('a#video-title, a#video-title-link'); const meta = txt(el.querySelector('#metadata-line'));
        return { id: a?.href?.split('&')[0] || '', tac_gia: txt(el.querySelector('#channel-name a, ytd-channel-name a')), noi_dung: txt(a),
          url: a?.href?.split('&')[0] || '', view: tim(meta, /([\d.,]+\s*[KkMmNn]?\w*)\s*(views|lượt xem)/i), ngay_tuong_doi: meta.split('\n').pop() };
      } },
  };

  function gom(thiTruong) {
    const c = CAU_HINH[site]; if (!c) return 0;
    let n = 0;
    document.querySelectorAll(c.the).forEach(el => {
      try { const r = c.doc(el); if (!r.id || D.P[r.id]) return; r.thiTruong = thiTruong; r.trang = location.href; D.P[r.id] = r; n++; } catch (e) { }
    });
    return n;
  }
  async function cuonChay({ lan = 20, thiTruong = 'vn' }) {
    for (let i = 0; i < lan; i++) {
      const n = gom(thiTruong); D.log.push(`lần ${i + 1}: +${n}`);
      window.scrollBy(0, window.innerHeight * 0.9);
      await sleep(2000 + Math.random() * 2000);
    }
    gom(thiTruong); D.done = true;
  }
  const cuon = (o = {}) => { if (site === 'khac') return 'Trang này chưa có cấu hình; dùng cách dự phòng (get_page_text).'; D.done = false; D.log = []; cuonChay(o); return 'started ' + site; };
  const status = () => ({ done: D.done, site, bai: Object.keys(D.P).length, log: D.log.slice(-3).join(' | ') });
  function jsonl() {
    const day = new Date().toISOString().slice(0, 10);
    return Object.values(D.P).map(r => {
      const nd = (r.noi_dung || '').replace(/\s+/g, ' ');
      return JSON.stringify({ id: `${site}:${r.id}`.slice(0, 300), nguon: site, thi_truong: r.thiTruong, loai: 'bai', tieu_de: nd.slice(0, 140), mo_ta: nd.slice(140, 600),
        tac_gia: r.tac_gia || '', kenh: r.tac_gia || '', url: r.url, ngay: '', the: [], ghi_chu: r.mo_ta_tg || r.ngay_tuong_doi || '',
        so_do: { like: r.like || 0, comment: r.comment || 0, share: r.share || 0, view: r.view || 0 }, trang_nguon: r.trang, ngay_quet: day });
    }).join('\n');
  }
  function copyButton(text = jsonl()) {
    window.DF_TXT = text;
    const b = document.createElement('button'); b.textContent = 'COPY ' + text.length;
    b.style.cssText = 'position:fixed;inset:0;font-size:80px;z-index:99999;background:#fff';
    b.onclick = async () => { await navigator.clipboard.writeText(text); b.textContent = 'COPIED ' + text.length; setTimeout(() => b.remove(), 1500); };
    document.body.appendChild(b); return text.length;
  }
  const chunk = i => (window.DF_TXT ||= jsonl()).slice(i * 40000, (i + 1) * 40000);
  const xoa = () => { D.P = {}; D.log = []; return 'đã xoá'; };
  return { cuon, status, jsonl, copyButton, chunk, xoa, so, site };
})();
