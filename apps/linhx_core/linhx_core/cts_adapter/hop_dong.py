"""Hợp đồng dữ liệu và luật xử lý tạo đơn + webhook SePay tương thích Chiêm Tinh Số (CTS).

Thuần Python, không import frappe ở đầu file.
"""
from __future__ import annotations

import copy
import hmac
import re
import uuid
from datetime import datetime, timedelta, timezone

MAU_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAU_MA_CTS = re.compile(r"\b(CTS[0-9A-F]{10})\b", re.IGNORECASE)

DANH_MUC_MAC_DINH: dict[str, dict] = {
    "SKU-CT-NATAL-FULL-STD": {
        "ten": "Bản đồ sao cá nhân đầy đủ",
        "gia": 199000,
        "kenh": ["web", "zalo", "messenger"],
    },
    "SKU-CT-CHILD-STD": {
        "ten": "Bản đồ sao cho em bé",
        "gia": 199000,
        "kenh": ["web", "zalo", "messenger"],
    },
    "SKU-CT-SYN-STD": {
        "ten": "Hợp đôi",
        "gia": 299000,
        "kenh": ["web", "zalo", "messenger"],
    },
    "SKU-CT-YEAR-2027-STD": {
        "ten": "Dự báo năm 2027",
        "gia": 249000,
        "kenh": ["web", "zalo", "messenger"],
    },
    "SKU-CT-3M-STD": {
        "ten": "Dự báo 3 tháng",
        "gia": 99000,
        "kenh": ["web"],
    },
}


def _sinh_noi_dung_ck(da_co: set[str]) -> str:
    while True:
        ma = "CTS" + uuid.uuid4().hex[:10].upper()
        if ma not in da_co:
            return ma


def _sinh_order_id(da_co: set[str]) -> str:
    while True:
        ma = "ord_" + uuid.uuid4().hex[:16].lower()
        if ma not in da_co:
            return ma


def xac_thuc_apikey(authorization: str | None, khoa: str | None) -> bool:
    """Kiểm tra header Authorization đúng dạng 'Apikey <khoa>'."""
    if not isinstance(authorization, str) or not isinstance(khoa, str):
        return False
    khoa_sach = khoa.strip()
    if not khoa_sach:
        return False
    mong_doi = f"Apikey {khoa_sach}"
    return hmac.compare_digest(
        authorization.strip().encode("utf-8"),
        mong_doi.encode("utf-8"),
    )


def tao_don(payload: dict, danh_muc: dict, kho: dict) -> tuple[int, dict]:
    """Tạo đơn theo hợp đồng POST /v1/checkout của CTS.

    - Kiểm tra điều khoản, email, hồ sơ và sản phẩm/kênh trong `danh_muc`.
    - Giá lấy từ `danh_muc[sku]["gia"]`, bỏ qua mọi trường `gia`/`tong` do client gửi.
    - Ghi đơn mới vào `kho["don"]` và trả `(200, serialize_public_order)` không lộ `email`, `ho_so`.
    """
    if not isinstance(payload, dict):
        return 422, {"detail": "Dữ liệu đầu vào không hợp lệ"}

    if payload.get("dong_y_dieu_khoan") is not True:
        return 422, {
            "detail": "Bắt buộc xác nhận đồng ý điều khoản ('dong_y_dieu_khoan': true)"
        }

    raw_email = payload.get("email")
    email = str(raw_email).strip().lower() if isinstance(raw_email, str) else ""
    if not email or not MAU_EMAIL.fullmatch(email):
        return 422, {"detail": "Trường 'email' không hợp lệ"}

    ho_so = payload.get("ho_so")
    if not isinstance(ho_so, dict) or not str(ho_so.get("ho_ten") or "").strip():
        return 422, {"detail": "Trường 'ho_so' không hợp lệ"}

    sku = str(payload.get("sku") or "").strip()
    if not sku:
        return 422, {"detail": "Trường 'sku' không hợp lệ"}

    kenh = str(payload.get("kenh") or "").strip()
    if not kenh:
        return 422, {"detail": "Trường 'kenh' không hợp lệ"}

    sp = (danh_muc or {}).get(sku) if isinstance(danh_muc, dict) else None
    if not isinstance(sp, dict) or kenh not in (sp.get("kenh") or []):
        return 404, {
            "detail": f"Không tìm thấy sản phẩm '{sku}' trên kênh '{kenh}'"
        }

    gia_goc = int(sp["gia"])
    tong = gia_goc

    ds_don = kho.setdefault("don", [])
    da_co_ck = {str(d.get("noi_dung_ck") or "").upper() for d in ds_don if isinstance(d, dict)}
    da_co_id = {str(d.get("order_id") or "") for d in ds_don if isinstance(d, dict)}

    noi_dung_ck = _sinh_noi_dung_ck(da_co_ck)
    order_id = _sinh_order_id(da_co_id)

    luc_tao = datetime.now(timezone.utc).replace(microsecond=0)
    luc_het_han = luc_tao + timedelta(hours=2)
    created_at = luc_tao.isoformat()
    expires_at = luc_het_han.isoformat()

    ngan_hang = "MB"
    so_tk = "0000000000"
    qr_url = (
        f"https://api.example.vn/v1/pay/vietqr.png"
        f"?acc={so_tk}&bank={ngan_hang}&amount={tong}&des={noi_dung_ck}"
    )

    don_luu = {
        "order_id": order_id,
        "sku": sku,
        "ten_san_pham": str(sp.get("ten") or ""),
        "kenh": kenh,
        "gia_goc": gia_goc,
        "tong": tong,
        "da_nhan": 0,
        "trang_thai": "cho_thanh_toan",
        "noi_dung_ck": noi_dung_ck,
        "email": email,
        "ho_so": copy.deepcopy(ho_so),
        "dong_y_dieu_khoan": True,
        "dong_y_nhan_tin": bool(payload.get("dong_y_nhan_tin", False)),
        "created_at": created_at,
        "expires_at": expires_at,
    }
    ds_don.append(don_luu)

    than = {
        "order_id": order_id,
        "sku": sku,
        "ten_san_pham": str(sp.get("ten") or ""),
        "kenh": kenh,
        "gia_goc": gia_goc,
        "ma_giam": None,
        "so_tien_giam": 0,
        "tong": tong,
        "trang_thai": "cho_thanh_toan",
        "la_qua": False,
        "items": [],
        "reports": [],
        "so_mon": 1,
        "ma_combo": None,
        "giam_combo": 0,
        "tuy_chon_them": None,
        "phi_tuy_chon_them": 0,
        "utm": None,
        "ma_doi_tac": None,
        "gia_lap": False,
        "qr": {
            "noi_dung_ck": noi_dung_ck,
            "so_tien": tong,
            "ngan_hang": ngan_hang,
            "so_tk": so_tk,
            "url": qr_url,
        },
        "created_at": created_at,
        "expires_at": expires_at,
        "la_thue_bao": False,
        "he_nha": None,
    }
    return 200, than


