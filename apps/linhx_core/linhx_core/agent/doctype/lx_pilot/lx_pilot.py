from __future__ import annotations

import logging

from frappe.model.document import Document

from linhx_core.agent import pilot
from linhx_core.crm.quyen_don_vi import kiem_tra_quyen_doc

logger = logging.getLogger(__name__)


def _lay_bay_gio() -> str:
    try:
        import frappe

        now_dt = getattr(getattr(frappe, "utils", None), "now_datetime", None)
        if callable(now_dt):
            return pilot.chuan_hoa_tg(now_dt())
    except (ImportError, AttributeError):
        pass
    return pilot.bay_gio()


def _lay_bat_dau_luc(doc) -> str:
    bd = getattr(doc, "bat_dau_luc", None)
    if bd:
        return pilot.chuan_hoa_tg(bd)
    tao_luc = getattr(doc, "creation", None)
    if tao_luc:
        return pilot.chuan_hoa_tg(tao_luc)
    return _lay_bay_gio()


def _ghi_log_loi(tieu_de: str, chi_tiet: str) -> None:
    logger.warning("%s: %s", tieu_de, chi_tiet)
    try:
        import frappe

        log_err = getattr(frappe, "log_error", None)
        if callable(log_err) and getattr(frappe, "db", None):
            log_err(message=chi_tiet, title=tieu_de)
    except Exception:
        pass


def _lay_ban_ghi_cu(doc) -> dict | None:
    if hasattr(doc, "get_doc_before_save"):
        truoc = doc.get_doc_before_save()
        if truoc is not None:
            return {
                "co_hoi": getattr(truoc, "co_hoi", None),
                "don_vi": getattr(truoc, "don_vi", None),
                "bat_dau_luc": getattr(truoc, "bat_dau_luc", None),
                "han_hoan_thanh": getattr(truoc, "han_hoan_thanh", None),
                "trang_thai": getattr(truoc, "trang_thai", None),
                "cac_buoc": getattr(truoc, "cac_buoc", None),
            }
    if hasattr(doc, "is_new") and callable(doc.is_new) and doc.is_new():
        return None
    ten = getattr(doc, "name", None)
    if ten:
        try:
            import frappe

            if getattr(frappe, "db", None) and callable(getattr(frappe.db, "get_value", None)):
                du_lieu = frappe.db.get_value(
                    "LX Pilot",
                    ten,
                    ["co_hoi", "don_vi", "bat_dau_luc", "han_hoan_thanh", "trang_thai", "cac_buoc"],
                    as_dict=True,
                )
                if isinstance(du_lieu, dict):
                    return du_lieu
        except (ImportError, AttributeError):
            pass
        except Exception as exc:
            _ghi_log_loi("LX Pilot: lỗi đọc bản ghi cũ", str(exc))
    return None


