// Máy nhận lead tối giản cho unikon.vn. Node ≥ 18, không cần cài gói.
// Chạy: node server.mjs  (PORT=8080, LEAD_DIR=./leads). Tuỳ chọn báo tin:
//   TG_TOKEN + TG_CHAT  -> nhắn Telegram mỗi lead
//   SHEET_WEBHOOK       -> POST JSON tới Google Apps Script (ghi vào Sheet)
//   TRUST_PROXY=1       -> đứng sau Caddy/Nginx, lấy IP thật từ X-Forwarded-For
//   RATE_MAX            -> số brief tối đa mỗi IP trong 10 phút (mặc định 5)
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
const LOAI = ["brief", "goi-lai", "tai-bo-kiem"];
// Câu đồng ý nguyên văn trên trang, lưu kèm lead làm bằng chứng.
const DONG_Y = {
  "brief": "Tôi đồng ý để Unikon dùng thông tin này để liên hệ về brief, theo chính sách dữ liệu.",
  "goi-lai": "Tôi đồng ý để Unikon gọi lại cho tôi, theo chính sách dữ liệu.",
  "tai-bo-kiem": "Tôi đồng ý để Unikon gửi bộ kiểm và thông tin liên quan qua email, theo chính sách dữ liệu.",
};

function tra(res, code, obj) { res.writeHead(code, { ...DAU, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }); res.end(JSON.stringify(obj)); }
const chu = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");

function kiem(d) {
  const x = {
    ho_ten: chu(d.ho_ten, 80), cong_ty: chu(d.cong_ty, 120), dien_thoai: chu(d.dien_thoai, 20), email: chu(d.email, 120),
    vai_tro: chu(d.vai_tro, 40), han_pitch: chu(d.han_pitch, 10), khach_hang: chu(d.khach_hang, 120), an_ten_khach: d.an_ten_khach === true,
    ngan_sach: chu(d.ngan_sach, 40), goi: chu(d.goi, 30),
    loai_asset: Array.isArray(d.loai_asset) ? d.loai_asset.filter((g) => typeof g === "string").slice(0, 6).map((g) => g.slice(0, 30)) : [],
    brief: chu(d.brief, 3000), trang: chu(d.trang, 200), nguon: {}, loai: LOAI.includes(d.loai) ? d.loai : "brief",
  };
  if (d.nguon && typeof d.nguon === "object") for (const k of ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"]) if (d.nguon[k]) x.nguon[k] = chu(String(d.nguon[k]), 80);
  if (!x.ho_ten) return [null, "Thiếu họ tên"];
  if (!x.cong_ty && x.loai === "brief") return [null, "Thiếu tên công ty"];
  if (x.loai === "goi-lai" && !x.dien_thoai) return [null, "Cần số điện thoại để gọi lại"];
  if (x.loai === "tai-bo-kiem" && !x.email) return [null, "Cần email để gửi bộ kiểm"];
  if (!x.dien_thoai && !x.email) return [null, "Cần điện thoại hoặc email"];
  if (x.dien_thoai && !/^[0-9+().\s-]{8,20}$/.test(x.dien_thoai)) return [null, "Số điện thoại chưa đúng"];
  if (x.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email)) return [null, "Email chưa đúng"];
  if (d.dong_y !== true) return [null, "Cần đồng ý để chúng tôi liên hệ"];
  return [x, null];
}

async function guiDi(lead) {
  const viec = [];
  if (process.env.TG_TOKEN && process.env.TG_CHAT) {
    const ten = { "brief": "Brief pitch", "goi-lai": "GỌI LẠI", "tai-bo-kiem": "Tải bộ kiểm (chờ PDF)" }[lead.loai];
    const t = `${ten} ${lead.ma}\n${lead.ho_ten} · ${lead.cong_ty || "-"} · ${lead.vai_tro || "-"}\n${lead.dien_thoai || ""} ${lead.email || ""}\nHạn pitch: ${lead.han_pitch || "-"} · Asset: ${lead.loai_asset.join(", ") || "-"} · NS: ${lead.ngan_sach || "-"} · Gợi ý: ${lead.goi || "-"}\nKhách cuối: ${lead.an_ten_khach ? "(ẩn tên) " : ""}${lead.khach_hang || "-"}\nNguồn: ${lead.nguon.kenh || lead.nguon.utm_source || "trực tiếp"}`;
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
  const ma = "UK-" + new Date().toISOString().slice(2, 10).replace(/-/g, "") + "-" + randomBytes(2).toString("hex").toUpperCase();
  if (d.website) return tra(res, 200, { ok: true, ma }); // bẫy bot: giả vờ nhận
  const [x, loi] = kiem(d);
  if (loi) return tra(res, 400, { loi });
  ds.push(now); luot.set(ip, ds);
  const lead = { ma, luc: new Date().toISOString(), ...x, dong_y: { luc: new Date().toISOString(), cau: DONG_Y[x.loai], ip }, ua: chu(req.headers["user-agent"] || "", 200) };
  await mkdir(LEAD_DIR, { recursive: true });
  await appendFile(join(LEAD_DIR, "leads.jsonl"), JSON.stringify(lead) + "\n");
  if (x.loai === "tai-bo-kiem") await appendFile(join(LEAD_DIR, "cho-bo-kiem.jsonl"), JSON.stringify({ ma, luc: lead.luc, ho_ten: x.ho_ten, email: x.email, cong_ty: x.cong_ty }) + "\n"); // danh sách chờ gửi PDF
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
}).listen(PORT, () => console.log(`unikon-site chạy ở http://localhost:${PORT}`));
