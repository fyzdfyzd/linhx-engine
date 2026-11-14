"""Nghiệm thu landing Listening Vietnam. KHÓA: thợ không được sửa file này.
Chạy: python -m pytest viec/lvn-landing/nghiem-thu -q  (cần: pip install pytest playwright; python -m playwright install chromium)
"""
import pathlib
import pytest
from playwright.sync_api import sync_playwright

GOC = pathlib.Path(__file__).resolve().parents[1]
TRANG = (GOC / "index.html").as_uri()
BO_QUA = {"brand", "tham-khao", "nghiem-thu", "bang-chung"}
KHOI = ["van-de", "cach-lam", "bao-cao-mau", "bang-gia", "lien-he"]


@pytest.fixture(scope="module")
def tr():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def mo(tr, w, h):
    pg = tr.new_page(viewport={"width": w, "height": h})
    loi = []
    pg.on("console", lambda m: m.type == "error" and loi.append(m.text))
    pg.on("pageerror", lambda e: loi.append(str(e)))
    pg.goto(TRANG)
    pg.wait_for_load_state("load")
    return pg, loi


def test_dung_luong_duoi_300kb():
    """Tiêu chí: tổng file trang (trừ brand/tham-khao/nghiem-thu/bang-chung) < 300 KB."""
    tong = sum(f.stat().st_size for f in GOC.rglob("*") if f.is_file() and f.relative_to(GOC).parts[0] not in BO_QUA)
    assert tong < 300 * 1024, tong


def test_khung_va_ten(tr):
    """Tiêu chí: lang vi, tiêu đề có tên brand, đủ 5 khối đúng thứ tự, viết đúng tên."""
    pg, _ = mo(tr, 1280, 800)
    assert pg.get_attribute("html", "lang") == "vi"
    assert "Listening Vietnam" in pg.title()
    ys = [pg.locator(f"#{k}").bounding_box()["y"] for k in KHOI]
    assert ys == sorted(ys)
    chu = pg.inner_text("body")
    for sai in ("Listening Việt Nam", "ListeningVN", "Listen VN"):
        assert sai not in chu
    for m in ("Sentinel", "Analyzer", "Predictor", "Narrator", "Tracker"):
        assert m in chu
    assert sum(chu.count(c) for c in "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ") > 50
    assert "[điền sau]" in pg.inner_text("#bang-gia")


@pytest.mark.parametrize("w,h", [(360, 740), (1280, 800)])
def test_cta_man_dau_va_khong_tran(tr, w, h):
    """Tiêu chí: nút Nhận báo cáo mẫu thấy ngay màn đầu, không cuộn ngang, không lỗi console."""
    pg, loi = mo(tr, w, h)
    cta = pg.locator('[data-cta="bao-cao-mau"]').first
    assert cta.is_visible()
    bb = cta.bounding_box()
    assert bb["y"] + bb["height"] <= h
    assert pg.evaluate("document.documentElement.scrollWidth") <= w
    assert loi == []


def test_form_gui_hien_cam_on(tr):
    """Tiêu chí: bấm CTA tới form, email sai không gửi được, email đúng hiện #cam-on."""
    pg, loi = mo(tr, 360, 740)
    pg.locator('[data-cta="bao-cao-mau"]').first.click()
    f = pg.locator("#form-lien-he")
    email = f.locator('input[type="email"]')
    assert email.get_attribute("required") is not None
    assert not pg.locator("#cam-on").is_visible()
    email.fill("sai")
    f.locator('[type="submit"]').click()
    assert not pg.locator("#cam-on").is_visible()
    email.fill("ten@congty.vn")
    f.locator('[type="submit"]').click()
    pg.wait_for_selector("#cam-on", state="visible", timeout=3000)
    assert loi == []
