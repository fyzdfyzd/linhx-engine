// medium_tag.js: adapter B1 cho Medium, chạy trong Chrome đã đăng nhập của Linh (Claude in Chrome → javascript_tool).
// Khác medium_scan.js của vault: KHÔNG lấy For you / Following (lệch theo sở thích Linh). Chỉ lấy feed theo tag
// cho một bộ tag phủ đủ các mảng đời sống, cộng Staff Picks, rồi 12 bài trên trang mỗi tác giả để có mốc so
// "bài vượt trung vị của chính tác giả". Xuất JSONL theo schema LAB029.
//
// Cách chạy: mở https://medium.com, dán file này, rồi:
//   MT.start({moiTag: 100})   chạy nền; MT.status() đến khi done: true
//   MT.copyButton()           bấm để chép JSONL; hoặc MT.chunk(i) lấy theo khúc 40k ký tự
//   PowerShell: Get-Clipboard -Raw | Out-File -Encoding utf8 b1-medium.jsonl ; python gapscan.py nhap b1-medium.jsonl
// Muốn đổi bộ tag: MT.start({tags: ['aging', 'grief', ...]}).
// Chỉ đọc, nhịp chậm. Không clap, follow, comment. Không gửi dữ liệu ra ngoài medium.com.

window.MT = (() => {
  const gql = async (query, variables = {}) =>
    (await fetch('/_/graphql', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ query, variables }) })).json();
  const PF = `id title mediumUrl firstPublishedAt clapCount readingTime isLocked creator{ id name username socialStats{followerCount} } collection{ id name slug subscriberCount } extendedPreviewContent{ subtitle } postResponses{ count } tags{ normalizedTagSlug }`;
  const D = window.MT_DATA ||= { P: {}, AU: {}, log: [], done: false };
  const TAGS = [
    // đời sống, tâm lý, quan hệ
    'self-improvement', 'psychology', 'mental-health', 'relationships', 'love', 'marriage', 'divorce', 'parenting', 'family', 'friendship', 'loneliness',
    'aging', 'women', 'men', 'life-lessons', 'life', 'grief', 'memoir', 'this-happened-to-me', 'spirituality', 'philosophy', 'stoicism', 'mindfulness',
    // sức khoẻ
    'health', 'neuroscience', 'nutrition', 'fitness', 'sleep', 'longevity', 'adhd',
    // xã hội, văn hoá
    'society', 'culture', 'history', 'politics', 'social-media', 'internet-culture', 'education', 'science', 'travel', 'humor',
    // công việc, tiền
    'money', 'personal-finance', 'investing', 'economics', 'business', 'startup', 'entrepreneurship', 'leadership', 'careers', 'productivity', 'work',
    'freelancing', 'side-hustle', 'marketing',
    // công nghệ
    'artificial-intelligence', 'chatgpt', 'ai-tools', 'technology', 'future-of-work', 'programming', 'data-science',
    // viết
    'writing-tips', 'creativity', 'books', 'reading'];
  const add = (p, src) => { if (!p) return; const e = D.P[p.id] ||= { ...p, src: [] }; if (!e.src.includes(src)) e.src.push(src); };
  const pool = (n, fn) => { let i = 0; return Promise.all(Array.from({ length: n }, async () => { while (true) { const k = i++; if (!(await fn(k))) break; } })); };

  async function feed(tag, max) {
    let nx = { limit: 25 }, m = 0;
    while (m < max) {
      const d = await gql(`query($p:PagingOptions){ tagFeed(tagSlug:"${tag}", paging:$p){ items{ post{ ${PF} } } pagingInfo{ next{ limit to source from page } } } }`, { p: nx });
      const c = d.data?.tagFeed; if (!c) { D.log.push(`${tag} lỗi`); break; }
      c.items.forEach(x => add(x.post, 'tag:' + tag)); m += c.items.length; const nn = c.pagingInfo?.next; if (!nn || !c.items.length) break;
      nx = { limit: nn.limit, to: nn.to, source: nn.source, from: nn.from, page: nn.page };
    }
  }
  async function run({ tags = TAGS, moiTag = 100, staff = 150, tacGia = true, luong = 5 } = {}) {
    let from = null, n = 0;
    while (n < staff) { const pg = from ? `,from:"${from}"` : ''; const c = (await gql(`query { staffPicksFeed(input:{paging:{limit:25${pg}}}){ items{ post{ ${PF} } } pagingInfo{ next{ from } } } }`)).data?.staffPicksFeed;
      if (!c) break; c.items.forEach(x => add(x.post, 'staff')); n += c.items.length; from = c.pagingInfo?.next?.from; if (!from || !c.items.length) break; }
    D.log.push(`staff ${n}`);
    await pool(luong, async k => { if (k >= tags.length) return false; await feed(tags[k], moiTag); return true; });
    D.log.push(`bài theo tag ${Object.keys(D.P).length}`);
    if (tacGia) {
      const ids = [...new Set(Object.values(D.P).map(p => p.creator?.id).filter(Boolean))].filter(id => !D.AU[id]);
      await pool(luong * 2, async k => { if (k >= ids.length) return false; const id = ids[k];
        try { const d = await gql(`query { user(id:"${id}"){ id name socialStats{followerCount} homepagePostsConnection(paging:{limit:12}){ posts{ ${PF} } } } }`);
          D.AU[id] = 1; (d.data?.user?.homepagePostsConnection?.posts || []).forEach(p => add(p, 'author')); } catch (e) { D.AU[id] = 0; } return true; });
      D.log.push(`sau trang tác giả ${Object.keys(D.P).length}`);
    }
    D.done = true;
  }
  const start = o => { D.done = false; D.log = []; run(o).catch(e => { D.log.push('EX ' + e); D.done = true; }); return 'started'; };
  const status = () => ({ done: D.done, bai: Object.keys(D.P).length, tac_gia: Object.keys(D.AU).length, log: D.log.join(' | ') });
  function jsonl() {
    const day = new Date().toISOString().slice(0, 10);
    return Object.values(D.P).map(p => JSON.stringify({
      id: 'med:' + p.id, nguon: 'medium', thi_truong: 'quoc-te', loai: 'bai', tieu_de: p.title, mo_ta: p.extendedPreviewContent?.subtitle || '',
      url: p.mediumUrl || `https://medium.com/p/${p.id}`, tac_gia: p.creator?.name || '', tac_gia_id: p.creator?.id || '', kenh: p.collection?.name || '',
      ngay: new Date(p.firstPublishedAt || 0).toISOString().slice(0, 10), the: (p.tags || []).map(t => t.normalizedTagSlug),
      so_do: { clap: p.clapCount || 0, comment: p.postResponses?.count || 0, follower: p.creator?.socialStats?.followerCount || 0 },
      tra_phi: !!p.isLocked, phut_doc: Math.round(p.readingTime || 0), nguon_phu: p.src, ngay_quet: day })).join('\n');
  }
  function copyButton(text = jsonl()) {
    window.MT_TXT = text;
    document.body.innerHTML = ''; const b = document.createElement('button'); b.textContent = 'COPY ' + text.length;
    b.style.cssText = 'position:fixed;inset:0;font-size:80px;z-index:99999';
    b.onclick = async () => { await navigator.clipboard.writeText(text); b.textContent = 'COPIED ' + text.length; };
    document.body.appendChild(b); return text.length;
  }
  const chunk = i => (window.MT_TXT ||= jsonl()).slice(i * 40000, (i + 1) * 40000);
  return { start, status, jsonl, copyButton, chunk, TAGS, data: D };
})();
