---
name: xuong-persona
description: Tự học kiểu nhân vật nào làm người ta thích, chia sẻ, tranh luận; phát triển persona có character flaw theo phong cách chung. Dùng khi đọc được bài phản ứng mạnh, khi cần persona mới cho Persona OS, hoặc khi Linh hỏi "persona nào đang ăn".
---

# Xưởng persona

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

1. **Gắn nhãn khi đọc.** Bài có tương tác cao: `persona-gan --doc ID --kieu <slug kiểu nhân vật> --cam-xuc a,b --phan-ung <thich|chia_se|tranh_luan|luu|binh_luan|gan_ten_ban> --flaw "khuyết điểm hiện ra" --giong "..."`. Kiểu đặt tên ổn định (ví dụ `nguoi-ke-that-tha`, `ba-ngoai-hoi-xua`).
2. **Xếp hạng.** `persona-xep-hang` → `bao-cao/PERSONA-<ngày>.md`: kiểu nào kéo cảm xúc và phản ứng gì, khuyết điểm nào hay đi kèm.
3. **Phát triển.** Viết persona ứng viên vào `ho-so/persona/<ma>.md` theo khuôn `_MAU.md` (13 mục + khối json). Bắt buộc: ít nhất một flaw có `bieu_hien`, `vi_sao_de_thuong`, `khong_bao_gio`; lập trường tranh luận có `vi_sao` và ngoài chủ đề cấm; `phong_cach` đúng mã trong `phong-cach.md`.
4. **Kiểm.** `persona-kiem` phải xanh trước khi đưa Linh duyệt.
5. **Thử.** Persona mới bắt đầu ở G0 như mọi kênh; kết quả 30 ngày so theo cảm xúc và phản ứng trong RETRO.

Flaw là nét người làm nhân vật đáng thương (vụng, trì hoãn, cứng đầu, nói quá rồi tự nhận), không phải hành vi gây hại hay xúc phạm người khác. Tranh luận là quan điểm có lập luận, không phải câu chọc giận.
