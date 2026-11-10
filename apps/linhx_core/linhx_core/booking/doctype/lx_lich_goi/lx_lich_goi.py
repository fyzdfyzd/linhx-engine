"""Controller DocType LX Lich Goi: kiểm giờ làm việc (8–18h giờ VN), chặn trùng giờ cùng người phụ trách, khoá phân quyền theo Đơn vị."""
from __future__ import annotations

import importlib
import logging
import pathlib
import sys

from frappe.model.document import Document

from linhx_core.api import tim_ham
from linhx_core.crm.quyen_don_vi import (
    co_quyen,
    dieu_kien,
    kiem_ghi,
    kiem_tra_quyen_doc,
    la_user_mien,
    lay_don_vi_cua_user,
)

logger = logging.getLogger(__name__)

_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[5]
PHUT_MAC_DINH = 30
DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"
TRANG_THAI_LICH = ("cho_goi", "da_goi", "huy")


def _goi_ham_booking(khoa: str, *args, **kwargs):
    """Tra hàm cung_cap của gói đặt lịch qua dang_ky_module và gọi động."""
    ds_duong = tim_ham("cung_cap", khoa, thu_muc_apps=_THU_MUC_APPS)
    if not ds_duong:
        raise RuntimeError(f"Chưa đăng ký hàm cung_cap cho '{khoa}' trong module.json")
    duong_ham = ds_duong[0]
    ten_module, ten_ham = duong_ham.rsplit(".", 1)
    ten_app = ten_module.split(".")[0]
    thu_muc_app = _THU_MUC_APPS / ten_app
    if thu_muc_app.is_dir() and str(thu_muc_app) not in sys.path:
        sys.path.insert(0, str(thu_muc_app))
    mod = importlib.import_module(ten_module)
    ham = getattr(mod, ten_ham)
    return ham(*args, **kwargs)


class LoiQuyenLichGoi(PermissionError, ValueError):
    """Ngoại lệ phân quyền đơn vị trên LX Lich Goi khi chạy môi trường không có frappe.throw."""


def _nem_loi_hop_le(thong_bao: str) -> None:
    try:
        import frappe

        throw_fn = getattr(frappe, "throw", None)
        if callable(throw_fn):
            exc_cls = getattr(frappe, "ValidationError", ValueError)
            throw_fn(thong_bao, exc_cls)
    except ImportError:
        pass
    raise ValueError(thong_bao)


def _nem_loi_quyen(thong_bao: str) -> None:
    try:
        import frappe

        throw_fn = getattr(frappe, "throw", None)
        if callable(throw_fn):
            exc_cls = getattr(frappe, "PermissionError", LoiQuyenLichGoi)
            throw_fn(thong_bao, exc_cls)
    except ImportError:
        pass
    raise LoiQuyenLichGoi(thong_bao)


def _ghi_log_loi(tieu_de: str, chi_tiet: str) -> None:
    logger.warning("%s: %s", tieu_de, chi_tiet)
    try:
        import frappe

        log_err = getattr(frappe, "log_error", None)
        if callable(log_err) and getattr(frappe, "db", None):
            log_err(message=chi_tiet, title=tieu_de)
    except Exception:
        pass


def _la_doc_moi(doc) -> bool:
    if doc is None:
        return False
    if isinstance(doc, dict):
        return bool(doc.get("__islocal"))
    is_new_fn = getattr(doc, "is_new", None)
    if callable(is_new_fn):
        try:
            return bool(is_new_fn())
        except Exception:
            pass
    return bool(getattr(doc, "__islocal", False))


def _lay_thuoc_tinh(doc, ten: str):
    if doc is None:
        return None
    if isinstance(doc, dict):
        return doc.get(ten)
    return getattr(doc, ten, None)


def _doc_don_vi_nguoi_hoac_co_hoi_tu_db(
    ma_nguoi: str | None,
    ma_co_hoi: str | None = None,
) -> str | None:
    try:
        import frappe
    except ImportError:
        return None

    db = getattr(frappe, "db", None)
    if db is None:
        return None
    get_value_fn = getattr(db, "get_value", None)
    if not callable(get_value_fn):
        return None

    ng = str(ma_nguoi or "").strip()
    ch = str(ma_co_hoi or "").strip()
    if ch:
        try:
            tt_ch = get_value_fn("LX Co Hoi", ch, ["don_vi", "nguoi"], as_dict=True)
            if isinstance(tt_ch, dict):
                ng_ch = str(tt_ch.get("nguoi") or "").strip()
                if not ng and ng_ch:
                    ng = ng_ch
                if not ng or not ng_ch or ng_ch == ng:
                    dv_ch = str(tt_ch.get("don_vi") or "").strip()
                    if dv_ch:
                        return dv_ch
        except Exception as exc:
            _ghi_log_loi("LX Lich Goi: lỗi đọc đơn vị từ LX Co Hoi", str(exc))

    if ng:
        try:
            dv_ng = get_value_fn("LX Nguoi", ng, "don_vi")
            if dv_ng:
                return str(dv_ng).strip()
        except Exception as exc:
            _ghi_log_loi("LX Lich Goi: lỗi đọc đơn vị từ LX Nguoi", str(exc))
    return None


