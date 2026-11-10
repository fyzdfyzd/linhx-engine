"""Controller DocType LX Pilot: gắn Cơ hội, kế thừa và khoá chặt phân quyền theo Đơn vị (LX Don Vi).

Cơ chế phân quyền đọc/ghi theo Đơn vị ngay trong vùng agent/**:
1. Trường `don_vi` (Link -> LX Don Vi, reqd=1) và `co_hoi` (Link -> LX Co Hoi, reqd=1) bắt buộc khác rỗng
   từ `_gan_thong_tin_tu_co_hoi` và `validate`. Nhờ `don_vi` không bao giờ rỗng và vai trò `LX Nhan Vien`
   không bật `ignore_user_permissions`, `DatabaseQuery.add_user_permissions` của Frappe tự động lọc
   mọi truy vấn danh sách (`get_list`, `/api/resource/LX Pilot`, `reportview`) theo `User Permission`
   (`allow = "LX Don Vi"`) của nhân viên.
2. `LXPilot.has_permission` ghi đè `Document.has_permission` (được gọi bởi `GET /api/resource/LX Pilot/<name>`,
   `/api/v2/document/LX Pilot/<name>`, `frappe.client.get`, `getdoc`, `save`, `insert`, `delete`) kết hợp
   `onload`, `before_insert`, `validate`, `before_save`, `on_trash` đối chiếu trực tiếp bản ghi trong DB
   và đơn vị của `LX Co Hoi` qua `quyen_don_vi`.
"""
from __future__ import annotations

import importlib
import json
import logging
import pathlib
import sys

from frappe.model.document import Document

from linhx_core import dang_ky_module
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


def _tra_ham_pilot(khoa: str):
    """Tra hàm cung_cap của gói Agent Force qua dang_ky_module (không import trực tiếp gói ở tầng lõi)."""
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


class LoiQuyenPilot(PermissionError, ValueError):
    """Ngoại lệ phân quyền đơn vị trên LX Pilot khi chạy môi trường không có frappe.throw."""


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
            exc_cls = getattr(frappe, "PermissionError", LoiQuyenPilot)
            throw_fn(thong_bao, exc_cls)
    except ImportError:
        pass
    raise LoiQuyenPilot(thong_bao)


def _lay_bay_gio() -> str:
    chuan_hoa_tg = _tra_ham_pilot("agent.pilot.chuan_hoa_tg")
    bay_gio = _tra_ham_pilot("agent.pilot.bay_gio")
    try:
        import frappe

        now_dt = getattr(getattr(frappe, "utils", None), "now_datetime", None)
        if callable(now_dt):
            return chuan_hoa_tg(now_dt())
    except (ImportError, AttributeError):
        pass
    return bay_gio()


def _lay_bat_dau_luc(doc) -> str:
    chuan_hoa_tg = _tra_ham_pilot("agent.pilot.chuan_hoa_tg")
    bd = getattr(doc, "bat_dau_luc", None)
    if bd:
        return chuan_hoa_tg(bd)
    tao_luc = getattr(doc, "creation", None)
    if tao_luc:
        return chuan_hoa_tg(tao_luc)
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


def _doc_don_vi_co_hoi_tu_db(ma_ch: str | None, bat_buoc: bool = False) -> str | None:
    ma = str(ma_ch or "").strip()
    if not ma:
        return None
    try:
        import frappe
    except ImportError:
        return None

    db = getattr(frappe, "db", None)
    if db is None:
        return None

    get_value_fn = getattr(db, "get_value", None)
    if not callable(get_value_fn):
        if bat_buoc:
            _nem_loi_hop_le("Không truy cập được cơ sở dữ liệu để đọc Cơ hội")
        return None

    try:
        thong_tin = get_value_fn("LX Co Hoi", ma, ["don_vi", "nguoi"], as_dict=True)
    except Exception as exc:
        _ghi_log_loi("LX Pilot: lỗi đọc đơn vị của LX Co Hoi", str(exc))
        if bat_buoc:
            _nem_loi_hop_le(f"Không đọc được Cơ hội {ma!r}")
        return None

    if not isinstance(thong_tin, dict) or not thong_tin:
        if bat_buoc:
            _nem_loi_hop_le(f"Cơ hội {ma!r} không tồn tại")
        return None

    dv = str(thong_tin.get("don_vi") or "").strip()
    if not dv and thong_tin.get("nguoi"):
        try:
            dv_nguoi = get_value_fn("LX Nguoi", str(thong_tin["nguoi"]).strip(), "don_vi")
            dv = str(dv_nguoi or "").strip()
        except Exception as exc:
            _ghi_log_loi("LX Pilot: lỗi đọc đơn vị từ LX Nguoi", str(exc))
            if bat_buoc:
                _nem_loi_hop_le(f"Không đọc được Đơn vị của Cơ hội {ma!r}")
            return None
    return dv or ""


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
            if not callable(get_value_fn):
                _nem_loi_hop_le("Không truy cập được cơ sở dữ liệu để đọc bản ghi Pilot hiện có")
            try:
                du_lieu = get_value_fn(
                    "LX Pilot",
                    ten,
                    ["co_hoi", "don_vi", "bat_dau_luc", "han_hoan_thanh", "trang_thai", "cac_buoc"],
                    as_dict=True,
                )
            except Exception as exc:
                _ghi_log_loi("LX Pilot: lỗi đọc bản ghi cũ từ DB", str(exc))
                _nem_loi_hop_le("Không đọc được bản ghi Pilot hiện có từ cơ sở dữ liệu")
                return None
            if isinstance(du_lieu, dict) and du_lieu:
                return du_lieu

    if hasattr(doc, "get_doc_before_save") and callable(doc.get_doc_before_save):
        truoc = doc.get_doc_before_save()
        if truoc is not None:
            return {
                "co_hoi": _lay_thuoc_tinh(truoc, "co_hoi"),
                "don_vi": _lay_thuoc_tinh(truoc, "don_vi"),
                "bat_dau_luc": _lay_thuoc_tinh(truoc, "bat_dau_luc"),
                "han_hoan_thanh": _lay_thuoc_tinh(truoc, "han_hoan_thanh"),
                "trang_thai": _lay_thuoc_tinh(truoc, "trang_thai"),
                "cac_buoc": _lay_thuoc_tinh(truoc, "cac_buoc"),
            }
    return None


