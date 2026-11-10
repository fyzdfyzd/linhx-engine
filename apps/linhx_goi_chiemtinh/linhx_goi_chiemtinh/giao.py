"""Giao báo cáo Chiêm Tinh Số (CTS) qua luồng giao hàng chung (loai_giao == 'bao_cao_cts').

Thuần Python ở mức nạp file (không `import frappe` ở đầu file); chỉ giao tiếp với lõi qua `linhx_core.api`
và tra cứu hàm của `linhx_cts` qua `tim_ham`.
"""
from __future__ import annotations

import importlib
import json
import math
from typing import Callable
import urllib.error
import urllib.request

try:
    from linhx_core.api import doc_cau_hinh, gia_hop_le, tim_ham
except ModuleNotFoundError:
    def doc_cau_hinh(khoa: str | None = None, mac_dinh: object = None, *, cau_hinh: dict | None = None) -> object:
        if isinstance(cau_hinh, dict):
            return cau_hinh if khoa is None else cau_hinh.get(khoa, mac_dinh)
        return {} if khoa is None else mac_dinh

    def gia_hop_le(so_tien: object, goi: dict) -> bool:
        if not isinstance(goi, dict) or so_tien is None or isinstance(so_tien, bool):
            return False
        try:
            tien = float(so_tien)
            gia_san = float(goi.get("gia_san", 0) or 0)
        except (TypeError, ValueError):
            return False
        return math.isfinite(tien) and math.isfinite(gia_san) and tien >= 0 and tien >= gia_san

    def tim_ham(loai: str, khoa: str = "", **_kwargs) -> list[str]:
        return []


TRUONG_SO_KHOP: tuple[str, ...] = ("ma_don", "so_tien", "goi", "trang_thai")

_ANH_XA_TRANG_THAI_CTS: dict[str, str] = {
    "da_thanh_toan": "da_tra",
    "paid": "da_tra",
    "cho_thanh_toan": "cho_tra",
    "pending": "cho_tra",
    "da_huy": "huy",
    "refunded": "da_hoan",
}


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


def _ghi_log_loi(frappe_mod, tieu_de: str) -> None:
    if frappe_mod is None:
        return
    log_error = getattr(frappe_mod, "log_error", None)
    if callable(log_error):
        try:
            log_error(title=tieu_de)
        except TypeError:
            try:
                log_error(tieu_de)
            except Exception:
                pass
        except Exception:
            pass


def _so_tien_hop_le(gia_tri: object) -> tuple[bool, int | None]:
    """Kiểm tra `so_tien` là số nguyên hợp lệ (không phải None, bool hay chuỗi). Không tự đoán hay lấp bằng giá."""
    if gia_tri is None or isinstance(gia_tri, bool):
        return False, None
    if isinstance(gia_tri, int):
        return True, gia_tri
    if isinstance(gia_tri, float):
        if math.isfinite(gia_tri) and gia_tri.is_integer():
            return True, int(gia_tri)
        return False, None
    return False, None


def _chuoi_hop_le(gia_tri: object) -> tuple[bool, str | None]:
    """Kiểm tra trường chuỗi bắt buộc (`ma_don`, `goi`, `trang_thai`) có mặt và khác rỗng."""
    if not isinstance(gia_tri, str):
        return False, None
    sach = gia_tri.strip()
    if not sach:
        return False, None
    return True, sach


def so_khop(don_engine: dict, don_cts: dict) -> list[str]:
    """So khớp đơn engine với đơn CTS, trả danh sách trường lệch trong `(ma_don, so_tien, goi, trang_thai)`.

    - Giữ đúng thứ tự `("ma_don", "so_tien", "goi", "trang_thai")`.
    - Trường thiếu ở một bên (hoặc cả hai bên), hoặc có giá trị `None`/rỗng đều tính là LỆCH.
    - Tuyệt đối không lấp `so_tien` bằng `gia`/`tong`/`gia_goc`, không đoán giá trị mặc định.
    """
    if not isinstance(don_engine, dict) or not isinstance(don_cts, dict):
        raise ValueError("don_engine và don_cts phải là dict")

    lech: list[str] = []
    for truong in TRUONG_SO_KHOP:
        if truong not in don_engine or truong not in don_cts:
            lech.append(truong)
            continue

        gt_eng = don_engine[truong]
        gt_cts = don_cts[truong]
        if gt_eng is None or gt_cts is None:
            lech.append(truong)
            continue

        if truong == "so_tien":
            ok_eng, tien_eng = _so_tien_hop_le(gt_eng)
            ok_cts, tien_cts = _so_tien_hop_le(gt_cts)
            if not ok_eng or not ok_cts or tien_eng != tien_cts:
                lech.append(truong)
        else:
            ok_eng, chu_eng = _chuoi_hop_le(gt_eng)
            ok_cts, chu_cts = _chuoi_hop_le(gt_cts)
            if not ok_eng or not ok_cts or chu_eng != chu_cts:
                lech.append(truong)

    return lech


