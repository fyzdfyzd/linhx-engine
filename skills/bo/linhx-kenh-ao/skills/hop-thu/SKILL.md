---
name: hop-thu
description: Kéo bình luận và tin nhắn, phân loại xanh/vàng/đỏ, soạn trả lời đúng giọng nhân vật, gửi qua cổng, cập nhật điểm fan. Dùng cho bước hop_thu.
---

# Hộp thư

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

1. `hop-thu-keo` rồi `hop-thu-phan-loai` (luật trong `ho-so/hang-rui-ro.md`). Spam tự ẩn; brand và chuyện lớn vào hàng chuyển Linh và tạo brand lead.
2. `hop-thu-ds --trang-thai cho_soan`. Đọc từng tin, nếu luật bắt sai thì `hop-thu-gan --id --hang --nhan --ly-do`.
3. Soạn: `hop-thu-soan --id --tra-loi "..."`. Ngắn, đúng giọng, nhắc tên người, trả lời đúng câu họ hỏi. Ai hỏi có phải AI không: trả lời thật, câu phải chứa `cau_tu_nhan_ai` trong hồ sơ.
4. Gửi: `hop-thu-gui`. Hạng xanh tự gửi ở mức tự chủ 3; vàng cần `hop-thu-duyet`; đỏ chỉ khi Linh duyệt (`--linh`). DM chỉ trong 24 giờ sau tin của người kia.
5. `fan-cap-nhat`; người lên bậc fan hoặc siêu fan thì ghi vào báo cáo phiên để Linh biết.

Không nhắn chủ động cho người chưa từng nhắn; tôn trọng `khong_nhan`.
