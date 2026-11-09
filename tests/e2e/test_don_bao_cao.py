"""T2: Hành trình E2E Playwright một đơn báo cáo trả QR (webhook giả lập) rồi tự giao.

Luồng kiểm:
1. Mở trang đặt báo cáo (#/) trên bản cài linhx (E2E_LINHX_URL), chọn gói [data-goi],
   nhập thương hiệu + email và bấm nút thanh toán QR [data-tra-qr] (Q1).
2. Xác nhận hiển thị mã QR img[data-qr] kèm mã đơn, số tiền và nội dung chuyển khoản.
3. Gửi webhook giả lập đúng khuôn dạng vào /api/method/linhx_core.pay.api_sepay.webhook
   với khoá từ E2E_SEPAY_KHOA, số tiền và nội dung chuyển khoản của đơn.
4. Xác nhận đơn chuyển sang trạng thái da_tra (B3) và hệ thống tự sinh LX Job
   có nguon="don", trạng thái vào hàng ngay (bỏ duyệt tay) kèm đường dẫn tự giao báo cáo
   /# /bao-cao/<job>/<ma_xem> trong vòng <= 60 giây (B4).
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import urlparse

import pytest
from playwright.sync_api import sync_playwright

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360f8cfc0f01f0005000201e2b2a3f40000000049454e44ae426082"
)
_KET_QUA_CHAY: list[dict] = []


def _doc_url(ten_bien: str) -> str:
    gia_tri = os.environ.get(ten_bien, "").strip().rstrip("/")
    if not gia_tri:
        raise RuntimeError(f"Thiếu biến môi trường {ten_bien}")
    return gia_tri


def _doc_khoa_webhook() -> str:
    gia_tri = os.environ.get("E2E_SEPAY_KHOA", "").strip()
    if not gia_tri:
        raise RuntimeError("Thiếu biến môi trường E2E_SEPAY_KHOA")
    return gia_tri


def _doc_tai_khoan_dieu_hanh() -> tuple[str, str]:
    tai_khoan = (
        os.environ.get("E2E_USER")
        or os.environ.get("LINH_EMAIL")
        or "Administrator"
    ).strip()
    bi_mat = (
        os.environ.get("E2E_AUTH_SECRET")
        or os.environ.get("LINH_MAT_KHAU")
        or os.environ.get("ADMIN_PASSWORD")
        or ""
    ).strip()
    if not bi_mat:
        raise RuntimeError("Thiếu biến môi trường mật khẩu điều hành (E2E_AUTH_SECRET / LINH_MAT_KHAU)")
    return tai_khoan, bi_mat


def _dang_nhap_frappe(request_ctx, url_goc: str, tai_khoan: str, bi_mat: str) -> str:
    origin = f"{urlparse(url_goc).scheme}://{urlparse(url_goc).netloc}"
    resp = request_ctx.post(
        f"{url_goc}/api/method/login",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": f"{url_goc}/",
            "Origin": origin,
        },
        data=json.dumps({"usr": tai_khoan, "pwd": bi_mat}),
    )
    assert resp.status == 200, f"Đăng nhập {url_goc} thất bại: HTTP {resp.status}"
    resp_phien = request_ctx.get(
        f"{url_goc}/api/method/linhx_worker.api.phien",
        headers={
            "Accept": "application/json",
            "Referer": f"{url_goc}/",
        },
    )
    if resp_phien.status == 200:
        du_lieu = (resp_phien.json() or {}).get("message") or {}
        return str(du_lieu.get("csrf") or "")
    return ""


def _header_json(url_goc: str, csrf_token: str = "") -> dict[str, str]:
    origin = f"{urlparse(url_goc).scheme}://{urlparse(url_goc).netloc}"
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": f"{url_goc}/",
        "Origin": origin,
        "X-Frappe-CSRF-Token": csrf_token or "fetch",
    }


def test_don_bao_cao():
    url_linhx = _doc_url("E2E_LINHX_URL")
    khoa_webhook = _doc_khoa_webhook()
    tai_khoan, bi_mat = _doc_tai_khoan_dieu_hanh()

    moc_thoi_gian = str(int(time.time() * 1000))
    ten_brand = f"Trà Đồi Mây {moc_thoi_gian[-6:]}"
    email_khach = f"e2e-don+{moc_thoi_gian}@vd.vn"

    with sync_playwright() as p:
        trinh_duyet = p.chromium.launch(headless=True)
        try:
            boi_canh = trinh_duyet.new_context(viewport={"width": 1280, "height": 900})
            trang = boi_canh.new_page()

            origin = f"{urlparse(url_linhx).scheme}://{urlparse(url_linhx).netloc}"
            url_bi_chan: list[str] = []

            # Trả ảnh PNG 1x1 nội bộ cho ảnh VietQR và chặn mọi kết nối ra ngoài máy chủ thử
            def _chan_ngoai(route):
                url_req = route.request.url
                if "img.vietqr.io" in url_req:
                    route.fulfill(status=200, content_type="image/png", body=PNG_1X1)
                elif url_req.startswith((origin, "data:", "blob:")):
                    route.continue_()
                else:
                    url_bi_chan.append(url_req)
                    route.abort()

            trang.route("**/*", _chan_ngoai)

            # 1. Mở trang #/ chọn gói và bấm trả QR (Q1)
            trang.goto(f"{url_linhx}/#/", wait_until="networkidle", timeout=30000)
            trang.wait_for_selector("[data-goi]", state="visible", timeout=20000)

            for rong in (390, 1280):
                trang.set_viewport_size({"width": rong, "height": 900})
                khong_tran = trang.evaluate(
                    "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
                )
                assert khong_tran, f"Trang đặt báo cáo #/ bị tràn ngang ở độ rộng {rong}px"

            phan_tu_goi = trang.locator("[data-goi]").first
            ma_goi_chon = str(phan_tu_goi.get_attribute("data-goi") or "").strip()
            assert ma_goi_chon, "Phần tử [data-goi] phải có mã gói"
            phan_tu_goi.click()

            trang.fill('input[name="brand"]', ten_brand)
            if trang.locator('input[name="email"]').count():
                trang.fill('input[name="email"]', email_khach)

            with trang.expect_response(
                lambda r: "api_ban.tao_don" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as thong_tin_tao_don:
                trang.locator("[data-tra-qr]").first.click()

            phan_hoi_don = thong_tin_tao_don.value
            assert phan_hoi_don.status == 200, f"tao_don trả HTTP {phan_hoi_don.status}"
            du_lieu_don = (phan_hoi_don.json() or {}).get("message") or {}
            ma_don = str(du_lieu_don.get("ma_don") or "").strip()
            so_tien = int(du_lieu_don.get("so_tien") or 0)
            noi_dung_ck = str(du_lieu_don.get("noi_dung_ck") or "").strip()
            qr_url = str(du_lieu_don.get("qr_url") or "").strip()

            assert ma_don, "tao_don phải trả ma_don"
            assert so_tien > 0, "tao_don phải trả so_tien > 0"
            assert noi_dung_ck, "tao_don phải trả noi_dung_ck"
            assert qr_url, "tao_don phải trả qr_url"

            # 2. Xác nhận hiển thị img[data-qr] trên giao diện
            trang.wait_for_selector("img[data-qr]", state="visible", timeout=15000)
            src_qr = str(trang.get_attribute("img[data-qr]", "src") or "")
            assert src_qr == qr_url, "img[data-qr] phải gắn đúng qr_url từ tao_don"
            trang.wait_for_function(
                "document.querySelector('img[data-qr]').naturalWidth > 0",
                timeout=10000,
            )

            # 3. Gửi webhook giả lập vào /api/method/linhx_core.pay.api_sepay.webhook (B3)
            tx_id = f"E2E-TX-{moc_thoi_gian}"
            payload_webhook = {
                "id": tx_id,
                "gateway": "MBBank",
                "transactionDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "accountNumber": "0000123456789",
                "transferType": "in",
                "transferAmount": so_tien,
                "content": f"CHUYEN KHOAN {noi_dung_ck}",
                "code": noi_dung_ck,
                "referenceCode": f"FT{moc_thoi_gian}",
            }
            origin = f"{urlparse(url_linhx).scheme}://{urlparse(url_linhx).netloc}"
            t_bat_dau_tra = time.monotonic()
            resp_wh = boi_canh.request.post(
                f"{url_linhx}/api/method/linhx_core.pay.api_sepay.webhook",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Apikey {khoa_webhook}",
                    "Referer": f"{url_linhx}/",
                    "Origin": origin,
                },
                data=json.dumps(payload_webhook),
            )
            assert resp_wh.status == 200, f"api_sepay.webhook trả HTTP {resp_wh.status}: {resp_wh.text()}"
            kq_wh = (resp_wh.json() or {}).get("message") or {}
            assert kq_wh.get("success") is True and kq_wh.get("khop") is True, f"Webhook không khớp đơn: {kq_wh}"
            assert kq_wh.get("ma_don") == ma_don

            # 4. Đối chiếu đơn da_tra (B3) và LX Job nguon="don" sinh trong <= 60 giây (B4)
            csrf = _dang_nhap_frappe(boi_canh.request, url_linhx, tai_khoan, bi_mat)
            hdr = _header_json(url_linhx, csrf)

            resp_don_db = boi_canh.request.get(
                f"{url_linhx}/api/resource/LX Don",
                headers=hdr,
                params={
                    "filters": json.dumps([["ma", "=", ma_don]]),
                    "fields": json.dumps(["name", "ma", "trang_thai", "so_tien", "tx_id"]),
                },
            )
            assert resp_don_db.status == 200, f"Đọc LX Don thất bại: HTTP {resp_don_db.status}"
            ds_don_db = (resp_don_db.json() or {}).get("data") or []
            assert len(ds_don_db) == 1, f"Không tìm thấy LX Don {ma_don}"
            assert ds_don_db[0].get("trang_thai") == "da_tra", f"Đơn chưa chuyển da_tra: {ds_don_db[0]}"

            job_don = None
            han_cho = t_bat_dau_tra + 60.0
            while time.monotonic() <= han_cho:
                resp_job = boi_canh.request.get(
                    f"{url_linhx}/api/resource/LX Job",
                    headers=hdr,
                    params={
                        "filters": json.dumps([["don", "=", ma_don]]),
                        "fields": json.dumps(
                            ["name", "don", "nguon", "trang_thai", "workflow", "dau_vao", "ma_xem"]
                        ),
                    },
                )
                if resp_job.status == 200:
                    ds_job = (resp_job.json() or {}).get("data") or []
                    if ds_job:
                        job_don = ds_job[0]
                        break
                time.sleep(0.5)

            giay_tu_tra_toi_job = round(time.monotonic() - t_bat_dau_tra, 3)
            assert job_don is not None, f"Không sinh LX Job cho đơn {ma_don} trong 60 giây"
            assert 0 <= giay_tu_tra_toi_job <= 60, f"Thời gian sinh Job vượt 60s: {giay_tu_tra_toi_job}s"
            assert job_don.get("nguon") == "don", f"LX Job phải có nguon='don': {job_don}"
            assert job_don.get("trang_thai") != "cho_duyet", f"LX Job từ đơn đã trả phải bỏ duyệt tay: {job_don}"
            assert ten_brand in str(job_don.get("dau_vao") or ""), "dau_vao của LX Job phải chứa brand của đơn"

            ten_job = str(job_don.get("name") or "").strip()
            ma_xem = str(job_don.get("ma_xem") or "").strip()
            assert ten_job and ma_xem, "LX Job phải có name và ma_xem để tự giao link báo cáo"

            # Mở đường dẫn tự giao báo cáo của khách (#/bao-cao/<job>/<ma_xem>) xác nhận truy cập được
            with trang.expect_response(
                lambda r: "xem_bao_cao" in r.url and r.status == 200,
                timeout=20000,
            ) as thong_tin_xem_bc:
                trang.goto(f"{url_linhx}/#/bao-cao/{ten_job}/{ma_xem}", wait_until="networkidle", timeout=30000)

            du_lieu_xem_bc = (thong_tin_xem_bc.value.json() or {}).get("message") or {}
            assert du_lieu_xem_bc.get("viec") == ten_job
            assert du_lieu_xem_bc.get("brand") == ten_brand
            trang.wait_for_selector(".buoc", state="visible", timeout=15000)
            assert not url_bi_chan, f"Phát hiện gọi mạng ra ngoài: {url_bi_chan}"

            _KET_QUA_CHAY.append(
                {
                    "don": ma_don,
                    "job": ten_job,
                    "giay_tu_tra_toi_job": giay_tu_tra_toi_job,
                    "goi": ma_goi_chon,
                    "so_tien": so_tien,
                }
            )
            boi_canh.close()
        finally:
            trinh_duyet.close()


@pytest.fixture(scope="module", autouse=True)
def _ghi_bang_chung_e2e():
    _KET_QUA_CHAY.clear()
    yield
    duong_dan_out = os.environ.get("E2E_JSON_OUT", "").strip()
    if not duong_dan_out or not _KET_QUA_CHAY:
        return
    url_linhx = os.environ.get("E2E_LINHX_URL", "").strip()
    cuoi = _KET_QUA_CHAY[-1]
    du_lieu = {
        "luc": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "url_linhx": url_linhx,
        "ket_qua": "passed",
        "don": cuoi["don"],
        "job": cuoi["job"],
        "giay_tu_tra_toi_job": cuoi["giay_tu_tra_toi_job"],
    }
    p = Path(duong_dan_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(du_lieu, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
