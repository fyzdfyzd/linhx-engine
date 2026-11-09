"""Kiểm thử đơn vị cho linhx_core.crm.t1 và linhx_core.crm.api_form (D2)."""
from __future__ import annotations

import json
import sys
import types
from unittest.mock import patch

import pytest

from linhx_core.crm import dong_y, t1

LUC_1 = "2026-11-09 09:00:00"
LUC_2 = "2026-11-09 09:05:00"
LUC_3 = "2026-11-09 09:10:00"


def test_t1_ghi_ket_qua_nguoi_moi_va_dong_y_mot_buoc():
    r = t1.ghi_ket_qua(
        {
            "email": "Lan@VD.vn",
            "tong": 12,
            "muc": "Sẵn sàng một phần",
            "dong_y_lien_he": True,
            "dong_y_marketing": True,
            "nguon": "gia-mao-tu-client",
        },
        [],
        [],
        LUC_1,
    )
    n = r["nguoi"]
    assert n["nguon"] == "T1"
    assert n["tang_pheu"] == "moi"
    assert n["t1_tong"] == 12
    assert n["t1_muc"] == "Sẵn sàng một phần"
    assert [(x["muc_dich"], x["dong_y"]) for x in r["so_dong_y"]] == [
        ("lien_he", True),
        ("marketing", True),
    ]


def test_t1_nguoi_da_co_khong_ghi_de_du_lieu_cu_va_khong_ghi_de_rut_dong_y():
    cu = [
        {
            "name": "NGUOI-001",
            "ho_ten": "Lan Gốc",
            "email": "lan@vd.vn",
            "zalo": "zalo_goc",
            "nguon": "trang-ifagent",
            "tang_pheu": "lien_he",
            "t1_tong": 12,
            "t1_muc": "Sẵn sàng một phần",
        }
    ]
    so_cu = [
        {"nguoi": "NGUOI-001", "muc_dich": "lien_he", "dong_y": True, "luc": LUC_1, "nguon": "T1"},
        {"nguoi": "NGUOI-001", "muc_dich": "marketing", "dong_y": True, "luc": LUC_1, "nguon": "T1"},
        {"nguoi": "NGUOI-001", "muc_dich": "marketing", "dong_y": False, "luc": LUC_2, "nguon": "khach_rut"},
    ]
    r = t1.ghi_ket_qua(
        {
            "ho_ten": "Kẻ Lạ Ghi Đè",
            "email": "LAN@vd.vn",
            "zalo": "zalo_ke_la",
            "nguon": "client_hack",
            "tong": 20,
            "muc": "Sẵn sàng",
            "dong_y_lien_he": True,
            "dong_y_marketing": True,
        },
        cu,
        so_cu,
        LUC_3,
    )
    assert len(r["ds_nguoi"]) == 1
    n = r["nguoi"]
    assert n["ho_ten"] == "Lan Gốc"
    assert n["zalo"] == "zalo_goc"
    assert n["nguon"] == "trang-ifagent"
    assert n["tang_pheu"] == "lien_he"
    assert n["t1_tong"] == 12
    assert n["t1_muc"] == "Sẵn sàng một phần"
    assert n["lich_su_t1"] == [{"luc": LUC_3, "t1_tong": 20, "t1_muc": "Sẵn sàng"}]

    # marketing đã rút (dong_y=False ở LUC_2) nên không được ghi đè thành True
    assert dong_y.hieu_luc(r["so_dong_y"], "NGUOI-001", "marketing") is False
    assert dong_y.hieu_luc(r["so_dong_y"], "NGUOI-001", "lien_he") is True
    assert [(x["muc_dich"], x["dong_y"]) for x in r["so_dong_y"]] == [
        ("lien_he", True),
        ("marketing", True),
        ("marketing", False),
        ("lien_he", True),
    ]


