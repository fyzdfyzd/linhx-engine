"""O5: Bàn /#/engine: hàng phiếu chờ duyệt, nút duyệt / trả lại có lý do, dùng được ở 390px.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/ops/ban_phieu.py thuần Python (không import frappe ở đầu file):
    ds_phieu_cho(ds_phieu: list[dict]) -> list[dict]
        chỉ lấy phiếu có trang_thai == "nhap", xếp mới nhất trước
    duyet_phieu(ds_phieu: list[dict], ma_phieu: str, vai_tro: list[str]) -> dict
        chuyển phiếu ma_phieu từ "nhap" sang "duyet" (chỉ vai điều hành System Manager / LX Operator,
        thiếu quyền -> PermissionError)
    tra_phieu(ds_phieu: list[dict], ma_phieu: str, ly_do: str, vai_tro: list[str]) -> dict
        bắt buộc ly_do.strip() không rỗng (rỗng -> ValueError), chỉ vai điều hành (thiếu -> PermissionError),
        chuyển trang_thai sang "tra" và lưu ly_do_tra = ly_do.strip() vào phiếu
- apps/linhx_core/linhx_core/ops/api_ban_phieu.py:
    @frappe.whitelist() `phieu_cho` trả danh sách phiếu nhap
    @frappe.whitelist(methods=["POST"]) `duyet` (ma_phieu) và `tra_lai` (ma_phieu, ly_do)
- front/index.html trên #/engine:
    gọi GET /api/method/linhx_core.ops.api_ban_phieu.phieu_cho và vẽ danh sách phiếu nhap vào phần tử #phieu-cho.
    Mỗi phiếu có nút [data-duyet-phieu="<name>"], ô nhập lý do [data-ly-do-tra="<name>"] và nút [data-tra-phieu="<name>"].
    Bấm trả lại khi chưa nhập lý do thì không gọi POST tra_lai; có lý do thì gửi POST {ma_phieu, ly_do} tới
    /api/method/linhx_core.ops.api_ban_phieu.tra_lai. Không tràn ngang ở 390px và 1280px.
"""
import pytest

from _chung import ma, CORE, dong_trang, khong_import_frappe_dau_file, nap_module, trang_front_engine


def _bp():
    return nap_module("linhx_core.ops.ban_phieu", CORE)


def test_phieu_cho_va_tra_lai_bat_buoc_ly_do():
    """Tiêu chí: #phieu-cho liệt kê phiếu nhap; trả lại bắt buộc lý do, lý do lưu vào phiếu."""
    bp = _bp()
    ds = [
        {"name": "PH-1", "de": "Phiếu một", "trang_thai": "nhap", "creation": "2026-11-09 08:00:00"},
        {"name": "PH-2", "de": "Phiếu hai", "trang_thai": "duyet", "creation": "2026-11-09 09:00:00"},
        {"name": "PH-3", "de": "Phiếu ba", "trang_thai": "nhap", "creation": "2026-11-09 10:00:00"},
    ]
    cho = bp.ds_phieu_cho(ds)
    assert [x["name"] for x in cho] == ["PH-3", "PH-1"]

    with pytest.raises(ValueError):
        bp.tra_phieu(ds, "PH-1", "   ", ["LX Operator"])
    with pytest.raises(PermissionError):
        bp.tra_phieu(ds, "PH-1", "Đề chưa rõ", ["Guest"])

    da_tra = bp.tra_phieu(ds, "PH-1", "Đề thiếu tiêu chí", ["LX Operator"])
    assert da_tra["trang_thai"] == "tra" and da_tra["ly_do_tra"] == "Đề thiếu tiêu chí"
    assert ds[0]["trang_thai"] == "tra" and ds[0]["ly_do_tra"] == "Đề thiếu tiêu chí"

    da_duyet = bp.duyet_phieu(ds, "PH-3", ["LX Operator"])
    assert da_duyet["trang_thai"] == "duyet"
    khong_import_frappe_dau_file(ma("ops/ban_phieu.py"))


def test_ban_engine_phieu_cho_va_390_1280_khong_tran_ngang():
    """Tiêu chí: #phieu-cho liệt kê phiếu nhap; trả lại bắt buộc lý do; 390 và 1280 không tràn ngang."""
    from _chung import GOC
    assert "phieu-cho" in (GOC / "front" / "index.html").read_text(encoding="utf-8"), "front/index.html chưa có #phieu-cho"
    phieu_mau = [
        {"name": "PHIEU-CHO-01", "loai_phieu": "feature", "de": "Thêm bộ lọc bảng điều hành", "trang_thai": "nhap"},
    ]
    api = {
        "/api/method/linhx_core.ops.api_ban_phieu.phieu_cho": lambda pt, b: (200, {"message": phieu_mau}, None),
        "/api/method/linhx_core.ops.api_ban_phieu.duyet": lambda pt, b: (200, {"message": {"ok": True}}, None),
        "/api/method/linhx_core.ops.api_ban_phieu.tra_lai": lambda pt, b: (200, {"message": {"ok": True}}, None),
    }
    for rong in (390, 1280):
        p, b, pg, s, ghi = trang_front_engine(api, rong=rong, cho="#phieu-cho")
        try:
            pg.wait_for_function(
                "document.querySelector('#phieu-cho') && document.querySelector('#phieu-cho').innerText.includes('PHIEU-CHO-01')",
                timeout=10000,
            )
            sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
            assert sw <= rong, f"tràn ngang ở {rong}px (scrollWidth={sw})"

            if rong == 390:
                nut_tra = pg.locator('[data-tra-phieu="PHIEU-CHO-01"]')
                nut_tra.click()
                pg.wait_for_timeout(400)
                assert not [x for x in ghi if x[0] == "POST" and "tra_lai" in x[1]], "chưa nhập lý do thì không được gửi POST tra_lai"

                o_ly_do = pg.locator('[data-ly-do-tra="PHIEU-CHO-01"]')
                o_ly_do.fill("Phạm vi vùng chưa khớp")
                nut_tra.click()
                pg.wait_for_timeout(500)
                post_tra = [x for x in ghi if x[0] == "POST" and "tra_lai" in x[1]]
                assert post_tra and post_tra[-1][2].get("ly_do") == "Phạm vi vùng chưa khớp"
        finally:
            dong_trang(p, b, s)