def _lay_ban_ghi_cu(doc) -> dict | None:
    ten = str(_lay_thuoc_tinh(doc, "name") or "").strip()
    if ten and not _la_doc_moi(doc):
        try:
            import frappe
        except ImportError:
            frappe = None

        db = getattr(frappe, "db", None) if frappe is not None else None
        if db is not None:
            get_value_fn = getattr(db, "get_value", None)
            if callable(get_value_fn):
                try:
                    du_lieu = get_value_fn(
                        "LX Lich Goi",
                        ten,
                        [
                            "nguoi",
                            "co_hoi",
                            "phu_trach",
                            "don_vi",
                            "bat_dau",
                            "ket_thuc",
                            "phut",
                            "trang_thai",
                        ],
                        as_dict=True,
                    )
                    if isinstance(du_lieu, dict) and du_lieu:
                        return du_lieu
                except Exception as exc:
                    _ghi_log_loi("LX Lich Goi: lỗi đọc bản ghi cũ từ DB", str(exc))
                    _nem_loi_hop_le("Không đọc được bản ghi Lịch gọi hiện có từ cơ sở dữ liệu")

    if hasattr(doc, "get_doc_before_save") and callable(doc.get_doc_before_save):
        truoc = doc.get_doc_before_save()
        if truoc is not None:
            return {
                "nguoi": _lay_thuoc_tinh(truoc, "nguoi"),
                "co_hoi": _lay_thuoc_tinh(truoc, "co_hoi"),
                "phu_trach": _lay_thuoc_tinh(truoc, "phu_trach"),
                "don_vi": _lay_thuoc_tinh(truoc, "don_vi"),
                "bat_dau": _lay_thuoc_tinh(truoc, "bat_dau"),
                "ket_thuc": _lay_thuoc_tinh(truoc, "ket_thuc"),
                "phut": _lay_thuoc_tinh(truoc, "phut"),
                "trang_thai": _lay_thuoc_tinh(truoc, "trang_thai"),
            }
    return None


def _lay_ds_lich_phu_trach_db(phu_trach: str, *, khoa_dong: bool = False) -> list[dict]:
    """Đọc các lịch chưa huỷ của `phu_trach` từ DB (dùng `FOR UPDATE` khi cần khoá chống đua)."""
    pt = str(phu_trach or "").strip()
    if not pt:
        return []
    try:
        import frappe
    except ImportError:
        return []

    db = getattr(frappe, "db", None)
    if db is None:
        return []

    if khoa_dong and callable(getattr(db, "sql", None)):
        try:
            rows = db.sql(
                """
                SELECT name, nguoi, phu_trach, bat_dau, ket_thuc, phut, trang_thai, ghi_chu, co_hoi, don_vi
                FROM `tabLX Lich Goi`
                WHERE phu_trach = %s AND trang_thai != 'huy'
                ORDER BY bat_dau ASC
                FOR UPDATE
                """,
                (pt,),
                as_dict=True,
            )
            if isinstance(rows, (list, tuple)):
                return [dict(r) for r in rows if isinstance(r, dict)]
        except Exception as exc:
            _ghi_log_loi("LX Lich Goi: lỗi truy vấn FOR UPDATE", str(exc))

    get_all_fn = getattr(frappe, "get_all", None)
    if callable(get_all_fn):
        try:
            ds = get_all_fn(
                "LX Lich Goi",
                filters={"phu_trach": pt, "trang_thai": ["!=", "huy"]},
                fields=[
                    "name",
                    "nguoi",
                    "phu_trach",
                    "bat_dau",
                    "ket_thuc",
                    "phut",
                    "trang_thai",
                    "ghi_chu",
                    "co_hoi",
                    "don_vi",
                ],
                order_by="bat_dau asc",
            )
            if isinstance(ds, (list, tuple)):
                return [dict(r) for r in ds if isinstance(r, dict)]
        except Exception as exc:
            _ghi_log_loi("LX Lich Goi: lỗi get_all lịch phụ trách", str(exc))
    return []