def frappe_has_permission(doc, ptype: str | None = None, user: str | None = None, **kwargs) -> bool:
    """Kiểm tra quyền truy cập (read/write/create/delete) trên LX Pilot theo Đơn vị (User Permission LX Don Vi)."""
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
    dv_co_hoi_cu: str | None = None
    if isinstance(cu, dict):
        ch_cu = str(cu.get("co_hoi") or "").strip()
        if ch_cu:
            dv_co_hoi_cu = _doc_don_vi_co_hoi_tu_db(ch_cu, bat_buoc=False)
            if dv_co_hoi_cu is not None and not co_quyen({"don_vi": dv_co_hoi_cu}, ds_don_vi, False):
                return False
        dv_cu = str(cu.get("don_vi") or dv_co_hoi_cu or "").strip()
        if not co_quyen({"don_vi": dv_cu}, ds_don_vi, False):
            return False

    ch_moi = str(_lay_thuoc_tinh(doc, "co_hoi") or "").strip()
    dv_co_hoi_moi = _doc_don_vi_co_hoi_tu_db(ch_moi, bat_buoc=False) if ch_moi else None
    dv_moi = str(_lay_thuoc_tinh(doc, "don_vi") or "").strip()
    if not dv_moi and cu is None and dv_co_hoi_moi:
        dv_moi = dv_co_hoi_moi

    if dv_moi and dv_co_hoi_moi and dv_moi != dv_co_hoi_moi:
        return False

    if isinstance(cu, dict):
        dv_cu_str = str(cu.get("don_vi") or dv_co_hoi_cu or "").strip()
        ch_cu_str = str(cu.get("co_hoi") or "").strip()
        if dv_cu_str and dv_moi and dv_cu_str != dv_moi:
            return False
        if ch_cu_str and ch_moi and ch_cu_str != ch_moi:
            return False

    doc_cu_kiem = (
        {"don_vi": str(cu.get("don_vi") or dv_co_hoi_cu or "").strip()}
        if isinstance(cu, dict)
        else None
    )
    return kiem_ghi({"don_vi": dv_moi}, doc_cu_kiem, dv_co_hoi_moi, ds_don_vi, False)


has_permission = frappe_has_permission


def frappe_permission_query_conditions(
    user: str | None = None, doctype: str | None = None, **kwargs
) -> str:
    """Sinh điều kiện SQL lọc danh sách LX Pilot theo Đơn vị (User Permission LX Don Vi)."""
    try:
        import frappe
    except ImportError:
        return ""

    session_obj = getattr(frappe, "session", None)
    nguoi_dung = user or (getattr(session_obj, "user", None) if session_obj is not None else None)
    mien = la_user_mien(nguoi_dung)
    ds_don_vi = [] if mien else lay_don_vi_cua_user(nguoi_dung)
    return dieu_kien(doctype or "LX Pilot", ds_don_vi, mien)


get_permission_query_conditions = frappe_permission_query_conditions


