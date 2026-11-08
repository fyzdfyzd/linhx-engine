"""Chế độ bóng (shadow mode) cho Chiêm Tinh Số (CTS).

Nhận bản sao đơn và webhook SePay từ CTS khi cờ `bat_bong` bật (mặc định tắt),
dùng lại luật của `hop_dong` để cập nhật kho đơn bóng và đối chiếu báo lệch,
tuyệt đối không thực hiện bước bàn giao sản phẩm cho khách.
"""
from __future__ import annotations

import copy

from linhx_core.cts_adapter import hop_dong

_KHOA_BONG_NOI_BO = "_che_do_bong_noi_bo_"
_AUTH_BONG_NOI_BO = f"Apikey {_KHOA_BONG_NOI_BO}"


def bat(cau_hinh: dict | None) -> bool:
    """Trả về True chỉ khi `cau_hinh["bat_bong"]` có kiểu bool và bằng True (mặc định tắt)."""
    return isinstance(cau_hinh, dict) and cau_hinh.get("bat_bong") is True


def nhan_don_bong(
    don_cts: dict,
    cau_hinh: dict | None,
    kho_bong: dict,
) -> dict | None:
    """Ghi bản sao đơn bóng từ CTS vào `kho_bong` với `da_nhan = 0`.

    Khi cờ `bat_bong` tắt, trả `None` và không thay đổi `kho_bong`.
    """
    if not bat(cau_hinh):
        return None
    if not isinstance(don_cts, dict) or not isinstance(kho_bong, dict):
        return None

    noi_dung_ck = str(don_cts.get("noi_dung_ck") or "").strip().upper()
    if not noi_dung_ck:
        return None

    ds_don = kho_bong.setdefault("don", [])
    kho_bong.setdefault("tx", [])

    don_bong = copy.deepcopy(don_cts)
    don_bong["order_id"] = str(don_cts.get("order_id") or "")
    don_bong["noi_dung_ck"] = noi_dung_ck
    don_bong["tong"] = int(don_cts.get("tong") or 0)
    don_bong["da_nhan"] = 0
    don_bong["trang_thai"] = str(don_cts.get("trang_thai") or "cho_thanh_toan")

    da_co = hop_dong.tim_don_theo_ma(ds_don, noi_dung_ck)
    if da_co is None:
        ds_don.append(don_bong)
        return don_bong
    return da_co


def nhan_bong(
    webhook: dict,
    cau_hinh: dict | None,
    kho_bong: dict,
) -> dict | None:
    """Nhận bản sao webhook SePay từ CTS và áp dụng luật `hop_dong.nhan_webhook` lên `kho_bong`.

    Khi cờ `bat_bong` tắt, trả `None` và không thay đổi `kho_bong`.
    Khi cờ bật, luôn trả kèm `"giao": False`.
    """
    if not bat(cau_hinh):
        return None
    if not isinstance(webhook, dict) or not isinstance(kho_bong, dict):
        return None

    ma_http, than = hop_dong.nhan_webhook(
        webhook,
        kho_bong,
        _AUTH_BONG_NOI_BO,
        _KHOA_BONG_NOI_BO,
    )
    if ma_http != 200:
        return None

    ma_ck = hop_dong.trich_ma_cts(webhook.get("content"))
    don = hop_dong.tim_don_theo_ma(kho_bong.get("don", []), ma_ck)
    return {
        "tx_id": than.get("tx_id"),
        "noi_dung_ck": ma_ck,
        "trang_thai": don.get("trang_thai") if isinstance(don, dict) else than.get("trang_thai"),
        "da_nhan": don.get("da_nhan") if isinstance(don, dict) else than.get("da_nhan"),
        "giao": False,
    }


def so_lech(don_cts: list[dict], kho_bong: dict) -> list[dict]:
    """Đối chiếu danh sách `don_cts` với `kho_bong` theo `noi_dung_ck` trên `da_nhan`, `trang_thai`.

    Mỗi chỗ lệch trả về `{"noi_dung_ck", "truong", "cts", "bong"}`.
    Đơn chỉ có ở một bên có `"truong": "thieu_don"`.
    """
    ds_cts = don_cts if isinstance(don_cts, list) else []
    ds_bong = (
        kho_bong.get("don", [])
        if isinstance(kho_bong, dict) and isinstance(kho_bong.get("don"), list)
        else []
    )

    cts_theo_ma: dict[str, dict] = {}
    thu_tu_ma: list[str] = []
    for d in ds_cts:
        if not isinstance(d, dict):
            continue
        ma = str(d.get("noi_dung_ck") or "").strip().upper()
        if not ma:
            continue
        if ma not in cts_theo_ma:
            thu_tu_ma.append(ma)
        cts_theo_ma[ma] = d

    bong_theo_ma: dict[str, dict] = {}
    for d in ds_bong:
        if not isinstance(d, dict):
            continue
        ma = str(d.get("noi_dung_ck") or "").strip().upper()
        if not ma:
            continue
        if ma not in cts_theo_ma and ma not in bong_theo_ma:
            thu_tu_ma.append(ma)
        bong_theo_ma[ma] = d

    ket_qua: list[dict] = []
    for ma in thu_tu_ma:
        d_cts = cts_theo_ma.get(ma)
        d_bong = bong_theo_ma.get(ma)
        if d_cts is None or d_bong is None:
            ket_qua.append(
                {
                    "noi_dung_ck": ma,
                    "truong": "thieu_don",
                    "cts": d_cts.get("order_id") if isinstance(d_cts, dict) else None,
                    "bong": d_bong.get("order_id") if isinstance(d_bong, dict) else None,
                }
            )
            continue

        for truong in ("da_nhan", "trang_thai"):
            gt_cts = d_cts.get(truong)
            gt_bong = d_bong.get(truong)
            if gt_cts != gt_bong:
                ket_qua.append(
                    {
                        "noi_dung_ck": ma,
                        "truong": truong,
                        "cts": gt_cts,
                        "bong": gt_bong,
                    }
                )

    return ket_qua
