"""Kiểm thử hộp trắng cho form.py, t1.py và api_form (C2 + D2: gộp trùng, rút đồng ý, bảo mật K4)."""
from __future__ import annotations

import importlib
import json
import sys
import types
from unittest.mock import patch

import pytest

from linhx_core.crm import dong_y, form, t1

LUC_1 = "2026-11-09 09:00:00"
LUC_2 = "2026-11-09 09:05:00"
LUC_3 = "2026-11-09 09:10:00"


class _FakeDoc:
    def __init__(self, data: dict, kho: dict[str, list[dict]], bo_dem: dict[str, int]):
        self._kho = kho
        self._bo_dem = bo_dem
        self.doctype = data["doctype"]
        self.flags = types.SimpleNamespace(ignore_permissions=False)
        for k, v in data.items():
            setattr(self, k, v)
        self.name = data.get("name")

    def insert(self, ignore_permissions: bool = False):
        loai = self.doctype
        self._bo_dem[loai] = self._bo_dem.get(loai, 0) + 1
        tien_to = {
            "LX Nguoi": "LX-NGUOI",
            "LX Co Hoi": "LX-CH",
            "LX Dong Y": "LX-DY",
        }.get(loai, "DOC")
        self.name = f"{tien_to}-{self._bo_dem[loai]:04d}"
        ban_ghi = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k not in ("doctype", "flags")
        }
        ban_ghi["creation"] = f"2026-11-09 09:00:{self._bo_dem[loai]:02d}"
        self._kho.setdefault(loai, []).append(ban_ghi)
        return self

    def save(self, ignore_permissions: bool = False):
        bang = self._kho.setdefault(self.doctype, [])
        for idx, item in enumerate(bang):
            if item.get("name") == self.name:
                cap_nhat = dict(item)
                for k, v in self.__dict__.items():
                    if not k.startswith("_") and k not in ("doctype", "flags"):
                        cap_nhat[k] = v
                bang[idx] = cap_nhat
                break
        return self


def _tao_moi_truong_frappe(monkeypatch, site: str = "ifagent"):
    kho: dict[str, list[dict]] = {
        "LX Nguoi": [],
        "LX Co Hoi": [],
        "LX Dong Y": [],
    }
    bo_dem: dict[str, int] = {}
    lich_su_get_all: list[dict] = []

    fake_frappe = types.ModuleType("frappe")

    class ValidationError(Exception):
        pass

    class PermissionError(Exception):
        pass

    class DuplicateEntryError(Exception):
        pass

    fake_frappe.ValidationError = ValidationError
    fake_frappe.PermissionError = PermissionError
    fake_frappe.DuplicateEntryError = DuplicateEntryError
    fake_frappe.local = types.SimpleNamespace(
        site=site,
        request_ip="127.0.0.1",
        response={},
        form_dict={},
        request=None,
    )
    fake_frappe.conf = {}

    def whitelist(allow_guest: bool = False, methods=None):
        def _dec(fn):
            return fn
        return _dec

    fake_frappe.whitelist = whitelist
    fake_frappe.cache = lambda: None

    def throw(msg, exc=ValidationError):
        if isinstance(exc, type) and issubclass(exc, Exception):
            raise exc(msg)
        raise ValidationError(msg)

    fake_frappe.throw = throw

    def get_single(doctype: str):
        if doctype == "LX Cau Hinh":
            return types.SimpleNamespace(bat_crm=1, bat_pay=1)
        return types.SimpleNamespace()

    fake_frappe.get_single = get_single

    def get_all(
        doctype: str,
        fields=None,
        filters=None,
        or_filters=None,
        order_by=None,
        limit=None,
        **kwargs,
    ):
        lich_su_get_all.append(
            {
                "doctype": doctype,
                "fields": fields,
                "filters": filters,
                "or_filters": or_filters,
                "order_by": order_by,
                "limit": limit,
            }
        )
        ds = list(kho.get(doctype, []))
        if isinstance(filters, dict):
            ds = [
                d
                for d in ds
                if all(d.get(k) == v for k, v in filters.items())
            ]
        if or_filters:
            ket_qua_loc = []
            for d in ds:
                khop = False
                for dieu_kien in or_filters:
                    _, truong, toan_tu, gia_tri = dieu_kien
                    val = d.get(truong)
                    if toan_tu == "in" and val in (gia_tri or []):
                        khop = True
                        break
                    if toan_tu == "=" and val == gia_tri:
                        khop = True
                        break
                    if toan_tu == "like" and isinstance(val, str) and isinstance(gia_tri, str):
                        mau = gia_tri.strip("%")
                        if mau in val:
                            khop = True
                            break
                if khop:
                    ket_qua_loc.append(d)
            ds = ket_qua_loc
        if limit is not None:
            ds = ds[: int(limit)]
        return [dict(x) for x in ds]

    def _get_doc(arg1, arg2=None):
        if isinstance(arg1, dict):
            return _FakeDoc(arg1, kho, bo_dem)
        for item in kho.get(arg1, []):
            if item.get("name") == arg2:
                return _FakeDoc(dict(item, doctype=arg1), kho, bo_dem)
        raise KeyError(arg2)

    fake_frappe.get_all = get_all
    fake_frappe.get_doc = _get_doc

    class _FakeDB:
        def get_single_value(self, doctype: str, fieldname: str):
            if doctype == "LX Cau Hinh":
                return 1
            return None

        def set_value(self, doctype: str, name: str, fieldname, value=None, **kwargs):
            for ban_ghi in kho.get(doctype, []):
                if ban_ghi.get("name") == name:
                    if isinstance(fieldname, dict):
                        ban_ghi.update(fieldname)
                    else:
                        ban_ghi[fieldname] = value

    fake_frappe.db = _FakeDB()

    fake_rl = types.ModuleType("frappe.rate_limiter")
    fake_rl.rate_limit = lambda **kw: (lambda fn: fn)

    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    monkeypatch.setitem(sys.modules, "frappe.rate_limiter", fake_rl)
    monkeypatch.delitem(sys.modules, "linhx_core.crm.api_form", raising=False)
    api_form = importlib.import_module("linhx_core.crm.api_form")
    api_form._BO_DEM_KHOA_DU_PHONG.clear()
    return api_form, kho, lich_su_get_all


