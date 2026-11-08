"""Kiểm thử đơn vị cho linhx_core.ban và linhx_core.api_ban_dieu_hanh."""
from datetime import datetime
import importlib
import sys
from unittest.mock import MagicMock, patch

from linhx_core import ban


def test_tong_hop_bien_gio_va_dinh_dang():
    luc = "2026-11-09 12:00:00"
    jobs = [
        {"name": "J1", "trang_thai": "cho_duyet", "creation": "2026-11-09 08:00:00"},
        {"name": "J2", "trang_thai": "cho", "creation": "2026-11-09 11:00:00"},
        {"name": "J3", "trang_thai": "cho_duyet", "creation": datetime(2026, 11, 9, 10, 0, 0)},
        {"name": "J4", "trang_thai": "cho_duyet", "creation": ""},
    ]
    nguoi = [
        {"name": "N_DUNG_BIEN_DUOI", "creation": "2026-11-08 12:00:00"},
        {"name": "N_NGOAI_BIEN_DUOI", "creation": "2026-11-08 11:59:59"},
        {"name": "N_DUNG_LUC", "creation": "2026-11-09 12:00:00"},
        {"name": "N_ISO", "creation": "2026-11-09T11:30:00.123456"},
    ]
    don = [
        {"name": "D1", "creation": "2026-11-09 11:00:00", "so_tien": 99000},
        {"name": "D2", "creation": "2026-11-08 11:59:59", "so_tien": 5000},
    ]
    kq = ban.tong_hop(jobs, nguoi, don, luc, gio=24)
    assert [x["name"] for x in kq["viec_cho"]] == ["J3", "J1", "J4"]
    assert [x["name"] for x in kq["lead_moi"]] == ["N_DUNG_LUC", "N_ISO", "N_DUNG_BIEN_DUOI"]
    assert [x["name"] for x in kq["don_moi"]] == ["D1"]


def test_api_ban_dieu_hanh_quyen_va_du_lieu():
    fake_frappe = MagicMock()
    fake_frappe.whitelist.return_value = lambda fn: fn
    fake_frappe.session.user = "dh@test.local"
    fake_frappe.get_roles.return_value = ["LX Operator"]
    fake_frappe.db.exists.return_value = True

    def fake_get_all(dt, **kwargs):
        if dt == "LX Job":
            return [{"name": "J-9", "workflow": "ai-noi-gi-ve-brand", "trang_thai": "cho_duyet", "creation": "2026-11-09 10:00:00"}]
        if dt == "LX Nguoi":
            return [{"name": "N-1", "ho_ten": "Lan", "creation": "2026-11-09 11:30:00"}]
        if dt == "LX Don":
            return [{"name": "D-1", "so_tien": 99000, "creation": "2026-11-09 11:45:00"}]
        return []

    fake_frappe.get_all.side_effect = fake_get_all
    fake_utils = MagicMock()
    fake_utils.now_datetime.return_value = datetime(2026, 11, 9, 12, 0, 0)

    with patch.dict(sys.modules, {"frappe": fake_frappe, "frappe.utils": fake_utils}):
        sys.modules.pop("linhx_core.api_ban_dieu_hanh", None)
        api_bdh = importlib.import_module("linhx_core.api_ban_dieu_hanh")
        kq = api_bdh.ban(gio=24)
        assert [x["name"] for x in kq["viec_cho"]] == ["J-9"]
        assert [x["name"] for x in kq["lead_moi"]] == ["N-1"]
        assert [x["name"] for x in kq["don_moi"]] == ["D-1"]
