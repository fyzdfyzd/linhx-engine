"""L3: giao hàng chung: đơn chuyển sang da_tra -> phát don.da_tra -> gọi hàm giao của gói theo loai_giao của Gói.

Hợp đồng (HOP-DONG.md, Đợt 3):
- DocType "LX Goi" thêm trường loai_giao (Select: bao_cao, quyen_dung, lich, tep).
- apps/linhx_core/linhx_core/giao_hang.py (thuần Python):
    can_phat(trang_thai_cu, trang_thai_moi) -> bool: True chỉ khi chuyển từ khác da_tra sang da_tra
    chon_ham(loai_giao: str, danh_sach_module: list[dict]) -> str: hàm khai ở "giao" của module.json;
        không có ai khai -> ValueError; hai module cùng khai -> ValueError
    xu_ly(ban_ghi_su_kien: dict, doc_goi: callable(ten_don)->dict, danh_sach_module, goi: callable(duong, don, goi)) -> str
        đọc du_lieu.don, lấy gói của đơn, chọn hàm theo loai_giao, gọi, trả đường hàm đã gọi
- hooks.py linhx_core: doc_events "LX Don" nối giao_hang (phát don.da_tra khi can_phat); module.json linhx_core khai
  nghe "don.da_tra": "linhx_core.giao_hang.nghe".
"""
import pytest

from _chung import CORE, nap_module, ten_truong, tim_doctype


def _m():
    return nap_module("linhx_core.giao_hang", CORE)


DS = [{"ten": "linhx_goi_baocao", "giao": {"bao_cao": "linhx_goi_baocao.giao.giao"}},
      {"ten": "linhx_goi_booking", "giao": {"lich": "linhx_goi_booking.giao.giao"}}]


def test_goi_co_loai_giao():
    """Tiêu chí: LX Goi có trường loai_giao, hooks nối LX Don vào giao_hang"""
    _, d = tim_doctype("LX Goi")
    tr = ten_truong(d)
    assert "loai_giao" in tr
    assert {"bao_cao", "quyen_dung", "lich", "tep"} <= set(str(tr["loai_giao"].get("options", "")).split("\n"))
    h = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    assert "LX Don" in h and "giao_hang" in h


def test_can_phat_chi_khi_chuyen_sang_da_tra():
    """Tiêu chí: chỉ phát một lần khi đơn chuyển sang da_tra"""
    m = _m()
    assert m.can_phat("cho_tra", "da_tra") is True
    assert m.can_phat("da_tra", "da_tra") is False
    assert m.can_phat(None, "cho_tra") is False


def test_chon_va_goi_ham_giao():
    """Tiêu chí: gọi đúng hàm giao của gói theo loai_giao, thiếu hoặc trùng thì lỗi"""
    m = _m()
    assert m.chon_ham("lich", DS) == "linhx_goi_booking.giao.giao"
    with pytest.raises(ValueError):
        m.chon_ham("tep", DS)
    with pytest.raises(ValueError):
        m.chon_ham("bao_cao", DS + [{"ten": "x", "giao": {"bao_cao": "x.g"}}])
    goi = []
    duong = m.xu_ly({"ten": "don.da_tra", "du_lieu": {"don": "DON-9"}},
                    lambda ten: {"name": ten, "goi": "G1", "loai_giao": "bao_cao"}, DS,
                    lambda d, don, g: goi.append((d, don["name"])))
    assert duong == "linhx_goi_baocao.giao.giao" and goi == [("linhx_goi_baocao.giao.giao", "DON-9")]
