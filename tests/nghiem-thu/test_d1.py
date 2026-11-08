"""D1: Tool T1 Khám (LAB113) thành freebie trên Trang BU. Người dùng chạy T1 và thấy bản tóm tắt.

Hợp đồng (HOP-DONG.md):
- sites/ifagent/kham.json (nội dung lấy từ bản thử T1 Khám của LAB113):
    {"tieu_de", "cau": [{"ma", "hoi", "lua_chon": [{"nhan", "diem": int}]}] (>= 5 câu),
     "muc": [{"tu": int, "den": int, "ten", "tom_tat"}] phủ kín từ tổng nhỏ nhất tới lớn nhất, không chồng}
- trang-bu có trang /kham (out/kham.html hoặc out/kham/index.html), dựng với SITE_JSON=sites/ifagent/site.json,
  đọc kham.json lúc dựng. Mỗi câu một khối [data-cau="<ma>"], mỗi lựa chọn là input radio trong khối đó.
  Trả lời đủ thì hiện [data-tom-tat] chứa "ten" và "tom_tat" của mức ứng với tổng điểm. Chạy hoàn toàn trên trình duyệt,
  không gọi mạng.
"""
import json

from _chung import GOC, TRANG_BU, chan_ra_ngoai, dung_trang_bu, may_chu_web

KHAM = GOC / "sites" / "ifagent" / "kham.json"


def _k():
    assert KHAM.exists(), "thiếu sites/ifagent/kham.json"
    return json.loads(KHAM.read_text(encoding="utf-8"))


def test_kham_json():
    k = _k()
    assert len(k["cau"]) >= 5
    nho = sum(min(l["diem"] for l in c["lua_chon"]) for c in k["cau"])
    lon = sum(max(l["diem"] for l in c["lua_chon"]) for c in k["cau"])
    muc = sorted(k["muc"], key=lambda m: m["tu"])
    assert muc[0]["tu"] <= nho and muc[-1]["den"] >= lon, "các mức phải phủ từ tổng nhỏ nhất tới lớn nhất"
    for a, b in zip(muc, muc[1:]):
        assert b["tu"] == a["den"] + 1, "các mức liền nhau, không chồng, không hở"


def _muc(k, tong):
    return next(m for m in k["muc"] if m["tu"] <= tong <= m["den"])


def test_chay_t1_thay_tom_tat():
    from playwright.sync_api import sync_playwright
    k = _k()
    s, url = may_chu_web(TRANG_BU / "out")
    try:
        dung_trang_bu({"SITE_JSON": str(GOC / "sites" / "ifagent" / "site.json")})
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong, chon in ((390, "max"), (1280, "min")):
                pg = b.new_page(viewport={"width": rong, "height": 900})
                bi_chan = chan_ra_ngoai(pg, url)
                pg.goto(url + "/kham", wait_until="networkidle")
                if pg.locator("[data-cau]").count() == 0:
                    pg.goto(url + "/kham.html", wait_until="networkidle")
                tong = 0
                for c in k["cau"]:
                    ds = c["lua_chon"]
                    i = max(range(len(ds)), key=lambda j: ds[j]["diem"]) if chon == "max" else min(range(len(ds)), key=lambda j: ds[j]["diem"])
                    tong += ds[i]["diem"]
                    pg.locator(f'[data-cau="{c["ma"]}"] input[type="radio"]').nth(i).check()
                nut = pg.locator("[data-xem-ket-qua]")
                if nut.count():
                    nut.first.click()
                pg.wait_for_selector("[data-tom-tat]", state="visible", timeout=10000)
                tt = pg.inner_text("[data-tom-tat]")
                m = _muc(k, tong)
                assert m["ten"] in tt and m["tom_tat"][:40] in tt, f"tổng {tong}: phải hiện mức {m['ten']}"
                assert not bi_chan, f"T1 gọi ra ngoài: {bi_chan[:3]}"
                sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                assert sw <= rong, f"tràn ngang ở {rong}px"
                pg.close()
            b.close()
    finally:
        s.shutdown()
