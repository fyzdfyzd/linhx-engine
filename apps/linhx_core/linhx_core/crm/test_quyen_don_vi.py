"""Unit test cho linhx_core.crm.quyen_don_vi."""
from pathlib import Path
import sys
import types

import pytest

_CORE_DIR = str(Path(__file__).resolve().parents[2])
if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

from linhx_core.crm import quyen_don_vi as q


class _GiaPermissionError(Exception):
    pass


class _GiaDoc:
    def __init__(self, doctype: str, name: str | None = None, don_vi: str | None = None, nguoi: str | None = None, truoc=None, is_new: bool = False):
        self.doctype = doctype
        self.name = name
        self.don_vi = don_vi
        self.nguoi = nguoi
        self._truoc = truoc
        self._is_new = is_new
        self.flags = types.SimpleNamespace(ignore_permissions=False)

    def get_doc_before_save(self):
        return self._truoc

    def is_new(self):
        return self._is_new


def _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",), db_records=None, bat_crm=1):
    db_records = db_records or {}

    class _GiaDB:
        def sql(self, query, params=()):
            if "tabSingles" in query:
                return [(str(bat_crm),)]
            if "tabUser Permission" in query:
                return [(dv,) for dv in user_perms]
            return []

        def exists(self, doctype, name):
            return (doctype, name) in db_records

        def get_value(self, doctype, name, fieldname):
            rec = db_records.get((doctype, name))
            if not rec:
                return None
            return rec.get(fieldname)

    frappe_gia = types.SimpleNamespace(
        session=types.SimpleNamespace(user=user),
        local=types.SimpleNamespace(request=None, _lx_cau_hinh_cache=None),
        db=_GiaDB(),
        PermissionError=_GiaPermissionError,
        get_roles=lambda u=None: list(roles),
        logger=lambda *a, **kw: types.SimpleNamespace(error=lambda *x, **y: None),
    )

    def _throw(msg, exc=_GiaPermissionError):
        raise exc(msg)

    frappe_gia.throw = _throw
    monkeypatch.setitem(sys.modules, "frappe", frappe_gia)
    return frappe_gia


def test_sua_ban_ghi_don_vi_khac_gui_don_vi_minh_van_chan(monkeypatch):
    db_records = {
        ("LX Nguoi", "NGUOI-B"): {"don_vi": "DV-B"},
    }
    _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",), db_records=db_records)
    doc_gia_mao = _GiaDoc("LX Nguoi", name="NGUOI-B", don_vi="DV-A")
    assert q.frappe_has_permission(doc_gia_mao, ptype="write") is False
    with pytest.raises(_GiaPermissionError):
        q.kiem_tra_quyen_doc(doc_gia_mao)


def test_tao_co_hoi_tro_nguoi_don_vi_khac_bi_chan(monkeypatch):
    db_records = {
        ("LX Nguoi", "NGUOI-A"): {"don_vi": "DV-A"},
        ("LX Nguoi", "NGUOI-B"): {"don_vi": "DV-B"},
    }
    _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",), db_records=db_records)
    ch_cheo = _GiaDoc("LX Co Hoi", name="CH-MOI", don_vi="DV-A", nguoi="NGUOI-B", is_new=True)
    assert q.frappe_has_permission(ch_cheo, ptype="create") is False
    with pytest.raises(_GiaPermissionError):
        q.kiem_tra_quyen_doc(ch_cheo)

    ch_hop_le = _GiaDoc("LX Co Hoi", name="CH-MOI-2", don_vi=None, nguoi="NGUOI-A", is_new=True)
    assert q.frappe_has_permission(ch_hop_le, ptype="create") is True
    q.kiem_tra_quyen_doc(ch_hop_le)
    assert ch_hop_le.don_vi == "DV-A"
