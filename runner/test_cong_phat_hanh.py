"""Kiểm thử cổng phát hành `runner/cong_phat_hanh.py` bằng HTTP cục bộ (không conftest, không mạng ngoài)."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading

import pytest

RUNNER_DIR = Path(__file__).resolve().parent
REPO_ROOT = RUNNER_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runner import cong_phat_hanh  # noqa: E402

TZ_VN = timezone(timedelta(hours=7))


@contextmanager
def _may_chu_gia(phan_hoi_fn):
    """Dựng HTTP server cục bộ trên 127.0.0.1:0 và ghi lại mọi request nhận được."""
    nhat_ky: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def _xu_ly(self):
            nhat_ky.append(
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": dict(self.headers.items()),
                }
            )
            status, headers, body = phan_hoi_fn(self.command, self.path, self.headers)
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            if isinstance(body, str):
                body = body.encode("utf-8")
            if body:
                self.wfile.write(body)

        def do_GET(self):
            self._xu_ly()

        def do_POST(self):
            self._xu_ly()

        def do_PUT(self):
            self._xu_ly()

        def do_DELETE(self):
            self._xu_ly()

        def do_HEAD(self):
            self._xu_ly()

        def log_message(self, _fmt, *_args):
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    luong = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    luong.start()
    try:
        host, port = httpd.server_address[:2]
        yield f"http://{host}:{port}", nhat_ky
    finally:
        httpd.shutdown()
        httpd.server_close()
        luong.join(timeout=2.0)


def test_thanh_cong_get_healthz_khop_build_sha():
    def tra_loi(method, path, _headers):
        if method == "GET" and path == "/healthz":
            return (
                200,
                {"Content-Type": "application/json; charset=utf-8"},
                json.dumps({"ok": True, "app": "event-stg", "BUILD_SHA": "9f8e7d6c"}),
            )
        return 404, {"Content-Type": "text/plain"}, "not found"

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        gio_hop_le = datetime(2026, 11, 15, 10, 30, 0, tzinfo=TZ_VN)
        kq = cong_phat_hanh.kiem_cong_phat_hanh(
            base=base_url + "/",
            sha="9f8e7d6c",
            prod=["ifagent.net", "event.ifagent.net"],
            now=gio_hop_le,
        )
        assert kq.dat is True
        assert kq.ma_thoat == 0
        assert kq.build_sha == "9f8e7d6c"
        assert len(nhat_ky) == 1
        assert nhat_ky[0]["method"] == "GET"
        assert nhat_ky[0]["path"] == "/healthz"


def test_sai_hoac_thieu_build_sha_va_loi_http():
    kich_ban = [
        (200, json.dumps({"ok": True, "BUILD_SHA": "sha-cu-111"}), "BUILD_SHA"),
        (200, json.dumps({"ok": True, "version": "1.0.0"}), "BUILD_SHA"),
        (200, json.dumps({"ok": False, "BUILD_SHA": "sha-moi-222"}), "BUILD_SHA"),
        (503, json.dumps({"ok": False, "BUILD_SHA": "sha-moi-222"}), "HTTP_STATUS"),
    ]
    chi_so = [0]

    def tra_loi(_method, _path, _headers):
        code, payload, _ = kich_ban[chi_so[0]]
        return code, {"Content-Type": "application/json"}, payload

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        gio = datetime(2026, 11, 15, 15, 0, 0, tzinfo=TZ_VN)
        for idx, (_, _, loai_ky_vong) in enumerate(kich_ban):
            chi_so[0] = idx
            kq = cong_phat_hanh.kiem_cong_phat_hanh(
                base=base_url,
                sha="sha-moi-222",
                prod=["prod.example.com"],
                now=gio,
            )
            assert kq.dat is False
            assert kq.ma_thoat != 0
            assert kq.loai_loi == loai_ky_vong
        assert len(nhat_ky) == len(kich_ban)
        assert all(r["method"] == "GET" for r in nhat_ky)


def test_chan_ten_mien_prod_khong_goi_http_va_khong_chan_nham_staging():
    def tra_loi(_method, _path, _headers):
        return 200, {"Content-Type": "application/json"}, json.dumps({"ok": True, "BUILD_SHA": "abc1234"})

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        gio = datetime(2026, 11, 15, 11, 0, 0, tzinfo=TZ_VN)
        # Chặn trực tiếp khi --base trùng tên miền trong --prod (không gửi bất kỳ gói HTTP nào)
        kq_local_prod = cong_phat_hanh.kiem_cong_phat_hanh(
            base=base_url,
            sha="abc1234",
            prod="ifagent.net, 127.0.0.1; demo.ifagent.net",
            now=gio,
        )
        assert kq_local_prod.dat is False
        assert kq_local_prod.loai_loi == "PROD"
        assert nhat_ky == []

        # Chặn tên miền prod kể cả khác hoa/thường, có cổng, hoặc truyền dạng URL trong --prod
        kq_prod_url = cong_phat_hanh.kiem_cong_phat_hanh(
            base="https://EVENT.IFAGENT.NET:8443/app",
            sha="abc1234",
            prod=["https://event.ifagent.net/", "ifagent.net"],
            now=gio,
        )
        assert kq_prod_url.dat is False
        assert kq_prod_url.loai_loi == "PROD"

        # Không chặn nhầm staging-event.ifagent.net khi --prod chỉ liệt kê ifagent.net, event.ifagent.net
        assert cong_phat_hanh.trung_ten_mien_prod(
            "staging-event.ifagent.net",
            cong_phat_hanh.tach_danh_sach_prod(["ifagent.net", "event.ifagent.net"]),
        ) is None

    # Chặn cả trường hợp staging trả redirect 302 trỏ về tên miền prod
    def tra_redirect(_method, _path, _headers):
        return 302, {"Location": "https://event.ifagent.net/healthz"}, ""

    with _may_chu_gia(tra_redirect) as (base_stg, nhat_ky_redir):
        kq_redir = cong_phat_hanh.kiem_cong_phat_hanh(
            base=base_stg,
            sha="abc1234",
            prod=["event.ifagent.net"],
            now=datetime(2026, 11, 15, 11, 0, 0, tzinfo=TZ_VN),
        )
        assert kq_redir.dat is False
        assert kq_redir.loai_loi == "PROD"
        assert len(nhat_ky_redir) == 1
        assert nhat_ky_redir[0]["method"] == "GET"


@pytest.mark.parametrize(
    "gio_kiem,cho_phep",
    [
        (datetime(2026, 11, 15, 6, 59, 59, tzinfo=TZ_VN), False),
        (datetime(2026, 11, 15, 0, 30, 0, tzinfo=TZ_VN), False),
        (datetime(2026, 11, 15, 22, 1, 0, tzinfo=TZ_VN), False),
        (datetime(2026, 11, 15, 23, 0, 0, tzinfo=TZ_VN), False),
        # Múi giờ UTC quy đổi sang giờ VN: 16:15 UTC = 23:15 VN (chặn), 23:30 UTC = 06:30 VN (chặn)
        (datetime(2026, 11, 15, 16, 15, 0, tzinfo=timezone.utc), False),
        (datetime(2026, 11, 14, 23, 30, 0, tzinfo=timezone.utc), False),
        # Biên hợp lệ trong khung 07:00 - 22:00 giờ VN
        (datetime(2026, 11, 15, 7, 0, 0, tzinfo=TZ_VN), True),
        (datetime(2026, 11, 15, 14, 30, 0, tzinfo=TZ_VN), True),
        (datetime(2026, 11, 15, 22, 0, 0, tzinfo=TZ_VN), True),
    ],
)
def test_chan_gio_vn_ngoai_khung_7h_22h(gio_kiem: datetime, cho_phep: bool):
    def tra_loi(_method, _path, _headers):
        return 200, {"Content-Type": "application/json"}, json.dumps({"BUILD_SHA": "c0ffee12"})

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        kq = cong_phat_hanh.kiem_cong_phat_hanh(
            base=base_url,
            sha="c0ffee12",
            prod=["prod.ifagent.net"],
            now=gio_kiem,
        )
        assert kq.dat is cho_phep
        if cho_phep:
            assert kq.ma_thoat == 0
            assert len(nhat_ky) == 1
        else:
            assert kq.ma_thoat != 0
            assert kq.loai_loi == "GIO_VN"
            assert nhat_ky == []


def test_chi_dung_get_va_chan_scheme_khong_an_toan():
    def tra_loi(_method, _path, _headers):
        return 200, {"Content-Type": "application/json"}, json.dumps({"BUILD_SHA": "11223344"})

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        gio = datetime(2026, 11, 15, 9, 0, 0, tzinfo=TZ_VN)
        for phuong_thuc in ("POST", "PUT", "DELETE", "PATCH", "HEAD"):
            kq = cong_phat_hanh.kiem_cong_phat_hanh(
                base=base_url,
                sha="11223344",
                now=gio,
                method=phuong_thuc,
            )
            assert kq.dat is False
            assert kq.loai_loi == "PHUONG_THUC"
        assert nhat_ky == []

        kq_file = cong_phat_hanh.kiem_cong_phat_hanh(
            base="file:///etc/passwd",
            sha="11223344",
            now=gio,
        )
        assert kq_file.dat is False
        assert kq_file.loai_loi == "THAM_SO"


def test_cli_cong_phat_hanh_truoc_sau_va_chan():
    def tra_loi(_method, _path, _headers):
        return 200, {"Content-Type": "application/json"}, json.dumps({"ok": True, "BUILD_SHA": "778899aa"})

    with _may_chu_gia(tra_loi) as (base_url, nhat_ky):
        script = str(RUNNER_DIR / "cong_phat_hanh.py")
        # 1. Chế độ --truoc (ghi nhận SHA hiện tại trước khi deploy để ghi lệnh rollback)
        p_truoc = subprocess.run(
            [sys.executable, script, "--base", base_url, "--truoc", "--prod", "ifagent.net", "--now", "10:15"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert p_truoc.returncode == 0, p_truoc.stderr
        assert "778899aa" in p_truoc.stdout

        # 2. Chế độ kiểm sau deploy khớp --sha
        p_sau = subprocess.run(
            [
                sys.executable,
                script,
                "--base",
                base_url,
                "--sha",
                "778899aa",
                "--prod",
                "ifagent.net",
                "--prod",
                "event.ifagent.net",
                "--now",
                "10:20",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert p_sau.returncode == 0, p_sau.stderr
        assert "778899aa" in p_sau.stdout

        # 3. Chặn giờ đêm (> 22h VN) qua CLI
        p_dem = subprocess.run(
            [sys.executable, script, "--base", base_url, "--sha", "778899aa", "--now", "22:30"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert p_dem.returncode != 0
        assert "22:00" in p_dem.stderr or "GIO_VN" in p_dem.stderr

        assert len(nhat_ky) == 2
        assert all(r["method"] == "GET" for r in nhat_ky)


def test_khuon_phieu_va_muc_phat_hanh_trong_skill():
    phieu_mau = (RUNNER_DIR / "phieu-mau" / "deploy-staging.md").read_text(encoding="utf-8")
    assert "cong_phat_hanh.py" in phieu_mau
    assert "rollback" in phieu_mau.lower()
    assert "CAN-LINH:" in phieu_mau

    skill_md = (REPO_ROOT / "skills" / "le" / "hang-doi-may" / "SKILL.md").read_text(encoding="utf-8")
    assert "## Phát hành" in skill_md
    assert "cong_phat_hanh.py" in skill_md
    assert "rollback" in skill_md.lower()
    assert "CAN-LINH" in skill_md

