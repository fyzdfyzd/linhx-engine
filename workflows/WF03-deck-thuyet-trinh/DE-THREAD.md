# WF03 · Deck thuyết trình, chào khách

Làn 2 · Chung · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Deck HTML/PPTX từng slide một ý, đúng brand, có vòng tự chấm

## Có sẵn
- Skill: linhx-deck 15 bước (LAB027), vong-lap-slide (LAB099), dung-deck, anh-sang-slide, proposal-studio
- Hiện trạng: Chạy trọn 1 lần, Linh OK 30/10 (deck Sakédemy chào VCB 11/11 slide đạt)

## Ai làm
Claude: ghost deck, chấm · agy: dựng slide · ChatGPT Plus: ảnh rời không chữ · Claude máy cty: chấm mắt mới · Linh: D2 template, D4

## Máy đo (đạt mới qua)
vls.py đo trên render: tương phản, tràn chữ, phông đủ dấu; 3 người chấm tách thợ ≥ 4/5 mỗi slide; ≤ 3 vòng

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | Bài nói CSMO Topic 07 (18/11) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Deck ifAgent Event chào một brief thật | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | Deck Agent Force chào DN đầu tiên | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF03-deck-thuyet-trinh/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF03-deck-thuyet-trinh\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá deck thuyết trình**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
