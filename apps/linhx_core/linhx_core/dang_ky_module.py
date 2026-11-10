"""Đăng ký và tra cứu module theo khai báo apps/<app>/module.json (thuần Python)."""
from __future__ import annotations

import heapq
import json
import pathlib
import re

LOP_HOP_LE = ("loi", "adapter", "goi")
THU_TU_LOP = {"loi": 0, "adapter": 1, "goi": 2}
LOAI_HAM = ("nghe", "cung_cap", "giao")

_MAU_SEMVER = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")
_MAU_DIEU_KIEN = re.compile(r"^(>=|<=|!=|==|=|>|<|\^|~=)?\s*([0-9]+\.[0-9]+\.[0-9]+)$")


def _tach_semver(phien_ban: object, nhan: str) -> tuple[int, int, int]:
    if not isinstance(phien_ban, str):
        raise ValueError(f"{nhan}: phiên bản '{phien_ban}' không phải semver x.y.z")
    khop = _MAU_SEMVER.fullmatch(phien_ban.strip())
    if not khop:
        raise ValueError(f"{nhan}: phiên bản '{phien_ban}' không phải semver x.y.z")
    return int(khop.group(1)), int(khop.group(2)), int(khop.group(3))


def _tach_rang_buoc_loi(can_loi: object, ten_app: str) -> list[tuple[str, tuple[int, int, int]]]:
    if not isinstance(can_loi, str) or not can_loi.strip():
        raise ValueError(f"{ten_app}: trường 'can_loi' không hợp lệ ({can_loi!r})")
    danh_sach: list[tuple[str, tuple[int, int, int]]] = []
    for phan in can_loi.split(","):
        muc = phan.strip()
        khop = _MAU_DIEU_KIEN.fullmatch(muc)
        if not khop:
            raise ValueError(f"{ten_app}: trường 'can_loi' không hợp lệ ({can_loi!r})")
        toan_tu = khop.group(1) or "=="
        if toan_tu == "=":
            toan_tu = "=="
        danh_sach.append((toan_tu, _tach_semver(khop.group(2), ten_app)))
    return danh_sach


def _thoa_dieu_kien(ban_loi: tuple[int, int, int], toan_tu: str, moc: tuple[int, int, int]) -> bool:
    if toan_tu == ">=":
        return ban_loi >= moc
    if toan_tu == "<=":
        return ban_loi <= moc
    if toan_tu == ">":
        return ban_loi > moc
    if toan_tu == "<":
        return ban_loi < moc
    if toan_tu == "==":
        return ban_loi == moc
    if toan_tu == "!=":
        return ban_loi != moc
    lon, vua, nho = moc
    if toan_tu == "~=":
        return moc <= ban_loi < (lon, vua + 1, 0)
    if toan_tu == "^":
        if lon > 0:
            return moc <= ban_loi < (lon + 1, 0, 0)
        if vua > 0:
            return moc <= ban_loi < (0, vua + 1, 0)
        return ban_loi == (0, 0, nho)
    return False


def _la_duong_ham_hop_le(duong_ham: object) -> bool:
    if not isinstance(duong_ham, str) or "." not in duong_ham:
        return False
    cac_phan = duong_ham.split(".")
    return len(cac_phan) >= 2 and all(phan.isidentifier() for phan in cac_phan)


def _kiem_bang_ham(gia_tri: object, truong: str, ten_app: str) -> dict[str, str]:
    if gia_tri is None:
        return {}
    if not isinstance(gia_tri, dict):
        raise ValueError(f"{ten_app}: trường '{truong}' phải là object")
    ket_qua: dict[str, str] = {}
    for khoa, duong_ham in gia_tri.items():
        if not isinstance(khoa, str) or not khoa.strip():
            raise ValueError(f"{ten_app}: khoá trong '{truong}' không hợp lệ ({khoa!r})")
        if not _la_duong_ham_hop_le(duong_ham):
            raise ValueError(f"{ten_app}: đường hàm của '{truong}.{khoa}' không hợp lệ ({duong_ham!r})")
        ket_qua[khoa] = duong_ham
    return ket_qua


