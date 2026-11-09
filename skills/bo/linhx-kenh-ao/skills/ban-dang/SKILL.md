---
name: ban-dang
description: "Mở bàn đăng cho Linh: mọi bài, câu bình luận, câu trả lời và bài học của một hoặc nhiều persona đã soạn sẵn, Linh chỉ bấm Đăng, sửa hoặc Bỏ. Dùng khi Linh muốn duyệt và đăng nhanh, hoặc hỏi \"hôm nay có gì cần đăng\"."
---

# Bàn đăng

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py"`.

1. Trước khi mở bàn, mọi mục phải đã soạn xong: bài qua `bai-them` + `bai-cham` (trạng thái `cho_duyet`), chạm qua `cham-de-xuat`, trả lời hạng vàng/đỏ qua `hop-thu-soan`, bài học tầng 2 qua `bai-hoc-them`.
2. Mở giao diện trên máy Linh: `ban-dang --phuc-vu --goc <thư mục kênh hoặc thư mục chứa nhiều kênh>` rồi đưa Linh link `http://127.0.0.1:8765/`. Một thư mục chứa 50 kênh con thì bàn gom cả 50, lọc theo persona.
3. Linh bấm trên giao diện. Nếu Linh muốn duyệt qua chat, dùng `ban-dang --goc <kênh>` để lấy danh sách rồi `ban-dang --bam <id> --loai bai|cham|tra_loi|bai_hoc [--noi-dung "..."] [--hanh-dong bo --ly-do "nhạt"]`.
4. Không bao giờ bấm thay Linh. Không tìm đường đăng khác khi cổng chặn; báo lý do cổng.

Ý nghĩa nút:
- Bài: Đăng = duyệt; tới giờ hẹn thì `dang` tự đăng qua Postiz. Bài đã quá giờ thì đăng luôn. Sửa chữ trước khi bấm được ghi là một lần sửa (để học).
- Chạm: nền tảng không có API cho bình luận bài người khác, nên nút là "Chép và mở": chép câu, mở bài, Linh dán và gửi.
- Trả lời: Gửi = duyệt và gửi qua adapter hộp thư (Graph API Meta).
- Bài học: Nhận = thành luật viết, agent đọc từ phiên sau.
Mọi lần bấm, sửa, bỏ (kèm lý do) và thời gian chờ được ghi vào bảng `phan_hoi` cho `hoc-ngay`.
