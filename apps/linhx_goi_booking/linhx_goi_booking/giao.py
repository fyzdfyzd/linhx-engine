"""Giao hàng cho gói đặt lịch (loai_giao == 'lich') qua luồng giao hàng chung của lõi (L3 / G3).

Thuần Python ở mức nạp file (không `import frappe` ở đầu file); chỉ giao tiếp với lõi qua `linhx_core.api`.
"""
from __future__ import annotations

import logging

from linhx_core.api import cap_quyen_dung, gia_hop_le
from linhx_goi_booking import dat_lich

logger = logging.getLogger(__name__)


def _lay_frappe():
    try:
        import frappe
    except ImportError:
        return None
    return frappe


def _co_db(frappe_mod) -> bool:
    if frappe_mod is None:
        return False
    try:
        return getattr(frappe_mod, "db", None) is not None
    except Exception:
        return False


def _cap_quyen_an_toan(don: dict, goi: dict, kho_quyen: list[dict] | None) -> dict:
    """Cấp quyền dùng cho đơn: chỉ dùng kho bộ nhớ khi người gọi truyền `kho_quyen`;
    khi `kho_quyen is None` bắt buộc gọi thẳng `cap_quyen_dung(don, goi)` và để lỗi nổi lên.
    """
    if kho_quyen is not None:
        kq = cap_quyen_dung(don, goi, kho=kho_quyen)
    else:
        kq = cap_quyen_dung(don, goi)
    if kq is None:
        raise ValueError("Không cấp được quyền dùng cho đơn đặt lịch")
    return kq


def _luu_lich_db_neu_co(
    frappe_mod,
    *,
    ma_don: str,
    nguoi: str,
    phu_trach: str,
    bat_dau: object,
    phut: object,
    ghi_chu: str,
    co_hoi: str = "",
    don_vi: str = "",
) -> dict:
    nguon_don = f"don:{ma_don}"
    db = getattr(frappe_mod, "db", None)
    get_all_fn = getattr(frappe_mod, "get_all", None)
    if callable(get_all_fn):
        try:
            da_co = get_all_fn(
                "LX Lich Goi",
                filters={"nguoi": nguoi, "nguon": nguon_don, "trang_thai": ["!=", "huy"]},
                fields=["name", "nguoi", "phu_trach", "bat_dau", "ket_thuc", "phut", "trang_thai", "ghi_chu", "co_hoi", "don_vi"],
                limit=1,
            )
            if da_co and isinstance(da_co[0], dict):
                return dict(da_co[0])
        except Exception as exc:
            logger.warning(
                "Lỗi kiểm tra lịch gọi đã giao của đơn %s: %s",
                ma_don,
                type(exc).__name__,
            )
            raise

    ds_hien_co: list[dict] = []
    if db is not None and callable(getattr(db, "sql", None)):
        try:
            rows = db.sql(
                """
                SELECT name, nguoi, phu_trach, bat_dau, ket_thuc, phut, trang_thai, ghi_chu, co_hoi, don_vi
                FROM `tabLX Lich Goi`
                WHERE phu_trach = %s AND trang_thai != 'huy'
                ORDER BY bat_dau ASC
                FOR UPDATE
                """,
                (phu_trach,),
                as_dict=True,
            )
            if isinstance(rows, (list, tuple)):
                ds_hien_co = [dict(r) for r in rows if isinstance(r, dict)]
        except Exception as exc:
            logger.warning(
                "Lỗi truy vấn FOR UPDATE lịch hiện có của %s khi giao đơn %s: %s",
                phu_trach,
                ma_don,
                type(exc).__name__,
            )
            raise
    elif callable(get_all_fn):
        try:
            rows = get_all_fn(
                "LX Lich Goi",
                filters={"phu_trach": phu_trach, "trang_thai": ["!=", "huy"]},
                fields=["name", "nguoi", "phu_trach", "bat_dau", "ket_thuc", "phut", "trang_thai", "ghi_chu", "co_hoi", "don_vi"],
                order_by="bat_dau asc",
            )
            if isinstance(rows, (list, tuple)):
                ds_hien_co = [dict(r) for r in rows if isinstance(r, dict)]
        except Exception as exc:
            logger.warning(
                "Lỗi get_all lịch hiện có của %s khi giao đơn %s: %s",
                phu_trach,
                ma_don,
                type(exc).__name__,
            )
            raise

    goi_dat: dict = {
        "nguoi": nguoi,
        "phu_trach": phu_trach,
        "bat_dau": bat_dau,
        "phut": phut,
        "ghi_chu": ghi_chu,
    }
    if co_hoi:
        goi_dat["co_hoi"] = co_hoi
    if don_vi:
        goi_dat["don_vi"] = don_vi

    ds_moi = dat_lich.dat_lich(ds_hien_co, goi_dat)
    ban_ghi = dict(ds_moi[-1])

    get_doc_fn = getattr(frappe_mod, "get_doc", None)
    if callable(get_doc_fn):
        du_lieu_doc: dict = {
            "doctype": "LX Lich Goi",
            "nguoi": ban_ghi["nguoi"],
            "phu_trach": ban_ghi["phu_trach"],
            "bat_dau": ban_ghi["bat_dau"],
            "ket_thuc": ban_ghi["ket_thuc"],
            "phut": ban_ghi["phut"],
            "trang_thai": ban_ghi["trang_thai"],
            "ghi_chu": ban_ghi.get("ghi_chu") or "",
            "nguon": nguon_don,
        }
        if co_hoi:
            du_lieu_doc["co_hoi"] = co_hoi
        if don_vi:
            du_lieu_doc["don_vi"] = don_vi
        doc = get_doc_fn(du_lieu_doc)
        doc._ds_lich_hien_co = ds_hien_co
        if hasattr(doc, "flags"):
            doc.flags.ignore_permissions = True
        doc.insert(ignore_permissions=True)
        if getattr(doc, "name", None):
            ban_ghi["name"] = str(doc.name)
    return ban_ghi


