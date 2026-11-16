#!/usr/bin/env python3
"""Thu thập bằng chứng E2E giao diện đa khổ bằng Playwright.

Chạy:
  python runner/bang_chung.py --url <http://...> --kho iphone,kiosk,desktop --video --ra <thư mục>
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from typing import Callable, Sequence
from urllib.parse import urlparse
import uuid

KHO_CHUAN: dict[str, dict[str, int]] = {
    "iphone": {"rong": 390, "cao": 844, "dpr": 3},
    "kiosk": {"rong": 1080, "cao": 1920, "dpr": 1},
    "desktop": {"rong": 1440, "cao": 900, "dpr": 1},
}

KHO_MAC_DINH = "iphone,kiosk,desktop"
TEN_TEP_JSON = "bang-chung.json"


class LoiThieuPlaywright(RuntimeError):
    """Báo máy chưa cài thư viện Playwright hoặc trình duyệt Chromium."""


def kiem_tra_url(url: str) -> str:
    """Chỉ cho phép http:// hoặc https:// có host hợp lệ; cấm cứng file://."""
    chuoi = str(url or "").strip()
    if not chuoi:
        raise ValueError("URL không được để trống; chỉ nhận http:// hoặc https://.")
    phan_tich = urlparse(chuoi)
    giao_thuc = (phan_tich.scheme or "").lower()
    if giao_thuc == "file" or chuoi.lower().startswith("file:"):
        raise ValueError(f"Cấm giao thức file:// (chỉ nhận http/https): {chuoi}")
    if giao_thuc not in ("http", "https") or not phan_tich.netloc:
        raise ValueError(f"URL không hợp lệ (chỉ nhận http:// hoặc https://): {chuoi}")
    return chuoi


def phan_tich_kho(kho: str | Sequence[str]) -> list[str]:
    """Tách và kiểm tra danh sách tên khổ màn hình."""
    if isinstance(kho, str):
        danh_sach_tho = [muc.strip().lower() for muc in kho.split(",")]
    else:
        danh_sach_tho = [str(muc).strip().lower() for muc in kho]

    ket_qua: list[str] = []
    for ten in danh_sach_tho:
        if not ten:
            continue
        if ten not in KHO_CHUAN:
            ho_tro = ", ".join(KHO_CHUAN.keys())
            raise ValueError(f"Khổ '{ten}' không hợp lệ (chỉ hỗ trợ: {ho_tro}).")
        if ten not in ket_qua:
            ket_qua.append(ten)

    if not ket_qua:
        ho_tro = ", ".join(KHO_CHUAN.keys())
        raise ValueError(f"Danh sách khổ rỗng (chỉ hỗ trợ: {ho_tro}).")
    return ket_qua


def tinh_sha256(duong_dan: Path) -> str:
    """Tính mã băm SHA-256 hex cho một tệp."""
    bam = hashlib.sha256()
    with Path(duong_dan).open("rb") as tep:
        while True:
            khoi = tep.read(65536)
            if not khoi:
                break
            bam.update(khoi)
    return bam.hexdigest()


def _nap_sync_playwright(sync_playwright_fn: Callable | None = None) -> Callable:
    if sync_playwright_fn is not None:
        return sync_playwright_fn
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise LoiThieuPlaywright(
            "Thiếu Playwright trên máy. Cài bằng: "
            "python -m pip install playwright && python -m playwright install chromium"
        ) from exc
    return sync_playwright


def _cuon_mot_luot(page, so_buoc: int = 5, nghi_ms: int = 90) -> None:
    """Cuộn trang một lượt từ đầu xuống cuối để ghi hình chuyển động và bố cục."""
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(nghi_ms)
    max_y = int(
        page.evaluate(
            "() => Math.max(0, (document.documentElement.scrollHeight || document.body.scrollHeight || 0) - window.innerHeight)"
        )
        or 0
    )
    if max_y <= 0:
        page.wait_for_timeout(nghi_ms * 2)
        return
    for buoc in range(1, so_buoc + 1):
        vi_tri = int(round(max_y * buoc / so_buoc))
        page.evaluate(f"window.scrollTo(0, {vi_tri})")
        page.wait_for_timeout(nghi_ms)
    page.wait_for_timeout(nghi_ms)


def _dem_anh_trung_dom(page) -> int:
    """Đếm số thẻ <img> bị lặp cùng nguồn ảnh trên trang (dupImg)."""
    return int(
        page.evaluate(
            """() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const dem = Object.create(null);
                for (const el of imgs) {
                    const src = String(el.currentSrc || el.getAttribute('src') || '').trim();
                    if (!src) continue;
                    dem[src] = (dem[src] || 0) + 1;
                }
                let trung = 0;
                for (const k of Object.keys(dem)) {
                    if (dem[k] > 1) trung += (dem[k] - 1);
                }
                return trung;
            }"""
        )
        or 0
    )


