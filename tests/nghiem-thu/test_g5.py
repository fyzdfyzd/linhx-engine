"""G5: gói phiếu agy nội bộ ra khỏi lõi (làm sau khi O7 đạt).

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_goi_ops (pyproject.toml, linhx_goi_ops/__init__.py, hooks.py, modules.txt, module.json lớp "goi", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/ops/phieu_agy.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/phieu_agy.py
    apps/linhx_core/linhx_core/ops/keo_phieu.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/keo_phieu.py
    apps/linhx_core/linhx_core/ops/nop_phieu.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/nop_phieu.py
    apps/linhx_core/linhx_core/ops/cham_phieu.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/cham_phieu.py
    apps/linhx_core/linhx_core/ops/ban_phieu.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/ban_phieu.py
    apps/linhx_core/linhx_core/ops/api_tho.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/api_tho.py
    apps/linhx_core/linhx_core/ops/api_ban_phieu.py -> apps/linhx_goi_ops/linhx_goi_ops/ops/api_ban_phieu.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.

"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["ops/phieu_agy.py", "ops/keo_phieu.py", "ops/nop_phieu.py", "ops/cham_phieu.py", "ops/ban_phieu.py", "ops/api_tho.py", "ops/api_ban_phieu.py"]
MOI = ["linhx_goi_ops/linhx_goi_ops/ops/phieu_agy.py", "linhx_goi_ops/linhx_goi_ops/ops/keo_phieu.py", "linhx_goi_ops/linhx_goi_ops/ops/nop_phieu.py", "linhx_goi_ops/linhx_goi_ops/ops/cham_phieu.py", "linhx_goi_ops/linhx_goi_ops/ops/ban_phieu.py", "linhx_goi_ops/linhx_goi_ops/ops/api_tho.py", "linhx_goi_ops/linhx_goi_ops/ops/api_ban_phieu.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_goi_ops đủ khung, module.json lớp goi"""
    kiem_app("linhx_goi_ops", "goi")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_goi_ops, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

