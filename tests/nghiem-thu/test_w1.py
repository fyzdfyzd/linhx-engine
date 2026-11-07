"""W1: bảng thợ trên /#/engine: phiếu đang chạy, phút, token, tỉ lệ phiếu sửa theo tuần, số lần chạm trần.

Hợp đồng (HOP-DONG.md):
- Nguồn số liệu là nhật ký phiếu thật do bộ điều phối ghi (canh/dieu-phoi-engine.ps1, thợ không sửa):
    .canh/phieu.tsv  (UTF-8, tab, dòng đầu là tên cột) cột:
        luc_giao, luc_xong, tho, phieu, feature, loai (moi|sua), dung (xong|gio|ngu), ket_luan (DAT|CHUA_DAT),
        phut, token_vao, token_ra
    .canh/dang-chay.json  [{"tho", "phieu", "feature", "tu"}]
- apps/linhx_worker/linhx_worker/bang_tho.py thuần Python (không import frappe ở đầu file):
    COT: tuple tên cột đúng thứ tự trên
    doc_phieu(duong_dan) -> list[dict]   số (tho, phut, token_*) thành int, ô trống thành 0; thiếu file -> []
    tong_hop(ds, dang_chay=None) -> dict
        {"so_phieu", "dang_chay": list, "phut", "token_vao", "token_ra",
         "cham_tran": số phiếu dung in (gio, ngu),
         "theo_tuan": [{"tuan": "YYYY-Www" (ISO, theo luc_giao), "so_phieu", "so_sua", "ti_le_sua": so_sua/so_phieu làm tròn 2}]
                      xếp tuần tăng dần}
- apps/linhx_worker/linhx_worker/api.py có @frappe.whitelist() `bang_tho` (chỉ người điều hành) trả tong_hop.
- front/index.html: trang #/engine gọi goi("bang_tho") và vẽ vào phần tử id="bang-tho": tên phiếu đang chạy,
  tỉ lệ sửa mỗi tuần dạng phần trăm số nguyên (vd. 30%), số lần chạm trần trong phần tử id="cham-tran".
"""
import json
import re

from _chung import ANH, GOC, may_chu_web, nap_module

APP = GOC / "apps" / "linhx_worker"
COT = ("luc_giao", "luc_xong", "tho", "phieu", "feature", "loai", "dung", "ket_luan", "phut", "token_vao", "token_ra")

# 10 phiếu mẫu: tuần 2026-W45 (2-8/11) 6 phiếu, 2 sửa; tuần 2026-W46 (9-15/11) 4 phiếu, 3 sửa; 2 chạm trần
MAU = [
    ("2026-11-02T09:00:00", "2026-11-02T09:31:00", 1, "20261102-0900-t1", "N1", "moi", "xong", "CHUA_DAT", 31, 120000, 9000),
    ("2026-11-02T10:00:00", "2026-11-02T10:40:00", 1, "20261102-1000-t1", "N1", "sua", "gio", "DAT", 40, 150000, 11000),
    ("2026-11-03T09:00:00", "2026-11-03T09:20:00", 2, "20261103-0900-t2", "N3", "moi", "xong", "DAT", 20, 80000, 5000),
    ("2026-11-04T09:00:00", "2026-11-04T09:25:00", 2, "20261104-0900-t2", "A1", "moi", "xong", "CHUA_DAT", 25, 90000, 6000),
    ("2026-11-05T09:00:00", "2026-11-05T09:15:00", 2, "20261105-0900-t2", "A1", "sua", "xong", "DAT", 15, 60000, 4000),
    ("2026-11-08T22:00:00", "2026-11-08T22:30:00", 1, "20261108-2200-t1", "B1", "moi", "xong", "DAT", 30, 100000, 7000),
    ("2026-11-09T08:00:00", "2026-11-09T08:30:00", 1, "20261109-0800-t1", "C1", "moi", "ngu", "CHUA_DAT", 30, 50000, 3000),
    ("2026-11-09T09:00:00", "2026-11-09T09:40:00", 1, "20261109-0900-t1", "C1", "sua", "xong", "CHUA_DAT", 40, 70000, 5000),
    ("2026-11-10T09:00:00", "2026-11-10T09:20:00", 2, "20261110-0900-t2", "C1", "sua", "xong", "DAT", 20, 65000, 4500),
    ("2026-11-11T09:00:00", "2026-11-11T09:10:00", 2, "20261111-0900-t2", "B2", "sua", "xong", "DAT", 10, 30000, 2000),
]


def _bt():
    return nap_module("linhx_worker.bang_tho", APP)


def _ghi_tsv(p, dong):
    p.write_text("\t".join(COT) + "\n" + "".join("\t".join(str(x) for x in d) + "\n" for d in dong), encoding="utf-8")


def test_cot_khop_bo_dieu_phoi():
    bt = _bt()
    assert tuple(bt.COT) == COT
    ps1 = (GOC / "canh" / "dieu-phoi-engine.ps1").read_text(encoding="utf-8-sig")
    assert "`t".join(COT) in ps1, "cột phieu.tsv của bộ điều phối phải khớp COT"


