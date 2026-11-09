# WF02 · Trang bán OPC (QR)

Làn 2 · OPC · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Trang bán một sản phẩm B2C: giới thiệu, nhập thông tin, QR, giao hàng tự động

## Có sẵn
- Skill: web-thiet-ke, thiet-ke landing, ux-copy, ra-phap-che (LAB107), brand-chiemtinh
- Hiện trạng: chiemtinh.vn đang bán; landing CTS LAB106 dựng 3 nhánh; chưa có khuôn chung

## Ai làm
Claude: đề, copy, pháp chế, chấm · agy: dựng · Linh: D2, D4, giá

## Máy đo (đạt mới qua)
một đơn QR đi trọn (kiểm T2); 0 lỗi đỏ pháp chế; chụp 360/1280; thời gian từ vào trang tới QR ≤ 3 bước

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | Báo cáo 'AI nói gì về thương hiệu' (B4 đợt 1) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Trang sản phẩm chiemtinh.vn làm lại trên khuôn | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | OPC kế tiếp (gia phả AI, LAB115) | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF02-landing-opc-ban-qr/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF02-landing-opc-ban-qr\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá trang bán OPC qua QR**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
