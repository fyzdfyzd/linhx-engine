// Máy nhận lead tối giản cho sakedemy.com (tư vấn lớp doanh nghiệp, gọi lại, học thử). Node ≥ 18, không cần cài gói.
// Chạy: node server.mjs  (PORT=8080, LEAD_DIR=./leads). Tuỳ chọn báo tin:
//   TG_TOKEN + TG_CHAT  -> nhắn Telegram mỗi lead
//   SHEET_WEBHOOK       -> POST JSON tới Google Apps Script (ghi vào Sheet)
//   TRUST_PROXY=1       -> đứng sau Caddy/Nginx, lấy IP thật từ X-Forwarded-For
//   RATE_MAX            -> số lead tối đa mỗi IP trong 10 phút (mặc định 5)
// Khi lõi engine (C2) xong, chỉ đổi hàm guiDi() sang API engine; trang không đổi.
import http from "node:http";
import { readFile, appendFile, mkdir, stat } from "node:fs/promises";
import { join, extname, normalize } from "node:path";
import { randomBytes } from "node:crypto";

const PORT = +process.env.PORT || 8080;
const GOC = new URL("./public/", import.meta.url).pathname;
const LEAD_DIR = process.env.LEAD_DIR || new URL("./leads/", import.meta.url).pathname;
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ttf": "font/ttf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8" };
const DAU = { "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin", "X-Frame-Options": "SAMEORIGIN" };
const luot = new Map(); // ip -> [mốc thời gian]

function tra(res, code, obj) { res.writeHead(code, { ...DAU, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }); res.end(JSON.stringify(obj)); }
const chu = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");

const LOAI = ["tu-van", "goi-lai", "hoc-thu"];
const CAU_DONG_Y = {
  "tu-van": "Tôi đồng ý để Sakédemy dùng thông tin này để liên hệ tư vấn.",
  "goi-lai": "Tôi đồng ý để Sakédemy gọi lại cho tôi.",
  "hoc-thu": "Tôi đồng ý nhận email từ Sakédemy.",
};
const ds = (v, n) => (Array.isArray(v) ? v.filter((g) => typeof g === "string").slice(0, 8).map((g) => g.slice(0, n)) : []);
function kiem(d) {
  const x = {
    loai: LOAI.includes(d.loai) ? d.loai : "tu-van",
    ho_ten: chu(d.ho_ten, 80), cong_ty: chu(d.cong_ty, 120), vai_tro: chu(d.vai_tro, 80), dien_thoai: chu(d.dien_thoai, 20), email: chu(d.email, 120),
    so_hoc_vien: chu(d.so_hoc_vien, 40), phong_ban: ds(d.phong_ban, 30), hinh_thuc: chu(d.hinh_thuc, 20), thoi_gian: chu(d.thoi_gian, 40),
    nhu_cau: chu(d.nhu_cau, 3000), goi: chu(d.goi, 40), trang: chu(d.trang, 200), nguon: {},
  };
  if (d.nguon && typeof d.nguon === "object") for (const k of ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"]) if (d.nguon[k]) x.nguon[k] = chu(String(d.nguon[k]), 80);
  if (x.loai === "hoc-thu") { if (!x.email) return [null, "Cần email để gửi bài học thử"]; }
  else if (!x.ho_ten) return [null, "Thiếu họ tên"];
  if (!x.cong_ty && x.loai === "tu-van") return [null, "Thiếu tên công ty"];
  if (x.loai === "goi-lai" && !x.dien_thoai) return [null, "Cần số điện thoại để gọi lại"];
  if (!x.dien_thoai && !x.email) return [null, "Cần điện thoại hoặc email"];
  if (x.dien_thoai && !/^[0-9+().\s-]{8,20}$/.test(x.dien_thoai)) return [null, "Số điện thoại chưa đúng"];
  if (x.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email)) return [null, "Email chưa đúng"];
  if (d.dong_y !== true) return [null, "Cần đồng ý để chúng tôi liên hệ"];
  return [x, null];
}

