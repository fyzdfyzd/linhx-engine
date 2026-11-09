"""Controller DocType LX Case: kiểm tra tính hợp lệ và bảo vệ case chưa duyệt."""
from __future__ import annotations

from frappe.model.document import Document

from linhx_core.cred import kho_case

VAI_QUAN_TRI_CASE = ("System Manager", "LX Operator")


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
            "chi_so": getattr(self, "chi_so", None),
            "mo_ta": getattr(self, "mo_ta", None),
            "da_duyet": getattr(self, "da_duyet", 0),
            "pilot": getattr(self, "pilot", None),
        }

    def validate(self) -> None:
        try:
            chuan = kho_case.kiem_case(self._to_dict())
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return

        self.tieu_de = chuan["tieu_de"]
        self.khach_hang = chuan["khach_hang"]
        self.chi_so = chuan["chi_so"]
        self.mo_ta = chuan["mo_ta"]
        self.da_duyet = 1 if chuan["da_duyet"] else 0
