"""T3: Hành trình E2E Playwright ifagent: lead → đặt lịch → pilot → case ở hai độ rộng 390 và 1280.

Luồng kiểm:
1. Mở trang BU ifagent (E2E_IFAGENT_URL), điền và gửi form[data-lead] để tạo LX Nguoi + LX Co Hoi.
2. Đặt lịch gọi tư vấn 1-1 qua form[data-dat-lich] (F2: dat_lich_goi), xác nhận lịch vào viec_cho_lich_goi
   của người phụ trách và đồng bộ lead sang linhx (E2E_LINHX_URL).
3. Tạo LX Pilot gắn với Cơ hội (F1: playbook 7 bước, hạn 14 ngày), kiểm tra chặn nhảy bước khi bước trước
   chưa xong, sau đó hoàn thành tuần tự đủ 7 bước để chuyển trạng thái Pilot sang "xong".
4. Tạo LX Case chưa duyệt (da_duyet=0) và LX Case đã duyệt có chỉ số (da_duyet=1, gắn Pilot) (F3),
   xác nhận API và trang BU ifagent chỉ hiển thị case đã duyệt và ẩn tuyệt đối case chưa duyệt ở cả 390px và 1280px.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
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
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": f"{url_goc}/",
        "Origin": origin,
        "X-Frappe-CSRF-Token": csrf_token or "fetch",
    }


def _chon_khung_gio_dat_lich(hat_giong: int, rong: int) -> str:
    """Sinh khung giờ 30 phút trong giờ hành chính (08:00–17:30 giờ VN) không đụng giữa các lượt chạy."""
    ngay_cong = (hat_giong % 360) + 1
    cac_gio = (8, 9, 10, 11, 13, 14, 15, 16)
    chi_so_gio = ((hat_giong // 360) + (0 if rong == 390 else 4)) % len(cac_gio)
    gio = cac_gio[chi_so_gio]
    phut = 0 if (hat_giong % 2 == 0) else 30
    ngay = datetime(2026, 11, 10) + timedelta(days=ngay_cong)
    return ngay.strftime(f"%Y-%m-%d {gio:02d}:{phut:02d}:00")


def _dam_bao_don_vi(request_ctx, url_goc: str, csrf: str, ma_don_vi: str = "BU-IFAGENT") -> None:
    hdr = _header_json(url_goc, csrf)
    resp_get = request_ctx.get(f"{url_goc}/api/resource/LX Don Vi/{ma_don_vi}", headers=hdr)
    if resp_get.status == 200:
        return
    request_ctx.post(
        f"{url_goc}/api/resource/LX Don Vi",
        headers=hdr,
        data=json.dumps({"ma": ma_don_vi, "ten": "Khối IF Agent"}),
    )


@pytest.mark.parametrize("rong", RONG_MAN_HINH)
def test_hanh_trinh_ifagent(rong: int):
    url_ifagent = _doc_url("E2E_IFAGENT_URL")
    url_linhx = _doc_url("E2E_LINHX_URL")
    tai_khoan, bi_mat = _doc_tai_khoan_dieu_hanh()

    hat_giong = int(time.time() * 1000)
    moc_thoi_gian = f"{hat_giong}-{rong}"
    so_duoi = f"{hat_giong % 100000000:08d}"
    dien_thoai_thu = f"09{so_duoi}"
    email_thu = f"e2e-ifagent+{moc_thoi_gian}@vd.vn"
    ho_ten_thu = f"Khách E2E ifAgent {rong}px"
    bat_dau_lich = _chon_khung_gio_dat_lich(hat_giong, rong)

    with sync_playwright() as p:
        trinh_duyet = p.chromium.launch(headless=True)
        try:
            boi_canh = trinh_duyet.new_context(viewport={"width": rong, "height": 900})
            trang = boi_canh.new_page()

            origin_ifagent = f"{urlparse(url_ifagent).scheme}://{urlparse(url_ifagent).netloc}"
            origin_linhx = f"{urlparse(url_linhx).scheme}://{urlparse(url_linhx).netloc}"
            url_bi_chan: list[str] = []

            def _chan_ngoai(route):
                url_req = route.request.url
                if url_req.startswith((origin_ifagent, origin_linhx, "data:", "blob:")):
                    route.continue_()
                else:
                    url_bi_chan.append(url_req)
                    route.abort()

            trang.route("**/*", _chan_ngoai)

            # 1. Khách mở trang ifagent và gửi form[data-lead]
            trang.goto(f"{url_ifagent}/", wait_until="networkidle", timeout=30000)
            trang.wait_for_selector("form[data-lead]", state="visible", timeout=15000)

            khong_tran_dau = trang.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
            assert khong_tran_dau, f"Trang ifagent bị tràn ngang ở độ rộng {rong}px"

            form_lead = trang.locator("form[data-lead]")
            form_lead.locator('input[name="ho_ten"]').fill(ho_ten_thu)
            form_lead.locator('input[name="dien_thoai"]').fill(dien_thoai_thu)
            form_lead.locator('input[name="email"]').fill(email_thu)
            form_lead.locator('textarea[name="nhu_cau"]').fill(
                f"Tư vấn triển khai Agent Force 7 bước ({rong}px)"
            )
            form_lead.locator('input[name="dong_y_lien_he"]').check()

            with trang.expect_response(
                lambda r: "api_form.nhan_form" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as ph_lead_info:
                form_lead.locator('button[type="submit"]').click()

            ph_lead = ph_lead_info.value
            assert ph_lead.status == 200, f"nhan_form trả HTTP {ph_lead.status}: {ph_lead.text()}"
            kq_lead = (ph_lead.json() or {}).get("message") or {}
            ma_nguoi = str(kq_lead.get("nguoi") or "").strip()
            ma_co_hoi = str(kq_lead.get("co_hoi") or "").strip()
            assert ma_nguoi, "nhan_form phải trả mã LX Nguoi"
            assert ma_co_hoi, "nhan_form phải trả mã LX Co Hoi"

            trang.wait_for_selector("[data-cam-on]", state="visible", timeout=15000)

            # 2. Khách đặt lịch gọi tư vấn trên form[data-dat-lich] (F2)
            trang.wait_for_selector("form[data-dat-lich]", state="visible", timeout=15000)
            form_lich = trang.locator("form[data-dat-lich]")

            if not form_lich.locator('input[name="ho_ten"]').input_value().strip():
                form_lich.locator('input[name="ho_ten"]').fill(ho_ten_thu)
            if not form_lich.locator('input[name="dien_thoai"]').input_value().strip():
                form_lich.locator('input[name="dien_thoai"]').fill(dien_thoai_thu)
            if not form_lich.locator('input[name="email"]').input_value().strip():
                form_lich.locator('input[name="email"]').fill(email_thu)
            if not form_lich.locator('input[name="nguoi"]').input_value().strip():
                form_lich.locator('input[name="nguoi"]').fill(ma_nguoi)

            form_lich.locator('input[name="bat_dau"]').fill(bat_dau_lich)
            form_lich.locator('input[name="phut"]').fill("30")
            form_lich.locator('textarea[name="ghi_chu"]').fill(
                f"Đặt lịch gọi tư vấn lộ trình Pilot ({rong}px)"
            )
            if not form_lich.locator('input[name="dong_y_lien_he"]').is_checked():
                form_lich.locator('input[name="dong_y_lien_he"]').check()

            with trang.expect_response(
                lambda r: "api_booking.dat_lich_goi" in r.url and r.request.method == "POST",
                timeout=20000,
            ) as ph_lich_info:
                form_lich.locator('button[type="submit"]').click()

            ph_lich = ph_lich_info.value
            assert ph_lich.status == 200, f"dat_lich_goi trả HTTP {ph_lich.status}: {ph_lich.text()}"
            kq_lich = (ph_lich.json() or {}).get("message") or {}
            ma_lich = str(kq_lich.get("lich") or "").strip()
            phu_trach = str(kq_lich.get("phu_trach") or "").strip()
            assert ma_lich, "dat_lich_goi phải trả mã LX Lich Goi"
            assert phu_trach, "dat_lich_goi phải gán người phụ trách"

            trang.wait_for_selector("[data-dat-lich-thanh-cong]", state="visible", timeout=15000)

            # Kiểm tra lịch chờ gọi của người phụ trách và tạo/chạy Pilot 7 bước (F1)
            ctx_quan_tri = trinh_duyet.new_context()
            try:
                csrf_ifagent = _dang_nhap_frappe(ctx_quan_tri.request, url_ifagent, tai_khoan, bi_mat)
                hdr_ifagent = _header_json(url_ifagent, csrf_ifagent)

                resp_vc_lich = ctx_quan_tri.request.get(
                    f"{url_ifagent}/api/method/linhx_core.booking.api_booking.viec_cho_lich_goi",
                    headers=hdr_ifagent,
                    params={"phu_trach": phu_trach},
                )
                assert resp_vc_lich.status == 200, f"viec_cho_lich_goi trả HTTP {resp_vc_lich.status}"
                ds_vc_lich = (resp_vc_lich.json() or {}).get("message") or []
                assert any(
                    isinstance(x, dict) and x.get("name") == ma_lich for x in ds_vc_lich
                ), f"Lịch {ma_lich} phải nằm trong viec_cho_lich_goi của {phu_trach}"

                # Đảm bảo Cơ hội gắn đơn vị BU-IFAGENT trước khi khởi tạo LX Pilot
                _dam_bao_don_vi(ctx_quan_tri.request, url_ifagent, csrf_ifagent, "BU-IFAGENT")
                resp_cap_nhat_ng = ctx_quan_tri.request.put(
                    f"{url_ifagent}/api/resource/LX Nguoi/{ma_nguoi}",
                    headers=hdr_ifagent,
                    data=json.dumps({"don_vi": "BU-IFAGENT"}),
                )
                assert resp_cap_nhat_ng.status == 200
                resp_cap_nhat_ch = ctx_quan_tri.request.put(
                    f"{url_ifagent}/api/resource/LX Co Hoi/{ma_co_hoi}",
                    headers=hdr_ifagent,
                    data=json.dumps({"don_vi": "BU-IFAGENT"}),
                )
                assert resp_cap_nhat_ch.status == 200

                # Chuyển chéo lead sang linhx để đồng bộ hồ sơ liên hệ với bàn điều hành linhx
                resp_dy_cheo = ctx_quan_tri.request.post(
                    f"{url_ifagent}/api/resource/LX Dong Y",
                    headers=hdr_ifagent,
                    data=json.dumps(
                        {
                            "nguoi": ma_nguoi,
                            "muc_dich": "chuyen_cheo",
                            "dong_y": 1,
                            "luc": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "nguon": "T3",
                        }
                    ),
                )
                assert resp_dy_cheo.status in (200, 201), f"Ghi đồng ý chuyển chéo thất bại: {resp_dy_cheo.status}"
                resp_chuyen = ctx_quan_tri.request.post(
                    f"{url_ifagent}/api/method/linhx_core.crm.api_lead.gui_lead",
                    headers=hdr_ifagent,
                    data=json.dumps(
                        {
                            "nguoi": ma_nguoi,
                            "site_dich": "linhx",
                            "don_vi": "BU-IFAGENT",
                        }
                    ),
                )
                assert resp_chuyen.status == 200, f"gui_lead sang linhx thất bại: HTTP {resp_chuyen.status}"

                # 3. Tạo LX Pilot gắn Cơ hội (F1: 7 bước, hạn 14 ngày)
                bat_dau_pilot = "2026-11-10 08:30:00"
                resp_tao_pilot = ctx_quan_tri.request.post(
                    f"{url_ifagent}/api/resource/LX Pilot",
                    headers=hdr_ifagent,
                    data=json.dumps(
                        {
                            "co_hoi": ma_co_hoi,
                            "phu_trach": phu_trach,
                            "don_vi": "BU-IFAGENT",
                            "bat_dau_luc": bat_dau_pilot,
                        }
                    ),
                )
                assert resp_tao_pilot.status in (200, 201), (
                    f"Tạo LX Pilot thất bại: HTTP {resp_tao_pilot.status}: {resp_tao_pilot.text()}"
                )
                du_lieu_pilot = (resp_tao_pilot.json() or {}).get("data") or {}
                ma_pilot = str(du_lieu_pilot.get("name") or "").strip()
                assert ma_pilot, "Phải tạo được bản ghi LX Pilot"
                assert du_lieu_pilot.get("trang_thai") == "dang_chay"

                cac_buoc = du_lieu_pilot.get("cac_buoc")
                if isinstance(cac_buoc, str):
                    cac_buoc = json.loads(cac_buoc)
                assert isinstance(cac_buoc, list) and len(cac_buoc) == 7, "Pilot mới phải có đúng 7 bước"

                # Kiểm tra chặn nhảy bước: hoàn thành bước 2 khi bước 1 chưa xong phải bị từ chối
                buoc_nhay_coc = [dict(b) for b in cac_buoc]
                buoc_nhay_coc[1]["trang_thai"] = "xong"
                buoc_nhay_coc[1]["xong_luc"] = "2026-11-10 09:00:00"
                resp_nhay_buoc = ctx_quan_tri.request.put(
                    f"{url_ifagent}/api/resource/LX Pilot/{ma_pilot}",
                    headers=hdr_ifagent,
                    data=json.dumps({"cac_buoc": buoc_nhay_coc}),
                )
                assert resp_nhay_buoc.status >= 400, "Phải chặn hoàn thành bước 2 khi bước 1 chưa xong"

                # Hoàn thành tuần tự đủ 7 bước của Pilot
                buoc_tuan_tu = [dict(b) for b in cac_buoc]
                for idx in range(7):
                    buoc_tuan_tu[idx]["trang_thai"] = "xong"
                    buoc_tuan_tu[idx]["xong_luc"] = f"2026-11-{10 + idx:02d} 10:00:00"
                    resp_buoc = ctx_quan_tri.request.put(
                        f"{url_ifagent}/api/resource/LX Pilot/{ma_pilot}",
                        headers=hdr_ifagent,
                        data=json.dumps({"cac_buoc": buoc_tuan_tu}),
                    )
                    assert resp_buoc.status == 200, (
                        f"Hoàn thành bước {idx + 1} thất bại: HTTP {resp_buoc.status}: {resp_buoc.text()}"
                    )
                    dl_buoc = (resp_buoc.json() or {}).get("data") or {}
                    if idx < 6:
                        assert dl_buoc.get("trang_thai") == "dang_chay"
                    else:
                        assert dl_buoc.get("trang_thai") == "xong"

                # 4. Tạo LX Case chưa duyệt và LX Case đã duyệt gắn với Pilot (F3)
                tieu_de_chua_duyet = f"Case Chưa Duyệt Ẩn {moc_thoi_gian}"
                chi_so_chua_duyet = f"+999% nội bộ ({rong}px)"
                resp_case_an = ctx_quan_tri.request.post(
                    f"{url_ifagent}/api/resource/LX Case",
                    headers=hdr_ifagent,
                    data=json.dumps(
                        {
                            "tieu_de": tieu_de_chua_duyet,
                            "khach_hang": "Nội bộ",
                            "cho_phep_hien_ten": 0,
                            "chi_so": chi_so_chua_duyet,
                            "mo_ta": "Case chưa duyệt tuyệt đối không ra công khai",
                            "da_duyet": 0,
                            "pilot": ma_pilot,
                        }
                    ),
                )
                assert resp_case_an.status in (200, 201), f"Tạo case chưa duyệt thất bại: {resp_case_an.status}"

                tieu_de_da_duyet = f"Case Pilot ifAgent {moc_thoi_gian}"
                chi_so_da_duyet = f"Giảm 68% thời gian phản hồi ({rong}px)"
                mo_ta_da_duyet = f"Nghiệm thu từ Pilot {ma_pilot} sau 7 bước triển khai."
                resp_case_duyet = ctx_quan_tri.request.post(
                    f"{url_ifagent}/api/resource/LX Case",
                    headers=hdr_ifagent,
                    data=json.dumps(
                        {
                            "tieu_de": tieu_de_da_duyet,
                            "khach_hang": ho_ten_thu,
                            "cho_phep_hien_ten": 1,
                            "chi_so": chi_so_da_duyet,
                            "mo_ta": mo_ta_da_duyet,
                            "da_duyet": 1,
                            "pilot": ma_pilot,
                        }
                    ),
                )
                assert resp_case_duyet.status in (200, 201), (
                    f"Tạo case đã duyệt thất bại: HTTP {resp_case_duyet.status}: {resp_case_duyet.text()}"
                )
                dl_case_duyet = (resp_case_duyet.json() or {}).get("data") or {}
                ma_case = str(dl_case_duyet.get("name") or "").strip()
                assert ma_case, "Phải tạo được bản ghi LX Case đã duyệt"
            finally:
                ctx_quan_tri.close()

            # Kiểm tra API công khai danh_sach_case và noi_dung_ifagent
            resp_ds_case = boi_canh.request.get(
                f"{url_ifagent}/api/method/linhx_core.cred.api_cred.danh_sach_case",
                headers={"Accept": "application/json"},
            )
            assert resp_ds_case.status == 200, f"danh_sach_case trả HTTP {resp_ds_case.status}"
            chu_ds_case = json.dumps(resp_ds_case.json(), ensure_ascii=False)
            assert tieu_de_da_duyet in chu_ds_case and chi_so_da_duyet in chu_ds_case
            assert tieu_de_chua_duyet not in chu_ds_case

            # Mở lại trang BU ifagent xác nhận case đã duyệt hiện trên giao diện và case chưa duyệt bị ẩn
            trang.goto(f"{url_ifagent}/", wait_until="networkidle", timeout=30000)
            trang.wait_for_selector(".the-muc", state="visible", timeout=15000)

            noi_dung_trang = trang.inner_text("main")
            assert tieu_de_da_duyet in noi_dung_trang, "Trang ifagent phải hiển thị tiêu đề case đã duyệt"
            assert chi_so_da_duyet in noi_dung_trang, "Trang ifagent phải hiển thị chỉ số case đã duyệt"
            assert tieu_de_chua_duyet not in noi_dung_trang, "Trang ifagent không được hiển thị case chưa duyệt"

            khong_tran_case = trang.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
            assert khong_tran_case, f"Trang ifagent (có case) bị tràn ngang ở độ rộng {rong}px"

            # Đối chiếu bàn điều hành trên linhx ở độ rộng hiện tại
            _dang_nhap_frappe(boi_canh.request, url_linhx, tai_khoan, bi_mat)
            trang.goto(f"{url_linhx}/#/engine", wait_until="networkidle", timeout=30000)
            trang.wait_for_selector("#lead-moi", state="visible", timeout=20000)
            khong_tran_ban = trang.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
            assert khong_tran_ban, f"Bàn điều hành #/engine bị tràn ngang ở độ rộng {rong}px"
            assert not url_bi_chan, f"Phát hiện gọi mạng ra ngoài: {url_bi_chan}"

            _KET_QUA_CHAY.append(
                {
                    "rong": int(rong),
                    "email": email_thu,
                    "dien_thoai": dien_thoai_thu,
                    "lead": ma_nguoi,
                    "co_hoi": ma_co_hoi,
                    "lich": ma_lich,
                    "phu_trach": phu_trach,
                    "pilot": ma_pilot,
                    "case": ma_case,
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
        "lich": cuoi["lich"],
        "pilot": cuoi["pilot"],
        "case": cuoi["case"],
        "chi_tiet": _KET_QUA_CHAY,
    }
    p = Path(duong_dan_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(du_lieu, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