def test_nhan_form_gop_trung_khong_ghi_de_du_lieu_cu(monkeypatch):
    api_form, kho, lich_su = _tao_moi_truong_frappe(monkeypatch)
    try:
        r1 = api_form.nhan_form(
            ho_ten="Nguyễn Thị Lan",
            dien_thoai="0912345678",
            email="lan@vd.vn",
            nhu_cau="Tư vấn lần 1",
            dong_y_lien_he=True,
            dong_y_marketing=False,
        )
        assert r1["ok"] is True
        assert r1["ban_cai"] == "ifagent"
        assert r1["nguoi"] == "LX-NGUOI-0001"
        assert "ho_ten" not in r1 and "email" not in r1 and "t1_tong" not in r1
        assert len(kho["LX Nguoi"]) == 1
        assert len(kho["LX Co Hoi"]) == 1
        assert len(kho["LX Dong Y"]) == 1

        # Gửi lần 2 cùng SĐT với tên/email khác và tick thêm marketing
        r2 = api_form.nhan_form(
            ho_ten="Tên Giả Mạo",
            dien_thoai="+84912345678",
            email="giamao@vd.vn",
            nhu_cau="Tư vấn lần 2",
            dong_y_lien_he=True,
            dong_y_marketing=True,
        )
        assert r2["ok"] is True
        assert r2["nguoi"] == "LX-NGUOI-0001"
        assert len(kho["LX Nguoi"]) == 1, "Gửi lại cùng SĐT không được tạo LX Nguoi trùng"
        # Dữ liệu cũ trên LX Nguoi không bị ghi đè bằng dữ liệu form
        assert kho["LX Nguoi"][0]["ho_ten"] == "Nguyễn Thị Lan"
        assert kho["LX Nguoi"][0]["email"] == "lan@vd.vn"
        assert len(kho["LX Co Hoi"]) == 2
        assert "giamao@vd.vn" in (kho["LX Co Hoi"][1].get("ghi_chu") or "")
        assert dong_y.hieu_luc(kho["LX Dong Y"], "LX-NGUOI-0001", "marketing") is False
        assert len(kho["LX Dong Y"]) == 3, "Ghi đủ 3 dòng (lien_he lần 1, lien_he lần 2, marketing chờ xác minh lần 2)"
        assert [(d["muc_dich"], d["dong_y"], d.get("trang_thai")) for d in kho["LX Dong Y"]] == [
            ("lien_he", 1, None),
            ("lien_he", 1, None),
            ("marketing", 0, "cho_xac_minh"),
        ], "Đồng ý marketing qua form công khai ở trạng thái cho_xac_minh cho tới khi xác nhận OTP"

        truy_van_nguoi = [q for q in lich_su if q["doctype"] == "LX Nguoi"]
        for q in truy_van_nguoi:
            assert q["or_filters"], "Phải lọc theo khoá liên hệ, không quét toàn bảng"
            assert q["limit"] == api_form.GIOI_HAN_TRUY_VAN_NGUOI
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


