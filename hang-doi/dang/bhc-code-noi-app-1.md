may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-noi-app
nhan: may-2 2026-11-17T05:12:22+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: nối khung B-trang-chu vào app (thay trang chủ nền tối cũ).
1. `git -C C:\linhx\ifagent fetch origin agy/bhc-code-nhan-nguon agy/bhc-code-khung-trang-chu`; worktree C:\linhx\ifagent-wt\bhc-code-noi-app, nhánh mới agy/bhc-code-noi-app từ origin/agy/bhc-code-nhan-nguon; `git merge --no-edit origin/agy/bhc-code-khung-trang-chu` (xung đột chỉ ở bang-chung/ thì giữ cả hai).
2. Thay public/ (trang chủ) bằng giao diện màn a của B-trang-chu, giữ nguyên API hiện có (form gửi như cũ, hàng đợi, polling, lead). Màn b (bảng sự thật) = bước xác nhận trước khi quét; màn c = trạng thái đang quét đọc từ API polling thật (số câu, thứ tự hàng đợi); màn d = kết quả, nút "Xem báo cáo đầy đủ" dẫn tới /bao-cao/<mã>/ nếu có, ô lead dùng API lead cũ (bắt buộc ô đồng ý). Giữ màn sân khấu ?stage=1 như cũ.
3. Không đổi chữ, màu, bố cục so với khung; chỉ thay số mẫu bằng số thật từ API. Trong test/E2E dùng AI giả (không gọi Gemini thật).
4. Test: E2E node --test + Playwright trên http://localhost:3020 với AI giả: nhập → xác nhận sự thật → đang quét → kết quả → mở /bao-cao/<mã>/; các luật khoá cũ của B-trang-chu (lề 360, lưới 1280, input trống, cấm tên mô hình chưa chạy) chạy lại trên trang thật. npm.cmd run verify xanh, không giảm số pass.
5. Bằng chứng bang-chung/bhc-code-noi-app/: 4 bước × 1280 và 360 trên app thật, video Playwright 1 lượt (ngoài git, chép G:\My Drive\brand-health\bhc-code-noi-app\ nếu có G:).
CẤM: deploy, gọi AI thật/khoá API, in khoá, gửi mail, sửa test cũ, sửa JSON bao-cao/bien-tap, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW. Hết giờ thì push phần đã xong và ghi rõ còn thiếu gì.
KET-QUA.md: `dat: co|khong`; SHA; E2E pass/fail; verify; phần còn thiếu.

nhip: 05:33 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
