"""T1: Hành trình E2E Playwright một lead đi trọn ở hai độ rộng 390 và 1280.

Luồng kiểm:
1. Mở trang /kham trên bản cài ifagent (E2E_IFAGENT_URL), trả lời câu hỏi T1, nhập email dạng e2e+<thời điểm>@...
   kèm tick đồng ý liên hệ để mở khoá [data-ket-qua-day-du] và tạo hồ sơ LX Nguoi + LX Dong Y.
2. Ghi nhận đồng ý chuyển chéo và gọi API chuyển lead (A5: gui_lead -> nhan_lead) từ ifagent sang linhx.
3. Tạo LX Co Hoi cho lead trên linhx, xác nhận hệ thống tự giao người phụ trách (phu_trach).
4. Đăng nhập điều hành trên linhx (E2E_LINHX_URL), mở bàn /#/engine và xác nhận lead mới hiển thị trong #lead-moi.
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

RONG_MAN_HINH = (390, 1280)
_KET_QUA_CHAY: list[dict] = []


def _doc_url(ten_bien: str) -> str:
    gia_tri = os.environ.get(ten_bien, "").strip().rstrip("/")
    if not gia_tri:
        raise RuntimeError(f"Thiếu biến môi trường {ten_bien}")
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
    hdr = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": f"{url_goc}/",
        "Origin": origin,
        "X-Frappe-CSRF-Token": csrf_token or "fetch",
    }
    return hdr


@pytest.mark.parametrize("rong", RONG_MAN_HINH)
def test_hanh_trinh_lead(rong: int):
    url_ifagent = _doc_url("E2E_IFAGENT_URL")
    url_linhx = _doc_url("E2E_LINHX_URL")
    tai_khoan, bi_mat = _doc_tai_khoan_dieu_hanh()

    moc_thoi_gian = f"{int(time.time() * 1000)}-{rong}"
    email_thu = f"e2e+{moc_thoi_gian}@vd.vn"

    with sync_playwright() as p:
        trinh_duyet = p.chromium.launch(headless=True)
        try:
            boi_canh = trinh_duyet.new_context(viewport={"width": rong, "height": 900})
            trang = boi_canh.new_page()

            # 1. Làm T1 trên trang ifagent (/kham) -> đưa email + đồng ý
            trang.goto(f"{url_ifagent}/kham", wait_until="networkidle", timeout=30000)
            if trang.locator("[data-cau]").count() == 0:
                trang.goto(f"{url_ifagent}/kham.html", wait_until="networkidle", timeout=30000)

            so_cau = trang.locator("[data-cau]").count()
            assert so_cau > 0, "Trang /kham phải có danh sách câu hỏi [data-cau]"

            khong_tran_kham = trang.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
            assert khong_tran_kham, f"Trang /kham bị tràn ngang ở độ rộng {rong}px"

            for idx in range(so_cau):
                trang.locator("[data-cau]").nth(idx).locator('input[type="radio"]').first.check()

            if trang.locator("[data-xem-ket-qua]").count():
                trang.locator("[data-xem-ket-qua]").first.click()

            trang.wait_for_selector("[data-tom-tat]", state="visible", timeout=15000)
            assert not trang.locator("[data-ket-qua-day-du]").is_visible()

            bieu_mau = trang.locator("form[data-nhan-ket-qua]")
            bieu_mau.locator('[name="email"]').fill(email_thu)
            bieu_mau.locator('[name="dong_y_lien_he"]').check()
            if bieu_mau.locator('[name="dong_y_marketing"]').count():
                bieu_mau.locator('[name="dong_y_marketing"]').check()

            with trang.expect_response(
                lambda r: "nhan_ket_qua_t1" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as thong_tin_phan_hoi:
                bieu_mau.locator('button, [type="submit"]').first.click()

            phan_hoi_t1 = thong_tin_phan_hoi.value
            assert phan_hoi_t1.status == 200, f"nhan_ket_qua_t1 trả mã {phan_hoi_t1.status}"
            than_t1 = (phan_hoi_t1.json() or {}).get("message") or {}
            ma_nguoi_ifagent = str(than_t1.get("nguoi") or "").strip()
            assert ma_nguoi_ifagent, "nhan_ket_qua_t1 phải trả mã LX Nguoi"

            trang.wait_for_selector("[data-ket-qua-day-du]", state="visible", timeout=15000)

            # 2. Ghi nhận đồng ý chuyển chéo trên ifagent và chuyển lead sang linhx (A5)
            ctx_ifagent = trinh_duyet.new_context()
            try:
                csrf_ifagent = _dang_nhap_frappe(ctx_ifagent.request, url_ifagent, tai_khoan, bi_mat)
                luc_dong_y = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                resp_dy = ctx_ifagent.request.post(
                    f"{url_ifagent}/api/resource/LX Dong Y",
                    headers=_header_json(url_ifagent, csrf_ifagent),
                    data=json.dumps(
                        {
                            "nguoi": ma_nguoi_ifagent,
                            "muc_dich": "chuyen_cheo",
                            "dong_y": 1,
                            "luc": luc_dong_y,
                            "nguon": "T1",
                        }
                    ),
                )
                assert resp_dy.status in (200, 201), f"Ghi đồng ý chuyển chéo thất bại: HTTP {resp_dy.status}"

                resp_chuyen = ctx_ifagent.request.post(
                    f"{url_ifagent}/api/method/linhx_core.crm.api_lead.gui_lead",
                    headers=_header_json(url_ifagent, csrf_ifagent),
                    data=json.dumps(
                        {
                            "nguoi": ma_nguoi_ifagent,
                            "site_dich": "linhx",
                            "don_vi": "BU-IFAGENT",
                        }
                    ),
                )
                assert resp_chuyen.status == 200, f"gui_lead (A5) thất bại: HTTP {resp_chuyen.status}"
                kq_chuyen = (resp_chuyen.json() or {}).get("message") or {}
                ma_nguoi_linhx = str(kq_chuyen.get("nguoi_moi") or "").strip()
                assert ma_nguoi_linhx, "gui_lead phải trả mã nguoi_moi bên linhx"
                assert kq_chuyen.get("tu") == "ifagent" and kq_chuyen.get("toi") == "linhx"
            finally:
                ctx_ifagent.close()

            # 3. Tạo Cơ hội trên linhx -> xác nhận hệ thống tự giao phu_trach
            csrf_linhx = _dang_nhap_frappe(boi_canh.request, url_linhx, tai_khoan, bi_mat)
            resp_co_hoi = boi_canh.request.post(
                f"{url_linhx}/api/resource/LX Co Hoi",
                headers=_header_json(url_linhx, csrf_linhx),
                data=json.dumps(
                    {
                        "nguoi": ma_nguoi_linhx,
                        "nhu_cau": f"Tư vấn lộ trình T1 Khám ({rong}px)",
                        "nguon": "ifagent",
                        "trang_thai": "moi",
                    }
                ),
            )
            assert resp_co_hoi.status in (200, 201), f"Tạo LX Co Hoi thất bại: HTTP {resp_co_hoi.status}"
            du_lieu_co_hoi = (resp_co_hoi.json() or {}).get("data") or {}
            ma_co_hoi = str(du_lieu_co_hoi.get("name") or "").strip()
            phu_trach = str(du_lieu_co_hoi.get("phu_trach") or "").strip()
            assert ma_co_hoi, "Phải tạo được bản ghi LX Co Hoi"
            assert phu_trach, "Cơ hội tạo mới phải được tự động giao người phụ trách (phu_trach)"

            # 4. Mở bàn điều hành (#/engine) trên linhx -> thấy lead trong #lead-moi
            trang.goto(f"{url_linhx}/#/engine", wait_until="networkidle", timeout=30000)
            trang.wait_for_selector("#lead-moi", state="visible", timeout=20000)
            trang.wait_for_function(
                """(args) => {
                    const el = document.querySelector('#lead-moi');
                    if (!el) return false;
                    const text = el.innerText || '';
                    return text.includes(args.lead) || text.includes(args.email);
                }""",
                arg={"lead": ma_nguoi_linhx, "email": email_thu},
                timeout=30000,
            )
            noi_dung_lead_moi = trang.inner_text("#lead-moi")
            assert ma_nguoi_linhx in noi_dung_lead_moi or email_thu in noi_dung_lead_moi

            khong_tran_ban = trang.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
            assert khong_tran_ban, f"Bàn điều hành #/engine bị tràn ngang ở độ rộng {rong}px"

            _KET_QUA_CHAY.append(
                {
                    "rong": int(rong),
                    "email": email_thu,
                    "nguoi_ifagent": ma_nguoi_ifagent,
                    "lead": ma_nguoi_linhx,
                    "co_hoi": ma_co_hoi,
                    "phu_trach": phu_trach,
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
    url_ifagent = os.environ.get("E2E_IFAGENT_URL", "").strip()
    url_linhx = os.environ.get("E2E_LINHX_URL", "").strip()
    cuoi = _KET_QUA_CHAY[-1]
    du_lieu = {
        "luc": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "url_ifagent": url_ifagent,
        "url_linhx": url_linhx,
        "ket_qua": "passed" if len(_KET_QUA_CHAY) >= 2 else "failed",
        "rong": sorted({int(x["rong"]) for x in _KET_QUA_CHAY}),
        "so_test": len(_KET_QUA_CHAY),
        "lead": cuoi["lead"],
        "phu_trach": cuoi["phu_trach"],
        "chi_tiet": _KET_QUA_CHAY,
    }
    p = Path(duong_dan_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(du_lieu, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
