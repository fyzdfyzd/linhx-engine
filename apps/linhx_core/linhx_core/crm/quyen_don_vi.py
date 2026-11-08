"""A4: Phân quyền dữ liệu theo Đơn vị (LX Don Vi) cho người dùng CRM.

Đơn vị của user chỉ lấy từ User Permission (allow = "LX Don Vi").
Người dùng có vai trò System Manager hoặc Administrator được miễn (mien = True).
Người của đơn vị dùng vai trò "LX Nhan Vien".
"""
from linhx_core.co_module import (
    frappe_has_permission as _co_module_has_permission,
    frappe_permission_query_conditions as _co_module_query_conditions,
)

VAI_TRO_NHAN_VIEN = "LX Nhan Vien"


def _ghi_loi_frappe(tieu_de: str) -> None:
    try:
        import frappe

        if callable(getattr(frappe, "logger", None)):
            frappe.logger("linhx_core").error(tieu_de)
    except Exception:
        pass


def dam_bao_vai_tro() -> None:
    """Đảm bảo vai trò 'LX Nhan Vien' tồn tại khi cài hoặc migrate app."""
    try:
        import frappe

        if not getattr(frappe, "db", None):
            return
        if not frappe.db.exists("Role", VAI_TRO_NHAN_VIEN):
            doc = frappe.get_doc(
                {
                    "doctype": "Role",
                    "role_name": VAI_TRO_NHAN_VIEN,
                    "desk_access": 1,
                    "disabled": 0,
                }
            )
            doc.insert(ignore_permissions=True)
            if callable(getattr(frappe.db, "commit", None)):
                frappe.db.commit()
    except Exception:
        _ghi_loi_frappe("quyen_don_vi: loi tao vai tro LX Nhan Vien")


def _chuan_hoa_ds_don_vi(don_vi_cua_user) -> list[str]:
    if not don_vi_cua_user:
        return []
    if isinstance(don_vi_cua_user, str):
        don_vi_cua_user = [don_vi_cua_user]
    kq: list[str] = []
    for dv in don_vi_cua_user:
        if dv is None:
            continue
        chu = str(dv).strip()
        if chu and chu not in kq:
            kq.append(chu)
    return kq


def _escape_sql_don_vi(gia_tri: str) -> str:
    return gia_tri.replace("\\", "\\\\").replace("'", "''")


def _lay_thuoc_tinh(doc, ten: str):
    if doc is None:
        return None
    if isinstance(doc, dict):
        return doc.get(ten)
    return getattr(doc, ten, None)


def _lay_don_vi(doc) -> str:
    return str(_lay_thuoc_tinh(doc, "don_vi") or "").strip()


def co_quyen(doc: dict, don_vi_cua_user: list[str], mien: bool) -> bool:
    """Kiểm tra quyền truy cập bản ghi theo Đơn vị.

    - mien (System Manager/Administrator) luôn True.
    - doc['don_vi'] trống -> chỉ người được miễn thấy (trả False nếu không miễn).
    - Còn lại trả True khi doc['don_vi'] thuộc don_vi_cua_user.
    """
    if bool(mien):
        return True
    if doc is None:
        return False
    don_vi_str = _lay_don_vi(doc)
    if not don_vi_str:
        return False
    ds = _chuan_hoa_ds_don_vi(don_vi_cua_user)
    return don_vi_str in ds


def dieu_kien(doctype: str, don_vi_cua_user: list[str], mien: bool) -> str:
    """Sinh biểu thức SQL cho permission_query_conditions theo Đơn vị.

    - mien -> ""
    - không đơn vị -> "1=0"
    - còn lại -> "`tab<doctype>`.`don_vi` in ('X', 'Y')" (đã escape dấu ')
    """
    if bool(mien):
        return ""
    ds = _chuan_hoa_ds_don_vi(don_vi_cua_user)
    if not ds:
        return "1=0"
    ten_bang = str(doctype or "").replace("`", "")
    danh_sach_sql = ", ".join(f"'{_escape_sql_don_vi(dv)}'" for dv in ds)
    return f"`tab{ten_bang}`.`don_vi` in ({danh_sach_sql})"


