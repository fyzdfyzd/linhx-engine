"""Kiểm thử controller LXPilot kết nối gói Agent Force qua dang_ky_module."""
from __future__ import annotations

import copy
import json
import sys
import types
from unittest.mock import patch

import pytest


def _tao_frappe_gia_lap():
    frappe_mod = types.ModuleType("frappe")
    model_mod = types.ModuleType("frappe.model")
    doc_mod = types.ModuleType("frappe.model.document")

    class _StubValidationError(ValueError):
        pass

    class _StubPermissionError(PermissionError, ValueError):
        pass

    class _StubDocument:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    doc_mod.Document = _StubDocument
    model_mod.document = doc_mod
    frappe_mod.model = model_mod
    frappe_mod.ValidationError = _StubValidationError
    frappe_mod.PermissionError = _StubPermissionError

    def _throw(msg, exc=_StubValidationError):
        if isinstance(exc, type) and issubclass(exc, BaseException):
            raise exc(msg)
        if isinstance(exc, BaseException):
            raise exc
        raise _StubValidationError(msg)

    frappe_mod.throw = _throw
    return frappe_mod, model_mod, doc_mod


def test_controller_lx_pilot_ke_thua_co_hoi_va_kiem_luat():
    frappe_mod, model_mod, doc_mod = _tao_frappe_gia_lap()

    class _StubDB:
        loi_db = False

        @classmethod
        def get_value(cls, dt, name, fields=None, as_dict=False):
            if cls.loi_db:
                raise RuntimeError("Mất kết nối DB")
            if dt == "LX Co Hoi":
                if name == "CH-10":
                    d = {"phu_trach": "sale10@vd.vn", "don_vi": "IFAGENT", "nguoi": "NG-10"}
                    return d if as_dict else d.get(fields)
                if name == "CH-KHONG-DV":
                    d = {"phu_trach": "sale10@vd.vn", "don_vi": "", "nguoi": ""}
                    return d if as_dict else d.get(fields)
            return None

    frappe_mod.db = _StubDB()

    with patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        try:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            from linhx_core.agent.doctype.lx_pilot.lx_pilot import LXPilot

            doc = LXPilot(co_hoi="CH-10", bat_dau_luc="2026-11-01 08:30:00", han_hoan_thanh="2026-12-31 00:00:00")
            doc.before_insert()
            doc.validate()

            assert doc.phu_trach == "sale10@vd.vn"
            assert doc.don_vi == "IFAGENT"
            assert doc.han_hoan_thanh == "2026-11-15 08:30:00"
            assert doc.trang_thai == "dang_chay"
            assert len(doc.cac_buoc) == 7

            doc_khong_co_ch = LXPilot(co_hoi="CH-KHONG-TON-TAI", bat_dau_luc="2026-11-01 08:30:00")
            with pytest.raises(frappe_mod.ValidationError):
                doc_khong_co_ch.before_insert()

            doc_ch_khong_dv = LXPilot(co_hoi="CH-KHONG-DV", bat_dau_luc="2026-11-01 08:30:00")
            with pytest.raises(frappe_mod.ValidationError):
                doc_ch_khong_dv.before_insert()

            _StubDB.loi_db = True
            try:
                doc_loi_db = LXPilot(co_hoi="CH-10", bat_dau_luc="2026-11-01 08:30:00")
                with pytest.raises(frappe_mod.ValidationError):
                    doc_loi_db.before_insert()
            finally:
                _StubDB.loi_db = False

            doc_sai_dv = LXPilot(co_hoi="CH-10", don_vi="DON-VI-KHAC", bat_dau_luc="2026-11-01 08:30:00")
            with pytest.raises(frappe_mod.PermissionError):
                doc_sai_dv.before_insert()

            with pytest.raises(frappe_mod.ValidationError):
                doc.hoan_thanh_buoc(2, "2026-11-02 09:00:00")

            doc_sai = LXPilot(
                co_hoi="CH-10",
                bat_dau_luc="2026-11-01 08:30:00",
                trang_thai="xong",
                cac_buoc=json.dumps(doc.cac_buoc),
            )
            with pytest.raises(frappe_mod.ValidationError):
                doc_sai.validate()

            for s in range(1, 8):
                doc.hoan_thanh_buoc(s, f"2026-11-0{s} 10:00:00")
            doc.validate()
            assert doc.trang_thai == "xong"

            truoc = copy.deepcopy(doc)
            doc.get_doc_before_save = lambda: truoc
            doc.trang_thai = "dang_chay"
            with pytest.raises(frappe_mod.ValidationError):
                doc.validate()
        finally:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            pkg = sys.modules.get("linhx_core.agent.doctype.lx_pilot")
            if pkg is not None and hasattr(pkg, "lx_pilot"):
                delattr(pkg, "lx_pilot")


