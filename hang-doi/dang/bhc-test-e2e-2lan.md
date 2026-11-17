may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-test-e2e
nhan: may-2 2026-11-17T07:40:24+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: chạy kiểm thử đầu-cuối HAI LẦN liên tiếp trên bản nối app, KHÔNG sửa code.
1. Worktree C:\linhx\ifagent-wt\bhc-test-e2e, nhánh agy/bhc-test-e2e từ origin/agy/bhc-code-noi-app (de292e3).
2. Lần 1 và lần 2, mỗi lần: dọn data/ tạm, `npm.cmd run verify`, rồi E2E 4 bước (nhập → xác nhận sự thật → đang quét → kết quả → /bao-cao/<mã>/ → tải PDF HTTP 200 → để lại lead có ô đồng ý → GET /api/leads.csv với mã quản trị thấy đúng 1 dòng). AI giả, không gọi mạng. Thêm ca: 2 khách quét cùng lúc (hàng đợi đúng thứ tự), vượt trần lượt/IP bị chặn có câu báo dễ hiểu, khởi động lại server giữa lần 1 và 2 thì báo cáo lần 1 vẫn mở được.
3. Ghi log thô từng lần vào bang-chung/bhc-test-e2e/lan-1.txt, lan-2.txt; bảng so sánh 2 lần (ca nào lệch kết quả giữa 2 lần = không ổn định, ghi rõ). Ảnh 1280 và 360 của bước kết quả lần 2.
4. Thiếu test cho ca ở bước 2 thì viết test mới (test/e2e-*.test.js), không sửa code sản phẩm. Lỗi thật của sản phẩm: ghi vào KET-QUA, KHÔNG tự sửa.
CẤM: sửa code sản phẩm, deploy, gọi AI thật, in khoá, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; bảng ca × lần 1 × lần 2; lỗi sản phẩm tìm thấy.

nhip: 07:55 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
