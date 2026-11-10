"""K2: Chiêm Tinh Số chạy thật trên engine: gói linhx_goi_chiemtinh giao báo cáo qua luồng chung, song song với hệ cũ.

Hợp đồng (HOP-DONG.md, Đợt 4):
- apps/linhx_goi_chiemtinh (module.json lớp "goi", phu_thuoc ["linhx_cts"], giao {"bao_cao_cts": "linhx_goi_chiemtinh.giao.giao"}).
  LX Goi loai_giao thêm "bao_cao_cts" (sửa L3 nếu cần thì qua module.json, không sửa giao_hang.py).
- linhx_goi_chiemtinh/giao.py: giao(don, goi) gọi API báo cáo CTS qua linhx_cts (URL, khoá đọc từ cấu hình, không viết cứng);
  cờ "cts_that" (LX Cau Hinh) mặc định tắt: tắt thì chỉ ghi kết quả đối chiếu, bật thì giao thật cho khách.
  Hàm thuần: so_khop(don_engine: dict, don_cts: dict) -> list[str] các trường lệch (so_tien, ma_don, goi, trang_thai).
- Bằng chứng: bang-chung/K2/doi-chieu.json {"luc": str, "so_don": int >= 3, "lech": 0, "co_cts_that": false}
  từ đơn thật chạy song song trên VM.
"""
from _chung import bang_chung_json, nap_module
from _dot3 import APPS, kiem_app, kiem_kien_truc


def test_app_va_khai_bao():
    """Tiêu chí: gói chiemtinh đủ khung, khai giao bao_cao_cts"""
    d = kiem_app("linhx_goi_chiemtinh", "goi")
    assert "linhx_cts" in d.get("phu_thuoc", []) and d.get("giao", {}).get("bao_cao_cts")
    kiem_kien_truc()


def test_so_khop():
    """Tiêu chí: so khớp đơn engine với đơn CTS chỉ ra trường lệch"""
    m = nap_module("linhx_goi_chiemtinh.giao", APPS / "linhx_goi_chiemtinh")
    a = {"ma_don": "ord_1", "so_tien": 99000, "goi": "natal", "trang_thai": "da_tra"}
    assert m.so_khop(a, dict(a)) == []
    assert m.so_khop(a, {**a, "so_tien": 199000}) == ["so_tien"]
    chu = (APPS / "linhx_goi_chiemtinh" / "linhx_goi_chiemtinh" / "giao.py").read_text(encoding="utf-8")
    assert "cts_that" in chu and "chiemtinh.vn" not in chu


def test_bang_chung_song_song():
    """Tiêu chí: ít nhất 3 đơn thật chạy song song không lệch"""
    d = bang_chung_json("K2", "doi-chieu.json")
    assert int(d["so_don"]) >= 3 and int(d["lech"]) == 0 and d["co_cts_that"] is False