def test_t1_gioi_han_do_dai_va_honeypot():
    with pytest.raises(ValueError):
        t1.ghi_ket_qua(
            {"email": "a@vd.vn", "ho_ten": "A" * 121, "tong": 12, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True},
            [],
            [],
            LUC_1,
        )
    with pytest.raises(ValueError):
        t1.ghi_ket_qua(
            {"email": "a" * 250 + "@vd.vn", "tong": 12, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True},
            [],
            [],
            LUC_1,
        )
    with pytest.raises(ValueError):
        t1.ghi_ket_qua(
            {"zalo": "z" * 65, "tong": 12, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True},
            [],
            [],
            LUC_1,
        )
    with pytest.raises(ValueError):
        t1.ghi_ket_qua(
            {"email": "a@vd.vn", "website": "http://spam.local", "tong": 12, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True},
            [],
            [],
            LUC_1,
        )


class _DocGia:
    def __init__(self, data: dict, kho: dict[str, list[dict]]):
        self._kho = kho
        self.flags = types.SimpleNamespace(ignore_permissions=False)
        for k, v in data.items():
            setattr(self, k, v)

    def insert(self, ignore_permissions: bool = False):
        bang = self._kho.setdefault(self.doctype, [])
        if not getattr(self, "name", None):
            self.name = f"{self.doctype.replace(' ', '-')}-{len(bang) + 1}"
        ban_ghi = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "flags"
        }
        bang.append(ban_ghi)
        return self

    def save(self, ignore_permissions: bool = False):
        bang = self._kho.setdefault(self.doctype, [])
        for idx, item in enumerate(bang):
            if item.get("name") == self.name:
                cap_nhat = dict(item)
                for k, v in self.__dict__.items():
                    if not k.startswith("_") and k != "flags":
                        cap_nhat[k] = v
                bang[idx] = cap_nhat
                break
        return self


def _tao_frappe_gia(kho: dict[str, list[dict]]):
    frappe_mod = types.ModuleType("frappe")
    rate_mod = types.ModuleType("frappe.rate_limiter")

    class ValidationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    frappe_mod.ValidationError = ValidationError
    frappe_mod.PermissionError = PermissionError
    frappe_mod.local = types.SimpleNamespace(
        site="ifagent",
        request_ip="127.0.0.1",
        response={},
        form_dict={},
        request=None,
    )
    frappe_mod.conf = {}

    def whitelist(*_a, **_kw):
        def _wrap(fn):
            return fn
        return _wrap

    def rate_limit(*_a, **_kw):
        def _wrap(fn):
            return fn
        return _wrap

    rate_mod.rate_limit = rate_limit
    frappe_mod.whitelist = whitelist

    def throw(msg, exc=ValidationError):
        if isinstance(exc, type) and issubclass(exc, Exception):
            raise exc(msg)
        raise ValidationError(msg)

    frappe_mod.throw = throw
    frappe_mod.cache = lambda: None

    def get_all(doctype, filters=None, or_filters=None, fields=None, **_kw):
        ds = list(kho.get(doctype, []))
        if isinstance(filters, dict):
            for k, v in filters.items():
                ds = [x for x in ds if x.get(k) == v]
        if isinstance(or_filters, list) and or_filters:
            ket = []
            for x in ds:
                khop = False
                for cond in or_filters:
                    if len(cond) == 4:
                        _, truong, toan_tu, gia_tri = cond
                    else:
                        truong, toan_tu, gia_tri = cond
                    val = x.get(truong)
                    if toan_tu == "in" and val in (gia_tri or []):
                        khop = True
                        break
                    if toan_tu == "=" and val == gia_tri:
                        khop = True
                        break
                if khop:
                    ket.append(x)
            ds = ket
        return [dict(x) for x in ds]

    def get_doc(arg1, arg2=None):
        if isinstance(arg1, dict):
            return _DocGia(arg1, kho)
        for item in kho.get(arg1, []):
            if item.get("name") == arg2:
                return _DocGia(dict(item, doctype=arg1), kho)
        raise KeyError(arg2)

    frappe_mod.get_all = get_all
    frappe_mod.get_doc = get_doc
    return frappe_mod, rate_mod


