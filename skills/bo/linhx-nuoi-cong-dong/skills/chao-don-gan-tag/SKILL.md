---
name: chao-don-gan-tag
description: Soạn lời chào người mới theo nguồn vào (lớp nào, workshop, giới thiệu), kèm một câu hỏi chia nhánh để gắn tag đầu tiên, và các tin SOP theo mốc D+1/3/7/14/30/90. Dùng khi có lớp mới vào cộng đồng hoặc Linh nói "soạn lời chào", "soạn tin SOP".
---

# Chào đón và gắn tag

Mẫu ý tưởng: lời chào 企业微信 theo mã kênh + câu trắc nghiệm thành tag (LAB041 refs/C mẫu 1–2).

1. Đọc `config/cong-dong.json` (`sop_nguoi_moi`, `thang_offer`) và `output/NHAC-VIEC-TUAN.csv`.
2. Với mỗi lớp/mốc cần làm, soạn **một bài đăng chung** cho nhóm lớp (≤ 90 chữ, gọi đúng tên lớp/khoá, nhắc 1 điều học viên đã làm trong lớp) và **một bản tin nhắn riêng** chỉ cho người `dong_y_lien_he=1`.
3. Lời chào D+1 kết thúc bằng một câu hỏi chọn 1 trong 3–4 đáp án (ví dụ: "Bạn muốn giao cho agent việc nào trước: A soạn văn bản, B tổng hợp số liệu, C trả lời khách, D khác"). Ghi đáp án ↔ tag vào cuối bản nháp để SO nhập lại thành `tra_loi_khao_sat`.
4. Giọng: anh/chị, ngắn, không chào bán trước D+30; D+90 mới nhắc bậc offer kế tiếp.
5. Xuất thành file `output/TIN-NHAP-<ngày>.md`. Không gửi.
