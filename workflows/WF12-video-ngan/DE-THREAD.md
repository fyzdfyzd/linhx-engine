# WF12 · Video ngắn, reel

Làn 3 · Chung · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Reel, trailer, video giải thích; có giọng Việt, phụ đề

## Có sẵn
- Skill: phim-code v0.3 (LAB059), sd-* (studio), gen-video anh Vinh, flow-canh-tron-khung
- Hiện trạng: Render thử 4 giây; trailer CSMO đang có thread riêng

## Ai làm
Claude: kịch bản, chấm · agy: dựng · Gemini Flow/Veo máy cty: cảnh · Linh: D2, D4

## Máy đo (đạt mới qua)
kiem_khung + kiem_video (LUFS, khung đen, freeze); phông đủ dấu; chấm từng shot

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | Trailer diễn giả CSMO (gộp với thread đang chạy) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Reel ifAgent Event | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | Video giải thích báo cáo CTS | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF12-video-ngan/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF12-video-ngan\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá dựng video ngắn**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