def co_cts_that(cau_hinh: dict | None = None) -> bool:
    """Đọc cờ `cts_that` (mặc định tắt = False). Chỉ trả True khi cờ bật rõ ràng."""
    if isinstance(cau_hinh, dict) and "cts_that" in cau_hinh:
        gt = cau_hinh.get("cts_that")
        if isinstance(gt, bool):
            return gt
        if isinstance(gt, int):
            return gt == 1
        if isinstance(gt, str):
            return gt.strip().lower() in ("1", "true")
        return False

    frappe_mod = _lay_frappe()
    if _co_db(frappe_mod):
        db = getattr(frappe_mod, "db", None)
        try:
            if callable(getattr(db, "get_single_value", None)):
                val = db.get_single_value("LX Cau Hinh", "cts_that")
                if val is not None:
                    if isinstance(val, bool):
                        return val
                    if isinstance(val, int):
                        return val == 1
                    if isinstance(val, str):
                        return val.strip().lower() in ("1", "true")
        except Exception:
            _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh.co_cts_that.db")

    try:
        gt_api = doc_cau_hinh("cts_that", False, cau_hinh=cau_hinh if isinstance(cau_hinh, dict) else None)
        if isinstance(gt_api, bool):
            return gt_api
        if isinstance(gt_api, int):
            return gt_api == 1
        if isinstance(gt_api, str):
            return gt_api.strip().lower() in ("1", "true")
    except Exception:
        _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh.co_cts_that.doc_cau_hinh")
    return False


def _doc_cau_hinh_ket_noi_cts(cau_hinh: dict | None = None) -> dict[str, str]:
    """Đọc URL và khoá gọi API báo cáo CTS từ cấu hình site qua `linhx_cts` (không viết cứng URL hay khoá).

    Chỉ đọc khoá riêng của API báo cáo (`cts_api_khoa` / `cts_bao_cao_khoa`), tuyệt đối không
    dùng khoá SePay (`sepay_khoa`) của cổng thanh toán.
    """
    nguon: dict = {}
    frappe_mod = _lay_frappe()
    if frappe_mod is not None:
        try:
            conf = getattr(frappe_mod, "conf", None) or {}
            if isinstance(conf, dict):
                nguon.update(conf)
        except Exception:
            _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh._doc_cau_hinh_ket_noi_cts.conf")
    if isinstance(cau_hinh, dict):
        nguon.update(cau_hinh)

    url_host = ""
    try:
        ds_ham = tim_ham("cung_cap", "cts.tao_don")
        if ds_ham:
            ten_mod = ds_ham[0].rsplit(".", 1)[0]
            mod_hd = importlib.import_module(ten_mod)
            doc_ch = getattr(mod_hd, "doc_cau_hinh_cts", None)
            if callable(doc_ch):
                trich = doc_ch(nguon)
                url_host = str(trich.get("host") or "").strip().rstrip("/")
    except Exception:
        _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh._doc_cau_hinh_ket_noi_cts.host")

    url_bao_cao = str(
        nguon.get("cts_bao_cao_url")
        or nguon.get("cts_api_url")
        or (f"{url_host}/v1/reports/deliver" if url_host else "")
        or ""
    ).strip()
    khoa = str(
        nguon.get("cts_api_khoa")
        or nguon.get("cts_bao_cao_khoa")
        or ""
    ).strip()
    return {"url": url_bao_cao, "khoa": khoa}


def _chuan_don_cts(don_cts: dict) -> dict:
    """Chuẩn hoá bản ghi `LX Don CTS` từ DB (nếu ở dạng `order_id`/`sku`/`da_nhan`) về 4 trường chuẩn của `so_khop`.

    Chỉ lấy `so_tien` từ `so_tien` hoặc `da_nhan` (tiền thực nhận), tuyệt đối không lấy từ `gia`/`gia_goc`/`tong`.
    """
    ket_qua: dict = {}
    if "ma_don" in don_cts:
        ket_qua["ma_don"] = don_cts["ma_don"]
    elif "order_id" in don_cts:
        ket_qua["ma_don"] = don_cts["order_id"]

    if "so_tien" in don_cts:
        ket_qua["so_tien"] = don_cts["so_tien"]
    elif "da_nhan" in don_cts:
        ket_qua["so_tien"] = don_cts["da_nhan"]

    if "goi" in don_cts:
        ket_qua["goi"] = don_cts["goi"]
    elif "sku" in don_cts:
        ket_qua["goi"] = don_cts["sku"]

    if "trang_thai" in don_cts:
        tt = don_cts["trang_thai"]
        if isinstance(tt, str) and ("order_id" in don_cts or "sku" in don_cts or "da_nhan" in don_cts):
            ket_qua["trang_thai"] = _ANH_XA_TRANG_THAI_CTS.get(tt.strip(), tt.strip())
        else:
            ket_qua["trang_thai"] = tt

    return ket_qua


