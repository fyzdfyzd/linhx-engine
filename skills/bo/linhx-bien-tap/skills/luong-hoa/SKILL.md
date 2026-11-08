---
name: luong-hoa
description: Lượng hoá bốn lớp kiểm trong đầu biên tập viên (hiểu, tin, ý, giọng) thành con số, bằng trích xuất lặp nhiều lượt đến khi ổn định rồi so với dải của bài Linh đã đăng. Dùng khi cần biết bài nặng lỗi văn máy đến đâu mà không chỉ dựa vào giám khảo cảm tính. Hiện chỉ số liệu/1000 chữ đủ tách để chặn; xem references/dai-luong-hoa.md.
---

# Lượng hoá bốn lớp kiểm

Linh 19/10/2026: biên tập viên đọc với 3–4 lớp kiểm trong đầu, mỗi lớp ứng với một nhóm câu hỏi. Skill này biến từng câu hỏi thành thứ đếm được. Máy không chấm hay dở; nó trích từng ẩn dụ, số liệu, chuyện, chủ thể, chỗ phải nhớ, rồi script đếm.

| Lớp | Câu hỏi trong đầu biên tập viên | Chỉ số | Lỗi Vân Anh |
|---|---|---|---|
| 1. Hiểu | Người ngoài ngành đọc có hiểu ngay không? Ai nói câu này? Từ này là gì? | phải nhớ từ đoạn xa / 1000 chữ; thuật ngữ chưa giải nghĩa; % chủ thể không tên | VA-05, VA-06, DN |
| 2. Tin | Chuyện này có thật không, có ai thật, ở đâu, lúc nào, nói gì? | neo cụ thể mỗi câu chuyện; % câu tóm tắt trong chuyện | VA-07 |
| 3. Ý | Số này để làm gì? Bỏ đi bài có mất gì không? | số liệu / 1000 chữ; % số liệu không đỡ ý nào; số liệu nhắc lại cách ≥4 đoạn | VA-04 |
| 4. Giọng | Đây có phải người viết không? | ẩn dụ / 1000 chữ; ẩn dụ trải ≥2 đoạn; độ trải lớn nhất; % câu hai vế (`cham_cau.py`) | VA-01, VA-05 |

## Chạy
1. Hai subagent mới (không phải người viết, không thấy nhau), mỗi subagent đọc `${CLAUDE_PLUGIN_ROOT}/references/trich-xuat-dau-van.md` và bài, ghi `trich/<bai>.lan1.json`, `trich/<bai>.lan2.json`.
2. `python ${CLAUDE_PLUGIN_ROOT}/scripts/luong_hoa.py bai.md trich/<bai>.lan*.json`. Script dò lại mọi trích dẫn trong bài, bỏ mục bịa ("trích ảo"), báo trung bình và độ lệch giữa các lượt.
3. **Rà đệ quy:** chỉ số nào lệch giữa hai lượt quá 30% trung bình (hoặc trích ảo >10%) thì chạy thêm một lượt trích cho riêng phần đó, tối đa 4 lượt, đến khi lệch nhỏ. Còn lệch sau 4 lượt thì ghi "không ổn định" và không dùng chỉ số ấy để chặn bài.
4. So với dải của bài Linh đã đăng trong `${CLAUDE_PLUGIN_ROOT}/references/dai-luong-hoa.md`. Chỉ số ngoài dải thì ghi vào phiếu biên tập kèm mục trích làm bằng chứng (ẩn dụ nào, số nào, đoạn nào).
5. Sau khi tác giả sửa, chạy lại cả bốn lớp trên bản mới (vòng lặp sửa, đo, sửa), tối đa ba vòng như `bien-tap-bai`.

## Không làm
Không bảo subagent viết lập luận từng câu (bộ lọc chặn); chỉ xin JSON theo khuôn. Không dùng chỉ số chưa có dải bài đăng để chặn bài.