def test_khong_ghi_de_dong_rut_dong_y(monkeypatch):
    api_form, kho, _ = _tao_moi_truong_frappe(monkeypatch)
    try:
        api_form.nhan_form(
            ho_ten="Trần Minh",
            dien_thoai="0987654321",
            email="minh@vd.vn",
            nhu_cau="Lần 1",
            dong_y_lien_he=True,
            dong_y_marketing=True,
        )
        ma_nguoi = kho["LX Nguoi"][0]["name"]
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is False

        # Khách rút đồng ý marketing (dong_y=0)
        kho["LX Dong Y"].append(
            {
                "name": "LX-DY-RUT",
                "nguoi": ma_nguoi,
                "muc_dich": "marketing",
                "dong_y": 0,
                "luc": "2099-01-01 00:00:00",
                "nguon": "khach-rut",
            }
        )
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is False

        # Kẻ lạ gửi lại form với dong_y_marketing=True -> không được ghi đè dòng rút đồng ý
        api_form.nhan_form(
            ho_ten="Trần Minh",
            dien_thoai="0987654321",
            nhu_cau="Lần 2",
            dong_y_lien_he=True,
            dong_y_marketing=True,
        )
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is False
        assert [d.get("trang_thai") for d in kho["LX Dong Y"] if d["muc_dich"] == "marketing"] == [
            "cho_xac_minh",
            None,
        ]
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


def test_chan_nguon_client_va_gioi_han_do_dai(monkeypatch):
    api_form, kho, _ = _tao_moi_truong_frappe(monkeypatch)
    try:
        api_form.nhan_form(
            ho_ten="Lê Hoa",
            dien_thoai="0901112233",
            nhu_cau="Kiểm nguồn",
            dong_y_lien_he=True,
            nguon="nguon-gia-mao-tu-client",
        )
        assert kho["LX Co Hoi"][0]["nguon"] == "trang-ifagent"
        assert kho["LX Dong Y"][0]["nguon"] == "trang-ifagent"

        with pytest.raises(Exception):
            api_form.nhan_form(
                ho_ten="A" * (form.DO_DAI_TOI_DA_HO_TEN + 1),
                dien_thoai="0901112233",
                dong_y_lien_he=True,
            )
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


def test_khop_sdt_ngoac_va_rut_dong_y_nguoi_thu_hai(monkeypatch):
    api_form, kho, _ = _tao_moi_truong_frappe(monkeypatch)
    try:
        kho["LX Nguoi"].append(
            {
                "name": "LX-NGUOI-CU1",
                "ho_ten": "Người Một",
                "dien_thoai": "(0994) / 178 / 778",
                "email": "mot@vd.vn",
                "creation": "2026-11-09 08:00:01",
            }
        )
        kho["LX Nguoi"].append(
            {
                "name": "LX-NGUOI-CU2",
                "ho_ten": "Người Hai",
                "dien_thoai": "0909998887",
                "email": "hai@vd.vn",
                "creation": "2026-11-09 08:00:02",
            }
        )
        kho["LX Dong Y"].append(
            {
                "name": "LX-DY-1",
                "nguoi": "LX-NGUOI-CU1",
                "muc_dich": "marketing",
                "dong_y": 1,
                "luc": "2026-11-09 08:10:00",
                "nguon": "trang-ifagent",
            }
        )
        kho["LX Dong Y"].append(
            {
                "name": "LX-DY-2",
                "nguoi": "LX-NGUOI-CU2",
                "muc_dich": "marketing",
                "dong_y": 0,
                "luc": "2099-01-01 00:00:00",
                "nguon": "khach-rut",
            }
        )

        r = api_form.nhan_form(
            ho_ten="Khách Gửi Lại",
            dien_thoai="0994178778",
            email="hai@vd.vn",
            nhu_cau="Kiểm gộp SĐT định dạng lạ + sổ người thứ hai",
            dong_y_lien_he=True,
            dong_y_marketing=True,
        )
        assert r["ok"] is True
        assert r["nguoi"] == "LX-NGUOI-CU1"
        assert len(kho["LX Nguoi"]) == 2
        cac_dy_mkt_moi = [
            d
            for d in kho["LX Dong Y"]
            if d.get("muc_dich") == "marketing" and d.get("name") not in ("LX-DY-1", "LX-DY-2")
        ]
        assert not cac_dy_mkt_moi, "Phải tôn trọng dòng rút đồng ý trên bản ghi khớp thứ hai"
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


