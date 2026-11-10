"""P1: adapter Việt Nam linhx_vn: SePay, VietQR, sổ S1a ra khỏi lõi.

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_vn (pyproject.toml, linhx_vn/__init__.py, hooks.py, modules.txt, module.json lớp "adapter", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/pay/sepay.py -> apps/linhx_vn/linhx_vn/pay/sepay.py
    apps/linhx_core/linhx_core/pay/api_sepay.py -> apps/linhx_vn/linhx_vn/pay/api_sepay.py
    apps/linhx_core/linhx_core/pay/vietqr.py -> apps/linhx_vn/linhx_vn/pay/vietqr.py
    apps/linhx_core/linhx_core/pay/so_s1a.py -> apps/linhx_vn/linhx_vn/pay/so_s1a.py
    apps/linhx_core/linhx_core/pay/api_thue.py -> apps/linhx_vn/linhx_vn/pay/api_thue.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.
- Webhook SePay gọi linhx_core.api.danh_dau_da_tra (lõi tự phát don.da_tra), không tự đổi trạng thái đơn.
"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["pay/sepay.py", "pay/api_sepay.py", "pay/vietqr.py", "pay/so_s1a.py", "pay/api_thue.py"]
MOI = ["linhx_vn/linhx_vn/pay/sepay.py", "linhx_vn/linhx_vn/pay/api_sepay.py", "linhx_vn/linhx_vn/pay/vietqr.py", "linhx_vn/linhx_vn/pay/so_s1a.py", "linhx_vn/linhx_vn/pay/api_thue.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_vn đủ khung, module.json lớp adapter"""
    kiem_app("linhx_vn", "adapter")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_vn, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

