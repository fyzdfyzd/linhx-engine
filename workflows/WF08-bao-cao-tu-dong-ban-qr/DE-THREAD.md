# WF08 · Báo cáo tự động bán QR

Làn 3 · OPC · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Báo cáo cá nhân hoá sinh từ dữ liệu, giao tự động sau khi trả QR

## Có sẵn
- Skill: report-core (LAB046, cổng 17 luật), brand-check, bao-cao-va-sua, module report của engine
- Hiện trạng: CTS đang bán; report-core chiêm tinh 97,5/100; báo cáo 'AI nói gì' chạy ở ENGINE 0.1

## Ai làm
Claude: blueprint, cổng chất lượng · agy: domain, kho lời giải · Linh: D4 mẫu đầu

## Máy đo (đạt mới qua)
cổng 17 luật đạt; 0 số bịa; trả tiền tới nhận báo cáo ≤ 10 phút; 20 mẫu ngẫu nhiên không lỗi

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | 'AI nói gì về thương hiệu' (B4) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Bản đồ sao Chiêm Tinh Số chạy trên report chung | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | Báo cáo mới: hướng nghiệp | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF08-bao-cao-tu-dong-ban-qr/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF08-bao-cao-tu-dong-ban-qr\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá báo cáo tự động bán QR**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
