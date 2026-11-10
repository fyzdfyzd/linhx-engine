"""Kiểm thử DocType `LX Don CTS` và `LX Giao Dich CTS` trong `linhx_core`:
bảo vệ quyền PII (permlevel 1) và ràng buộc duy nhất `tx_id`, `order_id`, `noi_dung_ck`.
"""
from __future__ import annotations

import json
import pathlib
import sys
import types
from unittest import mock

GOC_APP = pathlib.Path(__file__).resolve().parents[2]
if str(GOC_APP) not in sys.path:
    sys.path.insert(0, str(GOC_APP))


class _PermissionError(Exception):
    pass


class _ValidationError(Exception):
    pass


def test_doctype_pii_permissions_va_unique_tx_id():
    thu_muc_dt = pathlib.Path(__file__).resolve().parent / "doctype"
    don_json = json.loads((thu_muc_dt / "lx_don_cts" / "lx_don_cts.json").read_text(encoding="utf-8"))
    gd_json = json.loads((thu_muc_dt / "lx_giao_dich_cts" / "lx_giao_dich_cts.json").read_text(encoding="utf-8"))

    truong_don = {f["fieldname"]: f for f in don_json["fields"]}
    assert truong_don["order_id"].get("unique") == 1
    assert truong_don["noi_dung_ck"].get("unique") == 1
    assert truong_don["email"].get("permlevel") == 1, "email (PII) phải đặt ở permlevel 1"
    assert truong_don["ho_so"].get("permlevel") == 1, "ho_so (PII) phải đặt ở permlevel 1"

    quyen_don = don_json.get("permissions", [])
    roles_perm1 = {p["role"] for p in quyen_don if p.get("permlevel") == 1 and p.get("read")}
    assert roles_perm1 == {"System Manager"}, "chỉ System Manager được đọc PII ở permlevel 1"

    truong_gd = {f["fieldname"]: f for f in gd_json["fields"]}
    assert truong_gd["tx_id"].get("unique") == 1, "tx_id phải có ràng buộc unique"


def test_controller_quyen_don_cts():
    frappe_mod = types.ModuleType("frappe")
    frappe_mod.PermissionError = _PermissionError
    frappe_mod.ValidationError = _ValidationError
    frappe_mod.session = types.SimpleNamespace(user="Guest")
    frappe_mod.db = None
    frappe_mod.get_roles = lambda u: ["LX Nhan Vien"] if u == "nv@test.local" else ["System Manager"]

    def _throw(msg, exc=_ValidationError):
        raise exc(msg)

    frappe_mod.throw = _throw

    model_mod = types.ModuleType("frappe.model")
    doc_mod = types.ModuleType("frappe.model.document")

    class Document:
        def is_new(self):
            return True

    doc_mod.Document = Document
    model_mod.document = doc_mod

    ten_mod = "linhx_core.cts_adapter.doctype.lx_don_cts.lx_don_cts"
    with mock.patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        sys.modules.pop(ten_mod, None)
        from linhx_core.cts_adapter.doctype import lx_don_cts as pkg_don
        if hasattr(pkg_don, "lx_don_cts"):
            delattr(pkg_don, "lx_don_cts")
        from linhx_core.cts_adapter.doctype.lx_don_cts import lx_don_cts

        try:
            assert lx_don_cts.co_quyen_don_cts(None, "read", "Guest") is False
            assert lx_don_cts.co_quyen_don_cts(None, "read", "nv@test.local") is False
            assert lx_don_cts.dieu_kien_truy_van_don_cts("Guest") == "1=0"
            assert lx_don_cts.dieu_kien_truy_van_don_cts("nv@test.local") == "1=0"
            assert lx_don_cts.co_quyen_don_cts(None, "read", "admin@test.local") is True
        finally:
            sys.modules.pop(ten_mod, None)
            if hasattr(pkg_don, "lx_don_cts"):
                delattr(pkg_don, "lx_don_cts")
