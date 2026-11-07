"""C4: Trang BU thứ hai (unikon) dựng chỉ bằng file cấu hình trên khuôn C1, không sửa code khuôn.

Hợp đồng (HOP-DONG.md):
- sites/unikon/site.json: {"ten": "unikon", "noi_dung": {"tieu_de", "mo_ta", "muc": [{"ten", "mo_ta"}]}, ...}
  sites/unikon/ chỉ chứa cấu hình và ảnh (.json .md .png .jpg .jpeg .webp .svg), không có code.
- Khuôn trang-bu (C1, C3) dựng site theo biến môi trường SITE_JSON=<đường dẫn site.json>: nội dung lấy từ "noi_dung"
  (NOI_DUNG_URL vẫn ưu tiên nếu có). Phần nhận SITE_JSON là việc của C3 (đưa ifagent vào sites/ifagent/site.json).
- Các commit "C4: ..." không đụng file nào ngoài sites/unikon/, bang-chung/C4/ và features-dot1b.json.
"""
import json
import os
import shutil
import subprocess

from _chung import ANH, GOC, git, may_chu_web

SITE = GOC / "sites" / "unikon"
TB = GOC / "trang-bu"
DUOC = {".json", ".md", ".png", ".jpg", ".jpeg", ".webp", ".svg"}


def _site():
    p = SITE / "site.json"
    assert p.exists(), "thiếu sites/unikon/site.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_chi_cau_hinh():
    d = _site()
    assert d.get("ten") == "unikon"
    nd = d.get("noi_dung") or {}
    assert isinstance(nd.get("tieu_de"), str) and nd["tieu_de"].strip()
    assert isinstance(nd.get("mo_ta"), str)
    assert isinstance(nd.get("muc"), list) and nd["muc"] and all({"ten", "mo_ta"} <= set(m) for m in nd["muc"])
    la = [str(p.relative_to(GOC)) for p in SITE.rglob("*") if p.is_file() and p.suffix.lower() not in DUOC]
    assert not la, f"sites/unikon chỉ chứa cấu hình, không chứa code: {la}"


def test_diff_khong_dung_khuon():
    cac = [x for x in git("log", "--format=%H", "--grep=^C4:", "--extended-regexp").split() if x]
    assert cac, "chưa có commit nào 'C4: ...'"
    for h in cac:
        for f in git("show", "--name-only", "--format=", h).split("\n"):
            f = f.strip()
            if f and not (f.startswith(("sites/unikon/", "bang-chung/C4/")) or f == "features-dot1b.json"):
                raise AssertionError(f"commit C4 {h[:8]} đụng ngoài cấu hình: {f}")


def test_dung_site_bang_cau_hinh():
    d = _site()
    assert (TB / "node_modules").is_dir(), "chạy `npm ci` trong trang-bu trước khi kiểm"
    out = TB / "out"
    shutil.rmtree(out, ignore_errors=True)
    env = {k: v for k, v in os.environ.items() if k != "NOI_DUNG_URL"}
    env.update(SITE_JSON=str(SITE / "site.json"), NEXT_TELEMETRY_DISABLED="1")
    npm = shutil.which("npm") or "npm"
    r = subprocess.run([npm, "run", "build"], cwd=TB, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="ignore", timeout=420)
    assert r.returncode == 0, "dựng tĩnh lỗi:\n" + (r.stdout + r.stderr)[-2000:]
    idx = out / "index.html"
    assert idx.exists()
    tieu_de = d["noi_dung"]["tieu_de"]
    assert tieu_de in idx.read_text(encoding="utf-8"), "trang dựng không chứa tiêu đề từ sites/unikon/site.json"

    from playwright.sync_api import sync_playwright
    s, url = may_chu_web(out)
    ANH.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                pg = b.new_page(viewport={"width": rong, "height": 900})
                ra_ngoai = []
                pg.on("request", lambda rq: ra_ngoai.append(rq.url) if not rq.url.startswith(("http://127.0.0.1", "data:", "blob:")) else None)
                pg.goto(url + "/", wait_until="networkidle")
                pg.screenshot(path=str(ANH / f"c4-{rong}.png"), full_page=True)
                sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                assert sw <= rong, f"tràn ngang ở {rong}px (scrollWidth {sw})"
                assert tieu_de in pg.content()
                assert not ra_ngoai, f"trang tĩnh gọi ra ngoài: {ra_ngoai[:3]}"
                pg.close()
            b.close()
    finally:
        s.shutdown()