def _tim_don_cts_db(don_engine: dict) -> dict | None:
    """Tìm bản ghi `LX Don CTS` tương ứng trên Frappe DB theo `ma_don`/`order_id` hoặc `noi_dung_ck`."""
    frappe_mod = _lay_frappe()
    if not _co_db(frappe_mod):
        return None
    db = frappe_mod.db
    try:
        if callable(getattr(db, "table_exists", None)) and not db.table_exists("LX Don CTS"):
            return None
    except Exception:
        _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh._tim_don_cts_db.table_exists")
        return None

    ma_don = str(
        don_engine.get("ma_don")
        or don_engine.get("ma")
        or don_engine.get("name")
        or ""
    ).strip()
    noi_dung_ck = str(don_engine.get("noi_dung_ck") or "").strip()

    fields = ["name", "order_id", "noi_dung_ck", "sku", "da_nhan", "trang_thai"]
    if ma_don and callable(getattr(frappe_mod, "get_all", None)):
        rows = frappe_mod.get_all(
            "LX Don CTS",
            filters={"order_id": ma_don},
            fields=fields,
            limit=1,
            ignore_permissions=True,
        )
        if rows and isinstance(rows[0], dict):
            return dict(rows[0])
    if noi_dung_ck and callable(getattr(frappe_mod, "get_all", None)):
        rows = frappe_mod.get_all(
            "LX Don CTS",
            filters={"noi_dung_ck": noi_dung_ck},
            fields=fields,
            limit=1,
            ignore_permissions=True,
        )
        if rows and isinstance(rows[0], dict):
            return dict(rows[0])
    return None


def _goi_api_bao_cao_cts(
    url: str,
    khoa: str,
    payload: dict,
    goi_api: Callable[[str, dict, dict], dict] | None = None,
) -> dict:
    """Gọi HTTP POST tới API báo cáo CTS từ URL và khoá trong cấu hình."""
    url_sach = str(url or "").strip()
    khoa_sach = str(khoa or "").strip()
    if not url_sach:
        raise ValueError("Thiếu cấu hình URL API báo cáo CTS (cts_bao_cao_url / cts_host)")
    if not khoa_sach:
        raise ValueError("Thiếu cấu hình khoá API báo cáo CTS (cts_api_khoa / cts_bao_cao_khoa)")

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Apikey {khoa_sach}",
    }
    if callable(goi_api):
        phan_hoi = goi_api(url_sach, payload, headers)
    else:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url_sach, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                status_code = getattr(resp, "status", None) or resp.getcode()
                raw = resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"API báo cáo CTS trả mã lỗi HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Lỗi kết nối API báo cáo CTS: {exc.reason}") from exc

        if status_code is not None and not (200 <= int(status_code) < 300):
            raise RuntimeError(f"API báo cáo CTS trả mã ngoài 2xx: {status_code}")

        if not raw or not raw.strip():
            raise RuntimeError("API báo cáo CTS trả phản hồi rỗng")
        try:
            phan_hoi = json.loads(raw)
        except ValueError as exc:
            raise RuntimeError("API báo cáo CTS trả JSON không hợp lệ") from exc

    if not isinstance(phan_hoi, dict):
        raise RuntimeError("Phản hồi API báo cáo CTS phải là dict JSON")
    if phan_hoi.get("ok") is False or phan_hoi.get("delivered") is False or phan_hoi.get("error"):
        raise RuntimeError(f"API báo cáo CTS báo lỗi giao hàng: {phan_hoi.get('error') or phan_hoi}")
    status_ph = phan_hoi.get("status")
    if isinstance(status_ph, int) and not (200 <= status_ph < 300):
        raise RuntimeError(f"API báo cáo CTS trả status không thành công: {status_ph}")
    return phan_hoi


