"""K1: tạo bản cài cho một BU hay OPC bằng một lệnh: site Frappe riêng + gói bật sẵn + giao diện + tên miền.

Hợp đồng (HOP-DONG.md, Đợt 4):
- cli/linhx_cli/ban_cai.py (thuần Python, không import frappe):
    ke_hoach(ten: str, giao_dien: str | None, goi: list[str], ten_mien: str, goc=<gốc repo>) -> dict
        ten khớp ^[a-z][a-z0-9-]{1,30}$; mỗi gói là app có apps/<gói>/module.json; giao_dien (nếu có) là thư mục giao-dien/<tên>;
        sai thì ValueError.
        trả {"ten", "ten_mien", "cau_hinh": "deploy/sites/<ten>.json",
             "buoc": list[list[str]] (đối số, không phải chuỗi shell) theo thứ tự: bench new-site <ten_mien>,
                     bench --site <ten_mien> install-app cho linhx_core rồi từng gói theo thứ tự phụ thuộc module.json,
                     bench --site <ten_mien> migrate}
        gói thiếu phụ thuộc trong danh sách thì tự thêm phụ thuộc trước nó.
- CLI: python -m linhx_cli tao-ban-cai --ten <x> --ten-mien <d> [--giao-dien <bu>] [--goi a,b] [--chay-thu]
    --chay-thu in JSON kế hoạch, không chạy gì; không --chay-thu thì ghi deploy/sites/<ten>.json và chạy từng bước trên VM.
- Bằng chứng: bang-chung/K1/ban-cai.json {"luc": str, "ten": "sakedemy", "ten_mien": str, "url": str, "ma": 200, "phut": số <= 15, "goi": list}
  chạy thật trên VM linhx-engine-1.
"""
import json
import subprocess
import sys

import pytest

from _chung import GOC, bang_chung_json, nap_module


def _m():
    return nap_module("linhx_cli.ban_cai", GOC / "cli")


def test_ke_hoach_dung_thu_tu():
    """Tiêu chí: kế hoạch cài lõi trước, gói theo thứ tự phụ thuộc, lệnh là list đối số"""
    m = _m()
    k = m.ke_hoach("sakedemy", "sakedemy", [], "sakedemy.35-198-251-2.nip.io")
    assert k["cau_hinh"] == "deploy/sites/sakedemy.json"
    assert all(isinstance(b, list) for b in k["buoc"])
    phang = [" ".join(b) for b in k["buoc"]]
    assert "new-site" in phang[0] and "migrate" in phang[-1]
    cai = [b[-1] for b in k["buoc"] if "install-app" in b]
    assert cai[0] == "linhx_core"


@pytest.mark.parametrize("sai", [("Sake Demy", None, []), ("x;rm", None, []), ("sakedemy", "khong-co", []),
                                 ("sakedemy", None, ["linhx_khong_co"])])
def test_tu_choi_dau_vao_sai(sai):
    """Tiêu chí: tên, giao diện, gói không có thì từ chối"""
    with pytest.raises(ValueError):
        _m().ke_hoach(*sai, "a.vd.vn")


def test_cli_chay_thu():
    """Tiêu chí: CLI --chay-thu in kế hoạch JSON, không chạy lệnh"""
    r = subprocess.run([sys.executable, "-m", "linhx_cli", "tao-ban-cai", "--ten", "thu", "--ten-mien", "thu.vd.vn", "--chay-thu"],
                       cwd=GOC, capture_output=True, text=True, encoding="utf-8", timeout=30,
                       env={**__import__("os").environ, "PYTHONPATH": str(GOC / "cli")})
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    assert d["ten"] == "thu" and d["buoc"]
    assert not (GOC / "deploy" / "sites" / ("thu" + ".json")).exists(), "chạy thử không được ghi cấu hình"


def test_bang_chung_vm():
    """Tiêu chí: tạo thật bản cài sakedemy trên VM trong 15 phút"""
    d = bang_chung_json("K1", "ban-cai.json")
    assert d["ten"] == "sakedemy" and d["ma"] == 200 and float(d["phut"]) <= 15