def giao(
    don: dict,
    goi: dict,
    *,
    ds_lich: list[dict] | None = None,
    kho_quyen: list[dict] | None = None,
) -> dict:
    """Hàm giao hàng của `linhx_goi_booking` cho `loai_giao == 'lich'`.

    - Kiểm tra đơn đã thanh toán (`trang_thai == 'da_tra'`) và đạt giá sàn của gói (`gia_hop_le`).
    - Cấp quyền dùng (`LX Quyen Dung`) qua `linhx_core.api.cap_quyen_dung`:
      khi `kho_quyen is None`, bắt buộc cấp quyền thật trên DB và để lỗi nổi lên (không tạo kho tạm giả).
    - Nếu đơn kèm thông tin đặt lịch (`nguoi`, `phu_trach`, `bat_dau`):
      + Khi có `ds_lich` hoặc có kết nối Frappe DB: kiểm giờ làm việc (8–18h giờ VN), kiểm trùng giờ
        qua `dat_lich.dat_lich`, lưu lịch và trả `trang_thai == 'da_dat_lich'`.
      + Khi chạy thuần Python không có Frappe DB và không truyền `ds_lich`: chỉ kiểm giờ làm việc
        trên danh sách rỗng (chưa có kho lịch để kiểm trùng giờ và lưu DB) và trả `trang_thai == 'tam_tinh_lich'`.
    """
    if not isinstance(don, dict):
        raise ValueError("don phải là dict")
    if not isinstance(goi, dict):
        raise ValueError("goi phải là dict")

    loai = str(goi.get("loai_giao") or don.get("loai_giao") or "lich").strip()
    if loai and loai != "lich":
        raise ValueError(f"Gói không thuộc loai_giao='lich': {loai!r}")

    if str(don.get("trang_thai") or "").strip() != "da_tra":
        raise ValueError("Chỉ giao lịch khi đơn ở trạng thái da_tra")

    if not gia_hop_le(don.get("so_tien"), goi):
        raise ValueError("Số tiền đơn chưa đạt giá sàn của gói")

    ma_don = str(don.get("name") or don.get("ma") or "").strip()
    if not ma_don:
        raise ValueError("Đơn thiếu định danh name/ma")
    ma_goi = str(goi.get("name") or goi.get("ma") or don.get("goi") or "").strip()
    nguoi = str(don.get("nguoi") or "").strip()

    don_chuan = dict(don)
    don_chuan.setdefault("name", ma_don)
    don_chuan.setdefault("ma", ma_don)
    if ma_goi:
        don_chuan.setdefault("goi", ma_goi)

    goi_chuan = dict(goi)
    if ma_goi:
        goi_chuan.setdefault("name", ma_goi)
        goi_chuan.setdefault("ma", ma_goi)

    quyen = _cap_quyen_an_toan(don_chuan, goi_chuan, kho_quyen)

    bat_dau = don.get("bat_dau")
    phu_trach = str(don.get("phu_trach") or goi.get("phu_trach") or "").strip()
    phut = don.get("phut", dat_lich.PHUT_MAC_DINH)
    ghi_chu = str(don.get("ghi_chu") or f"Giao lịch từ đơn {ma_don}").strip()
    co_hoi = str(don.get("co_hoi") or "").strip()
    don_vi = str(don.get("don_vi") or goi.get("don_vi") or "").strip()

    lich_tao: dict | None = None
    da_kiem_va_luu_lich = False
    if bat_dau is not None and str(bat_dau).strip():
        if not nguoi:
            raise ValueError("Đơn có bat_dau nhưng thiếu mã khách hàng (nguoi)")
        if not phu_trach:
            raise ValueError("Đơn có bat_dau nhưng thiếu người phụ trách (phu_trach)")

        if ds_lich is not None:
            goi_dat: dict = {
                "nguoi": nguoi,
                "phu_trach": phu_trach,
                "bat_dau": bat_dau,
                "phut": phut,
                "ghi_chu": ghi_chu,
            }
            if co_hoi:
                goi_dat["co_hoi"] = co_hoi
            if don_vi:
                goi_dat["don_vi"] = don_vi
            moi = dat_lich.dat_lich(ds_lich, goi_dat)
            ds_lich[:] = moi
            lich_tao = dict(moi[-1])
            da_kiem_va_luu_lich = True
        else:
            frappe_mod = _lay_frappe()
            if _co_db(frappe_mod):
                lich_tao = _luu_lich_db_neu_co(
                    frappe_mod,
                    ma_don=ma_don,
                    nguoi=nguoi,
                    phu_trach=phu_trach,
                    bat_dau=bat_dau,
                    phut=phut,
                    ghi_chu=ghi_chu,
                    co_hoi=co_hoi,
                    don_vi=don_vi,
                )
                da_kiem_va_luu_lich = True
            else:
                moi = dat_lich.dat_lich(
                    [],
                    {
                        "nguoi": nguoi,
                        "phu_trach": phu_trach,
                        "bat_dau": bat_dau,
                        "phut": phut,
                        "ghi_chu": ghi_chu,
                    },
                )
                lich_tao = dict(moi[-1])
                da_kiem_va_luu_lich = False

    if lich_tao is None:
        trang_thai = "san_sang_dat_lich"
    elif da_kiem_va_luu_lich:
        trang_thai = "da_dat_lich"
    else:
        trang_thai = "tam_tinh_lich"

    return {
        "ok": True,
        "loai_giao": "lich",
        "don": ma_don,
        "goi": ma_goi,
        "nguoi": nguoi,
        "trang_thai": trang_thai,
        "quyen_dung": quyen,
        "lich": lich_tao,
    }
