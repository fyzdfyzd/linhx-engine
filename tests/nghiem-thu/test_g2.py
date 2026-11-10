"""G2: gói báo cáo: phần làm báo cáo sau trả ra khỏi lõi, giao qua luồng giao hàng chung (loai_giao bao_cao).

Hợp đồng (HOP-DONG.md, Đợt 3, sửa luôn không để file chuyển tiếp):
- App Frappe apps/linhx_goi_baocao (pyproject.toml, linhx_goi_baocao/__init__.py, hooks.py, modules.txt, module.json lớp "goi", can_loi ">=0.3.0").
- Chuyển code (DocType ở lại linhx_core trong đợt 3, chỉ chuyển Python):
    apps/linhx_core/linhx_core/pay/sau_tra.py -> apps/linhx_goi_baocao/linhx_goi_baocao/sau_tra.py
    apps/linhx_core/linhx_core/pay/ban_bao_cao.py -> apps/linhx_goi_baocao/linhx_goi_baocao/ban_bao_cao.py
  File cũ xoá hẳn; chỗ trong linhx_core từng import chúng đổi sang tra hàm qua dang_ky_module (cung_cap/nghe/giao) hoặc sự kiện.
  Nghiệm thu cũ vẫn xanh: chúng tìm chỗ mới qua CHUYEN_CHO trong tests/nghiem-thu/_chung.py.
- Luật ba lớp (_dot3.kiem_kien_truc) xanh.
- module.json: "giao": {"bao_cao": "linhx_goi_baocao.<module>.<hàm>"}; hooks lõi bỏ doc_events trỏ sau_tra (L3 đã nối giao_hang).
"""
from _dot3 import kiem_app, kiem_da_chuyen, kiem_kien_truc

CU = ["pay/sau_tra.py", "pay/ban_bao_cao.py"]
MOI = ["linhx_goi_baocao/linhx_goi_baocao/sau_tra.py", "linhx_goi_baocao/linhx_goi_baocao/ban_bao_cao.py"]


def test_app_va_khai_bao():
    """Tiêu chí: app linhx_goi_baocao đủ khung, module.json lớp goi"""
    kiem_app("linhx_goi_baocao", "goi")


def test_da_chuyen_het():
    """Tiêu chí: code đã chuyển sang linhx_goi_baocao, file cũ trong linhx_core đã xoá"""
    kiem_da_chuyen(CU, MOI)


def test_kien_truc():
    """Tiêu chí: không import ngược lớp"""
    kiem_kien_truc()

import json

from _dot3 import APPS


def test_khai_giao_bao_cao():
    """Tiêu chí: module.json khai giao bao_cao, hooks lõi không còn trỏ sau_tra"""
    d = json.loads((APPS / "linhx_goi_baocao" / "module.json").read_text(encoding="utf-8"))
    assert d.get("giao", {}).get("bao_cao", "").startswith("linhx_goi_baocao.")
    assert "sau_tra" not in (APPS / "linhx_core" / "linhx_core" / "hooks.py").read_text(encoding="utf-8")

