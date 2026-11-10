"""API công khai cho Kho case có số (cred) và nội dung Trang BU ifagent.

Thuần Python ở mức nạp file (không `import frappe` ở đầu file); nạp trễ `frappe` trong hàm.
"""
from __future__ import annotations

import json
import logging
import pathlib

from linhx_goi_agentforce.cred import kho_case
from linhx_goi_agentforce.cred.kho_case import case_cong_khai, noi_dung_trang_bu

logger = logging.getLogger(__name__)

TRUONG_CASE_CONG_KHAI = [
    "name",
    "tieu_de",
    "khach_hang",
    "cho_phep_hien_ten",
    "chi_so",
    "mo_ta",
    "da_duyet",
]
GIOI_HAN_CASE = 100


def _lay_frappe():
    try:
        import frappe
    except ImportError:
        return None
    return frappe


def _whitelist(allow_guest: bool = False):
    def _trang_tri(fn):
        frappe = _lay_frappe()
        if frappe is not None and callable(getattr(frappe, "whitelist", None)):
            fn = frappe.whitelist(allow_guest=allow_guest)(fn)
        setattr(fn, "_allow_guest", bool(allow_guest))
        return fn

    return _trang_tri


def _duong_site_ifagent() -> pathlib.Path:
    goc_repo = pathlib.Path(__file__).resolve().parents[4]
    return goc_repo / "sites" / "ifagent" / "site.json"


def _doc_site_ifagent() -> dict:
    duong = _duong_site_ifagent()
    if duong.exists():
        try:
            du_lieu = json.loads(duong.read_text(encoding="utf-8"))
            if isinstance(du_lieu, dict):
                return du_lieu
        except Exception as exc:
            logger.warning("Không đọc được sites/ifagent/site.json: %s", exc)
    return {
        "ten": "ifagent",
        "ban_cai": "ifagent",
        "noi_dung": {
            "tieu_de": "ifAgent — Trang BU Trợ lý AI và Tự động hoá",
            "mo_ta": "Giải pháp chuẩn hoá quy trình kinh doanh, chăm sóc khách hàng và vận hành tự động trên nền LINHX ENGINE.",
            "muc": [],
        },
    }


def _doc_ds_case_tu_db() -> list[dict]:
    frappe = _lay_frappe()
    if frappe is None:
        return []
    get_all_fn = getattr(frappe, "get_all", None)
    if not callable(get_all_fn):
        db = getattr(frappe, "db", None)
        get_all_fn = getattr(db, "get_all", None) if db is not None else None
    if not callable(get_all_fn):
        return []

    try:
        rows = get_all_fn(
            "LX Case",
            filters={"da_duyet": 1},
            fields=list(TRUONG_CASE_CONG_KHAI),
            order_by="modified desc",
            limit_page_length=GIOI_HAN_CASE,
        )
    except Exception as exc:
        logger.warning("Lỗi truy vấn LX Case: %s", exc)
        return []

    if not isinstance(rows, (list, tuple)):
        return []
    return [dict(r) for r in rows if isinstance(r, dict)]


@_whitelist(allow_guest=True)
def danh_sach_case() -> list[dict]:
    """Trả danh sách các case đã duyệt có chỉ số kết quả; ẩn tuyệt đối case chưa duyệt."""
    ds_db = _doc_ds_case_tu_db()
    return case_cong_khai(ds_db)


@_whitelist(allow_guest=True)
def noi_dung_ifagent() -> dict:
    """Trả nội dung Trang BU ifagent chỉ ghép các case công khai đã duyệt từ DB."""
    site_cfg = _doc_site_ifagent()
    ds_db = _doc_ds_case_tu_db()
    return kho_case.noi_dung_trang_bu(site_cfg, case_cong_khai(ds_db))
