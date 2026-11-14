may: may-1
loai: code
tran_phut: 30

Sửa runner hàng đợi trong repo fyzdfyzd/linhx-engine, nhánh `claude/project-thread-jowxv1`.
Làm trong worktree riêng `D:\linhx\wt-ba-may` (có sẵn thì `git fetch` + `git checkout claude/project-thread-jowxv1` + `git pull`; chưa có thì `git worktree add` từ D:\LINHX\LINHX-ENGINE). KHÔNG sửa D:\linhx\hang-doi (runner đang chạy) và thư mục làm việc chính của D:\LINHX\LINHX-ENGINE.

Việc: thêm công tắc `LINHX_NHAN_BAT_KY` (mặc định 1). Đặt 0 thì máy CHỈ nhận phiếu có `may:` đúng tên máy, bỏ qua phiếu `bat-ky`.
- runner/hang_doi_git.py: chỗ chọn phiếu (gần dòng 504 và 550).
- runner/cai-may.ps1 và runner/cai_may.py: thêm cờ `-ChiDichDanh` (ps1) / tham số tương ứng (py) ghi `LINHX_NHAN_BAT_KY=0` vào tho.env.
- Test mới trong runner/ (không dùng conftest.py): máy có công tắc 0 bỏ qua phiếu bat-ky, vẫn nhận phiếu đích danh.
- Chạy `python -m pytest runner -q`, tất cả phải đạt (trừ nếu có test đường dẫn chỉ đạt trên Windows thì vẫn phải đạt ở đây).
- Commit một lần, push lên `claude/project-thread-jowxv1`.

Trả lời: số test đạt, hash commit, file đã đổi.
