from __future__ import annotations

import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import threading
import uuid

import pytest

from runner import bang_chung, linhx_runner


def _xoa_thu_muc(duong_dan: Path) -> None:
    if not duong_dan.exists():
        return

    def _xu_ly_loi(fn, p, _):
        try:
            os.chmod(p, stat.S_IWRITE)
            fn(p)
        except OSError:
            pass

    shutil.rmtree(duong_dan, onerror=_xu_ly_loi)


@pytest.fixture
def tmp_path():
    goc_viec = linhx_runner.GOC / "viec"
    viec_da_co = goc_viec.exists()
    tm_goc = goc_viec / f"pytest-tmp-bc-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tm_goc.mkdir(parents=True, exist_ok=True)
    try:
        yield tm_goc
    finally:
        _xoa_thu_muc(tm_goc)
        if not viec_da_co and goc_viec.exists():
            try:
                next(goc_viec.iterdir())
            except StopIteration:
                goc_viec.rmdir()


def _kich_thuoc_png(duong_dan: Path) -> tuple[int, int]:
    du_lieu = duong_dan.read_bytes()
    assert du_lieu[:8] == b"\x89PNG\r\n\x1a\n"
    rong, cao = struct.unpack(">II", du_lieu[16:24])
    return int(rong), int(cao)


def _chay_http_cuc_bo(thu_muc_web: Path, ghi_nhan_cuon: list[str] | None = None):
    class BoXuLy(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(thu_muc_web), **kwargs)

        def do_GET(self):
            if self.path.startswith("/__cuon?"):
                if ghi_nhan_cuon is not None:
                    ghi_nhan_cuon.append(self.path)
                self.send_response(204)
                self.end_headers()
                return
            super().do_GET()

        def log_message(self, format, *args):
            return

    may_chu = http.server.ThreadingHTTPServer(("127.0.0.1", 0), BoXuLy)
    luong = threading.Thread(target=may_chu.serve_forever, daemon=True)
    luong.start()
    cong = may_chu.server_address[1]
    return may_chu, f"http://127.0.0.1:{cong}"


def test_cam_file_uri_va_url_khong_hop_le(tmp_path: Path, capsys):
    tep_html = tmp_path / "trang.html"
    tep_html.write_text("<h1> Tĩnh </h1>", encoding="utf-8")

    for url_xau in (
        tep_html.as_uri(),
        "file:///C:/trang.html",
        "FILE://localhost/trang.html",
        "ftp://127.0.0.1/trang.html",
        "javascript:alert(1)",
        "/trang.html",
        "http://",
        "",
    ):
        with pytest.raises(ValueError):
            bang_chung.kiem_tra_url(url_xau)

    tm_ra = tmp_path / "ra-cam"
    ma_thoat = bang_chung.main(["--url", tep_html.as_uri(), "--ra", str(tm_ra)])
    err = capsys.readouterr().err
    assert ma_thoat == 2
    assert "file://" in err.lower()
    assert not (tm_ra / "bang-chung.json").exists()


def test_kho_khong_hop_le_bao_loi(tmp_path: Path, capsys):
    assert bang_chung.phan_tich_kho("iphone, kiosk , desktop,iphone") == [
        "iphone",
        "kiosk",
        "desktop",
    ]
    with pytest.raises(ValueError):
        bang_chung.phan_tich_kho("tablet")
    with pytest.raises(ValueError):
        bang_chung.phan_tich_kho(" , ")

    ma_thoat = bang_chung.main(
        ["--url", "http://127.0.0.1:9999/", "--kho", "tv4k", "--ra", str(tmp_path / "ra")]
    )
    err = capsys.readouterr().err
    assert ma_thoat == 2
    assert "tv4k" in err


