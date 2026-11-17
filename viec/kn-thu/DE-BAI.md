# Thử kỹ năng agy trên từng máy (17/11)

Mục tiêu: biết chắc máy nào làm được việc gì. Mỗi phiếu thử MỘT kỹ năng, ≤ 25 phút, kết quả là một dòng trong ma trận `viec/kn-thu/MA-TRAN.md` (Claude ghi, agy không sửa).

## Luật chung cho mọi phiếu kn-*
1. BƯỚC 0: `hostname`. Sai máy ghi trong phiếu thì dừng, KET-QUA ghi `SAI_MAY: <hostname>`.
2. Dòng 2 của phần thân KET-QUA luôn là: `KET_LUAN: DAT | HONG | CHUA_DANG_NHAP | KHONG_CO_CONG_CU` + ` — <lý do ≤ 120 ký tự>`.
3. Trình duyệt, thử theo thứ tự, dùng cách đầu tiên chạy được và ghi tên cách vào KET-QUA (`trinh_duyet: browsentic | agy-browser | cdp-9222`):
   a. MCP Browsentic (Chrome đã đăng nhập, cổng 8765) nếu `agy mcp list` có.
   b. Trình duyệt sẵn có của agy.
   c. Chrome hồ sơ RIÊNG: `chrome.exe --user-data-dir=<o>\linhx\chrome-agy --remote-debugging-port=9222` (o = D: nếu có, không thì C:). KHÔNG mở cổng debug trên User Data mặc định (Chrome mới chặn, đã thử 17/11).
4. Trang đòi đăng nhập: KHÔNG gõ mật khẩu, KHÔNG tạo tài khoản. Để nguyên cửa sổ đăng nhập mở, ghi `KET_LUAN: CHUA_DANG_NHAP` và khối `CAN-LINH: đăng nhập <dịch vụ> trên <máy> (cửa sổ <cách 3a/b/c>); LENH: (không)`, rồi dừng.
5. Bằng chứng: ít nhất 1 ảnh màn hình PNG ≤ 1 MB + file kết quả, chép vào `hang-doi/xong/<id>/`. File > 1 MB (video, nhạc) chép vào `<LINHX_DRIVE_DIR>/kn-thu/<id>/`, KET-QUA ghi đường dẫn + dung lượng + sha256.
6. Tab: tối đa 5, đóng tab mình mở, KET-QUA ghi `Tab: đã đóng N/N`. Không ghi email, cookie, token, mật khẩu vào repo hay KET-QUA (email che dạng `ai***@gmail.com`).
7. Không tác vụ nền rồi chờ. Việc chờ lâu (deep research, render) thì kiểm trạng thái mỗi 1–2 phút ở tiền cảnh.
8. Không trả phí, không bấm nâng cấp gói, không đăng/chia sẻ công khai gì.
9. KET-QUA ≤ 2000 ký tự, thêm dòng `phut_that: <số phút>` và `loi_gap: <lỗi lặp lại được nếu có>`.