def test_api_nhan_ket_qua_t1_khong_lo_du_lieu_cu_va_ton_trong_rut_dong_y():
    kho: dict[str, list[dict]] = {"LX Nguoi": [], "LX Dong Y": []}
    frappe_mod, rate_mod = _tao_frappe_gia(kho)

    with patch.dict(sys.modules, {"frappe": frappe_mod, "frappe.rate_limiter": rate_mod}):
        sys.modules.pop("linhx_core.crm.api_form", None)
        import linhx_core.crm.api_form as api_form

        with patch("linhx_core.co_module._doc_cau_hinh_frappe", return_value={"bat_crm": 1}):
            # Lần 1: khách mới gửi email nhận kết quả T1
            res1 = api_form.nhan_ket_qua_t1(
                email="Khach1@VD.vn",
                ho_ten="Khách Gốc Bí Mật",
                tong=12,
                muc="Sẵn sàng một phần",
                dong_y_lien_he=True,
                dong_y_marketing=True,
                nguon="client-gia-mao",
            )
            assert res1["ok"] is True
            assert res1["ban_cai"] == "ifagent"
            assert res1["nguoi"] == "LX-Nguoi-1"
            assert "ho_ten" not in res1 and "email" not in res1
            assert len(kho["LX Nguoi"]) == 1
            assert kho["LX Nguoi"][0]["nguon"] == "T1"
            assert kho["LX Nguoi"][0]["tang_pheu"] == "moi"
            assert kho["LX Nguoi"][0]["t1_tong"] == 12

            # Khách rút đồng ý marketing (dong_y=0)
            kho["LX Dong Y"].append(
                {
                    "name": "LX-Dong-Y-3",
                    "nguoi": "LX-Nguoi-1",
                    "muc_dich": "marketing",
                    "dong_y": 0,
                    "luc": "2099-01-01 00:00:00",
                    "nguon": "khach_rut",
                }
            )

            # Lần 2: gửi lại với cùng email nhưng tên khác và điểm khác (19 - Sẵn sàng)
            res2 = api_form.nhan_ket_qua_t1(
                email="khach1@vd.vn",
                ho_ten="Kẻ Lạ Thăm Dò",
                zalo="zalo_ke_la",
                tong=19,
                muc="Sẵn sàng",
                dong_y_lien_he=True,
                dong_y_marketing=True,
            )
            # Phản hồi chỉ chứa điểm vừa gửi (19), KHÔNG lộ tên cũ, email cũ hay điểm cũ (12)
            chu_res2 = json.dumps(res2, ensure_ascii=False)
            assert "Khách Gốc Bí Mật" not in chu_res2
            assert "khach1@vd.vn" not in chu_res2
            assert res2["ket_qua_day_du"]["tong"] == 19
            assert res2["ket_qua_day_du"]["muc"] == "Sẵn sàng"

            # Trong DB: hồ sơ cũ giữ nguyên tên, điểm cũ (12) và marketing vẫn ở trạng thái rút (False)
            ng_db = kho["LX Nguoi"][0]
            assert ng_db["ho_ten"] == "Khách Gốc Bí Mật"
            assert ng_db.get("zalo") is None
            assert ng_db["t1_tong"] == 12
            assert ng_db["t1_muc"] == "Sẵn sàng một phần"
            ls_db = json.loads(ng_db["lich_su_t1"])
            assert len(ls_db) == 1 and ls_db[0]["t1_tong"] == 19

            assert dong_y.hieu_luc(kho["LX Dong Y"], "LX-Nguoi-1", "marketing") is False
            assert dong_y.hieu_luc(kho["LX Dong Y"], "LX-Nguoi-1", "lien_he") is True
            # Trình tự sổ đồng ý: lần 1 (lien_he=1, marketing=1), rút (marketing=0), lần 2 chỉ ghi thêm lien_he=1
            assert [(d["muc_dich"], int(d["dong_y"])) for d in kho["LX Dong Y"]] == [
                ("lien_he", 1),
                ("marketing", 1),
                ("marketing", 0),
                ("lien_he", 1),
            ]