def frappe_has_permission(doc, ptype: str | None = None, user: str | None = None, **kwargs) -> bool:
    """Kiểm tra quyền truy cập trên LX Lich Goi theo Đơn vị (User Permission LX Don Vi)."""
    try:
        import frappe
    except ImportError:
        return True

    session_obj = getattr(frappe, "session", None)
    nguoi_dung = user or (getattr(session_obj, "user", None) if session_obj is not None else None)
    if not nguoi_dung:
        return session_obj is None

    if la_user_mien(nguoi_dung):
        return True

    ds_don_vi = lay_don_vi_cua_user(nguoi_dung)
    if not ds_don_vi:
        return False

    if doc is None or isinstance(doc, str):
        return bool(ds_don_vi)

    cu = _lay_ban_ghi_cu(doc)
    dv_goc_cu: str | None = None
    if isinstance(cu, dict):
        dv_goc_cu = _doc_don_vi_nguoi_hoac_co_hoi_tu_db(cu.get("nguoi"), cu.get("co_hoi"))
        if dv_goc_cu is not None and not co_quyen({"don_vi": dv_goc_cu}, ds_don_vi, False):
            return False
        dv_cu = str(cu.get("don_vi") or dv_goc_cu or "").strip()
        if not co_quyen({"don_vi": dv_cu}, ds_don_vi, False):
            return False

    ng_moi = str(_lay_thuoc_tinh(doc, "nguoi") or "").strip()
    ch_moi = str(_lay_thuoc_tinh(doc, "co_hoi") or "").strip()
    dv_goc_moi = _doc_don_vi_nguoi_hoac_co_hoi_tu_db(ng_moi, ch_moi) if (ng_moi or ch_moi) else None
    dv_moi = str(_lay_thuoc_tinh(doc, "don_vi") or "").strip()
    if not dv_moi and cu is None and dv_goc_moi:
        dv_moi = dv_goc_moi

    if dv_moi and dv_goc_moi and dv_moi != dv_goc_moi:
        return False

    if isinstance(cu, dict):
        dv_cu_str = str(cu.get("don_vi") or dv_goc_cu or "").strip()
        if dv_cu_str and dv_moi and dv_cu_str != dv_moi:
            return False

    doc_cu_kiem = (
        {"don_vi": str(cu.get("don_vi") or dv_goc_cu or "").strip()}
        if isinstance(cu, dict)
        else None
    )
    return kiem_ghi({"don_vi": dv_moi}, doc_cu_kiem, dv_goc_moi, ds_don_vi, False)


has_permission = frappe_has_permission


def frappe_permission_query_conditions(
    user: str | None = None, doctype: str | None = None, **kwargs
) -> str:
    """Sinh điều kiện SQL lọc danh sách LX Lich Goi theo Đơn vị."""
    try:
        import frappe
    except ImportError:
        return ""

    session_obj = getattr(frappe, "session", None)
    nguoi_dung = user or (getattr(session_obj, "user", None) if session_obj is not None else None)
    mien = la_user_mien(nguoi_dung)
    ds_don_vi = [] if mien else lay_don_vi_cua_user(nguoi_dung)
    return dieu_kien(doctype or "LX Lich Goi", ds_don_vi, mien)


get_permission_query_conditions = frappe_permission_query_conditions


def kiem_tra_quyen_lich_goi_doc(doc, method: str | None = None) -> None:
    if not isinstance(doc, dict) and not getattr(doc, "doctype", None):
        doc.doctype = "LX Lich Goi"

    ng_moi = str(_lay_thuoc_tinh(doc, "nguoi") or "").strip()
    ch_moi = str(_lay_thuoc_tinh(doc, "co_hoi") or "").strip()
    dv_hien_tai = str(_lay_thuoc_tinh(doc, "don_vi") or "").strip()
    if ng_moi or ch_moi:
        dv_db = _doc_don_vi_nguoi_hoac_co_hoi_tu_db(ng_moi, ch_moi)
        if dv_hien_tai and dv_db and dv_hien_tai != dv_db:
            _nem_loi_quyen("Đơn vị của Lịch gọi phải khớp với Đơn vị của Người / Cơ hội")

    try:
        import frappe
    except ImportError:
        return

    if getattr(frappe, "session", None) is None:
        return
    if la_user_mien() or getattr(getattr(doc, "flags", None), "ignore_permissions", False):
        return

    ptype = "read" if method == "onload" else "write"
    if not frappe_has_permission(doc, ptype=ptype):
        _nem_loi_quyen("Không có quyền thao tác trên Lịch gọi của đơn vị khác")

    kiem_tra_quyen_doc(doc, method)


