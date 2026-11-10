"""Hàm dùng chung cho bộ nghiệm thu LINHX ENGINE đợt 1.

Bộ nghiệm thu là hộp đen theo tieu_chi trong features-dot1.json. Thợ KHÔNG được sửa thư mục này.
Không gọi mạng thật, không gọi SePay thật. Chỉ được mở máy chủ cục bộ 127.0.0.1 khi cần.
Hợp đồng giao diện (đường dẫn, tên hàm) ghi ở HOP-DONG.md cùng thư mục.
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

GOC = pathlib.Path(__file__).resolve().parents[2]          # gốc repo linhx-engine
REPO = GOC                                                # repo riêng fyzdfyzd/linhx-engine: gốc git = GOC
CORE = GOC / "apps" / "linhx_core"                        # app Frappe linhx_core
BANG_CHUNG = GOC / "bang-chung"
ANH = GOC / ".canh-tho" / "anh"                           # ảnh chụp lúc kiểm (không commit), người canh xem
DU_LIEU = pathlib.Path(__file__).resolve().parent / "du-lieu"

BO_QUA_THU_MUC = {".git", "node_modules", "__pycache__", ".next", "out", ".canh", ".venv", "venv"}

MAU_BI_MAT = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"xox[bpas]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{40,}"),
    # khoá SePay / mật khẩu gán thẳng giá trị thật (không phải biến môi trường hay chỗ trống)
    re.compile(r"(?i)(sepay[_a-z]*|api_?key|secret|password|mat_?khau|token)\s*[:=]\s*['\"][A-Za-z0-9+/_\-]{24,}['\"]"),
]


def doc_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def cac_file(goc, bo_qua=BO_QUA_THU_MUC):
    goc = pathlib.Path(goc)
    for p in goc.rglob("*"):
        if p.is_file() and not (set(p.relative_to(goc).parts[:-1]) & bo_qua):
            yield p


def quet_bi_mat(goc, bo_qua_file=()):
    """Trả danh sách 'đường_dẫn: mẫu' của chỗ giống bí mật."""
    loi = []
    for p in cac_file(goc):
        if p.name in bo_qua_file or p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2", ".pdf", ".zip"}:
            continue
        try:
            chu = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in MAU_BI_MAT:
            if m.search(chu):
                loi.append(f"{p}: {m.pattern[:40]}")
                break
    return loi


def file_bi_mat(goc):
    """File không được có: .env thật, khoá riêng, chứng chỉ, file phiên đăng nhập."""
    loi = []
    for p in cac_file(goc):
        ten = p.name.lower()
        if (ten == ".env" or (ten.startswith(".env.") and not ten.endswith((".example", ".mau", ".sample")))
                or ten.endswith((".pem", ".key", ".p12", ".pfx", ".keystore"))
                or ten in {"id_rsa", "id_ed25519", "credentials.json", "token.json", "service-account.json", "tho.env"}):
            loi.append(str(p))
    return loi


# Đợt 3 (Linh 10/11 "sửa luôn"): code chuyển khỏi linhx_core sang adapter/gói. Nghiệm thu cũ tìm chỗ mới trước, chỗ cũ sau.
# tiền tố module cũ -> (thư mục app mới tính từ GOC, tiền tố module mới)
CHUYEN_CHO = {
    "linhx_core.crm.t1": ("apps/linhx_goi_ifagent", "linhx_goi_ifagent.t1"),
    "linhx_core.crm.xac_minh_marketing": ("apps/linhx_goi_ifagent", "linhx_goi_ifagent.xac_minh_marketing"),
    "linhx_core.pay.sau_tra": ("apps/linhx_goi_baocao", "linhx_goi_baocao.sau_tra"),
    "linhx_core.pay.ban_bao_cao": ("apps/linhx_goi_baocao", "linhx_goi_baocao.ban_bao_cao"),
    "linhx_core.pay.sepay": ("apps/linhx_vn", "linhx_vn.pay.sepay"),
    "linhx_core.pay.api_sepay": ("apps/linhx_vn", "linhx_vn.pay.api_sepay"),
    "linhx_core.pay.vietqr": ("apps/linhx_vn", "linhx_vn.pay.vietqr"),
    "linhx_core.pay.so_s1a": ("apps/linhx_vn", "linhx_vn.pay.so_s1a"),
    "linhx_core.pay.api_thue": ("apps/linhx_vn", "linhx_vn.pay.api_thue"),
    "linhx_core.id.zalo_oauth": ("apps/linhx_vn", "linhx_vn.id.zalo_oauth"),
    "linhx_core.id.google_oauth": ("apps/linhx_vn", "linhx_vn.id.google_oauth"),
    "linhx_core.cts_adapter": ("apps/linhx_cts", "linhx_cts"),
    "linhx_core.booking": ("apps/linhx_goi_booking", "linhx_goi_booking"),
    "linhx_core.agent": ("apps/linhx_goi_agentforce", "linhx_goi_agentforce.agent"),
    "linhx_core.cred": ("apps/linhx_goi_agentforce", "linhx_goi_agentforce.cred"),
    "linhx_core.ops": ("apps/linhx_goi_ops", "linhx_goi_ops.ops"),
}


def cho_moi(ten_module):
    """(tên module, thư mục gốc) ở chỗ mới nếu đã chuyển, None nếu chưa."""
    for cu, (app, moi) in CHUYEN_CHO.items():
        if ten_module == cu or ten_module.startswith(cu + "."):
            ten = moi + ten_module[len(cu):]
            f = GOC / app / pathlib.Path(*ten.split("."))
            if f.with_suffix(".py").exists() or (f / "__init__.py").exists():
                return ten, GOC / app
    return None


def ma(duong_trong_core):
    """Đường file code: "pay/vietqr.py" (tính từ apps/linhx_core/linhx_core) -> chỗ mới nếu đã chuyển, chỗ cũ nếu chưa."""
    ten = "linhx_core." + duong_trong_core.removesuffix(".py").replace("/", ".")
    m = cho_moi(ten)
    if m:
        return m[1] / (m[0].replace(".", "/") + ".py")
    return CORE / "linhx_core" / duong_trong_core


def nap_module(ten_module, duong_dan_goc, chan_frappe=True):
    """Nạp module Python thuần (không cần Frappe). chan_frappe=True: `import frappe` ở đầu module sẽ lỗi.
    Module đã chuyển chỗ ở đợt 3 (CHUYEN_CHO) thì nạp bản ở chỗ mới."""
    m = cho_moi(ten_module)
    if m:
        ten_module, duong_dan_goc = m
    duong_dan_goc = str(duong_dan_goc)
    if duong_dan_goc not in sys.path:
        sys.path.insert(0, duong_dan_goc)
    cu = sys.modules.get("frappe", "khong")
    if chan_frappe:
        sys.modules["frappe"] = None  # import frappe -> ImportError
    try:
        for k in [k for k in sys.modules if k == ten_module or k.startswith(ten_module + ".")]:
            del sys.modules[k]
        return importlib.import_module(ten_module)
    finally:
        if chan_frappe:
            if cu == "khong":
                sys.modules.pop("frappe", None)
            else:
                sys.modules["frappe"] = cu


def tim_doctype(ten, goc=None):
    """Tìm file JSON định nghĩa DocType có "name" == ten trong goc. Trả (đường dẫn, dict) hoặc (None, None)."""
    tep = ten.lower().replace(" ", "_") + ".json"
    # goc=None: linhx_core trước rồi mọi app (DocType có thể đã chuyển sang adapter/gói ở đợt 3)
    cac_goc = [goc] if goc is not None else [CORE, GOC / "apps"]
    for p in (q for g in cac_goc for q in pathlib.Path(g).rglob(tep)):
        if "doctype" in p.parts:
            try:
                d = doc_json(p)
            except Exception:
                continue
            if d.get("name") == ten and d.get("doctype") == "DocType":
                return p, d
    return None, None


def ten_truong(d):
    return {f.get("fieldname"): f for f in d.get("fields", [])}


def bang_chung_json(fid, ten_file):
    p = BANG_CHUNG / fid / ten_file
    assert p.exists(), f"thiếu bằng chứng {p.relative_to(GOC)} (ghi từ VM thật, xem HOP-DONG.md)"
    return doc_json(p)


def git(*args, cwd=REPO):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def may_chu_web(thu_muc, api=None, ghi_nhan=None):
    """Máy chủ 127.0.0.1 phục vụ file tĩnh trong thu_muc và API giả cùng gốc.
    api: {"/api/method/x.y": ham(phuong_thuc, than_dict) -> (ma_http, obj | bytes, content_type)}
    ghi_nhan: list, nhận (phuong_thuc, duong_dan, than_dict) của mọi lần gọi API."""
    import functools
    import http.server
    import threading
    from urllib.parse import urlparse

    api = api or {}

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _api(self, pt):
            duong = urlparse(self.path).path
            if duong not in api:
                return False
            n = int(self.headers.get("Content-Length") or 0)
            than = {}
            if n:
                raw = self.rfile.read(n)
                try:
                    than = json.loads(raw.decode("utf-8"))
                except Exception:
                    than = {"_raw": raw.decode("utf-8", "ignore")}
            if ghi_nhan is not None:
                ghi_nhan.append((pt, self.path, than))
            ma, obj, ct = api[duong](pt, than)
            b = obj if isinstance(obj, bytes) else json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(ma)
            self.send_header("Content-Type", ct or "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return True

        def do_GET(self):
            if not self._api("GET"):
                super().do_GET()

        def do_POST(self):
            if not self._api("POST"):
                self.send_error(404)

    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(thu_muc)))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"


PNG_1x1 = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                        "1f15c4890000000d49444154789c6360f8cfc0f01f0005000201e2b2a3f40000000049454e44ae426082")


# ---------- dùng chung cho nghiệm thu đợt 1 phần sau (viết 8/11) ----------

TRANG_BU = GOC / "trang-bu"


def dung_trang_bu(env_them=None, bo=("NOI_DUNG_URL", "SITE_JSON", "API_GOC")):
    """Dựng tĩnh trang-bu (npm run build) với biến môi trường thêm. Trả thư mục out/."""
    import os
    import shutil
    assert (TRANG_BU / "node_modules").is_dir(), "chạy `npm ci` trong trang-bu trước khi kiểm"
    out = TRANG_BU / "out"
    shutil.rmtree(out, ignore_errors=True)
    env = {k: v for k, v in os.environ.items() if k not in bo}
    env.update(NEXT_TELEMETRY_DISABLED="1", **(env_them or {}))
    npm = shutil.which("npm") or "npm"
    r = subprocess.run([npm, "run", "build"], cwd=TRANG_BU, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="ignore", timeout=420)
    assert r.returncode == 0, "dựng tĩnh lỗi:\n" + (r.stdout + r.stderr)[-2000:]
    assert (out / "index.html").exists(), "dựng xong phải có trang-bu/out/index.html"
    return out


def chan_ra_ngoai(pg, goc_url):
    """Chặn mọi request không về máy chủ thử; trả list URL đã bị chặn."""
    bi_chan = []

    def r(route):
        u = route.request.url
        if u.startswith((goc_url, "data:", "blob:")):
            route.continue_()
        else:
            bi_chan.append(u)
            route.abort()
    pg.route("**/*", r)
    return bi_chan


def trang_front_engine(api_them, rong=1280, hash_="#/engine", cho=None):
    """Mở front/index.html#/engine với API giả (người điều hành đã đăng nhập). Trả (playwright, browser, page, server, ghi_nhan)."""
    from playwright.sync_api import sync_playwright
    ghi = []
    api = {
        "/api/method/linhx_worker.api.phien": lambda pt, b: (200, {"message": {"user": "dh@test.local", "dieu_hanh": True, "csrf": "x"}}, None),
        "/api/method/linhx_worker.api.bang": lambda pt, b: (200, {"message": {"workers": [], "workflows": [], "jobs": [], "dem": {}, "luc": "2026-11-09 09:00:00", "user": "dh@test.local"}}, None),
    }
    api.update(api_them)
    s, url = may_chu_web(GOC / "front", api, ghi_nhan=ghi)
    p = sync_playwright().start()
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": rong, "height": 900})
    chan_ra_ngoai(pg, url)
    pg.goto(url + "/index.html" + hash_)
    if cho:
        pg.wait_for_selector(cho, timeout=15000)
    return p, b, pg, s, ghi


def dong_trang(p, b, s):
    try:
        b.close()
        p.stop()
    finally:
        s.shutdown()


def ghi_nguon_proto(p, thu_muc="nguon/03-opc-os/"):
    """File p phải ghi chuyển từ file có thật trong nguon/... (chống viết lại từ đầu)."""
    chu = pathlib.Path(p).read_text(encoding="utf-8")
    m = re.findall(re.escape(thu_muc) + r"[\w./-]+", chu)
    assert m, f"{pathlib.Path(p).name} phải ghi chuyển từ file nào trong {thu_muc}"
    assert any((GOC / x.rstrip(".")).exists() for x in m), f"đường dẫn nguồn ghi trong {pathlib.Path(p).name} không có thật"


def khong_import_frappe_dau_file(p):
    chu = pathlib.Path(p).read_text(encoding="utf-8")
    dau = [d for d in chu.splitlines() if re.match(r"^(import|from)\s", d)]
    assert not any(re.match(r"^(import frappe|from frappe)", d) for d in dau), f"{pathlib.Path(p).name} phải thuần Python (import frappe trong hàm)"
