"""C2: form Trang BU ghi Người + Cơ hội + Đồng ý vào bản cài. Gửi form thì có Người, Cơ hội, Đồng ý mới.

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/form.py thuần Python:
    xu_ly(du_lieu: dict, ds_nguoi: list, so_dong_y: list, luc: str, nguon: str) -> dict
        du_lieu {"ho_ten", "dien_thoai", "email", "nhu_cau", "dong_y_lien_he": bool, "dong_y_marketing": bool}
        thiếu cả dien_thoai và email -> ValueError; dong_y_lien_he không True -> ValueError (không lưu gì)
        trả {"ds_nguoi" (đã gộp trùng bằng gop_trung), "nguoi": dict, "co_hoi": {"nguoi", "nhu_cau", "nguon", "trang_thai": "moi"},
             "so_dong_y": sổ mới (dong_y.ghi): luôn có lien_he=True; marketing chỉ khi tick (True), không tick thì không ghi}
- linhx_core/crm/api_form.py: @frappe.whitelist(allow_guest=True, methods=["POST"]) `nhan_form` gọi form.xu_ly rồi insert
  LX Nguoi / LX Co Hoi / LX Dong Y; có giới hạn tần suất (frappe rate_limit hoặc tự đếm theo IP).
- trang-bu: trang chủ có <form data-lead> với input name ho_ten, dien_thoai, email, nhu_cau (textarea được),
  checkbox name dong_y_lien_he và dong_y_marketing; gửi POST JSON tới
  `${API_GOC}/api/method/linhx_core.crm.api_form.nhan_form` (API_GOC đọc lúc dựng, mặc định "" = cùng gốc);
  thành công hiện phần tử [data-cam-on]; chưa tick dong_y_lien_he thì không gửi.
- Sau khi đạt hộp đen, bộ điều phối chạy thêm kiểm tích hợp HTTP thật trên bench: tests/nghiem-thu/tich-hop/th_c2.py
  (khách gửi form -> có LX Nguoi, LX Co Hoi, LX Dong Y; khách không đọc lại được hồ sơ).
"""
import pytest

from _chung import CORE, TRANG_BU, dung_trang_bu, khong_import_frappe_dau_file, may_chu_web, nap_module

LUC = "2026-11-09 09:00:00"
URL_API = "/api/method/linhx_core.crm.api_form.nhan_form"


def _f():
    return nap_module("linhx_core.crm.form", CORE)


def test_xu_ly_tao_du_ba():
    f = _f()
    r = f.xu_ly({"ho_ten": "Lan", "dien_thoai": "0912345678", "nhu_cau": "Cần báo cáo", "dong_y_lien_he": True},
                [], [], LUC, "trang-ifagent")
    assert len(r["ds_nguoi"]) == 1 and r["nguoi"]["ho_ten"] == "Lan"
    assert r["co_hoi"]["trang_thai"] == "moi" and r["co_hoi"]["nguon"] == "trang-ifagent" and r["co_hoi"]["nhu_cau"] == "Cần báo cáo"
    md = [(x["muc_dich"], x["dong_y"]) for x in r["so_dong_y"]]
    assert md == [("lien_he", True)], "không tick marketing thì chỉ ghi đồng ý liên hệ"
    r2 = f.xu_ly({"ho_ten": "Lan N", "dien_thoai": "+84912345678", "dong_y_lien_he": True, "dong_y_marketing": True},
                 r["ds_nguoi"], r["so_dong_y"], LUC, "trang-ifagent")
    assert len(r2["ds_nguoi"]) == 1, "gửi lại cùng số phải gộp người"
    assert ("marketing", True) in [(x["muc_dich"], x["dong_y"]) for x in r2["so_dong_y"]]


def test_tu_choi_khi_thieu():
    f = _f()
    with pytest.raises(ValueError):
        f.xu_ly({"ho_ten": "A", "dong_y_lien_he": True}, [], [], LUC, "x")
    with pytest.raises(ValueError):
        f.xu_ly({"ho_ten": "A", "email": "a@vd.vn", "dong_y_lien_he": False}, [], [], LUC, "x")


def test_api():
    chu = (CORE / "linhx_core" / "crm" / "api_form.py").read_text(encoding="utf-8")
    assert "allow_guest=True" in chu and "def nhan_form(" in chu
    assert "rate_limit" in chu or "request_ip" in chu, "nhan_form mở cho khách phải giới hạn tần suất"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "form.py")


def test_form_trang_bu_gui_dung():
    from playwright.sync_api import sync_playwright
    ghi = []
    api = {URL_API: lambda pt, b: (200, {"message": {"ok": True}}, None)}
    s, url = may_chu_web(TRANG_BU / "out", api, ghi_nhan=ghi)
    try:
        dung_trang_bu({"API_GOC": url})
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                ghi.clear()
                pg = b.new_page(viewport={"width": rong, "height": 900})
                pg.goto(url + "/", wait_until="networkidle")
                f = pg.locator("form[data-lead]")
                f.locator('[name="ho_ten"]').fill("Minh Thử")
                f.locator('[name="dien_thoai"]').fill("0987000111")
                f.locator('[name="email"]').fill("minh@vd.vn")
                f.locator('[name="nhu_cau"]').fill("Muốn thử T1")
                f.locator('button, [type="submit"]').first.click()
                pg.wait_for_timeout(800)
                assert not [x for x in ghi if x[0] == "POST"], "chưa tick đồng ý liên hệ thì không gửi"
                f.locator('[name="dong_y_lien_he"]').check()
                f.locator('button, [type="submit"]').first.click()
                pg.wait_for_selector("[data-cam-on]", state="visible", timeout=10000)
                post = [x for x in ghi if x[0] == "POST" and x[1].startswith(URL_API)]
                assert len(post) == 1
                t = post[0][2]
                assert t.get("ho_ten") == "Minh Thử" and t.get("dien_thoai") == "0987000111" and t.get("email") == "minh@vd.vn"
                assert t.get("dong_y_lien_he") is True and not t.get("dong_y_marketing")
                sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                assert sw <= rong, f"tràn ngang ở {rong}px"
                pg.close()
            b.close()
    finally:
        s.shutdown()
