"""OTP email dùng chung cho LINHX Core (đăng nhập và xác minh đồng ý marketing C2B).

Module thuần Python (không import frappe ở đầu file):
- Chỉ lưu bản băm HMAC-SHA256 của mã OTP trong kho (không bao giờ lưu mã trần).
- Mã hết hạn sau 10 phút (`HAN_PHUT = 10`).
- Nhập sai 5 lần (`SAI_TOI_DA = 5`) thì khoá kênh 15 phút (`KHOA_PHUT = 15`).
- Mã chỉ dùng một lần (`da_dung = True` ngay sau khi xác minh thành công).
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import threading
from typing import Callable, Iterator

from linhx_core.crm import gop_trung

HAN_PHUT = 10
SAI_TOI_DA = 5
KHOA_PHUT = 15

CHO_PHAT_LAI_GIAY = 60
GIOI_HAN_PHAT_MOI_GIO_EMAIL = 5
GIOI_HAN_PHAT_MOI_GIO_IP = 10
CUA_SO_GIOI_HAN_GIAY = 3600

DO_DAI_MA_OTP = 6
DO_DAI_EMAIL_TOI_DA = 254
DO_DAI_MUC_DICH_TOI_DA = 64
DO_DAI_MA_TOI_DA = 64
DO_DAI_IP_TOI_DA = 64
DINH_DANG_LUC_MAC_DINH = "%Y-%m-%d %H:%M:%S"

MUC_DICH_HOP_LE = frozenset({
    "dang_nhap",
    "marketing",
    "xac_minh_email",
    "khoi_phuc_mat_khau",
    "xac_nhan_giao_dich",
})

_MAU_LOCAL_EMAIL = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`~-]+$")
_MAU_DOMAIN_EMAIL = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")
_KHOA_GIAO_DICH = threading.RLock()
_TEN_KHOA_TAM_TIEN_TRINH = "_linhx_otp_khoa_hmac_tam"


def _gio_may_chu() -> str:
    """Lấy thời điểm hiện tại của máy chủ theo UTC định dạng chuẩn."""
    return datetime.now(timezone.utc).replace(tzinfo=None).strftime(DINH_DANG_LUC_MAC_DINH)


def _chan_tham_so_tu_request_http() -> None:
    """Chặn việc truyền `luc` hoặc `ma_otp` từ `frappe.local.form_dict` khi gọi qua HTTP request."""
    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is None:
        return
    local_ctx = getattr(frappe_mod, "local", None)
    if local_ctx is None or getattr(local_ctx, "request", None) is None:
        return
    form_dict = getattr(local_ctx, "form_dict", None)
    if isinstance(form_dict, dict) and ("luc" in form_dict or "ma_otp" in form_dict):
        raise ValueError("Không cho phép truyền tham số luc hoặc ma_otp từ HTTP request")


def _lay_khoa_hmac() -> bytes:
    """Lấy khoá bí mật HMAC từ biến môi trường hoặc cấu hình site Frappe (không lưu cứng trong code)."""
    tu_env = os.environ.get("LINHX_OTP_KHOA_BI_MAT") or os.environ.get("LINHX_OTP_HMAC_KEY")
    if isinstance(tu_env, str) and tu_env.strip():
        return tu_env.strip().encode("utf-8")

    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is not None:
        conf = getattr(frappe_mod, "conf", None)
        if conf is not None and hasattr(conf, "get"):
            for ten_khoa in ("otp_khoa_bi_mat", "linhx_otp_khoa_bi_mat", "encryption_key"):
                gia_tri = conf.get(ten_khoa)
                if isinstance(gia_tri, str) and gia_tri.strip():
                    return gia_tri.strip().encode("utf-8")
        raise RuntimeError("Thiếu cấu hình khoá bí mật OTP (otp_khoa_bi_mat) trong site_config")

    # Chỉ dùng khi chạy pytest hộp đen độc lập không có Frappe và không đặt biến môi trường
    khoa_tam = getattr(sys, _TEN_KHOA_TAM_TIEN_TRINH, None)
    if not isinstance(khoa_tam, bytes) or len(khoa_tam) < 32:
        khoa_tam = secrets.token_bytes(32)
        setattr(sys, _TEN_KHOA_TAM_TIEN_TRINH, khoa_tam)
    return khoa_tam


def _chuan_hoa_email(email: str) -> str:
    """Chuẩn hoá email chữ thường, từ chối ký tự `|` và kiểm tra khuôn dạng."""
    if not isinstance(email, str):
        raise ValueError("Email phải là chuỗi ký tự")
    email_chuan = gop_trung.chuan_hoa_email(email)
    if (
        not email_chuan
        or len(email_chuan) > DO_DAI_EMAIL_TOI_DA
        or "|" in email_chuan
        or "@" not in email_chuan
        or any(ch.isspace() for ch in email_chuan)
    ):
        raise ValueError("Email không hợp lệ")
    local_part, _, domain_part = email_chuan.partition("@")
    if (
        not local_part
        or not domain_part
        or "@" in domain_part
        or not _MAU_LOCAL_EMAIL.match(local_part)
        or not _MAU_DOMAIN_EMAIL.match(domain_part)
    ):
        raise ValueError("Email không hợp lệ")
    return email_chuan


def _chuan_hoa_muc_dich(muc_dich: str) -> str:
    """Chuẩn hoá và kiểm tra mục đích OTP theo danh sách trắng."""
    if not isinstance(muc_dich, str):
        raise ValueError("Mục đích OTP phải là chuỗi ký tự")
    muc_dich_chuan = muc_dich.strip()
    if (
        not muc_dich_chuan
        or len(muc_dich_chuan) > DO_DAI_MUC_DICH_TOI_DA
        or "|" in muc_dich_chuan
        or muc_dich_chuan not in MUC_DICH_HOP_LE
    ):
        raise ValueError("Mục đích OTP không hợp lệ")
    return muc_dich_chuan


def _chuan_hoa_ma_otp(ma_otp: str) -> str:
    """Chuẩn hoá và kiểm tra chuỗi mã OTP."""
    if not isinstance(ma_otp, str):
        raise ValueError("Mã OTP phải là chuỗi ký tự")
    ma_chuan = ma_otp.strip()
    if not ma_chuan or len(ma_chuan) > DO_DAI_MA_TOI_DA:
        raise ValueError("Mã OTP không hợp lệ")
    return ma_chuan


def _chuan_hoa_ip(ip: str | None) -> str | None:
    """Chuẩn hoá chuỗi địa chỉ IP (nếu được cung cấp)."""
    if ip is None:
        return None
    if not isinstance(ip, str):
        raise ValueError("Địa chỉ IP không hợp lệ")
    ip_chuan = ip.strip()
    if not ip_chuan or len(ip_chuan) > DO_DAI_IP_TOI_DA or any(ch.isspace() for ch in ip_chuan):
        raise ValueError("Địa chỉ IP không hợp lệ")
    return ip_chuan


def _phan_tich_luc(luc: str) -> datetime:
    """Phân tích chuỗi thời điểm và chuẩn hoá về UTC naive để so sánh an toàn."""
    if not isinstance(luc, str) or not luc.strip():
        raise ValueError("Thời điểm (luc) không hợp lệ")
    chuoi = luc.strip()
    try:
        dt = datetime.strptime(chuoi, DINH_DANG_LUC_MAC_DINH)
    except ValueError:
        try:
            dt = datetime.fromisoformat(chuoi)
        except ValueError as exc:
            raise ValueError(f"Thời điểm không đúng định dạng: {luc!r}") from exc
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _dinh_dang_luc(thoi_diem: datetime) -> str:
    """Định dạng thống nhất thời điểm theo chuẩn `YYYY-MM-DD HH:MM:SS`."""
    if thoi_diem.tzinfo is not None:
        thoi_diem = thoi_diem.astimezone(timezone.utc).replace(tzinfo=None)
    return thoi_diem.strftime(DINH_DANG_LUC_MAC_DINH)


def _khoa_kenh(email_chuan: str, muc_dich_chuan: str) -> str:
    """Tạo khoá kênh tách biên rõ ràng bằng `json.dumps([email, muc_dich])`."""
    return json.dumps([email_chuan, muc_dich_chuan], ensure_ascii=False)


@contextmanager
def _giao_dich_khoa_kenh(kho: dict, khoa: str) -> Iterator[None]:
    """Bọc thao tác đọc và ghi trong khoá luồng và giao dịch DB `SELECT ... FOR UPDATE` (nếu có)."""
    with _KHOA_GIAO_DICH:
        frappe_mod = sys.modules.get("frappe")
        db = getattr(frappe_mod, "db", None) if frappe_mod is not None else None
        sql_fn = getattr(db, "sql", None) if db is not None else None
        if callable(sql_fn) and getattr(kho, "_bang_db", None):
            dong_khoa = sql_fn(
                "SELECT name, ma_bam, tao_luc, het_han_luc, da_dung, so_lan_sai, khoa_den "
                "FROM `tabLX OTP` WHERE khoa_kenh = %s FOR UPDATE",
                (khoa,),
                as_dict=True,
            )
            if isinstance(dong_khoa, list) and dong_khoa:
                kho[khoa] = dict(dong_khoa[0])
        yield


def _cap_nhat_nguyen_tu(
    kho: dict,
    khoa: str,
    ban_ghi: dict,
    *,
    da_dung_moi: bool | None = None,
    so_lan_sai_moi: int | None = None,
    khoa_den_moi: str | None = None,
    cap_nhat_luc_moi: str | None = None,
) -> bool:
    """Cập nhật nguyên tử có điều kiện (`WHERE da_dung = 0 AND so_lan_sai < SAI_TOI_DA`)."""
    if ban_ghi.get("da_dung") is True:
        return False
    so_lan_sai_hien_tai = int(ban_ghi.get("so_lan_sai") or 0)
    if so_lan_sai_hien_tai >= SAI_TOI_DA:
        return False

    frappe_mod = sys.modules.get("frappe")
    db = getattr(frappe_mod, "db", None) if frappe_mod is not None else None
    sql_fn = getattr(db, "sql", None) if db is not None else None
    if callable(sql_fn) and getattr(kho, "_bang_db", None):
        sql_fn(
            "UPDATE `tabLX OTP` SET da_dung = %s, so_lan_sai = %s, khoa_den = %s "
            "WHERE khoa_kenh = %s AND da_dung = 0 AND so_lan_sai < %s",
            (
                1 if da_dung_moi else 0,
                so_lan_sai_moi if so_lan_sai_moi is not None else so_lan_sai_hien_tai,
                khoa_den_moi,
                khoa,
                SAI_TOI_DA,
            ),
        )
        con_tro = getattr(db, "_cursor", None)
        so_dong = getattr(con_tro, "rowcount", 1) if con_tro is not None else 1
        if so_dong == 0:
            return False

    if da_dung_moi is not None:
        ban_ghi["da_dung"] = da_dung_moi
    if so_lan_sai_moi is not None:
        ban_ghi["so_lan_sai"] = so_lan_sai_moi
    if khoa_den_moi is not None:
        ban_ghi["khoa_den"] = khoa_den_moi
    if cap_nhat_luc_moi is not None:
        ban_ghi["cap_nhat_luc"] = cap_nhat_luc_moi
    return True


def bam_ma(email: str, muc_dich: str, ma_otp: str) -> str:
    """Băm HMAC-SHA256 hex của `(email chuẩn hoá chữ thường, muc_dich, ma_otp)`.

    Không bao giờ trả mã OTP trần.
    """
    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    ma_chuan = _chuan_hoa_ma_otp(ma_otp)
    du_lieu = json.dumps(
        ["linhx-otp-v2", email_chuan, muc_dich_chuan, ma_chuan],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    khoa_hmac = _lay_khoa_hmac()
    return hmac.new(khoa_hmac, du_lieu, hashlib.sha256).hexdigest()


def _sinh_ma_otp() -> str:
    """Sinh mã OTP ngẫu nhiên an toàn gồm 6 chữ số."""
    return f"{secrets.randbelow(10 ** DO_DAI_MA_OTP):0{DO_DAI_MA_OTP}d}"


def _loc_lich_su_trong_gio(ds_luc: list[str], thoi_diem: datetime) -> list[str]:
    """Giữ lại các mốc thời gian phát mã nằm trong cửa sổ 1 giờ gần nhất."""
    ket_qua: list[str] = []
    for moc in ds_luc:
        if not isinstance(moc, str):
            continue
        try:
            dt = _phan_tich_luc(moc)
        except ValueError:
            continue
        khoang_cach = (thoi_diem - dt).total_seconds()
        if 0 <= khoang_cach < CUA_SO_GIOI_HAN_GIAY:
            ket_qua.append(_dinh_dang_luc(dt))
    return ket_qua


def _kiem_gioi_han_phat(
    kho: dict,
    email_chuan: str,
    ip_chuan: str | None,
    thoi_diem: datetime,
) -> None:
    """Kiểm tra giới hạn số lần phát mã mỗi giờ theo email và theo IP."""
    tong_theo_email = 0
    tong_theo_ip = 0
    for gia_tri in kho.values():
        if not isinstance(gia_tri, dict):
            continue
        lich_su = _loc_lich_su_trong_gio(list(gia_tri.get("lich_su_phat") or []), thoi_diem)
        if gia_tri.get("email") == email_chuan:
            tong_theo_email += len(lich_su)
        if ip_chuan is not None:
            lich_su_ip = gia_tri.get("lich_su_phat_ip")
            if isinstance(lich_su_ip, dict) and ip_chuan in lich_su_ip:
                tong_theo_ip += len(_loc_lich_su_trong_gio(list(lich_su_ip.get(ip_chuan) or []), thoi_diem))

    if tong_theo_email >= GIOI_HAN_PHAT_MOI_GIO_EMAIL:
        raise ValueError("Vượt quá giới hạn số lần phát mã OTP mỗi giờ cho email này")
    if ip_chuan is not None and tong_theo_ip >= GIOI_HAN_PHAT_MOI_GIO_IP:
        raise ValueError("Vượt quá giới hạn số lần phát mã OTP mỗi giờ cho địa chỉ IP này")


def phat_ma(
    kho: dict,
    email: str,
    muc_dich: str,
    luc: str | None = None,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], object] | None = None,
    ip: str | None = None,
) -> dict:
    """Phát mã OTP mới cho kênh `(email, muc_dich)` tại thời điểm `luc`.

    - Nếu kênh đang bị khoá tại thời điểm `luc` (`luc < khoa_den`) -> `raise ValueError`.
    - Áp dụng thời gian chờ tối thiểu giữa hai lần phát (`CHO_PHAT_LAI_GIAY`) và giới hạn
      số lần phát mỗi giờ theo email và theo IP.
    - Giữ nguyên `so_lan_sai` và `khoa_den` khi phát lại trước khi mã cũ được dùng hoặc hết khoá.
    - Sinh mã 6 chữ số (hoặc dùng `ma_otp` truyền vào khi kiểm thử).
    - Chỉ lưu bản băm `ma_bam = bam_ma(...)` vào `kho`, tuyệt đối không lưu mã trần.
    - Nếu có `gui_mail` thì gọi `gui_mail(email_chuan, ma_otp, muc_dich)`.
    - Trả `{"email": email_chuan, "muc_dich": muc_dich, "het_han_luc": str}`.
    """
    if not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")
    if gui_mail is not None and not callable(gui_mail):
        raise ValueError("gui_mail phải là hàm gọi được")

    _chan_tham_so_tu_request_http()
    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    ip_chuan = _chuan_hoa_ip(ip)
    luc_hieu_luc = _gio_may_chu() if luc is None else luc
    thoi_diem = _phan_tich_luc(luc_hieu_luc)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    with _giao_dich_khoa_kenh(kho, khoa):
        ban_ghi_cu = kho.get(khoa)
        so_lan_sai_ke_thua = 0
        khoa_den_ke_thua: str | None = None
        lich_su_cu: list[str] = []
        lich_su_ip_cu: dict[str, list[str]] = {}

        if isinstance(ban_ghi_cu, dict):
            tao_luc_cu = ban_ghi_cu.get("tao_luc")
            cap_nhat_cu = ban_ghi_cu.get("cap_nhat_luc") or tao_luc_cu
            if cap_nhat_cu and thoi_diem < _phan_tich_luc(str(cap_nhat_cu)):
                raise ValueError("Thời điểm phát mã không hợp lệ (lùi thời gian so với bản ghi hiện tại)")

            khoa_den_cu = ban_ghi_cu.get("khoa_den")
            da_man_han_khoa = False
            if khoa_den_cu:
                if thoi_diem < _phan_tich_luc(str(khoa_den_cu)):
                    raise ValueError("Kênh OTP đang bị khoá tạm thời do nhập sai quá số lần cho phép")
                da_man_han_khoa = True

            if tao_luc_cu:
                giay_da_qua = (thoi_diem - _phan_tich_luc(str(tao_luc_cu))).total_seconds()
                if giay_da_qua < CHO_PHAT_LAI_GIAY:
                    raise ValueError("Vui lòng chờ tối thiểu 60 giây trước khi yêu cầu phát lại mã OTP")

            da_dung_cu = ban_ghi_cu.get("da_dung") is True
            if not da_dung_cu and not da_man_han_khoa:
                so_lan_sai_ke_thua = int(ban_ghi_cu.get("so_lan_sai") or 0)
                khoa_den_ke_thua = str(khoa_den_cu) if khoa_den_cu else None

            lich_su_cu = _loc_lich_su_trong_gio(list(ban_ghi_cu.get("lich_su_phat") or []), thoi_diem)
            raw_ip_map = ban_ghi_cu.get("lich_su_phat_ip")
            if isinstance(raw_ip_map, dict):
                for k_ip, ds_ip in raw_ip_map.items():
                    if isinstance(k_ip, str) and isinstance(ds_ip, list):
                        da_loc = _loc_lich_su_trong_gio(ds_ip, thoi_diem)
                        if da_loc:
                            lich_su_ip_cu[k_ip] = da_loc

        _kiem_gioi_han_phat(kho, email_chuan, ip_chuan, thoi_diem)

        if ma_otp is None:
            ma_chuan = _sinh_ma_otp()
        else:
            ma_chuan = _chuan_hoa_ma_otp(ma_otp)

        ma_bam = bam_ma(email_chuan, muc_dich_chuan, ma_chuan)
        tao_luc_str = _dinh_dang_luc(thoi_diem)
        het_han_str = _dinh_dang_luc(thoi_diem + timedelta(minutes=HAN_PHUT))

        lich_su_moi = lich_su_cu + [tao_luc_str]
        ban_ghi_moi: dict = {
            "email": email_chuan,
            "muc_dich": muc_dich_chuan,
            "ma_bam": ma_bam,
            "tao_luc": tao_luc_str,
            "cap_nhat_luc": tao_luc_str,
            "het_han_luc": het_han_str,
            "so_lan_sai": so_lan_sai_ke_thua,
            "da_dung": False,
            "khoa_den": khoa_den_ke_thua,
            "lich_su_phat": lich_su_moi,
        }
        if ip_chuan is not None or lich_su_ip_cu:
            if ip_chuan is not None:
                lich_su_ip_cu[ip_chuan] = lich_su_ip_cu.get(ip_chuan, []) + [tao_luc_str]
            ban_ghi_moi["lich_su_phat_ip"] = lich_su_ip_cu

        kho[khoa] = ban_ghi_moi

    if gui_mail is not None:
        gui_mail(email_chuan, ma_chuan, muc_dich_chuan)

    return {
        "email": email_chuan,
        "muc_dich": muc_dich_chuan,
        "het_han_luc": het_han_str,
    }


def xac_minh(
    kho: dict,
    email: str,
    muc_dich: str,
    ma_nhap: str,
    luc: str | None = None,
) -> dict:
    """Xác minh mã OTP `ma_nhap` cho kênh `(email, muc_dich)` tại thời điểm `luc`.

    Trả `{"ok": bool, "ly_do": str | None}`:
    - Đang trong thời gian khoá (`luc < khoa_den`) -> `{"ok": False, "ly_do": "bi_khoa"}`
    - Mã đã dùng (`da_dung == True`) -> `{"ok": False, "ly_do": "da_dung"}`
    - Quá 10 phút (`luc > het_han_luc`) -> `{"ok": False, "ly_do": "het_han"}`
    - Băm không khớp: tăng `so_lan_sai += 1`; nếu `so_lan_sai >= 5` thì đặt
      `khoa_den = luc + 15 phút` và trả `{"ok": False, "ly_do": "bi_khoa"}`;
      chưa tới 5 lần trả `{"ok": False, "ly_do": "sai_ma"}`
    - Băm khớp, còn hạn, chưa dùng, không khoá: đặt `da_dung = True`,
      trả `{"ok": True, "ly_do": None}`.
    """
    if not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")

    _chan_tham_so_tu_request_http()
    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    luc_hieu_luc = _gio_may_chu() if luc is None else luc
    thoi_diem = _phan_tich_luc(luc_hieu_luc)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    with _giao_dich_khoa_kenh(kho, khoa):
        ban_ghi = kho.get(khoa)
        if not isinstance(ban_ghi, dict):
            return {"ok": False, "ly_do": "sai_ma"}

        khoa_den = ban_ghi.get("khoa_den")
        if khoa_den and thoi_diem < _phan_tich_luc(str(khoa_den)):
            return {"ok": False, "ly_do": "bi_khoa"}

        tao_luc = ban_ghi.get("tao_luc")
        cap_nhat_luc = ban_ghi.get("cap_nhat_luc") or tao_luc
        if (tao_luc and thoi_diem < _phan_tich_luc(str(tao_luc))) or (
            cap_nhat_luc and thoi_diem < _phan_tich_luc(str(cap_nhat_luc))
        ):
            if khoa_den:
                return {"ok": False, "ly_do": "bi_khoa"}
            return {"ok": False, "ly_do": "het_han"}

        if ban_ghi.get("da_dung") is True:
            return {"ok": False, "ly_do": "da_dung"}

        het_han_luc = ban_ghi.get("het_han_luc")
        if not het_han_luc or thoi_diem > _phan_tich_luc(str(het_han_luc)):
            return {"ok": False, "ly_do": "het_han"}

        if int(ban_ghi.get("so_lan_sai") or 0) >= SAI_TOI_DA:
            return {"ok": False, "ly_do": "bi_khoa"}

        ma_nhap_str = ma_nhap.strip() if isinstance(ma_nhap, str) else ""
        ma_bam_luu = str(ban_ghi.get("ma_bam") or "")
        khop = False
        if ma_nhap_str and len(ma_nhap_str) <= DO_DAI_MA_TOI_DA and ma_bam_luu:
            bam_nhap = bam_ma(email_chuan, muc_dich_chuan, ma_nhap_str)
            khop = hmac.compare_digest(ma_bam_luu.encode("utf-8"), bam_nhap.encode("utf-8"))

        luc_str = _dinh_dang_luc(thoi_diem)
        if not khop:
            so_lan_sai = int(ban_ghi.get("so_lan_sai") or 0) + 1
            khoa_den_moi = (
                _dinh_dang_luc(thoi_diem + timedelta(minutes=KHOA_PHUT))
                if so_lan_sai >= SAI_TOI_DA
                else None
            )
            da_cap_nhat_sai = _cap_nhat_nguyen_tu(
                kho,
                khoa,
                ban_ghi,
                so_lan_sai_moi=so_lan_sai,
                khoa_den_moi=khoa_den_moi,
                cap_nhat_luc_moi=luc_str,
            )
            if not da_cap_nhat_sai:
                if ban_ghi.get("da_dung") is True:
                    return {"ok": False, "ly_do": "da_dung"}
                return {"ok": False, "ly_do": "bi_khoa"}
            if so_lan_sai >= SAI_TOI_DA:
                return {"ok": False, "ly_do": "bi_khoa"}
            return {"ok": False, "ly_do": "sai_ma"}

        da_cap_nhat = _cap_nhat_nguyen_tu(
            kho,
            khoa,
            ban_ghi,
            da_dung_moi=True,
            so_lan_sai_moi=0,
            cap_nhat_luc_moi=luc_str,
        )
        if not da_cap_nhat:
            return {"ok": False, "ly_do": "da_dung"}
        return {"ok": True, "ly_do": None}


def phat_ma_tu_api(
    kho: dict,
    email: str,
    muc_dich: str,
    gui_mail: Callable[[str, str, str], object] | None = None,
    ip: str | None = None,
) -> dict:
    """Điểm vào an toàn cho tầng API: luôn tự lấy giờ máy chủ và tự sinh mã OTP."""
    _chan_tham_so_tu_request_http()
    return phat_ma(
        kho=kho,
        email=email,
        muc_dich=muc_dich,
        luc=_gio_may_chu(),
        ma_otp=None,
        gui_mail=gui_mail,
        ip=ip,
    )


def xac_minh_tu_api(
    kho: dict,
    email: str,
    muc_dich: str,
    ma_nhap: str,
) -> dict:
    """Điểm vào an toàn cho tầng API: luôn tự lấy giờ máy chủ, không nhận `luc` từ request."""
    _chan_tham_so_tu_request_http()
    return xac_minh(
        kho=kho,
        email=email,
        muc_dich=muc_dich,
        ma_nhap=ma_nhap,
        luc=_gio_may_chu(),
    )
