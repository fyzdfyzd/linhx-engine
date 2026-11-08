"""A4: quyền theo Đơn vị: người của đơn vị chỉ thấy dữ liệu đơn vị mình. User đơn vị X gọi API Người của đơn vị Y nhận 403.

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/quyen_don_vi.py thuần Python:
    co_quyen(doc: dict, don_vi_cua_user: list[str], mien: bool) -> bool   mien (System Manager/Administrator) luôn True;
                                                                         doc["don_vi"] trống -> chỉ người được miễn thấy
    dieu_kien(doctype: str, don_vi_cua_user: list[str], mien: bool) -> str
        mien -> "" ; không đơn vị -> "1=0" ; còn lại "`tab<doctype>`.`don_vi` in ('X', 'Y')" (giá trị đã escape dấu ')
- Đơn vị của user lấy từ User Permission (allow = "LX Don Vi") hoặc trường trên User; ghi trong quyen_don_vi.py.
- hooks.py: has_permission và permission_query_conditions cho "LX Nguoi" và "LX Co Hoi" trỏ vào hàm dùng quyen_don_vi
  (giữ chặn module tắt của N3).
- Bằng chứng bench WSL máy cty: bang-chung/A4/quyen.json
    {"luc", "site", "goi": [{"user", "don_vi_user", "don_vi_ban_ghi", "url", "status"}]}
    có ít nhất: một lần cùng đơn vị status 200 (GET /api/resource/LX Nguoi/<ten>), một lần khác đơn vị status 403,
    và một lần get_list khác đơn vị không trả bản ghi của đơn vị kia (status 200, "so_ban_ghi_don_vi_khac": 0).
"""
from _chung import CORE, bang_chung_json, khong_import_frappe_dau_file, nap_module


def _q():
    return nap_module("linhx_core.crm.quyen_don_vi", CORE)


def test_co_quyen():
    q = _q()
    assert q.co_quyen({"don_vi": "X"}, ["X"], False) is True
    assert q.co_quyen({"don_vi": "Y"}, ["X"], False) is False
    assert q.co_quyen({"don_vi": "Y"}, [], True) is True
    assert q.co_quyen({"don_vi": ""}, ["X"], False) is False
    assert q.co_quyen({"don_vi": "Y"}, ["X", "Y"], False) is True


def test_dieu_kien_query():
    q = _q()
    assert q.dieu_kien("LX Nguoi", ["X"], True) == ""
    assert q.dieu_kien("LX Nguoi", [], False) == "1=0"
    dk = q.dieu_kien("LX Nguoi", ["X", "O'Brien"], False)
    assert "`tabLX Nguoi`.`don_vi`" in dk and "'X'" in dk
    assert "O'Brien'" not in dk.replace("O''Brien'", "").replace("O\\'Brien'", ""), "phải escape dấu ' trong tên đơn vị"


def test_hooks_noi_quyen():
    chu = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    for dt in ["LX Nguoi", "LX Co Hoi"]:
        assert chu.count(f'"{dt}"') + chu.count(f"'{dt}'") >= 2, f"hooks.py phải khai has_permission và permission_query_conditions cho {dt}"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "quyen_don_vi.py")


def test_bang_chung_bench():
    d = bang_chung_json("A4", "quyen.json")
    assert d.get("luc") and d.get("site")
    goi = d.get("goi") or []
    cung = [g for g in goi if g.get("don_vi_user") == g.get("don_vi_ban_ghi") and "/api/resource/LX" in g.get("url", "")]
    khac = [g for g in goi if g.get("don_vi_user") != g.get("don_vi_ban_ghi") and "/api/resource/LX" in g.get("url", "")]
    assert any(g.get("status") == 200 for g in cung), "thiếu lần gọi cùng đơn vị trả 200"
    assert any(g.get("status") == 403 for g in khac), "thiếu lần gọi khác đơn vị trả 403"
    ds = [g for g in goi if "get_list" in g.get("url", "") and g.get("don_vi_user") != g.get("don_vi_ban_ghi")]
    assert any(g.get("status") == 200 and g.get("so_ban_ghi_don_vi_khac") == 0 for g in ds), "get_list khác đơn vị không được lộ bản ghi"
    assert all(not str(g.get("user", "")).startswith("Administrator") for g in khac), "phải kiểm bằng user thường"
