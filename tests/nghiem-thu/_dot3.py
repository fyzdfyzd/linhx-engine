"""Kiểm dùng chung đợt 3 (lõi / adapter / gói, Linh duyệt 10/11/2026)."""
import ast
import json
import re

from _chung import GOC, khong_import_frappe_dau_file

APPS = GOC / "apps"
LOP = {"loi", "adapter", "goi"}


def doc_module_json(app):
    p = APPS / app / "module.json"
    assert p.exists(), f"thiếu apps/{app}/module.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d.get("ten") == app and d.get("lop") in LOP and re.fullmatch(r"\d+\.\d+\.\d+", str(d.get("ban", "")))
    return d


def kiem_app(app, lop):
    """App Frappe đủ khung + module.json đúng lớp."""
    goc = APPS / app
    for f in ["pyproject.toml", f"{app}/__init__.py", f"{app}/hooks.py", f"{app}/modules.txt"]:
        assert (goc / f).exists(), f"thiếu apps/{app}/{f}"
    d = doc_module_json(app)
    assert d["lop"] == lop, f"{app} phải là lớp {lop}"
    return d


def cac_import(app):
    """(file, module) mọi import linhx_* trong app (bỏ test_*.py)."""
    ra = []
    for p in (APPS / app).rglob("*.py"):
        if p.name.startswith("test_"):
            continue
        try:
            cay = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for n in ast.walk(cay):
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                ra.append((p, n.module))
            elif isinstance(n, ast.Import):
                ra += [(p, a.name) for a in n.names]
    return [(p, m) for p, m in ra if m.startswith("linhx_")]


def kiem_kien_truc():
    """Lõi chỉ import lõi (không adapter/gói); adapter/gói chỉ import linhx_core.api từ lõi; gói không import gói khác."""
    loi = []
    cac = {x.name: doc_module_json(x.name)["lop"] for x in APPS.iterdir() if (x / "module.json").exists()}
    for a in sorted(cac):
        lop = cac[a]
        for p, m in cac_import(a):
            goc = m.split(".")[0]
            if goc == a or (lop == "loi" and cac.get(goc) == "loi"):
                continue  # trong app, hoặc lõi gọi lõi (linhx_worker <-> linhx_core)
            r = p.relative_to(GOC).as_posix()
            if lop == "loi":
                loi.append(f"{r}: lõi import {m}")
            elif goc == "linhx_core" and not (m == "linhx_core.api" or m.startswith("linhx_core.api.")):
                loi.append(f"{r}: {lop} chỉ được import linhx_core.api, đang import {m}")
            elif goc != "linhx_core" and lop == "goi":
                loi.append(f"{r}: gói import app khác {m}")
    assert not loi, "\n".join(loi)


def kiem_da_chuyen(cu, moi):
    """File cũ trong linhx_core đã xoá, file mới có, không import frappe đầu file."""
    for c, m in zip(cu, moi):
        assert not (APPS / "linhx_core" / "linhx_core" / c).exists(), f"còn file cũ apps/linhx_core/linhx_core/{c} (sửa luôn, không để file chuyển tiếp)"
        assert (APPS / m).exists(), f"thiếu apps/{m}"
        khong_import_frappe_dau_file(APPS / m)
