"""Thực thi lệnh `linhx tao-site <ten> --cau-hinh <file>`."""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

CAC_MODULE_MAC_DINH = ("crm", "pay")
CAC_APP_BAT_BUOC = ("linhx_core", "linhx_worker")
TEN_SITE_HOP_LE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
TEN_MODULE_HOP_LE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")


def _co_bat(gia_tri) -> int:
    if isinstance(gia_tri, bool):
        return 1 if gia_tri else 0
    if isinstance(gia_tri, (int, float)):
        return 1 if gia_tri == 1 else 0
    if isinstance(gia_tri, str):
        return 1 if gia_tri.strip().lower() in ("1", "true", "yes", "on") else 0
    return 0


def _kiem_tra_ten_site(ten: str) -> str:
    ten_sach = str(ten or "").strip()
    if not ten_sach or ".." in ten_sach or not TEN_SITE_HOP_LE.match(ten_sach):
        raise ValueError(f"Tên site không hợp lệ: {ten!r}")
    return ten_sach


def _doc_co_module(duong_cau_hinh: str | pathlib.Path) -> dict[str, int]:
    p = pathlib.Path(duong_cau_hinh)
    du_lieu = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(du_lieu, dict):
        raise ValueError("File cấu hình phải là một JSON object")
    modules = du_lieu.get("modules")
    if modules is None:
        modules = {}
    if not isinstance(modules, dict):
        raise ValueError("Trường 'modules' trong file cấu hình phải là một JSON object")

    co: dict[str, int] = {}
    for m in CAC_MODULE_MAC_DINH:
        co[f"bat_{m}"] = _co_bat(modules.get(m, False))

    for k, v in modules.items():
        ten_mod = str(k or "").strip().lower()
        if ten_mod in CAC_MODULE_MAC_DINH:
            co[f"bat_{ten_mod}"] = _co_bat(v)
            continue
        if not TEN_MODULE_HOP_LE.match(ten_mod):
            raise ValueError(f"Tên module không hợp lệ: {k!r}")
        co[f"bat_{ten_mod}"] = _co_bat(v)

    return co


def sinh_lenh_tao_site(
    ten: str,
    duong_cau_hinh: str | pathlib.Path,
    sites_dir: str | pathlib.Path = "sites",
) -> list[str]:
    """Sinh danh sách lệnh bench cần chạy để tạo hoặc cập nhật site."""
    ten_sach = _kiem_tra_ten_site(ten)
    co_module = _doc_co_module(duong_cau_hinh)
    thu_muc_sites = pathlib.Path(sites_dir)
    site_config = thu_muc_sites / ten_sach / "site_config.json"
    da_co_site = site_config.is_file()

    kwargs_json = json.dumps(
        {
            "doctype": "LX Cau Hinh",
            "name": "LX Cau Hinh",
            "fieldname": co_module,
        },
        ensure_ascii=False,
    )
    lenh_dat_co = f"bench --site {ten_sach} execute frappe.client.set_value --kwargs '{kwargs_json}'"

    if not da_co_site:
        lenh = [
            (
                f"bench new-site {ten_sach} --mariadb-user-host-login-scope=% "
                '--db-root-password "${DB_ROOT_PASSWORD:?}" '
                '--admin-password "${ADMIN_PASSWORD:?}"'
            ),
        ]
        for app in CAC_APP_BAT_BUOC:
            lenh.append(f"bench --site {ten_sach} install-app {app}")
        lenh.append(lenh_dat_co)
        return lenh

    lenh = []
    for app in CAC_APP_BAT_BUOC:
        lenh.append(
            f"bench --site {ten_sach} list-apps | grep -E '^{app}([[:space:]]|$)' >/dev/null "
            f"|| bench --site {ten_sach} install-app {app}"
        )
    lenh.append(f"bench --site {ten_sach} migrate")
    lenh.append(lenh_dat_co)
    return lenh


def _xac_dinh_bench_dir(sites_dir: str | pathlib.Path, bench_dir: str | pathlib.Path | None = None) -> pathlib.Path:
    if bench_dir:
        return pathlib.Path(bench_dir).resolve()
    sd = pathlib.Path(sites_dir).resolve()
    if (sd.parent / "apps").is_dir() or sd.name == "sites":
        return sd.parent
    return pathlib.Path.cwd()


