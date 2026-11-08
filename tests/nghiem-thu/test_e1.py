"""E1: bàn /#/engine thêm: việc chờ anh, lead mới, đơn mới. Lead và đơn mới hiện trên bàn trong 1 phút.

Hợp đồng (HOP-DONG.md):
- linhx_core/ban.py thuần Python:
    tong_hop(jobs: list, nguoi: list, don: list, luc: str, gio=24) -> dict
        {"viec_cho": jobs trang_thai "cho_duyet" (mới nhất trước),
         "lead_moi": Người có creation trong `gio` giờ trước luc (mới nhất trước),
         "don_moi": Đơn có creation trong `gio` giờ trước luc (mới nhất trước)}
- linhx_core/api_ban_dieu_hanh.py: @frappe.whitelist() `ban` (chỉ người điều hành) trả tong_hop.
- front/index.html #/engine gọi GET /api/method/linhx_core.api_ban_dieu_hanh.ban, vẽ vào #viec-cho, #lead-moi, #don-moi
  (mỗi dòng có tên/mã bản ghi); gọi lại ít nhất mỗi 60 giây (lead/đơn mới hiện trong 1 phút).
"""
from _chung import CORE, dong_trang, khong_import_frappe_dau_file, nap_module, trang_front_engine

LUC = "2026-11-09 12:00:00"


def test_tong_hop():
    bn = nap_module("linhx_core.ban", CORE)
    jobs = [{"name": "J1", "trang_thai": "cho_duyet", "creation": "2026-11-09 08:00:00"},
            {"name": "J2", "trang_thai": "xong", "creation": "2026-11-09 09:00:00"},
            {"name": "J3", "trang_thai": "cho_duyet", "creation": "2026-11-09 10:00:00"}]
    nguoi = [{"name": "N1", "creation": "2026-11-08 11:00:00"}, {"name": "N2", "creation": "2026-11-09 11:59:00"},
             {"name": "N3", "creation": "2026-11-08 12:30:00"}]
    don = [{"name": "D1", "creation": "2026-11-09 11:00:00"}, {"name": "D2", "creation": "2026-11-01 11:00:00"}]
    r = bn.tong_hop(jobs, nguoi, don, LUC)
    assert [x["name"] for x in r["viec_cho"]] == ["J3", "J1"]
    assert [x["name"] for x in r["lead_moi"]] == ["N2", "N3"]
    assert [x["name"] for x in r["don_moi"]] == ["D1"]
    assert [x["name"] for x in bn.tong_hop(jobs, nguoi, don, LUC, gio=1)["lead_moi"]] == ["N2"]
    khong_import_frappe_dau_file(CORE / "linhx_core" / "ban.py")


def test_ban_hien_va_tu_lam_moi():
    lan = {"n": 0}

    def ban(pt, b):
        lan["n"] += 1
        lead = [{"name": "LEAD-A", "ho_ten": "Lan"}] + ([{"name": "LEAD-MOI-B", "ho_ten": "Minh"}] if lan["n"] > 1 else [])
        return 200, {"message": {"viec_cho": [{"name": "VIEC-9", "workflow": "ai-noi-gi-ve-brand"}],
                                 "lead_moi": lead, "don_moi": [{"name": "DON-77", "so_tien": 99000}]}}, None
    api = {"/api/method/linhx_core.api_ban_dieu_hanh.ban": ban}
    from playwright.sync_api import sync_playwright  # noqa: F401  (trang_front_engine dùng)
    p, b, pg, s, _ = trang_front_engine(api, cho="#lead-moi")
    try:
        pg.wait_for_function("document.querySelector('#lead-moi').innerText.includes('LEAD-A') || document.querySelector('#lead-moi').innerText.includes('Lan')", timeout=10000)
        assert "VIEC-9" in pg.inner_text("#viec-cho") and "DON-77" in pg.inner_text("#don-moi")
        pg.wait_for_function("document.querySelector('#lead-moi').innerText.includes('LEAD-MOI-B') || document.querySelector('#lead-moi').innerText.includes('Minh')",
                             timeout=65000)
    finally:
        dong_trang(p, b, s)
