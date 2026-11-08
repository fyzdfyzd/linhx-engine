---
name: dan-trang
description: Bước 9–12 của linhx-report. Ảnh bìa và mở chương có ref, dựng báo cáo bằng Typst theo phong cách nhà và brand, kiểm bản in bằng script (D01–D17), render từng trang để xem và chấm theo rubric tạp chí, sửa đến khi mọi trang đạt, rồi bàn giao. Dùng trong quy trình bao-cao hoặc khi cần dựng lại PDF.
---

# Bước 9–12: ảnh, dàn trang, kiểm bản in, bàn giao

Cần: Typst ≥0.13 (`winget install --id Typst.Typst` trên Windows; hoặc biến `TYPST_BIN`), Python có `pymupdf`, `matplotlib`, `pillow`. Font đi kèm plugin (`fonts/`, OFL).

## Bước 9: ảnh (`09-anh/`)

- Đề bài ghi "Ảnh: không" → bỏ qua, bìa và mở chương dùng khối màu brand.
- Có ảnh: dùng skill `hinh-anh` của linhx-deck (ChatGPT Plus qua Chrome, ảnh neo, mọi ảnh có ref là trang mẫu từ bước 0 + moodboard, rà H1–H8, sửa ≤3 vòng). Tên tệp cố định: `bia.jpg` (dọc, 1240×1754 trở lên), `chuong-1.jpg`, `chuong-2.jpg`… (ngang, 2480×1100). Không chữ, không logo, không người giống thật trong ảnh.
- `09-anh/nhat-ky.json`: `[{"ten":"bia.jpg","ref":["00-mau/…"],"dat":true}]`.

## Bước 10: dựng

`report.py dung <dir>`: đọc chương, hình, nguồn, style → `10-bao-cao.json` → `10-typst/main.typ` → `bao-cao.pdf`. Lỗi biên dịch: đọc `10-typst/bien-dich.log`, sửa nội dung chương (thường do cú pháp khối), không sửa `lib.typ` trong dự án. Muốn đổi thiết kế thì sửa style (`style.json`) hoặc `typst/lib.typ` của plugin rồi dựng lại.

## Bước 11: kiểm bản in và chấm từng trang

1. `report.py anh-trang <dir>` → `11-anh-trang/trang-NN.png` + `tong-quan.jpg`.
2. XEM TỪNG TRANG (Read ảnh). Chấm theo `references/rubric-tap-chi.md`, đặt cạnh trang mẫu tương ứng trong ghost report (`mau:`). Ghi `11-cham-trang.json`: `[{"trang":n,"kieu":"T12","diem":{"diem_nhin":1-5,"nhip":1-5,"khoang_trang":1-5,"phan_cap_chu":1-5,"ky_thuat":1-5},"sua":"…"}]`.
3. Trang điểm trung bình <3,5 hoặc có tiêu chí <3: sửa (chia lại đoạn, đổi vị trí hình, thêm số lớn hoặc trích dẫn, cắt chữ, đổi kiểu trang trong ghost report), dựng lại, chấm lại. Tối đa 3 vòng; hết 3 vòng vẫn dưới ngưỡng thì báo Linh trang nào và vì sao.
4. `report.py cong <dir> 11` (đo D01–D17 + kiểm bảng chấm). Gửi Linh `tong-quan.jpg` và PDF, Linh duyệt.

## Bước 12: bàn giao (`12-ban-giao/`)

- `bao-cao.pdf` (chép từ thư mục báo cáo), `README.md` gồm: tên, ngày, phong cách, mục "Nguồn" (số nguồn, tầng, tệp sổ), mục "Linh cần làm" (việc còn lại trước khi gửi), link tới tệp gốc.
- Tuỳ chọn: tóm tắt 2 trang (dựng lại với chỉ `00-tom-tat.md`), rút deck bằng linhx-deck, bài đăng bằng linhx-viet-bai.
- `report.py cong <dir> 12`. Không gửi cho ai khi Linh chưa nói.
