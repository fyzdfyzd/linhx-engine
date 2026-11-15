may: may-2
loai: khac
tran_phut: 30
theo_doi: C:\linhx\ifagent
nhan: may-2 2026-11-15T08:26:30+0700

Dựng chỗ làm Yên Lam trên máy 2 (repo private fyzdfyzd/ifagent, 2,9 GB). Chạy mọi lệnh ở tiền cảnh, không chạy lệnh nền.
1. Ghi phiên bản: `git --version`, `node -v`, `npm -v`, `npx playwright --version`, `gcloud --version` (thiếu cái nào thì ghi THIEU, không tự cài gcloud).
2. Thiếu node (cần ≥ 20) thì cài bằng `winget install OpenJS.NodeJS.LTS`.
3. Clone nền một lần: `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent` (có rồi thì `git fetch --all`). Hỏi đăng nhập thì dừng, ghi CAN_LINH_DANG_NHAP.
4. `git -C C:\linhx\ifagent checkout claude/project-thread-qdzzr4` và ghi `git rev-parse HEAD` (phải là 075e80a5...).
5. Kiểm có đủ: commit 43921412, 9f362093, nhánh claude/kiem-thu-rc1, claude/project-thread-4abpu3 (`git cat-file -t <sha>`).
6. `cd apps/lab && npm ci` (hoặc `npm install` nếu không có lockfile), rồi `npx playwright install chromium`.
CẤM: không sửa file trong repo, không push, không in khoá/mật khẩu, không đụng thư mục ngoài C:\linhx\ifagent.
Trả lời KET-QUA.md: bảng công cụ/phiên bản, SHA HEAD, 4 dòng có/không, dung lượng trống ổ C:.
