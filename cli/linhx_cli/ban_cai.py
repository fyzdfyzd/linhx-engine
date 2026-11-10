"""Tạo bản cài cho một BU hay OPC bằng một lệnh (thuần Python, không import frappe)."""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess

GOC_MAC_DINH = pathlib.Path(__file__).resolve().parents[2]
MAU_TEN_BAN_CAI = re.compile(r"^[a-z][a-z0-9-]{1,30}$")
MAU_TEN_THU_MUC = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")
MAU_TEN_MIEN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.-]{0,252}$")


def _xep_goi_theo_phu_thuoc(goi: list[str] | tuple[str, ...], thu_muc_apps: pathlib.Path) -> list[str]:
    da_xong: set[str] = {"linhx_core"}
    dang_duyet: set[str] = set()
    thu_tu_goi: list[str] = []

    def _them_goi(ten_goi: str) -> None:
        if not isinstance(ten_goi, str) or not MAU_TEN_THU_MUC.fullmatch(ten_goi):
            raise ValueError(f"Tên gói không hợp lệ: {ten_goi!r}")
        tep_mod = thu_muc_apps / ten_goi / "module.json"
        if not tep_mod.is_file():
            raise ValueError(f"Gói không tồn tại hoặc thiếu module.json: {ten_goi!r}")
        if ten_goi in da_xong:
            return
        if ten_goi in dang_duyet:
            raise ValueError(f"Vòng phụ thuộc gói: {ten_goi!r}")
        try:
            du_lieu = json.loads(tep_mod.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Không đọc được module.json của {ten_goi}: {exc}") from exc
        if not isinstance(du_lieu, dict):
            raise ValueError(f"module.json của {ten_goi} phải là một JSON object")
        phu_thuoc = du_lieu.get("phu_thuoc") or []
        if not isinstance(phu_thuoc, list) or not all(isinstance(x, str) and x.strip() for x in phu_thuoc):
            raise ValueError(f"Trường phu_thuoc của {ten_goi} không hợp lệ")

        dang_duyet.add(ten_goi)
        for dep in phu_thuoc:
            dep_sach = dep.strip()
            if dep_sach == "linhx_core":
                continue
            _them_goi(dep_sach)
        dang_duyet.remove(ten_goi)
        da_xong.add(ten_goi)
        thu_tu_goi.append(ten_goi)

    for g in goi:
        _them_goi(g)

    return thu_tu_goi


def ke_hoach(
    ten: str,
    giao_dien: str | None,
    goi: list[str],
    ten_mien: str,
    goc: str | pathlib.Path = GOC_MAC_DINH,
) -> dict:
    """Sinh kế hoạch tạo bản cài cho một BU/OPC."""
    if not isinstance(ten, str) or not MAU_TEN_BAN_CAI.fullmatch(ten):
        raise ValueError(f"Tên bản cài không hợp lệ: {ten!r}")

    if not isinstance(ten_mien, str):
        raise ValueError(f"Tên miền không hợp lệ: {ten_mien!r}")
    ten_mien_sach = ten_mien.strip()
    if not ten_mien_sach or ".." in ten_mien_sach or not MAU_TEN_MIEN.fullmatch(ten_mien_sach):
        raise ValueError(f"Tên miền không hợp lệ: {ten_mien!r}")

    goc_path = pathlib.Path(goc)
    if giao_dien is not None:
        if not isinstance(giao_dien, str) or not MAU_TEN_THU_MUC.fullmatch(giao_dien):
            raise ValueError(f"Tên giao diện không hợp lệ: {giao_dien!r}")
        if not (goc_path / "giao-dien" / giao_dien).is_dir():
            raise ValueError(f"Giao diện không tồn tại: {giao_dien!r}")

    if goi is None:
        ds_goi: list[str] = []
    elif isinstance(goi, (list, tuple)):
        ds_goi = list(goi)
    else:
        raise ValueError("Danh sách gói phải là list")

    thu_tu_goi = _xep_goi_theo_phu_thuoc(ds_goi, goc_path / "apps")
    apps_cai = ["linhx_core", *thu_tu_goi]

    buoc: list[list[str]] = [
        ["bench", "new-site", ten_mien_sach],
        *[["bench", "--site", ten_mien_sach, "install-app", app] for app in apps_cai],
        ["bench", "--site", ten_mien_sach, "migrate"],
    ]

    return {
        "ten": ten,
        "ten_mien": ten_mien_sach,
        "giao_dien": giao_dien,
        "goi": thu_tu_goi,
        "cau_hinh": f"deploy/sites/{ten}.json",
        "buoc": buoc,
    }


def _doc_env_file(duong: pathlib.Path) -> dict[str, str]:
    kq: dict[str, str] = {}
    if not duong.is_file():
        return kq
    try:
        for dong in duong.read_text(encoding="utf-8").splitlines():
            s = dong.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            kq[k.strip()] = v.strip().strip("'\"")
    except OSError:
        pass
    return kq


def _tim_docker_prefix(container: str) -> list[str] | None:
    if not shutil.which("docker"):
        return None
    for prefix in (["docker"], ["sudo", "-n", "docker"]):
        r = subprocess.run(
            [*prefix, "inspect", container],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            return prefix
    return None


def tao_ban_cai(
    ten: str,
    ten_mien: str,
    giao_dien: str | None = None,
    goi: list[str] | None = None,
    chay_thu: bool = False,
    goc: str | pathlib.Path = GOC_MAC_DINH,
    bench_dir: str | pathlib.Path | None = None,
    db_root_password: str | None = None,
    admin_password: str | None = None,
) -> dict:
    """Tạo bản cài BU/OPC: ghi deploy/sites/<ten>.json và chạy từng bước khi không phải chạy thử."""
    kh = ke_hoach(ten=ten, giao_dien=giao_dien, goi=goi or [], ten_mien=ten_mien, goc=goc)
    if chay_thu:
        return kh

    goc_path = pathlib.Path(goc)
    duong_cau_hinh = goc_path / kh["cau_hinh"]
    duong_cau_hinh.parent.mkdir(parents=True, exist_ok=True)
    noi_dung_cau_hinh = {
        "ten": kh["ten"],
        "ten_mien": kh["ten_mien"],
        "giao_dien": kh["giao_dien"],
        "goi": kh["goi"],
        "modules": {
            "crm": True,
            "pay": True,
        },
    }
    duong_cau_hinh.write_text(
        json.dumps(noi_dung_cau_hinh, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    env_deploy = _doc_env_file(goc_path / "deploy" / ".env")
    db_pw = (
        db_root_password
        or os.environ.get("DB_ROOT_PASSWORD")
        or os.environ.get("MARIADB_ROOT_PASSWORD")
        or env_deploy.get("DB_ROOT_PASSWORD")
    )
    adm_pw = (
        admin_password
        or os.environ.get("ADMIN_PASSWORD")
        or env_deploy.get("ADMIN_PASSWORD")
    )

    container = os.environ.get("LINHX_BACKEND_CONTAINER", "linhx-engine-backend-1")
    docker_prefix = None if bench_dir else _tim_docker_prefix(container)

    for b in kh["buoc"]:
        lenh = list(b)
        if "new-site" in lenh:
            if docker_prefix:
                kiem_site = subprocess.run(
                    [*docker_prefix, "exec", container, "test", "-f", f"sites/{kh['ten_mien']}/site_config.json"],
                    check=False,
                )
                if kiem_site.returncode == 0:
                    continue
            else:
                thu_muc_bench = pathlib.Path(bench_dir) if bench_dir else goc_path
                if (thu_muc_bench / "sites" / kh["ten_mien"] / "site_config.json").is_file():
                    continue
            lenh.append("--mariadb-user-host-login-scope=%")
            if db_pw:
                lenh.extend(["--db-root-password", db_pw])
            if adm_pw:
                lenh.extend(["--admin-password", adm_pw])
        elif "install-app" in lenh:
            app_cai = lenh[-1]
            if docker_prefix:
                da_cai = subprocess.run(
                    [*docker_prefix, "exec", container, "bench", "--site", kh["ten_mien"], "list-apps"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if da_cai.returncode == 0 and app_cai in da_cai.stdout.split():
                    continue

        if docker_prefix:
            r = subprocess.run([*docker_prefix, "exec", container, *lenh], check=False)
        else:
            thu_muc_bench = pathlib.Path(bench_dir) if bench_dir else goc_path
            r = subprocess.run(lenh, cwd=str(thu_muc_bench), check=False)
        if r.returncode != 0:
            raise RuntimeError(f"Bước cài đặt thất bại (mã thoát {r.returncode}): {b[0]} {b[1]}")

    return kh
