# BÀI HỌC RÚT RA (`BAI_HOC.md`) · 01_MAY_TAO_NOI_DUNG

## 1. Bài học về đóng gói tự thân (`vendor/`) chống đứt gãy khi Archive LAB
- Đề 00 quy định chuyển `D:\LINHX\LAB\*` sang `D:\LINHX\ARCHIVE\PROTO_2026-10-25\`. Việc viết `scripts/pack_vendor.py` đóng gói có chọn lọc 1.020 file (`skills/`, `scripts/`, `references/`, `ho-so-bien-tap/`, `brands/sakedemy/`, mẫu `persona-sample-60.json`) vào `01_MAY_TAO_NOI_DUNG/vendor/` giúp bộ điều phối chạy độc lập 100% mà không sửa 1 byte nào ở LAB gốc và không cần chép hàng chục GB cache/model weights.

## 2. Bài học kỹ thuật phát hiện qua 3 vòng Test thật với `cham_cau.py` (`LAB049`)
1. **Lỗi mã hoá UTF-8 trên Windows (`Vòng Test 1`)**:
   - `cham_cau.py` và `kiem_van_dich.py` của `LAB049` dùng `print()` tiếng Việt nhưng chưa bật `sys.stdout.reconfigure(encoding="utf-8")` (khác với `kiem_van.py` đã có dòng này). Khi gọi qua `subprocess` trên Windows mặc định `cp1252`, lệnh `--sach` bị lỗi `UnicodeEncodeError`.
   - **Cách khắc phục**: Cấu hình `PYTHONIOENCODING=utf-8` trong `dieu_phoi.py` và bổ sung `sys.stdout.reconfigure(encoding="utf-8")` vào bản `vendor/LAB049/`.
2. **Bẫy Blockquote Metadata đầu file (`Vòng Test 1`)**:
   - Hàm `doc_doan()` trong `cham_cau.py` bỏ qua dòng bắt đầu bằng `#`, `|`, `*Nguồn`, `---`, nhưng lại **gọt dấu `>` của blockquote để chấm như đoạn văn xuôi `Đ1`**. Do đó, nếu đặt khối truy vết ở đầu file Bước 08 bằng `> **Truy vết**: ...`, `cham_cau.py` sẽ chấm luôn dòng metadata đó và báo lỗi `chữ-số` / `thiếu-mã-nguồn(Module**)`.
   - **Cách khắc phục**: Đặt khối truy vết ở đầu file Bước 08 dưới dạng bảng Markdown (`| Hạng mục | Giá trị |`), vừa rõ ràng cho người đọc vừa được `cham_cau.py` bỏ qua chính xác.
3. **Ngưỡng độ dài câu trung bình (`19 – 39 từ`) và câu hai vế (`≤ 5%`) (`Vòng Test 2`)**:
   - Ở các bài viết chuyên sâu và báo cáo, nếu gộp 2 mệnh đề lớn bằng `, còn ... thì ...`, vừa đẩy độ dài câu trung bình vượt ngưỡng `39 từ` (`39.9` – `40.5 từ`), vừa chạm cờ cứng `hai-vế` (`VA-01`). Tách các câu ghép quá 50 từ thành hai câu 24–30 từ giúp nhịp văn chảy tự nhiên và đưa cả 3 loại nội dung vượt ngưỡng `CQS 95.8 – 96.8/100`, `cham_cau = ĐẠT 100%`.

## 3. Bài học về thử Outline trên Persona Neo (Module 2 + Module 4 + Module 5)
- Đưa 3 Persona Neo (đã lọc tầng nhân khẩu `LAB048` + đắp nỗi sợ ẩn và câu hay cãi `LAB049`) vào đọc thử 3 phương án Outline ngay ở Bước 4 giúp loại sớm các phương án nặng lý thuyết vĩ mô (Phương án A) hoặc liệt kê mẹo bề nổi (Phương án C), đồng thời biến chính **câu phản biện của Persona** thành danh sách ràng buộc bắt buộc cho Bước 6.
