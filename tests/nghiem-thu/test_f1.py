"""F1: LX Pilot gắn Cơ hội: playbook 7 bước, hạn 14 ngày, báo trễ.

Hợp đồng (HOP-DONG.md):
- DocType JSON trong apps/linhx_core/linhx_core/agent/doctype/lx_pilot/lx_pilot.json:
    name = "LX Pilot", có trường co_hoi (Link LX Co Hoi), bat_dau_luc (Datetime/Date),
    han_hoan_thanh (Datetime/Date), trang_thai (Select: dang_chay, xong, huy), cac_buoc.
- apps/linhx_core/linhx_core/agent/pilot.py thuần Python (không import frappe ở đầu file):
    SO_BUOC = 7
    SO_NGAY_HAN = 14
    PLAYBOOK_7_BUOC: tuple/list gồm đúng 7 bước chuẩn
    tao_pilot(co_hoi: str, bat_dau_luc: str, phu_trach: str = "") -> dict
        trả {"co_hoi": co_hoi, "phu_trach": phu_trach, "bat_dau_luc": bat_dau_luc,
             "han_hoan_thanh": bat_dau_luc + 14 ngày ("YYYY-MM-DD HH:MM:SS"),
             "trang_thai": "dang_chay",
             "cac_buoc": [{"so": 1..7, "ma": str, "ten": str, "trang_thai": "chua_lam", "xong_luc": None}]}
    hoan_thanh_buoc(pilot: dict, so_buoc: int, luc: str) -> dict
        - nếu có bất kỳ bước nào < so_buoc mà trang_thai != "xong" -> raise ValueError
        - so_buoc ngoài 1..7 -> raise ValueError
        - đánh dấu bước so_buoc có trang_thai = "xong", xong_luc = luc;
          khi hoàn thành bước 7 thì đặt pilot["trang_thai"] = "xong"
    viec_cho(ds_pilot: list[dict], luc: str) -> list[dict]
        trả danh sách các pilot chưa xong (trang_thai == "dang_chay") đã quá 14 ngày
        (luc > han_hoan_thanh), mỗi phần tử gắn "qua_han": True, xếp han_hoan_thanh tăng dần.
- Controller lx_pilot.py gọi pilot.
"""
import pytest

from _chung import ma, CORE, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype


def _pl():
    return nap_module("linhx_core.agent.pilot", CORE)


def test_pilot_moi_co_dung_7_buoc():
    """Tiêu chí: pilot mới có đúng 7 bước."""
    pl = _pl()
    p = pl.tao_pilot("CH-001", "2026-11-01 09:00:00", phu_trach="sale@vd.vn")
    assert p["co_hoi"] == "CH-001" and p["trang_thai"] == "dang_chay"
    assert p["han_hoan_thanh"] == "2026-11-15 09:00:00"
    buoc = p.get("cac_buoc") or []
    assert len(buoc) == 7
    assert [b["so"] for b in buoc] == [1, 2, 3, 4, 5, 6, 7]
    assert all(b["trang_thai"] == "chua_lam" for b in buoc)


def test_khong_di_buoc_sau_khi_buoc_truoc_chua_xong():
    """Tiêu chí: không đi bước sau khi bước trước chưa xong."""
    pl = _pl()
    p = pl.tao_pilot("CH-002", "2026-11-01 09:00:00")
    with pytest.raises(ValueError):
        pl.hoan_thanh_buoc(p, 2, "2026-11-02 09:00:00")
    with pytest.raises(ValueError):
        pl.hoan_thanh_buoc(p, 7, "2026-11-02 09:00:00")

    p = pl.hoan_thanh_buoc(p, 1, "2026-11-02 09:00:00")
    assert p["cac_buoc"][0]["trang_thai"] == "xong"
    with pytest.raises(ValueError):
        pl.hoan_thanh_buoc(p, 3, "2026-11-03 09:00:00")

    for s in range(2, 8):
        p = pl.hoan_thanh_buoc(p, s, f"2026-11-0{s} 10:00:00")
    assert p["trang_thai"] == "xong"


def test_qua_14_ngay_chua_xong_thi_vao_viec_cho():
    """Tiêu chí: quá 14 ngày chưa xong thì vào viec_cho."""
    pl = _pl()
    p_tre = pl.tao_pilot("CH-TRE", "2026-11-01 08:00:00", phu_trach="a@vd.vn")
    p_con_han = pl.tao_pilot("CH-CON-HAN", "2026-11-05 08:00:00", phu_trach="a@vd.vn")
    p_da_xong = pl.tao_pilot("CH-XONG", "2026-10-20 08:00:00", phu_trach="a@vd.vn")
    for s in range(1, 8):
        p_da_xong = pl.hoan_thanh_buoc(p_da_xong, s, "2026-10-25 10:00:00")

    vc = pl.viec_cho([p_tre, p_con_han, p_da_xong], "2026-11-16 09:00:00")
    assert [x["co_hoi"] for x in vc] == ["CH-TRE"]
    assert vc[0]["qua_han"] is True


def test_doctype_lx_pilot():
    """Kiểm tra DocType LX Pilot và tính thuần Python của pilot.py."""
    p, d = tim_doctype("LX Pilot")
    assert d, "thiếu DocType LX Pilot"
    tr = ten_truong(d)
    assert tr.get("co_hoi", {}).get("options") == "LX Co Hoi"
    assert "han_hoan_thanh" in tr and "trang_thai" in tr and "cac_buoc" in tr
    assert p.with_suffix(".py").exists()
    khong_import_frappe_dau_file(ma("agent/pilot.py"))
