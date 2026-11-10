"""L1: khai báo module: mỗi app có module.json; lõi đọc, xếp thứ tự phụ thuộc, tra hàm do app cung cấp.

Hợp đồng (HOP-DONG.md, Đợt 3):
- apps/<app>/module.json: {"ten": "<tên app>", "ban": "x.y.z", "lop": "loi"|"adapter"|"goi", "can_loi": ">=x.y.z" (lõi thì bỏ),
  "phu_thuoc": [app], "nghe": {"<sự kiện>": "<module.ham>"}, "cung_cap": {"<khoá>": "<module.ham>"}, "giao": {"<loai_giao>": "<module.ham>"}}
  linhx_core và linhx_worker là "loi".
- apps/linhx_core/linhx_core/dang_ky_module.py (thuần Python, không import frappe đầu file):
    doc(duong) -> dict: thiếu ten/ban/lop, lop lạ, ban không phải semver -> ValueError
    quet(thu_muc_apps, ban_loi: str) -> list[dict]: mọi module.json, xếp sao cho phụ thuộc đứng trước;
        phụ thuộc không có, vòng phụ thuộc, can_loi không khớp ban_loi -> ValueError (thông điệp có tên app)
    tim_ham(danh_sach: list[dict], loai: "nghe"|"cung_cap"|"giao", khoa: str) -> list[str] (đường "module.ham", theo thứ tự quet)
"""
import json

import pytest

from _chung import CORE, nap_module
from _dot3 import doc_module_json


def _m():
    return nap_module("linhx_core.dang_ky_module", CORE)


def _viet(goc, ten, **k):
    (goc / ten).mkdir(parents=True, exist_ok=True)
    d = {"ten": ten, "ban": "0.1.0", "lop": "goi", "can_loi": ">=0.3.0", "phu_thuoc": []}
    d.update(k)
    (goc / ten / "module.json").write_text(json.dumps(d), encoding="utf-8")


def test_app_hien_co_khai_bao():
    """Tiêu chí: linhx_core và linhx_worker có module.json lớp lõi"""
    assert doc_module_json("linhx_core")["lop"] == "loi"
    assert doc_module_json("linhx_worker")["lop"] == "loi"


def test_doc_va_xep_phu_thuoc(tmp_path):
    """Tiêu chí: quét module.json, xếp phụ thuộc trước, tra hàm theo loại"""
    m = _m()
    _viet(tmp_path, "linhx_goi_b", phu_thuoc=["linhx_vn"], giao={"bao_cao": "linhx_goi_b.giao.giao"})
    _viet(tmp_path, "linhx_vn", lop="adapter", nghe={"don.da_tra": "linhx_vn.so.ghi"})
    ds = m.quet(tmp_path, "0.3.1")
    ten = [d["ten"] for d in ds]
    assert ten.index("linhx_vn") < ten.index("linhx_goi_b")
    assert m.tim_ham(ds, "giao", "bao_cao") == ["linhx_goi_b.giao.giao"]
    assert m.tim_ham(ds, "nghe", "don.da_tra") == ["linhx_vn.so.ghi"]
    assert m.tim_ham(ds, "cung_cap", "khong_co") == []


@pytest.mark.parametrize("hong", ["thieu_dep", "vong", "can_loi", "lop_la"])
def test_tu_choi_khai_bao_sai(tmp_path, hong):
    """Tiêu chí: phụ thuộc thiếu, vòng, can_loi lệch, lớp lạ thì báo lỗi có tên app"""
    m = _m()
    if hong == "thieu_dep":
        _viet(tmp_path, "linhx_goi_a", phu_thuoc=["linhx_khong_co"])
    elif hong == "vong":
        _viet(tmp_path, "linhx_goi_a", phu_thuoc=["linhx_goi_c"])
        _viet(tmp_path, "linhx_goi_c", phu_thuoc=["linhx_goi_a"])
    elif hong == "can_loi":
        _viet(tmp_path, "linhx_goi_a", can_loi=">=9.0.0")
    else:
        _viet(tmp_path, "linhx_goi_a", lop="plugin")
    with pytest.raises(ValueError, match="linhx_goi_a|linhx_goi_c"):
        m.quet(tmp_path, "0.3.1")
