"""Unit test cho module booking (F2): dat_lich, LXLichGoi và api_booking."""
from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import patch

import pytest

from linhx_core.booking import dat_lich


def test_dat_lich_gio_lam_viec_va_mui_gio():
    # Đúng biên 08:00 -> 08:30 và 17:30 -> 18:00
    ds = dat_lich.dat_lich(
        [],
        {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 08:00:00", "phut": 30},
    )
    assert len(ds) == 1
    assert ds[0]["ket_thuc"] == "2026-11-10 08:30:00"
    assert ds[0]["trang_thai"] == "cho_goi"

    # Chuỗi UTC tương đương 09:00 giờ VN (02:00Z) được quy đổi đúng về giờ VN
    ds = dat_lich.dat_lich(
        ds,
        {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10T02:00:00Z", "phut": 30},
    )
    assert ds[-1]["bat_dau"] == "2026-11-10 09:00:00"
    assert ds[-1]["ket_thuc"] == "2026-11-10 09:30:00"

    # Ngoài giờ làm hoặc dữ liệu sai -> ValueError
    for gio_sai in (
        "2026-11-10 07:59:59",
        "2026-11-10 17:31:00",
        "2026-11-10 18:00:00",
        "2026-11-10",
        "",
    ):
        with pytest.raises(ValueError):
            dat_lich.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": gio_sai, "phut": 30},
            )

    for phut_sai in (0, -15, 601, True, "abc"):
        with pytest.raises(ValueError):
            dat_lich.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 09:00:00", "phut": phut_sai},
            )


