---
name: hoc-tu-ban-sua
description: So bản nháp AI với bản Linh sửa xong để rút luật giọng mới, ghi sổ học, chỉ đưa vào sổ tay giọng khi một cách sửa lặp lại từ 3 lần. Dùng khi Linh gửi lại bài đã sửa, nói "đây là bản tôi chốt", hoặc sau khi một bài được đăng.
---

# Học từ bản Linh sửa

Mượn từ athola voice-learn và writing-agent edit-diff-learner.

1. Lấy hai bản: bản AI giao (`ban-giao.md` hoặc `nhap-v2.md`) và bản Linh chốt (file Linh gửi hoặc bản đã đăng).
2. So từng đoạn. Với mỗi chỗ sửa, ghi: câu cũ, câu mới, loại sửa (bỏ, thêm chuyện, đổi chữ, đổi nhịp, đổi kết, sửa sự kiện), đoán lý do.
3. Bỏ qua sửa lỗi chính tả, sửa sự kiện đơn lẻ, sửa do toà soạn (nếu Linh nói rõ).
4. Ghi vào `${CLAUDE_PLUGIN_ROOT}/du-lieu/SO-HOC.md` (tạo nếu chưa có), mỗi chỗ sửa một dòng, có ngày và tên bài.
5. Đếm: loại sửa nào đã xuất hiện từ 3 lần ở ít nhất 2 bài, đề xuất cho Linh một thay đổi trong `SO-TAY-GIONG.md`. Ưu tiên mài sắc nước đi cũ hơn thêm luật mới.
6. Bản Linh chốt được thêm vào `du-lieu/mau-goc/` làm mẫu. Sau đó đo lại mốc:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_van.py do-giong <các bài thuần> -o ${CLAUDE_PLUGIN_ROOT}/du-lieu/moc-giong.json`
   Chỉ đưa vào tập đo những bài Linh tự viết hoặc sửa kỹ.
7. Chuyện mới Linh thêm vào bài thì ghi vào `KHO-CHUYEN-THAT.md`.

Không tự sửa sổ tay khi chưa đủ 3 lần. Một lần sửa có thể chỉ là tâm trạng hôm đó.
