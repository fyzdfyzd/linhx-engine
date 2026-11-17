may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 20
tu_sua: 1
phu_thuoc: ev-hieu-nang-14
theo_doi: D:\linhx\linhx-engine-wt\runner-moc

Phiếu lx-runner-moc-15: sửa runner báo nhầm bí mật khi phiếu tạo worktree mới. KHÔNG merge vào main, chỉ đẩy nhánh để Claude duyệt.
Lỗi: runner/rao_phieu.py inspect_new_commits. Khi `theo_doi` chưa tồn tại lúc nhận phiếu, base_sha rỗng → infer_initial_base_when_cloned_in_agy chỉ nhận reflog "clone:"; với `git worktree add ... -b <nhánh> <điểm>` reflog đầu là "branch: Created from ..." (hoặc "reset: moving to") nên rơi về cây rỗng → quét cả repo → báo nhầm dòng cũ (ví dụ apps/lab/..., apps/event/test/e2e/platform.test.js:38) → mọi phiếu ev-* ra "loi" rồi tự sinh -sua-1.
0. `git clone https://github.com/fyzdfyzd/linhx-engine D:\linhx\linhx-engine-wt\runner-moc`, `git checkout -b agy/runner-moc-worktree origin/main`.
1. Sửa infer_initial_base_when_cloned_in_agy: lấy SHA của mục reflog CŨ NHẤT của HEAD bất kể chủ đề (clone:, branch: Created from, reset: moving to, checkout:), chỉ rơi về cây rỗng khi không có reflog. Giữ nguyên mọi hành vi khác.
2. Thêm test pytest (cùng chỗ các test runner hiện có): repo tạm có 1 commit chứa chuỗi giống khoá ở tệp cũ; tạo worktree `-b` từ commit đó; thêm 1 commit sạch; inspect_new_commits với base_sha "" phải trả bi_mat rỗng. Và ca ngược: commit mới có chuỗi giống khoá thì vẫn bắt được. Chạy toàn bộ test runner.
3. Push agy/runner-moc-worktree. KET-QUA ngắn: SHA, số dòng đổi, test pass/fail. Không in khoá, không sửa phiếu/hang-doi, không đụng runner đang chạy trên máy.