class LXLichGoi(Document):
    doctype = "LX Lich Goi"

    def has_permission(
        self, permtype: str = "read", *, debug: bool = False, user: str | None = None
    ) -> bool:
        if getattr(getattr(self, "flags", None), "ignore_permissions", False):
            return True
        if not frappe_has_permission(self, ptype=permtype, user=user):
            return False
        sup = getattr(super(), "has_permission", None)
        if callable(sup):
            return bool(sup(permtype, debug=debug, user=user))
        return True

    def onload(self) -> None:
        kiem_tra_quyen_lich_goi_doc(self, "onload")

    def _gan_thong_tin_tu_nguoi_va_co_hoi(self) -> None:
        ng = str(getattr(self, "nguoi", None) or "").strip()
        ch = str(getattr(self, "co_hoi", None) or "").strip()
        if not ng:
            _nem_loi_hop_le("Lịch gọi thiếu mã khách hàng / người đặt (nguoi)")
        self.nguoi = ng
        if ch:
            try:
                import frappe

                db = getattr(frappe, "db", None)
                get_val = getattr(db, "get_value", None) if db is not None else None
                if callable(get_val):
                    tt_ch = get_val("LX Co Hoi", ch, ["nguoi", "don_vi"], as_dict=True)
                    if isinstance(tt_ch, dict) and tt_ch:
                        ng_ch = str(tt_ch.get("nguoi") or "").strip()
                        if ng_ch and ng_ch != ng:
                            _nem_loi_hop_le("Cơ hội không thuộc về khách hàng đặt lịch")
            except ImportError:
                pass
            self.co_hoi = ch

        dv_db = _doc_don_vi_nguoi_hoac_co_hoi_tu_db(ng, ch)
        if dv_db:
            dv_hien_tai = str(getattr(self, "don_vi", None) or "").strip()
            if dv_hien_tai and dv_hien_tai != dv_db:
                _nem_loi_quyen("Đơn vị của Lịch gọi phải khớp với Đơn vị của Người / Cơ hội")
            self.don_vi = dv_db

    def _kiem_va_chuan_hoa_lich(self) -> None:
        self._gan_thong_tin_tu_nguoi_va_co_hoi()
        kiem_tra_quyen_lich_goi_doc(self, "validate")

        pt = str(getattr(self, "phu_trach", None) or "").strip()
        if not pt:
            _nem_loi_hop_le("Lịch gọi thiếu người phụ trách (phu_trach)")
        self.phu_trach = pt

        tt = str(getattr(self, "trang_thai", None) or "cho_goi").strip()
        if tt not in TRANG_THAI_LICH:
            _nem_loi_hop_le(f"Trạng thái lịch gọi không hợp lệ: {tt!r}")
        self.trang_thai = tt

        try:
            dt_bd, dt_kt, phut_int = _goi_ham_booking(
                "booking.kiem_gio_lam_viec",
                getattr(self, "bat_dau", None),
                getattr(self, "phut", PHUT_MAC_DINH),
            )
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return

        self.bat_dau = dt_bd.strftime(DINH_DANG_TG)
        self.ket_thuc = dt_kt.strftime(DINH_DANG_TG)
        self.phut = phut_int

        if self.trang_thai != "huy":
            ds_hien_co = getattr(self, "_ds_lich_hien_co", None)
            if ds_hien_co is None:
                ds_hien_co = _lay_ds_lich_phu_trach_db(self.phu_trach, khoa_dong=True)
            try:
                _goi_ham_booking(
                    "booking.kiem_trung_gio",
                    ds_hien_co,
                    self.phu_trach,
                    dt_bd,
                    dt_kt,
                    bo_qua_name=str(getattr(self, "name", None) or "").strip() or None,
                )
            except ValueError as exc:
                _nem_loi_hop_le(str(exc))
                return

    def before_insert(self) -> None:
        self._kiem_va_chuan_hoa_lich()

    def validate(self) -> None:
        cu = _lay_ban_ghi_cu(self)
        if isinstance(cu, dict):
            kiem_tra_quyen_lich_goi_doc(self, "validate")
            if cu.get("nguoi") and str(getattr(self, "nguoi", "") or "").strip() != str(cu["nguoi"]).strip():
                _nem_loi_hop_le("Không được đổi người đặt của Lịch gọi đã tạo")
            if cu.get("don_vi") and str(getattr(self, "don_vi", "") or "").strip() not in ("", str(cu["don_vi"]).strip()):
                _nem_loi_quyen("Không được phép đổi đơn vị của Lịch gọi")
        self._kiem_va_chuan_hoa_lich()

    def before_save(self) -> None:
        kiem_tra_quyen_lich_goi_doc(self, "before_save")

    def on_trash(self) -> None:
        kiem_tra_quyen_lich_goi_doc(self, "on_trash")
