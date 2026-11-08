"""Endpoint Frappe cho adapter Chiêm Tinh Số (CTS): checkout và sepay_webhook.

Lưu trữ đơn và giao dịch trong DocType `LX Don CTS` và `LX Giao Dich CTS` (Frappe DB),
khoá dòng `SELECT ... FOR UPDATE` kết hợp ràng buộc `unique` trên `tx_id` để chống đua đồng thời.
"""
from __future__ import annotations

import json
import logging

import frappe

from linhx_core.cts_adapter import hop_dong

_logger = logging.getLogger(__name__)


def _ghi_log_canh_bao(thong_diep: str, exc: Exception) -> None:
    loai_loi = type(exc).__name__
    try:
        log_fn = getattr(frappe, "logger", None)
        if callable(log_fn):
            log_fn().warning("%s (%s)", thong_diep, loai_loi)
            return
    except Exception:
        pass
    _logger.warning("%s (%s)", thong_diep, loai_loi)


def _doc_payload(kwargs: dict) -> dict:
    req = getattr(frappe, "request", None)
    if req is not None:
        try:
            du_lieu = req.get_json(silent=True)
            if isinstance(du_lieu, dict):
                return dict(du_lieu)
        except Exception as exc:
            _ghi_log_canh_bao("Lỗi đọc JSON từ request.get_json trong cts_adapter", exc)
        try:
            raw = req.get_data(as_text=True)
            if raw:
                du_lieu = json.loads(raw)
                if isinstance(du_lieu, dict):
                    return dict(du_lieu)
        except Exception as exc:
            _ghi_log_canh_bao("Lỗi giải mã JSON từ request.get_data trong cts_adapter", exc)
    return {k: v for k, v in (kwargs or {}).items() if k != "cmd"}


def _doc_cau_hinh_site() -> dict:
    conf = getattr(frappe, "conf", None) or {}
    try:
        return dict(conf)
    except Exception:
        return {}


def _doc_secret_webhook() -> str:
    return hop_dong.doc_cau_hinh_cts(_doc_cau_hinh_site())["sepay_khoa"]


def _doc_danh_muc() -> dict:
    conf = _doc_cau_hinh_site()
    dm = conf.get("cts_danh_muc")
    if isinstance(dm, dict) and dm:
        return dm
    return dict(hop_dong.DANH_MUC_MAC_DINH)


def _la_loi_trung_db(exc: Exception) -> bool:
    dup_cls = getattr(frappe, "DuplicateEntryError", None)
    if isinstance(dup_cls, type) and isinstance(exc, dup_cls):
        return True
    ten_lop = type(exc).__name__.lower()
    thong_diep = str(exc).lower()
    return (
        "duplicate" in ten_lop
        or "integrityerror" in ten_lop
        or "duplicate entry" in thong_diep
        or "unique constraint" in thong_diep
    )


def _gan_ma_http(ma_http: int) -> None:
    local_obj = getattr(frappe, "local", None)
    resp = getattr(local_obj, "response", None) if local_obj is not None else None
    if isinstance(resp, dict):
        resp["http_status_code"] = ma_http


