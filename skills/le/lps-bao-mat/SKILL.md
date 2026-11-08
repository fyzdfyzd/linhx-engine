---
name: lps-bao-mat
description: Mô hình hoá mối đe doạ, quét bảo mật tự động và tự pentest một ứng dụng web theo LPS (OWASP ASVS, Top 10, WSTG, LLM Top 10). Dùng khi tính năng chạm đăng nhập, phân quyền, dữ liệu cá nhân, tiền, upload file, LLM; trước phát hành; hoặc khi Linh nói "kiểm bảo mật", "pentest".
---

# Bảo mật và tự pentest

**Chỉ kiểm thử hệ thống của chính Linh, trên máy hoặc staging.** Không quét, không tấn công domain hay dịch vụ của bên khác. Không chạy công cụ tấn công lên production khi Linh chưa đồng ý bằng lời trong phiên.

## Bước 1. Mô hình mối đe doạ (khi viết SPEC)
Cập nhật `docs/security/THREAT-MODEL.md` từ template: tài sản, ranh giới tin cậy, bảng STRIDE, biện pháp kèm test chứng minh. Mức mục tiêu: **ASVS L1** cho mọi dự án T2/T3; **ASVS L2** khi có dữ liệu cá nhân, tiền, hoặc nhiều tenant.

## Bước 2. Quét tự động (đã nằm trong CI; chạy tay khi cần)
| Loại | Lệnh | Ngưỡng |
|---|---|---|
| Bí mật | `gitleaks git --redact` | 0 phát hiện |
| SAST | `semgrep scan --config p/default --config p/typescript --error` | 0 High chưa xử lý |
| Phụ thuộc | `pnpm audit --audit-level high` và `osv-scanner scan -r .` | 0 High/Critical có bản vá |
| Header | ZAP baseline lên staging (`zap-baseline.py -t <url>`) | 0 High |

## Bước 3. Tự pentest thủ công (trích WSTG, làm trên staging với 2 tài khoản A, B và 1 tenant khác)
- [ ] **Phân quyền ngang (IDOR):** đăng nhập A, gọi mọi endpoint có id của B. Mong đợi 403/404. Viết test tự động cho từng endpoint tìm được.
- [ ] **Phân quyền dọc:** tài khoản thường gọi endpoint admin.
- [ ] **Xác thực:** khoá/giới hạn sau nhiều lần sai; đổi mật khẩu huỷ phiên cũ; cookie `HttpOnly; Secure; SameSite`; JWT không chấp nhận `alg: none`, có hạn.
- [ ] **Đầu vào:** chuỗi `' OR 1=1--`, `<img src=x onerror=alert(1)>`, `../../etc/passwd`, số âm, số rất lớn, Unicode lạ ở mọi ô và query string. Kiểm không có lỗi 500 lộ stack trace.
- [ ] **Upload:** đổi đuôi file, file > giới hạn, SVG có script; file lưu ngoài thư mục web, tên ngẫu nhiên.
- [ ] **SSRF:** ô nhận URL có gọi được `http://169.254.169.254/` hoặc `localhost` không.
- [ ] **CSRF/CORS:** CORS không `*` khi có cookie; thao tác đổi trạng thái cần token hoặc SameSite.
- [ ] **Giới hạn tần suất** trên đăng nhập, OTP, gửi tin, endpoint gọi LLM tốn tiền.
- [ ] **LLM** (nếu có): prompt injection trực tiếp và gián tiếp (qua tài liệu/web được nạp), bot có lộ system prompt, dữ liệu người khác, hoặc gọi tool vượt quyền? Đầu ra LLM được escape trước khi hiển thị? Có giới hạn chi phí?
- [ ] **Dữ liệu cá nhân:** log, thông báo lỗi, analytics không chứa SĐT, CCCD, email; có chức năng xoá dữ liệu theo yêu cầu.

## Bước 4. Báo cáo
Ghi `docs/security/PENTEST-YYYYMMDD.md`: phạm vi, phiên bản, mục đã kiểm, phát hiện (mức Critical/High/Medium/Low, cách tái hiện, cách sửa), trạng thái. Phát hiện High trở lên chặn phát hành. Mỗi lỗ hổng sửa xong phải có test hồi quy.

## Khi nào cần pentest bên ngoài
T3 có thanh toán, dữ liệu cá nhân nhạy cảm, hoặc trên ~10.000 người dùng: thuê đơn vị pentest độc lập trước phát hành lớn và mỗi năm một lần.