def test_bao_thieu_playwright_khi_chua_cai(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)

    with pytest.raises(bang_chung.LoiThieuPlaywright) as exc_info:
        bang_chung._nap_sync_playwright()
    assert "playwright" in str(exc_info.value).lower()

    ma_thoat = bang_chung.main(
        ["--url", "http://127.0.0.1:9999/", "--ra", str(tmp_path / "ra-thieu")]
    )
    err = capsys.readouterr().err
    assert ma_thoat == 3
    assert "playwright" in err.lower()


def test_bao_thieu_chromium_va_phat_hien_anh_chup_trung_bam(tmp_path: Path):
    class _ChromiumThieu:
        def launch(self, headless: bool = True):
            raise RuntimeError("Executable doesn't exist at C:/ms-playwright/chromium")

    class _PWThieu:
        chromium = _ChromiumThieu()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with pytest.raises(bang_chung.LoiThieuPlaywright):
        bang_chung.thu_thap_bang_chung(
            url="http://127.0.0.1:8080/",
            ra=tmp_path / "ra-1",
            kho="iphone",
            sync_playwright_fn=lambda: _PWThieu(),
        )

    # Giả lập 2 khổ xuất ra cùng nội dung PNG -> so_anh_trung bắt được ảnh chụp trùng sha256
    class _TrangGia:
        video = None

        def set_default_timeout(self, ms):
            pass

        def on(self, event, cb):
            pass

        def goto(self, url, **kw):
            pass

        def screenshot(self, path, full_page=True):
            Path(path).write_bytes(b"\x89PNG\r\n\x1a\ncung-mot-anh")

        def evaluate(self, script):
            return 0

        def close(self):
            pass

    class _BoiCanhGia:
        def new_page(self):
            return _TrangGia()

        def close(self):
            pass

    class _TrinhDuyetGia:
        def new_context(self, **kw):
            return _BoiCanhGia()

        def close(self):
            pass

    class _PWGia:
        class _Ch:
            def launch(self, headless=True):
                return _TrinhDuyetGia()

        chromium = _Ch()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    kq = bang_chung.thu_thap_bang_chung(
        url="http://127.0.0.1:8080/",
        ra=tmp_path / "ra-trung-tep",
        kho="iphone,desktop",
        video=False,
        sync_playwright_fn=lambda: _PWGia(),
    )
    assert kq["so_anh_trung"] == 1



