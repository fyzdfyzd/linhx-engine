"""Unit test cho co_hoi và controller LXCoHoi."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import types

_CORE_DIR = str(Path(__file__).resolve().parents[4])
if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

from linhx_core.crm import co_hoi


def _nap_lx_co_hoi():
    if "frappe.model.document" not in sys.modules:
        frappe_mod = sys.modules.setdefault("frappe", types.ModuleType("frappe"))
        model_mod = sys.modules.setdefault("frappe.model", types.ModuleType("frappe.model"))
        doc_mod = sys.modules.setdefault("frappe.model.document", types.ModuleType("frappe.model.document"))

        class _Document:
            pass

        doc_mod.Document = _Document
        model_mod.document = doc_mod
        frappe_mod.model = model_mod
    from linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi import LXCoHoi

    return LXCoHoi


def test_viec_cho_han_giao_sai_dinh_dang_va_thieu():
    ds = [
        {"name": "CH_TRONG", "phu_trach": "", "han_giao": ""},
        {"name": "CH_DUNG", "phu_trach": None, "han_giao": "2026-11-09 10:00:00"},
        {"name": "CH_SAI", "phu_trach": None, "han_giao": "khong-phai-ngay"},
    ]
    vc = co_hoi.viec_cho(ds, "2026-11-09 09:00:00")
    theo_ten = {x["name"]: x for x in vc}
    assert theo_ten["CH_SAI"]["qua_han"] is True
    assert theo_ten["CH_DUNG"]["qua_han"] is False
    assert theo_ten["CH_TRONG"]["qua_han"] is False
    assert [x["name"] for x in vc] == ["CH_SAI", "CH_DUNG", "CH_TRONG"]


def test_controller_before_insert_kep_han_giao_va_tu_giao():
    LXCoHoi = _nap_lx_co_hoi()
    doc = LXCoHoi()
    doc.name = "CH-TEST-1"
    doc.creation = "2026-11-09 08:00:00"
    doc.han_giao = "2026-11-09 12:00:00"
    doc._ds_phu_trach = ["nv1@linhx.vn", "nv2@linhx.vn"]
    doc._ds_co_hoi_mo = [{"phu_trach": "nv1@linhx.vn", "trang_thai": "moi"}]
    doc.before_insert()
    assert doc.han_giao == "2026-11-09 09:00:00"
    assert doc.phu_trach == "nv2@linhx.vn"
    assert doc.trang_thai == "moi"