def don_vi_can_kiem(
    doc_moi: dict,
    doc_cu: dict | None,
    don_vi_nguoi: str | None,
) -> list[str]:
    """Tập đơn vị phải có quyền: doc_cu['don_vi'] (trong DB), doc_moi['don_vi'], và don_vi_nguoi (LX Co Hoi).
    Bỏ giá trị trống, không trùng.
    """
    kq: list[str] = []
    for dv in (
        _lay_don_vi(doc_cu),
        _lay_don_vi(doc_moi),
        str(don_vi_nguoi or "").strip(),
    ):
        if dv and dv not in kq:
            kq.append(dv)
    return kq


def kiem_ghi(
    doc_moi: dict,
    doc_cu: dict | None,
    don_vi_nguoi: str | None,
    don_vi_cua_user: list[str],
    mien: bool,
) -> bool:
    """Kiểm quyền ghi/đọc theo bản ghi trong DB:
    - mien luôn True
    - không có đơn vị nào để kiểm -> False
    - mọi đơn vị trong don_vi_can_kiem phải thuộc don_vi_cua_user
    """
    if bool(mien):
        return True
    if doc_cu is not None and not _lay_don_vi(doc_cu):
        return False
    if don_vi_nguoi is not None and not str(don_vi_nguoi).strip():
        return False
    if doc_moi is not None and not _lay_don_vi(doc_moi) and not str(don_vi_nguoi or "").strip():
        return False
    can_kiem = don_vi_can_kiem(doc_moi, doc_cu, don_vi_nguoi)
    if not can_kiem:
        return False
    ds = _chuan_hoa_ds_don_vi(don_vi_cua_user)
    if not ds:
        return False
    return all(dv in ds for dv in can_kiem)


def la_user_mien(user: str | None = None) -> bool:
    """Trả True nếu user là Administrator hoặc có role System Manager."""
    import frappe

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if not nguoi_dung or nguoi_dung == "Guest":
        return False
    if nguoi_dung == "Administrator":
        return True
    try:
        roles = set(frappe.get_roles(nguoi_dung) or [])
    except Exception:
        _ghi_loi_frappe("quyen_don_vi: loi doc roles")
        roles = set()
    return "System Manager" in roles


def lay_don_vi_cua_user(user: str | None = None) -> list[str]:
    """Lấy danh sách Đơn vị của user CHỈ từ User Permission (allow = 'LX Don Vi')."""
    import frappe

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if not nguoi_dung or nguoi_dung in ("Guest", "Administrator"):
        return []

    ds: list[str] = []
    try:
        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "sql", None)):
            rows = db.sql(
                "SELECT for_value FROM `tabUser Permission` WHERE user=%s AND allow=%s",
                (nguoi_dung, "LX Don Vi"),
            )
            for r in rows or []:
                if r and r[0]:
                    ds.append(str(r[0]))
        elif callable(getattr(frappe, "get_all", None)):
            vals = frappe.get_all(
                "User Permission",
                filters={"user": nguoi_dung, "allow": "LX Don Vi"},
                pluck="for_value",
                ignore_permissions=True,
            )
            ds.extend(str(v) for v in (vals or []) if v)
    except Exception:
        _ghi_loi_frappe("quyen_don_vi: loi doc User Permission")

    return _chuan_hoa_ds_don_vi(ds)


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


def _ton_tai_trong_db(doctype: str | None, name: str | None) -> bool:
    if not doctype or not name:
        return False
    try:
        import frappe

        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "exists", None)):
            return bool(db.exists(doctype, name))
    except Exception:
        _ghi_loi_frappe("quyen_don_vi: loi kiem ton tai db")
    return False


