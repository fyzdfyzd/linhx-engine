#!/usr/bin/env python3
"""Sinh cấu hình Caddy và unit systemd cho các giao diện BU trong giao-dien/<bu>/."""
from __future__ import annotations

import argparse
import functools
import http.server
import ipaddress
import os
import pathlib
import re
import sys

_MAU_TEN_SITE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
_MAU_HOST_AN_TOAN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?")
_MAU_USER = re.compile(r"[a-z_][a-z0-9_-]{0,31}")
_MAU_BI_MAT_UNIT = re.compile(r"(TOKEN|SECRET|PASSWORD|KEY)=\S", re.IGNORECASE)

DAU_BAT_DAU_CADDY = "# BEGIN LINHX-GIAO-DIEN"
DAU_KET_THUC_CADDY = "# END LINHX-GIAO-DIEN"
FORM_URL_MAC_DINH = "http://127.0.0.1/linhx/api/method/linhx_core.crm.api_form.nhan_form"


def _kiem_ten_site(ten: object) -> str:
    if not isinstance(ten, str) or not _MAU_TEN_SITE.fullmatch(ten):
        raise ValueError(f"tên site giao diện không hợp lệ: {ten!r}")
    return ten


def _kiem_cong(cong: object) -> int:
    if isinstance(cong, bool) or not isinstance(cong, int) or not (1 <= cong <= 65535):
        raise ValueError(f"cổng không hợp lệ: {cong!r}")
    return cong


def _chuan_ip_nip(ip: object) -> str:
    if not isinstance(ip, str) or not ip.strip():
        raise ValueError(f"địa chỉ IP không hợp lệ: {ip!r}")
    ip_cham = ip.strip().replace("-", ".")
    try:
        dia_chi = ipaddress.IPv4Address(ip_cham)
    except ipaddress.AddressValueError as exc:
        raise ValueError(f"địa chỉ IPv4 không hợp lệ: {ip!r}") from exc
    return str(dia_chi).replace(".", "-")


def _kiem_dich(dich: object) -> str:
    if not isinstance(dich, str) or not dich.strip():
        raise ValueError(f"địa chỉ đích reverse_proxy không hợp lệ: {dich!r}")
    chu = dich.strip()
    try:
        ip_obj = ipaddress.ip_address(chu.strip("[]"))
        return f"[{ip_obj}]" if isinstance(ip_obj, ipaddress.IPv6Address) else str(ip_obj)
    except ValueError:
        if _MAU_HOST_AN_TOAN.fullmatch(chu) and ".." not in chu:
            return chu
        raise ValueError(f"địa chỉ đích reverse_proxy không hợp lệ: {dich!r}") from None


def _kiem_duong_dan_unit(duong: object) -> str:
    if isinstance(duong, pathlib.PurePath):
        chu = duong.as_posix()
    elif isinstance(duong, str):
        chu = duong.strip().replace("\\", "/")
    else:
        raise ValueError(f"đường dẫn thư mục không hợp lệ: {duong!r}")
    if not chu or any(ch in chu for ch in ("\r", "\n", "\x00", '"', "'", "\t", " ")):
        raise ValueError(f"đường dẫn thư mục chứa ký tự không an toàn cho systemd: {duong!r}")
    return chu.rstrip("/") or "/"


def cac_site(goc: str | os.PathLike[str]) -> list[dict[str, str]]:
    """Quét giao-dien/<ten> có server.mjs hoặc public/index.html, trả danh sách xếp theo tên."""
    goc_path = pathlib.Path(goc)
    tm_giao_dien = goc_path / "giao-dien"
    if tm_giao_dien.is_symlink() or not tm_giao_dien.is_dir():
        return []

    ket_qua: list[dict[str, str]] = []
    for muc in sorted(tm_giao_dien.iterdir(), key=lambda p: p.name):
        if muc.is_symlink() or not muc.is_dir():
            continue
        if not _MAU_TEN_SITE.fullmatch(muc.name):
            continue
        server_mjs = muc / "server.mjs"
        public_dir = muc / "public"
        index_html = public_dir / "index.html"
        co_server = not server_mjs.is_symlink() and server_mjs.is_file()
        co_index = (
            not public_dir.is_symlink()
            and public_dir.is_dir()
            and not index_html.is_symlink()
            and index_html.is_file()
        )
        if co_server or co_index:
            ket_qua.append(
                {
                    "ten": muc.name,
                    "thu_muc": muc.resolve().as_posix(),
                }
            )
    return ket_qua