def thu_thap_bang_chung(
    url: str,
    ra: Path | str,
    kho: str | Sequence[str] = KHO_MAC_DINH,
    video: bool = False,
    timeout_ms: int = 30000,
    sync_playwright_fn: Callable | None = None,
) -> dict:
    """Mở URL trên từng khổ, chụp toàn trang, tuỳ chọn quay video 1 lượt cuộn và xuất bang-chung.json."""
    url_sach = kiem_tra_url(url)
    ds_kho = phan_tich_kho(kho)
    nap_pw = _nap_sync_playwright(sync_playwright_fn)

    tm_ra = Path(ra)
    tm_ra.mkdir(parents=True, exist_ok=True)

    chi_tiet_kho: dict[str, dict] = {}
    sha256_tep: dict[str, str] = {}
    loi_console_chung: list[str] = []

    with nap_pw() as pw:
        try:
            trinh_duyet = pw.chromium.launch(headless=True)
        except Exception as exc:
            thong_diep = str(exc)
            if "Executable doesn't exist" in thong_diep or "playwright install" in thong_diep.lower():
                raise LoiThieuPlaywright(
                    "Thiếu trình duyệt Chromium của Playwright. Chạy: python -m playwright install chromium"
                ) from exc
            raise

        try:
            for ten_kho in ds_kho:
                thong_so = KHO_CHUAN[ten_kho]
                rong = thong_so["rong"]
                cao = thong_so["cao"]
                dpr = thong_so["dpr"]

                tm_video_tam: Path | None = None
                tham_so_context: dict = {
                    "viewport": {"width": rong, "height": cao},
                    "device_scale_factor": dpr,
                }
                if video:
                    tm_video_tam = tm_ra / f".tmp-video-{ten_kho}-{uuid.uuid4().hex[:8]}"
                    tm_video_tam.mkdir(parents=True, exist_ok=True)
                    tham_so_context["record_video_dir"] = str(tm_video_tam)
                    tham_so_context["record_video_size"] = {"width": rong, "height": cao}

                loi_kho: list[str] = []
                boi_canh = trinh_duyet.new_context(**tham_so_context)
                trang = boi_canh.new_page()
                trang.set_default_timeout(timeout_ms)
                trang.on(
                    "console",
                    lambda msg, ds=loi_kho: ds.append(msg.text) if msg.type == "error" else None,
                )
                trang.on("pageerror", lambda err, ds=loi_kho: ds.append(str(err)))

                ten_anh = f"{ten_kho}.png"
                duong_dan_anh = tm_ra / ten_anh
                ten_video: str | None = f"{ten_kho}.webm" if video else None
                doi_tuong_video = None

                try:
                    trang.goto(url_sach, wait_until="load", timeout=timeout_ms)
                    trang.screenshot(path=str(duong_dan_anh), full_page=True)
                    if video:
                        _cuon_mot_luot(trang)
                        doi_tuong_video = trang.video
                    trung_dom = _dem_anh_trung_dom(trang)
                finally:
                    trang.close()
                    boi_canh.close()

                sha256_tep[ten_anh] = tinh_sha256(duong_dan_anh)

                if video:
                    duong_dan_video = tm_ra / str(ten_video)
                    try:
                        if doi_tuong_video is not None:
                            doi_tuong_video.save_as(str(duong_dan_video))
                    finally:
                        if tm_video_tam is not None:
                            shutil.rmtree(tm_video_tam, ignore_errors=True)
                    sha256_tep[str(ten_video)] = tinh_sha256(duong_dan_video)

                for dong_loi in loi_kho:
                    loi_console_chung.append(f"[{ten_kho}] {dong_loi}")

                muc_kho: dict = {
                    "rong": rong,
                    "cao": cao,
                    "dpr": dpr,
                    "anh": ten_anh,
                    "video": ten_video,
                    "so_anh_trung_dom": trung_dom,
                    "loi_console": loi_kho,
                }
                chi_tiet_kho[ten_kho] = muc_kho
        finally:
            trinh_duyet.close()

    ds_bam_anh = [sha256_tep[muc["anh"]] for muc in chi_tiet_kho.values()]
    so_trung_tep_anh = len(ds_bam_anh) - len(set(ds_bam_anh))
    so_trung_dom_max = max((muc["so_anh_trung_dom"] for muc in chi_tiet_kho.values()), default=0)
    so_anh_trung = so_trung_tep_anh + so_trung_dom_max

    ket_qua = {
        "url": url_sach,
        "kho": chi_tiet_kho,
        "sha256": sha256_tep,
        "so_anh_trung": so_anh_trung,
        "loi_console": loi_console_chung,
    }
    tep_json = tm_ra / TEN_TEP_JSON
    tep_json.write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ket_qua


def tao_bo_phan_tich_tham_so() -> argparse.ArgumentParser:
    bo = argparse.ArgumentParser(
        description="Chụp toàn trang đa khổ, quay video cuộn và xuất bang-chung.json bằng Playwright."
    )
    bo.add_argument("--url", required=True, help="URL trang cần kiểm (chỉ nhận http:// hoặc https://).")
    bo.add_argument(
        "--kho",
        default=KHO_MAC_DINH,
        help=f"Danh sách khổ cách nhau bởi dấu phẩy (mặc định: {KHO_MAC_DINH}).",
    )
    bo.add_argument("--video", action="store_true", help="Quay thêm video 1 lượt cuộn cho mỗi khổ.")
    bo.add_argument("--ra", required=True, help="Thư mục lưu ảnh, video và bang-chung.json.")
    bo.add_argument("--timeout-ms", type=int, default=30000, help="Thời gian chờ tải trang tối đa (ms).")
    return bo


def main(argv: Sequence[str] | None = None) -> int:
    bo = tao_bo_phan_tich_tham_so()
    tham_so = bo.parse_args(argv)
    try:
        ket_qua = thu_thap_bang_chung(
            url=tham_so.url,
            ra=tham_so.ra,
            kho=tham_so.kho,
            video=bool(tham_so.video),
            timeout_ms=int(tham_so.timeout_ms),
        )
    except ValueError as exc:
        print(f"LỖI THAM SỐ: {exc}", file=sys.stderr)
        return 2
    except LoiThieuPlaywright as exc:
        print(f"THIẾU PLAYWRIGHT: {exc}", file=sys.stderr)
        return 3

    duong_dan_json = Path(tham_so.ra) / TEN_TEP_JSON
    print(
        f"Đã ghi {duong_dan_json} (khổ={','.join(ket_qua['kho'].keys())}, "
        f"so_anh_trung={ket_qua['so_anh_trung']}, loi_console={len(ket_qua['loi_console'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
