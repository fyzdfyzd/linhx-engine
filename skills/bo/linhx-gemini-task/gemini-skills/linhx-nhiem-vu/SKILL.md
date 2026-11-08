---
name: linhx-nhiem-vu
description: Chuẩn làm nhiệm vụ dài cho LINHX trong Gemini Task: luật nguồn, cấu trúc thư mục, checkpoint zip, tự kiểm bằng script, nối lượt. Dùng khi đề gọi @linhx-nhiem-vu hoặc khi làm nhiệm vụ thu thập dữ liệu, nghiên cứu, dựng file cho LINHX.
---

# Chuẩn nhiệm vụ LINHX

Người giao việc là Claude (đề do Claude viết, Linh duyệt). Kết quả sẽ được chấm bằng máy, nên **làm đúng chuẩn dưới đây quan trọng hơn làm nhiều**.

## Máy của bạn (đã đo 17/10/2026)
- Bash KHÔNG ra mạng: curl, pip, npm bị chặn, không cài thêm thư viện. Lấy web bằng công cụ tìm kiếm và duyệt web của bạn, lưu nội dung đọc được vào file trong thư mục làm việc, rồi xử lý bằng Python có sẵn (sqlite3, pandas, Jinja2, WeasyPrint, Pillow, python-pptx; có LibreOffice, Chromium headless, font Noto tiếng Việt).
- Không có pytest: dùng `python3 -m unittest`. Không tạo file trùng tên thư viện (pytest.py, json.py, test.py…). In phiên bản công cụ và log đầy đủ.

## Luật
1. Không bịa. Mỗi dòng dữ liệu có URL gốc đã mở được; ghi URL gốc, không bọc `google.com/search?q=`.
2. Bản quyền: không lưu toàn văn tài liệu có bản quyền; chỉ URL, tiêu đề, trích ≤ 40 từ trong ngoặc kép, tóm ý viết lại. Phạm vi công cộng thì được lưu, ghi giấy phép.
3. Tôn trọng robots.txt, ≤ 1 yêu cầu/giây/tên miền, không đăng nhập, không vượt paywall.
4. Câu trọn vẹn: tuyệt đối không cắt đoạn văn theo số chữ/ký tự. Thiếu chỗ thì viết ngắn lại thành câu đủ ý.
5. Mọi con số trong TONG-KET.md và câu trả lời phải do script đếm. Không hứa trước số trang hay số dòng.
6. Mọi kết quả nằm trong file và zip. Không để kết quả chỉ trong canvas hay chỉ trong bảng chat.
7. Không hỏi lại giữa chừng; tự chọn hợp lý và ghi lý do vào NHAT-KY.md.
8. Tiếng Việt cho tài liệu; tên cột, mã, tên file không dấu.

## Thư mục chuẩn
```
<MA>/TIEN-DO.md  NHAT-KY.md  TONG-KET.md  TIEP-THEO.md (khi chưa xong)
<MA>/data/  <MA>/scripts/  <MA>/scripts/tests/  <MA>/output/
```
Đề có thể thêm file riêng; giữ đúng tên file đề yêu cầu.

## Checkpoint và nối lượt
- Xong mỗi pha: cập nhật TIEN-DO.md, rồi `python3 scripts/dong_goi.py <MA> pha-N` (tạo `<MA>-pha-N.zip`).
- Hết thời gian mà chưa xong: ghi TIEP-THEO.md (dừng ở đâu, còn gì, lượt sau bắt đầu từ đâu), rồi vẫn đóng gói.
- Lượt sau có đính kèm zip cũ: giải nén, đọc TIEP-THEO.md, chạy tiếp, không làm lại từ đầu.

## Tự kiểm trước khi trả lời (bắt buộc)
```
python3 scripts/tu_kiem.py <MA> --cot-van-ban tom_y_vi,mo_ta
```
Script đếm file, dòng và cột mỗi CSV; đoạn văn không kết thúc bằng dấu câu; URL bọc google; file trùng tên thư viện; tìm SQLite và đếm dòng mỗi bảng. Sửa hết lỗi nó báo, chạy lại, dán log cuối vào TONG-KET.md.

## Đầu ra cuối
`python3 scripts/dong_goi.py <MA> FULL` rồi đưa link tải `<MA>-FULL.zip`. Trả lời đúng 10 dòng: đã làm gì, số liệu chính (từ log tự kiểm), chưa làm được gì và vì sao.
