"""Logic thuần Python cho API thợ nộp phiếu Agy: kiểm khoá thợ, chặn nộp phiếu của thợ khác (403),
lưu commit/nhánh/nhật ký/phút/token và chống tạo bản ghi trùng khi nộp lại cùng commit.
"""
from __future__ import annotations

from linhx_goi_ops.ops.keo_phieu import _KHOA_LUONG, xac_thuc_tho


def _chuan_phut(gia_tri: object) -> int | float:
    if isinstance(gia_tri, bool) or gia_tri is None:
        raise ValueError("phut phải là số không âm")
    if isinstance(gia_tri, int):
        if gia_tri < 0:
            raise ValueError("phut không được âm")
        return gia_tri
    try:
        so = float(gia_tri)
    except (TypeError, ValueError) as exc:
        raise ValueError("phut phải là số") from exc
    if so < 0:
        raise ValueError("phut không được âm")
    if so.is_integer() and isinstance(gia_tri, str) and "." not in gia_tri.strip():
        return int(so)
    return so


def _chuan_token(gia_tri: object) -> int:
    if isinstance(gia_tri, bool) or gia_tri is None:
        raise ValueError("token phải là số nguyên không âm")
    try:
        so = int(gia_tri)
    except (TypeError, ValueError) as exc:
        raise ValueError("token phải là số nguyên") from exc
    if so < 0:
        raise ValueError("token không được âm")
    return so


def nop_phieu(
    kho: dict,
    ma_tho: str,
    khoa_tran: str | None,
    du_lieu: dict,
    luc: str,
) -> tuple[int, dict]:
    """Xác thực thợ và ghi nhận kết quả nộp phiếu nguyên tử theo hợp đồng O3."""
    with _KHOA_LUONG:
        if not xac_thuc_tho(kho, ma_tho, khoa_tran):
            return 401, {"ok": False, "loi": "unauthorized"}

        if not isinstance(du_lieu, dict):
            return 400, {"ok": False, "loi": "du_lieu_khong_hop_le"}

        ma_tho_chuan = ma_tho.strip()
        ma_phieu = str(du_lieu.get("ma_phieu") or du_lieu.get("name") or "").strip()
        if not ma_phieu:
            return 404, {"ok": False, "loi": "khong_tim_thay_phieu"}

        ds_phieu = kho.get("phieu")
        if not isinstance(ds_phieu, list):
            ds_phieu = []

        phieu_muc_tieu: dict | None = None
        for p in ds_phieu:
            if isinstance(p, dict) and p.get("name") == ma_phieu:
                phieu_muc_tieu = p
                break

        if phieu_muc_tieu is None:
            return 404, {"ok": False, "loi": "khong_tim_thay_phieu"}

        tho_hien_tai = str(phieu_muc_tieu.get("tho") or "").strip()
        if tho_hien_tai != ma_tho_chuan:
            return 403, {"ok": False, "loi": "khong_phai_phieu_cua_tho"}

        commit_moi = str(du_lieu.get("commit") or "").strip()
        nhanh_moi = str(du_lieu.get("nhanh") or "").strip()
        nhat_ky_moi = str(du_lieu.get("nhat_ky") or "")

        try:
            phut_moi = _chuan_phut(du_lieu.get("phut", 0))
            token_moi = _chuan_token(du_lieu.get("token", 0))
        except ValueError as exc:
            return 400, {"ok": False, "loi": str(exc)}

        lan_nop = kho.setdefault("lan_nop", [])
        if not isinstance(lan_nop, list):
            lan_nop = []
            kho["lan_nop"] = lan_nop

        trang_thai_hien_tai = phieu_muc_tieu.get("trang_thai")
        commit_cu = str(phieu_muc_tieu.get("commit") or "").strip()

        if trang_thai_hien_tai == "nop" and commit_cu == commit_moi:
            return 200, {"ok": True, "trung": True, "phieu": dict(phieu_muc_tieu)}

        for b in lan_nop:
            if (
                isinstance(b, dict)
                and b.get("ma_phieu") == ma_phieu
                and b.get("tho") == ma_tho_chuan
                and str(b.get("commit") or "").strip() == commit_moi
            ):
                return 200, {"ok": True, "trung": True, "phieu": dict(phieu_muc_tieu)}

        if trang_thai_hien_tai not in ("giao", "nop"):
            return 400, {"ok": False, "loi": "trang_thai_khong_hop_le"}

        phieu_muc_tieu["trang_thai"] = "nop"
        phieu_muc_tieu["commit"] = commit_moi
        phieu_muc_tieu["nhanh"] = nhanh_moi
        phieu_muc_tieu["nhat_ky"] = nhat_ky_moi
        phieu_muc_tieu["phut"] = phut_moi
        phieu_muc_tieu["token"] = token_moi
        phieu_muc_tieu["nop_luc"] = luc

        lan_nop.append(
            {
                "ma_phieu": ma_phieu,
                "tho": ma_tho_chuan,
                "commit": commit_moi,
                "nhanh": nhanh_moi,
                "nhat_ky": nhat_ky_moi,
                "phut": phut_moi,
                "token": token_moi,
                "nop_luc": luc,
            }
        )

        return 200, {"ok": True, "trung": False, "phieu": dict(phieu_muc_tieu)}
