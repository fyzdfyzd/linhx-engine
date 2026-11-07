"""A1: DocType LX Don Vi, LX To Chuc, LX Nguoi; khoá gộp trùng theo điện thoại, email, Zalo; chuyển từ PROTO 03 m04.

Hợp đồng (HOP-DONG.md):
- DocType JSON trong apps/linhx_core (module crm): LX Don Vi, LX To Chuc, LX Nguoi
  LX Nguoi có trường dien_thoai, email, zalo, don_vi (Link LX Don Vi)
- linhx_core/crm/gop_trung.py thuần Python:
    khoa_gop(nguoi: dict) -> set[str]       các khoá chuẩn hoá ("dt:84912345678", "email:a@b.vn", "zalo:...")
    gop(danh_sach: list[dict], moi: dict) -> list[dict]   thêm moi; trùng khoá thì gộp vào bản ghi cũ (giữ trường cũ, bù trường trống)
- gop_trung.py ghi rõ chuyển từ file nào trong nguon/03-opc-os (đường dẫn có thật)
- lx_nguoi.py (controller) gọi gop_trung khi thêm mới
"""
import re

from _chung import CORE, GOC, nap_module, tim_doctype, ten_truong


def _gt():
    return nap_module("linhx_core.crm.gop_trung", CORE)


def test_co_ba_doctype():
    for ten in ["LX Don Vi", "LX To Chuc", "LX Nguoi"]:
        p, d = tim_doctype(ten)
        assert d, f"thiếu DocType {ten}"
        assert str(d.get("module", "")).lower() == "crm", f"{ten} phải thuộc module crm"
    _, d = tim_doctype("LX Nguoi")
    tr = ten_truong(d)
    for f in ["dien_thoai", "email", "zalo", "don_vi"]:
        assert f in tr, f"LX Nguoi thiếu trường {f}"
    assert tr["don_vi"].get("fieldtype") == "Link" and tr["don_vi"].get("options") == "LX Don Vi"


def test_hai_nguoi_cung_so_dien_thoai_gop_mot():
    gt = _gt()
    ds = gt.gop([], {"ho_ten": "Lan", "dien_thoai": "0912 345 678"})
    ds = gt.gop(ds, {"ho_ten": "Lan Nguyễn", "dien_thoai": "+84912345678", "email": "lan@vd.vn"})
    assert len(ds) == 1, "cùng số điện thoại (khác cách viết) phải gộp một"
    assert ds[0].get("email") == "lan@vd.vn", "gộp phải bù trường còn trống"
    assert ds[0].get("ho_ten") == "Lan", "gộp không ghi đè trường đã có"


def test_gop_theo_email_va_zalo():
    gt = _gt()
    ds = gt.gop([], {"ho_ten": "A", "email": "Minh@VD.vn "})
    ds = gt.gop(ds, {"ho_ten": "A2", "email": "minh@vd.vn"})
    assert len(ds) == 1, "email khác hoa thường/khoảng trắng phải gộp"
    ds = gt.gop(ds, {"ho_ten": "B", "zalo": "zl_123"})
    ds = gt.gop(ds, {"ho_ten": "B2", "zalo": "zl_123", "dien_thoai": "0987000111"})
    assert len(ds) == 2


def test_khac_het_thi_khong_gop():
    gt = _gt()
    ds = gt.gop([], {"ho_ten": "X", "dien_thoai": "0901000001"})
    ds = gt.gop(ds, {"ho_ten": "Y", "dien_thoai": "0901000002", "email": "y@vd.vn"})
    ds = gt.gop(ds, {"ho_ten": "Z"})
    assert len(ds) == 3, "không có khoá chung thì không gộp (kể cả bản ghi không có khoá nào)"


def test_khoa_gop_chuan_hoa():
    gt = _gt()
    a = gt.khoa_gop({"dien_thoai": "0912.345.678"})
    b = gt.khoa_gop({"dien_thoai": "84912345678"})
    assert a and a == b
    assert gt.khoa_gop({}) == set()


def test_khong_viet_lai_logic_proto():
    p = CORE / "linhx_core" / "crm" / "gop_trung.py"
    chu = p.read_text(encoding="utf-8")
    m = re.findall(r"nguon/03-opc-os/[\w./-]+", chu)
    assert m, "gop_trung.py phải ghi chuyển từ file nào trong nguon/03-opc-os/"
    assert any((GOC / x.rstrip(".")).exists() for x in m), "đường dẫn nguồn ghi trong gop_trung.py không có thật"


def test_controller_goi_gop_trung():
    p, _ = tim_doctype("LX Nguoi")
    ctl = p.with_suffix(".py")
    assert ctl.exists() and "gop_trung" in ctl.read_text(encoding="utf-8"), "lx_nguoi.py phải gọi gop_trung khi thêm mới"
