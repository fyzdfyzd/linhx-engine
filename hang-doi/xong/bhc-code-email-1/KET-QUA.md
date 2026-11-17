model: gemini-4-argon-high
phieu: bhc-code-email-1
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/bhc-email/lead-1280.png, bang-chung/bhc-email/lead-360.png, bang-chung/bhc-email/man-lead-1280.png, bang-chung/bhc-email/man-lead-360.png, bang-chung/bhc-email/test-lap.log, bang-chung/bhc-email/thu-360.png, bang-chung/bhc-email/thu-600.png, bang-chung/bhc-email/thu-html-36...
drive: (khong)
phut: 21.77
token: vao=256422 ra=65896

Đã hoàn thành tính năng gửi báo cáo qua email cho khách để lại lead trên nhánh `agy/bhc-quan-tri` (trạng thái cao nhất: `REVIEW`).

### Tóm tắt kết quả
- **SHA đã push (`origin/agy/bhc-quan-tri`)**: `7b793e205524a8e9e9f862148117aff7438ecb85` (`7b793e20`)
- **Module gửi thư**: [thu.js](file:///C:/linhx/ifagent-wt/bhc-quan-tri/apps/brand-health/server/lib/thu.js)
  - Gửi qua Resend HTTP API (`https://api.resend.com/emails`) với khoá `RESEND_API_KEY` và người gửi `BH_THU_TU` (mặc định `"IF Agent <baocao@ifagent.net>"`). Không có khoá thì không gửi và ghi trạng thái `"chưa gửi: chưa cấu hình"` (không lỗi).
  - Hàng đợi gửi riêng bất đồng bộ, thử lại 3 lần với khoảng cách tăng dần (`1000ms`, `3000ms`, `9000ms`), không chặn luồng quét.
  - Mẫu thư HTML tiếng Việt có dấu: tiêu đề `"Báo cáo AI nói gì về <thương hiệu>"`, thân gồm 3 chỉ số (`Có mặt`, `Đúng`, `Đề xuất`), 1 câu chốt trọng tâm, nút mở `/bao-cao/<mã>/`, link tải PDF Light (`/bao-cao/<mã>/tai/light.pdf`), chân thư có hướng dẫn huỷ nhận thư; dựng bằng bảng + inline style theo token màu khung B, rộng `≤ 600px`
...[cat bot]...
/ifagent-wt/bhc-quan-tri/bang-chung/bhc-email/thu-html-600.png), [thu-html-360.png](file:///C:/linhx/ifagent-wt/bhc-quan-tri/bang-chung/bhc-email/thu-html-360.png).
  - Ảnh màn Lead: [lead-1280.png](file:///C:/linhx/ifagent-wt/bhc-quan-tri/bang-chung/bhc-email/lead-1280.png), [lead-360.png](file:///C:/linhx/ifagent-wt/bhc-quan-tri/bang-chung/bhc-email/lead-360.png).
  - Báo cáo kết quả: [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md).
