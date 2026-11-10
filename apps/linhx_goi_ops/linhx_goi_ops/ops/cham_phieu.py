"""Logic thuần Python chấm phiếu Agy tự động: chạy rào vùng và cổng kiểm trước,
chỉ khi cả hai đều xanh mới gọi Claude chấm đúng 1 lần; nếu Claude hết hạn mức
thì đánh dấu lỗi máy (không tính lần chưa đạt và giữ trạng thái 'nop').
"""
from __future__ import annotations

from collections.abc import Callable

MAU_HET_HAN_MUC = (
    "you've hit your weekly limit",
    "hit your weekly limit",
    "hit your daily limit",
    "weekly limit",
    "daily limit",
    "usage limit",
    "rate_limit",
    "rate limit",
    "overloaded_error",
)


def la_loi_het_han_muc(van_ban: object) -> bool:
    """Kiểm tra thông báo nhận xét hoặc ngoại lệ có báo hết hạn mức / quá tải của Claude không."""
    chu = str(van_ban or "").lower()
    if not chu:
        return False
    return any(mau in chu for mau in MAU_HET_HAN_MUC)


def cham_phieu(
    phieu: dict,
    chay_rao: Callable[[dict], dict],
    chay_cong_kiem: Callable[[dict], dict],
    goi_claude: Callable[[dict], dict],
) -> dict:
    """Chấm phiếu tự động theo hợp đồng O6."""
    if not isinstance(phieu, dict):
        raise ValueError("Phiếu phải là kiểu dict")
    if not callable(chay_rao) or not callable(chay_cong_kiem) or not callable(goi_claude):
        raise ValueError("chay_rao, chay_cong_kiem và goi_claude phải là hàm gọi được (callable)")

    so_lan_cu = int(phieu.get("so_lan_chua_dat") or 0)

    kq_rao = chay_rao(phieu)
    if not isinstance(kq_rao, dict):
        kq_rao = {"ok": bool(kq_rao), "loi": []}
    rao_ok = bool(kq_rao.get("ok"))

    kq_cong = chay_cong_kiem(phieu)
    if not isinstance(kq_cong, dict):
        kq_cong = {"ok": bool(kq_cong), "dau_ra": ""}
    cong_ok = bool(kq_cong.get("ok"))

    if not rao_ok or not cong_ok:
        ds_ly_do: list[str] = []
        if not rao_ok:
            loi_rao = kq_rao.get("loi")
            if isinstance(loi_rao, (list, tuple)):
                cac_loi = [str(x).strip() for x in loi_rao if str(x).strip()]
                ds_ly_do.append("; ".join(cac_loi) if cac_loi else "Trượt rào vùng")
            elif isinstance(loi_rao, str) and loi_rao.strip():
                ds_ly_do.append(loi_rao.strip())
            else:
                ds_ly_do.append("Trượt rào vùng")
        if not cong_ok:
            dau_ra = str(kq_cong.get("dau_ra") or kq_cong.get("loi") or "").strip()
            ds_ly_do.append(dau_ra if dau_ra else "Trượt cổng kiểm")

        ly_do_tra = "\n".join(ds_ly_do)
        phieu.update(
            {
                "trang_thai": "tra",
                "ket_luan": "CHUA_DAT",
                "loi_may": False,
                "so_lan_chua_dat": so_lan_cu + 1,
                "ly_do_tra": ly_do_tra,
                "nhan_xet": ly_do_tra,
            }
        )
        return phieu

    try:
        kq_claude = goi_claude(phieu)
    except Exception as exc:
        thong_bao_loi = str(exc)
        if la_loi_het_han_muc(thong_bao_loi):
            phieu.update(
                {
                    "trang_thai": "nop",
                    "ket_luan": "LOI_MAY",
                    "loi_may": True,
                    "so_lan_chua_dat": so_lan_cu,
                    "nhan_xet": thong_bao_loi,
                }
            )
            return phieu
        raise

    if not isinstance(kq_claude, dict):
        kq_claude = {"ket_luan": "CHUA_DAT", "nhan_xet": str(kq_claude or "")}

    ket_luan_raw = str(kq_claude.get("ket_luan") or "").strip()
    nhan_xet = str(kq_claude.get("nhan_xet") or "").strip()

    if la_loi_het_han_muc(nhan_xet) or la_loi_het_han_muc(ket_luan_raw):
        phieu.update(
            {
                "trang_thai": "nop",
                "ket_luan": "LOI_MAY",
                "loi_may": True,
                "so_lan_chua_dat": so_lan_cu,
                "nhan_xet": nhan_xet,
            }
        )
        return phieu

    if ket_luan_raw == "DAT":
        phieu.update(
            {
                "trang_thai": "dat",
                "ket_luan": "DAT",
                "loi_may": False,
                "so_lan_chua_dat": so_lan_cu,
                "nhan_xet": nhan_xet,
            }
        )
        return phieu

    ly_do = nhan_xet or "CHUA_DAT"
    phieu.update(
        {
            "trang_thai": "tra",
            "ket_luan": "CHUA_DAT",
            "loi_may": False,
            "so_lan_chua_dat": so_lan_cu + 1,
            "ly_do_tra": ly_do,
            "nhan_xet": nhan_xet,
        }
    )
    return phieu
