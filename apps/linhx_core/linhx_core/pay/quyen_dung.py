"""Kiểm giá sàn của Gói (LX Goi / LX Gia) và cấp Quyền dùng (LX Quyen Dung) khi đơn đã trả.

Chuyển từ: nguon/03-opc-os/modules/02_thiet_ke_goi_gia/module.py
(evaluate_pricing: tính giá gói sau chiết khấu và kiểm tra cửa giá sàn unit_economics_gate_passed)
và nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py
(handle_sepay_webhook: chỉ mở quyền nhận sản phẩm khi đơn chuyển sang paid và đủ tiền).
"""
from __future__ import annotations

NGUON_PROTO = "nguon/03-opc-os/modules/02_thiet_ke_goi_gia/module.py"


def tinh_gia_goi(goi: dict, phan_tram_giam: int = 0) -> int:
    """Tính giá cuối của gói sau phần trăm giảm (làm tròn nghìn đồng theo evaluate_pricing ở PROTO 03 m02)."""
    if not isinstance(goi, dict):
        return 0
    gia_goc = int(goi.get("gia") if goi.get("gia") is not None else goi.get("gia_san", 0))
    pct = max(0, min(100, int(phan_tram_giam or 0)))
    giam = int(round(gia_goc * pct / 100.0, -3)) if gia_goc > 0 and pct > 0 else 0
    return max(0, gia_goc - giam)


def gia_hop_le(so_tien: object, goi: dict) -> bool:
    """Trả True khi `so_tien` hợp lệ và >= `goi["gia_san"]`; False khi dưới giá sàn hoặc không hợp lệ."""
    if not isinstance(goi, dict) or so_tien is None or isinstance(so_tien, bool):
        return False
    try:
        tien = float(so_tien)
        gia_san = float(goi.get("gia_san", 0) or 0)
    except (TypeError, ValueError):
        return False
    return tien >= 0 and tien >= gia_san


def cap_quyen(don: dict, goi: dict) -> dict | None:
    """Cấp quyền dùng (`LX Quyen Dung`) khi đơn `trang_thai == "da_tra"` và `so_tien` đạt giá sàn của `goi`.

    Trả dict `{"goi", "nguoi", "don", "so_tien", "trang_thai"}` hoặc `None` nếu chưa đủ điều kiện.
    """
    if not isinstance(don, dict) or not isinstance(goi, dict):
        return None
    if don.get("trang_thai") != "da_tra":
        return None
    so_tien = don.get("so_tien")
    if not gia_hop_le(so_tien, goi):
        return None
    ma_goi_don = don.get("goi")
    ma_goi = goi.get("ma") or goi.get("name")
    if ma_goi_don and ma_goi and str(ma_goi_don) != str(ma_goi):
        return None
    return {
        "goi": ma_goi_don or ma_goi,
        "nguoi": don.get("nguoi"),
        "don": don.get("ma") or don.get("name"),
        "so_tien": so_tien,
        "trang_thai": "hieu_luc",
    }
