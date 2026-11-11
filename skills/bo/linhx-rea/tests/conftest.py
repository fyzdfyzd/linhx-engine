"""Cấu hình dùng chung và hàm sinh ảnh tổng hợp (`numpy`/`cv2`) cho bộ 5 pytest `rea-anh`."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

THU_MUC_TESTS = Path(__file__).resolve().parent
THU_MUC_SKILL = THU_MUC_TESTS.parent
GOC_REPO = THU_MUC_SKILL.parent
THU_MUC_SCRIPTS = THU_MUC_SKILL / "scripts"

for _p_them in (THU_MUC_SCRIPTS, THU_MUC_TESTS):
    if str(_p_them) not in sys.path:
        sys.path.insert(0, str(_p_them))


def sinh_anh_phoi_canh_co_diem_do_va_nhieu_le(rong: int = 480, cao: int = 360) -> np.ndarray:
    """Sinh ảnh tổng hợp cảnh 1: hành lang phối cảnh sâu + tâm điểm tròn đỏ cam ở (0.50, 0.46)
    + vệt sọc trắng/đen tương phản cực gắt nằm sát lề 2% mép ảnh (để kiểm tra loại bỏ lề 4%).
    """
    yy, xx = np.mgrid[0:cao, 0:rong].astype(np.float32)
    nx = xx / float(rong - 1)
    ny = yy / float(cao - 1)

    img = np.zeros((cao, rong, 3), dtype=np.uint8)
    # Tường và trần tối lạnh lùi vào tâm
    kc_tam = np.hypot(nx - 0.50, ny - 0.46)
    nen = np.clip(22.0 + 55.0 * kc_tam, 15, 90).astype(np.uint8)
    img[:, :, 0] = np.clip(nen + 14, 0, 255)
    img[:, :, 1] = nen
    img[:, :, 2] = np.clip(nen - 8, 0, 255)

    # Sàn gạch phối cảnh ở tiền cảnh dưới để tạo tín hiệu độ sâu gần-xa rõ cho Depth Anything V2
    pts_san = np.array(
        [[0, cao - 1], [rong - 1, cao - 1], [int(0.66 * rong), int(0.56 * cao)], [int(0.34 * rong), int(0.56 * cao)]],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(img, pts_san, (135, 130, 122), lineType=cv2.LINE_AA)
    for k in range(1, 6):
        yk = int((0.56 + 0.08 * k) * cao)
        if yk < cao:
            cv2.line(img, (0, yk), (rong - 1, yk), (92, 88, 82), 2, cv2.LINE_AA)

    # Khối trụ tiền cảnh sát góc trái-dưới để lớp gần nổi bật rõ
    cv2.rectangle(img, (int(0.06 * rong), int(0.42 * cao)), (int(0.22 * rong), int(0.95 * cao)), (168, 162, 152), -1)

    # Chủ thể đỏ bão hoà cao ở trung tâm (x=0.50, y=0.46)
    cx, cy = int(0.50 * rong), int(0.46 * cao)
    bk = int(0.09 * min(rong, cao))
    cv2.circle(img, (cx, cy), bk, (24, 36, 238), -1, cv2.LINE_AA)

    # Nhiễu tương phản trắng/đen gắt cố tình đặt sát mép trên & mép trái (< 2.5% cạnh, nằm trong vùng cấm 4%)
    le_y = max(2, int(0.02 * cao))
    for i in range(0, rong, 12):
        mau_soc = (255, 255, 255) if ((i // 12) % 2 == 0) else (0, 0, 0)
        img[:le_y, i : min(rong, i + 12)] = mau_soc

    return img


def sinh_anh_bau_troi_rong_va_vat_nho(rong: int = 480, cao: int = 360) -> np.ndarray:
    """Sinh ảnh tổng hợp cảnh 2: 82% bầu trời phẳng sáng ở xa + 1 khối hộp nhỏ ở góc dưới-phải,
    nhằm tạo phân bố tỉ lệ độ sâu `do_sau.ti_le` khác hẳn cảnh 1.
    """
    yy, xx = np.mgrid[0:cao, 0:rong].astype(np.float32)
    ny = yy / float(cao - 1)
    nx = xx / float(rong - 1)

    img = np.zeros((cao, rong, 3), dtype=np.uint8)
    img[:, :, 0] = np.clip(235.0 - 25.0 * ny, 0, 255).astype(np.uint8)
    img[:, :, 1] = np.clip(215.0 - 20.0 * ny, 0, 255).astype(np.uint8)
    img[:, :, 2] = np.clip(188.0 - 15.0 * nx, 0, 255).astype(np.uint8)

    # Đường chân trời thấp ở y=0.82
    y_chan_troi = int(0.82 * cao)
    img[y_chan_troi:, :] = (78, 96, 86)

    # Khối hộp tiền cảnh có vân ở góc dưới-phải
    x0, y0, x1, y1 = int(0.68 * rong), int(0.58 * cao), int(0.92 * rong), int(0.94 * cao)
    cv2.rectangle(img, (x0, y0), (x1, y1), (42, 68, 185), -1)
    cv2.rectangle(img, (x0 + 8, y0 + 8), (x1 - 8, y1 - 8), (65, 95, 215), 2)
    return img


def tao_dap_an_hop_le_tu_sinh(ten_anh: str) -> dict[str, Any]:
    """Tạo dữ liệu `dap_an.json` hợp lệ đủ 17 trục cho ảnh tự sinh."""
    return {
        "anh": ten_anh,
        "trang_thai": "da_dien",
        "nguoi_doc": "pytest-tu-sinh",
        "tra_loi": [
            {"ma": "chu_the_chinh", "gia_tri": "hinh_khoi_do_hoa", "ghi_chu": "Khối tròn đỏ trung tâm.", "moc": {"x": 0.50, "y": 0.46}},
            {"ma": "chu_the_phu", "gia_tri": "kien_truc_khong_gian" if False else "hau_canh_boi_canh", "ghi_chu": "Hành lang bao quanh.", "moc": {"vung": "B1"}},
            {"ma": "duong_dan_mat", "gia_tri": "duong_hoi_tu_phoi_canh", "ghi_chu": "Sàn hội tụ về tâm B2.", "moc": {"hop": [0.20, 0.40, 0.80, 0.95]}},
            {"ma": "anh_sang_huong", "gia_tri": "thuan_truoc", "ghi_chu": "Chiếu trực diện khối đỏ.", "moc": {"vung": "B2"}},
            {"ma": "anh_sang_cung_mem", "gia_tri": "vua_ro_khoi", "ghi_chu": "Ranh giới mảng rõ."},
            {"ma": "nhiet_mau", "gia_tri": "tuong_phan_nong_lanh", "ghi_chu": "Nền lạnh và điểm nhấn đỏ nóng."},
            {"ma": "chat_lieu", "gia_tri": "mang_vector_phang", "ghi_chu": "Mảng màu tổng hợp phẳng.", "moc": {"vung": "B2"}},
            {"ma": "phong_cach", "gia_tri": "toi_gian", "ghi_chu": "Hình kỷ hà tối giản."},
            {"ma": "bieu_tuong", "gia_tri": "mau_sac_an_du", "ghi_chu": "Tâm đỏ cô lập.", "moc": {"x": 0.50, "y": 0.46}},
            {"ma": "cam_xuc", "gia_tri": "kich_tinh_cang_thang", "ghi_chu": "Tương phản tập trung."},
            {"ma": "khong_gian", "gia_tri": "tuong_phan", "ghi_chu": "Sàn hút sâu phối cảnh."},
            {"ma": "duong_net", "gia_tri": "tuong_phan", "ghi_chu": "Nét thẳng sàn và đường tròn."},
            {"ma": "hinh_khoi", "gia_tri": "tuong_phan", "ghi_chu": "Khối chữ nhật và hình tròn."},
            {"ma": "sac_do", "gia_tri": "tuong_phan", "ghi_chu": "Tường tối và sàn trung sắc."},
            {"ma": "mau", "gia_tri": "tuong_phan", "ghi_chu": "Đỏ cam trên nền xanh xám."},
            {"ma": "chuyen_dong", "gia_tri": "tuong_dong", "ghi_chu": "Hút tĩnh về tâm."},
            {"ma": "nhip", "gia_tri": "tuong_dong", "ghi_chu": "Gạch ngang sàn lặp đều."},
        ],
        "the_de_xuat": [
            {
                "ten": "Điểm tròn đỏ tại tâm điểm tụ hành lang lạnh",
                "loai": "bo_cuc",
                "moc": {"vung": "B2"},
                "mo_ta": "Đặt hình tròn đỏ bão hoà tại điểm tụ trung tâm B2 trên nền hành lang xanh xám trầm.",
                "cach_lam": "Dựng các đường sàn tụ về B2, giữ nền độ bão hoà thấp và đặt vật thể đỏ chiếm ~5% diện tích tại điểm tụ.",
                "khi_dung": "Dùng khi cần khoá ánh nhìn tức thì vào tâm khung hình.",
                "nguon": ten_anh,
            }
        ],
    }
