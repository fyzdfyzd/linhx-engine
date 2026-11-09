# WF10 · Chiến lược, kế hoạch

Làn 3 · Chung · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Chiến lược sản phẩm/giá/khách theo chuẩn Trân Bảo của chị Hương

## Có sẵn
- Skill: chien-luoc 7 bước (LAB106), linhx-chuan, agy-tu-chay, the_opc (LAB117)
- Hiện trạng: A/B trên CTS: nhánh B qua D2 (3/11), nhánh A trượt P06

## Ai làm
Claude: đề, chấm · agy: nghiên cứu và viết · Linh: D2, D4 · mốc chuẩn: bộ Trân Bảo

## Máy đo (đạt mới qua)
12 tiêu chí high standard; PMF 12 tiêu chí; mọi giả định có ghi DATA_GAPS

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | CTS (đóng nhánh B tới D4) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | ifAgent Event 2027 | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | Agent Force gói thuê theo việc (LAB116) | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF10-chien-luoc-san-pham/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF10-chien-luoc-san-pham\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá làm chiến lược sản phẩm**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
