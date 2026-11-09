import copy
import json
import sys
import types
from unittest.mock import patch

import pytest

from linhx_core.agent import pilot


def test_tao_pilot_kiem_tra_dau_vao_va_7_buoc():
    with pytest.raises(ValueError):
        pilot.tao_pilot("", "2026-11-01 09:00:00")
    with pytest.raises(ValueError):
        pilot.tao_pilot(True, "2026-11-01 09:00:00")
    with pytest.raises(ValueError):
        pilot.tao_pilot("CH-01", "khong-phai-ngay")

    p = pilot.tao_pilot("  CH-01  ", "2026-11-01T09:30:00", phu_trach=" sale@vd.vn ")
    assert p["co_hoi"] == "CH-01"
    assert p["phu_trach"] == "sale@vd.vn"
    assert p["bat_dau_luc"] == "2026-11-01 09:30:00"
    assert p["han_hoan_thanh"] == "2026-11-15 09:30:00"
    assert p["trang_thai"] == "dang_chay"
    assert len(p["cac_buoc"]) == pilot.SO_BUOC == 7
    assert [b["so"] for b in p["cac_buoc"]] == [1, 2, 3, 4, 5, 6, 7]
    assert all(b["trang_thai"] == "chua_lam" and b["xong_luc"] is None for b in p["cac_buoc"])


def test_hoan_thanh_buoc_khong_sua_dict_dau_vao_va_chan_bien():
    p_goc = pilot.tao_pilot("CH-02", "2026-11-01 08:00:00")
    ban_sao = copy.deepcopy(p_goc)

    for so_sai in (0, -1, 8, True, False, "1"):
        with pytest.raises(ValueError):
            pilot.hoan_thanh_buoc(p_goc, so_sai, "2026-11-01 10:00:00")

    with pytest.raises(ValueError):
        pilot.hoan_thanh_buoc(p_goc, 2, "2026-11-01 10:00:00")

    assert p_goc == ban_sao

    p1 = pilot.hoan_thanh_buoc(p_goc, 1, "2026-11-01 10:00:00")
    assert p_goc["cac_buoc"][0]["trang_thai"] == "chua_lam"
    assert p1["cac_buoc"][0]["trang_thai"] == "xong"
    assert p1["cac_buoc"][0]["xong_luc"] == "2026-11-01 10:00:00"
    assert p1["trang_thai"] == "dang_chay"

    p_huy = copy.deepcopy(p1)
    p_huy["trang_thai"] = "huy"
    with pytest.raises(ValueError):
        pilot.hoan_thanh_buoc(p_huy, 2, "2026-11-02 10:00:00")


def test_viec_cho_xep_thu_tu_han_hoan_thanh_tang_dan():
    p_muon_hon = pilot.tao_pilot("CH-MUON", "2026-11-02 09:00:00", phu_trach="s1@vd.vn")
    p_som_hon = pilot.tao_pilot("CH-SOM", "2026-11-01 08:00:00", phu_trach="s2@vd.vn")
    p_dung_han = pilot.tao_pilot("CH-BIEN", "2026-11-03 12:00:00", phu_trach="s1@vd.vn")
    p_huy = pilot.tao_pilot("CH-HUY", "2026-10-15 08:00:00", phu_trach="s1@vd.vn")
    p_huy["trang_thai"] = "huy"

    # Đúng bằng han_hoan_thanh (2026-11-17 12:00:00) thì chưa quá 14 ngày
    ds = [p_muon_hon, p_som_hon, p_dung_han, p_huy]
    vc = pilot.viec_cho(ds, "2026-11-17 12:00:00")
    assert [x["co_hoi"] for x in vc] == ["CH-SOM", "CH-MUON"]
    assert all(x["qua_han"] is True for x in vc)
    assert "qua_han" not in p_som_hon


def test_controller_lx_pilot_ke_thua_co_hoi_va_kiem_luat():
    frappe_mod = types.ModuleType("frappe")
    model_mod = types.ModuleType("frappe.model")
    doc_mod = types.ModuleType("frappe.model.document")

    class _StubDocument:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    doc_mod.Document = _StubDocument
    model_mod.document = doc_mod
    frappe_mod.model = model_mod

    class _StubDB:
        @staticmethod
        def get_value(dt, name, fields, as_dict=False):
            if dt == "LX Co Hoi" and name == "CH-10":
                return {"phu_trach": "sale10@vd.vn", "don_vi": "IFAGENT"}
            return None

    frappe_mod.db = _StubDB()

    with patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        try:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            from linhx_core.agent.doctype.lx_pilot.lx_pilot import LXPilot

            doc = LXPilot(co_hoi="CH-10", bat_dau_luc="2026-11-01 08:30:00", han_hoan_thanh="2026-12-31 00:00:00")
            doc.before_insert()
            doc.validate()

            assert doc.phu_trach == "sale10@vd.vn"
            assert doc.don_vi == "IFAGENT"
            assert doc.han_hoan_thanh == "2026-11-15 08:30:00"
            assert doc.trang_thai == "dang_chay"
            assert len(doc.cac_buoc) == 7

            # Chặn gán sai đơn vị so với Cơ hội
            doc_sai_dv = LXPilot(co_hoi="CH-10", don_vi="DON-VI-KHAC", bat_dau_luc="2026-11-01 08:30:00")
            with pytest.raises(ValueError):
                doc_sai_dv.before_insert()

            # Chặn nhảy bước trên controller
            with pytest.raises(ValueError):
                doc.hoan_thanh_buoc(2, "2026-11-02 09:00:00")

            # Chặn sửa trực tiếp cac_buoc nhảy cóc hoặc đặt trạng thái xong sớm
            doc_sai = LXPilot(
                co_hoi="CH-10",
                bat_dau_luc="2026-11-01 08:30:00",
                trang_thai="xong",
                cac_buoc=json.dumps(doc.cac_buoc),
            )
            with pytest.raises(ValueError):
                doc_sai.validate()

            # Đi tuần tự 1..7 trên controller
            for s in range(1, 8):
                doc.hoan_thanh_buoc(s, f"2026-11-0{s} 10:00:00")
            doc.validate()
            assert doc.trang_thai == "xong"

            # Chặn lùi trạng thái hoặc đổi cơ hội khi đã xong
            truoc = copy.deepcopy(doc)
            doc.get_doc_before_save = lambda: truoc
            doc.trang_thai = "dang_chay"
            with pytest.raises(ValueError):
                doc.validate()
        finally:
            sys.modules.pop("linhx_core.agent.doctype.lx_pilot.lx_pilot", None)
            pkg = sys.modules.get("linhx_core.agent.doctype.lx_pilot")
            if pkg is not None and hasattr(pkg, "lx_pilot"):
                delattr(pkg, "lx_pilot")
