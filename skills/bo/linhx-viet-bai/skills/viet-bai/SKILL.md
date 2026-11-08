---
name: viet-bai
description: Quy trình viết bài chuẩn cho Linh (Lê Bích / Đinh Trần Tuấn Linh), từ đơn hàng đến bản giao, 7 trạm, không bịa chuyện. Dùng khi Linh nhờ viết bài báo, op-ed, tản văn, essay, bài Facebook, Substack, LinkedIn, hoặc nói "viết giúp tôi bài…", "lên bài cho Dân trí/Bloomberg/CafeBiz".
---

# Viết bài cho Linh

Đường dẫn trong skill này tính từ thư mục gốc của plugin (`${CLAUDE_PLUGIN_ROOT}`, tức hai cấp trên file này).

Nguyên tắc chia việc (mượn từ khazix-writer): **AI tìm tư liệu, dàn ý, ẩn dụ, kiến thức nền. Linh lo chuyện thật, góc nhìn cốt lõi, cảm xúc thật.** AI viết nháp để Linh sửa khoảng 20%, không viết thay Linh.

Mỗi bài có một thư mục làm việc `bai/<yyyy-mm-dd>-<ten-ngan>/` trong folder Linh đang mở (hoặc nơi Linh chỉ định). Các file trạm ghi vào đó.

## Trạm 1. Nhận đơn → `don-hang.md`

Hỏi tối đa 3 câu, chỉ hỏi cái chưa rõ:
1. Kênh và ký tên nào? (Lê Bích hay Đinh Trần Tuấn Linh; xem `skills/chuyen-kenh/references/kenh.md`)
2. Chủ đề, và Linh nghĩ gì về nó (một câu là đủ)?
3. Có chuyện thật nào Linh muốn kể không?

Không hỏi được (Linh vắng) thì chọn mặc định: Lê Bích, Dân trí Tâm điểm, 1.200–1.500 chữ. Ghi rõ đã chọn mặc định.

## Trạm 2. Tìm cái tứ → `tu.md`

Một bài cần một nghịch lý, viết được thành một câu. Ví dụ đã in: "người ta tìm đạo lý mong kết thúc có hậu, người bán đạo lý tạo ra kết thúc có tiền".

- Đưa 3 tứ khác nhau, mỗi tứ một câu, kèm tên khái niệm có thể đặt (nước đi số 4) và một cú chơi chữ ứng viên (nước đi số 3).
- Ghi kèm **phản chứng mạnh nhất** cho mỗi tứ. Lập trường là giả thuyết.
- Chủ đề mở, chưa có tứ: chuyển sang skill `y-tuong-bai` (vòng lặp LAB024) rồi quay lại.
- Chọn tứ khuyến nghị và đi tiếp. Linh có thể đổi sau.

## Trạm 3. Nạp nguyên liệu → `nguyen-lieu.md`

Cửa kiểm tư liệu (mượn từ human-writing): bài từ 1.200 chữ phải có ít nhất 5 tư liệu, mỗi cái gắn nhãn:
- `chuyen-that`: lấy từ `du-lieu/KHO-CHUYEN-THAT.md` hoặc lời Linh kể trong đơn hàng.
- `nguon`: số liệu, trích dẫn có link hoặc tên báo cáo kiểm được.
- `minh-hoa`: phép tính đồ chơi, giả định, ghi rõ là giả định trong bài.

Tìm thêm trong vault của Linh nếu có: `D:\LINHX\IDEA\CONTENT_VAULT\` (`_PATTERNS/`, `_ANGLES/`, `_VAULT/`), `AUTHOR_PROFILE.md`.

Không đủ 5 tư liệu thì: tìm thêm, hoặc để `[CẦN LINH: chuyện về …]`, hoặc rút bài xuống khoảng 600 chữ. **Chi tiết không có nguồn là chi tiết giả, không được vào bài.**

## Trạm 4. Dàn ý → `dan-y.md`

Đọc `skills/giong-linh/references/SO-TAY-GIONG.md` và 2 bài cùng kênh trong `du-lieu/mau-goc/` trước khi dàn ý.

Khung mặc định (không bắt buộc, nhưng đã thấy trong các bài thuần):
1. **Cảnh mở**: một chuyện nhỏ cụ thể hoặc một hành động của người đọc ("mở điện thoại của bạn ra"). Không bối cảnh, không câu hỏi tu từ.
2. **Gọi tên**: đặt tên hiện tượng, hoặc lật một chữ.
3. **Chân dung**: 2–3 cảnh "tôi thấy" có chi tiết vật lý, có thể nhại giọng.
4. **Bằng chứng nghề**: chuyện trong nghề, số liệu, phép tính đồ chơi.
5. **Chuyện bên lề**: một đoạn rẽ ngang tưởng lạc đề.
6. **Kết**: quay về hình ảnh mở, câu chốt ngắn tự giễu hoặc bỏ lửng.

Với ký tên Đinh Trần Tuấn Linh trên kênh kinh tế, khối 4 dài hơn, kết có thể là một đề xuất cụ thể, nhưng một đề xuất thôi, không danh sách chia vai.

## Trạm 5. Viết nháp → `nhap-v1.md`

- Văn xuôi liền mạch, không tiêu đề phụ, không gạch đầu dòng (trừ khi kênh yêu cầu, xem kenh.md).
- Câu dài chảy, trung vị khoảng 30 chữ. Một hoặc hai câu rất ngắn đứng riêng, không hơn.
- Humor, chuyện trước; lý thuyết sau. Cho thấy trước, giải thích sau.
- Viết số theo kênh: báo dùng chữ số, essay/Facebook viết bằng chữ.
- Giữ nguyên mức chắc chắn của tư liệu: "có thể" không thành "chắc chắn".

## Trạm 6. Biên tập → `nhap-v2.md` + `bao-cao-soat.md`

Chạy skill `soat-giong`. Tóm tắt:
1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_van.py kiem nhap-v1.md --moc ${CLAUDE_PLUGIN_ROOT}/du-lieu/moc-giong.json`
2. Ba lượt đọc độc lập (giọng, nội dung và tư liệu, người đọc báo), không lượt nào đọc kết luận của lượt khác. Gộp thành một danh sách sửa, ghi rõ **những câu hay phải giữ**.
3. Sửa một lần thành `nhap-v2.md`. Tối đa 2 vòng. Được phép kết luận "không cần sửa".

## Trạm 7. Chuyển kênh và giao → `ban-giao.md`

Chạy skill `chuyen-kenh`: tít (3 phương án), sapo, độ dài, cách ký tên, ảnh gợi ý. Bài Facebook rút từ bài báo phải viết lại, không cắt dán.

Giao cho Linh: `ban-giao.md` + danh sách `[CẦN LINH]` còn trống + điểm kiem_van. Khi Linh gửi lại bản đã sửa, chạy `hoc-tu-ban-sua`.

## Không làm

- Không bịa chuyện riêng của Linh, không bịa khảo sát, không "một nghiên cứu gần đây cho thấy" khi không có nguồn. Bản CafeBiz mẫu do AI viết năm 2026 trong vault từng mắc lỗi này.
- Không viết kết bằng lời khuyên chung chung chia vai.
- Không đăng, không gửi bài đi đâu. Bản giao là file; Linh tự gửi báo.