def caddy(
    cac: list[dict[str, str]],
    ip: str = "35.198.251.2",
    cong_dau: int = 8101,
    dich: str = "127.0.0.1",
) -> str:
    """Sinh cấu hình Caddy cho từng giao diện BU theo thứ tự ổn định, cổng tăng dần từ cong_dau."""
    ip_gach = _chuan_ip_nip(ip)
    cong_goc = _kiem_cong(cong_dau)
    dich_sach = _kiem_dich(dich)

    if len(cac) > 0 and cong_goc + len(cac) - 1 > 65535:
        raise ValueError("dải cổng vượt quá 65535")

    da_thay: set[str] = set()
    cac_khoi: list[str] = []
    for idx, site in enumerate(cac):
        if not isinstance(site, dict) or "ten" not in site:
            raise ValueError(f"mục site không hợp lệ: {site!r}")
        ten = _kiem_ten_site(site["ten"])
        if ten in da_thay:
            raise ValueError(f"trùng tên site giao diện: {ten}")
        da_thay.add(ten)
        cong = cong_goc + idx
        cac_khoi.append(
            f"http://{ten}.{ip_gach}.nip.io {{\n"
            f"\treverse_proxy {dich_sach}:{cong}\n"
            f"}}"
        )
    if not cac_khoi:
        return ""
    return "\n\n".join(cac_khoi) + "\n"


def systemd(
    site: dict[str, str],
    cong: int,
    user: str = "www-data",
    form_url: str = FORM_URL_MAC_DINH,
) -> str:
    """Sinh nội dung unit systemd cho một site giao diện BU (MemoryMax=256M, Restart=always, không chứa bí mật)."""
    if not isinstance(site, dict) or "ten" not in site or "thu_muc" not in site:
        raise ValueError(f"thông tin site không hợp lệ: {site!r}")
    ten = _kiem_ten_site(site["ten"])
    cong_so = _kiem_cong(cong)
    thu_muc = _kiem_duong_dan_unit(site["thu_muc"])
    if not isinstance(user, str) or not _MAU_USER.fullmatch(user):
        raise ValueError(f"user systemd không hợp lệ: {user!r}")
    if not isinstance(form_url, str) or not form_url.strip() or any(c in form_url for c in ("\r", "\n", "\x00", '"', " ")):
        raise ValueError(f"form_url không hợp lệ: {form_url!r}")

    tm_thuc = pathlib.Path(str(site["thu_muc"]))
    chi_tinh = (
        tm_thuc.is_dir()
        and not (tm_thuc / "server.mjs").is_file()
        and (tm_thuc / "public" / "index.html").is_file()
    )
    if chi_tinh:
        script_nay = _kiem_duong_dan_unit(pathlib.Path(__file__).resolve())
        lenh_chay = f"/usr/bin/python3 {script_nay} phuc-vu-tinh --thu-muc {thu_muc}/public"
        ghi_chu = f"# Phục vụ tĩnh public/index.html khi {ten} không có server.mjs\n"
    else:
        lenh_chay = f"/usr/bin/node {thu_muc}/server.mjs"
        ghi_chu = ""

    noi_dung = (
        f"[Unit]\n"
        f"Description=LINHX Giao dien BU {ten}\n"
        f"After=network.target\n"
        f"\n"
        f"[Service]\n"
        f"{ghi_chu}"
        f"Type=simple\n"
        f"User={user}\n"
        f"Group={user}\n"
        f"WorkingDirectory={thu_muc}\n"
        f"Environment=NODE_ENV=production\n"
        f"Environment=TRUST_PROXY=1\n"
        f"Environment=LINHX_FORM_URL={form_url.strip()}\n"
        f"EnvironmentFile=-/etc/default/linhx-giao-dien\n"
        f"Environment=PORT={cong_so}\n"
        f"ExecStart={lenh_chay}\n"
        f"Restart=always\n"
        f"RestartSec=3\n"
        f"MemoryMax=256M\n"
        f"TasksMax=128\n"
        f"IPAccounting=yes\n"
        f"IPAddressDeny=any\n"
        f"IPAddressAllow=localhost\n"
        f"IPAddressAllow=172.16.0.0/12\n"
        f"IPAddressAllow=192.168.0.0/16\n"
        f"NoNewPrivileges=yes\n"
        f"PrivateTmp=yes\n"
        f"PrivateDevices=yes\n"
        f"ProtectSystem=strict\n"
        f"ProtectKernelTunables=yes\n"
        f"ProtectControlGroups=yes\n"
        f"RestrictSUIDSGID=yes\n"
        f"\n"
        f"[Install]\n"
        f"WantedBy=multi-user.target\n"
    )
    if _MAU_BI_MAT_UNIT.search(noi_dung):
        raise ValueError("unit systemd không được chứa biến bí mật")
    return noi_dung