async function guiDi(lead) {
  const viec = [];
  if (process.env.TG_TOKEN && process.env.TG_CHAT) {
    const ten = { "tu-van": "Tư vấn lớp DN", "goi-lai": "GỌI LẠI", "hoc-thu": "Học thử" }[lead.loai];
    const t = `${ten} ${lead.ma}\n${lead.ho_ten || "-"} · ${lead.cong_ty || "-"} · ${lead.vai_tro || "-"}\n${lead.dien_thoai || ""} ${lead.email || ""}\nHọc viên: ${lead.so_hoc_vien || "-"} · Phòng ban: ${lead.phong_ban.join(", ") || "-"} · Hình thức: ${lead.hinh_thuc || "-"} · Khi nào: ${lead.thoi_gian || "-"}\nNguồn: ${lead.nguon.kenh || lead.nguon.utm_source || "trực tiếp"}`;
    viec.push(fetch(`https://api.telegram.org/bot${process.env.TG_TOKEN}/sendMessage`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ chat_id: process.env.TG_CHAT, text: t }) }));
  }
  if (process.env.SHEET_WEBHOOK) viec.push(fetch(process.env.SHEET_WEBHOOK, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(lead) }));
  const kq = await Promise.allSettled(viec);
  kq.forEach((k) => k.status === "rejected" && console.error("báo tin lỗi:", k.reason?.message));
}

async function nhanBrief(req, res) {
  const ip = ((process.env.TRUST_PROXY === "1" && req.headers["x-forwarded-for"]) || req.socket.remoteAddress || "").split(",")[0].trim();
  const now = Date.now(), ds = (luot.get(ip) || []).filter((t) => now - t < 600000);
  if (ds.length >= (+process.env.RATE_MAX || 5)) return tra(res, 429, { loi: "Bạn gửi hơi nhiều, thử lại sau ít phút" });
  let tho = "";
  for await (const c of req) { tho += c; if (tho.length > 20000) return tra(res, 413, { loi: "Brief quá dài" }); }
  let d; try { d = JSON.parse(tho); } catch { return tra(res, 400, { loi: "Dữ liệu không đọc được" }); }
  const ma = "SK-" + new Date().toISOString().slice(2, 10).replace(/-/g, "") + "-" + randomBytes(2).toString("hex").toUpperCase();
  if (d.website) return tra(res, 200, { ok: true, ma }); // bẫy bot: giả vờ nhận
  const [x, loi] = kiem(d);
  if (loi) return tra(res, 400, { loi });
  ds.push(now); luot.set(ip, ds);
  const lead = { ma, luc: new Date().toISOString(), ...x, dong_y: { luc: new Date().toISOString(), cau: CAU_DONG_Y[x.loai], ip }, ua: chu(req.headers["user-agent"] || "", 200) };
  await mkdir(LEAD_DIR, { recursive: true });
  await appendFile(join(LEAD_DIR, "leads.jsonl"), JSON.stringify(lead) + "\n");
  guiDi(lead);
  tra(res, 200, { ok: true, ma });
}

async function tinh(req, res) {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (p.endsWith("/")) p += "index.html";
  const f = normalize(join(GOC, p));
  if (!f.startsWith(GOC)) return tra(res, 403, { loi: "cấm" });
  try {
    if (!(await stat(f)).isFile()) throw 0;
    const b = await readFile(f), ext = extname(f);
    res.writeHead(200, { ...DAU, "Content-Type": MIME[ext] || "application/octet-stream", "Cache-Control": ext === ".html" || ext === ".json" ? "no-cache" : "public, max-age=604800" });
    res.end(req.method === "HEAD" ? undefined : b);
  } catch {
    if (!extname(p)) { try { if ((await stat(join(f, "index.html"))).isFile()) { res.writeHead(301, { Location: p + "/" }); return res.end(); } } catch {} }
    let b = "Không có trang này"; try { b = await readFile(join(GOC, "404.html")); } catch {}
    res.writeHead(404, { ...DAU, "Content-Type": "text/html; charset=utf-8" }); res.end(b);
  }
}

http.createServer((req, res) => {
  if (req.url.startsWith("/api/brief")) return req.method === "POST" ? nhanBrief(req, res).catch((e) => { console.error(e); tra(res, 500, { loi: "Máy nhận đang lỗi" }); }) : tra(res, 405, { loi: "Chỉ nhận POST" });
  if (req.url === "/api/song") return tra(res, 200, { ok: true });
  if (req.method !== "GET" && req.method !== "HEAD") return tra(res, 405, { loi: "Không hỗ trợ" });
  tinh(req, res);
}).listen(PORT, () => console.log(`sakedemy-site chạy ở http://localhost:${PORT}`));
