# Bàn giao: Kiến trúc LINHX ENGINE trên Frappe
Thread gốc: "Thiết kế kiến trúc LINHX ENGINE" (LINHX LAB) · Ngày đóng: 2026-11-05 · Người nhận: thread "chuyển nền tảng" hoặc agy

## 1. Mục tiêu
Thay khuôn OPC bằng LINHX ENGINE: một nền cắm module dùng cho landing, sản phẩm số, dịch vụ, B2B tới nền tảng; launch nhanh nhất mà vẫn nhận cập nhật lõi.

## 2. Đã xong
- Rà code 7 repo (Frappe, Payload, Medusa, ruoyi-vue-pro, PocketBase, Frappe Helpdesk/LMS) → 01-NGHIEN-CUU-NEN.md (có mục đa kênh, content hub, thiết bị, social)
- Ước lượng ý tưởng → golive và rebuild CTS → 02-Y-TUONG-DEN-GOLIVE.md
- 4 mô hình đặt Frappe, Frappe gọi agy, MCP → 03-MO-HINH-VA-AGY.md
- Bản chốt: 3 tầng, so sánh 7 ứng viên, giao diện/SEO, tổ chức repo, 8 đợt, mẫu liệt kê dự án → 04-CHOT-KIEN-TRUC.md
- Phiếu thử Frappe K1 (5 ca test, ca tải k6, đa kênh) → PHIEU-THU-FRAPPE-K1.md; bản trên máy cty D:\LINHX\LAB\LAB111-LINHX-ENGINE\thu-frappe\PHIEU.md
- Bản tự viết lõi cũ (chỉ tham khảo): KIEN-TRUC-LINHX-ENGINE.md, Claude Doc https://claude.ai/artifact/S6fTwDeW2CdADurH3tcZpm

## 3. Đang dở
- Phiếu thử Frappe CHƯA chạy: máy cty không có Docker/WSL, tài khoản ADMIN không có quyền quản trị. Hướng mới: chạy trên VPS staging (chờ Linh cấp).
- Chưa kiểm: agy CLI chạy headless trên Linux, đăng nhập Ultra trên server, điều khoản Google.

## 4. Quyết định đã chốt
- Dùng Frappe làm nền (Linh, 5/11 10:56). Lý do: quản trị/duyệt sẵn, dịch vụ/B2B, đội ngoài lo cập nhật lõi, cùng Python, MIT.
- Ba tầng: điều hành (site ops) / thợ / sản phẩm (app Frappe + mặt tiền Next.js). Không sửa lõi Frappe. Nghiệp vụ chỉ ở Frappe. Frappe không gửi lệnh shell cho máy.
- CTS đang có khách: giữ FastAPI, chuyển dần sau; không dừng bản cũ.
- Đăng bài đa kênh qua Postiz; thiết bị qua REST/webhook, MQTT cần cầu nối.

## 5. Việc tiếp theo
1. Linh liệt kê dự án theo mẫu mục 5 file 04 → gom bản đồ module dùng chung, thứ tự làm.
2. VPS staging 4–8 vCPU, 8–16 GB → chạy PHIEU-THU-FRAPPE-K1 + thử agy trên Linux · xong khi test xanh, không sửa lõi, bench update êm.
3. Đợt 2: linhx_ops + linhx-tho (giao phiếu agy từ Frappe, chạy 1 phiếu thật).
4. Đợt 3: linhx_vn (SePay, VietQR, Zalo) + linhx_quyen.

## 6. File quan trọng
- /mnt/project-files/LAB111-LINHX-ENGINE/04-CHOT-KIEN-TRUC.md (bản chính)
- 01, 02, 03, PHIEU-THU-FRAPPE-K1.md cùng thư mục
- Bản sao chốt trên máy cty: D:\LINHX\LAB\LAB111-LINHX-ENGINE\KIEN-TRUC-CHOT.md

## 7. Lưu ý
- Cần Linh quyết: hạn mở mã AGPL calc-service 20/11 (khuyên mở đúng hạn).
- Frappe Helpdesk, LMS là AGPL; kiểm giấy phép Builder trước khi dùng.
- Remote Control máy cty: dùng env D:\linhx chữ thường; D:\LINHX chữ hoa bị từ chối.
- Ước lượng theo phiếu ≤40 phút, không theo ngày/tuần.

## 8. Câu lệnh mở đầu
> Đọc `.handoff/HANDOFF-linhx-engine-kien-truc-2026-11-05.md` và 04-CHOT-KIEN-TRUC.md. Làm việc số 2 ở mục 5 khi có VPS, ghi kết quả vào cuối file dưới "## Nhật ký tiếp nhận".
