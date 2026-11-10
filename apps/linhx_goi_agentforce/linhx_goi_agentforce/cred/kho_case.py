"""Logic thuần Python cho Kho case có số (cred) và ghép nội dung Trang BU."""
from __future__ import annotations

import copy


def la_da_duyet(gia_tri: object) -> bool:
    """Trả True chỉ khi cờ da_duyet được bật rõ ràng (True hoặc 1)."""
    if isinstance(gia_tri, bool):
        return gia_tri is True
    if isinstance(gia_tri, int):
        return gia_tri == 1
    if isinstance(gia_tri, str):
        return gia_tri.strip().lower() in ("1", "true")
    return False


def _chuoi_sach(gia_tri: object) -> str:
    if gia_tri is None or isinstance(gia_tri, bool):
        return ""
    if not isinstance(gia_tri, str):
        gia_tri = str(gia_tri)
    return gia_tri.strip()


def kiem_case(case_dict: dict) -> dict:
    """Kiểm tra tính hợp lệ của một bản ghi LX Case và trả về bản chuẩn hoá."""
    if not isinstance(case_dict, dict):
        raise ValueError("Bản ghi case phải là dict")

    tieu_de = _chuoi_sach(case_dict.get("tieu_de"))
    if not tieu_de:
        raise ValueError("Tiêu đề case (tieu_de) không được để trống")

    chi_so = _chuoi_sach(case_dict.get("chi_so"))
    da_duyet = la_da_duyet(case_dict.get("da_duyet", False))
    if da_duyet and not chi_so:
        raise ValueError("Case đã duyệt bắt buộc phải có chỉ số kết quả (chi_so)")

    ket_qua = dict(case_dict)
    ket_qua["tieu_de"] = tieu_de
    ket_qua["khach_hang"] = _chuoi_sach(case_dict.get("khach_hang"))
    ket_qua["cho_phep_hien_ten"] = bool(la_da_duyet(case_dict.get("cho_phep_hien_ten", False)))
    ket_qua["chi_so"] = chi_so
    ket_qua["mo_ta"] = _chuoi_sach(case_dict.get("mo_ta"))
    ket_qua["da_duyet"] = bool(da_duyet)
    return ket_qua


def case_cong_khai(ds_case: list[dict] | None) -> list[dict]:
    """Chỉ trả các case đã duyệt (da_duyet == True/1) và có chi_so không rỗng.

    Case chưa duyệt (da_duyet False/0/None) hoặc thiếu tieu_de/chi_so tuyệt đối không ra danh sách công khai.
    Tên khách hàng (khach_hang) chỉ xuất ra khi có cờ cho_phep_hien_ten == True/1.
    Chỉ giữ các trường công khai an toàn để không rò rỉ dữ liệu nội bộ.
    """
    if not ds_case or not isinstance(ds_case, (list, tuple)):
        return []

    ket_qua: list[dict] = []
    for item in ds_case:
        if not isinstance(item, dict):
            continue
        if not la_da_duyet(item.get("da_duyet", False)):
            continue
        tieu_de = _chuoi_sach(item.get("tieu_de"))
        chi_so = _chuoi_sach(item.get("chi_so"))
        if not tieu_de or not chi_so:
            continue

        ban: dict[str, object] = {}
        if "name" in item and _chuoi_sach(item.get("name")):
            ban["name"] = _chuoi_sach(item.get("name"))
        ban["tieu_de"] = tieu_de
        if la_da_duyet(item.get("cho_phep_hien_ten", False)):
            ten_kh = _chuoi_sach(item.get("khach_hang"))
            if ten_kh:
                ban["khach_hang"] = ten_kh
        ban["chi_so"] = chi_so
        ban["mo_ta"] = _chuoi_sach(item.get("mo_ta"))
        ban["da_duyet"] = True
        ket_qua.append(ban)

    return ket_qua


def _muc_tu_case(case_item: dict, mau_ten: str = "") -> dict[str, str]:
    tieu_de = _chuoi_sach(case_item.get("tieu_de"))
    chi_so = _chuoi_sach(case_item.get("chi_so"))
    khach_hang = _chuoi_sach(case_item.get("khach_hang"))
    mo_ta = _chuoi_sach(case_item.get("mo_ta"))

    if mau_ten and "{tieu_de}" in mau_ten and "{chi_so}" in mau_ten:
        ten = (
            mau_ten.replace("{tieu_de}", tieu_de)
            .replace("{chi_so}", chi_so)
            .replace("{khach_hang}", khach_hang)
            .strip()
        )
    elif khach_hang and khach_hang.lower() not in tieu_de.lower():
        ten = f"{tieu_de} ({khach_hang}) — {chi_so}"
    else:
        ten = f"{tieu_de} — {chi_so}"

    return {
        "ten": ten,
        "mo_ta": mo_ta,
    }


def noi_dung_trang_bu(site_cfg: dict | None, ds_case: list[dict] | None = None) -> dict:
    """Ghép các case đã duyệt vào danh sách 'muc' của noi_dung cho khuôn trang-bu."""
    cfg = copy.deepcopy(site_cfg) if isinstance(site_cfg, dict) else {}
    goc_nd = cfg.get("noi_dung") if isinstance(cfg.get("noi_dung"), dict) else cfg

    tieu_de = _chuoi_sach(goc_nd.get("tieu_de")) or "Trang BU"
    mo_ta = _chuoi_sach(goc_nd.get("mo_ta"))

    muc: list[dict[str, str]] = []
    da_co_ten: set[str] = set()
    raw_muc = goc_nd.get("muc")
    if isinstance(raw_muc, (list, tuple)):
        for m in raw_muc:
            if not isinstance(m, dict):
                continue
            ten_muc = _chuoi_sach(m.get("ten"))
            mo_ta_muc = _chuoi_sach(m.get("mo_ta"))
            if not ten_muc and not mo_ta_muc:
                continue
            muc.append({"ten": ten_muc, "mo_ta": mo_ta_muc})
            if ten_muc:
                da_co_ten.add(ten_muc)

    cfg_case = cfg.get("case") if isinstance(cfg.get("case"), dict) else {}
    bat_case = cfg_case.get("bat", True) is not False
    mau_ten = _chuoi_sach(cfg_case.get("mau_ten"))

    nguon_case: list[dict] = []
    if isinstance(ds_case, (list, tuple)):
        nguon_case.extend(x for x in ds_case if isinstance(x, dict))

    if bat_case:
        for c in case_cong_khai(nguon_case):
            muc_case = _muc_tu_case(c, mau_ten=mau_ten)
            if muc_case["ten"] not in da_co_ten:
                muc.append(muc_case)
                da_co_ten.add(muc_case["ten"])

    return {
        "tieu_de": tieu_de,
        "mo_ta": mo_ta,
        "muc": muc,
    }
