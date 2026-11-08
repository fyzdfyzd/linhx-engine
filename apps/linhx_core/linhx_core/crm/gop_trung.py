"""Gộp trùng hồ sơ Người (LX Nguoi) theo số điện thoại, email, Zalo.

Chuyển từ: nguon/03-opc-os/modules/04_quan_ly_user/module.py
(UserManagementModule.upsert_from_order: trích xuất khoá liên hệ chuẩn hoá và gộp cập nhật hồ sơ khách).
"""
from __future__ import annotations

import re

NGUON_PROTO = "nguon/03-opc-os/modules/04_quan_ly_user/module.py"


def chuan_hoa_dien_thoai(dien_thoai: object) -> str:
    """Chuẩn hoá số điện thoại Việt Nam về dạng 84... (chỉ giữ chữ số)."""
    if dien_thoai is None:
        return ""
    chuso = re.sub(r"\D+", "", str(dien_thoai).strip())
    if not chuso:
        return ""
    if chuso.startswith("0084") and len(chuso) > 4:
        chuso = "84" + chuso[4:]
    elif chuso.startswith("0") and len(chuso) >= 9:
        chuso = "84" + chuso[1:]
    elif len(chuso) == 9 and chuso[0] in "35789":
        chuso = "84" + chuso
    return chuso


def chuan_hoa_email(email: object) -> str:
    """Chuẩn hoá email: cắt khoảng trắng hai đầu và chuyển chữ thường."""
    if email is None:
        return ""
    return str(email).strip().lower()


def chuan_hoa_zalo(zalo: object) -> str:
    """Chuẩn hoá định danh Zalo: cắt khoảng trắng hai đầu."""
    if zalo is None:
        return ""
    return str(zalo).strip()


def khoa_gop(nguoi: dict) -> set[str]:
    """Trả tập hợp khoá chuẩn hoá ('dt:84...', 'email:...', 'zalo:...') của một bản ghi Người."""
    if not isinstance(nguoi, dict):
        return set()
    khoa: set[str] = set()
    dt = chuan_hoa_dien_thoai(nguoi.get("dien_thoai"))
    if dt:
        khoa.add(f"dt:{dt}")
    em = chuan_hoa_email(nguoi.get("email"))
    if em:
        khoa.add(f"email:{em}")
    zl = chuan_hoa_zalo(nguoi.get("zalo"))
    if zl:
        khoa.add(f"zalo:{zl}")
    return khoa


def _la_trong(gia_tri: object) -> bool:
    if gia_tri is None:
        return True
    if isinstance(gia_tri, str):
        return gia_tri.strip() == ""
    if isinstance(gia_tri, (list, dict, set, tuple)):
        return len(gia_tri) == 0
    return False


def gop(danh_sach: list[dict], moi: dict) -> list[dict]:
    """Thêm bản ghi `moi` vào `danh_sach`; nếu trùng khoá thì gộp vào bản ghi cũ
    (giữ trường cũ đã có giá trị, bù trường còn trống từ `moi`).
    """
    ket_qua = [dict(x) for x in (danh_sach or [])]
    if not isinstance(moi, dict):
        return ket_qua
    ban_moi = dict(moi)
    khoa_moi = khoa_gop(ban_moi)
    if khoa_moi:
        for cu in ket_qua:
            if khoa_gop(cu) & khoa_moi:
                for k, v in ban_moi.items():
                    if _la_trong(cu.get(k)) and not _la_trong(v):
                        cu[k] = v
                return ket_qua
    ket_qua.append(ban_moi)
    return ket_qua