def doc(duong: str | pathlib.Path) -> dict:
    """Đọc và kiểm tra tính hợp lệ của một tệp module.json."""
    duong_tep = pathlib.Path(duong)
    ten_goi_y = duong_tep.parent.name or duong_tep.name
    try:
        du_lieu = json.loads(duong_tep.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{ten_goi_y}: không đọc được module.json ({exc})") from exc

    if not isinstance(du_lieu, dict):
        raise ValueError(f"{ten_goi_y}: nội dung module.json phải là object JSON")

    ten = du_lieu.get("ten")
    if not isinstance(ten, str) or not ten.strip():
        raise ValueError(f"{ten_goi_y}: thiếu hoặc sai trường 'ten'")
    ten = ten.strip()

    ban = du_lieu.get("ban")
    if not isinstance(ban, str) or not _MAU_SEMVER.fullmatch(ban):
        raise ValueError(f"{ten}: thiếu hoặc sai trường 'ban' semver x.y.z ({ban!r})")

    lop = du_lieu.get("lop")
    if not isinstance(lop, str) or lop not in LOP_HOP_LE:
        raise ValueError(f"{ten}: thiếu hoặc sai trường 'lop' ({lop!r})")

    if "can_loi" in du_lieu and du_lieu["can_loi"] is not None:
        _tach_rang_buoc_loi(du_lieu["can_loi"], ten)

    phu_thuoc_goc = du_lieu.get("phu_thuoc", [])
    if phu_thuoc_goc is None:
        phu_thuoc_goc = []
    if not isinstance(phu_thuoc_goc, list) or not all(
        isinstance(x, str) and x.strip() for x in phu_thuoc_goc
    ):
        raise ValueError(f"{ten}: trường 'phu_thuoc' phải là danh sách tên app")

    ket_qua = dict(du_lieu)
    ket_qua["ten"] = ten
    ket_qua["ban"] = ban
    ket_qua["lop"] = lop
    ket_qua["phu_thuoc"] = list(dict.fromkeys(x.strip() for x in phu_thuoc_goc))
    for truong in LOAI_HAM:
        ket_qua[truong] = _kiem_bang_ham(du_lieu.get(truong), truong, ten)
    return ket_qua


def quet(thu_muc_apps: str | pathlib.Path, ban_loi: str | None = None) -> list[dict]:
    """Quét mọi module.json trong thu_muc_apps, kiểm tra can_loi và xếp phụ thuộc đứng trước."""
    goc = pathlib.Path(thu_muc_apps)
    if not goc.is_dir():
        raise ValueError(f"thư mục apps không tồn tại: {goc}")

    theo_ten: dict[str, dict] = {}
    for thu_muc in sorted(goc.iterdir(), key=lambda p: p.name):
        if not thu_muc.is_dir() or thu_muc.name.startswith("."):
            continue
        tep_module = thu_muc / "module.json"
        if not tep_module.is_file():
            continue
        khai_bao = doc(tep_module)
        ten = khai_bao["ten"]
        if ten in theo_ten:
            raise ValueError(f"{ten}: trùng tên module trong {goc}")
        theo_ten[ten] = khai_bao

    if ban_loi is None:
        if "linhx_core" in theo_ten:
            ban_loi = theo_ten["linhx_core"]["ban"]
        else:
            raise ValueError("thiếu tham số ban_loi")
    so_ban_loi = _tach_semver(ban_loi, "ban_loi")

    for ten, khai_bao in theo_ten.items():
        can_loi = khai_bao.get("can_loi")
        if can_loi is not None:
            rang_buoc = _tach_rang_buoc_loi(can_loi, ten)
            if not all(_thoa_dieu_kien(so_ban_loi, op, moc) for op, moc in rang_buoc):
                raise ValueError(
                    f"{ten}: can_loi '{can_loi}' không khớp phiên bản lõi '{ban_loi}'"
                )

    nguoi_phu_thuoc: dict[str, list[str]] = {ten: [] for ten in theo_ten}
    bac_vao: dict[str, int] = {ten: 0 for ten in theo_ten}

    for ten, khai_bao in theo_ten.items():
        for dep in khai_bao["phu_thuoc"]:
            if dep not in theo_ten:
                raise ValueError(f"{ten}: thiếu module phụ thuộc '{dep}'")
            if dep == ten:
                raise ValueError(f"{ten}: vòng phụ thuộc tự tham chiếu '{ten}'")
            nguoi_phu_thuoc[dep].append(ten)
            bac_vao[ten] += 1

    hang_doi: list[tuple[int, str]] = [
        (THU_TU_LOP[theo_ten[ten]["lop"]], ten)
        for ten, bac in bac_vao.items()
        if bac == 0
    ]
    heapq.heapify(hang_doi)

    thu_tu: list[dict] = []
    while hang_doi:
        _, ten = heapq.heappop(hang_doi)
        thu_tu.append(theo_ten[ten])
        for con in nguoi_phu_thuoc[ten]:
            bac_vao[con] -= 1
            if bac_vao[con] == 0:
                heapq.heappush(hang_doi, (THU_TU_LOP[theo_ten[con]["lop"]], con))

    if len(thu_tu) < len(theo_ten):
        con_lai = sorted(ten for ten, bac in bac_vao.items() if bac > 0)
        tap_con_lai = set(con_lai)
        hien_tai = con_lai[0]
        duong_di: list[str] = []
        vi_tri: dict[str, int] = {}
        while hien_tai not in vi_tri:
            vi_tri[hien_tai] = len(duong_di)
            duong_di.append(hien_tai)
            hien_tai = next(
                dep for dep in theo_ten[hien_tai]["phu_thuoc"] if dep in tap_con_lai
            )
        chu_trinh = duong_di[vi_tri[hien_tai] :] + [hien_tai]
        bi_chan = [ten for ten in con_lai if ten not in chu_trinh]
        chi_tiet = f" (chặn: {', '.join(bi_chan)})" if bi_chan else ""
        raise ValueError(f"vòng phụ thuộc module: {' -> '.join(chu_trinh)}{chi_tiet}")

    return thu_tu


def tim_ham(danh_sach: list[dict], loai: str, khoa: str) -> list[str]:
    """Tra danh sách đường dẫn 'module.ham' theo loại (nghe/cung_cap/giao) và khoá, giữ thứ tự quet."""
    if loai not in LOAI_HAM:
        raise ValueError(f"loại tra hàm không hợp lệ: {loai!r}")
    if not isinstance(khoa, str) or not khoa:
        return []
    ket_qua: list[str] = []
    for khai_bao in danh_sach:
        bang = khai_bao.get(loai)
        if not isinstance(bang, dict) or khoa not in bang:
            continue
        gia_tri = bang[khoa]
        if isinstance(gia_tri, str) and gia_tri:
            ket_qua.append(gia_tri)
        elif isinstance(gia_tri, list):
            ket_qua.extend(x for x in gia_tri if isinstance(x, str) and x)
    return ket_qua
