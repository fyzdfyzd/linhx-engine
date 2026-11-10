"""K2b: Chiêm Tinh Số chạy song song trên engine với đơn thật đọc từ BẢN SAO DB của CTS (Linh 10/11: "bản sao db").

Hợp đồng (HOP-DONG.md, Đợt 4):
- linhx_goi_chiemtinh/doi_chieu_ban_sao.py:
  - chuyen_don(hang: dict) -> dict: hàm thuần đổi một hàng bảng order_orders của CTS
    (id, sku, tong, da_nhan, trang_thai, paid_at...) sang dạng đơn engine {ma_don, so_tien, goi, trang_thai}.
    so_tien lấy từ da_nhan (tiền đã nhận), không lấy gia_goc; goi lấy từ sku; trang_thai đổi qua bảng
    TRANG_THAI (paid -> da_tra, pending -> cho_tra, refunded -> da_hoan, giá trị lạ giữ nguyên để so_khop bắt lệch).
  - chay(url_ban_sao, so_don=3) -> dict: đọc đơn đã trả từ bản sao (CHỈ SELECT), chạy luồng giao của gói với cờ cts_that tắt,
    so_khop từng đơn, trả dict bằng chứng bên dưới. URL đọc từ biến môi trường CTS_BAN_SAO_URL, tên DB phải chứa "ban_sao"
    (không chạy được trên DB gốc). Không in email, hồ sơ, tên khách.
- deploy/cts-ban-sao.sh: trên VM, khôi phục bản pg_dump mới nhất của CTS (ops/sao_luu.py) vào DB cts_ban_sao,
  cấp role chỉ đọc, rồi chạy doi_chieu_ban_sao. Bí mật chỉ ở /root/linhx-bi-mat.env.
- Bằng chứng: bang-chung/K2b/doi-chieu.json
  {"luc": ISO, "may": "linhx-engine-1", "nguon": "ban_sao_db", "ban_sao_luc": ISO (giờ của bản dump),
   "so_don": int >= 3, "lech": 0, "co_cts_that": false, "ma_don_bam": [sha256 12+ hex ký tự, mỗi đơn một, không trùng]}
"""
import datetime as dt
import re

from _chung import GOC, bang_chung_json, nap_module
from _dot3 import APPS

GOI = APPS / "linhx_goi_chiemtinh" / "linhx_goi_chiemtinh"


def _m():
    return nap_module("linhx_goi_chiemtinh.doi_chieu_ban_sao", APPS / "linhx_goi_chiemtinh")


def test_chuyen_don_tu_hang_cts():
    """Tiêu chí: đổi hàng order_orders của CTS sang đơn engine, tiền lấy từ da_nhan"""
    m = _m()
    hang = {"id": "ord_9", "sku": "natal", "gia_goc": 199000, "tong": 99000, "da_nhan": 99000,
            "trang_thai": "paid", "email": "a@b.c", "ho_so_enc": "x"}
    d = m.chuyen_don(hang)
    assert d == {"ma_don": "ord_9", "so_tien": 99000, "goi": "natal", "trang_thai": "da_tra"}
    assert m.chuyen_don({**hang, "da_nhan": 0, "trang_thai": "pending"})["so_tien"] == 0
    assert m.chuyen_don({**hang, "trang_thai": "la_lung"})["trang_thai"] == "la_lung"


def test_chi_doc_ban_sao():
    """Tiêu chí: chỉ đọc bản sao DB, không ghi, không chạy trên DB gốc"""
    chu = (GOI / "doi_chieu_ban_sao.py").read_text(encoding="utf-8")
    assert "order_orders" in chu and "CTS_BAN_SAO_URL" in chu and "ban_sao" in chu
    assert not re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER)\b", chu, re.I), "chỉ được SELECT"
    assert not re.search(r"postgres(ql)?://[^\"'\s]*:[^\"'\s]*@", chu), "không viết cứng URL có mật khẩu"
    sh = (GOC / "deploy" / "cts-ban-sao.sh").read_text(encoding="utf-8")
    assert "cts_ban_sao" in sh and "linhx-bi-mat.env" in sh


def test_bang_chung_don_that_tu_ban_sao():
    """Tiêu chí: ít nhất 3 đơn thật từ bản sao DB chạy song song không lệch"""
    d = bang_chung_json("K2b", "doi-chieu.json")
    assert d["may"] == "linhx-engine-1" and d["nguon"] == "ban_sao_db"
    dt.datetime.fromisoformat(d["luc"].replace("Z", "+00:00"))
    dt.datetime.fromisoformat(d["ban_sao_luc"].replace("Z", "+00:00"))
    bam = d["ma_don_bam"]
    assert int(d["so_don"]) >= 3 and len(bam) == int(d["so_don"]) and len(set(bam)) == len(bam)
    assert all(re.fullmatch(r"[0-9a-f]{12,64}", b) for b in bam), "mã đơn phải băm, không để lộ mã thật"
    assert int(d["lech"]) == 0 and d["co_cts_that"] is False
