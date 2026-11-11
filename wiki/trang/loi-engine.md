---
tieu_de: Lõi LINHX ENGINE
loai: loi
trang_thai: dang-chay
cap_nhat: 2026-11-08
nguon: [nguon/2026-11-05-CHOT-KIEN-TRUC.md, nguon/2026-11-05-BAN-GIAO-LINHX-ENGINE-KIEN-TRUC.md, nguon/2026-11-08-BAN-DO-CTS-K6.md, nguon/2026-11-08-HOC-HOI-K5.md, https://claude.ai/artifact/QaCuXJbnuTuxgQSmCSyom9]
---
# Lõi LINHX ENGINE

**Một câu:** Frappe Framework (MIT, Python) làm lõi, app riêng `linhx_*` cắm vào; bản 0.1 đã chạy thật 6/11, đợt 1 (26 feature) đã khoá và đang giao thợ từ 8/11.

## Hiện trạng
- **0.1 (6/11):** app `linhx_worker` (LX Worker, LX Workflow, LX Job, hàng việc SKIP LOCKED), mặt tiền `front/`, thợ `runner/`, deploy Docker. Chạy ở VM `linhx-engine-1` (GCP project linhx-engine, asia-southeast1-b), mặt tiền http://35.198.251.2, bảng `/#/engine`. Báo cáo thật đầu: "AI nói gì về thương hiệu" cho VSMCamp.
- **Đợt 1 (8/11):** `features-dot1.json` 26 feature N1–N6, A1–A5, B1–B5, C1–C3, D1–D3, E1–E2, T1–T2, khoá bằng `features-dot1.json.khoa`, 34 test ở `tests/nghiem-thu/`. Hai thợ agy ENGINE-t1/t2 trên máy cty, điều khiển bằng `canh/dieu-khien.json`. N2, A1, B1 chờ thư mục PROTO (đang ở MSI). Nháp mở rộng: `features-dot1b.json`.
- **Chiêm Tinh Số chuyển sang:** 3 lớp, lớp tiền/đơn trước, động cơ chiêm tinh giữ máy riêng gọi API ([[du-an-chiem-tinh-so]]).

## Luật kiến trúc
1. Không sửa lõi Frappe; đổi hành vi bằng hook trong app của mình.
2. Giá, đơn, quyền dùng chỉ ở Frappe; mặt tiền và kênh không chứa nghiệp vụ.
3. Server không gửi lệnh shell cho máy; chỉ gửi đề + loại phiếu trong danh sách cho phép, thợ kéo việc.
4. Tên: app `linhx_<việc>`, repo `linhx-<việc>`, sản phẩm `site-<tên>` (đề xuất 5/11, chờ Linh OK).

## Ở đâu
- Code: repo `fyzdfyzd/linhx-engine` (main). Bản thợ đang chạy đợt 1: repo `fyzdfyzd/chiemtinhso` nhánh `claude/project-thread-imkbnt` thư mục `linhx-engine/`, máy cty `D:\LINHX\LINHX-OPC\CHIEMTINHSO-engine`, worktree thợ `D:\LINHX\LINHX-OPC\ENGINE-t<N>`.
- Bí mật VM: `/root/linhx-bi-mat.env` trên VM. Mật khẩu bảng: file ở máy cty (xem [[he-may-va-tai-khoan]]).
- Thiết kế cũ tự viết lõi (KIEN-TRUC-LINHX-ENGINE.md, doc S6fTwDeW2…) chỉ còn để tham khảo.

## Bài học agy (0.1)
Mỗi trang AI một lượt (~3–8 phút, trần 12); đề > 6.000 ký tự đưa qua file; đề phải cấm shell; "có nhắc tên" do code đo, không để AI gán.

## Liên quan
[[tong-quan]] [[he-du-an-tu-chay]] [[danh-muc-de-bai]] [[du-an-chiem-tinh-so]]
