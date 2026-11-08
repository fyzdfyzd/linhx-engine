# linhx-kenh-ao v0.2 (LAB040)

Plugin Claude Code/Antigravity cho vòng nuôi kênh người ảo. Agent làm phần nghĩ (đọc, tiêu hoá, viết, chấm, soạn trả lời, rút bài học); CLI `scripts/kenhao.py` (Python chuẩn, không cần cài gì) làm phần không được sai: lưu trạng thái SQLite, cổng chặn, hạn mức, nhãn AI, nhật ký.

## Khung hành vi (lõi)
- Đọc, xem, tương tác, tiêu hoá gấp ít nhất 10 lần phần tạo (cổng đăng kiểm bằng số).
- Dựa trên niềm tin và quan hệ: thang 7 bậc với từng người, điểm tin chỉ tăng khi người kia đáp lại, chạm 3 lần không được đáp thì dừng.
- Mọi hành động có mục đích trong danh sách cho phép, kèm lý do riêng.
- G0 Quan sát → G1 Làm quen → G2 Góp chuyện → G3 Nuôi kênh, lên giai đoạn theo ngày tuổi và chỉ số quan hệ.
- Xưởng persona: tự học kiểu nhân vật gây cảm xúc, persona bắt buộc có character flaw, một phong cách chung.

## Bàn đăng: người chỉ bấm
`kenhao ban-dang --phuc-vu --goc <thư mục kênh hoặc thư mục chứa nhiều kênh>` mở `http://127.0.0.1:8765/` trên máy. Mọi việc ra ngoài của mọi persona đã soạn sẵn: bài (Đăng), bình luận bài người khác (Chép và mở), trả lời hạng vàng/đỏ (Gửi), bài học (Nhận). Mỗi thẻ ghi mục đích, cho ai, dự báo, và lý do cổng sẽ chặn nếu có. Máy chủ chỉ nghe 127.0.0.1, đòi mã phiên. Mọi lần bấm, sửa, bỏ kèm lý do là dữ liệu học.

## Tự học mỗi ngày
`kenhao hoc-ngay` (lịch 23:10) học từ bốn nguồn: số liệu bài, bàn đăng (khẩu vị người duyệt), quan hệ (kiểu chạm nào được đáp), cổng (agent hay bị chặn vì đâu). Tầng 1 tự áp có trần và tự hoàn; tầng 2 thành thẻ "Bài học" trên bàn đăng; tầng 3 chỉ là đề xuất cho Linh. Kênh tự chấm chính nó bằng Brier của dự báo lúc đăng. Chi tiết trong skill `hoc-ngay`.

## Bắt đầu
```
python scripts/kenhao.py --home D:\LINHX\KENH-AO\may init
python scripts/kenhao.py --home D:\LINHX\KENH-AO\may kiem-ho-so
python scripts/kenhao.py --home D:\LINHX\KENH-AO\may giai-doan
```
Rồi gọi skill `kenh-ao` để chạy một phiên. Chạy thử không chạm mạng: thêm `--thu`.

## Chạy thử 90 ngày
`python -I tests/gia_lap.py <thư mục tạm>` (đặt `SO_NGAY` để đổi): giả lập cộng đồng 30 người, agent làm đúng khung, người duyệt chỉ bấm qua bàn đăng với khẩu vị cài sẵn. Kiểm 15 điều: 9 cổng chặn và vòng G0 → G3, cộng 6 điều của vòng tự học (bàn đăng ghi đủ kiểu bấm, tìm ra tín hiệu cài sẵn, tìm ra khẩu vị người duyệt, Thompson dồn về cái thắng, agent tự soi giảm lỗi, Brier dưới mức đoán bừa).

## Tay chân
- Đăng: Postiz tự host qua Public API (`adapters/postiz.py`, đọc từ code Postiz 16/10/2026, chưa chạy thật).
- Hộp thư và số liệu: Graph API Meta (`adapters/meta.py`, chưa kiểm tài khoản thật).
- Chạm bài người khác: Linh bấm "Chép và mở" trên bàn đăng rồi dán và gửi, vì các nền tảng lớn không có API chính thức cho việc này.

## Hook
`hooks/hooks.json` chặn ghi thẳng vào kenh.db, chặn gọi thẳng tool đăng/bình luận của MCP, và hỏi Linh trước khi sửa luật gốc.
