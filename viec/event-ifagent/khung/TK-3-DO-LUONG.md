# TK-3 · Khung 8 màn đo lường (hướng A, nền Đêm)
Thiết kế · Chân Cơ · 14/11/2026 · commit `cd62cd8`, nhánh `claude/project-thread-9c61ql`
- Khung HTML: `docs/thiet-ke/event-web/a/60-*.html` đến `71-*.html`. Sinh bằng `sinh-khung-do-luong.py`.
- Ảnh cỡ thật (27 tấm): `NOP/thiet-ke/do-luong/<màn>-<rộng>-cd62cd8.png`.
- Theo đề `NOP/TAO-NHAN-DE-KHUNG-MAN-DO-LUONG.md`. Số trên khung là số mẫu lấy theo đề; Build thay bằng số API.

## Luật chung cho Build
1. Token ev.css TK-1. Biểu đồ chỉ dùng một màu xanh (#0088FF, cột cao điểm #2E9FF8). Bản đồ nhiệt dùng thang xanh 7 bậc từ #162238 đến #7CC4FF. Số và nhãn luôn ở màu chữ, không tô màu theo cột.
2. Đầu màn: logo, tên màn, dấu **"Cập nhật trực tiếp"** (chấm ngọc) ở màn có SSE, nhãn viền **"Dữ liệu mẫu"** ở màn chạy dữ liệu mẫu. Dưới 390 đầu màn xếp dọc.
3. Phần **ước lượng** (số từ điện thoại khách) luôn nằm trong một khung viền nét đứt riêng, có chữ "ước lượng".
4. Cuối trang demo có một nút nhấn: "Làm báo cáo này cho sự kiện của bạn" (R1–R3) hoặc "Đo gian hàng của bạn" (T1–T3).
5. Không emoji trên nút và trên màn lớn. Tường cảm xúc dùng chữ + chấm thay cho emoji của đề.
6. Không cuộn ngang ở 390 (đã đo bằng máy chụp, 0 màn tràn).

## Màn
| Tệp | Cỡ | Nội dung chính |
|---|---|---|
| 60-r3-truc-tiep | 390, 1440 | "Sự kiện đang chạy" · 5 chỉ số · cột theo giờ 8–17 · 8 hoạt động mới nhất có giờ · khung ước lượng |
| 60-r3-het-han | 390 | "Đường dẫn đã hết hạn hoặc đã bị thu hồi." · "Xin đường dẫn mới từ ban tổ chức." |
| 61-v3-dien-thoai / 61-v3-da-gui | 390 | "Bạn đang thấy thế nào?" · 6 cảm xúc · ô chữ ≤ 3 từ · **Gửi** · màn "Cảm ơn bạn. Nhìn lên màn lớn nhé." (chữ chờ duyệt) · lỗi "Bạn vừa gửi rồi, đợi ít giây nhé." |
| 62-v3-man-lon | 1920 | tỉ lệ 6 cảm xúc · chỉ số năng lượng 0–100 · đường 60 phút (ô 2 phút) · tối đa 24 chữ đã duyệt · QR "Quét mã, gửi cảm xúc của bạn" |
| 63-v3-duyet | 390, 1440 | Chờ duyệt: **Hiện · Bỏ · Bỏ và chặn máy** · Đang hiện: **Gỡ** |
| 64-t1-ban-do-nhiet | 390, 1440 | lưới 16×10 có 6 khu · chú giải thang nhiệt · khu đông nhất (%) · thanh giờ 08:00–17:30 + "Phát lại cả ngày" |
| 65-t2-thoi-gian-dung | 390, 1440 | thẻ mỗi quầy (dừng ở giữa, 3/4 khách dưới X, % dừng từ 30 giây) · phân bố 5 mốc có chọn quầy · xếp quầy |
| 66-t3-duong-di / 66-t3-dien-thoai | 390, 1440 / 390 | phễu 3 bước · 5 đường đi phổ biến · số điểm trung bình · điện thoại: "Bạn đã qua … · Còn …", "Quét mã ở điểm tiếp theo. Qua đủ 3 điểm là đổi được quà." (ước lượng) |
| 67-r1-nha-tai-tro | 390, 1440 | chọn 1 trong 3 nhà tài trợ · 5 chỉ số · tỉ lệ để lại liên hệ · giờ cao điểm · cột theo giờ · xếp trải nghiệm |
| 68-r2-cuoi-ngay / 68-r2-ban-in-a4 | 390, 1440 / 794 | "Báo cáo ngày 14/11/2026" · 3 câu tóm tắt · 4 điểm nhấn · 3 khuyến nghị · 5 chỉ số · cột · xếp · khung ước lượng · **In / Lưu PDF** · bản A4 nền trắng |
| 69-v1-so-lieu-man-lon | 1440, 1920 | 3 số lớn (hỏi nhân vật, chụp, chơi) · cột theo giờ · khách quan tâm nhất |
| 70-v2-man-lon / 70-v2-duyet | 1920 / 390, 1440 | lưới 12 ô ảnh (4–24), ảnh mẫu có nhãn "Dữ liệu mẫu", QR mời chụp · duyệt: **Hiện · Gỡ**, không tên khách |
| 71-do-luong-trang-thai | 390, 1440 | dùng chung: Đang tải (khối xám), Trống "Chưa có lượt nào. Số sẽ hiện ngay khi có khách đầu tiên.", Mất kết nối "Mất kết nối. Kiểm tra mạng rồi thử lại." + "Đang tự thử lại · số cuối lúc …" + **Thử lại**; mất kết nối thì giữ số cuối, dấu trực tiếp chuyển xám |

## Ảnh
Ô ảnh tường V2 đang dùng ảnh mẫu có sẵn trong `img/`. Ảnh chuẩn lấy từ hàng chờ của Thái Văn Cơ khi có.

## Chờ Sản phẩm duyệt
Toàn bộ chữ do Thiết kế viết (tiêu đề, câu trạng thái, nút cuối trang). Nhãn khối "AI Tracking", "AI Campaign Report" giữ theo tên khối trong catalog; Quách Gia quyết có Việt hoá không.

## Lần sửa 1 (cd62cd8)
Theo NOP/SP-DOC-CHU-TK-3.md (Quách Gia duyệt, S1–S6): "Rạp phim mẫu · Bước vào phim"; "để lại liên lạc"; "cột sáng là giờ hiện tại"; số cột xếp có dấu chấm hàng nghìn; bỏ dòng ước lượng trên màn điện thoại khách T3; tường ảnh chỉ một nhãn "Dữ liệu mẫu" ở đầu màn. Nhãn "AI Tracking", "AI Campaign Report" giữ tiếng Anh (tên giải pháp).

## Lần sửa 2 (4050af8)
Theo phiếu CHAM/TK-3-DO-LUONG-cd62cd8-cham1.md: màn 63 duyệt chữ ở 390 xếp chữ và giờ một hàng, nút xuống hàng dưới; màn 62 tường cảm xúc vừa đúng 1920×1080; màn 71 mất kết nối có dấu "Cập nhật trực tiếp" màu xám. Ảnh mới: do-luong/*-4050af8.png.
