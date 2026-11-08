---
name: hap-thu-su-kien
description: Hấp thu nội dung một sự kiện đã đi hoặc chỉ xem lại: từ ghi chú, ảnh slide, video YouTube, bài tường thuật, ra talk, pain point, solution, số liệu, chấm diễn giả, bài học áp dụng cho LINHX. Dùng khi Linh nói "vừa đi event X", "tóm tắt event", "hấp thu hội thảo", gửi ảnh slide hoặc link video.
---

# Hấp thu sự kiện

## Nguồn đầu vào (dùng hết những gì có)
- Ghi chú, ảnh slide, ghi âm Linh gửi.
- Video: `eventscan.py phude <youtube_url> <event_id>` lấy phụ đề (cần yt-dlp) vào `data/transcripts/*.txt`.
- Bài tường thuật trên báo, fanpage BTC, bài LinkedIn của diễn giả (WebSearch tên sự kiện + "tường thuật", "chia sẻ tại").

## Các bước
1. Đọc `output/BAN-DO-CHU-DE.md` để biết các **nhóm** đã có. Ý nạp từ seed (`da_noi`) có nhóm tự sinh; gom lại bằng file `{"nhom": {insight_id: [loại, nhóm]}}` và `eventscan.py gan-nhom <file>`.
2. Với từng phiên: tiêu đề, diễn giả, 3 đến 5 câu tóm tắt, rồi tách ý theo loại: `pain_point` (ai đang đau gì, nói bằng lời của họ), `solution` (cách làm cụ thể, không phải khẩu hiệu), `so_lieu` (kèm nguồn), `xu_huong`, `cong_cu`, `cau_noi` (trích nguyên văn, ghi ai nói). Gán `nhom`: dùng lại nhóm cũ nếu cùng ý.
3. Chấm diễn giả 1 đến 5 theo thang trong `references/schema.md` của radar-su-kien. Lấy ý kiến của Linh nếu Linh đã nghe trực tiếp; ý kiến Linh thắng.
4. Ghi `data/hap-thu/<event_id>.json` theo schema, chạy `eventscan.py absorb data/hap-thu/<event_id>.json` rồi `eventscan.py insight`.
5. Viết `output/hap-thu/<event_id>.md` (1 trang): 5 điều đáng nhớ; 3 pain point có thể thành dịch vụ hoặc offer của LINHX; 2 solution đáng thử ngay; người nên kết nối tiếp; 3 ý tưởng bài viết (góc nhìn riêng của Linh, không chép lại diễn giả).
6. Nếu có diễn giả hoặc nhà tài trợ mới đáng theo dõi: `radar.py all` (hoặc `eventscan.py export-lab035` rồi `radar.py cong-dong seed su-kien\data\xuat-lab035.json`) để bảng DN/KOL nhận.

Không đăng bài, không gửi tin cho ai. Trích nguyên văn phải đúng nguồn; không chắc thì ghi là diễn giải.