def kiem_tra_quyen_pilot_doc(doc, method: str | None = None) -> None:
    """Kiểm tra quyền đọc/ghi/tạo/xoá trên tài liệu LX Pilot theo cả doc.don_vi, bản ghi DB cũ và LX Co Hoi."""
    if not isinstance(doc, dict) and not getattr(doc, "doctype", None):
        doc.doctype = "LX Pilot"

    ch_moi = str(_lay_thuoc_tinh(doc, "co_hoi") or "").strip()
    dv_hien_tai = str(_lay_thuoc_tinh(doc, "don_vi") or "").strip()
    if ch_moi:
        dv_ch_db = _doc_don_vi_co_hoi_tu_db(ch_moi, bat_buoc=False)
        if dv_hien_tai and dv_ch_db and dv_hien_tai != dv_ch_db:
            _nem_loi_quyen("Đơn vị của Pilot phải khớp với Đơn vị của Cơ hội")

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
        _nem_loi_quyen("Không có quyền thao tác trên Pilot của đơn vị khác")

    kiem_tra_quyen_doc(doc, method)


class LXPilot(Document):
    doctype = "LX Pilot"

    def has_permission(
        self, permtype: str = "read", *, debug: bool = False, user: str | None = None
    ) -> bool:
        """Ghi đè Document.has_permission để chặn đọc/ghi/xoá Pilot chéo Đơn vị qua API và Desk."""
        if getattr(getattr(self, "flags", None), "ignore_permissions", False):
            return True
        if not frappe_has_permission(self, ptype=permtype, user=user):
            return False
        sup = getattr(super(), "has_permission", None)
        if callable(sup):
            return bool(sup(permtype, debug=debug, user=user))
        return True

    def onload(self) -> None:
        kiem_tra_quyen_pilot_doc(self, "onload")
        if isinstance(getattr(self, "cac_buoc", None), str) and str(self.cac_buoc).strip():
            try:
                doc_cac_buoc = _tra_ham_pilot("agent.pilot.doc_cac_buoc")
                self.cac_buoc = doc_cac_buoc(self.cac_buoc)
            except ValueError:
                pass

    def get_valid_dict(self, *args, **kwargs):
        sup = getattr(super(), "get_valid_dict", None)
        if not callable(sup):
            return self._to_dict()
        buoc_goc = getattr(self, "cac_buoc", None)
        if isinstance(buoc_goc, (list, tuple)):
            try:
                self.cac_buoc = json.dumps(list(buoc_goc), ensure_ascii=False)
                return sup(*args, **kwargs)
            finally:
                self.cac_buoc = list(buoc_goc)
        return sup(*args, **kwargs)

    def _gan_thong_tin_tu_co_hoi(self) -> None:
        ma_ch = str(getattr(self, "co_hoi", None) or "").strip()
        if not ma_ch:
            _nem_loi_hop_le("Pilot thiếu mã cơ hội (co_hoi)")
        self.co_hoi = ma_ch

        try:
            import frappe
        except ImportError:
            return

        db = getattr(frappe, "db", None)
        if db is None:
            return

        get_value_fn = getattr(db, "get_value", None)
        if not callable(get_value_fn):
            _nem_loi_hop_le("Không truy cập được cơ sở dữ liệu để đọc Cơ hội")

        try:
            thong_tin = get_value_fn(
                "LX Co Hoi",
                ma_ch,
                ["phu_trach", "don_vi", "nguoi"],
                as_dict=True,
            )
        except Exception as exc:
            _ghi_log_loi("LX Pilot: lỗi đọc thông tin từ LX Co Hoi", str(exc))
            _nem_loi_hop_le(f"Không đọc được thông tin Cơ hội {ma_ch!r}")
            return

        if not isinstance(thong_tin, dict) or not thong_tin:
            _nem_loi_hop_le(f"Cơ hội {ma_ch!r} không tồn tại")
            return

        if not getattr(self, "phu_trach", None) and thong_tin.get("phu_trach"):
            self.phu_trach = thong_tin["phu_trach"]

        dv_ch = str(thong_tin.get("don_vi") or "").strip()
        if not dv_ch and thong_tin.get("nguoi"):
            try:
                dv_nguoi = get_value_fn("LX Nguoi", str(thong_tin["nguoi"]).strip(), "don_vi")
                dv_ch = str(dv_nguoi or "").strip()
            except Exception as exc:
                _ghi_log_loi("LX Pilot: lỗi đọc đơn vị từ LX Nguoi của Cơ hội", str(exc))
                _nem_loi_hop_le(f"Không đọc được Đơn vị của Cơ hội {ma_ch!r}")
                return

        if not dv_ch:
            _nem_loi_hop_le(f"Cơ hội {ma_ch!r} chưa có Đơn vị hợp lệ")
            return

        dv_hien_tai = str(getattr(self, "don_vi", None) or "").strip()
        if dv_hien_tai and dv_hien_tai != dv_ch:
            _nem_loi_quyen("Đơn vị của Pilot phải khớp với Đơn vị của Cơ hội")
        self.don_vi = dv_ch

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
        kiem_tra_quyen_pilot_doc(self, "before_insert")
        tao_pilot = _tra_ham_pilot("agent.pilot.tao_pilot")
        chuan_hoa_tg = _tra_ham_pilot("agent.pilot.chuan_hoa_tg")
        try:
            bat_dau = _lay_bat_dau_luc(self)
            mau = tao_pilot(
                co_hoi=str(getattr(self, "co_hoi", "") or ""),
                bat_dau_luc=bat_dau,
                phu_trach=str(getattr(self, "phu_trach", "") or ""),
            )
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return

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
                han_chuan = chuan_hoa_tg(self.han_hoan_thanh)
                if han_chuan > mau["han_hoan_thanh"] or han_chuan < mau["bat_dau_luc"]:
                    self.han_hoan_thanh = mau["han_hoan_thanh"]
                else:
                    self.han_hoan_thanh = han_chuan
            except ValueError:
                self.han_hoan_thanh = mau["han_hoan_thanh"]

    def validate(self) -> None:
        cu = _lay_ban_ghi_cu(self)
        if isinstance(cu, dict):
            # Kiểm quyền trên bản ghi cũ trước khi xử lý các trường được gửi lên
            kiem_tra_quyen_pilot_doc(self, "validate")
            if cu.get("co_hoi") and str(getattr(self, "co_hoi", "") or "").strip() != str(cu["co_hoi"]).strip():
                _nem_loi_hop_le("Không được đổi cơ hội của Pilot đã tạo")
            if cu.get("don_vi") and str(getattr(self, "don_vi", "") or "").strip() not in ("", str(cu["don_vi"]).strip()):
                _nem_loi_quyen("Không được phép đổi đơn vị của Pilot")

        self._gan_thong_tin_tu_co_hoi()
        kiem_tra_quyen_pilot_doc(self, "validate")

        tao_cac_buoc_mac_dinh = _tra_ham_pilot("agent.pilot.tao_cac_buoc_mac_dinh")
        chuan_hoa_tg = _tra_ham_pilot("agent.pilot.chuan_hoa_tg")
        doc_cac_buoc = _tra_ham_pilot("agent.pilot.doc_cac_buoc")
        kiem_pilot = _tra_ham_pilot("agent.pilot.kiem_pilot")
        try:
            if not getattr(self, "bat_dau_luc", None):
                self.bat_dau_luc = _lay_bat_dau_luc(self)
            if not getattr(self, "cac_buoc", None):
                self.cac_buoc = tao_cac_buoc_mac_dinh()

            if isinstance(cu, dict):
                tt_cu = cu.get("trang_thai")
                if tt_cu in ("xong", "huy") and getattr(self, "trang_thai", None) != tt_cu:
                    _nem_loi_hop_le(f"Pilot đã ở trạng thái {tt_cu!r}, không được chuyển ngược")
                if cu.get("bat_dau_luc"):
                    self.bat_dau_luc = chuan_hoa_tg(cu["bat_dau_luc"])
                if cu.get("cac_buoc"):
                    buoc_cu = doc_cac_buoc(cu["cac_buoc"])
                    buoc_moi = doc_cac_buoc(self.cac_buoc)
                    for b_cu, b_moi in zip(buoc_cu, buoc_moi):
                        if b_cu["trang_thai"] == "xong" and b_moi["trang_thai"] != "xong":
                            _nem_loi_hop_le(
                                f"Bước {b_cu['so']} đã hoàn thành, không được lùi về {b_moi['trang_thai']!r}"
                            )

            chuan = kiem_pilot(self._to_dict())
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return

        self.co_hoi = chuan["co_hoi"]
        self.phu_trach = chuan["phu_trach"]
        self.bat_dau_luc = chuan["bat_dau_luc"]
        self.han_hoan_thanh = chuan["han_hoan_thanh"]
        self.trang_thai = chuan["trang_thai"]
        self.cac_buoc = chuan["cac_buoc"]

    def before_save(self) -> None:
        kiem_tra_quyen_pilot_doc(self, "before_save")

    def on_trash(self) -> None:
        kiem_tra_quyen_pilot_doc(self, "on_trash")

    def hoan_thanh_buoc(self, so_buoc: int, luc: str | None = None) -> dict:
        """Đánh dấu hoàn thành bước so_buoc trên tài liệu LX Pilot."""
        hoan_thanh = _tra_ham_pilot("agent.pilot.hoan_thanh_buoc")
        try:
            kq = hoan_thanh(self._to_dict(), int(so_buoc), luc or _lay_bay_gio())
        except ValueError as exc:
            _nem_loi_hop_le(str(exc))
            return {}
        self.cac_buoc = kq["cac_buoc"]
        self.trang_thai = kq["trang_thai"]
        return kq
