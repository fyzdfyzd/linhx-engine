"""Đối soát webhook SePay, chống trùng tx_id và chuyển đơn sang trạng thái da_tra.

Chuyển từ: nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py
(PaymentFlowModule.handle_sepay_webhook: xác thực header Apikey, bỏ qua giao dịch tiền ra,
chống trùng tx_id, khớp nội dung chuyển khoản với mã đơn và đối soát số tiền).
"""
from __future__ import annotations

import hmac
import re

NGUON_PROTO = "nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py"


def chuan_noi_dung(chuoi: str | None) -> str:
    """Chuẩn hoá nội dung chuyển khoản: chữ hoa, bỏ khoảng trắng và dấu gạch."""
    return re.sub(r"[\s\-_]+", "", str(chuoi or "").upper())


def xac_thuc_khoa(authorization: str | None, khoa: str | None) -> bool:
    """Kiểm tra header Authorization có đúng dạng 'Apikey <khoa>' hay không."""
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


def _so_tien_hop_le(gia_tri) -> float | None:
    if gia_tri is None or isinstance(gia_tri, bool):
        return None
    try:
        return float(gia_tri)
    except (TypeError, ValueError):
        return None


def _khop_ranh_gioi_ma(ma_ck: str, chuoi_hoa: str) -> bool:
    """Kiểm tra `ma_ck` xuất hiện theo ranh giới token trong `chuoi_hoa` (cho phép cách/gạch giữa các ký tự)."""
    if not ma_ck or not chuoi_hoa:
        return False
    mau = r"(?<![A-Z0-9])" + r"[\s\-_]*".join(re.escape(ky_tu) for ky_tu in ma_ck) + r"(?![A-Z0-9])"
    return re.search(mau, chuoi_hoa) is not None


def tim_cac_don_khop(ds_don: list[dict], noi_dung: str | None) -> list[dict]:
    """Trả danh sách đơn khớp `noi_dung_ck` có độ dài mã lớn nhất (nhiều hơn 1 là mơ hồ)."""
    chuoi_hoa = str(noi_dung or "").upper()
    if not chuan_noi_dung(chuoi_hoa) or not isinstance(ds_don, list):
        return []

    ung_vien: list[tuple[int, dict]] = []
    for don in ds_don:
        if not isinstance(don, dict):
            continue
        ma_ck = chuan_noi_dung(don.get("noi_dung_ck"))
        if ma_ck and _khop_ranh_gioi_ma(ma_ck, chuoi_hoa):
            ung_vien.append((len(ma_ck), don))

    if not ung_vien:
        return []
    ung_vien.sort(key=lambda item: item[0], reverse=True)
    do_dai_max = ung_vien[0][0]
    return [don for do_dai, don in ung_vien if do_dai == do_dai_max]


def tim_don_khop(ds_don: list[dict], noi_dung: str | None) -> dict | None:
    """Tìm đơn duy nhất khớp `noi_dung_ck` trong `noi_dung` (nếu mơ hồ nhiều đơn cùng độ dài thì trả None)."""
    ket_qua = tim_cac_don_khop(ds_don, noi_dung)
    if len(ket_qua) != 1:
        return None
    return ket_qua[0]


