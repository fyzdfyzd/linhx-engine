# WF20 · Agent Force: workforce trong nhóm Zalo

Làn 1 · Agent Force · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Một đội agent + bộ skill riêng cho một tổ chức, sống trong nhóm Zalo của đội: nhân viên tag để giao việc, hỏi đáp, nhận file; có phân quyền, nhật ký, đếm việc xong

## Có sẵn
- Skill: Trợ lý Zalo LAB083 (nick phụ qua zalo-mcp vào được nhóm Zalo thường; OA chỉ 1-1, nhóm GMF phải mua riêng; phân quyền theo uid, claude -p), Agent Shell h10, linhx_worker, kho skill linhx-engine, sổ đếm việc LAB116, proposal-studio, brand-ifagent
- Hiện trạng: Trợ lý Zalo 'Nụ' chạy thật máy cty 31/10 cho Linh; chưa có workforce theo vai cho một đơn vị

## Ai làm
Linh: chọn bên + 5 việc đầu · Claude: bản đồ việc, vai agent, bộ 50 câu thử thật · agy: dựng skill, nối Zalo · người của bên đó (CEO ifAgent): dùng thử 7 ngày

## Máy đo (đạt mới qua)
đúng ≥ 90% trên bộ 50 câu thật, 0 bịa số/giá; chỉ trả lời khi được tag, người ngoài nhóm không lọt quyền; nick phụ không bị khoá sau 7 ngày; trả lời ≤ 2 phút; việc xong/tuần đếm được; người dùng thử chấm ≥ 4/5

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | Workforce nội bộ ifAgent: trả lời lead, tra hồ sơ năng lực, soạn proposal event, báo cáo sau sự kiện | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Workforce một BU khác (Unikon nhận brief agency, hoặc Sakedemy CSKH học viên) | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | DN khách pilot 14 ngày đầu tiên | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF20-workforce-zalo-cho-mot-ben/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF20-workforce-zalo-cho-mot-ben\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Dựng workforce cho nhóm Zalo**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
