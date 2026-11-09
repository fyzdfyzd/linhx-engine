"""I3: OTP email dùng chung (C2B dùng lại).

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/id/otp.py thuần Python (không import frappe ở đầu file):
    HAN_PHUT = 10
    SAI_TOI_DA = 5
    KHOA_PHUT = 15
    bam_ma(email: str, muc_dich: str, ma_otp: str) -> str
        băm SHA-256 hex của (email chuẩn hoá chữ thường, muc_dich, ma_otp); không bao giờ trả mã trần
    phat_ma(kho: dict, email: str, muc_dich: str, luc: str,
            ma_otp: str | None = None, gui_mail: callable | None = None) -> dict
        - nếu kênh (email, muc_dich) đang bị khoá tại thời điểm luc (luc < khoa_den) -> raise ValueError
        - sinh mã 6 chữ số (hoặc dùng ma_otp truyền vào khi kiểm thử)
        - chỉ lưu bản băm ma_bam = bam_ma(...) vào kho (tuyệt đối không lưu chuỗi ma_otp trần trong kho),
          kèm tao_luc = luc, het_han_luc = luc + 10 phút, so_lan_sai = 0, da_dung = False, khoa_den = None
        - nếu có gui_mail thì gọi gui_mail(email_chuan, ma_otp, muc_dich)
        - trả {"email": email_chuan, "muc_dich": muc_dich, "het_han_luc": str}
    xac_minh(kho: dict, email: str, muc_dich: str, ma_nhap: str, luc: str) -> dict
        Trả {"ok": bool, "ly_do": str | None}:
        - đang trong thời gian khoá (luc < khoa_den) -> {"ok": False, "ly_do": "bi_khoa"} (kể cả nhập đúng mã)
        - mã đã dùng (da_dung == True) -> {"ok": False, "ly_do": "da_dung"}
        - quá 10 phút (luc > het_han_luc) -> {"ok": False, "ly_do": "het_han"}
        - băm không khớp: tăng so_lan_sai += 1; nếu so_lan_sai >= 5 thì đặt khoa_den = luc + 15 phút và
          trả {"ok": False, "ly_do": "bi_khoa"}; chưa tới 5 lần trả {"ok": False, "ly_do": "sai_ma"}
        - băm khớp, còn hạn, chưa dùng, không khoá: đặt da_dung = True, trả {"ok": True, "ly_do": None}.
"""
import json

import pytest

from _chung import CORE, khong_import_frappe_dau_file, nap_module


def _otp():
    return nap_module("linhx_core.id.otp", CORE)


def test_ma_het_han_sau_10_phut():
    """Tiêu chí: mã hết hạn sau 10 phút."""
    otp = _otp()
    kho = {}
    otp.phat_ma(kho, "Lan@VD.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="482910")

    # Quá 10 phút (10 phút 1 giây): từ chối vì hết hạn
    kq_tre = otp.xac_minh(kho, "lan@vd.vn", "dang_nhap", "482910", "2026-11-09 10:10:01")
    assert kq_tre["ok"] is False and kq_tre["ly_do"] == "het_han"

    # Phát lại mã mới, xác minh đúng ở phút thứ 10: thành công
    otp.phat_ma(kho, "lan@vd.vn", "dang_nhap", "2026-11-09 10:20:00", ma_otp="593021")
    kq_kip = otp.xac_minh(kho, "lan@vd.vn", "dang_nhap", "593021", "2026-11-09 10:30:00")
    assert kq_kip["ok"] is True


def test_sai_5_lan_thi_khoa_15_phut():
    """Tiêu chí: sai 5 lần thì khoá 15 phút."""
    otp = _otp()
    kho = {}
    otp.phat_ma(kho, "minh@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="738291")

    for lan in range(1, 5):
        kq = otp.xac_minh(kho, "minh@vd.vn", "dang_nhap", "000000", f"2026-11-09 10:0{lan}:00")
        assert kq["ok"] is False and kq["ly_do"] == "sai_ma"

    # Lần sai thứ 5 lúc 10:05:00 -> khoá 15 phút (đến 10:20:00)
    kq5 = otp.xac_minh(kho, "minh@vd.vn", "dang_nhap", "000000", "2026-11-09 10:05:00")
    assert kq5["ok"] is False and kq5["ly_do"] == "bi_khoa"

    # Lúc 10:08:00 (đang bị khoá): nhập đúng mã hay xin phát mã mới đều bị chặn
    kq_dang_khoa = otp.xac_minh(kho, "minh@vd.vn", "dang_nhap", "738291", "2026-11-09 10:08:00")
    assert kq_dang_khoa["ok"] is False and kq_dang_khoa["ly_do"] == "bi_khoa"
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "minh@vd.vn", "dang_nhap", "2026-11-09 10:19:59", ma_otp="112233")

    # Sau 15 phút (10:20:01): hết khoá, phát mã mới và xác minh được
    otp.phat_ma(kho, "minh@vd.vn", "dang_nhap", "2026-11-09 10:20:01", ma_otp="884422")
    assert otp.xac_minh(kho, "minh@vd.vn", "dang_nhap", "884422", "2026-11-09 10:21:00")["ok"] is True


def test_chi_luu_bam_ma():
    """Tiêu chí: chỉ lưu băm mã."""
    otp = _otp()
    kho = {}
    da_gui = []
    otp.phat_ma(
        kho,
        "thao@vd.vn",
        "marketing",
        "2026-11-09 10:00:00",
        ma_otp="918273",
        gui_mail=lambda em, ma, md: da_gui.append((em, ma, md)),
    )
    assert da_gui == [("thao@vd.vn", "918273", "marketing")]
    chu_kho = json.dumps(kho)
    assert "918273" not in chu_kho, "tuyệt đối không được lưu mã OTP trần trong kho"
    assert otp.bam_ma("thao@vd.vn", "marketing", "918273") in chu_kho


def test_ma_dung_mot_lan():
    """Tiêu chí: mã dùng một lần."""
    otp = _otp()
    kho = {}
    otp.phat_ma(kho, "hung@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="654321")
    lan1 = otp.xac_minh(kho, "hung@vd.vn", "dang_nhap", "654321", "2026-11-09 10:01:00")
    lan2 = otp.xac_minh(kho, "hung@vd.vn", "dang_nhap", "654321", "2026-11-09 10:01:05")
    assert lan1["ok"] is True
    assert lan2["ok"] is False and lan2["ly_do"] == "da_dung"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "id" / "otp.py")
