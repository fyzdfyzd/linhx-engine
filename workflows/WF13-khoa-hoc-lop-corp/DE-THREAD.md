# WF13 · Course OS: khoá lớp corp

Làn 1 · EDU · Đề sẵn để mở thread. Đọc trước: `/mnt/project-files/WF-CHUAN/KHUNG-CHUAN.md`.

## Đầu ra
Nhận đề lớp DN thành bộ khoá đủ: đề cương, slide, bài tập, phiếu, học liệu, bản theo khách; trợ giảng dạy được

## Có sẵn
- Skill: course, course-architect, lesson-*, Course OS bản 2 (9 module, đã khoá đề 6/11), vong-lap-slide, linhx-chuan
- Hiện trạng: 25 khoá 2024–2026, mỗi lớp soạn gần như từ đầu; Course OS đã khoá đề, chưa chạy trọn một lớp

## Ai làm
Linh: nhu cầu khách, quan điểm chuyên môn, D4 · Claude: khung, chấm · agy: soạn học liệu, slide · 6 trợ giảng: dạy thử, chấm dạy được không

## Máy đo (đạt mới qua)
giờ công Linh ≤ 4 giờ/lớp; slide qua vls.py; trợ giảng dạy được không cần hỏi Linh; điểm học viên ≥ 4,5/5

## Bước 0
Đọc `NGOAI.md` (người ngoài đã làm), đọc code ít nhất 3 cái tốt nhất, ghi lấy gì bỏ gì.

## Ba vòng làm chuẩn
| Vòng | Đề thật | Ai điều phối | Xong khi |
|---|---|---|---|
| 1 | Lớp AI cho chi nhánh ngân hàng (khách corp thật kế tiếp) | Claude điều phối, agy làm thợ | Ra sản phẩm, ghi đủ lỗi vào BAI-HOC.md, sửa skill |
| 2 | Lớp agent cho DN, cuối lớp có cửa vào Agent Force | agy làm theo skill đã sửa, Claude chấm | Linh duyệt D4 không sửa lớn |
| 3 | Một lớp do trợ giảng dạy, agy tự soạn | agy tự chạy (agy-tu-chay), Claude chỉ canh | Đạt máy đo, Linh duyệt D4 không sửa lớn → nạp |

## Chỗ lưu
- Cloud: `/mnt/project-files/WF-CHUAN/WF13-khoa-hoc-lop-corp/` (vang/, vong-1/, vong-2/, vong-3/, BAI-HOC.md)
- Máy cty (file lớn: ảnh, PDF, video): `D:\LINHX\WF-CHUAN\WF13-khoa-hoc-lop-corp\`
- Đạt chuẩn: skill sửa trong `linhx-engine/skills/`, thêm loại phiếu vào `linhx_worker`, trang wiki.

## Thread
Tên: **Chuẩn hoá Course OS lớp corp**. Thread điều tiết: "Chuẩn hoá workflow chất lượng cho LINHX ENGINE".
Báo về thread điều tiết khi: xong bước 0, tới cổng D2/D4, xong mỗi vòng, bị chặn.
