from collections.abc import Callable
import importlib
import pathlib
import sys

from frappe.model.document import Document

from linhx_core import dang_ky_module

_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[5]


def _tra_ham_phieu_agy(khoa: str) -> Callable:
    """Tra hàm cung_cap của gói phieu_agy qua dang_ky_module (không import trực tiếp gói ở tầng lõi)."""
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



def _lay_vai_tro_hien_tai() -> list[str]:
    try:
        import frappe

        return list(frappe.get_roles() or [])
    except Exception:
        try:
            import frappe

            log_error = getattr(frappe, "log_error", None)
            if callable(log_error):
                log_error(title="LX Phieu Agy: không lấy được vai trò hiện tại")
        except Exception:
            pass
    return []


def _lay_trang_thai_cu(doc) -> str | None:
    if hasattr(doc, "get_doc_before_save"):
        truoc = doc.get_doc_before_save()
        if truoc is not None:
            return getattr(truoc, "trang_thai", None)
    if hasattr(doc, "is_new") and callable(doc.is_new) and doc.is_new():
        return None
    ten = getattr(doc, "name", None)
    if ten:
        try:
            import frappe

            if getattr(frappe, "db", None):
                return frappe.db.get_value("LX Phieu Agy", ten, "trang_thai")
        except (ImportError, AttributeError):
            pass
    return None


class LXPhieuAgy(Document):
    def _to_dict(self, trang_thai: str | None = None) -> dict:
        return {
            "name": getattr(self, "name", None),
            "loai_phieu": getattr(self, "loai_phieu", None),
            "de": getattr(self, "de", "") or "",
            "vung": getattr(self, "vung", "") or "",
            "trang_thai": trang_thai if trang_thai is not None else getattr(self, "trang_thai", None),
            "phut": getattr(self, "phut", None),
            "token": getattr(self, "token", None),
            "ly_do_tra": getattr(self, "ly_do_tra", "") or "",
        }

    def before_insert(self):
        if not getattr(self, "trang_thai", None):
            self.trang_thai = "nhap"
        if getattr(self, "phut", None) is None:
            self.phut = 0
        if getattr(self, "token", None) is None:
            self.token = 0

    def validate(self):
        if not getattr(self, "trang_thai", None):
            self.trang_thai = "nhap"
        du_lieu = self._to_dict()
        kiem_phieu = _tra_ham_phieu_agy("ops.phieu_agy.kiem_phieu")
        chuyen_trang_thai = _tra_ham_phieu_agy("ops.phieu_agy.chuyen_trang_thai")
        kiem_phieu(du_lieu)

        trang_thai_cu = _lay_trang_thai_cu(self)
        if trang_thai_cu and trang_thai_cu != self.trang_thai:
            kq = chuyen_trang_thai(
                self._to_dict(trang_thai=trang_thai_cu),
                self.trang_thai,
                vai_tro=_lay_vai_tro_hien_tai(),
                ly_do_tra=getattr(self, "ly_do_tra", "") or "",
            )
            self.trang_thai = kq["trang_thai"]
            if "ly_do_tra" in kq:
                self.ly_do_tra = kq["ly_do_tra"]
        elif trang_thai_cu is None and self.trang_thai != "nhap":
            kq = chuyen_trang_thai(
                self._to_dict(trang_thai="nhap"),
                self.trang_thai,
                vai_tro=_lay_vai_tro_hien_tai(),
                ly_do_tra=getattr(self, "ly_do_tra", "") or "",
            )
            self.trang_thai = kq["trang_thai"]
            if "ly_do_tra" in kq:
                self.ly_do_tra = kq["ly_do_tra"]