def test_tong_hop_10_phieu_mau(tmp_path):
    bt = _bt()
    p = tmp_path / "phieu.tsv"
    _ghi_tsv(p, MAU)
    ds = bt.doc_phieu(p)
    assert len(ds) == 10 and ds[0]["phut"] == 31 and ds[0]["tho"] == 1
    dc = [{"tho": 1, "phieu": "20261111-1000-t1", "feature": "Q1", "tu": "2026-11-11T10:00:00"}]
    th = bt.tong_hop(ds, dang_chay=dc)
    assert th["so_phieu"] == 10
    assert th["dang_chay"] == dc
    assert th["phut"] == sum(d[8] for d in MAU)
    assert th["token_vao"] == sum(d[9] for d in MAU) and th["token_ra"] == sum(d[10] for d in MAU)
    assert th["cham_tran"] == 2, "chạm trần = phiếu dừng vì quá giờ hoặc ngủ quên"
    assert th["theo_tuan"] == [
        {"tuan": "2026-W45", "so_phieu": 6, "so_sua": 2, "ti_le_sua": 0.33},
        {"tuan": "2026-W46", "so_phieu": 4, "so_sua": 3, "ti_le_sua": 0.75},
    ]
    assert bt.doc_phieu(tmp_path / "khong-co.tsv") == []
    assert bt.tong_hop([])["so_phieu"] == 0


def test_khop_so_phieu_that():
    p = GOC / ".canh" / "phieu.tsv"
    assert p.exists(), "chưa có .canh/phieu.tsv (bộ điều phối ghi sau mỗi phiếu chấm xong)"
    dong = [x for x in p.read_text(encoding="utf-8-sig").splitlines()[1:] if x.strip()]
    assert p.read_text(encoding="utf-8-sig").splitlines()[0].split("\t") == list(COT)
    bt = _bt()
    th = bt.tong_hop(bt.doc_phieu(p))
    assert th["so_phieu"] == len(dong) and sum(t["so_phieu"] for t in th["theo_tuan"]) == len(dong)


def test_api_bang_tho():
    chu = (APP / "linhx_worker" / "api.py").read_text(encoding="utf-8")
    m = re.search(r"@frappe\.whitelist\([^)]*\)\s*\ndef bang_tho\(", chu)
    assert m, "api.py thiếu @frappe.whitelist() def bang_tho"
    than = chu[m.end():].split("\n@frappe", 1)[0]
    assert "_la_dieu_hanh()" in than, "bang_tho chỉ cho người điều hành"
    assert "allow_guest" not in m.group(0)
    assert "bang_tho" in than and "tong_hop" in than


def test_ban_engine_hien_bang_tho():
    from playwright.sync_api import sync_playwright
    th = {"so_phieu": 10, "phut": 261, "token_vao": 815000, "token_ra": 56500, "cham_tran": 7,
          "dang_chay": [{"tho": 1, "phieu": "PHIEU-MOC-W1-9c2", "feature": "Q1", "tu": "2026-11-11T10:00:00"}],
          "theo_tuan": [{"tuan": "2026-W45", "so_phieu": 6, "so_sua": 2, "ti_le_sua": 0.33},
                        {"tuan": "2026-W46", "so_phieu": 4, "so_sua": 3, "ti_le_sua": 0.75}]}
    api = {
        "/api/method/linhx_worker.api.phien": lambda pt, b: (200, {"message": {"user": "dh@vidu.vn", "dieu_hanh": True, "csrf": "x"}}, None),
        "/api/method/linhx_worker.api.bang": lambda pt, b: (200, {"message": {"workers": [], "workflows": [], "jobs": [], "dem": {}, "luc": "2026-11-11 10:00:00", "user": "dh@vidu.vn"}}, None),
        "/api/method/linhx_worker.api.bang_tho": lambda pt, b: (200, {"message": th}, None),
    }
    s, url = may_chu_web(GOC / "front", api)
    ANH.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                pg = b.new_page(viewport={"width": rong, "height": 900})
                pg.route("**/*", lambda r: r.abort() if not r.request.url.startswith(url) else r.continue_())
                pg.goto(url + "/index.html#/engine")
                pg.wait_for_selector("#bang-tho", timeout=15000)
                pg.wait_for_function("document.querySelector('#bang-tho').innerText.includes('PHIEU-MOC-W1-9c2')", timeout=15000)
                chu = pg.inner_text("#bang-tho")
                assert "33%" in chu and "75%" in chu, "tỉ lệ sửa theo tuần phải hiện dạng phần trăm"
                assert "7" in pg.inner_text("#cham-tran"), "phải hiện số lần chạm trần"
                pg.screenshot(path=str(ANH / f"w1-{rong}.png"), full_page=True)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                assert sw <= rong, f"tràn ngang ở {rong}px"
                pg.close()
            b.close()
    finally:
        s.shutdown()