def xu_ly(
    payload: dict,
    kho: dict,
    authorization: str | None,
    khoa: str,
) -> tuple[int, dict]:
    """Xử lý payload webhook SePay trên bộ nhớ `kho` (`{"don": [...], "tx": [...], "lech": [...]}`).

    - `Authorization` khác `"Apikey <khoa>"` -> `(401, ...)` và không thay đổi `kho`.
    - Thiếu hoặc rỗng `id` (`tx_id`) -> `(400, ...)` trước khi đối soát.
    - `tx_id = str(payload["id"])` đã có trong `kho["tx"]` -> `(200, {"success": True, "trung": True})`.
    - Mọi giao dịch hợp lệ (có `id`, đúng khoá) được ghi vào `kho["tx"]` đúng một lần.
    - `transferType` khác `"in"` -> `(200, {"success": True, "bo_qua": True})`, không đổi đơn.
    - Không tìm thấy đơn khớp hoặc khớp mơ hồ nhiều đơn -> ghi `kho["lech"]`, trả `(200, {"success": True, "khop": False})`.
    - Sai số tiền -> giữ nguyên trạng thái đơn, ghi `kho["lech"]`.
    - Đơn không ở trạng thái `cho_tra` (`da_tra` hoặc `huy`) -> ghi `kho["lech"]`, không đổi trạng thái.
    - Đúng số tiền và đơn đang `cho_tra` -> chuyển `trang_thai` đơn sang `"da_tra"`, gán `tx_id` vào đơn.
    """
    if not xac_thuc_khoa(authorization, khoa):
        return 401, {"success": False, "error": "unauthorized"}

    if not isinstance(payload, dict) or not isinstance(kho, dict):
        return 400, {"success": False, "error": "invalid_payload"}

    raw_id = payload.get("id")
    tx_id = "" if (raw_id is None or isinstance(raw_id, bool)) else str(raw_id).strip()
    if not tx_id:
        return 400, {"success": False, "error": "missing_tx_id"}

    ds_tx = kho.setdefault("tx", [])
    if any(str(x) == tx_id for x in ds_tx):
        return 200, {"success": True, "trung": True, "tx_id": tx_id}

    ds_tx.append(tx_id)

    if payload.get("transferType") != "in":
        return 200, {"success": True, "bo_qua": True, "tx_id": tx_id}

    noi_dung_gop = f"{payload.get('content') or ''} {payload.get('code') or ''}".strip()
    ds_khop = tim_cac_don_khop(kho.get("don", []), noi_dung_gop)
    if not ds_khop:
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ly_do": "khong_tim_thay_don",
                "so_tien": payload.get("transferAmount"),
                "noi_dung": str(payload.get("content") or ""),
            }
        )
        return 200, {"success": True, "khop": False, "tx_id": tx_id}

    if len(ds_khop) > 1:
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ly_do": "nhieu_don_khop_mo_ho",
                "ds_ma_don": [d.get("ma") or d.get("name") for d in ds_khop],
                "so_tien": payload.get("transferAmount"),
                "noi_dung": str(payload.get("content") or ""),
            }
        )
        return 200, {"success": True, "khop": False, "mo_ho": True, "tx_id": tx_id}

    don = ds_khop[0]
    tien_nhan = _so_tien_hop_le(payload.get("transferAmount"))
    tien_don = _so_tien_hop_le(don.get("so_tien"))
    ma_don = don.get("ma") or don.get("name")

    if (
        tien_nhan is None
        or tien_don is None
        or tien_nhan <= 0
        or round(tien_nhan, 2) != round(tien_don, 2)
    ):
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ma_don": ma_don,
                "ly_do": "sai_so_tien",
                "so_tien_don": don.get("so_tien"),
                "so_tien_nhan": payload.get("transferAmount"),
            }
        )
        return 200, {
            "success": True,
            "khop": True,
            "sai_so_tien": True,
            "ma_don": ma_don,
            "tx_id": tx_id,
        }

    trang_thai = don.get("trang_thai")
    if trang_thai == "da_tra":
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ma_don": ma_don,
                "ly_do": "don_da_tra_truoc_do",
                "so_tien_nhan": payload.get("transferAmount"),
            }
        )
        return 200, {
            "success": True,
            "khop": True,
            "da_tra_truoc": True,
            "ma_don": ma_don,
            "tx_id": tx_id,
        }

    if trang_thai == "huy":
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ma_don": ma_don,
                "ly_do": "don_da_huy",
                "so_tien_nhan": payload.get("transferAmount"),
            }
        )
        return 200, {
            "success": True,
            "khop": True,
            "don_da_huy": True,
            "ma_don": ma_don,
            "tx_id": tx_id,
        }

    if trang_thai != "cho_tra":
        kho.setdefault("lech", []).append(
            {
                "tx_id": tx_id,
                "ma_don": ma_don,
                "ly_do": "trang_thai_khong_hop_le",
                "trang_thai": trang_thai,
                "so_tien_nhan": payload.get("transferAmount"),
            }
        )
        return 200, {
            "success": True,
            "khop": True,
            "trang_thai_khong_hop_le": True,
            "ma_don": ma_don,
            "tx_id": tx_id,
        }

    don["trang_thai"] = "da_tra"
    don["tx_id"] = tx_id
    return 200, {
        "success": True,
        "khop": True,
        "ma_don": ma_don,
        "tx_id": tx_id,
    }
