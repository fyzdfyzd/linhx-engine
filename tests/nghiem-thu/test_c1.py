"""C1: khuôn Next.js Trang BU từ demo ifAgent, đọc nội dung từ API bản cài. Dựng tĩnh được, chụp 390 và 1280 không tràn ngang.

Hợp đồng (HOP-DONG.md):
- linhx-engine/trang-bu/: package.json có next, script "build" dựng tĩnh ra trang-bu/out/ (output: "export")
- Lúc dựng đọc nội dung từ URL ở biến môi trường NOI_DUNG_URL (API bản cài), JSON dạng
    {"tieu_de": str, "mo_ta": str, "muc": [{"ten": str, "mo_ta": str}]}
  thiếu biến thì dùng trang-bu/noi-dung.mau.json
- node_modules cài sẵn bằng `npm ci` trong trang-bu (test không cài, không ra mạng)
Test mở API giả ở 127.0.0.1, dựng, rồi chụp trang tĩnh bằng Playwright ở bề rộng 390 và 1280.
"""
import functools
import http.server
import json
import os
import shutil
import subprocess
import threading

from _chung import GOC

TB = GOC / "trang-bu"
DAU = "MOC-KIEM-C1-7f3a"


def _may_chu(thu_muc=None, json_tra=None):
    if json_tra is not None:
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                b = json.dumps(json_tra, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

            def log_message(self, *a):
                pass
        lop = H
    else:
        class Im(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        lop = functools.partial(Im, directory=str(thu_muc))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), lop)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"


def test_khuon_next():
    pj = TB / "package.json"
    assert pj.exists(), "thiếu trang-bu/package.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    assert "next" in {**d.get("dependencies", {}), **d.get("devDependencies", {})}, "trang-bu phải dùng Next.js"
    assert "build" in d.get("scripts", {})
    assert (TB / "noi-dung.mau.json").exists(), "thiếu trang-bu/noi-dung.mau.json"
    assert (TB / "node_modules").is_dir(), "chạy `npm ci` trong trang-bu trước khi kiểm"


def test_dung_tinh_doc_api_va_khong_tran_ngang(tmp_path):
    api, url = _may_chu(json_tra={"tieu_de": f"Trang BU {DAU}", "mo_ta": "Mô tả thử",
                                   "muc": [{"ten": "Mục một", "mo_ta": "Nội dung mục một"}]})
    try:
        out = TB / "out"
        shutil.rmtree(out, ignore_errors=True)
        env = dict(os.environ, NOI_DUNG_URL=url, NEXT_TELEMETRY_DISABLED="1")
        npm = shutil.which("npm") or "npm"
        r = subprocess.run([npm, "run", "build"], cwd=TB, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="ignore", timeout=420)
        assert r.returncode == 0, "dựng tĩnh lỗi:\n" + (r.stdout + r.stderr)[-2000:]
    finally:
        api.shutdown()
    idx = out / "index.html"
    assert idx.exists(), "dựng xong phải có trang-bu/out/index.html"
    assert DAU in idx.read_text(encoding="utf-8"), "trang dựng không chứa nội dung lấy từ NOI_DUNG_URL"

    from playwright.sync_api import sync_playwright
    web, wurl = _may_chu(thu_muc=out)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                pg = b.new_page(viewport={"width": rong, "height": 900})
                ra_ngoai = []
                pg.on("request", lambda rq: ra_ngoai.append(rq.url) if not rq.url.startswith(("http://127.0.0.1", "data:", "blob:")) else None)
                pg.goto(wurl + "/", wait_until="networkidle")
                pg.screenshot(path=str(tmp_path / f"c1-{rong}.png"), full_page=True)
                sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                assert sw <= rong, f"tràn ngang ở {rong}px (scrollWidth {sw})"
                assert DAU in pg.content()
                assert not ra_ngoai, f"trang tĩnh gọi ra ngoài: {ra_ngoai[:3]}"
                pg.close()
            b.close()
    finally:
        web.shutdown()
