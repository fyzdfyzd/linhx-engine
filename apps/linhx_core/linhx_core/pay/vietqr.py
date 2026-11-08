"""Sinh nội dung chuyển khoản, URL mã VietQR và tạo đơn (LX Don).

Chuyển từ: nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py
(PaymentFlowModule.create_order và PaymentFlowModule._vietqr_url: sinh mã nội dung đối soát,
tạo URL ảnh QR theo số tiền + nội dung đơn hàng, khởi tạo đơn chờ thanh toán).
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlencode

from linhx_core.pay.quyen_dung import gia_hop_le

NGUON_PROTO = "nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py"


def noi_dung_ck(ma_don: str) -> str:
    """Sinh nội dung chuyển khoản chuẩn VietQR từ `ma_don`.

    Chỉ gồm chữ hoa và số (không dấu cách), dài 6..25 ký tự, luôn ghép tiền tố `"LX"`
    vào đầu phần mã đã làm sạch (không cắt `"LX"` có sẵn trong `ma_don`, nên mã `"LX5"`
    thành `"LXLX5..."` để tránh va chạm với mã `"5"`). Khi `ma_don` có ký tự bị lược bỏ
    hoặc dài hơn 23 ký tự, giữ tối đa 15 ký tự đầu và nối 8 ký tự hex SHA-256 của `ma_don`
    gốc để hai mã đơn khác nhau luôn cho hai nội dung khác nhau.
    """
    raw = str(ma_don or "").strip()
    if not raw:
        raise ValueError("ma_don không được để trống")
    sach = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if not sach:
        raise ValueError("ma_don phải chứa ít nhất một chữ cái hoặc chữ số")
    than = sach

    bam_phu = hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
    if raw != sach:
        than = f"{than[:15]}{bam_phu[:8]}"
    elif len(than) < 4:
        than = f"{than}{bam_phu[:8]}"
    elif len(than) > 23:
        than = f"{than[:15]}{bam_phu[:8]}"

    return f"LX{than}"


def qr_url(so_tien: int, noi_dung: str, ngan_hang: dict) -> str:
    """Sinh URL ảnh VietQR `https://img.vietqr.io/image/<bin>-<so_tk>-<mẫu>.png?...`.

    `ngan_hang` gồm `{"bin", "so_tk", "ten_tk"}` lấy từ cấu hình site.
    Ném `ValueError` khi `so_tien <= 0` hoặc không phải số nguyên.
    """
    if isinstance(so_tien, bool) or not isinstance(so_tien, int) or so_tien <= 0:
        raise ValueError("so_tien phải là số nguyên dương")
    if not isinstance(ngan_hang, dict):
        raise ValueError("ngan_hang phải là dict cấu hình ngân hàng")
    ma_bin = str(ngan_hang.get("bin") or "").strip()
    so_tk = str(ngan_hang.get("so_tk") or "").strip()
    ten_tk = str(ngan_hang.get("ten_tk") or "").strip()
    mau = str(ngan_hang.get("mau") or "compact2").strip()
    if not ma_bin or not so_tk:
        raise ValueError("Thiếu thông tin bin hoặc so_tk trong cấu hình ngân hàng")
    nd = str(noi_dung or "").strip()
    if not nd:
        raise ValueError("noi_dung không được để trống")

    tham_so = urlencode(
        {
            "amount": str(so_tien),
            "addInfo": nd,
            "accountName": ten_tk,
        }
    )
    return f"https://img.vietqr.io/image/{ma_bin}-{so_tk}-{mau}.png?{tham_so}"


def tao_don(goi: dict, nguoi: str, ngan_hang: dict, ma_don: str) -> dict:
    """Tạo dict đơn hàng (`LX Don`) ở trạng thái `cho_tra` kèm `noi_dung_ck` và `qr_url`.

    Số tiền lấy từ `goi["gia"]` nếu có, không thì `goi["gia_san"]`.
    Kiểm tra bằng `quyen_dung.gia_hop_le`; nếu dưới `gia_san` hoặc không hợp lệ thì ném `ValueError`.
    """
    if not isinstance(goi, dict):
        raise ValueError("goi phải là dict")
    raw_tien = goi.get("gia") if goi.get("gia") is not None else goi.get("gia_san")
    if raw_tien is None or isinstance(raw_tien, bool):
        raise ValueError("Gói thiếu thông tin giá")
    if isinstance(raw_tien, float) and not raw_tien.is_integer():
        raise ValueError("Số tiền đơn phải là số nguyên")
    try:
        so_tien = int(raw_tien)
    except (TypeError, ValueError) as exc:
        raise ValueError("Số tiền đơn không hợp lệ") from exc

    if so_tien <= 0 or not gia_hop_le(so_tien, goi):
        raise ValueError("Số tiền đơn dưới giá sàn của gói")

    nd = noi_dung_ck(ma_don)
    url = qr_url(so_tien, nd, ngan_hang)
    return {
        "ma": ma_don,
        "goi": goi.get("ma") or goi.get("name"),
        "nguoi": nguoi,
        "so_tien": so_tien,
        "trang_thai": "cho_tra",
        "noi_dung_ck": nd,
        "qr_url": url,
    }
