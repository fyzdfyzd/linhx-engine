---
name: nhu-cau-doc-gia
description: B2 radar khoảng trống. Từ dữ liệu hiện tượng, tính chỉ số cầu/cung, bài vượt trung vị, bài của tác giả nhỏ mà nổ, rồi gom thành cụm NHU CẦU độc giả (không phải tag) kèm nỗi đau và từ khoá Anh, Việt. Dùng sau B1 của LAB029.
---

# B2. Nhu cầu độc giả

1. `python gapscan.py tin-hieu` → `02-tin-hieu.json` và `02-mau-cho-claude.md`.
2. Đọc `02-mau-cho-claude.md`. Ba tín hiệu quan trọng:
   - **Cầu/cung > 1,5**: độc giả thưởng nhiều hơn số người viết.
   - **Bài vượt trung vị của chính tác giả** (×3 trở lên): chủ đề kéo người đọc mạnh hơn tên tuổi.
   - **Tác giả nhỏ mà bài nổ** (dưới 5.000 follower, bài ở top 10%): nhu cầu thật chưa có người lớn chiếm.
   Tag đông bài mà cầu/cung dưới 1 là chỗ cung thừa, tránh.
3. Gom thành **6 đến 12 cụm nhu cầu**. Một cụm là một nỗi lo hay mong muốn của một nhóm người, đặt tên bằng lời người đọc ("Tuổi trung niên và lão hoá"), không phải tên ngành ("Sức khoẻ"). Mỗi cụm cần ≥ 5 bài bằng chứng.
4. Viết `02-cum.json` theo `references/schema.md`: `ten`, `nhu_cau`, `noi_dau` (lời độc giả, giải pháp đã thất bại, khoảnh khắc kích hoạt), `bang_chung`, `the`, `tu_khoa_en`, `tu_khoa_vi`, `chuyen_giao` (0 đến 1) và `ly_do_chuyen_giao`.
   - `tu_khoa_vi` viết **có dấu**, theo cách người Việt thật sự nói (vòng phản tư: tự hỏi "người Việt gõ gì vào Google, viết gì trên Facebook khi gặp chuyện này?"). Tránh từ một âm tiết dễ trùng ("ai", "giàu").
   - `chuyen_giao`: nhu cầu này có tồn tại ở Việt Nam không, có bị chặn bởi văn hoá, pháp lý, thu nhập không. Ghi lý do một câu.
5. `python gapscan.py gan-cum`, đọc cảnh báo, chỉnh từ khoá cho cụm quá ít hoặc quá nhiều bài, chạy lại.
6. `python gapscan.py kiem b2`.

Không gọi chủ đề nào là "đang hot" nếu không trỏ được về bài và số đo cụ thể.