class LXPilot(Document):
    def _gan_thong_tin_tu_co_hoi(self) -> None:
        ma_ch = getattr(self, "co_hoi", None)
        if not ma_ch:
            return
        try:
            import frappe

            if getattr(frappe, "db", None) and callable(getattr(frappe.db, "get_value", None)):
                thong_tin = frappe.db.get_value(
                    "LX Co Hoi",
                    ma_ch,
                    ["phu_trach", "don_vi"],
                    as_dict=True,
                )
                if isinstance(thong_tin, dict):
                    if not getattr(self, "phu_trach", None) and thong_tin.get("phu_trach"):
                        self.phu_trach = thong_tin["phu_trach"]
                    dv_ch = str(thong_tin.get("don_vi") or "").strip()
                    dv_hien_tai = str(getattr(self, "don_vi", None) or "").strip()
                    if dv_ch:
                        if dv_hien_tai and dv_hien_tai != dv_ch:
                            raise ValueError("Đơn vị của Pilot phải khớp với Đơn vị của Cơ hội")
                        self.don_vi = dv_ch
        except ValueError:
            raise
        except (ImportError, AttributeError):
            pass
        except Exception as exc:
            _ghi_log_loi("LX Pilot: lỗi đọc thông tin từ LX Co Hoi", str(exc))

    def _to_dict(self) -> dict:
        return {
            "name": getattr(self, "name", None),
            "co_hoi": getattr(self, "co_hoi", None),
            "phu_trach": getattr(self, "phu_trach", "") or "",
            "don_vi": getattr(self, "don_vi", "") or "",
            "bat_dau_luc": getattr(self, "bat_dau_luc", None),
            "han_hoan_thanh": getattr(self, "han_hoan_thanh", None),
            "trang_thai": getattr(self, "trang_thai", None) or "dang_chay",
            "cac_buoc": getattr(self, "cac_buoc", None),
        }

    def before_insert(self) -> None:
        self._gan_thong_tin_tu_co_hoi()
        kiem_tra_quyen_doc(self, "before_insert")
        bat_dau = _lay_bat_dau_luc(self)
        mau = pilot.tao_pilot(
            co_hoi=str(getattr(self, "co_hoi", "") or ""),
            bat_dau_luc=bat_dau,
            phu_trach=str(getattr(self, "phu_trach", "") or ""),
        )
        self.co_hoi = mau["co_hoi"]
        self.phu_trach = mau["phu_trach"]
        self.bat_dau_luc = mau["bat_dau_luc"]
        if not getattr(self, "trang_thai", None):
            self.trang_thai = mau["trang_thai"]
        if not getattr(self, "cac_buoc", None):
            self.cac_buoc = mau["cac_buoc"]
        if not getattr(self, "han_hoan_thanh", None):
            self.han_hoan_thanh = mau["han_hoan_thanh"]
        else:
            try:
                dt_hien_tai = pilot._parse_tg(self.han_hoan_thanh)
                dt_toi_da = pilot._parse_tg(mau["han_hoan_thanh"])
                dt_bat_dau = pilot._parse_tg(mau["bat_dau_luc"])
                if dt_hien_tai > dt_toi_da or dt_hien_tai < dt_bat_dau:
                    self.han_hoan_thanh = mau["han_hoan_thanh"]
                else:
                    self.han_hoan_thanh = dt_hien_tai.strftime(pilot.DINH_DANG_TG)
            except ValueError:
                self.han_hoan_thanh = mau["han_hoan_thanh"]

    def validate(self) -> None:
        self._gan_thong_tin_tu_co_hoi()
        kiem_tra_quyen_doc(self, "validate")
        if not getattr(self, "bat_dau_luc", None):
            self.bat_dau_luc = _lay_bat_dau_luc(self)
        if not getattr(self, "cac_buoc", None):
            self.cac_buoc = pilot.tao_cac_buoc_mac_dinh()

        cu = _lay_ban_ghi_cu(self)
        if isinstance(cu, dict):
            if cu.get("co_hoi") and str(getattr(self, "co_hoi", "") or "").strip() != str(cu["co_hoi"]).strip():
                raise ValueError("Không được đổi cơ hội của Pilot đã tạo")
            tt_cu = cu.get("trang_thai")
            if tt_cu in ("xong", "huy") and getattr(self, "trang_thai", None) != tt_cu:
                raise ValueError(f"Pilot đã ở trạng thái {tt_cu!r}, không được chuyển ngược")
            if cu.get("bat_dau_luc"):
                self.bat_dau_luc = pilot.chuan_hoa_tg(cu["bat_dau_luc"])
            if cu.get("cac_buoc"):
                buoc_cu = pilot.doc_cac_buoc(cu["cac_buoc"])
                buoc_moi = pilot.doc_cac_buoc(self.cac_buoc)
                for b_cu, b_moi in zip(buoc_cu, buoc_moi):
                    if b_cu["trang_thai"] == "xong" and b_moi["trang_thai"] != "xong":
                        raise ValueError(
                            f"Bước {b_cu['so']} đã hoàn thành, không được lùi về {b_moi['trang_thai']!r}"
                        )

        chuan = pilot.kiem_pilot(self._to_dict())
        self.co_hoi = chuan["co_hoi"]
        self.phu_trach = chuan["phu_trach"]
        self.bat_dau_luc = chuan["bat_dau_luc"]
        self.han_hoan_thanh = chuan["han_hoan_thanh"]
        self.trang_thai = chuan["trang_thai"]
        self.cac_buoc = chuan["cac_buoc"]

    def hoan_thanh_buoc(self, so_buoc: int, luc: str | None = None) -> dict:
        """Đánh dấu hoàn thành bước so_buoc trên tài liệu LX Pilot."""
        kq = pilot.hoan_thanh_buoc(self._to_dict(), int(so_buoc), luc or _lay_bay_gio())
        self.cac_buoc = kq["cac_buoc"]
        self.trang_thai = kq["trang_thai"]
        return kq
