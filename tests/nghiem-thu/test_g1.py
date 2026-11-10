"""G1: gói ifAgent: T1 khám và xác minh marketing ra khỏi lõi.

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_goi_ifagent (pyproject.toml, linhx_goi_ifagent/__init__.py, hooks.py, modules.txt, module.json lớp "goi", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/crm/t1.py -> apps/linhx_goi_ifagent/linhx_goi_ifagent/t1.py
    apps/linhx_core/linhx_core/crm/xac_minh_marketing.py -> apps/linhx_goi_ifagent/linhx_goi_ifagent/xac_minh_marketing.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.
- api_form.py giữ các endpoint công khai cũ (vd def xac_nhan_marketing) nhưng gọi hàm của gói qua dang_ky_module.tim_ham(..., "cung_cap", ...).
"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["crm/t1.py", "crm/xac_minh_marketing.py"]
MOI = ["linhx_goi_ifagent/linhx_goi_ifagent/t1.py", "linhx_goi_ifagent/linhx_goi_ifagent/xac_minh_marketing.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_goi_ifagent đủ khung, module.json lớp goi"""
    kiem_app("linhx_goi_ifagent", "goi")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_goi_ifagent, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

from _chung import CORE


def test_api_form_khong_import_goi():
    """Tiêu chí: api_form của lõi gọi T1 qua tra hàm, không import gói"""
    chu = (CORE / "linhx_core" / "crm" / "api_form.py").read_text(encoding="utf-8")
    assert "t1" not in [x.strip() for x in chu.split("from linhx_core.crm import")[-1].split("\n")[0].split(",")]
    assert "linhx_goi_ifagent" not in chu