def giao(
    don: dict,
    goi: dict | None = None,
    *,
    cau_hinh: dict | None = None,
    don_cts: dict | None = None,
    goi_api: Callable[[str, dict, dict], dict] | None = None,
    kho_doi_chieu: list[dict] | None = None,
) -> dict:
    """Giao báo cáo CTS cho `loai_giao == 'bao_cao_cts'`.

    - Khi cờ `cts_that` tắt (mặc định): chỉ đối chiếu đơn engine với đơn CTS và ghi kết quả đối chiếu,
      không gọi giao thật cho khách (`da_giao_khach = False`).
    - Khi cờ `cts_that` bật: đối chiếu không lệch thì gọi API báo cáo CTS theo URL và khoá từ cấu hình.
    - Không bao giờ tự lấp `so_tien` của đơn bằng `gia` của gói.
    """
    if not isinstance(don, dict):
        raise ValueError("don phải là dict")
    goi_dict = dict(goi) if isinstance(goi, dict) else {}

    if str(don.get("trang_thai") or "").strip() != "da_tra":
        raise ValueError("Chỉ giao báo cáo CTS khi đơn ở trạng thái da_tra")

    if goi_dict and ("gia_san" in goi_dict or "gia" in goi_dict):
        if "so_tien" in don and don.get("so_tien") is not None:
            if not gia_hop_le(don.get("so_tien"), goi_dict):
                raise ValueError("Số tiền đơn chưa đạt giá sàn của gói")

    don_engine_so: dict = {}
    ma_don_raw = don.get("ma_don") if "ma_don" in don else (don.get("ma") if "ma" in don else don.get("name"))
    if ma_don_raw is not None:
        don_engine_so["ma_don"] = ma_don_raw
    if "so_tien" in don:
        don_engine_so["so_tien"] = don["so_tien"]
    if "goi" in don and don["goi"] is not None:
        don_engine_so["goi"] = don["goi"]
    elif goi_dict.get("ma") or goi_dict.get("name"):
        don_engine_so["goi"] = goi_dict.get("ma") or goi_dict.get("name")
    if "trang_thai" in don:
        don_engine_so["trang_thai"] = don["trang_thai"]

    ban_cts = don_cts if isinstance(don_cts, dict) else _tim_don_cts_db(don)
    if isinstance(ban_cts, dict):
        truong_lech = so_khop(don_engine_so, _chuan_don_cts(ban_cts))
    else:
        truong_lech = list(TRUONG_SO_KHOP)

    bat_that = co_cts_that(cau_hinh)
    ok_tien, tien_int = _so_tien_hop_le(don.get("so_tien") if "so_tien" in don else None)
    ma_don_str = str(don_engine_so.get("ma_don") or "").strip()
    ma_goi_str = str(don_engine_so.get("goi") or "").strip()

    ket_qua: dict = {
        "ok": len(truong_lech) == 0,
        "loai_giao": "bao_cao_cts",
        "ma_don": ma_don_str,
        "goi": ma_goi_str,
        "so_tien": tien_int if ok_tien else None,
        "trang_thai": str(don.get("trang_thai") or "").strip(),
        "lech": truong_lech,
        "co_cts_that": bat_that,
        "da_giao_khach": False,
    }

    if isinstance(kho_doi_chieu, list):
        kho_doi_chieu.append(dict(ket_qua))

    if not bat_that:
        return ket_qua

    if truong_lech:
        raise ValueError(f"Đơn {ma_don_str} lệch với CTS ở các trường: {', '.join(truong_lech)}")

    ket_noi = _doc_cau_hinh_ket_noi_cts(cau_hinh)
    phan_hoi = _goi_api_bao_cao_cts(
        ket_noi["url"],
        ket_noi["khoa"],
        {
            "ma_don": ma_don_str,
            "goi": ma_goi_str,
            "so_tien": ket_qua["so_tien"],
            "trang_thai": ket_qua["trang_thai"],
        },
        goi_api=goi_api,
    )
    ket_qua["da_giao_khach"] = True
    ket_qua["phan_hoi_cts"] = phan_hoi
    return ket_qua


def dam_bao_loai_giao_bao_cao_cts() -> list[str]:
    """Đảm bảo tuỳ chọn `bao_cao_cts` có trên trường `loai_giao` của `LX Goi` khi cài hoặc migrate app."""
    frappe_mod = _lay_frappe()
    if not _co_db(frappe_mod):
        return []
    da_cap_nhat: list[str] = []
    try:
        meta = frappe_mod.get_meta("LX Goi")
        df = meta.get_field("loai_giao") if meta else None
        if df is not None:
            opts = [x.strip() for x in str(df.options or "").split("\n") if x.strip()]
            if "bao_cao_cts" not in opts:
                opts.append("bao_cao_cts")
                frappe_mod.make_property_setter(
                    {
                        "doctype": "LX Goi",
                        "fieldname": "loai_giao",
                        "property": "options",
                        "value": "\n".join(opts),
                        "property_type": "Text",
                    }
                )
                da_cap_nhat.append("PropertySetter:LX Goi.loai_giao")
    except Exception:
        _ghi_log_loi(frappe_mod, "linhx_goi_chiemtinh.dam_bao_loai_giao_bao_cao_cts")
    return da_cap_nhat