def tao_site(
    ten: str,
    duong_cau_hinh: str | pathlib.Path,
    sites_dir: str | pathlib.Path = "sites",
    chay_thu: bool = False,
    bench_dir: str | pathlib.Path | None = None,
    db_root_password: str | None = None,
    admin_password: str | None = None,
) -> list[str]:
    """Tạo hoặc cập nhật site Frappe theo cấu hình module."""
    lenh = sinh_lenh_tao_site(ten=ten, duong_cau_hinh=duong_cau_hinh, sites_dir=sites_dir)
    if chay_thu:
        return lenh

    thu_muc_bench = _xac_dinh_bench_dir(sites_dir=sites_dir, bench_dir=bench_dir)
    env = dict(os.environ)
    if db_root_password is not None:
        env["DB_ROOT_PASSWORD"] = db_root_password
    elif not env.get("DB_ROOT_PASSWORD") and env.get("MARIADB_ROOT_PASSWORD"):
        env["DB_ROOT_PASSWORD"] = env["MARIADB_ROOT_PASSWORD"]

    if admin_password is not None:
        env["ADMIN_PASSWORD"] = admin_password

    ten_sach = _kiem_tra_ten_site(ten)
    da_co_site = (pathlib.Path(sites_dir) / ten_sach / "site_config.json").is_file()
    if not da_co_site:
        if not env.get("DB_ROOT_PASSWORD") or not env.get("ADMIN_PASSWORD"):
            raise ValueError(
                "Cần cung cấp DB_ROOT_PASSWORD và ADMIN_PASSWORD (qua biến môi trường hoặc tham số) khi tạo site mới"
            )

    local_bin = str(pathlib.Path.home() / ".local" / "bin")
    path_hien_tai = env.get("PATH", "")
    if local_bin not in path_hien_tai.split(os.pathsep):
        env["PATH"] = f"{local_bin}{os.pathsep}{path_hien_tai}" if path_hien_tai else local_bin

    for buoc in lenh:
        r = subprocess.run(
            ["bash", "-c", buoc],
            cwd=str(thu_muc_bench),
            env=env,
            check=False,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Lệnh thất bại (mã thoát {r.returncode}): {buoc}")

    return lenh


def _tao_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="linhx", description="CLI quản trị bản cài LINHX ENGINE")
    sub = parser.add_subparsers(dest="lenh_con", required=True)

    p_tao = sub.add_parser("tao-site", help="Tạo bản cài mới hoặc cập nhật bản cài hiện có theo cấu hình")
    p_tao.add_argument("ten", help="Tên site (ví dụ: linhx.local)")
    p_tao.add_argument("--cau-hinh", required=True, dest="cau_hinh", help="Đường dẫn tới file JSON cấu hình")
    p_tao.add_argument(
        "--sites-dir",
        default="sites",
        dest="sites_dir",
        help="Thư mục sites của Frappe bench (mặc định: sites)",
    )
    p_tao.add_argument(
        "--bench-dir",
        default=None,
        dest="bench_dir",
        help="Thư mục gốc Frappe bench (mặc định: tự suy từ --sites-dir)",
    )
    p_tao.add_argument(
        "--chay-thu",
        action="store_true",
        dest="chay_thu",
        help="Chỉ in ra JSON danh sách lệnh sẽ chạy, không thực thi",
    )
    p_tao.add_argument(
        "--db-root-password",
        default=None,
        dest="db_root_password",
        help="Mật khẩu root MariaDB (hoặc lấy từ biến môi trường DB_ROOT_PASSWORD)",
    )
    p_tao.add_argument(
        "--admin-password",
        default=None,
        dest="admin_password",
        help="Mật khẩu Administrator cho site mới (hoặc lấy từ biến môi trường ADMIN_PASSWORD)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _tao_parser()
    args = parser.parse_args(argv)
    if args.lenh_con == "tao-site":
        try:
            lenh = tao_site(
                ten=args.ten,
                duong_cau_hinh=args.cau_hinh,
                sites_dir=args.sites_dir,
                chay_thu=args.chay_thu,
                bench_dir=args.bench_dir,
                db_root_password=args.db_root_password,
                admin_password=args.admin_password,
            )
        except Exception as exc:
            print(f"Lỗi: {exc}", file=sys.stderr)
            return 1
        if args.chay_thu:
            print(json.dumps({"lenh": lenh}, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
