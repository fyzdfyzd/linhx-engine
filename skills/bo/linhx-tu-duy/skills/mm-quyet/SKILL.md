---
name: mm-quyet
description: Ghi một quyết định vào nhật ký quyết định của Linh (chỉ thêm, không sửa) kèm các thẻ mental model đã dùng, độ chắc, điều làm đổi ý và ngày chấm; hoặc chấm một quyết định cũ. Dùng khi Linh gõ /mm-quyet, nói "ghi quyết định", "chấm quyết định", hoặc sau /mm-chon cho một việc khó đảo ngược.
---

# Nhật ký quyết định

Lệnh: `node "${CLAUDE_PLUGIN_ROOT}/scripts/tu-duy.js" <lệnh>`

## Ghi quyết định mới
1. Hỏi hoặc rút từ cuộc trò chuyện đủ 9 trường:
   - `cau_hoi`
   - `boi_canh`
   - `lua_chon`: ít nhất 2, phải có phương án tốt nhất bị bỏ (M6)
   - `the`: 1–3 mã thẻ, **chọn trước khi nói tới quyết định** để tránh dùng thẻ biện minh
   - `lap_luan`
   - `quyet_dinh`
   - `do_chac`: 0–1
   - `doi_y_neu`: một dấu hiệu đo được, có ngày hoặc con số
   - `ngay_cham`: YYYY-MM-DD, thường sau 1–6 tháng
2. Ghi trường còn thiếu theo phần trả lời của Linh. Nếu Linh đã nói rõ mà chỉ thiếu ngày chấm, mặc định 3 tháng sau.
3. Viết JSON vào một file tạm, rồi chạy `quyet --file <file>`. Dùng file thay vì `--json` vì dấu nháy trên Windows dễ vỡ.
4. Báo lại mã quyết định và ngày chấm.

## Chấm quyết định
`cham <id> --dung dung|sai|mot-phan --ket-qua "..." --bai-hoc "..." --the-giup B3,C7 --the-nhieu M5`

- Mỗi quyết định chỉ chấm một lần. Script từ chối khi chấm lần thứ hai.
- Muốn bổ sung sau khi đã chấm thì dùng `vi-du`.
- Trước khi chấm, đọc lại phần "Đổi ý nếu" đã ghi, và hỏi Linh đúng điều đó.

Không bao giờ sửa `su-kien.jsonl` hay `nhat-ky-quyet-dinh.md` bằng tay. Nhật ký có giá trị chính vì không bị sửa.
