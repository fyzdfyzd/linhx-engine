"""F2: Đặt lịch gọi tư vấn từ Trang BU vào lịch người phụ trách.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/booking/dat_lich.py thuần Python (không import frappe ở đầu file):
    GIO_BAT_DAU = 8
    GIO_KET_THUC = 18
    dat_lich(ds_lich: list[dict], du_lieu: dict) -> list[dict]
        - du_lieu: {"nguoi": str, "phu_trach": str, "bat_dau": "YYYY-MM-DD HH:MM:SS", "phut": int = 30, "ghi_chu"?: str}
        - kiểm giờ làm việc (8:00 đến 18:00 giờ VN): giờ bắt đầu < 08:00:00 hoặc giờ kết thúc (bat_dau + phut) > 18:00:00
          -> raise ValueError
        - kiểm trùng giờ của cùng phu_trach (với các lịch có trang_thai != "huy"): nếu khoảng [bat_dau, ket_thuc)
          giao với lịch đã có của cùng phu_trach -> raise ValueError
        - trả danh sách lịch mới có thêm bản ghi {"nguoi", "phu_trach", "bat_dau", "ket_thuc", "phut", "trang_thai": "cho_goi", ...}
    viec_cho(ds_lich: list[dict], phu_trach: str | None = None) -> list[dict]
        lọc lịch có trang_thai == "cho_goi" (và đúng phu_trach nếu truyền vào), xếp bat_dau tăng dần
- apps/linhx_core/linhx_core/booking/api_booking.py:
    @frappe.whitelist(allow_guest=True, methods=["POST"]) `dat_lich_goi` (có giới hạn tần suất).
- trang-bu: có form[data-dat-lich] gửi POST tới /api/method/linhx_core.booking.api_booking.dat_lich_goi.
"""
import pytest

from _chung import CORE, TRANG_BU, khong_import_frappe_dau_file, nap_module


def _dl():
    return nap_module("linhx_core.booking.dat_lich", CORE)


def test_dat_trung_gio_bi_chan():
    """Tiêu chí: đặt trùng giờ bị chặn."""
    dl = _dl()
    ds = dl.dat_lich(
        [],
        {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 09:00:00", "phut": 30},
    )
    assert len(ds) == 1

    # Cùng người phụ trách, trùng hoàn toàn hoặc chồng một phần -> bị chặn
    for gio_trung in ("2026-11-10 09:00:00", "2026-11-10 09:15:00", "2026-11-10 08:45:00"):
        with pytest.raises(ValueError):
            dl.dat_lich(
                ds,
                {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": gio_trung, "phut": 30},
            )

    # Khác người phụ trách cùng giờ hoặc liền kề lúc 09:30 -> được phép
    ds = dl.dat_lich(ds, {"nguoi": "NG-02", "phu_trach": "sale2@vd.vn", "bat_dau": "2026-11-10 09:00:00", "phut": 30})
    ds = dl.dat_lich(ds, {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 09:30:00", "phut": 30})
    assert len(ds) == 3


def test_ngoai_gio_lam_8_18h_gio_vn_bi_chan():
    """Tiêu chí: ngoài giờ làm (8–18h giờ VN) bị chặn."""
    dl = _dl()
    for gio_ngoai in (
        "2026-11-10 07:30:00",
        "2026-11-10 07:59:00",
        "2026-11-10 17:45:00",  # kéo dài 30 phút tới 18:15 -> vượt 18h
        "2026-11-10 18:00:00",
        "2026-11-10 20:00:00",
    ):
        with pytest.raises(ValueError):
            dl.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": gio_ngoai, "phut": 30},
            )

    # Đúng biên 08:00 -> 08:30 và 17:30 -> 18:00 thì hợp lệ
    ds = dl.dat_lich([], {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 08:00:00", "phut": 30})
    ds = dl.dat_lich(ds, {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 17:30:00", "phut": 30})
    assert len(ds) == 2


def test_nguoi_phu_trach_thay_lich_trong_viec_cho():
    """Tiêu chí: người phụ trách thấy lịch trong viec_cho."""
    dl = _dl()
    ds = []
    ds = dl.dat_lich(ds, {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 14:00:00", "phut": 30})
    ds = dl.dat_lich(ds, {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 09:00:00", "phut": 30})
    ds = dl.dat_lich(ds, {"nguoi": "NG-03", "phu_trach": "sale2@vd.vn", "bat_dau": "2026-11-10 10:00:00", "phut": 30})

    vc_s1 = dl.viec_cho(ds, phu_trach="sale1@vd.vn")
    assert [x["nguoi"] for x in vc_s1] == ["NG-01", "NG-02"]
    assert all(x["phu_trach"] == "sale1@vd.vn" for x in vc_s1)

    khong_import_frappe_dau_file(CORE / "linhx_core" / "booking" / "dat_lich.py")
    api_p = CORE / "linhx_core" / "booking" / "api_booking.py"
    assert api_p.exists() and "def dat_lich_goi(" in api_p.read_text(encoding="utf-8")
    chu_tb = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in TRANG_BU.rglob("*") if p.is_file() and p.suffix in {".js", ".jsx", ".ts", ".tsx"})
    assert "data-dat-lich" in chu_tb
