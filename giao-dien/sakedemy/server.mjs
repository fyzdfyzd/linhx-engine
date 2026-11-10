// Máy phục vụ giao diện sakedemy.com và chuyển tiếp lead về LINHX Engine. Node ≥ 18, không cần cài gói.
// Chạy: node server.mjs  (PORT=8080). Cấu hình qua biến môi trường:
//   LINHX_FORM_URL      -> endpoint nhận form của engine (mặc định http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form)
//   TRUST_PROXY=1       -> đứng sau Caddy/Nginx, lấy IP thật từ X-Forwarded-For
//   RATE_MAX            -> số lead tối đa mỗi IP trong 10 phút (mặc định 5)
import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname, resolve, sep } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const BU = "sakedemy";
const PORT = +process.env.PORT || 8080;
const LINHX_FORM_URL = process.env.LINHX_FORM_URL || "http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form";
const GOC = resolve(fileURLToPath(new URL("./public/", import.meta.url)));
const GOC_TIEN_TO = GOC + sep;
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ttf": "font/ttf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8" };
const DAU = { "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin", "X-Frame-Options": "SAMEORIGIN" };
const DUONG_FORM = ["/api/brief", "/api/lead", "/api/form"];
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
  const kenh_nguon = {};
  if (d.nguon && typeof d.nguon === "object") for (const k of ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"]) if (d.nguon[k]) kenh_nguon[k] = chu(String(d.nguon[k]), 80);
  const x = {
    loai: LOAI.includes(d.loai) ? d.loai : "tu-van",
    ho_ten: chu(d.ho_ten, 80), cong_ty: chu(d.cong_ty, 120), vai_tro: chu(d.vai_tro, 80), dien_thoai: chu(d.dien_thoai, 20), email: chu(d.email, 120),
    so_hoc_vien: chu(d.so_hoc_vien, 40), phong_ban: ds(d.phong_ban, 30), hinh_thuc: chu(d.hinh_thuc, 20), thoi_gian: chu(d.thoi_gian, 40),
    nhu_cau: chu(d.nhu_cau, 1800), goi: chu(d.goi, 40), trang: chu(d.trang, 200), kenh_nguon, nguon: BU,
  };
  if (x.loai === "hoc-thu") { if (!x.email) return [null, "Cần email để gửi bài học thử"]; }
  else if (!x.ho_ten) return [null, "Thiếu họ tên"];
  if (!x.cong_ty && x.loai === "tu-van") return [null, "Thiếu tên công ty"];
  if (x.loai === "goi-lai" && !x.dien_thoai) return [null, "Cần số điện thoại để gọi lại"];
  if (!x.dien_thoai && !x.email) return [null, "Cần điện thoại hoặc email"];
  if (x.dien_thoai && !/^[0-9+().\s-]{8,20}$/.test(x.dien_thoai)) return [null, "Số điện thoại chưa đúng"];
  if (x.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email)) return [null, "Email chưa đúng"];
  if (d.dong_y !== true && d.dong_y_lien_he !== true) return [null, "Cần đồng ý để chúng tôi liên hệ"];
  if (!x.nhu_cau) {
    x.nhu_cau = chu([x.loai, x.cong_ty, x.vai_tro, x.goi, x.so_hoc_vien, x.phong_ban.join(", "), x.hinh_thuc, x.thoi_gian].filter(Boolean).join(" · "), 1800);
  }
  return [x, null];
}

async function guiDi(lead, ip) {
  const dau = { "Content-Type": "application/json", Accept: "application/json" };
  if (ip) dau["X-Forwarded-For"] = ip;
  const r = await fetch(LINHX_FORM_URL, {
    method: "POST",
    headers: dau,
    body: JSON.stringify(lead),
    signal: AbortSignal.timeout(10000),
  });
  let kq = null;
  try { kq = JSON.parse(await r.text()); } catch {}
  if (!r.ok || (kq && typeof kq === "object" && (kq.ok === false || kq.exc))) {
    throw new Error(`Engine trả mã ${r.status}`);
  }
  return kq;
}

async function nhanBrief(req, res) {
  const ip = ((process.env.TRUST_PROXY === "1" && req.headers["x-forwarded-for"]) || req.socket.remoteAddress || "").split(",")[0].trim();
  const now = Date.now(), dsLuot = (luot.get(ip) || []).filter((t) => now - t < 600000);
  if (dsLuot.length >= (+process.env.RATE_MAX || 5)) return tra(res, 429, { loi: "Bạn gửi hơi nhiều, thử lại sau ít phút" });
  let tho = "";
  for await (const c of req) { tho += c; if (tho.length > 20000) return tra(res, 413, { loi: "Brief quá dài" }); }
  let d; try { d = JSON.parse(tho); } catch { return tra(res, 400, { loi: "Dữ liệu không đọc được" }); }
  const ma = "SK-" + new Date().toISOString().slice(2, 10).replace(/-/g, "") + "-" + randomBytes(2).toString("hex").toUpperCase();
  if (d.website || d.hp_url || d.trap_field) return tra(res, 200, { ok: true, ma }); // bẫy bot: giả vờ nhận
  const [x, loi] = kiem(d);
  if (loi) return tra(res, 400, { loi });
  dsLuot.push(now); luot.set(ip, dsLuot);
  const luc = new Date().toISOString();
  const lead = { ma, luc, ...x, nguon: BU, dong_y_lien_he: true, dong_y: { luc, cau: CAU_DONG_Y[x.loai], ip }, ua: chu(req.headers["user-agent"] || "", 200) };
  try {
    await guiDi(lead, ip);
  } catch (e) {
    console.error("chuyển lead sang engine lỗi:", e?.message || e);
    return tra(res, 502, { loi: "Máy nhận lead đang tạm bận, vui lòng thử lại sau ít phút" });
  }
  tra(res, 200, { ok: true, ma });
}

async function tinh(req, res) {
  let p;
  try { p = decodeURIComponent(new URL(req.url, "http://x").pathname); } catch { return tra(res, 400, { loi: "Đường dẫn không hợp lệ" }); }
  if (p.endsWith("/")) p += "index.html";
  const f = resolve(GOC, "." + p);
  if (f !== GOC && !f.startsWith(GOC_TIEN_TO)) return tra(res, 403, { loi: "cấm" });
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
  const duong = new URL(req.url, "http://x").pathname;
  if (DUONG_FORM.some((d) => duong === d || duong.startsWith(d + "/"))) {
    return req.method === "POST" ? nhanBrief(req, res).catch((e) => { console.error(e); tra(res, 500, { loi: "Máy nhận đang lỗi" }); }) : tra(res, 405, { loi: "Chỉ nhận POST" });
  }
  if (duong === "/api/song") return tra(res, 200, { ok: true });
  if (req.method !== "GET" && req.method !== "HEAD") return tra(res, 405, { loi: "Không hỗ trợ" });
  tinh(req, res);
}).listen(PORT, () => console.log(`sakedemy-site chạy ở http://localhost:${PORT}`));
