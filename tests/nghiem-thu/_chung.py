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

GOC = pathlib.Path(__file__).resolve().parents[2]          # linhx-engine/
REPO = GOC.parent                                         # gốc repo git
CORE = GOC / "apps" / "linhx_core"                        # app Frappe linhx_core
BANG_CHUNG = GOC / "bang-chung"

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


def nap_module(ten_module, duong_dan_goc, chan_frappe=True):
    """Nạp module Python thuần (không cần Frappe). chan_frappe=True: `import frappe` ở đầu module sẽ lỗi."""
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


def tim_doctype(ten, goc=CORE):
    """Tìm file JSON định nghĩa DocType có "name" == ten trong goc. Trả (đường dẫn, dict) hoặc (None, None)."""
    tep = ten.lower().replace(" ", "_") + ".json"
    for p in pathlib.Path(goc).rglob(tep):
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
