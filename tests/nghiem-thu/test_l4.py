"""L4: mặt cắt công khai linhx_core.api cho adapter/gói + luật kiến trúc ba lớp.

Hợp đồng (HOP-DONG.md, Đợt 3):
- apps/linhx_core/linhx_core/api.py: không import frappe đầu file; API_CONG_KHAI: list[str] tên được phép dùng,
  ít nhất: "phat", "tim_ham", "tao_nguoi", "ghi_dong_y", "tao_don", "danh_dau_da_tra", "cap_quyen_dung", "doc_cau_hinh";
  mỗi tên là thuộc tính gọi được của module (nạp trễ phần cần Frappe bên trong hàm).
- Luật (tests/nghiem-thu/_dot3.py kiem_kien_truc): lõi không import adapter/gói; adapter, gói chỉ import linhx_core.api;
  gói không import gói hay adapter khác.
"""
from _chung import CORE, khong_import_frappe_dau_file, nap_module
from _dot3 import kiem_kien_truc


def test_api_cong_khai():
    """Tiêu chí: linhx_core.api có đủ tên công khai, gọi được"""
    khong_import_frappe_dau_file(CORE / "linhx_core" / "api.py")
    m = nap_module("linhx_core.api", CORE)
    can = {"phat", "tim_ham", "tao_nguoi", "ghi_dong_y", "tao_don", "danh_dau_da_tra", "cap_quyen_dung", "doc_cau_hinh"}
    assert can <= set(m.API_CONG_KHAI)
    for t in m.API_CONG_KHAI:
        assert callable(getattr(m, t, None)), t


def test_luat_ba_lop():
    """Tiêu chí: không app nào import ngược lớp"""
    kiem_kien_truc()
