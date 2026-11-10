// Máy phục vụ giao diện tuva.work (TUVA Communication) và chuyển tiếp lead về LINHX Engine. Node ≥ 18, không cần cài gói.
// Chạy: node server.mjs  (PORT=8080). Cấu hình qua biến môi trường:
//   LINHX_FORM_URL      -> endpoint nhận form của engine (mặc định http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form)
//   TRUST_PROXY=1       -> đứng sau Caddy/Nginx, lấy IP thật từ X-Forwarded-For
//   RATE_MAX            -> số brief tối đa mỗi IP trong 10 phút (mặc định 5)
import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname, resolve, sep } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const BU = "tuva";
const PORT = +process.env.PORT || 8080;
const LINHX_FORM_URL = process.env.LINHX_FORM_URL || "http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form";
try {
  const u = new URL(LINHX_FORM_URL);
  if (u.protocol === "http:" && !["127.0.0.1", "localhost", "::1", "[::1]"].includes(u.hostname)) {
    console.warn(`[${BU}] Cảnh báo: LINHX_FORM_URL dùng HTTP ngoài loopback (${u.hostname}); nên dùng HTTPS để mã hoá dữ liệu khách.`);
  }
} catch {}
const GOC = resolve(fileURLToPath(new URL("./public/", import.meta.url)));
const GOC_TIEN_TO = GOC + sep;
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ttf": "font/ttf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8" };
const DAU = { "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin", "X-Frame-Options": "SAMEORIGIN" };
const DUONG_FORM = ["/api/brief", "/api/lead", "/api/form"];
const luot = new Map(); // ip -> [mốc thời gian]

function tra(res, code, obj) { res.writeHead(code, { ...DAU, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }); res.end(JSON.stringify(obj)); }
const chu = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");

const LOAI = ["brief", "goi-lai", "tai-bo-quy-tac"];
const CAU = {
  vi: { brief: "Tôi đồng ý để TUVA dùng thông tin này để liên hệ về dự án.", "goi-lai": "Tôi đồng ý để TUVA gọi lại cho tôi.", "tai-bo-quy-tac": "Tôi đồng ý để TUVA gửi bộ quy tắc và thông tin liên quan tới email này." },
  en: { brief: "I agree that TUVA may use this information to contact me about the project.", "goi-lai": "I agree that TUVA may call me back.", "tai-bo-quy-tac": "I agree that TUVA may email me the AI rules and related information." },
};

function kiem(d) {
  const kenh_nguon = {};
  if (d.nguon && typeof d.nguon === "object") for (const k of ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"]) if (d.nguon[k]) kenh_nguon[k] = chu(String(d.nguon[k]), 80);
  // Engine giới hạn nhu_cau tối đa 2000 ký tự; từ chối trên 1800 ký tự để không cắt bớt im lặng
  if (typeof d.brief === "string" && d.brief.trim().length > 1800) return [null, "Brief quá dài (tối đa 1800 ký tự)"];
  if (typeof d.nhu_cau === "string" && d.nhu_cau.trim().length > 1800) return [null, "Nhu cầu quá dài (tối đa 1800 ký tự)"];
  const x = {
    loai: LOAI.includes(d.loai) ? d.loai : "brief", ngon_ngu: d.ngon_ngu === "en" ? "en" : "vi",
    ho_ten: chu(d.ho_ten, 80), cong_ty: chu(d.cong_ty, 120), dien_thoai: chu(d.dien_thoai, 20), email: chu(d.email, 120),
    vai_tro: chu(d.vai_tro, 60), linh_vuc: chu(d.linh_vuc, 60), han_nop: chu(d.han_nop, 10), nha_tai_tro: chu(d.nha_tai_tro, 120),
    ngan_sach: chu(d.ngan_sach, 60), brief: chu(d.brief, 1800), nhu_cau: chu(d.nhu_cau, 1800), ket_qua: chu(d.ket_qua, 200), trang: chu(d.trang, 200), kenh_nguon, nguon: BU,
  };
  if (!x.ho_ten) return [null, "Thiếu họ tên"];
  if (!x.cong_ty && x.loai === "brief") return [null, "Thiếu tên tổ chức"];
  if (x.loai === "goi-lai" && !x.dien_thoai) return [null, "Cần số điện thoại để gọi lại"];
  if (x.loai === "tai-bo-quy-tac" && !x.email) return [null, "Cần email để gửi bộ quy tắc"];
  if (!x.dien_thoai && !x.email) return [null, "Cần điện thoại hoặc email"];
  if (x.dien_thoai && !/^[0-9+().\s-]{8,20}$/.test(x.dien_thoai)) return [null, "Số điện thoại chưa đúng"];
  if (x.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x.email)) return [null, "Email chưa đúng"];
  if (x.han_nop && !/^\d{4}-\d{2}-\d{2}$/.test(x.han_nop)) x.han_nop = "";
  if (d.dong_y !== true && d.dong_y_lien_he !== true) return [null, "Cần đồng ý để chúng tôi liên hệ"];
  if (!x.nhu_cau) {
    x.nhu_cau = chu(x.brief || [x.loai, x.cong_ty, x.linh_vuc, x.nha_tai_tro, x.han_nop, x.ngan_sach, x.ket_qua].filter(Boolean).join(" · "), 1800);
  }
  if (x.loai !== "brief" && x.nhu_cau && !x.nhu_cau.startsWith(`[${x.loai}]`) && !x.nhu_cau.startsWith(`${x.loai} ·`)) {
    x.nhu_cau = chu(`[${x.loai}] ${x.nhu_cau}`, 1900);
  }
  return [x, null];
}

