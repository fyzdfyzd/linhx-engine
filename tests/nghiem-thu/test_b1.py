"""B1: LX Goi, LX Gia, LX Quyen Dung; chuyển từ PROTO 03 m02. Một Gói có giá sàn; quyền dùng cấp khi đơn trả.

Hợp đồng (HOP-DONG.md):
- DocType JSON trong apps/linhx_core (module pay): LX Goi (có gia_san kiểu Currency), LX Gia, LX Quyen Dung
- linhx_core/pay/quyen_dung.py thuần Python:
    gia_hop_le(so_tien, goi: dict) -> bool          False khi so_tien < goi["gia_san"]
    cap_quyen(don: dict, goi: dict) -> dict | None  don {"ma", "goi", "nguoi", "so_tien", "trang_thai"}
        chỉ cấp khi trang_thai == "da_tra" và gia_hop_le; trả {"goi", "nguoi", "don", ...}
- quyen_dung.py ghi rõ chuyển từ file nào trong nguon/03-opc-os (đường dẫn có thật)
"""
import re

from _chung import CORE, GOC, nap_module, tim_doctype, ten_truong

GOI = {"ma": "BC-AI", "ten": "Báo cáo AI nói gì", "gia_san": 5000}


def _qd():
    return nap_module("linhx_core.pay.quyen_dung", CORE)


def test_co_ba_doctype():
    for ten in ["LX Goi", "LX Gia", "LX Quyen Dung"]:
        _, d = tim_doctype(ten)
        assert d, f"thiếu DocType {ten}"
        assert str(d.get("module", "")).lower() == "pay", f"{ten} phải thuộc module pay"
    _, d = tim_doctype("LX Goi")
    tr = ten_truong(d)
    assert "gia_san" in tr and tr["gia_san"].get("fieldtype") == "Currency", "LX Goi thiếu gia_san (Currency)"


def test_gia_san():
    qd = _qd()
    assert qd.gia_hop_le(5000, GOI) is True
    assert qd.gia_hop_le(4999, GOI) is False
    assert qd.gia_hop_le(20000, GOI) is True


def test_cap_quyen_khi_don_da_tra():
    qd = _qd()
    q = qd.cap_quyen({"ma": "D1", "goi": "BC-AI", "nguoi": "N1", "so_tien": 5000, "trang_thai": "da_tra"}, GOI)
    assert q and q["goi"] == "BC-AI" and q["nguoi"] == "N1" and q["don"] == "D1"


def test_khong_cap_khi_chua_tra_hoac_duoi_gia_san():
    qd = _qd()
    for tt in ["cho_tra", "huy", "", None]:
        assert qd.cap_quyen({"ma": "D2", "goi": "BC-AI", "nguoi": "N1", "so_tien": 5000, "trang_thai": tt}, GOI) is None
    assert qd.cap_quyen({"ma": "D3", "goi": "BC-AI", "nguoi": "N1", "so_tien": 1000, "trang_thai": "da_tra"}, GOI) is None


def test_khong_viet_lai_logic_proto():
    chu = (CORE / "linhx_core" / "pay" / "quyen_dung.py").read_text(encoding="utf-8")
    m = re.findall(r"nguon/03-opc-os/[\w./-]+", chu)
    assert m, "quyen_dung.py phải ghi chuyển từ file nào trong nguon/03-opc-os/"
    assert any((GOC / x.rstrip(".")).exists() for x in m), "đường dẫn nguồn ghi trong quyen_dung.py không có thật"