def trich_ma_cts(noi_dung: str | None) -> str | None:
    """Trích mã chuyển khoản dạng CTS + 10 ký tự hex (không phân biệt hoa thường)."""
    m = MAU_MA_CTS.search(str(noi_dung or ""))
    return m.group(1).upper() if m else None


def tim_don_theo_ma(ds_don: list[dict], ma_ck: str | None) -> dict | None:
    """Tìm đơn trong `ds_don` theo `noi_dung_ck`."""
    if not ma_ck or not isinstance(ds_don, list):
        return None
    ma_hoa = ma_ck.upper()
    for d in ds_don:
        if isinstance(d, dict) and str(d.get("noi_dung_ck") or "").upper() == ma_hoa:
            return d
    return None


def ap_thanh_toan_cts(don: dict, so_tien_nhan: int) -> int:
    """Áp dụng khoản tiền nhận vào `don` theo đúng luật `apply_webhook_payment_to_order` của CTS.

    Trả về `chenh_lech`.
    """
    cu = str(don.get("trang_thai") or "cho_thanh_toan")
    don["da_nhan"] = int(don.get("da_nhan") or 0) + int(so_tien_nhan)
    tong = int(don.get("tong") or 0)

    if cu in ("het_han", "da_huy", "can_hoan_tien"):
        don["trang_thai"] = "can_hoan_tien"
        return int(don["da_nhan"])

    if don["da_nhan"] >= tong:
        if cu in ("cho_thanh_toan", "thieu_tien"):
            don["trang_thai"] = "da_thanh_toan"
    elif cu in ("cho_thanh_toan", "thieu_tien"):
        don["trang_thai"] = "thieu_tien"

    return max(0, int(don["da_nhan"]) - tong)


def nhan_webhook(
    payload: dict,
    kho: dict,
    authorization: str | None,
    khoa: str,
) -> tuple[int, dict]:
    """Xử lý webhook SePay theo hợp đồng POST /v1/pay/sepay/webhook của CTS."""
    if not xac_thuc_apikey(authorization, khoa):
        return 401, {"detail": "Sai hoặc thiếu khoá xác thực webhook"}

    if not isinstance(payload, dict):
        return 422, {"detail": "Payload webhook không hợp lệ"}

    raw_id = payload.get("id")
    tx_id = "" if (raw_id is None or isinstance(raw_id, bool)) else str(raw_id).strip()
    if not tx_id:
        return 422, {"detail": "Thiếu mã giao dịch 'id' trong webhook"}

    ds_don = kho.setdefault("don", [])
    ds_tx = kho.setdefault("tx", [])

    ma_ck = trich_ma_cts(payload.get("content"))
    don = tim_don_theo_ma(ds_don, ma_ck)

    if any(str(x) == tx_id for x in ds_tx):
        return 200, {
            "ok": True,
            "idempotent": True,
            "tx_id": tx_id,
            "order_id": don.get("order_id") if don else None,
        }

    loai_gd = payload.get("transferType", "in")
    if loai_gd != "in":
        return 200, {
            "ok": True,
            "status": "ignored",
            "tx_id": tx_id,
        }

    if not ma_ck or don is None:
        return 200, {
            "ok": True,
            "status": "unmatched",
            "tx_id": tx_id,
            "noi_dung_ck": ma_ck,
        }

    try:
        so_tien = int(payload.get("transferAmount") or 0)
    except (TypeError, ValueError):
        return 422, {"detail": "Trường 'transferAmount' không hợp lệ"}

    ds_tx.append(tx_id)
    chenh_lech = ap_thanh_toan_cts(don, so_tien)

    return 200, {
        "ok": True,
        "status": "matched",
        "tx_id": tx_id,
        "order_id": don.get("order_id"),
        "trang_thai": don.get("trang_thai"),
        "da_nhan": don.get("da_nhan"),
        "chenh_lech": chenh_lech,
    }
