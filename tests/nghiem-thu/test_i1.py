"""I1: Đăng nhập Google, gộp vào LX Nguoi theo khoá gộp trùng A1.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/id/google_oauth.py thuần Python (không import frappe ở đầu file),
  dùng lại linhx_core.crm.gop_trung (A1):
    dang_nhap_google(ho_so_google: dict, state_gui: str, state_phien: str,
                     ds_nguoi: list[dict], nhat_ky_gop: list[dict], luc: str) -> dict
        - ho_so_google: {"sub": str, "email": str, "email_verified": bool, "name"?: str}
        - state_gui hoặc state_phien rỗng hoặc không khớp (so sánh hằng thời gian hmac.compare_digest)
          -> raise ValueError
        - email trống hoặc email_verified không phải True -> raise ValueError
        - gộp vào ds_nguoi theo khoá gộp trùng A1 (email chuẩn hoá chữ thường, cắt khoảng trắng):
          * nếu email đã có trong ds_nguoi (kể cả khác hoa thường): KHÔNG tạo người mới (len(ds_nguoi) giữ nguyên),
            bù trường còn trống (vd. ho_ten, google_sub), ghi 1 dòng vào nhat_ky_gop:
            {"luc": luc, "kenh": "google", "hanh_dong": "gop", "email": email_chuan, "nguoi": ...}
          * nếu chưa có: thêm người mới vào ds_nguoi, ghi 1 dòng vào nhat_ky_gop với "hanh_dong": "tao_moi"
        - trả {"ds_nguoi": list, "nguoi": dict, "nhat_ky_gop": list, "da_gop": bool}
- apps/linhx_core/linhx_core/id/api_auth.py: @frappe.whitelist(allow_guest=True) `google_callback`.
"""
import pytest

from _chung import ma, CORE, khong_import_frappe_dau_file, nap_module

LUC = "2026-11-09 10:00:00"


def _go():
    return nap_module("linhx_core.id.google_oauth", CORE)


def test_email_da_co_khac_hoa_thuong_khong_tao_nguoi_moi():
    """Tiêu chí: email đã có (khác hoa thường) thì không tạo người mới."""
    go = _go()
    ds_cu = [{"name": "NG-01", "ho_ten": "Lan Nguyễn", "email": "Lan.Nguyen@VD.vn", "dien_thoai": "0912345678"}]
    nk = []
    kq = go.dang_nhap_google(
        {"sub": "gg-1001", "email": "  lan.nguyen@vd.vn ", "email_verified": True, "name": "Lan Google"},
        state_gui="st-hop-le-123",
        state_phien="st-hop-le-123",
        ds_nguoi=ds_cu,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert len(kq["ds_nguoi"]) == 1, "email đã có (khác hoa thường) thì không được tạo người mới"
    assert kq["da_gop"] is True
    assert kq["nguoi"]["ho_ten"] == "Lan Nguyễn", "gộp trùng giữ nguyên trường đã có"
    assert kq["nguoi"]["dien_thoai"] == "0912345678"


def test_state_oauth_sai_thi_tu_choi():
    """Tiêu chí: state OAuth sai thì từ chối."""
    go = _go()
    ho_so = {"sub": "gg-1002", "email": "minh@vd.vn", "email_verified": True, "name": "Minh"}
    for st_gui, st_phien in (
        ("state-a", "state-b"),
        ("", "state-b"),
        ("state-a", ""),
        ("", ""),
    ):
        with pytest.raises(ValueError):
            go.dang_nhap_google(ho_so, st_gui, st_phien, [], [], LUC)

    # email chưa xác minh cũng từ chối
    with pytest.raises(ValueError):
        go.dang_nhap_google(
            {"sub": "gg-1003", "email": "minh@vd.vn", "email_verified": False},
            "state-ok",
            "state-ok",
            [],
            [],
            LUC,
        )


def test_ghi_nhat_ky_gop():
    """Tiêu chí: ghi nhật ký gộp."""
    go = _go()
    ds = [{"name": "NG-01", "ho_ten": "Lan", "email": "lan@vd.vn"}]
    nk = []
    kq = go.dang_nhap_google(
        {"sub": "gg-999", "email": "LAN@VD.VN", "email_verified": True, "name": "Lan"},
        state_gui="st-1",
        state_phien="st-1",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert len(kq["nhat_ky_gop"]) == 1
    dong = kq["nhat_ky_gop"][0]
    assert dong.get("kenh") == "google" and dong.get("hanh_dong") == "gop"
    assert dong.get("email") == "lan@vd.vn" and dong.get("luc") == LUC

    khong_import_frappe_dau_file(ma("id/google_oauth.py"))
    api_p = CORE / "linhx_core" / "id" / "api_auth.py"
    assert api_p.exists() and "def google_callback(" in api_p.read_text(encoding="utf-8")
