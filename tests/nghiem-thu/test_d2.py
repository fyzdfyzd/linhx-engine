"""D2: kết quả đầy đủ T1 đổi lấy email/Zalo, ghi Người + Đồng ý + tầng phễu. Nhập email nhận kết quả, có Người mới gắn nguồn T1.

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/t1.py thuần Python:
    ghi_ket_qua(du_lieu: dict, ds_nguoi: list, so_dong_y: list, luc: str) -> dict
        du_lieu {"email" | "zalo", "ho_ten"?, "tong": int, "muc": str, "dong_y_lien_he": True, "dong_y_marketing": bool}
        thiếu cả email và zalo -> ValueError; dong_y_lien_he không True -> ValueError
        trả {"ds_nguoi", "nguoi" (nguon "T1", tang_pheu "moi", t1_tong, t1_muc), "so_dong_y"}
        người đã có (gộp trùng) giữ nguồn cũ, chỉ cập nhật t1_tong/t1_muc
- LX Nguoi thêm trường nguon (Data) và tang_pheu (Select có biet, moi, lien_he, co_hoi_don, khach, quay_lai).
- linhx_core/crm/api_form.py thêm @frappe.whitelist(allow_guest=True, methods=["POST"]) `nhan_ket_qua_t1`.
- Trang /kham (D1): sau tóm tắt có <form data-nhan-ket-qua> (input name email, name zalo, checkbox dong_y_lien_he,
  dong_y_marketing); gửi POST JSON {email|zalo, tong, muc, dong_y_lien_he, ...} tới
  `${API_GOC}/api/method/linhx_core.crm.api_form.nhan_ket_qua_t1`; chỉ khi máy chủ trả 200 mới hiện [data-ket-qua-day-du].
"""
import json

import pytest

from _chung import CORE, GOC, TRANG_BU, dung_trang_bu, may_chu_web, nap_module, ten_truong, tim_doctype

LUC = "2026-11-09 09:00:00"
URL_API = "/api/method/linhx_core.crm.api_form.nhan_ket_qua_t1"


def _t():
    return nap_module("linhx_core.crm.t1", CORE)


def test_ghi_nguoi_nguon_t1():
    t = _t()
    r = t.ghi_ket_qua({"email": "Lan@VD.vn", "tong": 12, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True}, [], [], LUC)
    n = r["nguoi"]
    assert n["nguon"] == "T1" and n["tang_pheu"] == "moi" and n["t1_tong"] == 12 and n["t1_muc"] == "Sẵn sàng một phần"
    assert [(x["muc_dich"], x["dong_y"]) for x in r["so_dong_y"]] == [("lien_he", True)]
    cu = [{"ho_ten": "Lan", "email": "lan@vd.vn", "nguon": "trang-ifagent", "tang_pheu": "lien_he"}]
    r2 = t.ghi_ket_qua({"email": "lan@vd.vn", "tong": 15, "muc": "Sẵn sàng", "dong_y_lien_he": True}, cu, [], LUC)
    assert len(r2["ds_nguoi"]) == 1 and r2["nguoi"]["nguon"] == "trang-ifagent" and r2["nguoi"]["t1_tong"] == 15


def test_tu_choi():
    t = _t()
    with pytest.raises(ValueError):
        t.ghi_ket_qua({"tong": 1, "muc": "x", "dong_y_lien_he": True}, [], [], LUC)
    with pytest.raises(ValueError):
        t.ghi_ket_qua({"zalo": "zl1", "tong": 1, "muc": "x"}, [], [], LUC)


def test_doctype_va_api():
    _, d = tim_doctype("LX Nguoi")
    tr = ten_truong(d)
    assert "nguon" in tr
    assert {"biet", "moi", "lien_he", "co_hoi_don", "khach", "quay_lai"} <= set(str(tr.get("tang_pheu", {}).get("options", "")).split("\n"))
    chu = (CORE / "linhx_core" / "crm" / "api_form.py").read_text(encoding="utf-8")
    assert "def nhan_ket_qua_t1(" in chu


def test_trang_kham_doi_email_lay_ket_qua():
    from playwright.sync_api import sync_playwright
    k = json.loads((GOC / "sites" / "ifagent" / "kham.json").read_text(encoding="utf-8"))
    ghi, tra = [], {"ma": 500}
    api = {URL_API: lambda pt, b: (tra["ma"], {"message": {"ok": tra["ma"] == 200}}, None)}
    s, url = may_chu_web(TRANG_BU / "out", api, ghi_nhan=ghi)
    try:
        dung_trang_bu({"SITE_JSON": str(GOC / "sites" / "ifagent" / "site.json"), "API_GOC": url})
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 390, "height": 900})
            pg.goto(url + "/kham", wait_until="networkidle")
            if pg.locator("[data-cau]").count() == 0:
                pg.goto(url + "/kham.html", wait_until="networkidle")
            for c in k["cau"]:
                pg.locator(f'[data-cau="{c["ma"]}"] input[type="radio"]').first.check()
            if pg.locator("[data-xem-ket-qua]").count():
                pg.locator("[data-xem-ket-qua]").first.click()
            pg.wait_for_selector("[data-tom-tat]", state="visible", timeout=10000)
            assert not pg.locator("[data-ket-qua-day-du]").is_visible(), "chưa đưa email thì chưa thấy kết quả đầy đủ"
            f = pg.locator("form[data-nhan-ket-qua]")
            f.locator('[name="email"]').fill("thu@vd.vn")
            f.locator('[name="dong_y_lien_he"]').check()
            f.locator('button, [type="submit"]').first.click()
            pg.wait_for_timeout(1000)
            assert not pg.locator("[data-ket-qua-day-du]").is_visible(), "máy chủ lỗi thì không hiện kết quả đầy đủ"
            tra["ma"] = 200
            f.locator('button, [type="submit"]').first.click()
            pg.wait_for_selector("[data-ket-qua-day-du]", state="visible", timeout=10000)
            post = [x[2] for x in ghi if x[0] == "POST" and x[1].startswith(URL_API)]
            assert post and post[-1].get("email") == "thu@vd.vn" and post[-1].get("dong_y_lien_he") is True
            assert isinstance(post[-1].get("tong"), int) and post[-1].get("muc")
            b.close()
    finally:
        s.shutdown()