def test_cli_chup_3_kho_quay_video_cuon_va_ghi_bang_chung_json(tmp_path: Path):
    pytest.importorskip("playwright.sync_api")

    tm_web = tmp_path / "web"
    tm_ra = tmp_path / "bang-chung"
    tm_web.mkdir()
    (tm_web / "hinh-1.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">'
        '<rect width="120" height="80" fill="#1d4ed8"/></svg>',
        encoding="utf-8",
    )
    (tm_web / "hinh-2.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">'
        '<rect width="120" height="80" fill="#15803d"/></svg>',
        encoding="utf-8",
    )
    (tm_web / "index.html").write_text(
        """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:,">
  <title>Kiểm thử bằng chứng E2E</title>
  <style>
    body { margin: 0; font-family: sans-serif; }
    section { height: 1300px; padding: 24px; box-sizing: border-box; }
    #dau { background: #eff6ff; }
    #cuoi { background: #f0fdf4; }
  </style>
</head>
<body>
  <section id="dau">
    <h1>Khối đầu</h1>
    <img src="/hinh-1.svg" alt="Hình 1">
  </section>
  <section id="cuoi">
    <h2>Khối cuối</h2>
    <img src="/hinh-2.svg" alt="Hình 2">
  </section>
  <script>
    let daBaoCuoi = false;
    window.addEventListener('scroll', () => {
      const day = (window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 20);
      if (day && !daBaoCuoi) {
        daBaoCuoi = true;
        fetch('/__cuon?w=' + window.innerWidth).catch(() => {});
      }
    });
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )

    ghi_cuon: list[str] = []
    may_chu, base_url = _chay_http_cuc_bo(tm_web, ghi_nhan_cuon=ghi_cuon)
    goc_repo = linhx_runner.GOC.parent
    try:
        ket_qua_chay = subprocess.run(
            [
                sys.executable,
                str(goc_repo / "runner" / "bang_chung.py"),
                "--url",
                f"{base_url}/",
                "--kho",
                "iphone,kiosk,desktop",
                "--video",
                "--ra",
                str(tm_ra),
            ],
            cwd=str(goc_repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        assert "bang-chung.json" in ket_qua_chay.stdout
    finally:
        may_chu.shutdown()
        may_chu.server_close()

    tep_json = tm_ra / "bang-chung.json"
    assert tep_json.is_file()
    du_lieu = json.loads(tep_json.read_text(encoding="utf-8"))

    assert du_lieu["url"] == f"{base_url}/"
    assert list(du_lieu["kho"].keys()) == ["iphone", "kiosk", "desktop"]
    assert du_lieu["so_anh_trung"] == 0
    assert du_lieu["loi_console"] == []

    # Kiểm tra kích thước ảnh toàn trang (cao ~2600px > chiều cao khung nhìn) và DPR
    r_ip, c_ip = _kich_thuoc_png(tm_ra / "iphone.png")
    assert r_ip == 390 * 3
    assert c_ip >= 2500 * 3

    r_ki, c_ki = _kich_thuoc_png(tm_ra / "kiosk.png")
    assert r_ki == 1080
    assert c_ki >= 2500

    r_de, c_de = _kich_thuoc_png(tm_ra / "desktop.png")
    assert r_de == 1440
    assert c_de >= 2500

    # Kiểm tra 3 video .webm hợp lệ và đã thực sự cuộn tới cuối trang trên cả 3 khổ
    for ten_kho in ("iphone", "kiosk", "desktop"):
        tep_vid = tm_ra / f"{ten_kho}.webm"
        assert tep_vid.is_file()
        dau_webm = tep_vid.read_bytes()[:4]
        assert dau_webm == b"\x1a\x45\xdf\xa3"
    assert len(ghi_cuon) >= 3

    # Không còn thư mục video tạm nào sót lại
    assert [p.name for p in tm_ra.iterdir() if p.name.startswith(".tmp-video-")] == []

    # Mọi file ảnh + video đều có sha256 khớp thực tế
    assert len(du_lieu["sha256"]) == 6
    for ten_tep, ma_bam in du_lieu["sha256"].items():
        thuc_te = hashlib.sha256((tm_ra / ten_tep).read_bytes()).hexdigest()
        assert ma_bam == thuc_te


def test_ghi_nhan_loi_console_va_anh_trung_khong_video(tmp_path: Path):
    pytest.importorskip("playwright.sync_api")

    tm_web = tmp_path / "web-loi"
    tm_ra = tmp_path / "ra-loi"
    tm_web.mkdir()
    (tm_web / "trung.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">'
        '<circle cx="20" cy="20" r="18" fill="#dc2626"/></svg>',
        encoding="utf-8",
    )
    (tm_web / "index.html").write_text(
        """<!doctype html>
<html lang="vi">
<head><meta charset="utf-8"><link rel="icon" href="data:,"><title>Lỗi</title></head>
<body>
  <img src="/trung.svg" alt="1">
  <img src="/trung.svg" alt="2">
  <script>console.error("loi-console-mau-va3");</script>
</body>
</html>
""",
        encoding="utf-8",
    )

    may_chu, base_url = _chay_http_cuc_bo(tm_web)
    try:
        ket_qua = bang_chung.thu_thap_bang_chung(
            url=f"{base_url}/",
            ra=tm_ra,
            kho="desktop",
            video=False,
        )
    finally:
        may_chu.shutdown()
        may_chu.server_close()

    assert (tm_ra / "desktop.png").is_file()
    assert not (tm_ra / "desktop.webm").exists()
    assert ket_qua["kho"]["desktop"]["video"] is None
    assert ket_qua["so_anh_trung"] == 1
    assert any("loi-console-mau-va3" in dong for dong in ket_qua["loi_console"])