def test_phan_quyen_don_vi_chan_doc_ghi_sua_xoa_cheo_don_vi():
    """Người đơn vị A đọc/tạo/sửa được pilot đơn vị A nhưng bị chặn đọc/sửa/tạo/xoá pilot đơn vị B."""
    frappe_mod, model_mod, doc_mod = _tao_frappe_gia_lap()
    frappe_mod.session = types.SimpleNamespace(user="nv_a@vd.vn")

    def _get_roles(user=None):
        u = user or frappe_mod.session.user
        if u == "Administrator":
            return ["Administrator", "System Manager"]
        return ["LX Nhan Vien"]

    frappe_mod.get_roles = _get_roles

    with patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        try:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            from linhx_core.agent.doctype.lx_pilot.lx_pilot import (
                LXPilot,
                _tra_ham_pilot,
                frappe_permission_query_conditions,
            )

            tao_cac_buoc_mac_dinh = _tra_ham_pilot("agent.pilot.tao_cac_buoc_mac_dinh")
            kho_co_hoi = {
                "CH-A": {"phu_trach": "nv_a@vd.vn", "don_vi": "DV-A", "nguoi": "NG-A"},
                "CH-B": {"phu_trach": "nv_b@vd.vn", "don_vi": "DV-B", "nguoi": "NG-B"},
            }
            kho_pilot = {
                "PILOT-A": {
                    "co_hoi": "CH-A",
                    "don_vi": "DV-A",
                    "bat_dau_luc": "2026-11-01 08:00:00",
                    "han_hoan_thanh": "2026-11-15 08:00:00",
                    "trang_thai": "dang_chay",
                    "cac_buoc": tao_cac_buoc_mac_dinh(),
                },
                "PILOT-B": {
                    "co_hoi": "CH-B",
                    "don_vi": "DV-B",
                    "bat_dau_luc": "2026-11-01 08:00:00",
                    "han_hoan_thanh": "2026-11-15 08:00:00",
                    "trang_thai": "dang_chay",
                    "cac_buoc": tao_cac_buoc_mac_dinh(),
                },
            }
            quyen_user = {
                "nv_a@vd.vn": [("DV-A",)],
                "nv_b@vd.vn": [("DV-B",)],
                "nv_khong_dv@vd.vn": [],
            }

            class _StubDB:
                @staticmethod
                def sql(query, params=None):
                    if "tabUser Permission" in query and params:
                        user = params[0]
                        return quyen_user.get(user, [])
                    return []

                @staticmethod
                def exists(dt, name):
                    if dt == "LX Pilot":
                        return name in kho_pilot
                    if dt == "LX Co Hoi":
                        return name in kho_co_hoi
                    return False

                @staticmethod
                def get_value(dt, name, fields=None, as_dict=False):
                    bang = kho_co_hoi if dt == "LX Co Hoi" else kho_pilot if dt == "LX Pilot" else {}
                    ban_ghi = bang.get(name)
                    if not ban_ghi:
                        return None
                    if as_dict:
                        if isinstance(fields, (list, tuple)):
                            return {k: copy.deepcopy(ban_ghi.get(k)) for k in fields}
                        return copy.deepcopy(ban_ghi)
                    if isinstance(fields, str):
                        return copy.deepcopy(ban_ghi.get(fields))
                    return copy.deepcopy(ban_ghi)

            frappe_mod.db = _StubDB()

            dk_a = frappe_permission_query_conditions(user="nv_a@vd.vn", doctype="LX Pilot")
            assert "`tabLX Pilot`.`don_vi` in ('DV-A')" == dk_a
            assert frappe_permission_query_conditions(user="nv_khong_dv@vd.vn", doctype="LX Pilot") == "1=0"
            assert frappe_permission_query_conditions(user="Administrator", doctype="LX Pilot") == ""

            frappe_mod.session.user = "nv_a@vd.vn"
            doc_a_moi = LXPilot(co_hoi="CH-A", bat_dau_luc="2026-11-01 09:00:00", __islocal=1)
            doc_a_moi.before_insert()
            doc_a_moi.validate()
            assert doc_a_moi.don_vi == "DV-A"
            assert doc_a_moi.has_permission("read") is True
            assert doc_a_moi.has_permission("write") is True

            doc_a_db = LXPilot(
                name="PILOT-A",
                co_hoi="CH-A",
                don_vi="DV-A",
                bat_dau_luc="2026-11-01 08:00:00",
                cac_buoc=copy.deepcopy(kho_pilot["PILOT-A"]["cac_buoc"]),
            )
            doc_a_db.onload()
            doc_a_db.hoan_thanh_buoc(1, "2026-11-02 09:00:00")
            doc_a_db.validate()
            doc_a_db.before_save()

            doc_b_db = LXPilot(
                name="PILOT-B",
                co_hoi="CH-B",
                don_vi="DV-B",
                bat_dau_luc="2026-11-01 08:00:00",
                cac_buoc=copy.deepcopy(kho_pilot["PILOT-B"]["cac_buoc"]),
            )
            assert doc_b_db.has_permission("read") is False
            with pytest.raises(frappe_mod.PermissionError):
                doc_b_db.onload()

            doc_tao_cheo = LXPilot(co_hoi="CH-B", bat_dau_luc="2026-11-01 09:00:00", __islocal=1)
            with pytest.raises(frappe_mod.PermissionError):
                doc_tao_cheo.before_insert()

            doc_gia_mao_dv = LXPilot(
                co_hoi="CH-B", don_vi="DV-A", bat_dau_luc="2026-11-01 09:00:00", __islocal=1
            )
            with pytest.raises(frappe_mod.PermissionError):
                doc_gia_mao_dv.before_insert()

            doc_sua_trom = LXPilot(
                name="PILOT-B",
                co_hoi="CH-A",
                don_vi="DV-A",
                bat_dau_luc="2026-11-01 08:00:00",
                trang_thai="huy",
                cac_buoc=copy.deepcopy(kho_pilot["PILOT-B"]["cac_buoc"]),
            )
            assert doc_sua_trom.has_permission("write") is False
            with pytest.raises(frappe_mod.PermissionError):
                doc_sua_trom.validate()
            with pytest.raises(frappe_mod.PermissionError):
                doc_sua_trom.before_save()
            with pytest.raises(frappe_mod.PermissionError):
                doc_sua_trom.on_trash()
        finally:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            pkg = sys.modules.get("linhx_core.agent.doctype.lx_pilot")
            if pkg is not None and hasattr(pkg, "lx_pilot"):
                delattr(pkg, "lx_pilot")
