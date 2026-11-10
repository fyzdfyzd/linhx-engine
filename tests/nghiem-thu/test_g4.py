"""G4: gói Agent Force: pilot và kho case ra khỏi lõi.

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_goi_agentforce (pyproject.toml, linhx_goi_agentforce/__init__.py, hooks.py, modules.txt, module.json lớp "goi", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/agent/pilot.py -> apps/linhx_goi_agentforce/linhx_goi_agentforce/agent/pilot.py
    apps/linhx_core/linhx_core/cred/kho_case.py -> apps/linhx_goi_agentforce/linhx_goi_agentforce/cred/kho_case.py
    apps/linhx_core/linhx_core/cred/api_cred.py -> apps/linhx_goi_agentforce/linhx_goi_agentforce/cred/api_cred.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.

"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["agent/pilot.py", "cred/kho_case.py", "cred/api_cred.py"]
MOI = ["linhx_goi_agentforce/linhx_goi_agentforce/agent/pilot.py", "linhx_goi_agentforce/linhx_goi_agentforce/cred/kho_case.py", "linhx_goi_agentforce/linhx_goi_agentforce/cred/api_cred.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_goi_agentforce đủ khung, module.json lớp goi"""
    kiem_app("linhx_goi_agentforce", "goi")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_goi_agentforce, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

