"""A4B: người của đơn vị chỉ thấy LX Don Vi của mình (tách từ A4 ngày 8/11 sau 3 lần trượt bảo mật K4).

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/quyen_don_vi.py thuần Python (không import frappe đầu file), thêm:
    dieu_kien_don_vi(don_vi_cua_user: list[str], mien: bool) -> str
        mien -> "" ; không đơn vị -> "1=0" ; còn lại "`tabLX Don Vi`.`name` in ('X', 'Y')" (escape dấu ')
    co_quyen_don_vi(ten_don_vi: str, don_vi_cua_user: list[str], mien: bool) -> bool
- hooks.py: has_permission và permission_query_conditions cho "LX Don Vi" trỏ vào hai hàm trên
  (đơn vị của user lấy từ User Permission như A4).
- Sau khi đạt hộp đen, bộ điều phối chạy kiểm tích hợp HTTP thật: tests/nghiem-thu/tich-hop/th_a4b.py.
- Bằng chứng bench WSL máy cty: bang-chung/A4B/don-vi.json
    {"luc", "site", "goi": [{"user", "don_vi_user", "url", "status", "so_don_vi_thay"}]}
    có get_list LX Don Vi bằng user thường thấy đúng 1 đơn vị (của mình) và GET đơn vị khác 403.
"""
from _chung import CORE, bang_chung_json, khong_import_frappe_dau_file, nap_module


def _q():
    return nap_module("linhx_core.crm.quyen_don_vi", CORE)


def test_dieu_kien_don_vi():
    q = _q()
    assert q.dieu_kien_don_vi(["X"], True) == ""
    assert q.dieu_kien_don_vi([], False) == "1=0"
    dk = q.dieu_kien_don_vi(["X", "O'Brien"], False)
    assert "`tabLX Don Vi`.`name`" in dk and "'X'" in dk
    assert "O'Brien'" not in dk.replace("O''Brien'", "").replace("O\\'Brien'", ""), "phải escape dấu ' trong tên đơn vị"


def test_co_quyen_don_vi():
    q = _q()
    assert q.co_quyen_don_vi("X", ["X"], False) is True
    assert q.co_quyen_don_vi("Y", ["X"], False) is False
    assert q.co_quyen_don_vi("Y", [], True) is True
    assert q.co_quyen_don_vi("", ["X"], False) is False


def test_hooks_don_vi():
    chu = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    assert chu.count('"LX Don Vi"') + chu.count("'LX Don Vi'") >= 2, "hooks.py phải khai has_permission và permission_query_conditions cho LX Don Vi"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "quyen_don_vi.py")


def test_bang_chung_bench():
    d = bang_chung_json("A4B", "don-vi.json")
    assert d.get("luc") and d.get("site")
    goi = d.get("goi") or []
    assert all(not str(g.get("user", "")).startswith("Administrator") for g in goi), "phải kiểm bằng user thường"
    assert any("LX%20Don%20Vi" in g.get("url", "").replace(" ", "%20") and g.get("status") == 200 and g.get("so_don_vi_thay") == 1 for g in goi), \
        "thiếu get_list LX Don Vi chỉ thấy 1 đơn vị"
    assert any(g.get("status") == 403 for g in goi), "thiếu lần GET đơn vị khác trả 403"
