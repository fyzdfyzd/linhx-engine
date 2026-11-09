"""Kiểm thử đơn vị và bảo mật (K4) cho `linhx_core.id.otp` (I3)."""
from __future__ import annotations

import json

import pytest

from linhx_core.id import otp


def test_sinh_ma_ngau_nhien_6_chu_so_va_tach_biet_muc_dich():
    kho: dict = {}
    da_gui: list[tuple[str, str, str]] = []

    kq_dn = otp.phat_ma(
        kho,
        "  Khach.Hang@VD.vn ",
        "dang_nhap",
        "2026-11-09 10:00:00",
        gui_mail=lambda em, ma, md: da_gui.append((em, ma, md)),
    )
    assert kq_dn == {
        "email": "khach.hang@vd.vn",
        "muc_dich": "dang_nhap",
        "het_han_luc": "2026-11-09 10:10:00",
    }
    assert len(da_gui) == 1
    em_gui, ma_sinh, md_gui = da_gui[0]
    assert em_gui == "khach.hang@vd.vn"
    assert md_gui == "dang_nhap"
    assert len(ma_sinh) == 6 and ma_sinh.isdigit()
    assert ma_sinh not in json.dumps(kho)

    # Mã của mục đích "dang_nhap" không dùng được cho mục đích "marketing"
    kq_sai_md = otp.xac_minh(kho, "khach.hang@vd.vn", "marketing", ma_sinh, "2026-11-09 10:01:00")
    assert kq_sai_md == {"ok": False, "ly_do": "sai_ma"}

    # Xác minh đúng mục đích "dang_nhap" (email khác hoa thường) -> thành công
    kq_dung = otp.xac_minh(kho, "KHACH.HANG@VD.VN", "dang_nhap", ma_sinh, "2026-11-09 10:01:00")
    assert kq_dung == {"ok": True, "ly_do": None}


def test_bam_ma_hmac_va_tu_choi_ky_tu_phan_cach_hoac_muc_dich_la():
    b1 = otp.bam_ma("Lan@VD.vn", "dang_nhap", "123456")
    b2 = otp.bam_ma("lan@vd.vn", "marketing", "123456")
    assert b1 != b2
    assert len(b1) == 64
    assert "123456" not in b1
    assert otp.bam_ma("LAN@VD.VN", "dang_nhap", "482910") == otp.bam_ma("lan@vd.vn", "dang_nhap", "482910")

    with pytest.raises(ValueError):
        otp.bam_ma("u|x@vd.vn", "dang_nhap", "123456")
    with pytest.raises(ValueError):
        otp.bam_ma("u@vd.vn", "muc_dich_ngoai_danh_sach", "123456")


def test_giu_nguyen_so_lan_sai_va_gioi_han_tan_suat_phat_ma():
    kho: dict = {}
    otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="111111", ip="203.0.113.10")

    # Chờ dưới 60 giây phát lại -> bị từ chối
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:00:30", ma_otp="222222", ip="203.0.113.10")

    # Đoán sai 4 lần rồi xin phát mã mới sau 2 phút -> bộ đếm sai vẫn giữ nguyên 4
    for phut in range(1, 5):
        kq = otp.xac_minh(kho, "an@vd.vn", "dang_nhap", "000000", f"2026-11-09 10:0{phut}:00")
        assert kq == {"ok": False, "ly_do": "sai_ma"}

    otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:06:00", ma_otp="333333", ip="203.0.113.10")
    # Sai thêm 1 lần nữa (tổng 5 lần) -> khoá kênh ngay lập tức
    kq_khoa = otp.xac_minh(kho, "an@vd.vn", "dang_nhap", "000000", "2026-11-09 10:06:10")
    assert kq_khoa == {"ok": False, "ly_do": "bi_khoa"}


def test_kiem_tra_dau_vao_va_chong_lui_thoi_gian():
    kho: dict = {}
    with pytest.raises(ValueError):
        otp.phat_ma(None, "a@vd.vn", "dang_nhap", "2026-11-09 10:00:00")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "khong-phai-email", "dang_nhap", "2026-11-09 10:00:00")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "   ", "2026-11-09 10:00:00")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "dang_nhap", "khong-phai-ngay")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="   ")

    otp.phat_ma(kho, "b@vd.vn", "dang_nhap", "2026-11-09 10:05:00", ma_otp="123456")
    # Lùi giờ về trước lúc phát mã -> từ chối
    kq_lui = otp.xac_minh(kho, "b@vd.vn", "dang_nhap", "123456", "2026-11-09 10:00:00")
    assert kq_lui["ok"] is False
