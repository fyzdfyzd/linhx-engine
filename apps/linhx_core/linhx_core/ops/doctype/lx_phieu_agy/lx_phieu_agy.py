from frappe.model.document import Document

from linhx_core.ops import phieu_agy


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
        phieu_agy.kiem_phieu(du_lieu)

        trang_thai_cu = _lay_trang_thai_cu(self)
        if trang_thai_cu and trang_thai_cu != self.trang_thai:
            kq = phieu_agy.chuyen_trang_thai(
                self._to_dict(trang_thai=trang_thai_cu),
                self.trang_thai,
                vai_tro=_lay_vai_tro_hien_tai(),
                ly_do_tra=getattr(self, "ly_do_tra", "") or "",
            )
            self.trang_thai = kq["trang_thai"]
            if "ly_do_tra" in kq:
                self.ly_do_tra = kq["ly_do_tra"]
        elif trang_thai_cu is None and self.trang_thai != "nhap":
            kq = phieu_agy.chuyen_trang_thai(
                self._to_dict(trang_thai="nhap"),
                self.trang_thai,
                vai_tro=_lay_vai_tro_hien_tai(),
                ly_do_tra=getattr(self, "ly_do_tra", "") or "",
            )
            self.trang_thai = kq["trang_thai"]
            if "ly_do_tra" in kq:
                self.ly_do_tra = kq["ly_do_tra"]
