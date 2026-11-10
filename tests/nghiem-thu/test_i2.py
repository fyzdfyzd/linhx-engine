"""I2: Đăng nhập Zalo (OA IF Agent), gộp như I1.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/id/zalo_oauth.py thuần Python (không import frappe ở đầu file),
  dùng lại linhx_core.crm.gop_trung (A1):
    dang_nhap_zalo(ho_so_zalo: dict, state_gui: str, state_phien: str,
                   ds_nguoi: list[dict], nhat_ky_gop: list[dict], luc: str) -> dict
        - ho_so_zalo: {"zalo_id": str, "dien_thoai"?: str, "ho_ten"?: str, "oa_id"?: str}
        - state_gui hoặc state_phien rỗng hoặc không khớp (hmac.compare_digest) -> raise ValueError
        - thiếu zalo_id -> raise ValueError
        - gộp vào ds_nguoi theo khoá gộp trùng A1 (chuẩn hoá SĐT 0... / +84... / 84... về 84..., hoặc khớp zalo_id):
          * trùng SĐT hoặc trùng zalo_id -> gộp vào bản ghi cũ (không tạo mới, bù trường trống như zalo / dien_thoai),
            ghi dòng nhật ký gộp {"luc": luc, "kenh": "zalo", "hanh_dong": "gop", "zalo_id": ..., "nguoi": ...}
          * chưa có -> thêm bản ghi mới vào ds_nguoi, ghi dòng nhật ký {"hanh_dong": "tao_moi", ...}
        - trả {"ds_nguoi": list, "nguoi": dict, "nhat_ky_gop": list, "da_gop": bool}
- apps/linhx_core/linhx_core/id/api_auth.py thêm @frappe.whitelist(allow_guest=True) `zalo_callback`.
"""
import pytest

from _chung import ma, CORE, khong_import_frappe_dau_file, nap_module

LUC = "2026-11-09 10:30:00"


def _zo():
    return nap_module("linhx_core.id.zalo_oauth", CORE)


def test_sdt_da_co_0_hoac_84_thi_gop():
    """Tiêu chí: SĐT đã có (0… hoặc 84…) thì gộp."""
    zo = _zo()
    ds = [{"name": "NG-10", "ho_ten": "Hùng", "dien_thoai": "0912 345 678"}]
    kq1 = zo.dang_nhap_zalo(
        {"zalo_id": "zl_hung_1", "dien_thoai": "84912345678", "ho_ten": "Hùng Zalo"},
        state_gui="st-zl-1",
        state_phien="st-zl-1",
        ds_nguoi=ds,
        nhat_ky_gop=[],
        luc=LUC,
    )
    assert len(kq1["ds_nguoi"]) == 1 and kq1["da_gop"] is True
    assert kq1["nguoi"]["zalo"] == "zl_hung_1", "gộp theo SĐT phải bù zalo_id vào hồ sơ cũ"

    # Ngược lại: hồ sơ cũ lưu 84..., Zalo trả 0...
    ds2 = [{"name": "NG-11", "ho_ten": "Mai", "dien_thoai": "+84987654321"}]
    kq2 = zo.dang_nhap_zalo(
        {"zalo_id": "zl_mai_2", "dien_thoai": "0987654321", "ho_ten": "Mai"},
        state_gui="st-zl-2",
        state_phien="st-zl-2",
        ds_nguoi=ds2,
        nhat_ky_gop=[],
        luc=LUC,
    )
    assert len(kq2["ds_nguoi"]) == 1 and kq2["da_gop"] is True


def test_zalo_id_da_co_thi_gop():
    """Tiêu chí: zalo_id đã có thì gộp."""
    zo = _zo()
    ds = [{"name": "NG-20", "ho_ten": "Tuấn", "zalo": "zl_tuan_99"}]
    kq = zo.dang_nhap_zalo(
        {"zalo_id": "zl_tuan_99", "dien_thoai": "0909111222", "ho_ten": "Tuấn OA"},
        state_gui="st-zl-3",
        state_phien="st-zl-3",
        ds_nguoi=ds,
        nhat_ky_gop=[],
        luc=LUC,
    )
    assert len(kq["ds_nguoi"]) == 1 and kq["da_gop"] is True
    assert kq["nguoi"].get("dien_thoai"), "gộp theo zalo_id phải bù SĐT còn trống"


def test_co_nhat_ky_gop():
    """Tiêu chí: có nhật ký gộp."""
    zo = _zo()
    ds = [{"name": "NG-30", "ho_ten": "Thảo", "zalo": "zl_thao_1"}]
    nk = []
    kq = zo.dang_nhap_zalo(
        {"zalo_id": "zl_thao_1", "ho_ten": "Thảo"},
        state_gui="st-ok",
        state_phien="st-ok",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert len(kq["nhat_ky_gop"]) == 1
    dong = kq["nhat_ky_gop"][0]
    assert dong.get("kenh") == "zalo" and dong.get("hanh_dong") == "gop"
    assert dong.get("zalo_id") == "zl_thao_1" and dong.get("luc") == LUC

    with pytest.raises(ValueError):
        zo.dang_nhap_zalo({"zalo_id": "zl_thao_1"}, "st-sai", "st-ok", ds, nk, LUC)

    khong_import_frappe_dau_file(ma("id/zalo_oauth.py"))
    chu = (CORE / "linhx_core" / "id" / "api_auth.py").read_text(encoding="utf-8")
    assert "def zalo_callback(" in chu
