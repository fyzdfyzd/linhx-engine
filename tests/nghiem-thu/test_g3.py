"""G3: gói đặt lịch ra khỏi lõi, giao qua luồng chung (loai_giao lich).

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_goi_booking (pyproject.toml, linhx_goi_booking/__init__.py, hooks.py, modules.txt, module.json lớp "goi", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/booking/api_booking.py -> apps/linhx_goi_booking/linhx_goi_booking/api_booking.py
    apps/linhx_core/linhx_core/booking/dat_lich.py -> apps/linhx_goi_booking/linhx_goi_booking/dat_lich.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.
- module.json: "giao": {"lich": "linhx_goi_booking.<module>.<hàm>"}.
"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["booking/api_booking.py", "booking/dat_lich.py"]
MOI = ["linhx_goi_booking/linhx_goi_booking/api_booking.py", "linhx_goi_booking/linhx_goi_booking/dat_lich.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_goi_booking đủ khung, module.json lớp goi"""
    kiem_app("linhx_goi_booking", "goi")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_goi_booking, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

import json

from _dot3 import APPS


def test_khai_giao_lich():
    """Tiêu chí: module.json khai giao lich"""
    d = json.loads((APPS / "linhx_goi_booking" / "module.json").read_text(encoding="utf-8"))
    assert d.get("giao", {}).get("lich", "").startswith("linhx_goi_booking.")

