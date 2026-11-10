"""Endpoint công khai bán gói báo cáo 'AI nói gì về thương hiệu' và tạo đơn VietQR."""
from __future__ import annotations

import importlib

import frappe
from frappe.rate_limiter import rate_limit

from linhx_core.api import tim_ham


def _nap_ham_cung_cap(khoa: str):
    ds = tim_ham("cung_cap", khoa)
    if not ds:
        thong_diep = f"Chưa cài gói cung cấp '{khoa}'"
        if callable(getattr(frappe, "throw", None)):
            frappe.throw(thong_diep)
        raise LookupError(thong_diep)
    duong_ham = ds[0]
    ten_module, ten_ham = duong_ham.rsplit(".", 1)
    try:
        mod = importlib.import_module(ten_module)
    except ImportError as exc:
        thong_diep = f"Không nạp được gói cung cấp '{khoa}' ({ten_module})"
        if callable(getattr(frappe, "throw", None)):
            frappe.throw(thong_diep)
        raise LookupError(thong_diep) from exc
    ham = getattr(mod, ten_ham, None)
    if not callable(ham):
        thong_diep = f"Hàm cung cấp '{duong_ham}' cho '{khoa}' không hợp lệ"
        if callable(getattr(frappe, "throw", None)):
            frappe.throw(thong_diep)
        raise LookupError(thong_diep)
    return ham


def _ds_goi() -> list[dict]:
    rows = frappe.get_all(
        "LX Goi",
        fields=["name", "ma", "ten", "gia", "gia_san", "mo_ta", "ban", "workflow"],
        ignore_permissions=True,
    )
    ket_qua: list[dict] = []
    for r in rows or []:
        d = dict(r)
        d["ma"] = d.get("ma") or d.get("name")
        d["ban"] = bool(d.get("ban"))
        ket_qua.append(d)
    return ket_qua


def _ngan_hang() -> dict:
    conf = getattr(frappe, "conf", None) or {}
    nh = conf.get("ngan_hang") or conf.get("vietqr")
    if isinstance(nh, dict) and nh.get("bin") and nh.get("so_tk"):
        return nh
    return {
        "bin": conf.get("vietqr_bin") or "",
        "so_tk": conf.get("vietqr_so_tk") or "",
        "ten_tk": conf.get("vietqr_ten_tk") or "",
    }


@frappe.whitelist(allow_guest=True)
def goi() -> list[dict]:
    """Trả danh mục gói báo cáo đang bán cho trang công khai."""
    goi_cong_khai = _nap_ham_cung_cap("baocao.goi_cong_khai")
    return goi_cong_khai(_ds_goi())


def _truong_tuy_chon(gt: object, toi_da: int, mot_dong_fn=None) -> str | None:
    if gt is None:
        return None
    mot_dong = mot_dong_fn or _nap_ham_cung_cap("baocao.mot_dong")
    return mot_dong(gt, toi_da) or None


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=3600)
def tao_don(
    brand,
    goi,
    email=None,
    nganh=None,
    thi_truong=None,
    doi_thu=None,
    su_that=None,
) -> dict:
    """Tạo đơn báo cáo theo gói trong catalog (không nhận giá từ client) và trả thông tin VietQR."""
    mot_dong = _nap_ham_cung_cap("baocao.mot_dong")
    so_tien_don = _nap_ham_cung_cap("baocao.so_tien_don")
    ten_brand = mot_dong(brand, 90)
    ma_goi = mot_dong(goi, 80)
    if not ten_brand:
        frappe.throw("Vui lòng nhập tên thương hiệu")
    if len(ten_brand) > 80:
        frappe.throw("Tên thương hiệu không được vượt quá 80 ký tự")
    if not ma_goi:
        frappe.throw("Vui lòng chọn gói báo cáo")

    ds = _ds_goi()
    tien = so_tien_don(ma_goi, ds)
    if tien is None:
        frappe.throw("Gói không hợp lệ hoặc đã ngừng bán")

    goi_goc = next((x for x in ds if x.get("ma") == ma_goi or x.get("name") == ma_goi), None) or {"ma": ma_goi}
    goi_hop_le = {**goi_goc, "gia": tien}
    ma_don = f"DON-{frappe.generate_hash(length=8).upper()}"
    tao_don_vietqr = _nap_ham_cung_cap("vn.tao_don")
    don = tao_don_vietqr(goi_hop_le, nguoi="", ngan_hang=_ngan_hang(), ma_don=ma_don)

    doc = frappe.get_doc(
        {
            "doctype": "LX Don",
            "ma": don["ma"],
            "goi": goi_goc.get("name") or goi_goc.get("ma"),
            "so_tien": don["so_tien"],
            "trang_thai": don["trang_thai"],
            "noi_dung_ck": don["noi_dung_ck"],
            "qr_url": don["qr_url"],
            "brand": ten_brand,
            "email": _truong_tuy_chon(email, 120, mot_dong),
            "nganh": _truong_tuy_chon(nganh, 80, mot_dong),
            "thi_truong": _truong_tuy_chon(thi_truong, 60, mot_dong),
            "doi_thu": _truong_tuy_chon(doi_thu, 120, mot_dong),
            "su_that": _truong_tuy_chon(su_that, 600, mot_dong),
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "ma_don": don["ma"],
        "so_tien": don["so_tien"],
        "noi_dung_ck": don["noi_dung_ck"],
        "qr_url": don["qr_url"],
    }
