---
name: tim-mau-clone
description: Bước 0 của linhx-report. Tìm cảm hứng và mẫu báo cáo đẹp (thư viện PDF của Linh, Envato Elements, Dribbble, Behance, Issuu, Pinterest, trang báo cáo của các hãng), rồi clone style và structure của mẫu chính thành phong cách dùng được. Dùng khi bắt đầu báo cáo mới, hoặc khi Linh nói "clone style báo cáo này", "học bố cục từ mẫu này", "/bao-cao-clone".
---

# Bước 0: tìm mẫu và clone phong cách

Script: `clone.py` (đo, rút màu, so sánh, lưu phong cách) và `report.py ap-style`, `report.py cong <dir> 0`.

## 1. Tìm mẫu (luôn làm, kể cả khi đã có phong cách nhà)

Mục tiêu: 3–8 mẫu hợp với loại báo cáo trong đề bài, Linh chọn 1 mẫu chính.

Nguồn theo thứ tự:
1. **Thư viện PDF của Linh:** `D:\LINHX\PLAN\RESEARCH\R2_AGENT_FORCE\01_REPORT_LIBRARY\pdf\` (108 báo cáo McKinsey, BCG, Bain, Deloitte, PwC, WEF, Stanford…; danh mục `00_THU_VIEN.csv`). Ảnh ghép sẵn của 24 báo cáo đã đo ở `LAB028-REPORT-FLOW/refs/mau-bao-cao/`.
2. **Trang template và cảm hứng** qua Claude in Chrome trên máy Linh (đã đăng nhập): Envato Elements (từ khoá "annual report", "magazine", "brochure report", "whitepaper"), Behance (Annual Report, Editorial Design), Dribbble ("report design", "editorial"), Issuu, Pinterest (bảng của Linh). Chỉ xem và tải ảnh xem trước như người dùng; tối đa 12 ảnh mỗi lần; không cào hàng loạt, không lưu ghim, không theo dõi. Máy chủ cloud không vào được các trang này: khi chạy từ cloud, mở phiên Remote Control trên máy Linh.
3. **Báo cáo của hãng nghiên cứu thị trường** (Kantar, NielsenIQ, Ipsos) khi loại báo cáo là thị trường: tải PDF công khai qua Chrome của Linh vào thư viện.

Với mỗi mẫu:
- PDF: `python -I clone.py do <pdf> --ra <dir> --ten <ten-mau> [--trang 1-40]` → `00-mau/<ten>/` (ảnh từng trang, `tong-quan.jpg`, `so-do.json`), `00-style.json`, `00-cau-truc-goi-y.json`. Mẫu phụ chỉ ghi `00-mau/<ten>/style.json`; thêm `--chinh` cho mẫu chính khi muốn dùng style clone (ghi `00-style.json`, cổng 0 sẽ đòi ảnh so sánh).
- Ảnh xem trước (Envato, Behance…): lưu vào `00-mau/<ten>/goc/`, rồi `clone.py anh <các ảnh> --ra <dir> --ten <ten-mau>` → bảng màu, tỷ lệ khung, ảnh ghép.

Đưa Linh ảnh `tong-quan.jpg` của từng mẫu, một dòng mỗi mẫu: điểm mạnh, hợp loại báo cáo nào, khuyến nghị mẫu chính. Ghi `00-cau-truc.json` (mẫu ở `du-lieu/mau/00-cau-truc.json`): `mau[]` có `ten, nguon, duong_dan, loai_giay_phep (hoc | dung-duoc), chon, vi_sao`.

## 2. Bóc structure (Claude xem tận mắt)

Mở từng ảnh trang của mẫu chính (`00-mau/<ten>/p-*.png`), sửa kiểu trang máy đoán trong `00-cau-truc-goi-y.json` và ghi vào `00-cau-truc.json` → `trang[]`: `so, kieu (T01–T23 trong viet-bao-cao/references/kieu-trang.md, hoặc M01… cho kiểu mới), ghi_chu` (lưới, phần tử, vị trí tiêu đề, nhãn hình, nguồn). Ít nhất 8 trang tiêu biểu.

Ghi thêm:
- `nhip`: chuỗi kiểu trang trong một chương, chỗ trang ảnh xen trang chữ, trang số lớn đặt đâu.
- `bai_hoc`: 3–8 điều cụ thể học được (cách viết tiêu đề hình, cách đặt nguồn, độ rộng lề treo, cách mở chương, cách dùng màu nhấn).
- Kiểu mới (M01…): mô tả lưới và phần tử đủ để dựng lại.

## 3. Clone style (khi dùng mẫu làm phong cách)

1. `00-style.json` là token đo được (khổ, lề, cột, cỡ chữ, giãn dòng, màu gốc, font gốc). Font gốc được thay bằng font mở đủ dấu (Be Vietnam Pro cho sans, Source Serif 4 cho serif). Mở tệp, chỉnh tay những chỗ máy đo lệch rõ (ví dụ cỡ tiêu đề bìa), ghi lý do trong `goc`.
2. `report.py ap-style <dir> --tu <dir>/00-style.json`. Màu của hãng mẫu luôn bị thay bằng màu brand (giữ ở `mau_mau_goc` để tham khảo).
3. Dựng 3 trang thử (bìa, trang chữ, trang hình) bằng nội dung giả trong một thư mục nháp, rồi `clone.py so-sanh <mau.pdf> <trang> <thu.pdf> <trang> --ra <dir>/00-so-sanh/<ten>.png`. Đọc độ lệch (lề, cỡ chữ thân); lệch lề > 0,03 hoặc cỡ chữ > 1 pt thì chỉnh style, tối đa 3 vòng.
4. Phong cách đạt và Linh thích: `clone.py luu <dir> --ten <ten-phong-cach>` để dùng lại.

## 4. Cổng

`report.py cong <dir> 0` rồi hỏi Linh chọn mẫu (gửi ảnh tổng quan các mẫu + khuyến nghị). 10 phút không trả lời thì duyệt theo khuyến nghị.
