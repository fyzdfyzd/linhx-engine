---
name: BM2_M2_media_hoa
description: "Big Module 2 - Điều phối Media hoá theo từng loại nội dung: Ảnh minh hoạ + DOCX (Bài viết), Biểu đồ SVG + Báo cáo HTML/PDF (Report mẫu), Slidev slides.md + Deck 10-deck.json + Slide HTML/PDF (Khoá học 1 buổi), Khung Nhân vật (LAB066) và Khung Video (LAB042). Áp dụng nhận diện tạm Sakedemy (LAB043)."
metadata:
  version: "0.1.0"
---

# Big Module 2 · Điều phối Media hoá (`BM2_M2_media_hoa`)

## 1. Bảng ánh xạ Media hoá theo Đề 01 (Bản 3)
| Hạng mục Media | LAB kế thừa trong `vendor/` | Đầu ra thực tế ở Mức 1 (Nhận diện tạm: Sakedemy) |
|---|---|---|
| **Nhận diện thương hiệu & Kiểm Onbrand** | `vendor/LAB043/brands/sakedemy/` + `vendor/LAB036/linhx-brand-check` | Áp bảng màu `#6EB264`, `#02403B`, `#414141`, font `Be Vietnam Pro`, khung hình lá bo chéo, chấm điểm tự động qua `check_onbrand_sakedemy()`. |
| **Ảnh minh hoạ (Bài viết)** | `vendor/LAB031/linhx-kho-minh-hoa` + `vendor/LAB043/linhx-onbrand` | Sinh 2 ảnh đồ hoạ/minh hoạ chuẩn `1920x1080` (`minh_hoa_01.svg`, `minh_hoa_02.svg`) + file giao bài `.docx` (qua `build_docx.js` hoặc generator chuẩn). |
| **PDF / Report đẹp (Report mẫu)** | `vendor/LAB028/linhx-report` + `vendor/LAB046/report-core` | Sinh 2 biểu đồ dữ liệu (`hinh_01_roi.svg`, `hinh_02_phan_tang.svg`), file dàn trang Typst (`10-bao-cao.typ`), bản HTML chuẩn in tạp chí A4 (`bao_cao_sakedemy.html`) và bản **PDF thật (`bao_cao_sakedemy.pdf`)**. |
| **Slide (Nội dung khoá học 1 buổi)** | `vendor/LAB027/linhx-deck` + `vendor/LAB017/linhx-course` + `vendor/LAB032/anh-sang-slide` | Sinh `slides.md` (chuẩn Slidev kèm lời giảng Gagné), `10-deck.json` + `10-ghost-deck.md` (chuẩn LAB027), bản trình chiếu `slide_deck_sakedemy.html` và bản **PDF Slide 16:9 (`slide_deck_sakedemy.pdf`)**. |
| **Nhân vật & Khung Video** | `vendor/LAB066/QUY-TRINH-3-VONG.md` + `LAB042` | Sinh hồ sơ neo nhân vật giảng viên/chuyên gia (`character_anchor_sakedemy.json`) và khung phân cảnh video Mức 1 (`video_storyboard_khung.json`). |
