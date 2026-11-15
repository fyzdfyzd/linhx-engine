may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\ifagent-wt\A1
phu_thuoc: yl-a0-may2
nhan: may-2 2026-11-15T08:35:19+0700

Phiếu A1 Yên Lam: gộp 2 commit vào nền. Chạy mọi lệnh ở tiền cảnh, không chạy test nền rồi chờ.
1. `git -C C:\linhx\ifagent fetch --all`, rồi `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\A1 -b agy/yl-a1-gop origin/claude/project-thread-qdzzr4` (nền 075e80a5).
2. Trong worktree: `git cherry-pick -x 43921412` (màn chờ AM-03b) rồi `git cherry-pick -x 9f362093` (Lam trả lời ngắn, bộ dò 22 câu). Có xung đột: KHÔNG tự chọn bừa; ghi file xung đột + đoạn diff vào KET-QUA, `git cherry-pick --abort`, dừng.
3. `cd apps/lab && npm ci`, rồi `node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js > ..\..\A1-test.log 2>&1`. Đọc tổng pass/fail. Lỗi được chấp nhận chỉ là lỗi môi trường đã biết (unikon-e2e, unikon-luna, t134 L-03, L-04, C-01; tối đa 7). Lỗi khác thì ghi tên test + 20 dòng log, không sửa test.
4. Commit log test (`A1-test.log`) KHÔNG đưa vào repo; chép vào thư mục phiếu.
5. `git push -u origin agy/yl-a1-gop`. KHÔNG push vào claude/project-thread-qdzzr4 (Claude chấm xong mới gộp).
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test, sửa file ngoài 2 cherry-pick. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md: SHA đỉnh agy/yl-a1-gop, có xung đột không, số test pass/fail/skip, danh sách tên test fail, đánh dấu từng tiêu chí ĐẠT/KHÔNG: (1) không xung đột, (2) test xanh trừ ≤7 lỗi môi trường.
