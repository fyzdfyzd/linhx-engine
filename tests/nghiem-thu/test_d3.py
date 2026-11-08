"""D3: bảng phễu 6 tầng bản 1 (biết, mồi, liên hệ, cơ hội/đơn, khách, quay lại) đếm từ crm + pay. Số mỗi tầng khớp số bản ghi thật.

Hợp đồng (HOP-DONG.md):
- linhx_core/pheu.py thuần Python:
    TANG = ("biet", "moi", "lien_he", "co_hoi_don", "khach", "quay_lai")
    dem(nguoi: list, co_hoi: list, don: list, luot_xem: int) -> dict[tang, int]
        biet       = luot_xem (lượt xem trang, truyền vào)
        moi        = số Người có nguon == "T1" (đã dùng mồi)
        lien_he    = tổng số Người
        co_hoi_don = số Người có ít nhất 1 Cơ hội hoặc 1 Đơn (theo trường nguoi)
        khach      = số Người có ít nhất 1 Đơn trang_thai "da_tra"
        quay_lai   = số Người có từ 2 Đơn "da_tra" trở lên
- linhx_core/api_pheu.py: @frappe.whitelist() `pheu` (chỉ người điều hành) đếm từ LX Nguoi, LX Co Hoi, LX Don.
- front/index.html #/engine gọi GET /api/method/linhx_core.api_pheu.pheu -> {"message": {tang: số}} và vẽ
  6 phần tử [data-tang="<tang>"] chứa đúng số.
"""
from _chung import CORE, dong_trang, khong_import_frappe_dau_file, nap_module, trang_front_engine

NGUOI = [{"name": "N1", "nguon": "T1"}, {"name": "N2", "nguon": "trang-ifagent"}, {"name": "N3", "nguon": "T1"},
         {"name": "N4"}, {"name": "N5", "nguon": "zalo"}]
CO_HOI = [{"name": "C1", "nguoi": "N1"}, {"name": "C2", "nguoi": "N2"}, {"name": "C3", "nguoi": "N1"}]
DON = [{"ma": "D1", "nguoi": "N2", "trang_thai": "da_tra"}, {"ma": "D2", "nguoi": "N2", "trang_thai": "da_tra"},
       {"ma": "D3", "nguoi": "N3", "trang_thai": "cho_tra"}, {"ma": "D4", "nguoi": "N4", "trang_thai": "da_tra"},
       {"ma": "D5", "nguoi": "N4", "trang_thai": "huy"}]
KY_VONG = {"biet": 120, "moi": 2, "lien_he": 5, "co_hoi_don": 4, "khach": 2, "quay_lai": 1}


def test_dem_khop_ban_ghi():
    ph = nap_module("linhx_core.pheu", CORE)
    assert ph.TANG == ("biet", "moi", "lien_he", "co_hoi_don", "khach", "quay_lai")
    assert ph.dem(NGUOI, CO_HOI, DON, 120) == KY_VONG
    assert ph.dem([], [], [], 0) == {t: 0 for t in ph.TANG}
    khong_import_frappe_dau_file(CORE / "linhx_core" / "pheu.py")


def test_api():
    chu = (CORE / "linhx_core" / "api_pheu.py").read_text(encoding="utf-8")
    assert "def pheu(" in chu and "allow_guest" not in chu


def test_ban_hien_6_tang():
    api = {"/api/method/linhx_core.api_pheu.pheu": lambda pt, b: (200, {"message": KY_VONG}, None)}
    p, b, pg, s, _ = trang_front_engine(api, cho='[data-tang="quay_lai"]')
    try:
        pg.wait_for_function("document.querySelector('[data-tang=\"biet\"]').innerText.includes('120')", timeout=10000)
        for t, n in KY_VONG.items():
            assert str(n) in pg.inner_text(f'[data-tang="{t}"]'), f"tầng {t} phải hiện {n}"
    finally:
        dong_trang(p, b, s)
