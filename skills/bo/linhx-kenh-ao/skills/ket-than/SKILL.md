---
name: ket-than
description: Xây quan hệ dựa trên niềm tin với người trong vòng: chọn ai để chạm, chạm thế nào, có mục đích gì, ghi nhận khi họ đáp lại. Dùng cho bước vong, cham.
---

# Kết thân có mục đích

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`. Thang quan hệ: chưa biết → đã đọc → đã chạm → đã góp chuyện → được đáp → hai chiều → đồng minh.

1. **Vòng.** `vong-ds`. Thêm người bằng `vong-them --ly-do` (vì sao người này đáng học hoặc cùng khán giả). Persona cùng nhà thêm với `--la-nha` để cổng chặn chạm chéo.
2. **Chọn người.** Ưu tiên người ở bậc "được đáp" và "hai chiều" (giữ lửa), sau đó người "đã đọc" có bài mới trong 7 ngày. Bỏ qua người đã chạm 3 lần liền không đáp: cổng sẽ chặn, và đó là tín hiệu tôn trọng.
3. **Đề xuất.** `cham-de-xuat --nguoi ID --doc ID --loai thich|luu|theo_doi|binh_luan|nhan --muc-dich <trong danh sách hanh-vi.md> --vi-sao "..." [--noi-dung "..." --chi-tiet "..."]`. Bình luận phải nhắc một chi tiết có thật trong bài gốc (`--chi-tiet`), nói điều cụ thể, không tự quảng bá ở G0 đến G2.
4. **Bị chặn** thì đọc `ly_do_chan` và làm theo (đọc thêm, chờ nghỉ, đổi mục đích), không viết lại câu để lách.
5. **Làm.** `cham-viec` liệt kê việc đã duyệt. Phần lớn nền tảng không có API chính thức để chạm bài người khác, nên việc do Linh làm trên app hoặc trình duyệt có Linh xem. Xong thì `cham-xong --id`.
6. **Đáp lại.** Khi người kia trả lời bình luận, theo dõi lại, bình luận bài mình, nhắc tên mình: `dap --nguoi ID --loai ...`. Chỉ tín hiệu hai chiều mới cộng điểm tin.
