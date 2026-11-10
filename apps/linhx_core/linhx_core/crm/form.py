"""Xử lý dữ liệu form Trang BU: chuẩn hoá, gộp trùng Người, tạo Cơ hội và ghi sổ Đồng ý.

Tham khảo luồng CRM và tuân thủ từ:
- nguon/03-opc-os/modules/04_quan_ly_user/module.py
- nguon/03-opc-os/modules/09_tuan_thu/module.py
"""
from __future__ import annotations

from linhx_core.crm import dong_y, gop_trung

DO_DAI_TOI_DA_HO_TEN = 120
DO_DAI_TOI_DA_DIEN_THOAI = 20
DO_DAI_TOI_DA_EMAIL = 254
DO_DAI_TOI_DA_NHU_CAU = 2000
TRUONG_HONEYPOT = ("website", "hp_url", "trap_field")


def _la_dong_y_true(gia_tri: object) -> bool:
    """Kiểm tra giá trị đồng ý có thực sự là True (hoặc 1/'true'/'1')."""
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, int):
        return gia_tri == 1
    if isinstance(gia_tri, str):
        return gia_tri.strip().lower() in ("1", "true", "yes", "on")
    return False


def _kiem_tra_dau_vao(du_lieu: dict) -> tuple[str, str, str, str]:
    """Kiểm tra honeypot và giới hạn độ dài các trường đầu vào trước khi chuẩn hoá/truy vấn."""
    for tr_hp in TRUONG_HONEYPOT:
        if str(du_lieu.get(tr_hp) or "").strip():
            raise ValueError("Phát hiện gửi tự động không hợp lệ")

    ho_ten = str(du_lieu.get("ho_ten") or "").strip()
    dien_thoai = str(du_lieu.get("dien_thoai") or "").strip()
    email = str(du_lieu.get("email") or "").strip()
    nhu_cau = str(du_lieu.get("nhu_cau") or "").strip()

    if len(ho_ten) > DO_DAI_TOI_DA_HO_TEN:
        raise ValueError(f"Họ tên vượt quá độ dài tối đa ({DO_DAI_TOI_DA_HO_TEN} ký tự)")
    if len(dien_thoai) > DO_DAI_TOI_DA_DIEN_THOAI:
        raise ValueError(f"Số điện thoại vượt quá độ dài tối đa ({DO_DAI_TOI_DA_DIEN_THOAI} ký tự)")
    if len(email) > DO_DAI_TOI_DA_EMAIL:
        raise ValueError(f"Email vượt quá độ dài tối đa ({DO_DAI_TOI_DA_EMAIL} ký tự)")
    if len(nhu_cau) > DO_DAI_TOI_DA_NHU_CAU:
        raise ValueError(f"Nhu cầu vượt quá độ dài tối đa ({DO_DAI_TOI_DA_NHU_CAU} ký tự)")

    return ho_ten, dien_thoai, email, nhu_cau


def da_rut_dong_y(
    so_dong_y: list[dict],
    dinh_danh: str | list[str] | set[str],
    muc_dich: str,
) -> bool:
    """Kiểm tra xem người dùng đã có bản ghi đồng ý cho `muc_dich` nhưng trạng thái hiệu lực
    mới nhất là rút đồng ý (`dong_y=0` / `False`).
    """
    if not so_dong_y:
        return False
    if isinstance(dinh_danh, str):
        tap_ma = {dinh_danh.strip()} if dinh_danh.strip() else set()
    else:
        tap_ma = {str(x).strip() for x in (dinh_danh or []) if str(x or "").strip()}
    if not tap_ma:
        return False

    ma_dai_dien = next(iter(tap_ma))
    so_quy_doi: list[dict] = []
    co_dong = False
    for d in so_dong_y:
        if not isinstance(d, dict):
            continue
        ma_d = dong_y._ma_nguoi(d.get("nguoi"))
        if ma_d in tap_ma:
            if str(d.get("trang_thai") or "").strip() == "cho_xac_minh":
                continue
            if d.get("muc_dich") == muc_dich:
                co_dong = True
            ban_sao = dict(d)
            ban_sao["nguoi"] = ma_dai_dien
            so_quy_doi.append(ban_sao)

    if not co_dong:
        return False
    return not dong_y.hieu_luc(so_quy_doi, ma_dai_dien, muc_dich)


def _can_ghi_dong_y(
    so_dong_y: list[dict],
    dinh_danh: str | list[str] | set[str],
    muc_dich: str,
    da_co_nguoi: bool,
) -> bool:
    """Chỉ ghi dòng đồng ý mới khi người dùng chưa rút đồng ý (`dong_y=0`) cho `muc_dich` này."""
    if da_co_nguoi and da_rut_dong_y(so_dong_y, dinh_danh, muc_dich):
        return False
    return True


