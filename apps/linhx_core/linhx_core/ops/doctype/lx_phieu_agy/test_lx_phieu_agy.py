import sys
import types
import pytest


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



def test_controller_validate_va_chuyen_trang_thai(monkeypatch):
    LXPhieuAgy = _nap_controller()
    import frappe

    doc = LXPhieuAgy()
    doc.loai_phieu = "feature"
    doc.de = "Thêm kiểm tra trạng thái phiếu"
    doc.before_insert()
    doc.validate()
    assert doc.trang_thai == "nhap"

    # Chuyển từ nhap -> duyet khi thiếu vai điều hành thì lỗi (kể cả khi gửi kèm _vai_tro giả mạo)
    truoc = LXPhieuAgy()
    truoc.trang_thai = "nhap"
    doc.get_doc_before_save = lambda: truoc
    doc.trang_thai = "duyet"
    doc._vai_tro = ["System Manager"]
    monkeypatch.setattr(frappe, "get_roles", lambda: ["Guest"], raising=False)
    with pytest.raises(PermissionError):
        doc.validate()

    # Khi get_roles lỗi thì ghi log_error và từ chối
    da_ghi_log = []
    monkeypatch.setattr(
        frappe,
        "get_roles",
        lambda: (_ for _ in ()).throw(RuntimeError("Chưa khởi tạo site")),
        raising=False,
    )
    monkeypatch.setattr(
        frappe,
        "log_error",
        lambda *args, **kwargs: da_ghi_log.append((args, kwargs)),
        raising=False,
    )
    with pytest.raises(PermissionError):
        doc.validate()
    assert len(da_ghi_log) == 1

    # Có vai điều hành từ frappe.get_roles() thì duyệt được
    monkeypatch.setattr(frappe, "get_roles", lambda: ["LX Operator"], raising=False)
    doc.validate()
    assert doc.trang_thai == "duyet"


def test_nhap_sang_tra_bat_buoc_ly_do():
    _nap_controller()
    from linhx_core.ops.doctype.lx_phieu_agy.lx_phieu_agy import _tra_ham_phieu_agy

    chuyen_trang_thai = _tra_ham_phieu_agy("ops.phieu_agy.chuyen_trang_thai")
    p = {"loai_phieu": "sua_loi", "de": "Sửa lỗi hiển thị", "trang_thai": "nhap"}
    with pytest.raises(PermissionError):
        chuyen_trang_thai(p, "tra", vai_tro=["Guest"], ly_do_tra="Chưa rõ")
    with pytest.raises(ValueError):
        chuyen_trang_thai(p, "tra", vai_tro=["System Manager"], ly_do_tra="   ")
    kq = chuyen_trang_thai(p, "tra", vai_tro=["System Manager"], ly_do_tra="Trùng phiếu cũ")
    assert kq["trang_thai"] == "tra" and kq["ly_do_tra"] == "Trùng phiếu cũ"
