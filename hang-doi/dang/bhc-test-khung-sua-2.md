may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-code-khung-trang-chu
nhan: may-2 2026-11-17T03:37:22+0700
moc: 41d7c19dd6eace20d0b979576d165eb038fbaa3d

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Khung B-trang-chu (nhánh agy/bhc-code-khung-trang-chu, đỉnh 41d7c19, git pull trước). Chấm Claude 8/10, còn 2 lỗi nội dung:
1. Luồng mẫu không nhất quán: màn b, c quét "Sữa Mộc Châu" nhưng màn d hiện kết quả Vinamilk. Đổi ví dụ của màn b, c, d thành MỘT thương hiệu: Vinamilk, dùng đúng số thật trong apps/brand-health/bao-cao/bien-tap/2026-11-13-vinamilk-9b816db5.json (không bịa số; sự thật màn b lấy từ bảng sự thật trong JSON). Ô nhập màn a giữ placeholder "VD: …".
2. Màn c đang liệt kê ChatGPT, Claude & Perplexity "0/24, lượt dự phòng". Giai đoạn này chỉ đo bằng Gemini (trí nhớ + có tìm web). Bỏ các dòng mô hình khác, chỉ còn 2 dòng Gemini; không nhắc mô hình chưa chạy.
3. Luật khoá: thêm test: (a) 4 màn chỉ nhắc một tên thương hiệu mẫu ngoài 2 thẻ báo cáo mẫu ở màn a (không còn "Mộc Châu"); (b) mọi số trong màn d có trong JSON Vinamilk; (c) không có chữ ChatGPT|Claude|Perplexity|OpenAI trong 4 màn. Đỏ trên 41d7c19, xanh sau sửa.
4. npm.cmd run verify xanh. Ghi đè bằng chứng như phiếu khung-sua-1 (ghep-1280.png, ghep-360.png, từng màn).
CẤM: sửa server/, đổi bố cục/màu, sinh ảnh AI, deploy, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; test mới đỏ→xanh; verify pass/fail.

nhip: 03:52 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
