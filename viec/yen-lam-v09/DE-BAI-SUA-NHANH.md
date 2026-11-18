# Yên Lam: sửa nhanh sau khi Linh test v0.9 (07:24 18/11) → chuẩn bị 1.0 rc1

Luật chung: như `DE-BAI.md` luật 1–9, khác ở chỗ:
- Nền: `origin/agy/yl09-gop` (đỉnh bcbd81be). Mỗi phiếu tạo nhánh `agy/yl10-<ma>` từ nền, chỉ push nhánh đó.
- LUẬT CHỐNG CHUYỂN NỀN: mỗi lệnh test hay Playwright chỉ chạy 1 tệp, ghi log ra tệp. Nếu công cụ báo lệnh đã chuyển nền thì KHÔNG kết thúc lượt, KHÔNG ngồi chờ: gọi trạng thái lệnh đó liên tục tới khi xong.
- Chỉ chạy test mới của phiếu + test khoá liên quan trực tiếp (từng tệp). Phút 30 phải commit + push dù chưa xong, ghi CON_LAI.
- Giữ nguyên CSS kính, màu, phông. Giữ logo Le Bros ở kiosk.
- Ảnh duyệt bằng mắt: kiosk 1080×1920, điện thoại 390×844 (deviceScaleFactor 2), ghép trước/sau thành `bang-chung/yl10-<ma>/ghep-*.png` (≤600 KB), tự chấm 1–10, <8 là chưa xong.
- CẤM: deploy (trừ phiếu yl10-deploy), gửi mail thật (test dùng mock), in khoá/mật khẩu, xoá dữ liệu, AI sinh mặt người.
- KET-QUA ≤ 2000 ký tự: `dat: co|khong`, SHA đỉnh, test, ảnh + điểm, CON_LAI.

Góp ý gốc của Linh (07:24):
KIOSK: Lam to ra, giao diện bớt rối; đang nói theo từng câu, cần nói cả đoạn; nén tri thức vừa phải; nút refresh vì hay lag; bật camera để Lam thấy người đối diện (quần áo…), camera bật nhưng ẩn khung hình; tracking biểu cảm; log chat cho kỹ thuật xem ở link riêng; trang sửa nhanh tri thức + xem log + comment, không cần đăng nhập để test nhanh; giao diện chụp ảnh đang vỡ; chưa nối widget theo lời Lam nói (nói gì hiện thông tin đó).
ĐỒNG HÀNH: cần email xác nhận mới được tham gia trả lời (đưa lên trên); "Lam" → "Yên Lam", gồm nói và chat, chuyển qua lại dễ; nạp tri thức mới cho đồng hành; chưa tìm được theo tên nội dung, diễn giả.
TRI THỨC MỚI: tài liệu Lark https://lebrothers.sg.larksuite.com/docx/YpPOdpE8JoQe3PxINjmlcBdXgLd
