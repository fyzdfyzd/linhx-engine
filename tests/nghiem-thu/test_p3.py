"""P3: adapter Chiêm Tinh Số linhx_cts ra khỏi lõi.

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_cts (pyproject.toml, linhx_cts/__init__.py, hooks.py, modules.txt, module.json lớp "adapter", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/cts_adapter/api.py -> apps/linhx_cts/linhx_cts/api.py
    apps/linhx_core/linhx_core/cts_adapter/bong.py -> apps/linhx_cts/linhx_cts/bong.py
    apps/linhx_core/linhx_core/cts_adapter/hop_dong.py -> apps/linhx_cts/linhx_cts/hop_dong.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.
- Chế độ bóng giữ nguyên hành vi (cờ tắt mặc định, không giao hàng).
"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["cts_adapter/api.py", "cts_adapter/bong.py", "cts_adapter/hop_dong.py"]
MOI = ["linhx_cts/linhx_cts/api.py", "linhx_cts/linhx_cts/bong.py", "linhx_cts/linhx_cts/hop_dong.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_cts đủ khung, module.json lớp adapter"""
    kiem_app("linhx_cts", "adapter")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_cts, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