def _luu_don_cts_db(don_luu: dict) -> None:
    """Lưu đơn CTS mới vào DocType `LX Don CTS` và commit."""
    ho_so_json = (
        json.dumps(don_luu.get("ho_so") or {}, ensure_ascii=False)
        if isinstance(don_luu.get("ho_so"), dict)
        else str(don_luu.get("ho_so") or "{}")
    )
    doc = frappe.get_doc(
        {
            "doctype": "LX Don CTS",
            "order_id": don_luu["order_id"],
            "noi_dung_ck": don_luu["noi_dung_ck"],
            "sku": don_luu["sku"],
            "ten_san_pham": don_luu.get("ten_san_pham") or "",
            "kenh": don_luu["kenh"],
            "gia_goc": int(don_luu["gia_goc"]),
            "tong": int(don_luu["tong"]),
            "da_nhan": int(don_luu.get("da_nhan") or 0),
            "trang_thai": don_luu.get("trang_thai") or "cho_thanh_toan",
            "email": don_luu["email"],
            "ho_so": ho_so_json,
            "dong_y_dieu_khoan": 1 if don_luu.get("dong_y_dieu_khoan") else 0,
            "dong_y_nhan_tin": 1 if don_luu.get("dong_y_nhan_tin") else 0,
            "created_at": don_luu.get("created_at") or "",
            "expires_at": don_luu.get("expires_at") or "",
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=True, methods=["POST"])
def checkout(**kwargs):
    """Nhận yêu cầu tạo đơn CTS (POST /v1/checkout), lưu vào DocType `LX Don CTS` và trả kết quả cùng dạng CTS.

    Chống trùng mã đơn dựa vào ràng buộc `unique` trên `order_id` và `noi_dung_ck` trong DB kết hợp vòng thử lại.
    """
    payload = _doc_payload(kwargs)
    danh_muc = _doc_danh_muc()
    cau_hinh = _doc_cau_hinh_site()
    kho: dict[str, list[dict]] = {"don": [], "tx": []}

    for _lan_thu in range(3):
        so_don_truoc = len(kho["don"])
        ma_http, than = hop_dong.tao_don(
            payload,
            danh_muc,
            kho,
            cau_hinh=cau_hinh,
        )
        if ma_http != 200:
            _gan_ma_http(ma_http)
            return than

        don_moi = kho["don"][-1] if len(kho["don"]) > so_don_truoc else None
        try:
            if don_moi is not None:
                _luu_don_cts_db(don_moi)
            _gan_ma_http(200)
            return than
        except Exception as exc:
            if getattr(frappe, "db", None) is not None and hasattr(frappe.db, "rollback"):
                frappe.db.rollback()
            if _la_loi_trung_db(exc):
                continue
            raise

    _gan_ma_http(500)
    return {"detail": "Không thể tạo mã đơn duy nhất sau nhiều lần thử"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def sepay_webhook(**kwargs):
    """Nhận webhook SePay của CTS (POST /v1/pay/sepay/webhook), khoá dòng DB (`FOR UPDATE`) và lưu giao dịch.

    Ghi chú theo hành vi gốc của CTS (`handle_sepay_webhook`):
    - Chỉ khi `status == "matched"` mới ghi bản ghi `LX Giao Dich CTS` (cột `tx_id` unique) và cập nhật `LX Don CTS`.
    - Các webhook `unmatched` (không tìm thấy mã đơn tương ứng) hoặc `ignored` (`transferType != "in"`)
      không ghi vào `LX Giao Dich CTS`, nên nếu SePay hoặc người vận hành gửi lại sau khi đơn đã có mặt
      thì giao dịch sẽ được đối soát lại bình thường.
    """
    authorization = frappe.get_request_header("Authorization")
    secret = _doc_secret_webhook()
    payload = _doc_payload(kwargs)

    if not hop_dong.xac_thuc_apikey(authorization, secret) or not isinstance(payload, dict):
        ma_http, than = hop_dong.nhan_webhook(
            payload,
            {"don": [], "tx": []},
            authorization,
            secret,
        )
        _gan_ma_http(ma_http)
        return than

    raw_id = payload.get("id")
    tx_id = "" if (raw_id is None or isinstance(raw_id, bool)) else str(raw_id).strip()
    if not tx_id:
        ma_http, than = hop_dong.nhan_webhook(
            payload,
            {"don": [], "tx": []},
            authorization,
            secret,
        )
        _gan_ma_http(ma_http)
        return than

    ma_ck = hop_dong.trich_ma_cts(payload.get("content"))
    rows_don: list[dict] = []

    try:
        if ma_ck:
            rows_don = frappe.db.sql(
                "SELECT name, order_id, sku, ten_san_pham, kenh, gia_goc, tong, da_nhan, "
                "trang_thai, noi_dung_ck, created_at, expires_at "
                "FROM `tabLX Don CTS` WHERE noi_dung_ck = %s FOR UPDATE",
                (ma_ck,),
                as_dict=True,
            ) or []
        da_co_tx = frappe.db.sql(
            "SELECT name, tx_id, order_id FROM `tabLX Giao Dich CTS` WHERE tx_id = %s FOR UPDATE",
            (tx_id,),
            as_dict=True,
        ) or []

        ds_don = [dict(r) for r in rows_don]
        ds_tx = [tx_id] if da_co_tx else []
        kho = {"don": ds_don, "tx": ds_tx}

        ma_http, than = hop_dong.nhan_webhook(
            payload,
            kho,
            authorization,
            secret,
        )
        if ma_http != 200:
            frappe.db.rollback()
            _gan_ma_http(ma_http)
            return than

        if than.get("idempotent"):
            if than.get("order_id") is None and da_co_tx and da_co_tx[0].get("order_id"):
                than["order_id"] = da_co_tx[0]["order_id"]
            frappe.db.commit()
            _gan_ma_http(200)
            return than

        # Ghi chú: chỉ lưu LX Giao Dich CTS khi khớp đơn (status == "matched").
        # Với status == "unmatched" hoặc "ignored", không lưu tx_id vào LX Giao Dich CTS
        # (khớp đúng hành vi handle_sepay_webhook hiện nay của CTS) để có thể xử lý lại khi gửi lại.
        if than.get("status") == "matched" and ds_don:
            don_sau = ds_don[0]
            doc_tx = frappe.get_doc(
                {
                    "doctype": "LX Giao Dich CTS",
                    "tx_id": tx_id,
                    "order_id": don_sau.get("order_id"),
                    "noi_dung_ck": ma_ck or "",
                    "loai_gd": str(payload.get("transferType") or "in"),
                    "so_tien": int(payload.get("transferAmount") or 0),
                    "trang_thai_ket_qua": "matched",
                    "noi_dung_goc": str(payload.get("content") or ""),
                }
            )
            doc_tx.insert(ignore_permissions=True)

            frappe.db.sql(
                "UPDATE `tabLX Don CTS` SET da_nhan = %s, trang_thai = %s WHERE name = %s",
                (
                    int(don_sau["da_nhan"]),
                    str(don_sau["trang_thai"]),
                    don_sau.get("name") or don_sau["order_id"],
                ),
            )
        frappe.db.commit()

        _gan_ma_http(200)
        return than
    except Exception as exc:
        if getattr(frappe, "db", None) is not None and hasattr(frappe.db, "rollback"):
            frappe.db.rollback()
        if _la_loi_trung_db(exc):
            order_id_trung = rows_don[0].get("order_id") if rows_don else None
            _gan_ma_http(200)
            return {
                "ok": True,
                "idempotent": True,
                "tx_id": tx_id,
                "order_id": order_id_trung,
            }
        raise
