"""B5: sổ S1a-HKD và báo đỏ khi doanh thu chạm ngưỡng; chuyển từ PROTO 03 m07.
Đơn da_tra ghi một dòng sổ. Vượt ngưỡng cấu hình thì có cảnh báo ở bàn.

Hợp đồng (HOP-DONG.md):
- DocType JSON module pay: LX So S1a (ngay Date, ma_don Data unique, dien_giai, so_tien Currency);
  DocType Single module pay "LX Cau Hinh Pay" có nguong_doanh_thu (Currency).
- linhx_core/pay/so_s1a.py thuần Python:
    NGUONG_MAC_DINH = 1_000_000_000
    dong_so(don: dict, ngay: str "YYYY-MM-DD") -> dict | None   chỉ đơn da_tra; {"ngay", "ma_don", "dien_giai", "so_tien"}
    ghi(so: list, don, ngay) -> list                            không ghi trùng ma_don
    tong_nam(so, nam: int) -> int
    canh_bao(so, nam, nguong=None) -> dict | None   >= nguong: {"muc": "do", "tong", "nguong"};
                                                    >= 90% nguong: {"muc": "vang", ...}; còn lại None
- linhx_core/pay/api_thue.py: @frappe.whitelist() `canh_bao_thue` (chỉ người điều hành) trả canh_bao năm hiện tại.
- so_s1a.py ghi chuyển từ file nào trong nguon/03-opc-os/ (đường dẫn có thật)
"""
from _chung import ma, CORE, ghi_nguon_proto, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype


def _s():
    return nap_module("linhx_core.pay.so_s1a", CORE)


def _don(ma, tien, tt="da_tra"):
    return {"ma": ma, "so_tien": tien, "trang_thai": tt, "goi": "BC-AI"}


def test_doctype():
    _, d = tim_doctype("LX So S1a")
    assert d and str(d.get("module", "")).lower() == "pay"
    tr = ten_truong(d)
    assert tr.get("ma_don", {}).get("unique") == 1 and tr.get("so_tien", {}).get("fieldtype") == "Currency"
    _, c = tim_doctype("LX Cau Hinh Pay")
    assert c and c.get("issingle") == 1 and ten_truong(c).get("nguong_doanh_thu", {}).get("fieldtype") == "Currency"


def test_moi_don_da_tra_mot_dong():
    s = _s()
    so = s.ghi([], _don("D1", 99000), "2026-11-09")
    so = s.ghi(so, _don("D1", 99000), "2026-11-09")
    so = s.ghi(so, _don("D2", 5000, "cho_tra"), "2026-11-09")
    assert len(so) == 1 and so[0]["ma_don"] == "D1" and so[0]["ngay"] == "2026-11-09" and so[0]["so_tien"] == 99000
    assert s.dong_so(_don("D3", 1, "huy"), "2026-11-09") is None


def test_canh_bao_nguong():
    s = _s()
    assert s.NGUONG_MAC_DINH == 1_000_000_000
    so = s.ghi([], _don("D1", 850_000_000), "2026-03-01")
    so = s.ghi(so, _don("D0", 500_000_000), "2025-12-31")
    assert s.tong_nam(so, 2026) == 850_000_000
    assert s.canh_bao(so, 2026) is None
    so = s.ghi(so, _don("D2", 60_000_000), "2026-06-01")
    assert s.canh_bao(so, 2026)["muc"] == "vang"
    so = s.ghi(so, _don("D3", 90_000_000), "2026-11-09")
    cb = s.canh_bao(so, 2026)
    assert cb["muc"] == "do" and cb["tong"] == 1_000_000_000 and cb["nguong"] == 1_000_000_000
    assert s.canh_bao(so, 2026, nguong=2_000_000_000) is None


def test_api_va_nguon():
    chu = (ma("pay/api_thue.py")).read_text(encoding="utf-8")
    assert "def canh_bao_thue(" in chu and "allow_guest" not in chu
    p = ma("pay/so_s1a.py")
    khong_import_frappe_dau_file(p)
    ghi_nguon_proto(p)
