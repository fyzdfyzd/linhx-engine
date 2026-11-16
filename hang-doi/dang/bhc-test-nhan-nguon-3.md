may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-code-nhan-nguon
nhan: may-2 2026-11-17T02:24:50+0700
moc: 288a6b4680ad0385c4ffc975209383b9710161c3

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh và chờ xong. Trong PowerShell gọi `npm.cmd`/`npx.cmd`. Push nhánh sau MỖI commit. Server chạy bằng Start-Process, nhớ PID, tắt đúng PID.
Landing báo cáo (nhánh agy/bhc-code-nhan-nguon, đỉnh 288a6b4, git pull trước): nhãn nguồn mới "· Gemini, trả lời từ trí nhớ · câu C1.3" dài hơn nên ở 1280 đẩy nút "Xem nguyên văn" xuống dòng riêng và nhãn nằm lệch cao hơn dòng chữ bên cạnh.
Sửa trong khung landing B (server/lib/landing.js / bao-cao/khung/B/landing-b.js): nhãn nguồn thành một dòng riêng ngay dưới câu "6/6 lần hỏi thẳng…", cỡ chữ nhỏ màu phụ như cũ, bỏ dấu "·" ở đầu; nút "Xem nguyên văn" nằm cùng dòng với nhãn nguồn ở 1280 (bên phải) và xuống dưới ở 360. Không đổi chữ, số, màu khác. Áp cho cả 2 thương hiệu.
Kiểm: npm.cmd run verify xanh. Chụp http://localhost:3020 landing 2 thương hiệu màn đầu 1280×800 và 360×780 Sáng + Vinamilk 1280 Đêm vào bang-chung/bhc-code-nhan-nguon/ (ghi đè, ≤ 600 KB). Commit, push.
CẤM như các phiếu bhc trước (không deploy, không AI thật, không đụng apps/event, apps/lab, packages/).
KET-QUA.md: `dat: co|khong`; SHA; verify; danh sách ảnh.
