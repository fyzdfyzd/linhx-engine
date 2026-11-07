"""Q1: trang bán báo cáo 'AI nói gì về thương hiệu' trên template 0.1 (front/index.html, trang #/):
nhập thương hiệu, chọn gói, nút trả QR gọi B2. Từ trang bán tới ảnh QR ≤ 3 bước, chụp 390 và 1280. Không lộ giá khác catalog.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/pay/ban_bao_cao.py thuần Python (không import frappe ở đầu file):
    goi_cong_khai(ds_goi: list[dict]) -> list[{"ma", "ten", "gia", "mo_ta"}]  chỉ gói "ban" là True; không trả trường khác
    so_tien_don(ma_goi, ds_goi) -> int | None   giá theo catalog (gói đang bán), không nhận giá từ client
- apps/linhx_core/linhx_core/pay/api_ban.py: @frappe.whitelist(allow_guest=True) `goi()` và `tao_don(brand, goi, email=None)`;
  tao_don lấy số tiền bằng ban_bao_cao.so_tien_don rồi tạo đơn + QR bằng phần pay của B2.
- front/index.html trang #/ (form có sẵn input name="brand"):
    GET  /api/method/linhx_core.pay.api_ban.goi       -> {"message": [{"ma", "ten", "gia", "mo_ta"}]}
    mỗi gói là một phần tử bấm được có thuộc tính data-goi="<ma>"; nút trả có thuộc tính data-tra-qr
    POST /api/method/linhx_core.pay.api_ban.tao_don   JSON {"brand", "goi", ...} (KHÔNG gửi giá/số tiền)
         -> {"message": {"ma_don", "so_tien", "noi_dung_ck", "qr_url"}}
    hiện <img data-qr src="<qr_url>"> và số tiền.
- Mọi số tiền hiện trên trang phải là giá trong catalog API trả (không viết cứng giá trong front).
"""
import re

from _chung import ANH, CORE, GOC, PNG_1x1, may_chu_web, nap_module

CAT = [
    {"ma": "BC-AI", "ten": "Báo cáo AI nói gì", "gia": 5000, "mo_ta": "Ba AI, 8 câu"},
    {"ma": "BC-AI-SAU", "ten": "Báo cáo sâu", "gia": 99000, "mo_ta": "Thêm đối thủ"},
]
TIEN = re.compile(r"(\d{1,3}(?:[.,]\d{3})+|\d+)\s?(?:đ|₫|VNĐ|VND)(?!\w)")


def _bb():
    return nap_module("linhx_core.pay.ban_bao_cao", CORE)


def test_catalog_cong_khai():
    bb = _bb()
    ds = [{"ma": "A", "ten": "Gói A", "gia": 5000, "mo_ta": "x", "ban": True, "gia_san": 4000, "ghi_chu_noi_bo": "bí mật"},
          {"ma": "B", "ten": "Gói B", "gia": 7000, "mo_ta": "y", "ban": False}]
    cong = bb.goi_cong_khai(ds)
    assert cong == [{"ma": "A", "ten": "Gói A", "gia": 5000, "mo_ta": "x"}], "chỉ gói đang bán, chỉ 4 trường công khai"
    assert bb.so_tien_don("A", ds) == 5000
    assert bb.so_tien_don("B", ds) is None, "gói ngừng bán không tạo đơn"
    assert bb.so_tien_don("C", ds) is None


def test_api_ban():
    chu = (CORE / "linhx_core" / "pay" / "api_ban.py").read_text(encoding="utf-8")
    assert chu.count("allow_guest=True") >= 2 and "def goi(" in chu and "def tao_don(" in chu
    assert "so_tien_don" in chu, "tao_don phải lấy số tiền từ catalog qua so_tien_don"
    assert not re.search(r"def tao_don\([^)]*(gia|so_tien|tong)", chu), "tao_don không nhận giá từ client"


def test_front_khong_viet_cung_gia():
    chu = (GOC / "front" / "index.html").read_text(encoding="utf-8")
    js = chu[chu.find("<script"):]
    assert not TIEN.findall(js), f"front viết cứng giá: {TIEN.findall(js)[:3]}"


def test_tu_trang_ban_toi_qr_3_buoc():
    from playwright.sync_api import sync_playwright
    goi_post = []

    def tao_don(pt, b):
        g = next((x for x in CAT if x["ma"] == b.get("goi")), None)
        if pt != "POST" or not g:
            return 417, {"exception": "sai gói"}, None
        return 200, {"message": {"ma_don": "DON-Q1-1", "so_tien": g["gia"], "noi_dung_ck": "LXQ1ABC123",
                                 "qr_url": "/qr-q1.png"}}, None
    api = {
        "/api/method/linhx_core.pay.api_ban.goi": lambda pt, b: (200, {"message": CAT}, None),
        "/api/method/linhx_core.pay.api_ban.tao_don": tao_don,
        "/api/method/linhx_worker.api.phien": lambda pt, b: (200, {"message": {"user": "Guest", "dieu_hanh": False, "csrf": None}}, None),
        "/qr-q1.png": lambda pt, b: (200, PNG_1x1, "image/png"),
    }
    s, url = may_chu_web(GOC / "front", api, ghi_nhan=goi_post)
    ANH.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                goi_post.clear()
                pg = b.new_page(viewport={"width": rong, "height": 900})
                pg.route("**/*", lambda r: r.abort() if not r.request.url.startswith(url) else r.continue_())
                pg.goto(url + "/index.html#/")
                pg.wait_for_selector('[data-goi="BC-AI-SAU"]', timeout=15000)
                # bước 1: nhập thương hiệu; bước 2: chọn gói; bước 3: bấm trả QR
                pg.fill('input[name="brand"]', "Trà Xanh Đồi Mây")
                pg.click('[data-goi="BC-AI-SAU"]')
                pg.click("[data-tra-qr]")
                pg.wait_for_selector("img[data-qr]", state="visible", timeout=15000)
                assert pg.get_attribute("img[data-qr]", "src").endswith("/qr-q1.png")
                pg.wait_for_function("document.querySelector('img[data-qr]').naturalWidth > 0", timeout=10000)
                post = [x for x in goi_post if x[0] == "POST" and "tao_don" in x[1]]
                assert len(post) == 1, "bấm trả một lần gọi tao_don đúng một lần"
                than = post[0][2]
                assert than.get("goi") == "BC-AI-SAU" and than.get("brand") == "Trà Xanh Đồi Mây"
                assert not ({"gia", "so_tien", "tong", "amount"} & set(than)), f"front không được gửi giá: {than}"
                chu = pg.inner_text("body")
                assert "99.000" in chu or "99,000" in chu, "phải hiện số tiền của gói đã chọn"
                la = {int(re.sub(r"\D", "", x)) for x in TIEN.findall(chu)} - {x["gia"] for x in CAT}
                assert not la, f"trang hiện giá ngoài catalog: {la}"
                pg.screenshot(path=str(ANH / f"q1-{rong}.png"), full_page=True)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                assert sw <= rong, f"tràn ngang ở {rong}px"
                pg.close()
            b.close()
    finally:
        s.shutdown()
