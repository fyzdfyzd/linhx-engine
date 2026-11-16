may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-nhan-nguon
nhan: may-2 2026-11-17T01:13:50+0700
moc: b176dcee17fa507bcdca081d69cb20178d84365b

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh và chờ xong. Trong PowerShell gọi `npm.cmd`/`npx.cmd`. Push nhánh sau MỖI commit. Nếu C:\linhx\ifagent-wt\bhc-code-nhan-nguon đã có thì dùng lại, nhánh agy/bhc-code-nhan-nguon.
Brand health check, phần 1/2: bỏ mã nguồn thô khỏi chữ người xem đọc.
1. Chưa có worktree thì: `git -C C:\linhx\ifagent fetch origin claude/project-thread-apl8gd`, `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\bhc-code-nhan-nguon -b agy/bhc-code-nhan-nguon origin/claude/project-thread-apl8gd`. Có rồi thì `git status`, giữ phần đã làm nếu đúng.
2. Tạo apps/brand-health/server/lib/nhan-nguon.js export `nhanNguon(ma)`: "gemini-nho/D2.2" → "Gemini, trả lời từ trí nhớ · câu D2.2"; "gemini-tim/C1.3" → "Gemini, có tìm trên web · câu C1.3"; nhiều id "gemini-nho/D2.1, D2.2" → "… · câu D2.1, D2.2". Thêm test đơn vị trong test/nhan-nguon.test.js.
3. Thay mọi chỗ in mã thô: `grep -rn "gemini-nho\|gemini-tim" apps/brand-health/bao-cao/khung apps/brand-health/server/lib apps/brand-health/public`. Chỉ đổi phần chữ nhãn nguồn, không đổi số, bố cục, chữ khác. Kiểm lại grep: chỉ còn trong nhan-nguon.js và test.
4. `npm.cmd run verify` trong apps/brand-health xanh (≥ 51 pass, 0 fail). Commit "bhc: nhanNguon", push.
CẤM: deploy, gọi AI thật, in khoá, gửi mail, sửa test cũ, sửa JSON bao-cao/bien-tap, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; verify pass/fail; kết quả grep bước 3.
