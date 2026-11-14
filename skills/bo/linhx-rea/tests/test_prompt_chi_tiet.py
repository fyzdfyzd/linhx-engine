"""Kiểm thử 8 (R4c): `prompt.md` kéo cụm chi tiết cụ thể + toạ độ từ `ghi_chu` của `dap_an` mẫu, bỏ `MAY-SAI:` và ≤25 từ."""
from __future__ import annotations

from pathlib import Path

import anh_do
import rea_core
import ve_nguoc
from conftest import THU_MUC_SKILL, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le


def test_prompt_keo_chi_tiet_tu_ghi_chu_dap_an(tmp_path: Path) -> None:
    p_anh = tmp_path / "vao" / "mau_088.png"
    ra_dir = tmp_path / "ra"
    muc_dir = ra_dir / "mau_088"
    anh_do.ghi_anh(p_anh, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le())
    anh_do.do_mot_anh(p_anh, muc_dir)

    p_tu_vung = THU_MUC_SKILL / "tu-vung" / "anh.yaml"
    rea_core.chay_viec_doc(ra_dir, p_tu_vung)

    ghi_chu_dai = (
        "Đường cắt sáng ngang sắc như dao tại y=0.66 chia tách nguồn sáng xanh lục lạnh bên trên "
        "với dải đèn flash/slit trắng gắt chiếu thẳng vào ngực áo giao lĩnh trắng chói phía dưới "
        "tạo tương phản kịch tính cho toàn bộ khung hình cận cảnh"
    )
    assert len(ve_nguoc.rut_gon_so_tu(ghi_chu_dai, toi_da_tu=25).split()) <= 25

    dap_an_mau = {
        "anh": "mau_088.png",
        "trang_thai": "da_dien",
        "nguoi_doc": "pytest",
        "tra_loi": [
            {
                "ma": "chu_the_chinh",
                "gia_tri": "chan_dung_nguoi",
                "ghi_chu": (
                    "MAY-SAI: máy đặt điểm hút mắt #2 (x=0.32, y=0.63) vào rìa tóc trống do nhiễu biên, "
                    "bỏ sót hoàn toàn đôi môi đỏ thẫm hé mở lộ hàm răng ở x=0.47, y=0.22 thuộc khuôn mặt dưới ám xanh ngọc."
                ),
                "moc": {"x": 0.47, "y": 0.22},
            },
            {
                "ma": "chu_the_phu",
                "gia_tri": "vai_lua_trang_phuc" if False else "dao_cu_vat_the",
                "ghi_chu": "Ngực áo giao lĩnh trắng chói chiếm trọn dải đáy hop=[0.06, 0.66, 0.94, 1.00].",
                "moc": {"hop": [0.06, 0.66, 0.94, 1.00]},
            },
            {
                "ma": "duong_dan_mat",
                "gia_tri": "luong_sang_tia_sang",
                "ghi_chu": "Biên cắt sáng ngang ở y=0.66 dẫn mắt bật ngược lên đôi môi đỏ ở x=0.47, y=0.22.",
                "moc": {"vung": "A2-B2"},
            },
            {
                "ma": "anh_sang_huong",
                "gia_tri": "thuan_truoc",
                "ghi_chu": ghi_chu_dai,
                "moc": {"x": 0.50, "y": 0.66},
            },
            {
                "ma": "anh_sang_cung_mem",
                "gia_tri": "cung_gat",
                "ghi_chu": "Biên cắt sáng ngang không chuyển tiếp cùng đốm phản quang trên môi dưới ở x=0.46, y=0.30.",
            },
            {
                "ma": "nhiet_mau",
                "gia_tri": "lanh_tram",
                "ghi_chu": "Màu da xanh ngọc/lục lam lạnh lẽo đối trọng sắc đỏ máu thẫm của đôi môi.",
            },
            {
                "ma": "chat_lieu",
                "gia_tri": "hon_hop",
                "ghi_chu": "Làn da mịn lạnh đặt cạnh sợi tóc khô và son môi bóng ướt ở x=0.46, y=0.30.",
                "moc": {"x": 0.46, "y": 0.30},
            },
            {
                "ma": "phong_cach",
                "gia_tri": "san_khau_mv",
                "ghi_chu": "Tạo hình sân khấu MV kỳ ảo với hóa trang da xanh ma mị và sọc ngang CRT.",
            },
            {
                "ma": "cam_xuc",
                "gia_tri": "bi_an_lanh_lung",
                "ghi_chu": "Cắt mất đôi mắt chỉ chừa đôi môi đỏ mở hé tạo cảm giác lạnh lùng bí ẩn.",
            },
        ],
        "the_de_xuat": [
            {
                "ten": "Điểm nhấn môi đỏ trên nền lạnh",
                "loai": "mau_sac",
                "moc": {"x": 0.47, "y": 0.22},
                "mo_ta": "Đặt sắc đỏ máu trên tổng thể xanh ngọc lạnh để ghim tiêu điểm.",
                "cach_lam": "Khử bão hoà nền về xanh lạnh và giữ nguyên sắc đỏ ở môi.",
                "khi_dung": "Khi cần ghim mắt tức thì vào một chi tiết biểu cảm nhỏ.",
                "nguon": "mau_088.png",
            }
        ],
    }
    rea_core.ghi_json(muc_dir / "dap_an.json", dap_an_mau)

    kq_ap = rea_core.chay_ap(ra_dir, tu_vung_path=p_tu_vung)
    assert kq_ap["loi"] == []

    kq_vn = ve_nguoc.ve_nguoc_mot_anh(muc_dir)
    prompt_txt = kq_vn["prompt"].read_text(encoding="utf-8")

    assert "MAY-SAI" not in prompt_txt.upper()
    assert "..." not in prompt_txt and "…" not in prompt_txt
    assert "red lips" in prompt_txt.lower()
    assert "môi đỏ" in prompt_txt.lower()
    assert "x=0.47, y=0.22" in prompt_txt
    assert "y=0.66" in prompt_txt