def test_luu_hoac_lay_nguoi_c2_chi_bat_duplicate_entry_error(monkeypatch):
    api_form, kho, _ = _tao_moi_truong_frappe(monkeypatch)
    try:
        fake_frappe = sys.modules["frappe"]

        def _insert_trung(self, ignore_permissions: bool = False):
            kho["LX Nguoi"].append(
                {
                    "name": "LX-NGUOI-RACE-C2",
                    "dien_thoai": "0912345678",
                    "email": "racec2@vd.vn",
                }
            )
            raise fake_frappe.DuplicateEntryError("Trùng khoá")

        with patch.object(_FakeDoc, "insert", _insert_trung):
            ma = api_form._luu_hoac_lay_nguoi(
                {"ho_ten": "Lan", "dien_thoai": "0912345678", "email": "racec2@vd.vn"},
                [],
                du_lieu_goc={"dien_thoai": "0912345678", "email": "racec2@vd.vn"},
            )
            assert ma == "LX-NGUOI-RACE-C2"

        def _insert_loi_khac(self, ignore_permissions: bool = False):
            raise RuntimeError("Lỗi cơ sở dữ liệu thật C2")

        with patch.object(_FakeDoc, "insert", _insert_loi_khac):
            with pytest.raises(RuntimeError, match="Lỗi cơ sở dữ liệu thật C2"):
                api_form._luu_hoac_lay_nguoi(
                    {"ho_ten": "Lan", "dien_thoai": "0912345678", "email": "racec2@vd.vn"},
                    [],
                    du_lieu_goc={"dien_thoai": "0912345678", "email": "racec2@vd.vn"},
                )
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


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

    class DuplicateEntryError(Exception):
        pass

    frappe_mod.ValidationError = ValidationError
    frappe_mod.PermissionError = PermissionError
    frappe_mod.DuplicateEntryError = DuplicateEntryError
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

            res2 = api_form.nhan_ket_qua_t1(
                email="khach1@vd.vn",
                ho_ten="Kẻ Lạ Thăm Dò",
                zalo="zalo_ke_la",
                tong=19,
                muc="Sẵn sàng",
                dong_y_lien_he=True,
                dong_y_marketing=True,
            )
            chu_res2 = json.dumps(res2, ensure_ascii=False)
            assert "Khách Gốc Bí Mật" not in chu_res2
            assert "khach1@vd.vn" not in chu_res2
            assert res2["ket_qua_day_du"]["tong"] == 19
            assert res2["ket_qua_day_du"]["muc"] == "Sẵn sàng"

            ng_db = kho["LX Nguoi"][0]
            assert ng_db["ho_ten"] == "Khách Gốc Bí Mật"
            assert ng_db.get("zalo") is None
            assert ng_db["t1_tong"] == 12
            assert ng_db["t1_muc"] == "Sẵn sàng một phần"
            ls_db = json.loads(ng_db["lich_su_t1"])
            assert len(ls_db) == 1 and ls_db[0]["t1_tong"] == 19

            assert dong_y.hieu_luc(kho["LX Dong Y"], "LX-Nguoi-1", "marketing") is False
            assert dong_y.hieu_luc(kho["LX Dong Y"], "LX-Nguoi-1", "lien_he") is True
            assert [(d["muc_dich"], int(d["dong_y"]), d.get("trang_thai")) for d in kho["LX Dong Y"]] == [
                ("lien_he", 1, None),
                ("marketing", 0, "cho_xac_minh"),
                ("marketing", 0, None),
                ("lien_he", 1, None),
            ]


