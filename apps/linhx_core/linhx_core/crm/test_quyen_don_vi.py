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

    frappe_gia = types.ModuleType("frappe")
    frappe_gia.__path__ = []
    frappe_gia.session = types.SimpleNamespace(user=user)
    frappe_gia.local = types.SimpleNamespace(request=None, _lx_cau_hinh_cache=None)
    frappe_gia.db = _GiaDB()
    frappe_gia.PermissionError = _GiaPermissionError
    frappe_gia.get_roles = lambda u=None: list(roles)
    frappe_gia.logger = lambda *a, **kw: types.SimpleNamespace(error=lambda *x, **y: None)

    def _throw(msg, exc=_GiaPermissionError):
        raise exc(msg)

    frappe_gia.throw = _throw

    mod_utils = types.ModuleType("frappe.utils")
    mod_utils.now_datetime = lambda: "2026-11-09 00:00:00"
    frappe_gia.utils = mod_utils

    mod_doc = types.ModuleType("frappe.model.document")
    mod_doc.Document = object
    mod_model = types.ModuleType("frappe.model")
    mod_model.document = mod_doc
    frappe_gia.model = mod_model

    monkeypatch.setitem(sys.modules, "frappe", frappe_gia)
    monkeypatch.setitem(sys.modules, "frappe.utils", mod_utils)
    monkeypatch.setitem(sys.modules, "frappe.model", mod_model)
    monkeypatch.setitem(sys.modules, "frappe.model.document", mod_doc)
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
    assert ch_hop_le.don_vi is None


def test_permission_query_conditions(monkeypatch):
    _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",))
    dk = q.frappe_permission_query_conditions(user="nv_a@test.local", doctype="LX Nguoi")
    assert dk == "`tabLX Nguoi`.`don_vi` in ('DV-A')"

    _cai_frappe_gia(monkeypatch, user="nv_khong_quyen@test.local", roles=("LX Nhan Vien",), user_perms=())
    assert q.frappe_permission_query_conditions(user="nv_khong_quyen@test.local", doctype="LX Co Hoi") == "1=0"

    _cai_frappe_gia(monkeypatch, user="Administrator", roles=("System Manager",), user_perms=())
    assert q.frappe_permission_query_conditions(user="Administrator", doctype="LX Nguoi") == ""

    _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",), bat_crm=0)
    assert q.frappe_permission_query_conditions(user="nv_a@test.local", doctype="LX Nguoi") == "1=0"


def test_sua_co_hoi_don_vi_khac_hoac_doi_nguoi_sang_don_vi_khac(monkeypatch):
    db_records = {
        ("LX Nguoi", "NGUOI-A"): {"don_vi": "DV-A"},
        ("LX Nguoi", "NGUOI-B"): {"don_vi": "DV-B"},
        ("LX Co Hoi", "CH-B"): {"don_vi": "DV-B", "nguoi": "NGUOI-B"},
        ("LX Co Hoi", "CH-A"): {"don_vi": "DV-A", "nguoi": "NGUOI-A"},
    }
    _cai_frappe_gia(monkeypatch, user="nv_a@test.local", roles=("LX Nhan Vien",), user_perms=("DV-A",), db_records=db_records)

    # Cơ hội của Y bị user X sửa (kể cả gửi don_vi = DV-A hoặc đổi nguoi sang NGUOI-B / NGUOI-A)
    ch_b_sua = _GiaDoc("LX Co Hoi", name="CH-B", don_vi="DV-A", nguoi="NGUOI-B", is_new=False)
    assert q.frappe_has_permission(ch_b_sua, ptype="write") is False
    with pytest.raises(_GiaPermissionError):
        q.kiem_tra_quyen_doc(ch_b_sua)

    # Cơ hội của X bị sửa đổi nguoi sang Người của Y
    ch_a_doi_nguoi = _GiaDoc("LX Co Hoi", name="CH-A", don_vi="DV-A", nguoi="NGUOI-B", is_new=False)
    assert q.frappe_has_permission(ch_a_doi_nguoi, ptype="write") is False
    with pytest.raises(_GiaPermissionError):
        q.kiem_tra_quyen_doc(ch_a_doi_nguoi)


