# 01_MAY_TAO_NOI_DUNG — Máy tạo nội dung + Media hoá, chống AI slop

> **Chuẩn**: `D:\LINHX\PLAN\00_SYSTEM\PROTO_DE\00_CHUAN_PROTO.md` & `01_MAY_TAO_NOI_DUNG.md` (Bản 3 · CHỐT 25/10 11:45)
> **Mức hiện tại**: **Mức 1 (`MUC_1_XONG`)** — Đóng gói hoàn chỉnh trong thư mục, chạy lại toàn bộ trong < 15 phút (thực tế ~8 giây).
> **Nhận diện thương hiệu đang dùng**: **Nhận diện tạm: Sakedemy (`LAB043`)**

---

## 1. Chạy lại toàn bộ trong 1 lệnh (< 15 phút)

Mở PowerShell tại `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG`:

```powershell
# 1. Chạy trọn cả 3 loại nội dung (bài viết, report mẫu, nội dung khoá học) qua 9 bước + Media hoá M1..M5
python dieu_phoi.py --loai all

# 2. Chạy riêng từng loại (hoặc bật cổng dừng chờ người duyệt ở Bước 5 với --duyet-outline nguoi)
python dieu_phoi.py --loai bai_viet
python dieu_phoi.py --loai report_mau
python dieu_phoi.py --loai noi_dung_khoa_hoc
python dieu_phoi.py --loai bai_viet --duyet-outline nguoi

# 3. Chạy kiểm thử nghiệm thu toàn diện (25 hạng mục kiểm tra cấu trúc, số đo LAB049, Onbrand LAB043, Giao kèo)
python verify.py
```

---

## 2. Giao kèo cho các Prototype khác gọi (`_KIEN_THUC/GIAO_KEO.md`)

Từ bất kỳ prototype nào (`02_TRO_LY_NHAN_LENH` .. `08_MAY_QUET_WEB`):

```python
import sys
sys.path.insert(0, r"D:\LINHX\PROTO\_DUNG_CHUNG")
from may_tao_noi_dung_adapter import taoNoiDung, kiemChatLuong

# 1. Tạo nội dung trọn chu trình 9 bước + Media hoá
kq = taoNoiDung("bai_viet", {
    "ngay": "2026-10-25",
    "slug": "bai-viet-moi",
    "de_bai": "Chủ đề cần viết...",
    "duyet_outline": "may",  # hoặc "nguoi"
})

# 2. Kiểm chất lượng chống AI slop (chạy thật cham_cau.py, kiem_van_dich.py, kiem_van.py của LAB049 + Onbrand LAB043)
cham = kiemChatLuong(kq["run_dir"] + "/09b_ban_sach_khong_ma_nguon.md", "bai_viet")
print(cham["diem"], cham["dat"], cham["loi"])
```

---

## 3. Cấu trúc đóng gói độc lập trong thư mục

- `00_PHAN_BIEN_VA_RA_SOAT.md`: Bản phản biện 6 điểm cốt lõi của đề bài & rà soát 13 LAB.
- `01_LICH_TRIEN_KHAI_MUC_1.md`: Lịch triển khai 6 chặng & checklist nghiệm thu.
- `vendor/`: Đóng gói 1.020 file từ 13 LAB (`LAB017`, `025`, `027`, `028`, `029`, `031`, `032`, `036`, `043`, `046`, `048`, `049`, `066`) kèm `VENDOR_MANIFEST.json` có mã băm SHA256. **Không sửa 1 byte nào ở thư mục LAB gốc**.
- `skills/`:
  - `BM1_01_phan_tich_de_bai/` (gắn `LAB025 idea-seeder`, `LAB028`, `LAB017`)
  - `BM1_02_persona_neo/` (**Gộp mới**: `LAB029` khoảng trống + `LAB048` lọc persona VN + `LAB049 doc-gia-ao`)
  - `BM1_03_tim_tham_chieu/` (gắn `LAB025 deep-researcher` ≥15 nguồn + `LAB028 tim-mau-clone`)
  - `BM1_04_outline_thu_persona/` (**Làm mới**: 30 insights → 3 phương án Outline A/B/C + thử phản ứng trên 3 Persona Neo)
  - `BM1_05_cham_chon_huong/` (**Làm mới hoàn toàn**: chấm chọn hướng theo 4 trụ cột + cờ `duyet_outline: nguoi/may`)
  - `BM1_06_trien_khai_draft1/` (điều phối theo loại: `LAB049+025`, `LAB028+046`, `LAB017`)
  - `BM1_07_danh_gia_draft1/` (chạy thật `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py` của `LAB049` + APS/CQS)
  - `BM1_08_viet_lai_giong_tac_gia/` (viết lại theo hồ sơ giọng `linh` + luật `van-anh`)
  - `BM1_09_bien_tap_3_vong/` (biên tập 6 lượt tách ngữ cảnh ≤3 vòng + rút kinh nghiệm)
  - `BM2_M1_chu_trinh_template/` (**Làm mới dạng chung**: 5 bước PDCA `M1..M5` theo mẫu `LAB043` v2)
  - `BM2_M2_media_hoa/` (xuất SVG, DOCX, HTML/PDF Report, Slidev `slides.md` + Deck `10-deck.json` + Slide HTML/PDF theo nhận diện tạm **Sakedemy**)
- `loai/`: 3 thư mục cấu hình `bai_viet/`, `report_mau/`, `noi_dung_khoa_hoc/`.
- `runs/`: Kết quả chạy thật 3 loại nội dung, mỗi bước 1 file riêng (`01..09`, `M1..M5`, `media/`).
- `demo/`: Bản ánh xạ `demo/input/` và `demo/output/` theo chuẩn `00_CHUAN_PROTO.md`.
- `logs/NHAT_KY_TRIEN_KHAI_VA_3_VONG_TEST.md`: Nhật ký toàn bộ quá trình triển khai và 3 vòng kiểm thử để Claude đọc tiếp.
