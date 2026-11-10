"""Controller DocType LX Case: kiểm tra tính hợp lệ và bảo vệ case chưa duyệt."""
from __future__ import annotations

import importlib
import pathlib
import sys

from frappe.model.document import Document

from linhx_core import dang_ky_module

VAI_QUAN_TRI_CASE = ("System Manager", "LX Operator")
_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[5]


def _tra_ham_case(khoa: str):
    """Tra hàm cung_cap của gói Agent Force qua dang_ky_module (không import trực tiếp gói ở tầng lõi)."""
    ds_module = dang_ky_module.quet(_THU_MUC_APPS)
    ds_duong = dang_ky_module.tim_ham(ds_module, "cung_cap", khoa)
    if not ds_duong:
        raise RuntimeError(f"Không tìm thấy hàm cung_cap cho khoá {khoa!r}")
    duong_ham = ds_duong[0]
    ten_module, ten_ham = duong_ham.rsplit(".", 1)
    ten_app = ten_module.split(".", 1)[0]
    duong_app = str(_THU_MUC_APPS / ten_app)
    if duong_app not in sys.path and (_THU_MUC_APPS / ten_app).is_dir():
        sys.path.insert(0, duong_app)
    mod = importlib.import_module(ten_module)
    ham = getattr(mod, ten_ham, None)
    if not callable(ham):
        raise AttributeError(f"Hàm cung_cap không gọi được: {duong_ham!r}")
    return ham


def _nem_loi_hop_le(thong_bao: str) -> None:
    try:
        import frappe

        throw_fn = getattr(frappe, "throw", None)
        if callable(throw_fn):
            exc_cls = getattr(frappe, "ValidationError", ValueError)
            throw_fn(thong_bao, exc_cls)
    except ImportError:
        pass
    raise ValueError(thong_bao)


def _la_quan_tri_case(user: str | None = None) -> bool:
    try:
        import frappe
    except ImportError:
        return True

    session_obj = getattr(frappe, "session", None)
    nguoi_dung = user or (getattr(session_obj, "user", None) if session_obj is not None else None)
    if not nguoi_dung:
        return session_obj is None
    if nguoi_dung == "Administrator":
        return True
    if nguoi_dung == "Guest":
        return False

    get_roles = getattr(frappe, "get_roles", None)
    if callable(get_roles):
        try:
            vai_tro = set(get_roles(nguoi_dung) or [])
            return bool(vai_tro.intersection(VAI_QUAN_TRI_CASE))
        except Exception:
            return False
    return False


class LXCase(Document):
    doctype = "LX Case"

    def has_permission(
        self, permtype: str = "read", *, debug: bool = False, user: str | None = None
    ) -> bool:
        if getattr(getattr(self, "flags", None), "ignore_permissions", False):
            return True
        if not _la_quan_tri_case(user):
            return False
        sup = getattr(super(), "has_permission", None)
        if callable(sup):
            return bool(sup(permtype, debug=debug, user=user))
        return True

    def _to_dict(self) -> dict:
        return {
            "name": getattr(self, "name", None),
            "tieu_de": getattr(self, "tieu_de", None),
            "khach_hang": getattr(self, "khach_hang", None),
            "cho_phep_hien_ten": getattr(self, "cho_phep_hien_ten", 0),
            "chi_so": getattr(self, "chi_so", None),
            "mo_ta": getattr(self, "mo_ta", None),
            "da_duyet": getattr(self, "da_duyet", 0),
            "pilot": getattr(self, "pilot", None),
        }

    def validate(self) -> None:
        kiem_case = _tra_ham_case("cred.kho_case.kiem_case")
        try:
            chuan = kiem_case(self._to_dict())
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return

        self.tieu_de = chuan["tieu_de"]
        self.khach_hang = chuan["khach_hang"]
        self.cho_phep_hien_ten = 1 if chuan["cho_phep_hien_ten"] else 0
        self.chi_so = chuan["chi_so"]
        self.mo_ta = chuan["mo_ta"]
        self.da_duyet = 1 if chuan["da_duyet"] else 0