def test_gop_trung_khong_chiem_ban_ghi_trong_don_vi_hoac_khac_don_vi(monkeypatch):
    db_records = {
        ("LX Nguoi", "NGUOI-TRONG"): {"don_vi": "", "ho_ten": "Khách Cũ Bí Mật", "dien_thoai": "0912345678", "email": "bimat@vd.vn"},
        ("LX Nguoi", "NGUOI-B"): {"don_vi": "DV-B", "ho_ten": "Khách Đơn Vị B", "dien_thoai": "0987654321", "email": "khachb@vd.vn"},
        ("LX Nguoi", "NGUOI-A"): {"don_vi": "DV-A", "ho_ten": "Khách Đơn Vị A", "dien_thoai": "0909000111", "email": "khacha@vd.vn"},
    }
    frappe_gia = _cai_frappe_gia(
        monkeypatch,
        user="nv_a@test.local",
        roles=("LX Nhan Vien",),
        user_perms=("DV-A",),
        db_records=db_records,
    )
    da_set_value = []
    frappe_gia.db.set_value = lambda dt, dn, f, val, **kw: da_set_value.append((dt, dn, f, val))
    frappe_gia.get_all = lambda dt, **kw: [
        {"name": k[1], **v} for k, v in db_records.items() if k[0] == dt
    ]

    from linhx_core.crm.doctype.lx_nguoi.lx_nguoi import LXNguoi

    # 1. Trùng SĐT với bản ghi có don_vi trống -> không được gộp, không lộ email/ho_ten
    ng_moi = LXNguoi()
    ng_moi.doctype = "LX Nguoi"
    ng_moi.name = "NGUOI-MOI-1"
    ng_moi.ho_ten = "Người Mới"
    ng_moi.dien_thoai = "0912345678"
    ng_moi.email = None
    ng_moi.zalo = None
    ng_moi.don_vi = "DV-A"
    ng_moi.to_chuc = None
    ng_moi.ghi_cong = None
    ng_moi.flags = types.SimpleNamespace(ignore_permissions=False)
    ng_moi._gop_trung_khi_them()
    assert getattr(ng_moi, "_gop_vao_name", None) is None
    assert ng_moi.email is None
    assert ng_moi.ho_ten == "Người Mới"

    # 2. Nếu cố tình gán _gop_vao_name trỏ tới bản ghi đơn vị trống hoặc DV-B -> db_insert chặn bằng PermissionError
    ng_moi._gop_vao_name = "NGUOI-TRONG"
    with pytest.raises(_GiaPermissionError):
        ng_moi.db_insert()
    ng_moi._gop_vao_name = "NGUOI-B"
    with pytest.raises(_GiaPermissionError):
        ng_moi.db_insert()
    assert da_set_value == []

    # 3. Khi don_vi mới để trống -> bỏ qua gộp
    ng_trong = LXNguoi()
    ng_trong.doctype = "LX Nguoi"
    ng_trong.ho_ten = "Không Đơn Vị"
    ng_trong.dien_thoai = "0909000111"
    ng_trong.email = None
    ng_trong.zalo = None
    ng_trong.don_vi = ""
    ng_trong.to_chuc = None
    ng_trong.ghi_cong = None
    ng_trong.flags = types.SimpleNamespace(ignore_permissions=False)
    ng_trong._gop_trung_khi_them()
    assert getattr(ng_trong, "_gop_vao_name", None) is None
    assert ng_trong.email is None

    # 4. Cùng đơn vị DV-A và user có quyền DV-A -> được gộp hợp lệ
    ng_cung = LXNguoi()
    ng_cung.doctype = "LX Nguoi"
    ng_cung.ho_ten = "Khách A Bổ Sung"
    ng_cung.dien_thoai = "0909000111"
    ng_cung.email = None
    ng_cung.zalo = "zl_a"
    ng_cung.don_vi = "DV-A"
    ng_cung.to_chuc = None
    ng_cung.ghi_cong = None
    ng_cung.flags = types.SimpleNamespace(ignore_permissions=False)
    ng_cung._gop_trung_khi_them()
    assert getattr(ng_cung, "_gop_vao_name", None) == "NGUOI-A"
    assert ng_cung.email == "khacha@vd.vn"
    ng_cung.db_insert()
    assert any(x[1] == "NGUOI-A" and x[2] == "zalo" and x[3] == "zl_a" for x in da_set_value)
    assert not any(x[2] == "don_vi" for x in da_set_value)


def test_quyen_lx_don_vi_a4b(monkeypatch):
    _cai_frappe_gia(
        monkeypatch,
        user="nv_a@test.local",
        roles=("LX Nhan Vien",),
        user_perms=("DV-A",),
    )
    dv_a = _GiaDoc("LX Don Vi", name="DV-A")
    dv_b = _GiaDoc("LX Don Vi", name="DV-B")
    assert q.frappe_has_permission_don_vi(dv_a, ptype="read") is True
    assert q.frappe_has_permission_don_vi(dv_b, ptype="read") is False
    assert q.frappe_has_permission_don_vi(dv_a, ptype="write") is False
    assert q.frappe_permission_query_conditions_don_vi(user="nv_a@test.local") == "`tabLX Don Vi`.`name` in ('DV-A')"
    with pytest.raises(_GiaPermissionError):
        q.kiem_tra_quyen_doc(dv_a)

    _cai_frappe_gia(
        monkeypatch,
        user="nv_rong@test.local",
        roles=("LX Nhan Vien",),
        user_perms=(),
    )
    assert q.frappe_has_permission_don_vi(dv_a, ptype="read") is False
    assert q.frappe_permission_query_conditions_don_vi(user="nv_rong@test.local") == "1=0"

    _cai_frappe_gia(
        monkeypatch,
        user="nv_a@test.local",
        roles=("LX Nhan Vien",),
        user_perms=("DV-A",),
        bat_crm=0,
    )
    assert q.frappe_has_permission_don_vi(dv_a, ptype="read") is False
    assert q.frappe_permission_query_conditions_don_vi(user="nv_a@test.local") == "1=0"