def test_api_xac_nhan_marketing_db_post_va_get(monkeypatch):
    api_form, kho, _ = _tao_moi_truong_frappe(monkeypatch)
    try:
        r = api_form.nhan_form(
            ho_ten="Phạm Thu",
            dien_thoai="0911222333",
            email="thu@vd.vn",
            nhu_cau="Kiểm C2B",
            dong_y_lien_he=True,
            dong_y_marketing=True,
        )
        ma_nguoi = r["nguoi"]
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is False
        assert len(kho.get("LX Xac Minh Marketing", [])) == 1

        # Phát mã cố định để kiểm GET vs POST trên DB
        api_form._luu_yeu_cau_otp_marketing_db(
            "thu@vd.vn",
            ma_nguoi,
            kho["LX Dong Y"],
            dong_y.bay_gio(),
            "trang-ifagent",
            ma_otp="654321",
        )
        assert "654321" not in json.dumps(kho["LX Xac Minh Marketing"])

        # Gọi GET không tiêu thụ mã và không ghi đồng ý
        kq_get = api_form.xac_nhan_marketing(
            email="thu@vd.vn",
            nguoi=ma_nguoi,
            ma_nhap="654321",
            phuong_thuc="GET",
        )
        assert kq_get["ok"] is False and kq_get.get("can_post") is True
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is False

        # Gọi POST kích hoạt đồng ý marketing
        kq_post = api_form.xac_nhan_marketing(
            email="thu@vd.vn",
            nguoi=ma_nguoi,
            ma_nhap="654321",
            phuong_thuc="POST",
        )
        assert kq_post["ok"] is True
        assert dong_y.hieu_luc(kho["LX Dong Y"], ma_nguoi, "marketing") is True

        # Gọi lại POST lần 2 với cùng mã -> từ chối
        kq_lan2 = api_form.xac_nhan_marketing(
            email="thu@vd.vn",
            nguoi=ma_nguoi,
            ma_nhap="654321",
            phuong_thuc="POST",
        )
        assert kq_lan2["ok"] is False and kq_lan2.get("ly_do") == "da_dung"
    finally:
        sys.modules.pop("linhx_core.crm.api_form", None)


def test_luu_hoac_lay_nguoi_t1_chi_bat_duplicate_entry_error():
    kho: dict[str, list[dict]] = {"LX Nguoi": [], "LX Dong Y": []}
    frappe_mod, rate_mod = _tao_frappe_gia(kho)

    with patch.dict(sys.modules, {"frappe": frappe_mod, "frappe.rate_limiter": rate_mod}):
        sys.modules.pop("linhx_core.crm.api_form", None)
        import linhx_core.crm.api_form as api_form

        def _insert_trung(self, ignore_permissions: bool = False):
            kho["LX Nguoi"].append(
                {
                    "name": "LX-Nguoi-Race",
                    "email": "race@vd.vn",
                    "nguon": "T1",
                    "tang_pheu": "moi",
                }
            )
            raise frappe_mod.DuplicateEntryError("Trùng khoá")

        with patch.object(_DocGia, "insert", _insert_trung):
            ma = api_form._luu_hoac_lay_nguoi_t1(
                {"email": "race@vd.vn", "t1_tong": 12, "t1_muc": "Sẵn sàng một phần"},
                [],
                du_lieu_goc={"email": "race@vd.vn"},
            )
            assert ma == "LX-Nguoi-Race"

        def _insert_loi_khac(self, ignore_permissions: bool = False):
            raise RuntimeError("Lỗi cơ sở dữ liệu thật")

        with patch.object(_DocGia, "insert", _insert_loi_khac):
            with pytest.raises(RuntimeError, match="Lỗi cơ sở dữ liệu thật"):
                api_form._luu_hoac_lay_nguoi_t1(
                    {"email": "race@vd.vn", "t1_tong": 12, "t1_muc": "Sẵn sàng một phần"},
                    [],
                    du_lieu_goc={"email": "race@vd.vn"},
                )