def ghep_caddy(noi_dung_cu: str, khoi_giao_dien: str) -> str:
    """Thay thế hoặc gắn khối BEGIN/END LINHX-GIAO-DIEN vào Caddyfile hiện có."""
    mau_khoi = re.compile(
        rf"\n*{re.escape(DAU_BAT_DAU_CADDY)}\n.*?{re.escape(DAU_KET_THUC_CADDY)}\n*",
        re.DOTALL,
    )
    nen = mau_khoi.sub("\n", noi_dung_cu or "").rstrip()
    phan_moi = khoi_giao_dien.strip()
    if not phan_moi:
        return (nen + "\n") if nen else ""
    khoi_boc = f"{DAU_BAT_DAU_CADDY}\n{phan_moi}\n{DAU_KET_THUC_CADDY}\n"
    if not nen:
        return khoi_boc
    return f"{nen}\n\n{khoi_boc}"


def _phuc_vu_tinh(thu_muc_public: pathlib.Path, cong: int) -> int:
    goc = thu_muc_public.resolve()
    if not goc.is_dir():
        print(f"Thư mục không tồn tại: {goc}", file=sys.stderr)
        return 1

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            return

        def end_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            super().end_headers()

    handler_cls = functools.partial(Handler, directory=str(goc))
    with http.server.ThreadingHTTPServer(("0.0.0.0", cong), handler_cls) as srv:
        srv.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Công cụ sinh cấu hình Caddy và systemd cho giao diện BU.")
    sub = p.add_subparsers(dest="lenh", required=True)

    p_ds = sub.add_parser("cac-site", help="In TSV: <ten>\\t<cong>\\t<thu_muc>")
    p_ds.add_argument("--goc", required=True)
    p_ds.add_argument("--cong-dau", type=int, default=8101)

    p_cd = sub.add_parser("caddy", help="In khối Caddy cho mọi giao diện BU")
    p_cd.add_argument("--goc", required=True)
    p_cd.add_argument("--ip", default="35.198.251.2")
    p_cd.add_argument("--cong-dau", type=int, default=8101)
    p_cd.add_argument("--dich", default="127.0.0.1")

    p_gc = sub.add_parser("ghep-caddy", help="Ghép khối giao diện vào Caddyfile hiện có")
    p_gc.add_argument("--caddyfile", required=True)
    p_gc.add_argument("--goc", required=True)
    p_gc.add_argument("--ip", default="35.198.251.2")
    p_gc.add_argument("--cong-dau", type=int, default=8101)
    p_gc.add_argument("--dich", default="127.0.0.1")

    p_sd = sub.add_parser("systemd", help="In unit systemd cho một giao diện BU")
    p_sd.add_argument("--goc", required=True)
    p_sd.add_argument("--ten", required=True)
    p_sd.add_argument("--cong-dau", type=int, default=8101)
    p_sd.add_argument("--user", default="www-data")
    p_sd.add_argument("--form-url", default=FORM_URL_MAC_DINH)

    p_pv = sub.add_parser("phuc-vu-tinh", help="Máy chủ tĩnh dự phòng khi site chỉ có public/index.html")
    p_pv.add_argument("--thu-muc", required=True)

    args = p.parse_args(argv)
    if args.lenh == "cac-site":
        cong_goc = _kiem_cong(args.cong_dau)
        for idx, s in enumerate(cac_site(args.goc)):
            print(f"{s['ten']}\t{cong_goc + idx}\t{s['thu_muc']}")
        return 0

    if args.lenh == "caddy":
        cs = cac_site(args.goc)
        sys.stdout.write(caddy(cs, ip=args.ip, cong_dau=args.cong_dau, dich=args.dich))
        return 0

    if args.lenh == "ghep-caddy":
        cs = cac_site(args.goc)
        khoi = caddy(cs, ip=args.ip, cong_dau=args.cong_dau, dich=args.dich)
        cf_path = pathlib.Path(args.caddyfile)
        cu = cf_path.read_text(encoding="utf-8") if cf_path.is_file() else ""
        sys.stdout.write(ghep_caddy(cu, khoi))
        return 0

    if args.lenh == "systemd":
        cs = cac_site(args.goc)
        cong_goc = _kiem_cong(args.cong_dau)
        for idx, s in enumerate(cs):
            if s["ten"] == args.ten:
                sys.stdout.write(
                    systemd(s, cong_goc + idx, user=args.user, form_url=args.form_url)
                )
                return 0
        print(f"Không tìm thấy site giao diện: {args.ten}", file=sys.stderr)
        return 1

    if args.lenh == "phuc-vu-tinh":
        cong = _kiem_cong(int(os.environ.get("PORT", "8080")))
        return _phuc_vu_tinh(pathlib.Path(args.thu_muc), cong)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