function layIp(req) {
  if (process.env.TRUST_PROXY === "1") {
    const xff = req.headers["x-forwarded-for"];
    if (typeof xff === "string" && xff.trim()) {
      const dsIp = xff.split(",").map((s) => s.trim()).filter(Boolean);
      if (dsIp.length) return dsIp[dsIp.length - 1];
    }
    const xReal = req.headers["x-real-ip"];
    if (typeof xReal === "string" && xReal.trim()) return xReal.trim();
  }
  return (req.socket.remoteAddress || "").trim();
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
  const hopLe =
    kq &&
    typeof kq === "object" &&
    !kq.exc &&
    (kq.ok === true || (kq.message && typeof kq.message === "object" ? kq.message.ok !== false : "message" in kq));
  if (!r.ok || !hopLe) {
    throw new Error(`Engine trả mã ${r.status}`);
  }
  return kq;
}

async function nhanBrief(req, res) {
  const ip = layIp(req);
  const now = Date.now(), dsLuot = (luot.get(ip) || []).filter((t) => now - t < 600000);
  if (dsLuot.length >= (+process.env.RATE_MAX || 5)) return tra(res, 429, { loi: "Bạn gửi hơi nhiều, thử lại sau ít phút" });
  let tho = "";
  for await (const c of req) { tho += c; if (tho.length > 20000) return tra(res, 413, { loi: "Brief quá dài" }); }
  let d; try { d = JSON.parse(tho); } catch { return tra(res, 400, { loi: "Dữ liệu không đọc được" }); }
  const ma = "TV-" + new Date().toISOString().slice(2, 10).replace(/-/g, "") + "-" + randomBytes(2).toString("hex").toUpperCase();
  if (d.website || d.hp_url || d.trap_field) return tra(res, 200, { ok: true, ma }); // bẫy bot: giả vờ nhận
  const [x, loi] = kiem(d);
  if (loi) return tra(res, 400, { loi });
  dsLuot.push(now); luot.set(ip, dsLuot);
  const luc = new Date().toISOString();
  const lead = { ma, luc, ...x, nguon: BU, dong_y_lien_he: true, dong_y: { luc, cau: CAU[x.ngon_ngu][x.loai], ip }, ua: chu(req.headers["user-agent"] || "", 200) };
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
  let duong;
  try { duong = new URL(req.url, "http://x").pathname; } catch { return tra(res, 400, { loi: "Đường dẫn không hợp lệ" }); }
  if (DUONG_FORM.some((d) => duong === d || duong.startsWith(d + "/"))) {
    return req.method === "POST" ? nhanBrief(req, res).catch((e) => { console.error(e); tra(res, 500, { loi: "Máy nhận đang lỗi" }); }) : tra(res, 405, { loi: "Chỉ nhận POST" });
  }
  if (duong === "/api/song") return tra(res, 200, { ok: true });
  if (req.method !== "GET" && req.method !== "HEAD") return tra(res, 405, { loi: "Không hỗ trợ" });
  tinh(req, res);
}).listen(PORT, () => console.log(`tuva-site chạy ở http://localhost:${PORT}`));
