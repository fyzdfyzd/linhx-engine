"""A4: quyền theo Đơn vị: người của đơn vị chỉ thấy dữ liệu đơn vị mình. User đơn vị X gọi API Người của đơn vị Y nhận 403.

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/quyen_don_vi.py thuần Python:
    co_quyen(doc: dict, don_vi_cua_user: list[str], mien: bool) -> bool   mien (System Manager/Administrator) luôn True;
                                                                         doc["don_vi"] trống -> chỉ người được miễn thấy
    dieu_kien(doctype: str, don_vi_cua_user: list[str], mien: bool) -> str
        mien -> "" ; không đơn vị -> "1=0" ; còn lại "`tab<doctype>`.`don_vi` in ('X', 'Y')" (giá trị đã escape dấu ')
- Đơn vị của user CHỈ lấy từ User Permission (allow = "LX Don Vi"); không đọc trường don_vi trên User.
- Chia 8/11 (sau 3 lần trượt bảo mật K4): kiểm quyền theo bản ghi trong DB, không theo doc client gửi:
    don_vi_can_kiem(doc_moi: dict, doc_cu: dict|None, don_vi_nguoi: str|None) -> list[str]
        tập đơn vị phải có quyền: doc_cu["don_vi"] (bản ghi đã có, giá trị trong DB), doc_moi["don_vi"],
        và don_vi_nguoi (LX Co Hoi: đơn vị của LX Nguoi mà trường nguoi trỏ tới, đọc từ DB). Bỏ giá trị trống, không trùng.
    kiem_ghi(doc_moi, doc_cu, don_vi_nguoi, don_vi_cua_user, mien) -> bool
        mien luôn True; không có đơn vị nào để kiểm -> False; còn lại mọi đơn vị trong don_vi_can_kiem phải thuộc don_vi_cua_user.
    Hook has_permission dùng kiem_ghi với doc_cu đọc từ DB (frappe.db.get_value) khi bản ghi đã tồn tại.
- Phần ẩn danh sách LX Don Vi của đơn vị khác là feature A4B (features-dot1b.json), không thuộc A4.
- Vai trò "LX Nhan Vien" (Role, cài kèm app: fixtures hoặc after_install) có quyền read, write, create trên LX Nguoi và LX Co Hoi;
  người của đơn vị dùng vai trò này (không phải System Manager, vì System Manager được miễn).
- Sau khi đạt hộp đen, bộ điều phối chạy thêm kiểm tích hợp HTTP thật trên bench: tests/nghiem-thu/tich-hop/th_a4.py.
- hooks.py: has_permission và permission_query_conditions cho "LX Nguoi" và "LX Co Hoi" trỏ vào hàm dùng quyen_don_vi
  (giữ chặn module tắt của N3).
- Bằng chứng bench WSL máy cty: bang-chung/A4/quyen.json
    {"luc", "site", "goi": [{"user", "don_vi_user", "don_vi_ban_ghi", "url", "status"}]}
    có ít nhất: một lần cùng đơn vị status 200 (GET /api/resource/LX Nguoi/<ten>), một lần khác đơn vị status 403,
    và một lần get_list khác đơn vị không trả bản ghi của đơn vị kia (status 200, "so_ban_ghi_don_vi_khac": 0).
"""
from _chung import CORE, bang_chung_json, khong_import_frappe_dau_file, nap_module, tim_doctype


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


def test_don_vi_can_kiem():
    q = _q()
    assert sorted(q.don_vi_can_kiem({"don_vi": "X"}, None, None)) == ["X"]
    assert sorted(q.don_vi_can_kiem({"don_vi": "X"}, {"don_vi": "Y"}, None)) == ["X", "Y"]
    assert sorted(q.don_vi_can_kiem({"don_vi": "X"}, None, "Y")) == ["X", "Y"]
    assert sorted(q.don_vi_can_kiem({"don_vi": "X"}, {"don_vi": "X"}, "X")) == ["X"]
    assert q.don_vi_can_kiem({"don_vi": ""}, None, None) == []


def test_kiem_ghi_theo_ban_ghi_db():
    q = _q()
    # sửa bản ghi của Y, client gửi don_vi = X: phải xét giá trị trong DB
    assert q.kiem_ghi({"don_vi": "X"}, {"don_vi": "Y"}, None, ["X"], False) is False
    # tạo cơ hội don_vi X nhưng nguoi thuộc Y
    assert q.kiem_ghi({"don_vi": "X"}, None, "Y", ["X"], False) is False
    assert q.kiem_ghi({"don_vi": "X"}, None, "X", ["X"], False) is True
    assert q.kiem_ghi({"don_vi": "X"}, {"don_vi": "X"}, None, ["X"], False) is True
    assert q.kiem_ghi({"don_vi": ""}, None, None, ["X"], False) is False
    assert q.kiem_ghi({"don_vi": "Y"}, {"don_vi": "Y"}, "Y", [], True) is True


def test_khong_lay_don_vi_tu_user():
    chu = (CORE / "linhx_core" / "crm" / "quyen_don_vi.py").read_text(encoding="utf-8")
    assert "User Permission" in chu, "đơn vị của user phải lấy từ User Permission"
    import re
    assert not re.search(r"""get_value\(\s*["']User["'][^)]*don_vi""", chu), "không lấy đơn vị từ trường don_vi của User"


def test_hooks_noi_quyen():
    chu = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    for dt in ["LX Nguoi", "LX Co Hoi"]:
        assert chu.count(f'"{dt}"') + chu.count(f"'{dt}'") >= 2, f"hooks.py phải khai has_permission và permission_query_conditions cho {dt}"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "quyen_don_vi.py")


def test_vai_tro_nhan_vien():
    for dt in ["LX Nguoi", "LX Co Hoi"]:
        _, d = tim_doctype(dt)
        vt = {p.get("role"): p for p in d.get("permissions", [])}
        assert vt.get("LX Nhan Vien", {}).get("read") == 1, f"{dt} phải cho vai trò LX Nhan Vien quyền đọc"
    chu = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (CORE / "linhx_core").rglob("*") if p.suffix in (".py", ".json"))
    assert '"LX Nhan Vien"' in chu and ("fixtures" in chu or "after_install" in chu), "vai trò LX Nhan Vien phải được tạo khi cài app"


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
