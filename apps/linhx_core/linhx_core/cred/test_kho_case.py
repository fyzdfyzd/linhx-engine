"""Kiểm thử controller LXCase kết nối gói Agent Force qua dang_ky_module."""
from __future__ import annotations

import sys
import types
from unittest.mock import patch

import pytest


def test_controller_lx_case_validate_va_has_permission():
    frappe_mod = types.ModuleType("frappe")
    model_mod = types.ModuleType("frappe.model")
    doc_mod = types.ModuleType("frappe.model.document")

    class _StubValidationError(ValueError):
        pass

    class _StubDocument:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    doc_mod.Document = _StubDocument
    model_mod.document = doc_mod
    frappe_mod.model = model_mod
    frappe_mod.ValidationError = _StubValidationError
    frappe_mod.session = types.SimpleNamespace(user="Administrator")
    frappe_mod.get_roles = lambda user=None: ["System Manager"] if user == "Administrator" else ["LX Nhan Vien"]

    def _throw(msg, exc=_StubValidationError):
        raise exc(msg)

    frappe_mod.throw = _throw

    with patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        try:
            sys.modules.pop("linhx_core.cred.doctype.lx_case.lx_case", None)
            from linhx_core.cred.doctype.lx_case.lx_case import LXCase

            doc_hop_le = LXCase(
                tieu_de=" Case Dược ",
                khach_hang=" Dược A ",
                cho_phep_hien_ten=1,
                chi_so=" +45% ",
                mo_ta=" Kết quả tốt ",
                da_duyet=1,
            )
            doc_hop_le.validate()
            assert doc_hop_le.tieu_de == "Case Dược"
            assert doc_hop_le.chi_so == "+45%"
            assert doc_hop_le.da_duyet == 1
            assert doc_hop_le.has_permission("read", user="Administrator") is True
            assert doc_hop_le.has_permission("read", user="Guest") is False

            doc_thieu_chi_so = LXCase(tieu_de="Case thiếu chỉ số", chi_so="  ", da_duyet=1)
            with pytest.raises(frappe_mod.ValidationError):
                doc_thieu_chi_so.validate()
        finally:
            sys.modules.pop("linhx_core.cred.doctype.lx_case.lx_case", None)
            pkg = sys.modules.get("linhx_core.cred.doctype.lx_case")
            if pkg is not None and hasattr(pkg, "lx_case"):
                delattr(pkg, "lx_case")
