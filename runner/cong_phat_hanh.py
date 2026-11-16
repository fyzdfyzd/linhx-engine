#!/usr/bin/env python3
"""Cổng phát hành cho hàng đợi máy (`runner/cong_phat_hanh.py`).

Chỉ kiểm tra an toàn qua phương thức GET (KHÔNG thực hiện deploy thật):
1. Chặn nếu `--base` (hoặc đích redirect) trùng tên miền prod trong `--prod`.
2. Chặn nếu giờ Việt Nam (UTC+7) > 22:00 hoặc < 07:00.
3. Chỉ dùng `GET <base>/healthz`, bắt buộc trả HTTP 200 và đúng `BUILD_SHA`.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

MUI_GIO_VN = timezone(timedelta(hours=7))
GIO_MO_CUA = 7
GIO_DONG_CUA = 22
KHOA_SHA = ("BUILD_SHA", "build_sha", "buildSha", "sha")
_HEADER_GET = {"Accept": "application/json", "User-Agent": "linhx-cong-phat-hanh/1.0"}
_TZ_COMPACT_RE = re.compile(r"([+-]\d{2})(\d{2})$")
_GIO_NGAN_RE = re.compile(r"^(\d{1,2})(?::(\d{2})(?::(\d{2}))?)?h?$")
_SHA_TEXT_RE = re.compile(r"(?m)^\s*BUILD_SHA\s*[:=]\s*([^\s#;\"']+)\s*$")


@dataclass(frozen=True)
class KetQuaCong:
    dat: bool
    ma_thoat: int
    loai_loi: str
    thong_diep: str
    build_sha: str | None = None
    url: str = ""
    gio_vn: str = ""


def _loi(ma: int, loai: str, thong_diep: str, url: str = "", gio_vn: str = "", build_sha: str | None = None) -> KetQuaCong:
    return KetQuaCong(False, ma, loai, thong_diep, build_sha=build_sha, url=url, gio_vn=gio_vn)


class _LoiChanRedirect(Exception):
    def __init__(self, loai: str, thong_diep: str) -> None:
        super().__init__(thong_diep)
        self.loai = loai
        self.thong_diep = thong_diep


def chuan_hoa_ten_mien(gia_tri: str | None) -> str:
    """Chuẩn hoá tên miền về chữ thường, bỏ cổng/đường dẫn/dấu chấm đuôi; giữ tiền tố `*.` nếu có."""
    muc = str(gia_tri or "").strip()
    if not muc:
        return ""
    wildcard = muc.startswith("*.")
    if wildcard:
        muc = muc[2:].strip()
    parsed = urllib.parse.urlparse(muc if "://" in muc else f"http://{muc}")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    return (f"*.{host}" if wildcard else host) if host else ""


def tach_danh_sach_prod(prod_raw: list | tuple | str | None) -> list[str]:
    """Tách danh sách `--prod` từ chuỗi phẩy/chấm phẩy/khoảng trắng hoặc danh sách lặp cờ."""
    if prod_raw is None:
        return []
    phan_tu: list[str] = []
    hang_doi = [prod_raw] if isinstance(prod_raw, str) else list(prod_raw)
    for muc in hang_doi:
        if isinstance(muc, (list, tuple)):
            hang_doi.extend(muc)
            continue
        for manh in re.split(r"[,\s;]+", str(muc or "")):
            chuan = chuan_hoa_ten_mien(manh)
            if chuan and chuan not in phan_tu:
                phan_tu.append(chuan)
    return phan_tu


def trung_ten_mien_prod(host: str | None, ds_prod: list[str]) -> str | None:
    """Trả về mẫu prod bị trùng nếu `host` khớp danh sách `--prod`, ngược lại trả `None`."""
    ten = chuan_hoa_ten_mien(host)
    if not ten:
        return None
    for mau in ds_prod:
        if mau.startswith("*."):
            goc = mau[2:]
            if ten == goc or ten.endswith("." + goc):
                return mau
        elif ten == mau:
            return mau
    return None


def lay_gio_vn(now: datetime | str | None = None) -> datetime:
    """Quy đổi thời điểm truyền vào (hoặc hiện tại) sang múi giờ Việt Nam (UTC+7)."""
    nguon = now if now is not None else os.environ.get("LINHX_CONG_NOW")
    if nguon is None or (isinstance(nguon, str) and not nguon.strip()):
        return datetime.now(MUI_GIO_VN)
    if isinstance(nguon, datetime):
        return nguon.replace(tzinfo=MUI_GIO_VN) if nguon.tzinfo is None else nguon.astimezone(MUI_GIO_VN)
    chuoi = str(nguon).strip()
    khop_gio = _GIO_NGAN_RE.match(chuoi)
    if khop_gio:
        g, p, s = int(khop_gio.group(1)), int(khop_gio.group(2) or 0), int(khop_gio.group(3) or 0)
        return datetime(2026, 1, 1, g, p, s, tzinfo=MUI_GIO_VN)
    chuoi = chuoi[:-1] + "+00:00" if chuoi.endswith(("Z", "z")) else _TZ_COMPACT_RE.sub(r"\1:\2", chuoi)
    dt = datetime.fromisoformat(chuoi)
    return dt.replace(tzinfo=MUI_GIO_VN) if dt.tzinfo is None else dt.astimezone(MUI_GIO_VN)


def trong_khung_gio_vn(dt_vn: datetime) -> bool:
    """Cho phép từ 07:00:00 đến 22:00:00 giờ VN; chặn nếu < 7h hoặc > 22h (sau 22:00)."""
    dt = lay_gio_vn(dt_vn)
    return dt.hour >= GIO_MO_CUA and (dt.hour, dt.minute, dt.second, dt.microsecond) <= (GIO_DONG_CUA, 0, 0, 0)


def trich_xuat_build_sha(than: str) -> tuple[bool, str | None, str | None]:
    """Đọc `BUILD_SHA` từ JSON `/healthz` (hoặc dòng khóa=giá_trị thuần chữ)."""
    van_ban = (than or "").strip()
    if not van_ban:
        return False, None, "phản hồi /healthz rỗng"
    try:
        du_lieu = json.loads(van_ban)
    except json.JSONDecodeError:
        khop = _SHA_TEXT_RE.search(van_ban)
        return (True, khop.group(1).strip(), None) if khop else (False, None, "phản hồi /healthz thiếu BUILD_SHA")
    if not isinstance(du_lieu, dict):
        return False, None, "phản hồi /healthz không phải đối tượng JSON"
    if "ok" in du_lieu and du_lieu["ok"] is False:
        return False, None, "phản hồi /healthz báo ok=false"
    for khoa in KHOA_SHA:
        gia_tri = du_lieu.get(khoa)
        if isinstance(gia_tri, str) and gia_tri.strip():
            return True, gia_tri.strip(), None
    return False, None, "JSON /healthz thiếu trường BUILD_SHA"


def _tao_url_healthz(base_url: str) -> tuple[str | None, str | None, str | None]:
    chuoi = (base_url or "").strip()
    if not chuoi:
        return None, None, "thiếu tham số --base"
    parsed = urllib.parse.urlparse(chuoi)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        return None, None, f"--base phải dùng http:// hoặc https:// kèm tên miền hợp lệ (nhận: {base_url!r})"
    duong = (parsed.path or "").rstrip("/") + "/healthz"
    return urllib.parse.urlunparse((parsed.scheme.lower(), parsed.netloc, duong, "", "", "")), parsed.hostname.lower().rstrip("."), None


class _RedirectChiGetAnToan(urllib.request.HTTPRedirectHandler):
    def __init__(self, ds_prod: list[str], toi_da: int = 3) -> None:
        super().__init__()
        self._ds_prod = ds_prod
        self._so_buoc = 0
        self._toi_da = toi_da

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self._so_buoc += 1
        if self._so_buoc > self._toi_da:
            raise _LoiChanRedirect("MANG", f"quá số bước redirect ({self._toi_da})")
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
            raise _LoiChanRedirect("THAM_SO", f"chặn redirect giao thức lạ: {newurl!r}")
        mau_trung = trung_ten_mien_prod(parsed.hostname, self._ds_prod)
        if mau_trung:
            raise _LoiChanRedirect("PROD", f"chặn redirect tới tên miền prod '{parsed.hostname}' (khớp '{mau_trung}')")
        return urllib.request.Request(newurl, method="GET", headers=dict(_HEADER_GET))


def _goi_get_healthz(url_healthz: str, ds_prod: list[str], timeout: float, gio_vn: str) -> tuple[str | None, KetQuaCong | None]:
    opener = urllib.request.build_opener(
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(),
        _RedirectChiGetAnToan(ds_prod),
    )
    req = urllib.request.Request(url_healthz, method="GET", headers=dict(_HEADER_GET))
    try:
        with opener.open(req, timeout=float(timeout)) as resp:
            status = getattr(resp, "status", resp.getcode())
            than = resp.read(65536).decode("utf-8", "replace")
    except _LoiChanRedirect as exc:
        return None, _loi(3 if exc.loai == "PROD" else 2, exc.loai, f"CHAN [{exc.loai}]: {exc.thong_diep}", url_healthz, gio_vn)
    except urllib.error.HTTPError as exc:
        return None, _loi(5, "HTTP_STATUS", f"LOI [HTTP_STATUS]: GET {url_healthz} trả mã HTTP {exc.code} (cần 200)", url_healthz, gio_vn)
    except Exception as exc:
        return None, _loi(5, "MANG", f"LOI [MANG]: không gọi được GET {url_healthz}: {exc}", url_healthz, gio_vn)
    if status != 200:
        return None, _loi(5, "HTTP_STATUS", f"LOI [HTTP_STATUS]: GET {url_healthz} trả mã HTTP {status} (cần 200)", url_healthz, gio_vn)
    return than, None


def kiem_cong_phat_hanh(
    base: str,
    sha: str | None = None,
    prod: list[str] | tuple[str, ...] | str | None = None,
    *,
    now: datetime | str | None = None,
    timeout: float = 10.0,
    truoc: bool = False,
    method: str = "GET",
) -> KetQuaCong:
    """Chạy toàn bộ cổng kiểm trước/sau phát hành staging (chỉ GET)."""
    if method != "GET":
        return _loi(2, "PHUONG_THUC", f"CHAN [PHUONG_THUC]: cổng phát hành chỉ dùng GET (nhận: {method!r})")
    url_healthz, host, loi_url = _tao_url_healthz(base)
    if loi_url or not url_healthz or not host:
        return _loi(2, "THAM_SO", f"CHAN [THAM_SO]: {loi_url}")
    ds_prod = tach_danh_sach_prod(prod)
    mau_trung = trung_ten_mien_prod(host, ds_prod)
    if mau_trung:
        return _loi(3, "PROD", f"CHAN [PROD]: base '{host}' trùng tên miền prod '{mau_trung}' trong --prod; prod luôn là CAN-LINH", url_healthz)
    try:
        dt_vn = lay_gio_vn(now)
    except ValueError as exc:
        return _loi(2, "THAM_SO", f"CHAN [THAM_SO]: giờ kiểm không hợp lệ ({exc})", url_healthz)
    chuoi_gio = dt_vn.strftime("%H:%M:%S")
    if not trong_khung_gio_vn(dt_vn):
        return _loi(4, "GIO_VN", f"CHAN [GIO_VN]: giờ VN hiện tại {chuoi_gio} nằm ngoài khung cho phép 07:00-22:00", url_healthz, chuoi_gio)
    sha_ky_vong = (sha or "").strip()
    if not truoc and not sha_ky_vong:
        return _loi(2, "THAM_SO", "CHAN [THAM_SO]: bắt buộc truyền --sha <BUILD_SHA> (hoặc --truoc khi kiểm trước deploy)", url_healthz, chuoi_gio)

    than, loi_http = _goi_get_healthz(url_healthz, ds_prod, timeout, chuoi_gio)
    if loi_http is not None or than is None:
        return loi_http or _loi(5, "MANG", "LOI [MANG]: không nhận được phản hồi", url_healthz, chuoi_gio)
    hop_le, sha_thuc_te, ly_do = trich_xuat_build_sha(than)
    if not hop_le or not sha_thuc_te:
        return _loi(6, "BUILD_SHA", f"LOI [BUILD_SHA]: {ly_do}", url_healthz, chuoi_gio)
    if sha_ky_vong and sha_thuc_te != sha_ky_vong:
        return _loi(
            6,
            "BUILD_SHA",
            f"LOI [BUILD_SHA]: GET {url_healthz} trả BUILD_SHA={sha_thuc_te!r} khác kỳ vọng {sha_ky_vong!r}",
            url_healthz,
            chuoi_gio,
            build_sha=sha_thuc_te,
        )
    return KetQuaCong(True, 0, "", f"OK: GET {url_healthz} BUILD_SHA={sha_thuc_te} (gio_vn={chuoi_gio})", sha_thuc_te, url_healthz, chuoi_gio)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cổng kiểm phát hành staging (chỉ GET /healthz, chặn prod, chặn ngoài 07:00-22:00 giờ VN).")
    ap.add_argument("--base", required=True, help="URL gốc của staging (vd: https://staging-event.ifagent.net)")
    ap.add_argument("--sha", default="", help="BUILD_SHA kỳ vọng từ GET /healthz")
    ap.add_argument("--prod", action="append", nargs="*", default=[], help="Danh sách tên miền prod cần chặn cứng")
    ap.add_argument("--truoc", action="store_true", help="Chế độ kiểm trước deploy staging (in BUILD_SHA hiện tại để lưu mốc rollback)")
    ap.add_argument("--timeout", type=float, default=10.0, help="Thời gian chờ tối đa mỗi lượt GET (giây)")
    ap.add_argument("--now", default=None, help="Giờ kiểm giả lập (ISO-8601 hoặc HH:MM giờ VN)")
    args = ap.parse_args(argv)
    kq = kiem_cong_phat_hanh(args.base, args.sha, args.prod, now=args.now, timeout=args.timeout, truoc=args.truoc, method="GET")
    print(kq.thong_diep, file=sys.stdout if kq.dat else sys.stderr)
    return kq.ma_thoat


if __name__ == "__main__":
    raise SystemExit(main())