def _doc_gia_tri_db(doctype: str | None, name: str | None, fieldname: str):
    if not doctype or not name:
        return None
    try:
        import frappe

        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "get_value", None)):
            return db.get_value(doctype, name, fieldname)
    except Exception:
        _ghi_loi_frappe("quyen_don_vi: loi doc gia tri db")
    return None


def _doc_don_vi_nguoi_tu_db(ten_nguoi: str | None) -> str | None:
    if not ten_nguoi:
        return None
    val = _doc_gia_tri_db("LX Nguoi", str(ten_nguoi).strip(), "don_vi")
    return str(val).strip() if val else None


def _doc_cu_tu_db(ten_dt: str | None, ten_doc: str | None, doc=None) -> dict | None:
    """Đọc bản ghi hiện có từ DB bằng frappe.db.get_value khi bản ghi đã tồn tại."""
    truoc = doc.get_doc_before_save() if callable(getattr(doc, "get_doc_before_save", None)) else None
    if ten_dt and ten_doc:
        don_vi_db = _doc_gia_tri_db(ten_dt, ten_doc, "don_vi")
        if ten_dt == "LX Co Hoi" and not don_vi_db:
            nguoi_db = _doc_gia_tri_db("LX Co Hoi", ten_doc, "nguoi")
            if nguoi_db:
                don_vi_db = _doc_don_vi_nguoi_tu_db(nguoi_db)
        if don_vi_db is not None and str(don_vi_db).strip():
            return {"don_vi": str(don_vi_db).strip()}
        if not _la_doc_moi(doc) and _ton_tai_trong_db(ten_dt, ten_doc):
            return {"don_vi": str(don_vi_db or "").strip()}
    if truoc is not None:
        dv_truoc = _lay_don_vi(truoc)
        if ten_dt == "LX Co Hoi" and not dv_truoc:
            nguoi_truoc = _lay_thuoc_tinh(truoc, "nguoi")
            if nguoi_truoc:
                dv_truoc = _doc_don_vi_nguoi_tu_db(nguoi_truoc) or ""
        return {"don_vi": dv_truoc}
    return None


def _tim_don_vi_nguoi(ten_dt: str | None, doc, doc_cu: dict | None) -> str | None:
    if ten_dt != "LX Co Hoi":
        return None
    nguoi_moi = _lay_thuoc_tinh(doc, "nguoi")
    if nguoi_moi:
        dv_nguoi = _doc_don_vi_nguoi_tu_db(nguoi_moi)
        return dv_nguoi if dv_nguoi else ""
    return None


def frappe_has_permission(doc, ptype=None, user=None, **kwargs):
    """Hook has_permission cho LX Nguoi và LX Co Hoi: giữ chặn cờ module N3 + kiểm quyền theo Đơn vị."""
    import frappe

    kq_module = _co_module_has_permission(doc, ptype=ptype, user=user, **kwargs)
    if kq_module is False:
        return False

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    mien = la_user_mien(nguoi_dung)
    if mien:
        return True

    ds_don_vi = lay_don_vi_cua_user(nguoi_dung)
    if not ds_don_vi:
        return False
    if doc is None or isinstance(doc, str):
        return bool(ds_don_vi)

    ten_dt = _lay_thuoc_tinh(doc, "doctype")
    ten_doc = _lay_thuoc_tinh(doc, "name")
    doc_cu = _doc_cu_tu_db(ten_dt, ten_doc, doc)
    don_vi_nguoi = _tim_don_vi_nguoi(ten_dt, doc, doc_cu)

    if ten_dt == "LX Co Hoi" and ten_doc and doc_cu is not None:
        nguoi_db = _doc_gia_tri_db("LX Co Hoi", ten_doc, "nguoi")
        if nguoi_db:
            dv_nguoi_db = _doc_don_vi_nguoi_tu_db(nguoi_db) or ""
            if not co_quyen({"don_vi": dv_nguoi_db}, ds_don_vi, mien):
                return False

    dv_moi = _lay_don_vi(doc)
    if ten_dt == "LX Co Hoi":
        if not dv_moi and doc_cu is None and don_vi_nguoi:
            dv_moi = don_vi_nguoi
            if not isinstance(doc, dict):
                try:
                    doc.don_vi = don_vi_nguoi
                except Exception:
                    pass
        if dv_moi and don_vi_nguoi and dv_moi != don_vi_nguoi:
            return False

    if doc_cu is not None and _lay_don_vi(doc_cu) and dv_moi and _lay_don_vi(doc_cu) != dv_moi:
        return False

    return kiem_ghi({"don_vi": dv_moi}, doc_cu, don_vi_nguoi, ds_don_vi, mien)


