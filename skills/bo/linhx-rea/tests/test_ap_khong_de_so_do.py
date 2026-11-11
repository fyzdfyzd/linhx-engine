"""Kiểm thử 3: `dap_an.json` có khoá `mau` giả -> `doc.json` giữ nguyên số đo gốc, có `xung_dot`."""
from __future__ import annotations

import copy
from pathlib import Path

import anh_do
import rea_core
from conftest import GOC_REPO, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le, tao_dap_an_hop_le_tu_sinh


def test_ap_khong_de_so_do(tmp_path: Path) -> None:
    p_anh = tmp_path / "vao" / "anh_kiem_ap.png"
    anh_do.ghi_anh(p_anh, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le(360, 270))

    dir_ra = tmp_path / "ra"
    muc_anh = dir_ra / "anh_kiem_ap"
    do_goc = copy.deepcopy(anh_do.do_mot_anh(p_anh, muc_anh))

    p_tu_vung = GOC_REPO / "linhx-rea" / "tu-vung" / "anh.yaml"
    rea_core.chay_viec_doc(dir_ra, p_tu_vung)

    dap_an_gia_mao = tao_dap_an_hop_le_tu_sinh("anh_kiem_ap.png")
    # Cố tình chèn khoá số đo `mau` giả mạo vào dap_an.json để thử ghi đè máy đo
    dap_an_gia_mao["mau"] = [{"hex": "#ff00ff", "ti_le": 1.0}]
    rea_core.ghi_json(muc_anh / "dap_an.json", dap_an_gia_mao)

    kq_ap = rea_core.chay_ap(dir_ra, tu_vung_path=p_tu_vung)
    assert not kq_ap["loi"]
    assert "anh_kiem_ap" in kq_ap["da_ap"]

    do_tren_dia = rea_core.doc_json(muc_anh / "do.json")
    doc_ket_qua = rea_core.doc_json(muc_anh / "doc.json")

    # Số đo gốc không bị đè ở cả do.json lẫn doc.json["do"]
    assert do_tren_dia == do_goc
    assert doc_ket_qua["do"] == do_goc
    assert doc_ket_qua["do"]["mau"] == do_goc["mau"]

    # Ý kiến ghi đè `mau` bị bắt vào `xung_dot`
    ds_xung_dot = doc_ket_qua["xung_dot"]
    assert len(ds_xung_dot) >= 1
    assert any(xd.get("loai") == "trung_khoa_do" and xd.get("khoa") == "mau" for xd in ds_xung_dot)
