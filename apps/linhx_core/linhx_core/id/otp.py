"""OTP email dùng chung cho LINHX Core (đăng nhập và xác minh đồng ý marketing C2B).

Module thuần Python (không import frappe ở đầu file):
- Chỉ lưu bản băm HMAC-SHA256 của mã OTP (không bao giờ lưu mã OTP trần).
- Mã hết hạn sau 10 phút (`HAN_PHUT = 10`).
- Nhập sai 5 lần (`SAI_TOI_DA = 5`) thì khoá kênh 15 phút (`KHOA_PHUT = 15`).
- Mã chỉ dùng một lần (`da_dung = True` ngay sau khi xác minh thành công).
- Giữ nguyên `so_lan_sai` và `khoa_den` khi phát lại mã trước khi hết khoá hoặc dùng xong;
  áp thời gian chờ tối thiểu 60 giây và giới hạn tần suất O(1) theo chỉ mục email/IP.
- Khi có kết nối DB Frappe (`tabLX OTP`), mọi thao tác đọc/cập nhật chạy trong giao dịch
  `SELECT ... FOR UPDATE` kèm `UPDATE ... WHERE da_dung = 0 AND so_lan_sai < %s`, kiểm
  `SELECT ROW_COUNT()` theo hướng đóng (fail-closed) rồi `commit` hoặc `rollback`.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import sys
import threading
from typing import Callable

from linhx_core.crm import gop_trung

HAN_PHUT = 10
SAI_TOI_DA = 5
KHOA_PHUT = 15

CHO_PHAT_LAI_GIAY = 60
GIOI_HAN_PHAT_MOI_GIO_EMAIL = 5
GIOI_HAN_PHAT_MOI_GIO_IP = 10
GIOI_HAN_SAI_MOI_GIO_IP = 10
CUA_SO_GIOI_HAN_GIAY = 3600
TOI_DA_KHOA_CHI_MUC_IP = 2000

DO_DAI_MA_OTP = 6
DO_DAI_EMAIL_TOI_DA = 254
DO_DAI_MUC_DICH_TOI_DA = 64
DO_DAI_MA_TOI_DA = 64
DINH_DANG_LUC_MAC_DINH = "%Y-%m-%d %H:%M:%S"

THONG_BAO_TU_CHOI_PHAT_MA = "Không thể phát mã OTP lúc này, vui lòng thử lại sau"

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
_BAM_GIA_HANG_THOI_GIAN = "0" * 64

_CHI_MUC_PHAT_IP: dict[str, list[str]] = {}
_CHI_MUC_SAI_IP: dict[str, list[str]] = {}


def _gio_may_chu() -> str:
    """Lấy thời điểm hiện tại của máy chủ theo UTC định dạng chuẩn."""
    return datetime.now(timezone.utc).replace(tzinfo=None).strftime(DINH_DANG_LUC_MAC_DINH)


def _dang_trong_request_http() -> bool:
    """Kiểm tra có đang trong ngữ cảnh HTTP request của Frappe hay không."""
    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is None:
        return False
    local_ctx = getattr(frappe_mod, "local", None)
    return getattr(local_ctx, "request", None) is not None


def _la_moi_truong_production() -> bool:
    """Kiểm tra biến môi trường có đánh dấu chạy production hay không."""
    for ten_bien in ("LINHX_ENV", "APP_ENV", "ENV", "FLASK_ENV"):
        gia_tri = str(os.environ.get(ten_bien) or "").strip().lower()
        if gia_tri in ("production", "prod"):
            return True
    return False


def _lay_khoa_hmac() -> bytes:
    """Lấy khoá bí mật HMAC riêng cho OTP từ biến môi trường hoặc `site_config` (`otp_khoa_bi_mat`).

    - Không dùng chung `encryption_key` của Frappe.
    - Báo lỗi cứng khi chạy trong Frappe hoặc khi `LINHX_ENV=production` mà thiếu cấu hình khoá.
    """
    for ten_env in ("LINHX_OTP_KHOA_BI_MAT", "LINHX_OTP_SECRET", "LINHX_OTP_HMAC_KEY"):
        tu_env = os.environ.get(ten_env)
        if isinstance(tu_env, str) and tu_env.strip():
            return tu_env.strip().encode("utf-8")

    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is not None:
        conf = getattr(frappe_mod, "conf", None)
        if conf is not None and hasattr(conf, "get"):
            for ten_khoa in ("otp_khoa_bi_mat", "linhx_otp_khoa_bi_mat"):
                gia_tri = conf.get(ten_khoa)
                if isinstance(gia_tri, str) and gia_tri.strip():
                    return gia_tri.strip().encode("utf-8")
        if conf is not None:
            raise RuntimeError("Thiếu cấu hình khoá bí mật OTP riêng (otp_khoa_bi_mat) trong site_config")

    if _la_moi_truong_production():
        raise RuntimeError("Bắt buộc cấu hình LINHX_OTP_KHOA_BI_MAT trong môi trường production")

    khoa_tam = getattr(sys, _TEN_KHOA_TAM_TIEN_TRINH, None)
    if not isinstance(khoa_tam, bytes) or len(khoa_tam) < 32:
        khoa_tam = secrets.token_bytes(32)
        setattr(sys, _TEN_KHOA_TAM_TIEN_TRINH, khoa_tam)
    return khoa_tam


def _la_proxy_tin_cay(ip_ket_noi: str, ds_tin_cay: object) -> bool:
    """Kiểm tra `ip_ket_noi` có nằm trong danh sách `trusted_proxies` của máy chủ hay không."""
    if not ip_ket_noi or not isinstance(ds_tin_cay, (list, tuple, set, frozenset)):
        return False
    tap_tin_cay = {str(x).strip() for x in ds_tin_cay if str(x).strip()}
    return ip_ket_noi in tap_tin_cay


def _lay_ip_khach_tin_cay() -> str | None:
    """Lấy địa chỉ IP khách từ `frappe.local.request_ip` ở phía máy chủ.

    Chỉ đọc `X-Forwarded-For` hoặc `X-Real-IP` khi `request_ip` nằm trong danh sách
    `trusted_proxies` của cấu hình máy chủ (`frappe.conf.trusted_proxies`).
    Tuyệt đối không nhận IP từ tham số hàm hay dữ liệu do client gửi.
    """
    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is None:
        return None
    local_ctx = getattr(frappe_mod, "local", None)
    if local_ctx is None:
        return None
    ip_ket_noi = str(getattr(local_ctx, "request_ip", "") or "").strip()
    if not ip_ket_noi:
        return None
    try:
        ipaddress.ip_address(ip_ket_noi)
    except ValueError:
        return None

    conf = getattr(frappe_mod, "conf", None)
    ds_tin_cay = conf.get("trusted_proxies") if hasattr(conf, "get") else None
    req = getattr(local_ctx, "request", None)
    headers = getattr(req, "headers", None) if req is not None else None
    if headers is not None and hasattr(headers, "get") and _la_proxy_tin_cay(ip_ket_noi, ds_tin_cay):
        xff = str(headers.get("X-Forwarded-For") or "").strip()
        if xff:
            cac_ip = [phan.strip() for phan in xff.split(",") if phan.strip()]
            for ung_vien in reversed(cac_ip):
                try:
                    ipaddress.ip_address(ung_vien)
                except ValueError:
                    continue
                if not _la_proxy_tin_cay(ung_vien, ds_tin_cay) or ung_vien == cac_ip[0]:
                    return ung_vien
        x_real = str(headers.get("X-Real-IP") or "").strip()
        if x_real:
            try:
                ipaddress.ip_address(x_real)
                return x_real
            except ValueError:
                pass
    return ip_ket_noi


def _lay_db_frappe():
    """Lấy kết nối `frappe.db` khi có đầy đủ giao diện giao dịch SQL (`sql`, `commit`, `rollback`)."""
    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is None:
        return None
    db = getattr(frappe_mod, "db", None)
    if db is None:
        return None
    if not (
        callable(getattr(db, "sql", None))
        and callable(getattr(db, "commit", None))
        and callable(getattr(db, "rollback", None))
    ):
        return None
    return db


def _so_dong_anh_huong(db) -> int:
    """Lấy số dòng bị ảnh hưởng của câu lệnh UPDATE/INSERT liền trước qua `frappe.db.sql`.

    Nếu không xác định được số dòng ảnh hưởng thì trả 0 để thất bại theo hướng đóng (fail-closed).
    """
    try:
        kq = db.sql("SELECT ROW_COUNT() AS so_dong", as_dict=True)
    except Exception:
        return 0
    if isinstance(kq, int) and not isinstance(kq, bool):
        return kq
    if isinstance(kq, (list, tuple)) and len(kq) == 1:
        dong = kq[0]
        if isinstance(dong, dict) and "so_dong" in dong:
            val = dong["so_dong"]
            if isinstance(val, int) and not isinstance(val, bool):
                return val
            if isinstance(val, str) and val.isdigit():
                return int(val)
        elif isinstance(dong, (list, tuple)) and len(dong) == 1:
            val = dong[0]
            if isinstance(val, int) and not isinstance(val, bool):
                return val
            if isinstance(val, str) and val.isdigit():
                return int(val)
    return 0


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
    """Giữ lại các mốc thời gian nằm trong cửa sổ 1 giờ gần nhất."""
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


def _ghi_chi_muc_ip(bang_ip: dict[str, list[str]], ip_chuan: str, ds_moi: list[str]) -> None:
    if ip_chuan not in bang_ip and len(bang_ip) >= TOI_DA_KHOA_CHI_MUC_IP:
        bang_ip.pop(next(iter(bang_ip)), None)
    bang_ip[ip_chuan] = ds_moi


def _parse_lich_su_json(chuoi_json: object) -> list[str]:
    if isinstance(chuoi_json, list):
        return [str(x) for x in chuoi_json if isinstance(x, str)]
    if isinstance(chuoi_json, str) and chuoi_json.strip():
        try:
            parsed = json.loads(chuoi_json)
            if isinstance(parsed, list):
                return [str(x) for x in parsed if isinstance(x, str)]
        except ValueError:
            return []
    return []


def _kiem_gioi_han_phat_theo_chi_muc(
    db,
    kho: dict | None,
    email_chuan: str,
    ip_tin_cay: str | None,
    thoi_diem: datetime,
) -> tuple[list[str], list[str]]:
    """Kiểm tra giới hạn phát mã mỗi giờ theo chỉ mục O(1) của email và IP (không duyệt toàn bộ kho)."""
    if db is not None:
        dong_email = db.sql(
            "SELECT `lich_su_phat_json` FROM `tabLX OTP` WHERE `email` = %s LIMIT 10",
            (email_chuan,),
            as_dict=True,
        )
        ds_email: list[str] = []
        for d in dong_email or []:
            if isinstance(d, dict):
                ds_email.extend(_loc_lich_su_trong_gio(_parse_lich_su_json(d.get("lich_su_phat_json")), thoi_diem))
    elif isinstance(kho, dict):
        chi_muc_email = kho.get("_chi_muc_email")
        ds_raw = chi_muc_email.get(email_chuan, []) if isinstance(chi_muc_email, dict) else []
        ds_email = _loc_lich_su_trong_gio(list(ds_raw) if isinstance(ds_raw, list) else [], thoi_diem)
    else:
        ds_email = []

    if len(ds_email) >= GIOI_HAN_PHAT_MOI_GIO_EMAIL:
        raise ValueError(THONG_BAO_TU_CHOI_PHAT_MA)

    ds_ip: list[str] = []
    if ip_tin_cay:
        ds_ip = _loc_lich_su_trong_gio(_CHI_MUC_PHAT_IP.get(ip_tin_cay, []), thoi_diem)
        if db is not None:
            dong_ip = db.sql(
                "SELECT `lich_su_phat_json` FROM `tabLX OTP` WHERE `ip_cuoi` = %s LIMIT 20",
                (ip_tin_cay,),
                as_dict=True,
            )
            ds_ip_db: list[str] = []
            for d in dong_ip or []:
                if isinstance(d, dict):
                    ds_ip_db.extend(_loc_lich_su_trong_gio(_parse_lich_su_json(d.get("lich_su_phat_json")), thoi_diem))
            if len(ds_ip_db) > len(ds_ip):
                ds_ip = ds_ip_db
        if len(ds_ip) >= GIOI_HAN_PHAT_MOI_GIO_IP:
            raise ValueError(THONG_BAO_TU_CHOI_PHAT_MA)

    return ds_email, ds_ip


def _doc_ban_ghi_db_for_update(db, khoa: str) -> dict | None:
    """Đọc và khoá dòng `tabLX OTP` bằng `SELECT ... FOR UPDATE` trong giao dịch DB."""
    dong = db.sql(
        "SELECT `name`, `khoa_kenh`, `email`, `muc_dich`, `ma_bam`, `tao_luc`, "
        "`cap_nhat_luc`, `het_han_luc`, `so_lan_sai`, `da_dung`, `khoa_den`, "
        "`lich_su_phat_json`, `ip_cuoi` "
        "FROM `tabLX OTP` WHERE `khoa_kenh` = %s FOR UPDATE",
        (khoa,),
        as_dict=True,
    )
    if isinstance(dong, (list, tuple)) and dong and isinstance(dong[0], dict):
        d = dict(dong[0])
        d["da_dung"] = bool(int(d.get("da_dung") or 0))
        d["so_lan_sai"] = int(d.get("so_lan_sai") or 0)
        d["lich_su_phat"] = _parse_lich_su_json(d.get("lich_su_phat_json"))
        return d
    return None


def _phat_ma(
    kho: dict | None,
    email: str,
    muc_dich: str,
    luc: str | None = None,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], object] | None = None,
) -> dict:
    """Hàm nội bộ phát mã OTP cho kênh `(email, muc_dich)`."""
    db = _lay_db_frappe()
    if db is None and not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict hoặc có kết nối cơ sở dữ liệu Frappe")
    if kho is not None and not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")
    if gui_mail is not None and not callable(gui_mail):
        raise ValueError("gui_mail phải là hàm gọi được")

    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    ip_tin_cay = _lay_ip_khach_tin_cay()
    luc_hieu_luc = _gio_may_chu() if luc is None else luc
    thoi_diem = _phan_tich_luc(luc_hieu_luc)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    with _KHOA_GIAO_DICH:
        try:
            ban_ghi_cu = _doc_ban_ghi_db_for_update(db, khoa) if db is not None else kho.get(khoa)  # type: ignore[union-attr]
            so_lan_sai_ke_thua = 0
            khoa_den_ke_thua: str | None = None
            lich_su_kenh_cu: list[str] = []

            if isinstance(ban_ghi_cu, dict):
                tao_luc_cu = ban_ghi_cu.get("tao_luc")
                cap_nhat_cu = ban_ghi_cu.get("cap_nhat_luc") or tao_luc_cu
                if cap_nhat_cu and thoi_diem < _phan_tich_luc(str(cap_nhat_cu)):
                    raise ValueError(THONG_BAO_TU_CHOI_PHAT_MA)

                khoa_den_cu = ban_ghi_cu.get("khoa_den")
                da_man_han_khoa = False
                if khoa_den_cu:
                    if thoi_diem < _phan_tich_luc(str(khoa_den_cu)):
                        raise ValueError(THONG_BAO_TU_CHOI_PHAT_MA)
                    da_man_han_khoa = True

                if tao_luc_cu:
                    giay_da_qua = (thoi_diem - _phan_tich_luc(str(tao_luc_cu))).total_seconds()
                    if giay_da_qua < CHO_PHAT_LAI_GIAY:
                        raise ValueError(THONG_BAO_TU_CHOI_PHAT_MA)

                da_dung_cu = bool(ban_ghi_cu.get("da_dung"))
                if not da_dung_cu and not da_man_han_khoa:
                    so_lan_sai_ke_thua = int(ban_ghi_cu.get("so_lan_sai") or 0)
                    khoa_den_ke_thua = str(khoa_den_cu) if khoa_den_cu else None

                lich_su_kenh_cu = _loc_lich_su_trong_gio(
                    list(ban_ghi_cu.get("lich_su_phat") or []),
                    thoi_diem,
                )

            ds_email_1h, ds_ip_1h = _kiem_gioi_han_phat_theo_chi_muc(
                db,
                kho,
                email_chuan,
                ip_tin_cay,
                thoi_diem,
            )

            ma_chuan = _sinh_ma_otp() if ma_otp is None else _chuan_hoa_ma_otp(ma_otp)
            ma_bam = bam_ma(email_chuan, muc_dich_chuan, ma_chuan)
            tao_luc_str = _dinh_dang_luc(thoi_diem)
            het_han_str = _dinh_dang_luc(thoi_diem + timedelta(minutes=HAN_PHUT))
            lich_su_moi = lich_su_kenh_cu + [tao_luc_str]
            lich_su_json = json.dumps(lich_su_moi, ensure_ascii=False)

            if db is not None:
                if isinstance(ban_ghi_cu, dict):
                    db.sql(
                        "UPDATE `tabLX OTP` "
                        "SET `email` = %s, `muc_dich` = %s, `ma_bam` = %s, `tao_luc` = %s, "
                        "`cap_nhat_luc` = %s, `het_han_luc` = %s, `so_lan_sai` = %s, "
                        "`da_dung` = 0, `khoa_den` = %s, `lich_su_phat_json` = %s, `ip_cuoi` = %s "
                        "WHERE `khoa_kenh` = %s",
                        (
                            email_chuan,
                            muc_dich_chuan,
                            ma_bam,
                            tao_luc_str,
                            tao_luc_str,
                            het_han_str,
                            so_lan_sai_ke_thua,
                            khoa_den_ke_thua,
                            lich_su_json,
                            ip_tin_cay,
                            khoa,
                        ),
                    )
                else:
                    db.sql(
                        "INSERT INTO `tabLX OTP` "
                        "(`name`, `khoa_kenh`, `email`, `muc_dich`, `ma_bam`, `tao_luc`, "
                        "`cap_nhat_luc`, `het_han_luc`, `so_lan_sai`, `da_dung`, `khoa_den`, "
                        "`lich_su_phat_json`, `ip_cuoi`) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s)",
                        (
                            khoa,
                            khoa,
                            email_chuan,
                            muc_dich_chuan,
                            ma_bam,
                            tao_luc_str,
                            tao_luc_str,
                            het_han_str,
                            so_lan_sai_ke_thua,
                            khoa_den_ke_thua,
                            lich_su_json,
                            ip_tin_cay,
                        ),
                    )
                if _so_dong_anh_huong(db) != 1:
                    db.rollback()
                    raise RuntimeError("Không lưu được bản ghi OTP vào cơ sở dữ liệu")
                db.commit()
        except Exception:
            if db is not None:
                db.rollback()
            raise

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
        if isinstance(kho, dict):
            kho[khoa] = ban_ghi_moi
            chi_muc_email = kho.setdefault("_chi_muc_email", {})
            if isinstance(chi_muc_email, dict):
                chi_muc_email[email_chuan] = ds_email_1h + [tao_luc_str]

        if ip_tin_cay:
            _ghi_chi_muc_ip(_CHI_MUC_PHAT_IP, ip_tin_cay, ds_ip_1h + [tao_luc_str])

    if gui_mail is not None:
        gui_mail(email_chuan, ma_chuan, muc_dich_chuan)

    return {
        "email": email_chuan,
        "muc_dich": muc_dich_chuan,
        "het_han_luc": het_han_str,
    }


def _xac_minh(
    kho: dict | None,
    email: str,
    muc_dich: str,
    ma_nhap: str,
    luc: str | None = None,
) -> dict:
    """Hàm nội bộ xác minh mã OTP theo giao dịch nguyên tử và so sánh hằng thời gian."""
    db = _lay_db_frappe()
    if db is None and not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict hoặc có kết nối cơ sở dữ liệu Frappe")
    if kho is not None and not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")

    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    ip_tin_cay = _lay_ip_khach_tin_cay()
    luc_hieu_luc = _gio_may_chu() if luc is None else luc
    thoi_diem = _phan_tich_luc(luc_hieu_luc)
    luc_str = _dinh_dang_luc(thoi_diem)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    ma_nhap_str = ma_nhap.strip() if isinstance(ma_nhap, str) else ""
    ma_hop_le = bool(ma_nhap_str) and len(ma_nhap_str) <= DO_DAI_MA_TOI_DA
    ma_de_bam = ma_nhap_str if ma_hop_le else "000000"
    bam_nhap = bam_ma(email_chuan, muc_dich_chuan, ma_de_bam)

    with _KHOA_GIAO_DICH:
        if ip_tin_cay:
            ds_sai_ip = _loc_lich_su_trong_gio(_CHI_MUC_SAI_IP.get(ip_tin_cay, []), thoi_diem)
            if len(ds_sai_ip) >= GIOI_HAN_SAI_MOI_GIO_IP:
                hmac.compare_digest(_BAM_GIA_HANG_THOI_GIAN.encode("utf-8"), bam_nhap.encode("utf-8"))
                return {"ok": False, "ly_do": "bi_khoa"}
        else:
            ds_sai_ip = []

        ban_ghi = _doc_ban_ghi_db_for_update(db, khoa) if db is not None else kho.get(khoa)  # type: ignore[union-attr]
        if not isinstance(ban_ghi, dict):
            hmac.compare_digest(_BAM_GIA_HANG_THOI_GIAN.encode("utf-8"), bam_nhap.encode("utf-8"))
            if db is not None:
                db.rollback()
            if ip_tin_cay:
                _ghi_chi_muc_ip(_CHI_MUC_SAI_IP, ip_tin_cay, ds_sai_ip + [luc_str])
            return {"ok": False, "ly_do": "sai_ma"}

        ma_bam_luu = str(ban_ghi.get("ma_bam") or "")
        bam_doi_chieu = ma_bam_luu if len(ma_bam_luu) == 64 else _BAM_GIA_HANG_THOI_GIAN
        khop = (
            hmac.compare_digest(bam_doi_chieu.encode("utf-8"), bam_nhap.encode("utf-8"))
            and ma_hop_le
            and bool(ma_bam_luu)
        )

        khoa_den = ban_ghi.get("khoa_den")
        if khoa_den and thoi_diem < _phan_tich_luc(str(khoa_den)):
            if db is not None:
                db.rollback()
            return {"ok": False, "ly_do": "bi_khoa"}

        tao_luc = ban_ghi.get("tao_luc")
        cap_nhat_luc = ban_ghi.get("cap_nhat_luc") or tao_luc
        if (tao_luc and thoi_diem < _phan_tich_luc(str(tao_luc))) or (
            cap_nhat_luc and thoi_diem < _phan_tich_luc(str(cap_nhat_luc))
        ):
            if db is not None:
                db.rollback()
            if khoa_den:
                return {"ok": False, "ly_do": "bi_khoa"}
            return {"ok": False, "ly_do": "het_han"}

        if bool(ban_ghi.get("da_dung")) is True:
            if db is not None:
                db.rollback()
            return {"ok": False, "ly_do": "da_dung"}

        het_han_luc = ban_ghi.get("het_han_luc")
        if not het_han_luc or thoi_diem > _phan_tich_luc(str(het_han_luc)):
            if db is not None:
                db.rollback()
            return {"ok": False, "ly_do": "het_han"}

        so_lan_sai_cu = int(ban_ghi.get("so_lan_sai") or 0)
        if so_lan_sai_cu >= SAI_TOI_DA:
            if db is not None:
                db.rollback()
            return {"ok": False, "ly_do": "bi_khoa"}

        if not khop:
            so_lan_sai_moi = so_lan_sai_cu + 1
            khoa_den_moi = (
                _dinh_dang_luc(thoi_diem + timedelta(minutes=KHOA_PHUT))
                if so_lan_sai_moi >= SAI_TOI_DA
                else None
            )
            if db is not None:
                db.sql(
                    "UPDATE `tabLX OTP` "
                    "SET `so_lan_sai` = %s, `khoa_den` = %s, `cap_nhat_luc` = %s "
                    "WHERE `khoa_kenh` = %s AND `da_dung` = 0 AND `so_lan_sai` = %s AND `so_lan_sai` < %s",
                    (so_lan_sai_moi, khoa_den_moi, luc_str, khoa, so_lan_sai_cu, SAI_TOI_DA),
                )
                if _so_dong_anh_huong(db) != 1:
                    db.rollback()
                    return {"ok": False, "ly_do": "bi_khoa"}
                db.commit()

            ban_ghi["so_lan_sai"] = so_lan_sai_moi
            if khoa_den_moi is not None:
                ban_ghi["khoa_den"] = khoa_den_moi
            ban_ghi["cap_nhat_luc"] = luc_str
            if isinstance(kho, dict):
                kho[khoa] = ban_ghi
            if ip_tin_cay:
                _ghi_chi_muc_ip(_CHI_MUC_SAI_IP, ip_tin_cay, ds_sai_ip + [luc_str])

            if so_lan_sai_moi >= SAI_TOI_DA:
                return {"ok": False, "ly_do": "bi_khoa"}
            return {"ok": False, "ly_do": "sai_ma"}

        if db is not None:
            db.sql(
                "UPDATE `tabLX OTP` "
                "SET `da_dung` = 1, `so_lan_sai` = 0, `cap_nhat_luc` = %s "
                "WHERE `khoa_kenh` = %s AND `da_dung` = 0 AND `so_lan_sai` = %s AND `so_lan_sai` < %s",
                (luc_str, khoa, so_lan_sai_cu, SAI_TOI_DA),
            )
            if _so_dong_anh_huong(db) != 1:
                db.rollback()
                return {"ok": False, "ly_do": "da_dung"}
            db.commit()

        ban_ghi["da_dung"] = True
        ban_ghi["so_lan_sai"] = 0
        ban_ghi["cap_nhat_luc"] = luc_str
        if isinstance(kho, dict):
            kho[khoa] = ban_ghi
        return {"ok": True, "ly_do": None}


def phat_ma(
    kho: dict,
    email: str,
    muc_dich: str,
    luc: str,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], object] | None = None,
) -> dict:
    """Phát mã OTP cho kênh `(email, muc_dich)` tại thời điểm `luc` (phục vụ kiểm thử / gọi nội bộ).

    Trong ngữ cảnh HTTP request (`frappe.local.request` tồn tại), hàm này bị chặn hoàn toàn
    để không cho phép bất kỳ API wrapper nào truyền `luc` hoặc `ma_otp` từ phía client;
    tầng API bắt buộc gọi `phat_ma_tu_api`.
    """
    if _dang_trong_request_http():
        raise PermissionError("Trong HTTP request chỉ được phép gọi phat_ma_tu_api")
    return _phat_ma(
        kho=kho,
        email=email,
        muc_dich=muc_dich,
        luc=luc,
        ma_otp=ma_otp,
        gui_mail=gui_mail,
    )


def xac_minh(
    kho: dict,
    email: str,
    muc_dich: str,
    ma_nhap: str,
    luc: str,
) -> dict:
    """Xác minh mã OTP `ma_nhap` cho kênh `(email, muc_dich)` tại thời điểm `luc` (kiểm thử / nội bộ).

    Trong ngữ cảnh HTTP request (`frappe.local.request` tồn tại), hàm này bị chặn hoàn toàn
    để không cho phép bất kỳ API wrapper nào truyền `luc` từ phía client;
    tầng API bắt buộc gọi `xac_minh_tu_api`.
    """
    if _dang_trong_request_http():
        raise PermissionError("Trong HTTP request chỉ được phép gọi xac_minh_tu_api")
    return _xac_minh(
        kho=kho,
        email=email,
        muc_dich=muc_dich,
        ma_nhap=ma_nhap,
        luc=luc,
    )


def phat_ma_tu_api(
    email: str,
    muc_dich: str,
    gui_mail: Callable[[str, str, str], object] | None = None,
) -> dict:
    """Điểm vào công khai cho tầng API: lưu trong DB `tabLX OTP`, tự lấy giờ máy chủ,
    tự sinh mã OTP và tự trích xuất IP khách từ proxy tin cậy (không nhận `luc`, `ma_otp`, `ip`, `kho`).
    """
    if _lay_db_frappe() is None:
        raise RuntimeError("phat_ma_tu_api yêu cầu kết nối cơ sở dữ liệu Frappe (tabLX OTP)")
    return _phat_ma(
        kho=None,
        email=email,
        muc_dich=muc_dich,
        luc=_gio_may_chu(),
        ma_otp=None,
        gui_mail=gui_mail,
    )


def xac_minh_tu_api(
    email: str,
    muc_dich: str,
    ma_nhap: str,
) -> dict:
    """Điểm vào công khai cho tầng API: truy vấn và cập nhật nguyên tử DB `tabLX OTP`,
    tự lấy giờ máy chủ và tự trích xuất IP khách từ proxy tin cậy (không nhận `luc`, `ip`, `kho`).
    """
    if _lay_db_frappe() is None:
        raise RuntimeError("xac_minh_tu_api yêu cầu kết nối cơ sở dữ liệu Frappe (tabLX OTP)")
    return _xac_minh(
        kho=None,
        email=email,
        muc_dich=muc_dich,
        ma_nhap=ma_nhap,
        luc=_gio_may_chu(),
    )
