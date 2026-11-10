"""Mặt cắt công khai (Python facade) của `linhx_core` dành cho các app lớp `adapter` và `goi`.

Luật kiến trúc ba lớp (Đợt 3):
- Lõi (`linhx_core`, `linhx_worker`) không import `adapter` hay `goi`.
- `adapter` và `goi` chỉ import từ lõi qua `linhx_core.api` (không import trực tiếp module nội bộ).
- Module này thuần Python ở mức nạp file (không `import frappe` ở đầu file; không gắn `@frappe.whitelist`
  để tránh mở mặt cắt nội bộ thành HTTP endpoint công khai). Phần cần Frappe được nạp trễ bên trong hàm.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import pathlib
import re
import secrets
from urllib.parse import urlencode

from linhx_core import co_module, dang_ky_module
from linhx_core.crm import dong_y as _dong_y
from linhx_core.crm import gop_trung as _gop_trung
from linhx_core.pay import quyen_dung as _quyen_dung

API_CONG_KHAI: list[str] = [
    "phat",
    "tim_ham",
    "tao_nguoi",
    "ghi_dong_y",
    "tao_don",
    "danh_dau_da_tra",
    "cap_quyen_dung",
    "doc_cau_hinh",
    "gia_hop_le",
    "module_bat",
    "doctype_bi_an",
    "khoa_gop",
    "gop_nguoi",
    "chuan_hoa_dien_thoai",
    "chuan_hoa_email",
    "chuan_hoa_zalo",
    "hieu_luc_dong_y",
]

__all__ = list(API_CONG_KHAI)

_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[2]

_CO_MAC_DINH: dict[str, int] = {
    "bat_crm": 0,
    "bat_pay": 0,
    "bat_bong": 0,
}

_KHOA_CAM_CAU_HINH: frozenset[str] = frozenset(
    {
        "db_password",
        "root_password",
        "admin_password",
        "mail_password",
        "encryption_key",
        "secret_key",
        "api_secret",
        "jwt_secret",
    }
)

_TRUONG_NGUOI: tuple[str, ...] = (
    "ho_ten",
    "dien_thoai",
    "email",
    "zalo",
    "don_vi",
    "to_chuc",
    "nguon",
    "tang_pheu",
    "t1_tong",
    "t1_muc",
    "lich_su_t1",
    "ghi_cong",
)

_GIOI_HAN_TRUONG_DON: tuple[tuple[str, int], ...] = (
    ("brand", 80),
    ("email", 120),
    ("nganh", 80),
    ("thi_truong", 60),
    ("doi_thu", 120),
    ("su_that", 600),
)


def _lay_frappe():
    """Nạp trễ module `frappe` khi có mặt trong môi trường chạy; trả `None` nếu không có."""
    try:
        import frappe
    except ImportError:
        return None
    return frappe


def _frappe_co_db(frappe_mod=None) -> bool:
    """Kiểm tra môi trường hiện tại có kết nối Frappe DB (hoặc mock Frappe trong kiểm thử) hay không."""
    mod = frappe_mod if frappe_mod is not None else _lay_frappe()
    if mod is None:
        return False
    try:
        if getattr(mod, "db", None) is not None:
            return True
    except Exception:
        return False
    return getattr(mod, "__file__", None) is None and callable(getattr(mod, "get_doc", None))


def _ma_nguoi_tu_tham_so(nguoi: object) -> str:
    if isinstance(nguoi, dict):
        return str(nguoi.get("name") or nguoi.get("nguoi") or "").strip()
    return str(nguoi or "").strip()


def _sinh_noi_dung_ck(ma_don: str) -> str:
    """Sinh nội dung chuyển khoản chuẩn `LX[A-Z0-9]{4,23}` từ `ma_don`."""
    raw = str(ma_don or "").strip()
    if not raw:
        raise ValueError("ma_don không được để trống")
    sach = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if not sach:
        raise ValueError("ma_don phải chứa ít nhất một chữ cái hoặc chữ số")
    bam_phu = hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
    if raw != sach or len(sach) > 23:
        than = f"{sach[:15]}{bam_phu[:8]}"
    elif len(sach) < 4:
        than = f"{sach}{bam_phu[:8]}"
    else:
        than = sach
    return f"LX{than}"


def _sinh_qr_vietqr(so_tien: int, noi_dung: str, ngan_hang: dict) -> str:
    """Sinh URL ảnh VietQR khi caller truyền cấu hình ngân hàng hợp lệ."""
    ma_bin = str(ngan_hang.get("bin") or "").strip()
    so_tk = str(ngan_hang.get("so_tk") or "").strip()
    ten_tk = str(ngan_hang.get("ten_tk") or "").strip()
    mau = str(ngan_hang.get("mau") or "compact2").strip()
    if not ma_bin or not so_tk:
        raise ValueError("Thiếu thông tin bin hoặc so_tk trong cấu hình ngân hàng")
    tham_so = urlencode(
        {
            "amount": str(so_tien),
            "addInfo": str(noi_dung or "").strip(),
            "accountName": ten_tk,
        }
    )
    return f"https://img.vietqr.io/image/{ma_bin}-{so_tk}-{mau}.png?{tham_so}"


def gia_hop_le(so_tien: object, goi: dict) -> bool:
    """Kiểm tra `so_tien` hợp lệ và đạt giá sàn (`gia_san`) của gói."""
    return _quyen_dung.gia_hop_le(so_tien, goi)


def module_bat(ten_module: str, cau_hinh: dict | None = None) -> bool:
    """Kiểm tra module có đang bật trong `cau_hinh` (hoặc cấu hình site hiện hành) hay không."""
    ch = cau_hinh if isinstance(cau_hinh, dict) else doc_cau_hinh()
    return co_module.module_bat(ten_module, ch if isinstance(ch, dict) else {})


def doctype_bi_an(ten_doctype: str, cau_hinh: dict | None = None) -> bool:
    """Trả `True` nếu `ten_doctype` thuộc module có cờ đang tắt."""
    ch = cau_hinh if isinstance(cau_hinh, dict) else doc_cau_hinh()
    return co_module.doctype_bi_an(ten_doctype, ch if isinstance(ch, dict) else {})


def khoa_gop(nguoi: dict) -> set[str]:
    """Trả tập hợp khoá chuẩn hoá (`dt:84...`, `email:...`, `zalo:...`) của hồ sơ Người."""
    return _gop_trung.khoa_gop(nguoi)


def gop_nguoi(danh_sach: list[dict], moi: dict) -> list[dict]:
    """Gộp bản ghi Người `moi` vào `danh_sach` theo khoá liên hệ chuẩn hoá (giữ trường cũ, bù trường trống)."""
    return _gop_trung.gop(danh_sach, moi)


def chuan_hoa_dien_thoai(dien_thoai: object) -> str:
    """Chuẩn hoá số điện thoại Việt Nam về dạng `84...`."""
    return _gop_trung.chuan_hoa_dien_thoai(dien_thoai)


def chuan_hoa_email(email: object) -> str:
    """Chuẩn hoá địa chỉ email chữ thường."""
    return _gop_trung.chuan_hoa_email(email)


def chuan_hoa_zalo(zalo: object) -> str:
    """Chuẩn hoá định danh Zalo."""
    return _gop_trung.chuan_hoa_zalo(zalo)


def hieu_luc_dong_y(so: list[dict], nguoi: str | dict, muc_dich: str) -> bool:
    """Kiểm tra đồng ý của `nguoi` cho `muc_dich` có đang hiệu lực trên sổ `so` hay không."""
    return _dong_y.hieu_luc(so, nguoi, muc_dich)


def tim_ham(
    loai: str | list[dict],
    khoa: str | None = None,
    danh_sach: list[dict] | None = None,
    *,
    thu_muc_apps: str | pathlib.Path | None = None,
    ban_loi: str | None = None,
) -> list[str]:
    """Tra danh sách đường hàm `module.ham` theo `loai` (`nghe` | `cung_cap` | `giao`) và `khoa`.

    Hỗ trợ cả hai cách gọi:
    - `tim_ham(loai, khoa, danh_sach=None)`: tự động quét `apps/*/module.json` khi `danh_sach` để trống.
    - `tim_ham(danh_sach, loai, khoa)`: tương thích trực tiếp chữ ký `dang_ky_module.tim_ham`.
    """
    if isinstance(loai, list) and isinstance(khoa, str) and isinstance(danh_sach, str):
        ds_dung = loai
        loai_dung = khoa
        khoa_dung = danh_sach
    elif isinstance(loai, str):
        loai_dung = loai
        khoa_dung = "" if khoa is None else khoa
        if danh_sach is not None:
            ds_dung = danh_sach
        else:
            goc_apps = pathlib.Path(thu_muc_apps) if thu_muc_apps is not None else _THU_MUC_APPS
            ds_dung = dang_ky_module.quet(goc_apps, ban_loi=ban_loi)
    else:
        raise ValueError("Tham số gọi tim_ham không hợp lệ")
    return dang_ky_module.tim_ham(ds_dung, loai_dung, khoa_dung)


def phat(
    ten: str,
    du_lieu: dict | None = None,
    kho: list[dict] | None = None,
) -> dict:
    """Phát sự kiện qua outbox của lõi (`su_kien` / DocType `LX Su Kien`)."""
    if not isinstance(ten, str) or not ten.strip():
        raise ValueError("Tên sự kiện không được để trống")
    ten_sach = ten.strip()
    if du_lieu is None:
        dl: dict = {}
    elif isinstance(du_lieu, dict):
        dl = copy.deepcopy(du_lieu)
    else:
        raise ValueError("du_lieu sự kiện phải là dict")

    try:
        from linhx_core import su_kien as _su_kien
    except ImportError:
        _su_kien = None

    if kho is not None:
        if not isinstance(kho, list):
            raise ValueError("kho sự kiện phải là list")
        if _su_kien is not None and callable(getattr(_su_kien, "phat", None)):
            return _su_kien.phat(ten_sach, dl, kho)
        ban_ghi = {
            "ten": ten_sach,
            "du_lieu": dl,
            "trang_thai": "cho",
            "lan": 0,
            "da_giao": [],
            "loi": "",
        }
        kho.append(ban_ghi)
        return ban_ghi

    if _su_kien is not None:
        for ten_ham_db in ("phat_frappe", "phat_db"):
            ham_db = getattr(_su_kien, ten_ham_db, None)
            if callable(ham_db):
                return ham_db(ten_sach, dl)
        ham_phat = getattr(_su_kien, "phat", None)
        if callable(ham_phat):
            try:
                tham_so = list(inspect.signature(ham_phat).parameters.values())
                if len(tham_so) >= 3 and tham_so[2].default is not inspect.Parameter.empty:
                    return ham_phat(ten_sach, dl)
            except (TypeError, ValueError):
                pass

    frappe = _lay_frappe()
    if not _frappe_co_db(frappe):
        raise RuntimeError("Cần truyền kho (list) hoặc chạy trong môi trường Frappe có kết nối DB")

    doc = frappe.get_doc(
        {
            "doctype": "LX Su Kien",
            "ten": ten_sach,
            "du_lieu": json.dumps(dl, ensure_ascii=False),
            "trang_thai": "cho",
            "lan": 0,
            "da_giao": json.dumps([], ensure_ascii=False),
            "loi": "",
        }
    )
    doc.insert(ignore_permissions=True)
    return {
        "name": getattr(doc, "name", None),
        "ten": ten_sach,
        "du_lieu": dl,
        "trang_thai": "cho",
        "lan": 0,
        "da_giao": [],
        "loi": "",
    }


def _chuan_du_lieu_nguoi(du_lieu: dict) -> dict:
    if not isinstance(du_lieu, dict):
        raise ValueError("du_lieu Người phải là dict")
    sach: dict = {}
    for truong in _TRUONG_NGUOI:
        if truong not in du_lieu or du_lieu[truong] is None:
            continue
        gt = du_lieu[truong]
        if truong == "email":
            em = _gop_trung.chuan_hoa_email(gt)
            if em:
                sach["email"] = em
        elif truong == "zalo":
            zl = _gop_trung.chuan_hoa_zalo(gt)
            if zl:
                sach["zalo"] = zl
        elif isinstance(gt, str):
            gt_s = gt.strip()
            if gt_s:
                sach[truong] = gt_s
        else:
            sach[truong] = copy.deepcopy(gt)

    if isinstance(du_lieu.get("name"), str) and du_lieu["name"].strip():
        sach["name"] = du_lieu["name"].strip()

    co_dinh_danh = any(
        bool(str(sach.get(k) or "").strip())
        for k in ("ho_ten", "dien_thoai", "email", "zalo")
    )
    if not co_dinh_danh:
        raise ValueError("Cần ít nhất họ tên hoặc kênh liên hệ (điện thoại, email, Zalo)")
    return sach


def _khop_cung_pham_vi_don_vi(cu: dict, moi: dict) -> bool:
    dv_moi = str(moi.get("don_vi") or "").strip()
    dv_cu = str(cu.get("don_vi") or "").strip()
    if dv_moi:
        return dv_cu == dv_moi
    return True


def _doc_nguoi_sang_dict(doc) -> dict:
    kq: dict = {"name": str(getattr(doc, "name", "") or "").strip()}
    for truong in _TRUONG_NGUOI:
        gt = getattr(doc, truong, None)
        if gt is not None:
            kq[truong] = gt
    return kq


def _tim_nguoi_trung_frappe(frappe_mod, ban_moi: dict) -> list[dict]:
    khoa_moi = _gop_trung.khoa_gop(ban_moi)
    if not khoa_moi or not callable(getattr(frappe_mod, "get_all", None)):
        return []
    or_filters: list = []
    dt_raw = str(ban_moi.get("dien_thoai") or "").strip()
    dt_chuan = _gop_trung.chuan_hoa_dien_thoai(dt_raw)
    if dt_chuan:
        cac_dt = {dt_chuan, f"+{dt_chuan}"}
        if dt_raw:
            cac_dt.add(dt_raw)
        if dt_chuan.startswith("84") and len(dt_chuan) > 2:
            cac_dt.add("0" + dt_chuan[2:])
        or_filters.append(["LX Nguoi", "dien_thoai", "in", sorted(cac_dt)])
    em = str(ban_moi.get("email") or "").strip()
    if em:
        or_filters.append(["LX Nguoi", "email", "in", [em]])
    zl = str(ban_moi.get("zalo") or "").strip()
    if zl:
        or_filters.append(["LX Nguoi", "zalo", "in", [zl]])
    if not or_filters:
        return []

    dv_moi = str(ban_moi.get("don_vi") or "").strip()
    bo_loc = {"don_vi": dv_moi} if dv_moi else None
    ds_ung_vien = frappe_mod.get_all(
        "LX Nguoi",
        filters=bo_loc,
        or_filters=or_filters,
        fields=["name", *_TRUONG_NGUOI],
        order_by="creation asc",
        limit=20,
    )
    ket_qua: list[dict] = []
    for item in ds_ung_vien or []:
        if isinstance(item, dict) and (_gop_trung.khoa_gop(item) & khoa_moi) and _khop_cung_pham_vi_don_vi(item, ban_moi):
            ket_qua.append(dict(item))
    return ket_qua


def tao_nguoi(
    du_lieu: dict,
    kho: list[dict] | None = None,
    *,
    ds_nguoi: list[dict] | None = None,
    ignore_permissions: bool = True,
) -> dict:
    """Tạo hoặc gộp trùng hồ sơ `LX Nguoi` (giữ nguyên trường cũ đã có, chỉ bù trường còn trống)."""
    ban_moi = _chuan_du_lieu_nguoi(du_lieu)
    kho_dung = kho if kho is not None else ds_nguoi

    if kho_dung is not None:
        if not isinstance(kho_dung, list):
            raise ValueError("kho Người phải là list")
        khoa_moi = _gop_trung.khoa_gop(ban_moi)
        ban_sao = [dict(x) for x in kho_dung if isinstance(x, dict)]
        if khoa_moi:
            for cu in ban_sao:
                if (_gop_trung.khoa_gop(cu) & khoa_moi) and _khop_cung_pham_vi_don_vi(cu, ban_moi):
                    for k, v in ban_moi.items():
                        if k == "name":
                            continue
                        if _gop_trung._la_trong(cu.get(k)) and not _gop_trung._la_trong(v):
                            cu[k] = v
                    if not cu.get("name"):
                        cu["name"] = ban_moi.get("name") or f"NGUOI-{len(ban_sao)}"
                    kho_dung[:] = ban_sao
                    return dict(cu)
        muc_moi = dict(ban_moi)
        if not muc_moi.get("name"):
            muc_moi["name"] = f"NGUOI-{len(ban_sao) + 1}"
        ban_sao.append(muc_moi)
        kho_dung[:] = ban_sao
        return dict(muc_moi)

    frappe = _lay_frappe()
    if not _frappe_co_db(frappe):
        muc_le = dict(ban_moi)
        muc_le.setdefault("name", "NGUOI-1")
        return muc_le

    ds_trung = _tim_nguoi_trung_frappe(frappe, ban_moi)
    if ds_trung and ds_trung[0].get("name"):
        ten_cu = str(ds_trung[0]["name"]).strip()
        doc_cu = frappe.get_doc("LX Nguoi", ten_cu)
        co_cap_nhat = False
        for truong in _TRUONG_NGUOI:
            if truong == "don_vi" or truong not in ban_moi:
                continue
            gt_cu = getattr(doc_cu, truong, None)
            gt_moi = ban_moi[truong]
            if _gop_trung._la_trong(gt_cu) and not _gop_trung._la_trong(gt_moi):
                if isinstance(gt_moi, (dict, list)):
                    gt_moi = json.dumps(gt_moi, ensure_ascii=False)
                setattr(doc_cu, truong, gt_moi)
                co_cap_nhat = True
        if co_cap_nhat:
            if ignore_permissions and hasattr(doc_cu, "flags"):
                doc_cu.flags.ignore_permissions = True
            doc_cu.save(ignore_permissions=ignore_permissions)
        return _doc_nguoi_sang_dict(doc_cu)

    du_lieu_doc: dict = {"doctype": "LX Nguoi"}
    for truong in _TRUONG_NGUOI:
        if truong in ban_moi:
            gt = ban_moi[truong]
            if isinstance(gt, (dict, list)):
                gt = json.dumps(gt, ensure_ascii=False)
            du_lieu_doc[truong] = gt

    doc_moi = frappe.get_doc(du_lieu_doc)
    if ignore_permissions and hasattr(doc_moi, "flags"):
        doc_moi.flags.ignore_permissions = True
    dup_cls = getattr(frappe, "DuplicateEntryError", None)
    loai_trung = (dup_cls,) if isinstance(dup_cls, type) and issubclass(dup_cls, Exception) else ()
    try:
        doc_moi.insert(ignore_permissions=ignore_permissions)
        return _doc_nguoi_sang_dict(doc_moi)
    except loai_trung:
        ds_lai = _tim_nguoi_trung_frappe(frappe, ban_moi)
        if ds_lai and ds_lai[0].get("name"):
            return dict(ds_lai[0])
        raise


_CHUA_TRUYEN = object()


def ghi_dong_y(
    nguoi: str | dict | list[dict],
    muc_dich: str | dict | None = None,
    dong_y: object = True,
    luc: object = None,
    nguon: object = _CHUA_TRUYEN,
    nguon_khi_truyen_so: str | None = None,
    *,
    trang_thai: str | None = None,
    kho: list[dict] | None = None,
    so_dong_y: list[dict] | None = None,
) -> dict:
    """Ghi một dòng nhật ký đồng ý dữ liệu cá nhân (`LX Dong Y`) bất biến.

    Hỗ trợ cả hai dạng gọi:
    - `ghi_dong_y(nguoi, muc_dich, dong_y=True, luc=None, nguon="api", trang_thai=None, kho=None)`
    - `ghi_dong_y(so, nguoi, muc_dich, dong_y=True, luc=None, nguon="api", trang_thai=None)`
    """
    if isinstance(nguoi, list):
        so_muc_tieu: list[dict] | None = nguoi
        nguoi_dung = muc_dich
        muc_dich_dung = str(dong_y or "").strip()
        dong_y_dung: object = True if luc is None else luc
        if nguon is _CHUA_TRUYEN:
            luc_dung: object = None
            nguon_dung: object = "api" if nguon_khi_truyen_so is None else nguon_khi_truyen_so
        else:
            luc_dung = nguon
            nguon_dung = "api" if nguon_khi_truyen_so is None else nguon_khi_truyen_so
    else:
        so_muc_tieu = kho if kho is not None else so_dong_y
        nguoi_dung = nguoi
        muc_dich_dung = str(muc_dich or "").strip()
        dong_y_dung = dong_y
        luc_dung = luc
        nguon_dung = "api" if nguon is _CHUA_TRUYEN else nguon

    thoi_diem = str(luc_dung or "").strip() or _dong_y.bay_gio()
    nguon_sach = str(nguon_dung or "").strip() or "api"
    so_goc = so_muc_tieu if isinstance(so_muc_tieu, list) else []
    so_moi = _dong_y.ghi(
        so_goc,
        nguoi_dung,
        muc_dich_dung,
        bool(_dong_y._chuan_dong_y(dong_y_dung)),
        thoi_diem,
        nguon_sach,
        trang_thai=trang_thai,
    )
    dong_moi = dict(so_moi[-1])

    if so_muc_tieu is not None:
        if not isinstance(so_muc_tieu, list):
            raise ValueError("kho đồng ý phải là list")
        so_muc_tieu[:] = so_moi
        return dong_moi

    frappe = _lay_frappe()
    if not _frappe_co_db(frappe):
        return dong_moi

    du_lieu_doc: dict = {
        "doctype": "LX Dong Y",
        "nguoi": dong_moi["nguoi"],
        "muc_dich": dong_moi["muc_dich"],
        "dong_y": 0 if dong_moi.get("trang_thai") == "cho_xac_minh" else (1 if dong_moi["dong_y"] else 0),
        "luc": dong_moi["luc"],
        "nguon": dong_moi["nguon"],
    }
    if dong_moi.get("trang_thai"):
        du_lieu_doc["trang_thai"] = dong_moi["trang_thai"]

    doc = frappe.get_doc(du_lieu_doc)
    if hasattr(doc, "flags"):
        doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    return {
        "name": getattr(doc, "name", None),
        **dong_moi,
    }


def _tim_goi_frappe(frappe_mod, ma_goi: str) -> dict | None:
    ma = str(ma_goi or "").strip()
    if not ma:
        return None
    db = getattr(frappe_mod, "db", None)
    if db is not None and callable(getattr(db, "get_value", None)):
        try:
            row = db.get_value(
                "LX Goi",
                ma,
                ["name", "ma", "ten", "gia", "gia_san", "ban", "workflow"],
                as_dict=True,
            )
            if isinstance(row, dict) and row.get("name"):
                return dict(row)
        except Exception:
            pass
    if callable(getattr(frappe_mod, "get_all", None)):
        for truong in ("name", "ma"):
            try:
                ds = frappe_mod.get_all(
                    "LX Goi",
                    filters={truong: ma},
                    fields=["name", "ma", "ten", "gia", "gia_san", "ban", "workflow"],
                    limit=1,
                )
                if ds and isinstance(ds[0], dict):
                    return dict(ds[0])
            except Exception:
                continue
    return None


def _lam_sach_thong_tin_don(thong_tin: dict | None, them: dict) -> dict:
    gop = {}
    if isinstance(thong_tin, dict):
        gop.update(thong_tin)
    gop.update(them)
    sach: dict = {}
    for truong, toi_da in _GIOI_HAN_TRUONG_DON:
        if truong not in gop or gop[truong] is None:
            continue
        chuoi = str(gop[truong]).replace("\r", " ").replace("\n", " ").strip()
        if len(chuoi) > toi_da:
            raise ValueError(f"Trường {truong} vượt quá {toi_da} ký tự")
        if chuoi:
            sach[truong] = chuoi
    return sach


def tao_don(
    goi: dict | str,
    nguoi: str | dict = "",
    kho_hoac_ngan_hang: list[dict] | dict | None = None,
    ma_don: str | None = None,
    *,
    so_tien: int | float | None = None,
    noi_dung_ck: str | None = None,
    qr_url: str | None = None,
    ngan_hang: dict | None = None,
    thong_tin: dict | None = None,
    kho: list[dict] | None = None,
    **them,
) -> dict:
    """Tạo đơn hàng `LX Don` ở trạng thái `cho_tra`, kiểm tra bắt buộc ngưỡng `gia_san` của `LX Goi`."""
    kho_dung = kho
    nh_dung = ngan_hang
    if isinstance(kho_hoac_ngan_hang, list) and kho_dung is None:
        kho_dung = kho_hoac_ngan_hang
    elif isinstance(kho_hoac_ngan_hang, dict) and nh_dung is None:
        nh_dung = kho_hoac_ngan_hang
    elif kho_hoac_ngan_hang is not None:
        raise ValueError("Tham số thứ ba của tao_don phải là kho (list) hoặc ngan_hang (dict)")

    frappe = _lay_frappe()
    co_db = _frappe_co_db(frappe) and kho_dung is None

    if isinstance(goi, str):
        ma_goi_tim = goi.strip()
        if not ma_goi_tim:
            raise ValueError("Mã gói không được để trống")
        if co_db:
            goi_db = _tim_goi_frappe(frappe, ma_goi_tim)
            if goi_db is None:
                raise ValueError(f"Không tìm thấy gói: {ma_goi_tim}")
            if "ban" in goi_db and goi_db["ban"] is not None and not bool(int(goi_db["ban"]) if isinstance(goi_db["ban"], (int, float)) else goi_db["ban"]):
                raise ValueError(f"Gói đã ngừng bán: {ma_goi_tim}")
            goi_dict = goi_db
        else:
            if so_tien is None:
                raise ValueError("Khi truyền mã gói dạng chuỗi ngoài Frappe cần truyền thêm so_tien")
            goi_dict = {"ma": ma_goi_tim, "name": ma_goi_tim, "gia": so_tien, "gia_san": 0}
    elif isinstance(goi, dict):
        goi_dict = dict(goi)
        if co_db:
            ten_goi_db = str(goi_dict.get("name") or goi_dict.get("ma") or "").strip()
            if ten_goi_db:
                goi_db = _tim_goi_frappe(frappe, ten_goi_db)
                if goi_db is not None:
                    gia_san_db = float(goi_db.get("gia_san") or 0)
                    gia_san_in = float(goi_dict.get("gia_san") or 0)
                    goi_dict["gia_san"] = max(gia_san_db, gia_san_in)
                    if goi_dict.get("gia") is None and goi_db.get("gia") is not None:
                        goi_dict["gia"] = goi_db["gia"]
    else:
        raise ValueError("goi phải là dict hoặc mã gói dạng chuỗi")

    raw_tien = (
        so_tien
        if so_tien is not None
        else (goi_dict.get("gia") if goi_dict.get("gia") is not None else goi_dict.get("gia_san"))
    )
    if raw_tien is None or isinstance(raw_tien, bool):
        raise ValueError("Gói thiếu thông tin giá")
    if isinstance(raw_tien, float) and not raw_tien.is_integer():
        raise ValueError("Số tiền đơn phải là số nguyên")
    try:
        tien_int = int(raw_tien)
    except (TypeError, ValueError) as exc:
        raise ValueError("Số tiền đơn không hợp lệ") from exc

    if tien_int <= 0 or not _quyen_dung.gia_hop_le(tien_int, goi_dict):
        raise ValueError("Số tiền đơn dưới giá sàn của gói")

    ma_sach = str(ma_don or "").strip() or f"DON-{secrets.token_hex(4).upper()}"
    nd_sach = str(noi_dung_ck or "").strip() or _sinh_noi_dung_ck(ma_sach)
    url_sach = str(qr_url or "").strip()
    if not url_sach and isinstance(nh_dung, dict):
        url_sach = _sinh_qr_vietqr(tien_int, nd_sach, nh_dung)

    ma_goi_luu = str(goi_dict.get("name") or goi_dict.get("ma") or "").strip()
    if not ma_goi_luu:
        raise ValueError("Gói thiếu định danh name/ma")

    ma_nguoi = _ma_nguoi_tu_tham_so(nguoi)
    phu_sach = _lam_sach_thong_tin_don(thong_tin, them)

    ban_ghi_don: dict = {
        "name": ma_sach,
        "ma": ma_sach,
        "goi": ma_goi_luu,
        "nguoi": ma_nguoi,
        "so_tien": tien_int,
        "trang_thai": "cho_tra",
        "noi_dung_ck": nd_sach,
        "qr_url": url_sach,
        **phu_sach,
    }

    if kho_dung is not None:
        kho_dung.append(ban_ghi_don)
        return dict(ban_ghi_don)

    if not co_db:
        return dict(ban_ghi_don)

    du_lieu_doc: dict = {
        "doctype": "LX Don",
        "ma": ma_sach,
        "goi": ma_goi_luu,
        "so_tien": tien_int,
        "trang_thai": "cho_tra",
        "noi_dung_ck": nd_sach,
        "qr_url": url_sach,
        **phu_sach,
    }
    if ma_nguoi:
        du_lieu_doc["nguoi"] = ma_nguoi

    doc = frappe.get_doc(du_lieu_doc)
    if hasattr(doc, "flags"):
        doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    ban_ghi_don["name"] = str(getattr(doc, "name", None) or ma_sach)
    return dict(ban_ghi_don)


def _doc_don_sang_dict(doc) -> dict:
    ma_ten = str(getattr(doc, "name", "") or "").strip()
    kq: dict = {
        "name": ma_ten,
        "ma": str(getattr(doc, "ma", None) or ma_ten).strip(),
        "goi": getattr(doc, "goi", None),
        "nguoi": getattr(doc, "nguoi", None),
        "so_tien": getattr(doc, "so_tien", None),
        "trang_thai": getattr(doc, "trang_thai", None),
        "noi_dung_ck": getattr(doc, "noi_dung_ck", None),
        "tx_id": getattr(doc, "tx_id", None),
        "qr_url": getattr(doc, "qr_url", None),
    }
    for truong, _ in _GIOI_HAN_TRUONG_DON:
        gt = getattr(doc, truong, None)
        if gt is not None:
            kq[truong] = gt
    return kq


def _tim_ten_don_frappe(frappe_mod, ma_tim: str) -> str | None:
    ma = str(ma_tim or "").strip()
    if not ma:
        return None
    db = getattr(frappe_mod, "db", None)
    if db is not None and callable(getattr(db, "exists", None)):
        try:
            ten = db.exists("LX Don", ma)
            if isinstance(ten, str) and ten:
                return ten
            if ten is True:
                return ma
        except Exception:
            pass
    if callable(getattr(frappe_mod, "get_all", None)):
        for truong in ("name", "ma", "noi_dung_ck"):
            try:
                ds = frappe_mod.get_all(
                    "LX Don",
                    filters={truong: ma},
                    fields=["name"],
                    limit=1,
                )
                if ds and isinstance(ds[0], dict) and ds[0].get("name"):
                    return str(ds[0]["name"]).strip()
            except Exception:
                continue
    return None


def _dam_bao_phat_don_da_tra_db(frappe_mod, ten_don: str, tx_id: str | None = None) -> None:
    """Đảm bảo sự kiện `don.da_tra` có mặt trong outbox `LX Su Kien` đúng một lần khi chuyển `da_tra`."""
    db = getattr(frappe_mod, "db", None)
    if db is None or not callable(getattr(db, "exists", None)):
        return
    try:
        co_doctype = db.exists("DocType", "LX Su Kien")
    except Exception:
        return
    if not co_doctype or isinstance(co_doctype, dict):
        return

    if callable(getattr(frappe_mod, "get_all", None)):
        try:
            ds_sk = frappe_mod.get_all(
                "LX Su Kien",
                filters={"ten": "don.da_tra"},
                fields=["name", "du_lieu"],
                order_by="creation desc",
                limit_page_length=50,
            )
            for sk in ds_sk or []:
                if not isinstance(sk, dict):
                    continue
                raw_dl = sk.get("du_lieu")
                dl = None
                if isinstance(raw_dl, dict):
                    dl = raw_dl
                elif isinstance(raw_dl, str) and raw_dl.strip():
                    try:
                        dl = json.loads(raw_dl)
                    except ValueError:
                        dl = None
                if isinstance(dl, dict) and str(dl.get("don") or "").strip() == ten_don:
                    return
        except Exception:
            pass

    goi_dl: dict = {"don": ten_don}
    if tx_id:
        goi_dl["tx_id"] = tx_id
    phat("don.da_tra", goi_dl)


def danh_dau_da_tra(
    don: str | dict | object,
    tx_id: str | None = None,
    *,
    so_tien: int | float | None = None,
    kho: list[dict] | None = None,
    kho_su_kien: list[dict] | None = None,
) -> dict:
    """Chuyển đơn `LX Don` sang `da_tra` (chống phát trùng) và phát sự kiện `don.da_tra`."""
    tx_sach = str(tx_id).strip() if isinstance(tx_id, str) and tx_id.strip() else None
    if so_tien is not None and isinstance(so_tien, bool):
        raise ValueError("so_tien không hợp lệ")

    if kho is not None:
        if not isinstance(kho, list):
            raise ValueError("kho đơn phải là list")
        ma_tim = (
            str(don.get("name") or don.get("ma") or don.get("noi_dung_ck") or "").strip()
            if isinstance(don, dict)
            else str(don or "").strip()
        )
        if not ma_tim:
            raise ValueError("Thiếu mã đơn cần đánh dấu đã trả")
        muc_khop = None
        for muc in kho:
            if not isinstance(muc, dict):
                continue
            if muc is don or ma_tim in {
                str(muc.get("name") or "").strip(),
                str(muc.get("ma") or "").strip(),
                str(muc.get("noi_dung_ck") or "").strip(),
            }:
                muc_khop = muc
                break
        if muc_khop is None:
            raise ValueError(f"Không tìm thấy đơn: {ma_tim}")

        tt_cu = str(muc_khop.get("trang_thai") or "").strip()
        if tt_cu == "huy":
            raise ValueError("Đơn đã huỷ, không thể đánh dấu đã trả")
        if tt_cu == "da_tra":
            return dict(muc_khop)
        if so_tien is not None and float(so_tien) < float(muc_khop.get("so_tien") or 0):
            raise ValueError("Số tiền thanh toán thấp hơn số tiền đơn")

        muc_khop["trang_thai"] = "da_tra"
        if tx_sach:
            muc_khop["tx_id"] = tx_sach
        if kho_su_kien is not None:
            ten_don = str(muc_khop.get("name") or muc_khop.get("ma") or ma_tim).strip()
            goi_sk: dict = {"don": ten_don}
            if muc_khop.get("tx_id"):
                goi_sk["tx_id"] = muc_khop["tx_id"]
            phat("don.da_tra", goi_sk, kho=kho_su_kien)
        return dict(muc_khop)

    frappe = _lay_frappe()
    la_doc_frappe = not isinstance(don, (str, dict)) and callable(getattr(don, "save", None))
    if la_doc_frappe or _frappe_co_db(frappe):
        if la_doc_frappe:
            doc_don = don
        else:
            ma_tim_db = (
                str(don.get("name") or don.get("ma") or don.get("noi_dung_ck") or "").strip()
                if isinstance(don, dict)
                else str(don or "").strip()
            )
            if not ma_tim_db:
                raise ValueError("Thiếu mã đơn cần đánh dấu đã trả")
            ten_doc = _tim_ten_don_frappe(frappe, ma_tim_db) or ma_tim_db
            doc_don = frappe.get_doc("LX Don", ten_doc, for_update=True)

        tt_cu_db = str(getattr(doc_don, "trang_thai", "") or "").strip()
        if tt_cu_db == "huy":
            raise ValueError("Đơn đã huỷ, không thể đánh dấu đã trả")
        if tt_cu_db == "da_tra":
            return _doc_don_sang_dict(doc_don)
        if so_tien is not None and float(so_tien) < float(getattr(doc_don, "so_tien", 0) or 0):
            raise ValueError("Số tiền thanh toán thấp hơn số tiền đơn")

        doc_don.trang_thai = "da_tra"
        if tx_sach:
            doc_don.tx_id = tx_sach
        if hasattr(doc_don, "flags"):
            doc_don.flags.ignore_permissions = True
        doc_don.save(ignore_permissions=True)

        ten_chinh = str(getattr(doc_don, "name", None) or getattr(doc_don, "ma", "") or "").strip()
        if kho_su_kien is not None:
            goi_sk_mem: dict = {"don": ten_chinh}
            if getattr(doc_don, "tx_id", None):
                goi_sk_mem["tx_id"] = doc_don.tx_id
            phat("don.da_tra", goi_sk_mem, kho=kho_su_kien)
        elif frappe is not None and ten_chinh:
            _dam_bao_phat_don_da_tra_db(frappe, ten_chinh, getattr(doc_don, "tx_id", None))
        return _doc_don_sang_dict(doc_don)

    if isinstance(don, dict):
        tt_cu_dict = str(don.get("trang_thai") or "").strip()
        if tt_cu_dict == "huy":
            raise ValueError("Đơn đã huỷ, không thể đánh dấu đã trả")
        if tt_cu_dict == "da_tra":
            return dict(don)
        if so_tien is not None and float(so_tien) < float(don.get("so_tien") or 0):
            raise ValueError("Số tiền thanh toán thấp hơn số tiền đơn")
        don["trang_thai"] = "da_tra"
        if tx_sach:
            don["tx_id"] = tx_sach
        if kho_su_kien is not None:
            ten_don_le = str(don.get("name") or don.get("ma") or "").strip()
            phat("don.da_tra", {"don": ten_don_le}, kho=kho_su_kien)
        return dict(don)

    raise RuntimeError("Cần truyền kho (list), dict đơn hoặc chạy trong môi trường Frappe có kết nối DB")


def cap_quyen_dung(
    don: dict | str,
    goi: dict | str | None = None,
    *,
    kho: list[dict] | None = None,
) -> dict | None:
    """Cấp `LX Quyen Dung` khi đơn đã `da_tra` và đạt ngưỡng `gia_san` của `LX Goi` (chống cấp trùng theo đơn)."""
    frappe = _lay_frappe()
    co_db = _frappe_co_db(frappe)

    if isinstance(don, dict):
        don_dict = dict(don)
    elif isinstance(don, str) and co_db:
        ten_doc = _tim_ten_don_frappe(frappe, don)
        if not ten_doc:
            raise ValueError(f"Không tìm thấy đơn: {don}")
        don_dict = _doc_don_sang_dict(frappe.get_doc("LX Don", ten_doc))
    else:
        return None

    if isinstance(goi, dict):
        goi_dict = dict(goi)
    else:
        ma_goi_tim = str(goi if isinstance(goi, str) and goi.strip() else (don_dict.get("goi") or "")).strip()
        if not ma_goi_tim or not co_db:
            return None
        goi_db = _tim_goi_frappe(frappe, ma_goi_tim)
        if goi_db is None:
            return None
        goi_dict = goi_db

    quyen = _quyen_dung.cap_quyen(don_dict, goi_dict)
    if quyen is None:
        return None

    if kho is not None:
        if not isinstance(kho, list):
            raise ValueError("kho quyền dùng phải là list")
        ma_don_q = str(quyen.get("don") or "").strip()
        if ma_don_q:
            for hien_co in kho:
                if isinstance(hien_co, dict) and str(hien_co.get("don") or "").strip() == ma_don_q:
                    return dict(hien_co)
        ban_ghi = dict(quyen)
        kho.append(ban_ghi)
        return dict(ban_ghi)

    if not co_db:
        return dict(quyen)

    ma_don_db = str(quyen.get("don") or "").strip()
    if ma_don_db and callable(getattr(frappe, "get_all", None)):
        try:
            da_cap = frappe.get_all(
                "LX Quyen Dung",
                filters={"don": ma_don_db},
                fields=["name", "goi", "nguoi", "don", "so_tien", "trang_thai"],
                limit=1,
            )
            if da_cap and isinstance(da_cap[0], dict):
                return dict(da_cap[0])
        except Exception:
            pass

    du_lieu_qd: dict = {
        "doctype": "LX Quyen Dung",
        "goi": quyen.get("goi"),
        "don": quyen.get("don"),
        "so_tien": quyen.get("so_tien"),
        "trang_thai": quyen.get("trang_thai") or "hieu_luc",
    }
    if quyen.get("nguoi"):
        du_lieu_qd["nguoi"] = quyen["nguoi"]

    doc_qd = frappe.get_doc(du_lieu_qd)
    if hasattr(doc_qd, "flags"):
        doc_qd.flags.ignore_permissions = True
    doc_qd.insert(ignore_permissions=True)
    return {
        "name": getattr(doc_qd, "name", None),
        **quyen,
    }


def _doc_co_single_frappe(frappe_mod) -> dict[str, int]:
    kq = dict(_CO_MAC_DINH)
    try:
        co_cb = co_module._doc_cau_hinh_frappe()
        if isinstance(co_cb, dict):
            for k, v in co_cb.items():
                kq[k] = int(co_module._co_bat(v))
    except Exception:
        pass
    db = getattr(frappe_mod, "db", None)
    if db is not None:
        try:
            if callable(getattr(db, "sql", None)):
                rows = db.sql(
                    "SELECT value FROM `tabSingles` WHERE doctype=%s AND field=%s LIMIT 1",
                    ("LX Cau Hinh", "bat_bong"),
                )
                val = rows[0][0] if rows else None
            elif callable(getattr(db, "get_single_value", None)):
                val = db.get_single_value("LX Cau Hinh", "bat_bong")
            else:
                val = None
            if val is not None:
                kq["bat_bong"] = int(co_module._co_bat(val))
        except Exception:
            pass
    return kq


def doc_cau_hinh(
    khoa: str | None = None,
    mac_dinh: object = None,
    *,
    cau_hinh: dict | None = None,
) -> object:
    """Đọc cờ bật module (`LX Cau Hinh`) và cấu hình site được phép dùng cho `adapter`/`goi`."""
    if khoa is not None:
        if not isinstance(khoa, str) or not khoa.strip():
            raise ValueError("khoa cấu hình phải là chuỗi khác rỗng hoặc None")
        khoa_sach = khoa.strip()
        if khoa_sach in _KHOA_CAM_CAU_HINH:
            raise PermissionError(f"Không được đọc khoá bí mật hệ thống qua linhx_core.api: {khoa_sach}")
    else:
        khoa_sach = None

    if cau_hinh is not None:
        if not isinstance(cau_hinh, dict):
            raise ValueError("cau_hinh truyền vào phải là dict")
        if khoa_sach is None:
            return {k: copy.deepcopy(v) for k, v in cau_hinh.items() if k not in _KHOA_CAM_CAU_HINH}
        return copy.deepcopy(cau_hinh[khoa_sach]) if khoa_sach in cau_hinh else mac_dinh

    frappe = _lay_frappe()
    co_db = _frappe_co_db(frappe)

    if khoa_sach is None:
        if co_db:
            return _doc_co_single_frappe(frappe)
        return dict(_CO_MAC_DINH)

    if khoa_sach in _CO_MAC_DINH:
        if co_db:
            bang_co = _doc_co_single_frappe(frappe)
            return bang_co.get(khoa_sach, 0 if mac_dinh is None else mac_dinh)
        return 0 if mac_dinh is None else mac_dinh

    if co_db and khoa_sach == "nguong_doanh_thu":
        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "get_single_value", None)):
            try:
                val_nd = db.get_single_value("LX Cau Hinh Pay", "nguong_doanh_thu")
                if val_nd is not None:
                    return val_nd
            except Exception:
                pass

    if frappe is not None:
        try:
            conf = getattr(frappe, "conf", None)
            if conf is not None and callable(getattr(conf, "get", None)):
                gt_conf = conf.get(khoa_sach)
                if gt_conf is not None:
                    return copy.deepcopy(gt_conf)
        except Exception:
            pass

    return mac_dinh
