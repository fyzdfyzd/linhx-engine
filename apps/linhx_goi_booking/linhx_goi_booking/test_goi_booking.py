"""Kiểm thử đơn vị cho gói `linhx_goi_booking` (F2 / G3):
- nạp thuần Python không cần Frappe
- kiểm giờ làm việc 8–18h giờ VN, chặn trùng giờ, việc chờ (`dat_lich`)
- giao hàng `giao` cho `loai_giao == 'lich'` (cấp quyền dùng thật, không nuốt lỗi DB, trạng thái `tam_tinh_lich` khi không có DB/ds_lich)
- API đặt lịch `dat_lich_goi` / `viec_cho_lich_goi`, đồng ý liên hệ, rút đồng ý, gộp trùng Người, chống đoán hồ sơ và chống ghép kênh OTP
- đối chiếu trực tiếp (parity test) các hàm CRM/OTP/đơn vị trong `api_booking` với bản gốc `linhx_core.crm`.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import types
from unittest.mock import patch

import pytest

GOC_APPS = pathlib.Path(__file__).resolve().parents[2]
for p in (GOC_APPS / "linhx_core", GOC_APPS / "linhx_goi_booking"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from linhx_goi_booking import api_booking, dat_lich, giao


def test_nap_thuan_python_khong_can_frappe():
    with patch.dict(sys.modules, {"frappe": None}):
        for mod_name in (
            "linhx_goi_booking.dat_lich",
            "linhx_goi_booking.api_booking",
            "linhx_goi_booking.giao",
        ):
            sys.modules.pop(mod_name, None)
            mod = importlib.import_module(mod_name)
            assert mod is not None


def test_dat_lich_gio_lam_viec_va_mui_gio():
    # Đúng biên 08:00 -> 08:30 và 17:30 -> 18:00
    ds = dat_lich.dat_lich(
        [],
        {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 08:00:00", "phut": 30},
    )
    assert len(ds) == 1
    assert ds[0]["ket_thuc"] == "2026-11-10 08:30:00"
    assert ds[0]["trang_thai"] == "cho_goi"

    # Chuỗi UTC tương đương 09:00 giờ VN (02:00Z) được quy đổi đúng về giờ VN
    ds = dat_lich.dat_lich(
        ds,
        {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10T02:00:00Z", "phut": 30},
    )
    assert ds[-1]["bat_dau"] == "2026-11-10 09:00:00"
    assert ds[-1]["ket_thuc"] == "2026-11-10 09:30:00"

    # Ngoài giờ làm hoặc dữ liệu sai -> ValueError
    for gio_sai in (
        "2026-11-10 07:59:59",
        "2026-11-10 17:31:00",
        "2026-11-10 18:00:00",
        "2026-11-10",
        "",
    ):
        with pytest.raises(ValueError):
            dat_lich.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": gio_sai, "phut": 30},
            )

    for phut_sai in (0, -15, 601, True, "abc"):
        with pytest.raises(ValueError):
            dat_lich.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 09:00:00", "phut": phut_sai},
            )


def test_dat_lich_trung_gio_va_viec_cho():
    goc = [
        {
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 10:00:00",
            "ket_thuc": "2026-11-10 10:30:00",
            "phut": 30,
            "trang_thai": "cho_goi",
        },
        {
            "nguoi": "NG-02",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 11:00:00",
            "ket_thuc": "2026-11-10 11:30:00",
            "phut": 30,
            "trang_thai": "huy",
        },
    ]
    with pytest.raises(ValueError):
        dat_lich.dat_lich(
            goc,
            {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 10:15:00", "phut": 30},
        )

    moi = dat_lich.dat_lich(
        goc,
        {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 11:00:00", "phut": 30},
    )
    assert len(goc) == 2
    assert len(moi) == 3

    vc = dat_lich.viec_cho(moi, phu_trach="sale1@vd.vn")
    assert [x["nguoi"] for x in vc] == ["NG-01", "NG-03"]


def test_giao_lich_qua_luong_giao_hang_chung():
    from linhx_core import dang_ky_module, giao_hang

    ds_mod = dang_ky_module.quet(GOC_APPS)
    duong_ham = giao_hang.chon_ham("lich", ds_mod)
    assert duong_ham == "linhx_goi_booking.giao.giao"

    don = {
        "name": "DON-LICH-01",
        "ma": "DON-LICH-01",
        "goi": "GOI-TU-VAN",
        "nguoi": "NG-01",
        "phu_trach": "sale1@vd.vn",
        "bat_dau": "2026-11-10 09:00:00",
        "phut": 30,
        "so_tien": 500000,
        "trang_thai": "da_tra",
    }
    goi_dict = {
        "name": "GOI-TU-VAN",
        "ma": "GOI-TU-VAN",
        "gia": 500000,
        "gia_san": 400000,
        "loai_giao": "lich",
    }

    kho_lich: list[dict] = []
    kho_quyen: list[dict] = []
    kq = giao.giao(don, goi_dict, ds_lich=kho_lich, kho_quyen=kho_quyen)
    assert kq["ok"] is True
    assert kq["loai_giao"] == "lich"
    assert kq["trang_thai"] == "da_dat_lich"
    assert len(kho_lich) == 1
    assert kho_lich[0]["bat_dau"] == "2026-11-10 09:00:00"
    assert len(kho_quyen) == 1
    assert kho_quyen[0]["don"] == "DON-LICH-01"

    # Đơn chưa thanh toán hoặc dưới giá sàn -> từ chối
    with pytest.raises(ValueError):
        giao.giao({**don, "trang_thai": "cho_tra"}, goi_dict)
    with pytest.raises(ValueError):
        giao.giao({**don, "so_tien": 100000}, goi_dict)


def test_giao_lich_khong_nuot_loi_db_va_trang_thai_tam_tinh():
    don = {
        "name": "DON-LICH-02",
        "ma": "DON-LICH-02",
        "goi": "GOI-TU-VAN",
        "nguoi": "NG-01",
        "phu_trach": "sale1@vd.vn",
        "bat_dau": "2026-11-10 10:00:00",
        "phut": 30,
        "so_tien": 500000,
        "trang_thai": "da_tra",
    }
    goi_dict = {
        "name": "GOI-TU-VAN",
        "ma": "GOI-TU-VAN",
        "gia": 500000,
        "gia_san": 400000,
        "loai_giao": "lich",
    }

    # 1. Khi kho_quyen is None và cap_quyen_dung ném lỗi (hoặc không có DB) -> lỗi phải nổi lên, không tạo quyền giả
    with patch.dict(sys.modules, {"frappe": None}):
        with pytest.raises(RuntimeError):
            giao.giao(don, goi_dict)

    with patch.object(giao, "cap_quyen_dung", side_effect=RuntimeError("DB mất kết nối khi ghi LX Quyen Dung")):
        with pytest.raises(RuntimeError, match="DB mất kết nối"):
            giao.giao(don, goi_dict)

    # 2. Khi có DB nhưng truy vấn lịch hiện có bị lỗi -> không được nuốt lỗi thành ds_hien_co=[]
    fake_frappe = types.ModuleType("frappe")
    fake_frappe.db = types.SimpleNamespace(
        sql=lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("Lỗi SQL FOR UPDATE"))
    )
    fake_frappe.get_all = None
    with patch.dict(sys.modules, {"frappe": fake_frappe}):
        with pytest.raises(RuntimeError, match="Lỗi SQL FOR UPDATE"):
            giao.giao(don, goi_dict, kho_quyen=[])

    # 3. Khi không có Frappe DB và không truyền ds_lich (nhưng có truyền kho_quyen=[]) -> trả trang_thai == 'tam_tinh_lich'
    with patch.dict(sys.modules, {"frappe": None}):
        kq_tam = giao.giao(don, goi_dict, kho_quyen=[])
        assert kq_tam["trang_thai"] == "tam_tinh_lich"


def test_chon_kenh_otp_cho_nguoi_chong_ghep_kenh_nan_nhan():
    nan_nhan = {
        "name": "NG-NAN-NHAN",
        "ho_ten": "Nạn Nhân",
        "dien_thoai": "0912345678",
        "email": "nan.nhan@vd.vn",
        "zalo": "zalo_nan_nhan",
    }
    # Cùng kênh hợp lệ của chính nạn nhân -> trả kênh chuẩn
    assert (
        api_booking._chon_kenh_otp_cho_nguoi(
            nan_nhan,
            em_chuan="nan.nhan@vd.vn",
            dt_chuan="84912345678",
        )
        == "nan.nhan@vd.vn"
    )
    assert (
        api_booking._chon_kenh_otp_cho_nguoi(
            nan_nhan,
            dt_chuan="84912345678",
            zl_chuan="ZALO_NAN_NHAN",
        )
        == "84912345678"
    )

    # Kẻ tấn công ghép SĐT của nạn nhân với email của kẻ tấn công -> bị từ chối ("")
    assert (
        api_booking._chon_kenh_otp_cho_nguoi(
            nan_nhan,
            em_chuan="ke.tan.cong@evil.vn",
            dt_chuan="84912345678",
        )
        == ""
    )
    # Kẻ tấn công ghép email của nạn nhân với SĐT của kẻ tấn công -> bị từ chối ("")
    assert (
        api_booking._chon_kenh_otp_cho_nguoi(
            nan_nhan,
            em_chuan="nan.nhan@vd.vn",
            dt_chuan="84999999999",
        )
        == ""
    )
    # Kẻ tấn công ghép SĐT của nạn nhân với Zalo của kẻ tấn công -> bị từ chối ("")
    assert (
        api_booking._chon_kenh_otp_cho_nguoi(
            nan_nhan,
            dt_chuan="84912345678",
            zl_chuan="zalo_ke_tan_cong",
        )
        == ""
    )


def test_dong_y_rut_dong_y_gop_trung_va_chong_doan_nguoi_dung():
    """Kiểm thử riêng đường đồng ý / rút đồng ý (kể cả chờ xác minh OTP), gộp trùng (dedupe) và chống đoán hồ sơ."""
    # 1. Rút đồng ý: bỏ qua dòng cho_xac_minh, tôn trọng dòng rút đồng ý mới nhất
    so_dong_y = [
        {"nguoi": "NG-01", "muc_dich": "lien_he", "dong_y": True, "luc": "2026-11-10 08:00:00"},
        {"nguoi": "NG-01", "muc_dich": "lien_he", "dong_y": False, "luc": "2026-11-10 09:00:00"},
        {
            "nguoi": "NG-01",
            "muc_dich": "lien_he",
            "dong_y": True,
            "trang_thai": "cho_xac_minh",
            "luc": "2026-11-10 10:00:00",
        },
    ]
    assert api_booking._da_rut_dong_y(so_dong_y, "NG-01", "lien_he") is True

    # 2. Dedupe: _tim_nguoi_da_co khớp theo khoá gộp SĐT/email chuẩn hoá và _luu_hoac_lay_nguoi giữ nguyên mã cũ
    ds_cu = [{"name": "NG-GOC", "ho_ten": "Tên Gốc", "dien_thoai": "0912345678", "email": "goc@vd.vn"}]
    khop = api_booking._tim_nguoi_da_co({"ho_ten": "Tên Mới", "dien_thoai": "+84 912 345 678"}, ds_cu)
    assert khop is not None and khop["name"] == "NG-GOC"
    assert api_booking._luu_hoac_lay_nguoi({"ho_ten": "Tên Mới", "dien_thoai": "+84912345678"}, ds_cu) == "NG-GOC"


def test_doi_chieu_ham_crm_voi_ban_loi():
    """Đối chiếu trực tiếp (parity test) 11 hàm CRM/OTP/đơn vị trong `api_booking` với bản gốc `linhx_core.crm`."""
    from linhx_core.crm import co_hoi, form, quyen_don_vi, xac_minh_marketing

    # 1. _cac_dang_dien_thoai
    fake_frappe = types.ModuleType("frappe")
    kho_nguoi = [
        {
            "name": "NG-01",
            "creation": "2026-11-10 08:00:00",
            "ho_ten": "Khách A",
            "dien_thoai": "0912 345 678",
            "email": "khacha@vd.vn",
            "zalo": "zalo_a",
            "nguon": "trang-ifagent",
            "tang_pheu": "T0",
            "t1_tong": 10,
            "t1_muc": "A",
            "lich_su_t1": '[{"tong": 10}]',
        },
        {
            "name": "NG-02",
            "creation": "2026-11-10 08:05:00",
            "ho_ten": "Khách B",
            "dien_thoai": "(098) 765-4321",
            "email": "khachb@vd.vn",
            "zalo": "zalo_b",
            "nguon": "trang-ifagent",
            "tang_pheu": "T0",
            "t1_tong": 0,
            "t1_muc": "",
            "lich_su_t1": [],
        },
    ]
    kho_dong_y = [
        {
            "name": "DY-1",
            "nguoi": "NG-01",
            "muc_dich": "lien_he",
            "dong_y": 1,
            "trang_thai": "hieu_luc",
            "luc": "2026-11-10 08:00:00",
            "nguon": "trang-ifagent",
        },
        {
            "name": "DY-2",
            "nguoi": "NG-02",
            "muc_dich": "lien_he",
            "dong_y": 0,
            "trang_thai": "da_rut",
            "luc": "2026-11-10 09:00:00",
            "nguon": "trang-ifagent",
        },
    ]

    def fake_get_all(doctype, filters=None, or_filters=None, pluck=None, **kwargs):
        if doctype == "LX Nguoi":
            return [dict(x) for x in kho_nguoi]
        if doctype == "LX Dong Y":
            ma = (filters or {}).get("nguoi")
            return [dict(x) for x in kho_dong_y if x["nguoi"] == ma]
        if doctype == "Has Role":
            return ["sale1@vd.vn", "sale2@vd.vn"]
        if doctype == "User Permission":
            u = (filters or {}).get("user")
            if u == "sale1@vd.vn" or (isinstance(u, list) and "sale1@vd.vn" in u[1]):
                return ["DV-A"] if u == "sale1@vd.vn" else ["sale1@vd.vn"]
            return []
        return []

    fake_frappe.get_all = fake_get_all
    fake_frappe.get_doc = lambda dt, ma: types.SimpleNamespace(**kho_nguoi[0]) if ma == "NG-01" else (_ for _ in ()).throw( KeyError(ma))
    fake_frappe.get_roles = lambda u=None: ["System Manager"] if u == "admin@vd.vn" else ["LX Nhan Vien"]
    fake_frappe.session = types.SimpleNamespace(user="sale1@vd.vn")
    fake_frappe.db = types.SimpleNamespace(sql=None)
    fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
    fake_rl = types.ModuleType("frappe.rate_limiter")
    fake_rl.rate_limit = lambda **kw: (lambda fn: fn)
    fake_model = types.ModuleType("frappe.model")
    fake_doc_mod = types.ModuleType("frappe.model.document")
    fake_doc_mod.Document = object

    with patch.dict(
        sys.modules,
        {
            "frappe": fake_frappe,
            "frappe.rate_limiter": fake_rl,
            "frappe.model": fake_model,
            "frappe.model.document": fake_doc_mod,
        },
    ):
        sys.modules.pop("linhx_core.crm.api_form", None)
        sys.modules.pop("linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi", None)
        api_form = importlib.import_module("linhx_core.crm.api_form")
        lx_co_hoi = importlib.import_module("linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi")

        # 1. _cac_dang_dien_thoai
        assert api_booking._cac_dang_dien_thoai("0912345678", "84912345678") == api_form._cac_dang_dien_thoai(
            "0912345678", "84912345678"
        )

        # 2. _tim_nguoi_trung
        dl_tim = {"dien_thoai": "0912345678", "email": "khacha@vd.vn"}
        assert api_booking._tim_nguoi_trung(dl_tim) == api_form._tim_nguoi_trung(dl_tim)

        # 3. _doc_nguoi_db
        assert api_booking._doc_nguoi_db("NG-01") == api_form._doc_nguoi_db("NG-01")

        # 4. _chuan_kenh & _nguoi_so_huu_kenh
        for kenh_thu in ("KHACHA@VD.VN", "0912345678", "+84912345678", "ZALO_A", "kenh_la@vd.vn", ""):
            assert api_booking._chuan_kenh(kenh_thu) == xac_minh_marketing._chuan_kenh(kenh_thu)
            assert api_booking._nguoi_so_huu_kenh(kho_nguoi[0], kenh_thu) == api_form._nguoi_so_huu_kenh(
                kho_nguoi[0], kenh_thu
            )

        # 5. _chon_kenh_otp_cho_nguoi
        for kwargs_otp in (
            {"em_chuan": "khacha@vd.vn", "dt_chuan": "84912345678"},
            {"em_chuan": "ke_la@vd.vn", "dt_chuan": "84912345678"},
            {"dt_chuan": "84912345678", "zl_chuan": "ZALO_A"},
            {"dt_chuan": "84912345678", "zl_chuan": "zalo_la"},
        ):
            assert api_booking._chon_kenh_otp_cho_nguoi(kho_nguoi[0], **kwargs_otp) == api_form._chon_kenh_otp_cho_nguoi(
                kho_nguoi[0], **kwargs_otp
            )

        # 6. _lay_so_dong_y_hien_co & _da_rut_dong_y
        so_b = api_booking._lay_so_dong_y_hien_co(kho_nguoi)
        so_f = api_form._lay_so_dong_y_hien_co(kho_nguoi)
        assert so_b == so_f
        assert api_booking._da_rut_dong_y(so_b, "NG-01", "lien_he") == form.da_rut_dong_y(so_f, "NG-01", "lien_he")

        # 7. _loc_ung_vien_crm, _la_user_mien, _lay_don_vi_cua_user, _chon_phu_trach_it_viec
        ds_u = ["sale1@vd.vn", "sale2@vd.vn", "khach@vd.vn"]
        assert api_booking._loc_ung_vien_crm(fake_frappe, ds_u, "DV-A") == lx_co_hoi._loc_ung_vien_crm(
            fake_frappe, ds_u, "DV-A"
        )
        for u_kiem in ("Administrator", "admin@vd.vn", "sale1@vd.vn", "Guest"):
            assert api_booking._la_user_mien(u_kiem) == quyen_don_vi.la_user_mien(u_kiem)
            assert api_booking._lay_don_vi_cua_user(u_kiem) == quyen_don_vi.lay_don_vi_cua_user(u_kiem)

        ds_ch_mo = [
            {"phu_trach": "sale1@vd.vn", "trang_thai": "moi"},
            {"phu_trach": "sale1@vd.vn", "trang_thai": "dang_lam"},
            {"phu_trach": "sale2@vd.vn", "trang_thai": "moi"},
        ]
        assert api_booking._chon_phu_trach_it_viec(["sale1@vd.vn", "sale2@vd.vn"], ds_ch_mo) == co_hoi.giao(
            {}, ["sale1@vd.vn", "sale2@vd.vn"], ds_ch_mo
        )


def test_api_booking_voi_mock_frappe():
    class FakeValidationError(ValueError):
        pass

    class FakePermissionError(PermissionError):
        pass

    kho_lich: list[dict] = []
    kho_nguoi: dict[str, dict] = {
        "NG-01": {
            "name": "NG-01",
            "ho_ten": "Khách Một",
            "dien_thoai": "0912345678",
            "email": "khach1@vd.vn",
            "don_vi": "DV-A",
        },
        "NG-02": {
            "name": "NG-02",
            "ho_ten": "Khách Hai",
            "dien_thoai": "0988777666",
            "email": "khach2@vd.vn",
            "don_vi": "DV-B",
        },
    }
    kho_co_hoi: list[dict] = [
        {
            "name": "CH-01",
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "don_vi": "DV-A",
            "trang_thai": "moi",
            "creation": "2026-11-10 08:00:00",
        },
        {
            "name": "CH-02",
            "nguoi": "NG-02",
            "phu_trach": "sale2@vd.vn",
            "don_vi": "DV-B",
            "trang_thai": "moi",
            "creation": "2026-11-10 08:05:00",
        },
    ]
    kho_dong_y: list[dict] = [
        {
            "name": "DY-01",
            "nguoi": "NG-01",
            "muc_dich": "lien_he",
            "dong_y": 1,
            "luc": "2026-11-10 08:00:00",
            "nguon": "trang-ifagent",
        }
    ]

    class FakeDoc:
        def __init__(self, d: dict):
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            for k, v in d.items():
                setattr(self, k, v)

        def insert(self, ignore_permissions: bool = False):
            if getattr(self, "doctype", "") == "LX Lich Goi":
                self.name = f"LG-{len(kho_lich) + 1:03d}"
                kho_lich.append(
                    {
                        "name": self.name,
                        "nguoi": self.nguoi,
                        "co_hoi": getattr(self, "co_hoi", ""),
                        "phu_trach": self.phu_trach,
                        "don_vi": getattr(self, "don_vi", ""),
                        "bat_dau": self.bat_dau,
                        "ket_thuc": self.ket_thuc,
                        "phut": self.phut,
                        "trang_thai": self.trang_thai,
                        "ghi_chu": getattr(self, "ghi_chu", ""),
                    }
                )
            elif getattr(self, "doctype", "") == "LX Co Hoi":
                self.name = f"CH-{len(kho_co_hoi) + 1:02d}"
            return self

    def fake_throw(msg, exc=FakeValidationError):
        if isinstance(exc, type) and issubclass(exc, BaseException):
            raise exc(msg)
        raise FakeValidationError(msg)

    def fake_get_all(doctype, filters=None, pluck=None, **kwargs):
        if doctype == "LX Lich Goi":
            pt = (filters or {}).get("phu_trach")
            return [dict(x) for x in kho_lich if (not pt or x.get("phu_trach") == pt) and x.get("trang_thai") != "huy"]
        if doctype == "LX Co Hoi":
            ng = (filters or {}).get("nguoi")
            ten_ch = (filters or {}).get("name")
            return [
                dict(x)
                for x in kho_co_hoi
                if (not ng or x.get("nguoi") == ng) and (not ten_ch or x.get("name") == ten_ch)
            ]
        if doctype == "LX Dong Y":
            ng = (filters or {}).get("nguoi")
            return [dict(x) for x in kho_dong_y if not ng or x.get("nguoi") == ng]
        if doctype == "LX Nguoi":
            return [dict(v) for v in kho_nguoi.values()]
        if doctype == "User Permission":
            user_f = (filters or {}).get("user")
            if user_f == "sale1@vd.vn":
                return ["DV-A"] if pluck else [{"user": "sale1@vd.vn", "for_value": "DV-A"}]
            if user_f == "sale2@vd.vn":
                return ["DV-B"] if pluck else [{"user": "sale2@vd.vn", "for_value": "DV-B"}]
            return []
        return []

    def fake_get_value(doctype, name, fieldname, as_dict=False):
        if doctype == "LX Nguoi" and name in kho_nguoi:
            return dict(kho_nguoi[name]) if as_dict else kho_nguoi[name].get(fieldname)
        if doctype == "LX Co Hoi":
            for ch in kho_co_hoi:
                if ch["name"] == name:
                    return dict(ch) if as_dict else ch.get(fieldname)
            return None
        if doctype == "User":
            return {"name": name, "enabled": 1, "user_type": "System User"} if as_dict else 1
        return None

    fake_frappe = types.ModuleType("frappe")
    fake_frappe.ValidationError = FakeValidationError
    fake_frappe.PermissionError = FakePermissionError
    fake_frappe.DuplicateEntryError = RuntimeError
    fake_frappe.throw = fake_throw
    fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
    fake_frappe.get_all = fake_get_all
    fake_frappe.get_roles = lambda u=None: ["LX Nhan Vien"]
    fake_frappe.get_doc = lambda arg1, arg2=None: (
        FakeDoc(kho_nguoi[arg2])
        if arg1 == "LX Nguoi" and arg2 in kho_nguoi
        else (_ for _ in ()).throw(KeyError(arg2))
        if arg1 == "LX Nguoi"
        else FakeDoc(arg1 if isinstance(arg1, dict) else {})
    )
    fake_frappe.local = types.SimpleNamespace(
        site="ifagent",
        request_ip="127.0.0.1",
        request=types.SimpleNamespace(
            method="POST",
            headers={},
            content_length=120,
            get_data=lambda **kw: b"{}",
            get_json=lambda **kw: None,
        ),
        form_dict={},
        response={},
        _lx_cau_hinh_cache={"bat_crm": 1, "bat_pay": 1},
    )
    fake_frappe.session = types.SimpleNamespace(user="Guest")
    fake_frappe.db = types.SimpleNamespace(
        get_value=fake_get_value,
        exists=lambda dt, n: n in kho_nguoi if dt == "LX Nguoi" else True,
        sql=None,
    )
    fake_frappe.cache = lambda: None

    with patch.dict(sys.modules, {"frappe": fake_frappe}):
        api_booking._BO_DEM_LICH_DU_PHONG.clear()

        # 1. Đặt lịch hợp lệ có kênh liên hệ khớp hồ sơ -> tự lấy phu_trach từ CH-01 (sale1@vd.vn)
        kq1 = api_booking.dat_lich_goi(
            nguoi="NG-01",
            dien_thoai="0912345678",
            bat_dau="2026-11-10 09:00:00",
            phut=30,
            ghi_chu="Tư vấn Agent Force",
            dong_y_lien_he=True,
        )
        assert kq1["ok"] is True
        assert kq1["phu_trach"] == "sale1@vd.vn"
        assert kq1["co_hoi"] == "CH-01"
        assert kq1["bat_dau"] == "2026-11-10 09:00:00"
        assert kq1["ket_thuc"] == "2026-11-10 09:30:00"

        # 2. Đặt trùng giờ -> bị chặn với 409
        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                phu_trach="sale1@vd.vn",
                bat_dau="2026-11-10 09:15:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 409

        # 3. Ngoài giờ làm (18:00) -> bị chặn với 400
        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                phu_trach="sale1@vd.vn",
                bat_dau="2026-11-10 18:00:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 400

        # 4. Người phụ trách đăng nhập xem viec_cho_lich_goi -> thấy lịch
        fake_frappe.session.user = "sale1@vd.vn"
        ds_vc = api_booking.viec_cho_lich_goi()
        assert len(ds_vc) == 1
        assert ds_vc[0]["nguoi"] == "NG-01"
        assert ds_vc[0]["phu_trach"] == "sale1@vd.vn"

        # 5. Nhân viên khác không được xem lịch của sale1@vd.vn
        fake_frappe.session.user = "sale2@vd.vn"
        with pytest.raises(FakePermissionError):
            api_booking.viec_cho_lich_goi(phu_trach="sale1@vd.vn")

        # 6. Chống đoán hồ sơ & chống ghép kênh: mã nguoi trơn, email lạ, hoặc ghép SĐT nạn nhân + email kẻ lạ -> 400
        fake_frappe.session.user = "Guest"
        api_booking._BO_DEM_LICH_DU_PHONG.clear()
        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                bat_dau="2026-11-10 15:00:00",
                phut=30,
            )
        assert fake_frappe.local.response.get("http_status_code") == 400

        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                email="ke_la@vd.vn",
                bat_dau="2026-11-10 15:00:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 400

        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-KHONG-TON-TAI",
                dien_thoai="0912345678",
                bat_dau="2026-11-10 15:00:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 400

        # 7. Khách gửi co_hoi của người khác (CH-02) và phu_trach của đơn vị khác (sale2@vd.vn) -> bị bỏ qua, giữ CH-01 & sale1@vd.vn
        api_booking._BO_DEM_LICH_DU_PHONG.clear()
        kq2 = api_booking.dat_lich_goi(
            nguoi="NG-01",
            dien_thoai="0912345678",
            co_hoi="CH-02",
            phu_trach="sale2@vd.vn",
            bat_dau="2026-11-10 10:00:00",
            phut=30,
            dong_y_lien_he=True,
        )
        assert kq2["co_hoi"] == "CH-01"
        assert kq2["phu_trach"] == "sale1@vd.vn"
        assert kho_lich[-1]["don_vi"] == "DV-A"

        # 8. Khách đã rút đồng ý liên hệ (dong_y=0) -> bị từ chối 400 kể cả khi gửi dong_y_lien_he=True
        kho_dong_y.append(
            {
                "name": "DY-02",
                "nguoi": "NG-01",
                "muc_dich": "lien_he",
                "dong_y": 0,
                "luc": "2026-11-10 12:00:00",
                "nguon": "trang-ifagent",
            }
        )
        api_booking._BO_DEM_LICH_DU_PHONG.clear()
        with pytest.raises(FakeValidationError, match="đã rút đồng ý"):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                bat_dau="2026-11-10 15:00:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 400


def test_trang_bu_form_dat_lich_cau_truc():
    goc = pathlib.Path(__file__).resolve().parents[3]
    idx = (goc / "trang-bu" / "pages" / "index.js").read_text(encoding="utf-8")
    assert "data-dat-lich" in idx
    assert "/api/method/linhx_core.booking.api_booking.dat_lich_goi" in idx
    assert 'name="bat_dau"' in idx
    assert "data-dat-lich-thanh-cong" in idx
