"""Kiểm thử đơn vị cho linhx_core.pheu và linhx_core.api_pheu."""
import importlib
import sys
from unittest.mock import MagicMock, patch

from linhx_core import pheu


def test_dem_6_tang():
    nguoi = [
        {"name": "N1", "nguon": "T1"},
        {"name": "N2", "nguon": "trang-ifagent"},
        {"name": "N3", "nguon": "T1"},
        {"name": "N4"},
        {"name": "N5", "nguon": "zalo"},
    ]
    co_hoi = [
        {"name": "C1", "nguoi": "N1"},
        {"name": "C2", "nguoi": "N2"},
        {"name": "C3", "nguoi": "N1"},
    ]
    don = [
        {"ma": "D1", "nguoi": "N2", "trang_thai": "da_tra"},
        {"ma": "D2", "nguoi": "N2", "trang_thai": "da_tra"},
        {"ma": "D3", "nguoi": "N3", "trang_thai": "cho_tra"},
        {"ma": "D4", "nguoi": "N4", "trang_thai": "da_tra"},
        {"ma": "D5", "nguoi": "N4", "trang_thai": "huy"},
    ]
    assert pheu.TANG == ("biet", "moi", "lien_he", "co_hoi_don", "khach", "quay_lai")
    assert pheu.dem(nguoi, co_hoi, don, 120) == {
        "biet": 120,
        "moi": 2,
        "lien_he": 5,
        "co_hoi_don": 4,
        "khach": 2,
        "quay_lai": 1,
    }
    assert pheu.dem([], [], [], 0) == {t: 0 for t in pheu.TANG}


def test_api_pheu_quyen_va_du_lieu():
    fake_frappe = MagicMock()
    fake_frappe.whitelist.return_value = lambda fn: fn
    fake_frappe.session.user = "dh@test.local"
    fake_frappe.get_roles.return_value = ["LX Operator"]
    fake_frappe.db.exists.return_value = True

    def fake_get_all(dt, **kwargs):
        if dt == "LX Nguoi":
            return [{"name": "N1", "nguon": "T1"}, {"name": "N2", "nguon": "zalo"}]
        if dt == "LX Co Hoi":
            return [{"name": "C1", "nguoi": "N1"}]
        if dt == "LX Don":
            return [
                {"name": "D1", "ma": "D1", "nguoi": "N2", "trang_thai": "da_tra"},
                {"name": "D2", "ma": "D2", "nguoi": "N2", "trang_thai": "da_tra"},
            ]
        return []

    fake_frappe.get_all.side_effect = fake_get_all

    with patch.dict(sys.modules, {"frappe": fake_frappe}):
        sys.modules.pop("linhx_core.api_pheu", None)
        api_ph = importlib.import_module("linhx_core.api_pheu")
        kq = api_ph.pheu(luot_xem=50)
        assert kq == {
            "biet": 50,
            "moi": 1,
            "lien_he": 2,
            "co_hoi_don": 2,
            "khach": 1,
            "quay_lai": 1,
        }