def xu_ly(
    du_lieu: dict,
    ds_nguoi: list[dict],
    so_dong_y: list[dict],
    luc: str,
    nguon: str,
) -> dict:
    """Xử lý dữ liệu form liên hệ từ Trang BU (thuần Python).

    - Bắt buộc có ít nhất `dien_thoai` hoặc `email` hợp lệ; thiếu cả hai -> ValueError.
    - Bắt buộc `dong_y_lien_he` là True; nếu không -> ValueError (không lưu gì).
    - Kiểm tra honeypot và giới hạn độ dài trường đầu vào.
    - Không nhận `nguon` từ `du_lieu` (client); chỉ dùng tham số `nguon` do server truyền vào.
    - Gộp trùng Người qua `gop_trung.gop` (giữ nguyên dữ liệu cũ, không ghi đè bằng dữ liệu form).
    - Tạo dict Cơ hội (`trang_thai="moi"`).
    - Ghi sổ Đồng ý một bước theo ô khách tick qua `dong_y.ghi`: luôn xét `lien_he=True` và
      `marketing=True` khi tick; nếu Người đã có và mục đích đó đang ở trạng thái rút đồng ý
      (`dong_y=0`) thì không ghi đè dòng rút đồng ý.
    """
    if not isinstance(du_lieu, dict):
        raise ValueError("Dữ liệu form không hợp lệ")

    if not _la_dong_y_true(du_lieu.get("dong_y_lien_he")):
        raise ValueError("Khách hàng phải đồng ý liên hệ trước khi gửi form")

    ho_ten, dien_thoai, email, nhu_cau = _kiem_tra_dau_vao(du_lieu)
    dt_chuan = gop_trung.chuan_hoa_dien_thoai(dien_thoai)
    em_chuan = gop_trung.chuan_hoa_email(email)
    if not dt_chuan and not em_chuan:
        raise ValueError("Phải cung cấp ít nhất số điện thoại hoặc email")

    nguon_str = str(nguon or "").strip() or "trang-bu"
    luc_str = str(luc or "").strip() or dong_y.bay_gio()

    ban_moi: dict = {
        "ho_ten": ho_ten,
        "dien_thoai": dien_thoai,
        "email": email,
    }

    khoa_moi = gop_trung.khoa_gop(ban_moi)
    da_co_nguoi = any(
        isinstance(cu, dict) and bool(gop_trung.khoa_gop(cu) & khoa_moi)
        for cu in (ds_nguoi or [])
    )

    ds_nguoi_moi = gop_trung.gop(ds_nguoi or [], ban_moi)

    nguoi_ket_qua: dict | None = None
    for muc in ds_nguoi_moi:
        if isinstance(muc, dict) and (gop_trung.khoa_gop(muc) & khoa_moi):
            nguoi_ket_qua = muc
            break
    if nguoi_ket_qua is None:
        nguoi_ket_qua = ds_nguoi_moi[-1]

    if not str(nguoi_ket_qua.get("name") or "").strip():
        ma_suy_ra = ""
        if da_co_nguoi and so_dong_y:
            cac_ma_so = {
                dong_y._ma_nguoi(d.get("nguoi"))
                for d in so_dong_y
                if isinstance(d, dict) and dong_y._ma_nguoi(d.get("nguoi"))
            }
            if len(cac_ma_so) == 1:
                ma_suy_ra = next(iter(cac_ma_so))
        nguoi_ket_qua["name"] = ma_suy_ra or f"NGUOI-{dt_chuan or em_chuan}"

    ma_nguoi = str(nguoi_ket_qua["name"]).strip()
    cac_dinh_danh = {
        x
        for x in (
            ma_nguoi,
            str(nguoi_ket_qua.get("dien_thoai") or "").strip(),
            str(nguoi_ket_qua.get("email") or "").strip(),
            dt_chuan,
            dien_thoai,
            em_chuan,
            email,
        )
        if x
    }
    so_dong_y_moi = [dict(d) if isinstance(d, dict) else d for d in (so_dong_y or [])]

    if _can_ghi_dong_y(so_dong_y_moi, cac_dinh_danh, "lien_he", da_co_nguoi):
        so_dong_y_moi = dong_y.ghi(
            so_dong_y_moi,
            nguoi_ket_qua,
            "lien_he",
            True,
            luc_str,
            nguon_str,
        )

    if _la_dong_y_true(du_lieu.get("dong_y_marketing")):
        if (
            _can_ghi_dong_y(so_dong_y_moi, cac_dinh_danh, "marketing", da_co_nguoi)
            and not dong_y.hieu_luc(so_dong_y_moi, ma_nguoi, "marketing")
        ):
            so_dong_y_moi = dong_y.ghi(
                so_dong_y_moi,
                nguoi_ket_qua,
                "marketing",
                True,
                luc_str,
                nguon_str,
                trang_thai="cho_xac_minh",
            )

    co_hoi_moi = {
        "nguoi": ma_nguoi,
        "nhu_cau": nhu_cau,
        "nguon": nguon_str,
        "trang_thai": "moi",
    }

    return {
        "ds_nguoi": ds_nguoi_moi,
        "nguoi": dict(nguoi_ket_qua),
        "co_hoi": co_hoi_moi,
        "so_dong_y": so_dong_y_moi,
    }
