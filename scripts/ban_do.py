#!/usr/bin/env python3
"""Bộ sinh bản đồ repo cho thợ: chữ ký hàm/lớp + trường DocType, một bậc import, có trần ký tự."""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import sys

THU_MUC_BO_QUA = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".next",
        "out",
        ".canh",
        ".canh-tho",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
TEP_CAU_HINH_GOI = frozenset({"pyproject.toml", "setup.py", "setup.cfg"})
GIOI_HAN_DOC_BYTE = 2 * 1024 * 1024


def _dong_dau_docstring(nut: ast.AST) -> str:
    doc = ast.get_docstring(nut, clean=True) or ""
    for dong in doc.splitlines():
        sach = dong.strip()
        if sach:
            return sach
    return ""


def _mot_dong_ast(nut: ast.AST) -> str:
    return " ".join(ast.unparse(nut).splitlines())


def _tom_tat_nut_py(nut: ast.stmt, thut: str = "") -> list[str]:
    if isinstance(nut, (ast.FunctionDef, ast.AsyncFunctionDef)):
        tu_khoa = "async def" if isinstance(nut, ast.AsyncFunctionDef) else "def"
        tham_so = _mot_dong_ast(nut.args)
        tra_ve = f" -> {_mot_dong_ast(nut.returns)}" if nut.returns is not None else ""
        dong = f"{thut}{tu_khoa} {nut.name}({tham_so}){tra_ve}:"
        mo_ta = _dong_dau_docstring(nut)
        if mo_ta:
            dong = f"{dong}  # {mo_ta}"
        return [dong]

    if isinstance(nut, ast.ClassDef):
        ke_thua = [_mot_dong_ast(b) for b in nut.bases] + [_mot_dong_ast(k) for k in nut.keywords]
        ngoac = f"({', '.join(ke_thua)})" if ke_thua else ""
        dong = f"{thut}class {nut.name}{ngoac}:"
        mo_ta = _dong_dau_docstring(nut)
        if mo_ta:
            dong = f"{dong}  # {mo_ta}"
        ket_qua = [dong]
        for con in nut.body:
            if isinstance(con, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                ket_qua.extend(_tom_tat_nut_py(con, thut + "  "))
        return ket_qua

    return []


def _phan_tich_ast(tep: Path) -> ast.Module | None:
    try:
        if not tep.is_file() or tep.stat().st_size > GIOI_HAN_DOC_BYTE:
            return None
        nguon = tep.read_text(encoding="utf-8-sig", errors="replace")
        return ast.parse(nguon, filename=str(tep))
    except (OSError, SyntaxError, ValueError):
        return None


def _tom_tat_cay_py(cay: ast.Module) -> str:
    cac_dong: list[str] = []
    for nut in cay.body:
        cac_dong.extend(_tom_tat_nut_py(nut))
    return "\n".join(cac_dong)


def tom_tat_file(duong: str | Path) -> str:
    """Tóm tắt chữ ký .py hoặc trường DocType .json; trả chuỗi rỗng với các loại file khác."""
    tep = Path(duong)
    try:
        if not tep.is_file() or tep.stat().st_size > GIOI_HAN_DOC_BYTE:
            return ""
    except OSError:
        return ""

    duoi = tep.suffix.lower()
    if duoi == ".py":
        cay = _phan_tich_ast(tep)
        if cay is None:
            return ""
        return _tom_tat_cay_py(cay)

    if duoi == ".json":
        try:
            chu = tep.read_text(encoding="utf-8-sig", errors="replace")
            if "DocType" not in chu:
                return ""
            du_lieu = json.loads(chu)
        except (OSError, ValueError, TypeError):
            return ""
        if not isinstance(du_lieu, dict) or du_lieu.get("doctype") != "DocType":
            return ""
        ten = str(du_lieu.get("name") or tep.stem).strip()
        ds_truong: list[str] = []
        for truong in du_lieu.get("fields") or []:
            if not isinstance(truong, dict):
                continue
            fn = str(truong.get("fieldname") or "").strip()
            ft = str(truong.get("fieldtype") or "").strip()
            if fn and ft:
                ds_truong.append(f"{fn}:{ft}")
        if ds_truong:
            return f"DocType {ten}: {', '.join(ds_truong)}"
        return f"DocType {ten}"

    return ""


def _bo_qua_thu_muc(ten: str) -> bool:
    return ten in THU_MUC_BO_QUA or "pytest-tmp" in ten or ten.endswith(".egg-info")


def _la_file_test(ten_file: str) -> bool:
    thap = ten_file.lower()
    return thap.startswith("test_") and thap.endswith(".py")


def _glob_re(mau: str) -> re.Pattern[str]:
    g = mau.strip().replace("\\", "/")
    while g.startswith("./"):
        g = g[2:]
    if g.endswith("/"):
        g += "**"
    ra = ""
    i = 0
    while i < len(g):
        if g.startswith("**/", i):
            ra += r"(?:.*/)?"
            i += 3
        elif g.startswith("**", i):
            ra += r".*"
            i += 2
        elif g[i] == "*":
            ra += r"[^/]*"
            i += 1
        elif g[i] == "?":
            ra += r"[^/]"
            i += 1
        else:
            ra += re.escape(g[i])
            i += 1
    return re.compile("^" + ra + "$")


def _quet_repo(goc: Path) -> tuple[list[str], set[str], set[str], list[str]]:
    ds_file: list[str] = []
    tap_py: set[str] = set()
    tap_co_init: set[str] = set()
    goc_uu_tien: set[str] = {""}
    tat_ca_thu_muc: set[str] = {""}

    goc_str = str(goc)
    for thu_muc_hien_tai, cac_thu_muc, cac_tep in os.walk(goc_str, followlinks=False):
        cac_thu_muc[:] = sorted(d for d in cac_thu_muc if not _bo_qua_thu_muc(d))
        rel_dir = os.path.relpath(thu_muc_hien_tai, goc_str).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        tat_ca_thu_muc.add(rel_dir)

        tap_ten_tep = set(cac_tep)
        if "__init__.py" in tap_ten_tep:
            tap_co_init.add(rel_dir)
        if tap_ten_tep & TEP_CAU_HINH_GOI:
            goc_uu_tien.add(rel_dir)

        for ten in sorted(cac_tep):
            if _la_file_test(ten):
                continue
            rel_tep = f"{rel_dir}/{ten}" if rel_dir else ten
            ds_file.append(rel_tep)
            if ten.lower().endswith(".py"):
                tap_py.add(rel_tep)

    for g in list(goc_uu_tien):
        thu_muc_src = f"{g}/src" if g else "src"
        if thu_muc_src in tat_ca_thu_muc:
            goc_uu_tien.add(thu_muc_src)

    goc_tu_goi: set[str] = set()
    for thu_muc_goi in tap_co_init:
        hien_tai = thu_muc_goi
        while hien_tai in tap_co_init and hien_tai != "":
            hien_tai = hien_tai.rsplit("/", 1)[0] if "/" in hien_tai else ""
        if hien_tai not in tap_co_init:
            goc_tu_goi.add(hien_tai)

    ds_file.sort()
    cac_goc = sorted(goc_uu_tien) + sorted(goc_tu_goi - goc_uu_tien)
    return ds_file, tap_py, tap_co_init, cac_goc


def _cac_goc_cho_file(rel_py: str, tap_co_init: set[str], cac_goc: list[str]) -> list[str]:
    thu_muc_cha = rel_py.rsplit("/", 1)[0] if "/" in rel_py else ""
    trong_nguon = rel_py == "nguon" or rel_py.startswith("nguon/")
    goc_hop_le = [
        g for g in cac_goc if trong_nguon or not (g == "nguon" or g.startswith("nguon/"))
    ]
    to_tien: list[str] = []
    for g in goc_hop_le:
        if g == "" or rel_py.startswith(g + "/"):
            to_tien.append(g)
    to_tien.sort(key=len, reverse=True)

    ket_qua: list[str] = []
    if thu_muc_cha not in tap_co_init:
        ket_qua.append(thu_muc_cha)
    for g in to_tien + goc_hop_le:
        if g not in ket_qua:
            ket_qua.append(g)
    return ket_qua


def _tim_module_tuyet_doi(ten_mod: str, tap_py: set[str], cac_goc: list[str]) -> str | None:
    phan = "/".join(p for p in ten_mod.split(".") if p)
    if not phan:
        return None
    for g in cac_goc:
        tien_to = f"{g}/{phan}" if g else phan
        ung_py = f"{tien_to}.py"
        if ung_py in tap_py:
            return ung_py
        ung_init = f"{tien_to}/__init__.py"
        if ung_init in tap_py:
            return ung_init
    return None


def _tim_import_cua_file(
    rel_py: str,
    cay: ast.Module,
    tap_py: set[str],
    tap_co_init: set[str],
    cac_goc: list[str],
) -> list[str]:
    goc_tim = _cac_goc_cho_file(rel_py, tap_co_init, cac_goc)
    ket_qua: list[str] = []

    def _them(duong_rel: str | None) -> None:
        if duong_rel and duong_rel != rel_py and duong_rel not in ket_qua:
            ket_qua.append(duong_rel)

    phan_thu_muc = rel_py.split("/")[:-1]

    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            for alias in nut.names:
                _them(_tim_module_tuyet_doi(alias.name, tap_py, goc_tim))
        elif isinstance(nut, ast.ImportFrom):
            if nut.level == 0:
                if not nut.module:
                    continue
                can_goc = False
                for alias in nut.names:
                    if alias.name != "*":
                        con = _tim_module_tuyet_doi(f"{nut.module}.{alias.name}", tap_py, goc_tim)
                        if con:
                            _them(con)
                        else:
                            can_goc = True
                    else:
                        can_goc = True
                if can_goc or not nut.names:
                    _them(_tim_module_tuyet_doi(nut.module, tap_py, goc_tim))
            else:
                if nut.level - 1 > len(phan_thu_muc):
                    continue
                co_so_phan = phan_thu_muc[: len(phan_thu_muc) - (nut.level - 1)]
                if nut.module:
                    co_so_phan = co_so_phan + [p for p in nut.module.split(".") if p]
                co_so = "/".join(co_so_phan)
                can_co_so = False
                for alias in nut.names:
                    if alias.name != "*":
                        ung = f"{co_so}/{alias.name}" if co_so else alias.name
                        if f"{ung}.py" in tap_py:
                            _them(f"{ung}.py")
                        elif f"{ung}/__init__.py" in tap_py:
                            _them(f"{ung}/__init__.py")
                        else:
                            can_co_so = True
                    else:
                        can_co_so = True
                if can_co_so:
                    if co_so:
                        if f"{co_so}.py" in tap_py:
                            _them(f"{co_so}.py")
                        elif f"{co_so}/__init__.py" in tap_py:
                            _them(f"{co_so}/__init__.py")
                    elif "__init__.py" in tap_py:
                        _them("__init__.py")

    return ket_qua


def _ghep_co_tran(cac_muc: list[tuple[str, str]], gioi_han: int) -> str:
    if gioi_han <= 0 or not cac_muc:
        return ""
    tran_noi_dung = gioi_han - 1 if gioi_han >= 2 else gioi_han
    cac_khoi: list[str] = []
    do_dai = 0

    for rel, noi_dung in cac_muc:
        dong_nd = [d for d in noi_dung.splitlines() if d.strip()]
        if not dong_nd:
            continue
        tieu_de = f"### {rel}"
        ngan_cach = "\n\n" if cac_khoi else ""
        khoi_day_du = tieu_de + "\n" + "\n".join(dong_nd)
        if do_dai + len(ngan_cach) + len(khoi_day_du) <= tran_noi_dung:
            cac_khoi.append(khoi_day_du)
            do_dai += len(ngan_cach) + len(khoi_day_du)
            continue

        toi_thieu = tieu_de + "\n" + dong_nd[0]
        if do_dai + len(ngan_cach) + len(toi_thieu) > tran_noi_dung:
            break

        dong_chon = [tieu_de, dong_nd[0]]
        do_dai_khoi = len(toi_thieu)
        for dong in dong_nd[1:]:
            if do_dai + len(ngan_cach) + do_dai_khoi + 1 + len(dong) > tran_noi_dung:
                break
            dong_chon.append(dong)
            do_dai_khoi += 1 + len(dong)
        cac_khoi.append("\n".join(dong_chon))
        break

    if not cac_khoi:
        return ""
    ket_qua = "\n\n".join(cac_khoi)
    if len(ket_qua) < gioi_han:
        ket_qua += "\n"
    return ket_qua


def ban_do(goc: str | Path, vung: list[str], gioi_han: int = 8000) -> str:
    """Sinh bản đồ Markdown cho các file khớp vùng rồi các file .py chúng import một bậc."""
    goc_path = Path(goc).resolve()
    if gioi_han <= 0 or not vung or not goc_path.is_dir():
        return ""

    ds_file, tap_py, tap_co_init, cac_goc = _quet_repo(goc_path)
    ds_vung: list[str] = []
    da_chon_vung: set[str] = set()

    for mau in vung:
        s = str(mau or "").strip().replace("\\", "/")
        while s.startswith("./"):
            s = s[2:]
        if not s:
            continue
        cac_bieu_thuc = [_glob_re(s)]
        if not any(ch in s for ch in "*?") and not s.endswith("/"):
            cac_bieu_thuc.append(_glob_re(s + "/**"))
        for rel in ds_file:
            if rel not in da_chon_vung and any(bt.match(rel) for bt in cac_bieu_thuc):
                da_chon_vung.add(rel)
                ds_vung.append(rel)

    bo_nho_cay: dict[str, ast.Module | None] = {}

    def _lay_cay(rel: str) -> ast.Module | None:
        if rel not in bo_nho_cay:
            bo_nho_cay[rel] = _phan_tich_ast(goc_path / rel)
        return bo_nho_cay[rel]

    ds_import: list[str] = []
    da_co_import: set[str] = set(da_chon_vung)
    for rel in ds_vung:
        if not rel.lower().endswith(".py"):
            continue
        cay = _lay_cay(rel)
        if cay is None:
            continue
        for imp_rel in _tim_import_cua_file(rel, cay, tap_py, tap_co_init, cac_goc):
            if imp_rel not in da_co_import:
                da_co_import.add(imp_rel)
                ds_import.append(imp_rel)

    ds_import.sort()

    cac_muc: list[tuple[str, str]] = []
    for rel in ds_vung + ds_import:
        if rel.lower().endswith(".py"):
            cay = _lay_cay(rel)
            nd = _tom_tat_cay_py(cay) if cay is not None else ""
        else:
            nd = tom_tat_file(goc_path / rel)
        if nd.strip():
            cac_muc.append((rel, nd))

    return _ghep_co_tran(cac_muc, gioi_han)


def main(argv: list[str] | None = None) -> int:
    bo_phan_tich = argparse.ArgumentParser(
        description="Sinh bản đồ chữ ký hàm/lớp và trường DocType theo vùng feature."
    )
    bo_phan_tich.add_argument("--goc", default=".", help="Thư mục gốc của repo")
    bo_phan_tich.add_argument(
        "--vung",
        nargs="+",
        action="extend",
        default=None,
        help="Mẫu glob vùng cần lấy bản đồ (có thể lặp lại)",
    )
    bo_phan_tich.add_argument(
        "--gioi-han",
        type=int,
        default=8000,
        help="Trần số ký tự tối đa của kết quả",
    )
    tham_so = bo_phan_tich.parse_args(argv)
    cac_vung = tham_so.vung if tham_so.vung else ["**"]

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ket_qua = ban_do(tham_so.goc, cac_vung, tham_so.gioi_han)
    if ket_qua:
        sys.stdout.write(ket_qua)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