def test_dat_lich_trung_gio_va_lich_huy():
    goc = [
        {
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 10:00:00",
            "ket_thuc": "2026-11-10 10:30:00",
            "phut": 30,
            "trang_thai": "cho_goi",
        },
        {
            "nguoi": "NG-02",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 11:00:00",
            "ket_thuc": "2026-11-10 11:30:00",
            "phut": 30,
            "trang_thai": "huy",
        },
    ]
    # Trùng với lịch đang cho_goi (10:00 - 10:30) -> chặn
    with pytest.raises(ValueError):
        dat_lich.dat_lich(
            goc,
            {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 10:15:00", "phut": 30},
        )

    # Trùng với lịch đã huỷ (11:00 - 11:30) -> được phép
    moi = dat_lich.dat_lich(
        goc,
        {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 11:00:00", "phut": 30},
    )
    assert len(goc) == 2, "không được sửa danh sách đầu vào"
    assert len(moi) == 3

    # viec_cho chỉ lấy cho_goi và xếp bat_dau tăng dần
    vc = dat_lich.viec_cho(moi, phu_trach="sale1@vd.vn")
    assert [x["nguoi"] for x in vc] == ["NG-01", "NG-03"]


def test_api_booking_va_controller_voi_mock_frappe():
    class FakeValidationError(ValueError):
        pass

    class FakePermissionError(PermissionError):
        pass

    kho_lich: list[dict] = []
    kho_nguoi: dict[str, dict] = {
        "NG-01": {
            "name": "NG-01",
            "ho_ten": "Khách Một",
            "dien_thoai": "0912345678",
            "email": "khach1@vd.vn",
            "don_vi": "DV-A",
        },
        "NG-02": {
            "name": "NG-02",
            "ho_ten": "Khách Hai",
            "dien_thoai": "0988777666",
            "email": "khach2@vd.vn",
            "don_vi": "DV-B",
        },
    }
    kho_co_hoi: list[dict] = [
        {
            "name": "CH-01",
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "don_vi": "DV-A",
            "trang_thai": "moi",
            "creation": "2026-11-10 08:00:00",
        },
        {
            "name": "CH-02",
            "nguoi": "NG-02",
            "phu_trach": "sale2@vd.vn",
            "don_vi": "DV-B",
            "trang_thai": "moi",
            "creation": "2026-11-10 08:05:00",
        },
    ]
    kho_dong_y: list[dict] = [
        {
            "name": "DY-01",
            "nguoi": "NG-01",
            "muc_dich": "lien_he",
            "dong_y": 1,
            "luc": "2026-11-10 08:00:00",
            "nguon": "trang-ifagent",
        }
    ]

    class FakeDoc:
        def __init__(self, d: dict):
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            for k, v in d.items():
                setattr(self, k, v)

        def save(self, ignore_permissions: bool = False):
            return self

        def insert(self, ignore_permissions: bool = False):
            if getattr(self, "doctype", "") == "LX Lich Goi":
                self.name = f"LG-{len(kho_lich) + 1:03d}"
                kho_lich.append(
                    {
                        "name": self.name,
                        "nguoi": self.nguoi,
                        "co_hoi": getattr(self, "co_hoi", ""),
                        "phu_trach": self.phu_trach,
                        "don_vi": getattr(self, "don_vi", ""),
                        "bat_dau": self.bat_dau,
                        "ket_thuc": self.ket_thuc,
                        "phut": self.phut,
                        "trang_thai": self.trang_thai,
                        "ghi_chu": getattr(self, "ghi_chu", ""),
                    }
                )
            elif getattr(self, "doctype", "") == "LX Co Hoi":
                self.name = f"CH-{len(kho_co_hoi) + 1:02d}"
            return self

    def fake_throw(msg, exc=FakeValidationError):
        if isinstance(exc, type) and issubclass(exc, BaseException):
            raise exc(msg)
        raise FakeValidationError(msg)

    def fake_get_all(doctype, filters=None, fields=None, or_filters=None, order_by=None, limit=None, pluck=None, **kwargs):
        if doctype == "LX Lich Goi":
            pt = (filters or {}).get("phu_trach")
            kq = [dict(x) for x in kho_lich if (not pt or x.get("phu_trach") == pt) and x.get("trang_thai") != "huy"]
            return kq
        if doctype == "LX Co Hoi":
            ng = (filters or {}).get("nguoi")
            ten_ch = (filters or {}).get("name")
            return [
                dict(x)
                for x in kho_co_hoi
                if (not ng or x.get("nguoi") == ng) and (not ten_ch or x.get("name") == ten_ch)
            ]
        if doctype == "LX Dong Y":
            ng = (filters or {}).get("nguoi")
            if isinstance(ng, (list, tuple)) and len(ng) == 2 and ng[0] == "in":
                ds_ng = set(ng[1])
                return [dict(x) for x in kho_dong_y if x.get("nguoi") in ds_ng]
            return [dict(x) for x in kho_dong_y if not ng or x.get("nguoi") == ng]
        if doctype == "LX Nguoi":
            return [dict(v) for v in kho_nguoi.values()]
        if doctype == "User Permission":
            user_f = (filters or {}).get("user")
            if user_f == "sale1@vd.vn":
                return ["DV-A"] if pluck else [{"user": "sale1@vd.vn", "for_value": "DV-A"}]
            if user_f == "sale2@vd.vn":
                return ["DV-B"] if pluck else [{"user": "sale2@vd.vn", "for_value": "DV-B"}]
            return []
        return []

    def fake_get_value(doctype, name, fieldname, as_dict=False):
        if doctype == "LX Nguoi" and name in kho_nguoi:
            ng = kho_nguoi[name]
            if as_dict:
                return dict(ng)
            return ng.get(fieldname)
        if doctype == "LX Co Hoi":
            for ch in kho_co_hoi:
                if ch["name"] == name:
                    if as_dict:
                        return dict(ch)
                    return ch.get(fieldname)
            return None
        if doctype == "User":
            if as_dict:
                return {"name": name, "enabled": 1, "user_type": "System User"}
            return 1
        return None

    fake_frappe = types.ModuleType("frappe")
    fake_frappe.ValidationError = FakeValidationError
    fake_frappe.PermissionError = FakePermissionError
    fake_frappe.DuplicateEntryError = RuntimeError
    fake_frappe.throw = fake_throw
    fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
    fake_frappe.get_all = fake_get_all
    fake_frappe.get_doc = lambda arg1, arg2=None: (
        FakeDoc(kho_nguoi[arg2]) if arg1 == "LX Nguoi" and arg2 in kho_nguoi else FakeDoc(arg1 if isinstance(arg1, dict) else {})
    )
    fake_frappe.local = types.SimpleNamespace(
        site="ifagent",
        request_ip="127.0.0.1",
        request=types.SimpleNamespace(
            method="POST",
            headers={},
            content_length=120,
            get_data=lambda **kw: b"{}",
            get_json=lambda **kw: None,
        ),
        form_dict={},
        response={},
        _lx_cau_hinh_cache={"bat_crm": 1, "bat_pay": 1},
    )
    fake_frappe.session = types.SimpleNamespace(user="Guest")
    fake_frappe.db = types.SimpleNamespace(
        get_value=fake_get_value,
        exists=lambda dt, n: n in kho_nguoi if dt == "LX Nguoi" else True,
        sql=None,
    )
    fake_frappe.cache = lambda: None

    fake_rl = types.ModuleType("frappe.rate_limiter")
    fake_rl.rate_limit = lambda **kw: (lambda fn: fn)
    fake_model = types.ModuleType("frappe.model")
    fake_doc_mod = types.ModuleType("frappe.model.document")

    class BaseDocument:
        def __init__(self, d=None):
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            for k, v in (d or {}).items():
                setattr(self, k, v)

    fake_doc_mod.Document = BaseDocument

    with patch.dict(
        sys.modules,
        {
            "frappe": fake_frappe,
            "frappe.rate_limiter": fake_rl,
            "frappe.model": fake_model,
            "frappe.model.document": fake_doc_mod,
        },
    ):
        try:
            for mod_name in (
                "linhx_core.crm.api_form",
                "linhx_core.booking.doctype.lx_lich_goi.lx_lich_goi",
                "linhx_core.booking.api_booking",
            ):
                sys.modules.pop(mod_name, None)
            api_booking = importlib.import_module("linhx_core.booking.api_booking")

            # 1. Đặt lịch hợp lệ có kênh liên hệ khớp hồ sơ -> tự lấy phu_trach từ CH-01 (sale1@vd.vn)
            kq1 = api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                bat_dau="2026-11-10 09:00:00",
                phut=30,
                ghi_chu="Tư vấn Agent Force",
                dong_y_lien_he=True,
            )
            assert kq1["ok"] is True
            assert kq1["phu_trach"] == "sale1@vd.vn"
            assert kq1["co_hoi"] == "CH-01"
            assert kq1["bat_dau"] == "2026-11-10 09:00:00"
            assert kq1["ket_thuc"] == "2026-11-10 09:30:00"

            # 2. Đặt trùng giờ -> bị chặn với 409
            with pytest.raises(FakeValidationError):
                api_booking.dat_lich_goi(
                    nguoi="NG-01",
                    dien_thoai="0912345678",
                    phu_trach="sale1@vd.vn",
                    bat_dau="2026-11-10 09:15:00",
                    phut=30,
                    dong_y_lien_he=True,
                )
            assert fake_frappe.local.response.get("http_status_code") == 409

            # 3. Ngoài giờ làm (18:00) -> bị chặn với 400
            with pytest.raises(FakeValidationError):
                api_booking.dat_lich_goi(
                    nguoi="NG-01",
                    dien_thoai="0912345678",
                    phu_trach="sale1@vd.vn",
                    bat_dau="2026-11-10 18:00:00",
                    phut=30,
                    dong_y_lien_he=True,
                )
            assert fake_frappe.local.response.get("http_status_code") == 400

            # 4. Người phụ trách đăng nhập xem viec_cho_lich_goi -> thấy lịch
            fake_frappe.session.user = "sale1@vd.vn"
            ds_vc = api_booking.viec_cho_lich_goi()
            assert len(ds_vc) == 1
            assert ds_vc[0]["nguoi"] == "NG-01"
            assert ds_vc[0]["phu_trach"] == "sale1@vd.vn"

            # 5. Nhân viên khác không được xem lịch của sale1@vd.vn
            fake_frappe.session.user = "sale2@vd.vn"
            with pytest.raises(FakePermissionError):
                api_booking.viec_cho_lich_goi(phu_trach="sale1@vd.vn")

            # 6. Mã nguoi trơn (không SĐT/email) hoặc mã nguoi kèm email không khớp hồ sơ -> bị chặn 400
            fake_frappe.session.user = "Guest"
            with pytest.raises(FakeValidationError):
                api_booking.dat_lich_goi(
                    nguoi="NG-01",
                    bat_dau="2026-11-10 15:00:00",
                    phut=30,
                )
            assert fake_frappe.local.response.get("http_status_code") == 400

            with pytest.raises(FakeValidationError):
                api_booking.dat_lich_goi(
                    nguoi="NG-01",
                    email="ke_la@vd.vn",
                    bat_dau="2026-11-10 15:00:00",
                    phut=30,
                    dong_y_lien_he=True,
                )
            assert fake_frappe.local.response.get("http_status_code") == 400

            with pytest.raises(FakeValidationError):
                api_booking.dat_lich_goi(
                    nguoi="NG-KHONG-TON-TAI",
                    dien_thoai="0912345678",
                    bat_dau="2026-11-10 15:00:00",
                    phut=30,
                    dong_y_lien_he=True,
                )
            assert fake_frappe.local.response.get("http_status_code") == 400

            # 7. Khách gửi co_hoi của người khác (CH-02) và phu_trach của đơn vị khác (sale2@vd.vn) -> bị bỏ qua, giữ CH-01 & sale1@vd.vn
            kq2 = api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                co_hoi="CH-02",
                phu_trach="sale2@vd.vn",
                bat_dau="2026-11-10 10:00:00",
                phut=30,
                dong_y_lien_he=True,
            )
            assert kq2["co_hoi"] == "CH-01"
            assert kq2["phu_trach"] == "sale1@vd.vn"
            assert kho_lich[-1]["don_vi"] == "DV-A"

            # 8. Controller LXLichGoi kiểm tra quyền đơn vị, chặn trùng giờ và chặn co_hoi khác người
            mod_lg = importlib.import_module("linhx_core.booking.doctype.lx_lich_goi.lx_lich_goi")
            fake_frappe.session.user = "sale1@vd.vn"
            doc_hop_le = mod_lg.LXLichGoi(
                {
                    "nguoi": "NG-01",
                    "phu_trach": "sale1@vd.vn",
                    "bat_dau": "2026-11-10 14:00:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            doc_hop_le.before_insert()
            assert doc_hop_le.don_vi == "DV-A"
            assert doc_hop_le.ket_thuc == "2026-11-10 14:30:00"
            assert doc_hop_le.has_permission("read", user="sale1@vd.vn") is True
            assert doc_hop_le.has_permission("read", user="sale2@vd.vn") is False

            doc_sai_co_hoi = mod_lg.LXLichGoi(
                {
                    "nguoi": "NG-01",
                    "co_hoi": "CH-02",
                    "phu_trach": "sale1@vd.vn",
                    "bat_dau": "2026-11-10 15:00:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            with pytest.raises(FakeValidationError):
                doc_sai_co_hoi.before_insert()
        finally:
            for mod_name in (
                "linhx_core.booking.api_booking",
                "linhx_core.booking.doctype.lx_lich_goi.lx_lich_goi",
                "linhx_core.crm.api_form",
            ):
                sys.modules.pop(mod_name, None)
            import linhx_core.booking as pkg_booking
            import linhx_core.crm as pkg_crm

            for attr in ("api_booking", "doctype"):
                if hasattr(pkg_booking, attr):
                    delattr(pkg_booking, attr)
            if hasattr(pkg_crm, "api_form"):
                delattr(pkg_crm, "api_form")


def test_trang_bu_form_dat_lich_cau_truc():
    from pathlib import Path

    goc = Path(__file__).resolve().parents[4]
    idx = (goc / "trang-bu" / "pages" / "index.js").read_text(encoding="utf-8")
    assert "data-dat-lich" in idx
    assert "/api/method/linhx_core.booking.api_booking.dat_lich_goi" in idx
    assert 'name="bat_dau"' in idx
    assert "data-dat-lich-thanh-cong" in idx


def test_playwright_form_dat_lich_trang_bu():
    import functools
    import http.server
    import json
    import os
    from pathlib import Path
    import shutil
    import subprocess
    import threading
    from urllib.parse import urlparse

    from playwright.sync_api import sync_playwright

    goc = Path(__file__).resolve().parents[4]
    tb = goc / "trang-bu"
    out = tb / "out"
    idx_html = out / "index.html"
    can_dung = (
        not idx_html.exists()
        or "data-dat-lich" not in idx_html.read_text(encoding="utf-8", errors="ignore")
        or '"apiGoc":"http' in idx_html.read_text(encoding="utf-8", errors="ignore")
    )
    if can_dung:
        shutil.rmtree(out, ignore_errors=True)
        env = {k: v for k, v in os.environ.items() if k not in ("NOI_DUNG_URL", "SITE_JSON", "API_GOC")}
        env["NEXT_TELEMETRY_DISABLED"] = "1"
        npm = shutil.which("npm") or "npm"
        r = subprocess.run(
            [npm, "run", "build"],
            cwd=tb,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=420,
        )
        assert r.returncode == 0, "dựng tĩnh trang-bu lỗi"

    ghi_nhan: list[tuple[str, str, dict]] = []
    url_api = "/api/method/linhx_core.booking.api_booking.dat_lich_goi"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            duong = urlparse(self.path).path
            if duong == url_api:
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b"{}"
                than = json.loads(raw.decode("utf-8"))
                ghi_nhan.append(("POST", duong, than))
                b = json.dumps({"message": {"ok": True, "lich": "LG-001", "trang_thai": "cho_goi"}}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
                return
            self.send_error(404)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(out)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url_goc = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rong in (390, 1280):
                ghi_nhan.clear()
                pg = b.new_page(viewport={"width": rong, "height": 900})
                pg.goto(url_goc + "/", wait_until="networkidle")
                f = pg.locator("form[data-dat-lich]")
                assert f.count() == 1
                f.locator('[name="ho_ten"]').fill("Trần Văn Đặt")
                f.locator('[name="dien_thoai"]').fill("0912888999")
                f.locator('[name="phu_trach"]').fill("sale1@vd.vn")
                f.locator('[name="bat_dau"]').fill("2026-11-10 09:00:00")
                f.locator('[name="phut"]').fill("30")
                f.locator('[name="ghi_chu"]').fill("Trao đổi triển khai Pilot")
                f.locator('button, [type="submit"]').first.click()
                pg.wait_for_selector("[data-dat-lich-thanh-cong]", state="visible", timeout=10000)
                assert len(ghi_nhan) == 1
                than_gui = ghi_nhan[0][2]
                assert than_gui["dien_thoai"] == "0912888999"
                assert than_gui["phu_trach"] == "sale1@vd.vn"
                assert than_gui["bat_dau"] == "2026-11-10 09:00:00"
                assert than_gui["phut"] == 30
                sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                assert sw <= rong, f"tràn ngang ở {rong}px"
                pg.close()
            b.close()
    finally:
        srv.shutdown()


