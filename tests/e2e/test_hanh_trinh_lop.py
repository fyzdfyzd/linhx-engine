"""E2E hanh trinh 3 lop (T4): lead BU -> LX Nguoi -> don bao_cao -> SePay -> LX Su Kien xong -> bao cao."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360f8cfc0f01f0005000201e2b2a3f40000000049454e44ae426082"
)
RONG_MAN_HINH = (390, 1280)
_KET_QUA_RONG: list[int] = []
_SU_KIEN_TRANG_THAI: list[str] = []
_CHI_TIET_CHAY: list[dict] = []


def _url_linhx() -> str:
    url = os.environ.get("E2E_LINHX_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("Can dat E2E_LINHX_URL de chay E2E hanh trinh 3 lop")
    return url


def _url_bu(url_linhx: str) -> str:
    bu = os.environ.get("E2E_BU_URL", "").strip().rstrip("/")
    if bu:
        return bu
    host = urllib.parse.urlparse(url_linhx).hostname or ""
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        ip_gach = host.replace(".", "-")
        return f"http://sakedemy.{ip_gach}.nip.io"
    return url_linhx


def _khoa_sepay() -> str:
    khoa = (
        os.environ.get("E2E_SEPAY_KHOA", "").strip()
        or os.environ.get("SEPAY_WEBHOOK_KEY", "").strip()
    )
    if not khoa:
        raise RuntimeError("Can dat E2E_SEPAY_KHOA de gia lap webhook SePay")
    return khoa


def _tai_khoan_van_hanh() -> tuple[str, str]:
    user = (
        os.environ.get("E2E_USER", "").strip()
        or os.environ.get("LINH_EMAIL", "").strip()
        or "Administrator"
    )
    pwd = (
        os.environ.get("E2E_AUTH_SECRET", "").strip()
        or os.environ.get("LINH_MAT_KHAU", "").strip()
        or os.environ.get("ADMIN_PASSWORD", "").strip()
    )
    if not pwd:
        raise RuntimeError("Can dat E2E_AUTH_SECRET de xac minh LX Nguoi / LX Su Kien / LX Job")
    return user, pwd


def _goi_webhook_sepay(
    url_linhx: str, khoa: str, noi_dung_ck: str, so_tien: int, ma_gd: str
) -> tuple[int, dict]:
    url = f"{url_linhx}/api/method/linhx_vn.pay.api_sepay.webhook"
    than = json.dumps(
        {
            "id": ma_gd,
            "transferType": "in",
            "transferAmount": so_tien,
            "content": f"MBVCB.99999.{noi_dung_ck}.CT tu 0123456789",
            "code": noi_dung_ck,
            "referenceCode": f"FT{ma_gd}",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=than,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Apikey {khoa}",
            "Referer": f"{url_linhx}/",
            "User-Agent": "LINHX-E2E-T4/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return resp.status, data.get("message") or data


class _PhienFrappe:
    def __init__(self, url_goc: str, user: str, pwd: str) -> None:
        self.url_goc = url_goc
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        than_login = urllib.parse.urlencode({"usr": user, "pwd": pwd}).encode("utf-8")
        req = urllib.request.Request(
            f"{url_goc}/api/method/login",
            data=than_login,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"{url_goc}/",
            },
        )
        with self.opener.open(req, timeout=20) as resp:
            assert resp.status == 200

    def doc_json(self, duong_dan: str) -> dict:
        req = urllib.request.Request(
            f"{self.url_goc}{duong_dan}",
            headers={
                "Accept": "application/json",
                "Referer": f"{self.url_goc}/",
            },
        )
        with self.opener.open(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))


def _tim_nguoi_theo_email(phien: _PhienFrappe, email: str) -> dict | None:
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps([["email", "=", email]]),
            "fields": json.dumps(["name", "ho_ten", "email", "dien_thoai", "nguon"]),
            "limit_page_length": "5",
        }
    )
    ds = (phien.doc_json(f"/api/resource/LX%20Nguoi?{params}") or {}).get("data") or []
    return ds[0] if ds else None


def _doc_goi(phien: _PhienFrappe, ma_goi: str) -> dict:
    ma_esc = urllib.parse.quote(ma_goi, safe="")
    return (phien.doc_json(f"/api/resource/LX%20Goi/{ma_esc}") or {}).get("data") or {}


def _tim_su_kien_don(phien: _PhienFrappe, ma_don: str) -> dict | None:
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps(
                [
                    ["ten", "=", "don.da_tra"],
                    ["du_lieu", "like", f"%{ma_don}%"],
                ]
            ),
            "fields": json.dumps(["name", "ten", "trang_thai", "du_lieu", "da_giao", "loi"]),
            "order_by": "creation desc",
            "limit_page_length": "10",
        }
    )
    ds = (phien.doc_json(f"/api/resource/LX%20Su%20Kien?{params}") or {}).get("data") or []
    for muc in ds:
        try:
            dl = json.loads(muc.get("du_lieu") or "{}")
        except ValueError:
            dl = {}
        if isinstance(dl, dict) and str(dl.get("don") or "").strip() == ma_don:
            return muc
    return ds[0] if ds else None


def _tim_job_theo_don(phien: _PhienFrappe, ma_don: str) -> dict | None:
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps([["don", "=", ma_don]]),
            "fields": json.dumps(["name", "trang_thai", "ma_xem", "nguon", "don"]),
            "limit_page_length": "5",
        }
    )
    ds = (phien.doc_json(f"/api/resource/LX%20Job?{params}") or {}).get("data") or []
    return ds[0] if ds else None


@pytest.mark.parametrize("rong", RONG_MAN_HINH)
def test_hanh_trinh_lead_don_tra_giao_qua_goi(rong: int) -> None:
    url_linhx = _url_linhx()
    url_bu = _url_bu(url_linhx)
    khoa_webhook = _khoa_sepay()
    user, pwd = _tai_khoan_van_hanh()
    phien = _PhienFrappe(url_linhx, user, pwd)

    host_ip = urllib.parse.urlparse(url_linhx).hostname or ""
    launch_args: list[str] = []
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host_ip):
        launch_args.append(f"--host-resolver-rules=MAP *.nip.io {host_ip}")

    hat_giong = int(time.time() * 1000)
    dau_moc = f"{hat_giong}-{rong}"
    email_lead = f"e2e-t4-{dau_moc}@example.com"
    sdt_lead = f"09{(hat_giong * 10 + (1 if rong == 390 else 2)) % 100000000:08d}"

    with sync_playwright() as p:
        trinh_duyet = p.chromium.launch(headless=True, args=launch_args)
        try:
            boi_canh = trinh_duyet.new_context(viewport={"width": rong, "height": 844})
            trang = boi_canh.new_page()

            def _xu_ly_route(route) -> None:
                if "img.vietqr.io" in route.request.url:
                    route.fulfill(status=200, content_type="image/png", body=PNG_1X1)
                else:
                    route.continue_()

            trang.route("**/*", _xu_ly_route)

            # Buoc 1: Nop form lead tren giao-dien BU -> tao LX Nguoi tren engine
            phan_hoi_bu = trang.goto(f"{url_bu}/", wait_until="networkidle", timeout=30000)
            assert phan_hoi_bu is not None and phan_hoi_bu.status < 400
            trang.wait_for_selector("#form-brief", timeout=15000)

            tran_bu = trang.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not tran_bu, f"Trang BU tran ngang o viewport {rong}px"

            trang.fill("#form-brief input[name='ho_ten']", f"Khach E2E T4 {rong}")
            trang.fill("#form-brief input[name='cong_ty']", f"Cong ty E2E T4 {rong}")
            trang.fill("#form-brief input[name='dien_thoai']", sdt_lead)
            trang.fill("#form-brief input[name='email']", email_lead)
            trang.fill(
                "#form-brief textarea[name='nhu_cau']",
                f"Kiem thu hanh trinh 3 lop T4 viewport {rong}px",
            )
            trang.check("#form-brief input[name='dong_y']")

            with trang.expect_response(
                lambda r: "/api/brief" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as doi_brief:
                trang.click("#form-brief button[type='submit']")
            resp_brief = doi_brief.value
            assert resp_brief.status == 200, f"api/brief tra status {resp_brief.status}"
            du_lieu_brief = resp_brief.json()
            assert du_lieu_brief.get("ok") is True, f"api/brief khong ok: {du_lieu_brief}"

            nguoi_doc = None
            for _ in range(15):
                nguoi_doc = _tim_nguoi_theo_email(phien, email_lead)
                if nguoi_doc and nguoi_doc.get("name"):
                    break
                time.sleep(0.5)
            assert nguoi_doc and nguoi_doc.get("name"), f"Chua tao LX Nguoi cho {email_lead}"

            # Buoc 2: Tao don cho goi co loai_giao=bao_cao tren engine
            phan_hoi = trang.goto(f"{url_linhx}/#/", wait_until="networkidle", timeout=30000)
            assert phan_hoi is not None and phan_hoi.status < 400
            trang.wait_for_selector("[data-goi]", timeout=15000)

            tran_ngang = trang.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not tran_ngang, f"Trang chu tran ngang o viewport {rong}px"

            cac_nut_goi = trang.locator("[data-goi]")
            so_nut = cac_nut_goi.count()
            assert so_nut >= 1, "Khong tim thay goi tren trang ban"

            nut_chon = None
            ma_goi_chon = ""
            for idx in range(so_nut):
                nut = cac_nut_goi.nth(idx)
                ma_goi = (nut.get_attribute("data-goi") or "").strip()
                if not ma_goi:
                    continue
                thong_tin_goi = _doc_goi(phien, ma_goi)
                if thong_tin_goi.get("loai_giao") == "bao_cao":
                    nut_chon = nut
                    ma_goi_chon = ma_goi
                    break

            assert nut_chon is not None and ma_goi_chon, "Khong tim thay LX Goi co loai_giao=bao_cao"
            nut_chon.click()

            ten_brand = f"E2E-T4-{rong}"
            trang.fill("input[name='brand']", ten_brand)
            if trang.locator("input[name='email']").count():
                trang.fill("input[name='email']", email_lead)

            with trang.expect_response(
                lambda r: "linhx_core.pay.api_ban.tao_don" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as doi_tao_don:
                trang.locator("[data-tra-qr]").first.click()
            resp_tao = doi_tao_don.value
            assert resp_tao.status == 200, f"tao_don tra status {resp_tao.status}"
            du_lieu_don = (resp_tao.json() or {}).get("message") or {}

            ma_don = du_lieu_don.get("ma_don")
            so_tien = int(du_lieu_don.get("so_tien") or 0)
            noi_dung_ck = du_lieu_don.get("noi_dung_ck")
            qr_url = du_lieu_don.get("qr_url")
            assert ma_don and so_tien > 0 and noi_dung_ck and qr_url, (
                f"Thieu thong tin don: {du_lieu_don}"
            )

            trang.wait_for_selector("img[data-qr]", state="visible", timeout=10000)
            src_qr = str(trang.get_attribute("img[data-qr]", "src") or "")
            assert src_qr == qr_url, f"img[data-qr] src khong khop qr_url: {src_qr} != {qr_url}"

            # Buoc 3: Goi webhook SePay gia lap -> LX Su Kien don.da_tra = xong
            ma_gd = f"E2E-T4-{int(time.time() * 1000)}-{rong}"
            ma_http, kq_webhook = _goi_webhook_sepay(
                url_linhx, khoa_webhook, noi_dung_ck, so_tien, ma_gd
            )
            assert ma_http == 200, f"Webhook tra HTTP {ma_http}"
            assert kq_webhook.get("khop") is True, f"Webhook khong khop don: {kq_webhook}"

            su_kien_doc = None
            for _ in range(90):
                su_kien_doc = _tim_su_kien_don(phien, ma_don)
                if su_kien_doc and su_kien_doc.get("trang_thai") == "xong":
                    break
                time.sleep(1.0)
            assert su_kien_doc is not None, f"Khong tim thay LX Su Kien don.da_tra cho {ma_don}"
            assert su_kien_doc.get("trang_thai") == "xong", (
                f"LX Su Kien don.da_tra chua xong: {su_kien_doc}"
            )

            # Buoc 4: Xac minh LX Job duoc tao qua linhx_goi_baocao va co link xem bao cao
            job_doc = None
            for _ in range(20):
                job_doc = _tim_job_theo_don(phien, ma_don)
                if job_doc and job_doc.get("name") and job_doc.get("ma_xem"):
                    break
                time.sleep(0.5)
            assert job_doc and job_doc.get("name") and job_doc.get("ma_xem"), (
                f"Chua tao LX Job cho don {ma_don}: {job_doc}"
            )
            assert job_doc.get("nguon") == "don"

            ten_job = job_doc["name"]
            ma_xem = job_doc["ma_xem"]
            with trang.expect_response(
                lambda r: "linhx_worker.api.xem_bao_cao" in r.url, timeout=20000
            ) as doi_xem:
                trang.goto(
                    f"{url_linhx}/#/bao-cao/{ten_job}/{ma_xem}",
                    wait_until="networkidle",
                    timeout=30000,
                )
            assert doi_xem.value.status == 200
            du_lieu_xem = (doi_xem.value.json() or {}).get("message") or {}
            assert du_lieu_xem.get("viec") == ten_job
            trang.wait_for_selector(".buoc", timeout=15000)

            tran_bc = trang.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not tran_bc, f"Trang bao cao tran ngang o viewport {rong}px"

            boi_canh.close()
        finally:
            trinh_duyet.close()

    if rong not in _KET_QUA_RONG:
        _KET_QUA_RONG.append(rong)
    _SU_KIEN_TRANG_THAI.append(su_kien_doc["trang_thai"])
    _CHI_TIET_CHAY.append(
        {
            "rong": int(rong),
            "email": email_lead,
            "nguoi": nguoi_doc["name"],
            "goi": ma_goi_chon,
            "don": ma_don,
            "su_kien_id": su_kien_doc["name"],
            "su_kien": su_kien_doc["trang_thai"],
            "job": ten_job,
        }
    )

    duong_json = os.environ.get("E2E_JSON_OUT", "").strip()
    if duong_json and sorted(_KET_QUA_RONG) == sorted(RONG_MAN_HINH):
        p_out = Path(duong_json)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_text(
            json.dumps(
                {
                    "luc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "url_linhx": url_linhx,
                    "url_bu": url_bu,
                    "ket_qua": "passed",
                    "rong": sorted(_KET_QUA_RONG),
                    "so_test": len(_KET_QUA_RONG),
                    "su_kien": "xong"
                    if all(s == "xong" for s in _SU_KIEN_TRANG_THAI)
                    else "loi",
                    "chi_tiet": _CHI_TIET_CHAY,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
