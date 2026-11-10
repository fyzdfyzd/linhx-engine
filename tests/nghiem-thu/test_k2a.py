"""K2a: gói linhx_goi_chiemtinh đủ khung + so khớp đơn engine với đơn CTS (tách từ K2, Linh 10/11).

Hợp đồng (HOP-DONG.md, Đợt 4):
- apps/linhx_goi_chiemtinh (module.json lớp "goi", phu_thuoc ["linhx_cts"], giao {"bao_cao_cts": "linhx_goi_chiemtinh.giao.giao"}).
- linhx_goi_chiemtinh/giao.py: giao(don, goi) gọi API báo cáo CTS qua linhx_cts (URL, khoá đọc từ cấu hình, không viết cứng);
  cờ "cts_that" (LX Cau Hinh) mặc định tắt: tắt thì chỉ ghi kết quả đối chiếu, bật thì giao thật cho khách.
- Hàm thuần so_khop(don_engine: dict, don_cts: dict) -> list[str] các trường lệch trong (ma_don, so_tien, goi, trang_thai),
  theo đúng thứ tự đó. Trường thiếu ở một bên là LỆCH: không lấp so_tien bằng giá, không đoán giá trị mặc định.
- Không xoá cứng bản ghi (frappe.delete_doc với force hay ignore_permissions) trong gói.
"""
import re

from _chung import nap_module
from _dot3 import APPS, kiem_app, kiem_kien_truc

GOI = APPS / "linhx_goi_chiemtinh" / "linhx_goi_chiemtinh"
MAU = {"ma_don": "ord_1", "so_tien": 99000, "goi": "natal", "trang_thai": "da_tra"}


def _m():
    return nap_module("linhx_goi_chiemtinh.giao", APPS / "linhx_goi_chiemtinh")


def test_app_va_khai_bao():
    """Tiêu chí: gói chiemtinh đủ khung, khai giao bao_cao_cts"""
    d = kiem_app("linhx_goi_chiemtinh", "goi")
    assert "linhx_cts" in d.get("phu_thuoc", []) and d.get("giao", {}).get("bao_cao_cts")
    chu = (GOI / "giao.py").read_text(encoding="utf-8")
    assert "cts_that" in chu and "chiemtinh.vn" not in chu
    kiem_kien_truc()


def test_so_khop_chi_ra_truong_lech():
    """Tiêu chí: so khớp đơn engine với đơn CTS chỉ ra trường lệch"""
    m = _m()
    assert m.so_khop(MAU, dict(MAU)) == []
    assert m.so_khop(MAU, {**MAU, "so_tien": 199000}) == ["so_tien"]
    assert m.so_khop(MAU, {**MAU, "goi": "transit", "trang_thai": "cho_tra"}) == ["goi", "trang_thai"]
    assert m.so_khop(MAU, {**MAU, "ma_don": "ord_2", "so_tien": 1}) == ["ma_don", "so_tien"]


def test_truong_thieu_la_lech_khong_lap():
    """Tiêu chí: trường thiếu ở một bên tính là lệch, không lấp số tiền bằng giá"""
    m = _m()
    thieu = {k: v for k, v in MAU.items() if k != "so_tien"}
    assert m.so_khop(MAU, {**thieu, "gia": 99000}) == ["so_tien"]
    assert m.so_khop({**thieu, "gia": 99000}, MAU) == ["so_tien"]
    assert m.so_khop(MAU, {**MAU, "so_tien": None}) == ["so_tien"]


def test_khong_xoa_cung():
    """Tiêu chí: gói không xoá cứng bản ghi"""
    for p in GOI.rglob("*.py"):
        if p.name.startswith("test_"):
            continue
        chu = p.read_text(encoding="utf-8")
        for m in re.finditer(r"delete_doc\((.*?)\)", chu, re.S):
            assert "force" not in m.group(1) and "ignore_permissions" not in m.group(1), f"{p.name}: xoá cứng"