def kiem_tra_quyen_doc(doc, method=None) -> None:
    """Hook doc_events (before_insert, validate, before_save, on_trash) cho LX Nguoi và LX Co Hoi:
    xét bản ghi trong DB bằng kiem_ghi, chặn ghi/sửa/xoá trái đơn vị.
    """
    import frappe

    ten_dt = _lay_thuoc_tinh(doc, "doctype")
    ten_doc = _lay_thuoc_tinh(doc, "name")

    if ten_dt == "LX Co Hoi":
        nguoi = _lay_thuoc_tinh(doc, "nguoi")
        don_vi_hien_tai = _lay_don_vi(doc)
        if nguoi:
            don_vi_nguoi = _doc_don_vi_nguoi_tu_db(nguoi)
            if not don_vi_hien_tai and don_vi_nguoi:
                if isinstance(doc, dict):
                    doc["don_vi"] = don_vi_nguoi
                else:
                    doc.don_vi = don_vi_nguoi
                don_vi_hien_tai = don_vi_nguoi
            if don_vi_hien_tai and don_vi_nguoi and don_vi_hien_tai != don_vi_nguoi:
                frappe.throw(
                    "Đơn vị của Cơ hội phải khớp với Đơn vị của Người",
                    frappe.PermissionError,
                )

    if getattr(frappe, "session", None) is None:
        return
    if la_user_mien() or getattr(getattr(doc, "flags", None), "ignore_permissions", False):
        return

    ds_don_vi = lay_don_vi_cua_user()
    doc_cu = _doc_cu_tu_db(ten_dt, ten_doc, doc)
    don_vi_nguoi = _tim_don_vi_nguoi(ten_dt, doc, doc_cu)
    dv_moi = _lay_don_vi(doc)

    if ten_dt == "LX Co Hoi" and ten_doc and doc_cu is not None:
        nguoi_db = _doc_gia_tri_db("LX Co Hoi", ten_doc, "nguoi")
        if nguoi_db:
            dv_nguoi_db = _doc_don_vi_nguoi_tu_db(nguoi_db) or ""
            if not co_quyen({"don_vi": dv_nguoi_db}, ds_don_vi, False):
                frappe.throw("Không có quyền trên cơ hội của đơn vị khác", frappe.PermissionError)

    if not kiem_ghi({"don_vi": dv_moi}, doc_cu, don_vi_nguoi, ds_don_vi, False):
        frappe.throw("Không có quyền thao tác trên đơn vị này", frappe.PermissionError)

    if doc_cu is not None and _lay_don_vi(doc_cu) != dv_moi:
        frappe.throw("Không được phép đổi đơn vị của bản ghi", frappe.PermissionError)


def frappe_permission_query_conditions(user=None, doctype=None, **kwargs) -> str:
    """Hook permission_query_conditions cho LX Nguoi và LX Co Hoi: giữ chặn cờ module N3 + lọc theo Đơn vị."""
    import frappe

    dk_module = _co_module_query_conditions(user=user, doctype=doctype, **kwargs)
    if dk_module:
        return dk_module

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    ten_dt = doctype or "LX Nguoi"
    mien = la_user_mien(nguoi_dung)
    ds_don_vi = [] if mien else lay_don_vi_cua_user(nguoi_dung)
    return dieu_kien(ten_dt, ds_don_vi, mien)
