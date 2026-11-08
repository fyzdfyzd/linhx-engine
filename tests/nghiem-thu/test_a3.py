"""A3: LX Dong Y theo mục đích (liên hệ, chuyển chéo, marketing), rút đồng ý, nhật ký.
Rút đồng ý thì API chuyển chéo từ chối. Mỗi thay đổi có dòng nhật ký.

Hợp đồng (HOP-DONG.md):
- DocType JSON module crm: LX Dong Y (nguoi Link LX Nguoi, muc_dich Select đúng 3 giá trị lien_he, chuyen_cheo, marketing,
  dong_y Check, luc Datetime, nguon Data), track_changes = 1. Bản ghi chỉ thêm: rút đồng ý là thêm dòng dong_y = 0.
- linhx_core/crm/dong_y.py thuần Python:
    MUC_DICH = ("lien_he", "chuyen_cheo", "marketing")
    class TuChoi(Exception)
    ghi(so, nguoi, muc_dich, dong_y, luc, nguon) -> list   trả sổ mới = sổ cũ + 1 dòng {nguoi, muc_dich, dong_y, luc, nguon};
                                                           không sửa sổ cũ; muc_dich lạ -> ValueError
    hieu_luc(so, nguoi, muc_dich) -> bool                  theo dòng có luc mới nhất của người + mục đích; không có -> False
    kiem_chuyen_cheo(so, nguoi) -> None                    raise TuChoi khi không còn đồng ý chuyen_cheo
- lx_dong_y.py chặn sửa/xoá bản ghi cũ (on_trash, validate khi không phải bản mới) để giữ nhật ký.
"""
import copy

import pytest

from _chung import CORE, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype


def _dy():
    return nap_module("linhx_core.crm.dong_y", CORE)


def test_doctype():
    p, d = tim_doctype("LX Dong Y")
    assert d and str(d.get("module", "")).lower() == "crm"
    tr = ten_truong(d)
    assert tr.get("nguoi", {}).get("options") == "LX Nguoi"
    assert set(str(tr.get("muc_dich", {}).get("options", "")).split()) == {"lien_he", "chuyen_cheo", "marketing"}
    assert tr.get("dong_y", {}).get("fieldtype") == "Check" and tr.get("luc", {}).get("fieldtype") == "Datetime"
    assert d.get("track_changes") == 1, "LX Dong Y phải bật track_changes"
    ctl = p.with_suffix(".py").read_text(encoding="utf-8")
    assert "on_trash" in ctl, "lx_dong_y.py phải chặn xoá để giữ nhật ký"


def test_moi_thay_doi_mot_dong_nhat_ky():
    dy = _dy()
    so = dy.ghi([], "N1", "chuyen_cheo", True, "2026-11-09 08:00:00", "form-ifagent")
    cu = copy.deepcopy(so)
    so2 = dy.ghi(so, "N1", "chuyen_cheo", False, "2026-11-09 09:00:00", "rut-qua-zalo")
    assert so == cu, "ghi không được sửa sổ cũ"
    assert len(so2) == 2 and so2[-1]["dong_y"] is False and so2[-1]["nguon"] == "rut-qua-zalo"
    with pytest.raises(ValueError):
        dy.ghi(so2, "N1", "ban_du_lieu", True, "2026-11-09 10:00:00", "x")


def test_rut_dong_y_thi_chuyen_cheo_tu_choi():
    dy = _dy()
    so = dy.ghi([], "N1", "chuyen_cheo", True, "2026-11-09 08:00:00", "form")
    so = dy.ghi(so, "N1", "marketing", True, "2026-11-09 08:00:00", "form")
    dy.kiem_chuyen_cheo(so, "N1")
    so = dy.ghi(so, "N1", "chuyen_cheo", False, "2026-11-09 09:00:00", "rut")
    with pytest.raises(dy.TuChoi):
        dy.kiem_chuyen_cheo(so, "N1")
    assert dy.hieu_luc(so, "N1", "marketing") is True, "rút một mục đích không ảnh hưởng mục đích khác"
    with pytest.raises(dy.TuChoi):
        dy.kiem_chuyen_cheo(so, "N2")


def test_theo_luc_moi_nhat_khong_theo_thu_tu_ghi():
    dy = _dy()
    so = dy.ghi([], "N1", "lien_he", False, "2026-11-09 10:00:00", "rut")
    so = dy.ghi(so, "N1", "lien_he", True, "2026-11-09 08:00:00", "nhap-bu")
    assert dy.hieu_luc(so, "N1", "lien_he") is False
    assert dy.MUC_DICH == ("lien_he", "chuyen_cheo", "marketing")


def test_thuan_python():
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "dong_y.py")
