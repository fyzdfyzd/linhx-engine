import sys
import types
import pytest

from linhx_core.ops import phieu_agy


def _nap_controller():
    if "frappe" not in sys.modules or sys.modules["frappe"] is None:
        frappe_mod = types.ModuleType("frappe")
        model_mod = types.ModuleType("frappe.model")
        doc_mod = types.ModuleType("frappe.model.document")

        class _StubDocument:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        doc_mod.Document = _StubDocument
        model_mod.document = doc_mod
        frappe_mod.model = model_mod
        sys.modules["frappe"] = frappe_mod
        sys.modules["frappe.model"] = model_mod
        sys.modules["frappe.model.document"] = doc_mod

    from linhx_core.ops.doctype.lx_phieu_agy.lx_phieu_agy import LXPhieuAgy

    return LXPhieuAgy


def test_controller_validate_va_chuyen_trang_thai():
    LXPhieuAgy = _nap_controller()
    doc = LXPhieuAgy()
    doc.loai_phieu = "feature"
    doc.de = "Thêm kiểm tra trạng thái phiếu"
    doc.before_insert()
    doc.validate()
    assert doc.trang_thai == "nhap"

    # Chuyển từ nhap -> duyet khi thiếu vai điều hành thì lỗi
    truoc = LXPhieuAgy()
    truoc.trang_thai = "nhap"
    doc.get_doc_before_save = lambda: truoc
    doc.trang_thai = "duyet"
    doc._vai_tro = ["Guest"]
    with pytest.raises(PermissionError):
        doc.validate()

    # Có vai điều hành thì duyệt được
    doc._vai_tro = ["LX Operator"]
    doc.validate()
    assert doc.trang_thai == "duyet"


def test_nhap_sang_tra_bat_buoc_ly_do():
    p = {"loai_phieu": "sua_loi", "de": "Sửa lỗi hiển thị", "trang_thai": "nhap"}
    with pytest.raises(PermissionError):
        phieu_agy.chuyen_trang_thai(p, "tra", vai_tro=["Guest"], ly_do_tra="Chưa rõ")
    with pytest.raises(ValueError):
        phieu_agy.chuyen_trang_thai(p, "tra", vai_tro=["System Manager"], ly_do_tra="   ")
    kq = phieu_agy.chuyen_trang_thai(p, "tra", vai_tro=["System Manager"], ly_do_tra="Trùng phiếu cũ")
    assert kq["trang_thai"] == "tra" and kq["ly_do_tra"] == "Trùng phiếu cũ"
