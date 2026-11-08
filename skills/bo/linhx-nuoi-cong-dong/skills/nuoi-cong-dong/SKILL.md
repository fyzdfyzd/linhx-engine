---
name: nuoi-cong-dong
description: Chạy vòng nuôi cộng đồng hằng tuần (chấm thành viên, việc SOP người mới, đề xuất, sức khoẻ) cho cộng đồng học viên LINHX hoặc cộng đồng khác. Dùng khi Linh nói "nuôi cộng đồng", "bản tin cộng đồng tuần này", "CLB học viên tuần này làm gì", hoặc khi không rõ dùng skill nào của plugin này.
---

# Nuôi cộng đồng (điều phối)

Thư mục cộng đồng (biến `NUOI_HOME`, mặc định thư mục đang mở). Hồ sơ đầu tiên: `D:\LINHX\LAB\LAB041-CONG-DONG-BAN-HANG\cong-dong\hoc-vien-linhx`. Cấu hình ở `config/cong-dong.json` (trọng số, cấp, SOP, nhịp, thang offer); sửa số ở đó, không sửa script.

## Mỗi tuần (sáng thứ Hai)
1. Có dữ liệu mới thì nhập trước (skill `nhap-du-lieu`): `python "${CLAUDE_PLUGIN_ROOT}/scripts/nuoi.py" nhap su-kien nhap/<file>.csv` (thanh-vien, don tương tự).
2. `python "${CLAUDE_PLUGIN_ROOT}/scripts/nuoi.py" tuan` → `output/BAO-CAO-TUAN.md`, `DE-XUAT-TUAN.csv`, `NHAC-VIEC-TUAN.csv`, `NHAC-VIEC-TUAN.ics` (kéo vào Google Calendar).
3. Với 5–10 đề xuất đầu: dùng skill `de-xuat-tuan` để soạn tin nháp. Với câu hỏi 14 ngày: skill `cau-hoi-thanh-noi-dung`.
4. Báo Linh 5 dòng: 1 số sức khoẻ đáng chú ý, ai có tín hiệu mua, ai nên mời làm AI Champion, việc SOP theo lớp, đề bài nội dung tuần sau. Đính kèm BAO-CAO-TUAN.md.
5. Linh làm xong thì ghi lại: `nuoi.py danh-dau <id> da-lam|bo|tu-choi`, `nuoi.py xong-sop <lớp> <mốc>`.

## Luật (bắt buộc)
- Agent soạn, người gửi. Không tự nhắn, đăng, kết bạn, gửi email. Hook `cong_gui_ra` sẽ hỏi duyệt mọi công cụ gửi ra ngoài.
- Không nhắn riêng người có `dong_y_lien_he=0`; chỉ tương tác trong nhóm.
- Không bot trên tài khoản Zalo cá nhân, không farm tài khoản, không tài khoản mồi, không giả làm người. Xem `references/ranh-gioi.md`.
- Dữ liệu học viên là dữ liệu cá nhân (Luật BVDLCN 91/2025): chỉ để trên máy Linh, không dán lên web công cụ khác.
