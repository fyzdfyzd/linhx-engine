may: may-2
loai: code
tran_phut: 40
nhan: may-2 2026-11-14T22:45:31+0700

Dựng landing Listening Vietnam.
1. Repo: `C:\linhx\wt-lvn` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-lvn`; có rồi: `git pull`).
2. Đọc `viec/lvn-landing/DE-BAI.md`, `brand/brand.json`, `brand/LUAT-ONBRAND.md`, `tham-khao/GHI-CHU.md` và 3 ảnh mẫu.
3. Được dùng orchestration (chia việc con: nội dung tiếng Việt, giao diện, form), nhưng gom lại một commit.
4. Viết `viec/lvn-landing/index.html` (+ css/js nếu cần) đúng đề.
5. Kiểm: `pip install pytest playwright` và `python -m playwright install chromium` nếu chưa có, rồi `python -m pytest viec/lvn-landing/nghiem-thu -q` phải đạt 5/5. Sửa trang cho tới khi đạt.
6. TUYỆT ĐỐI không sửa `viec/lvn-landing/nghiem-thu/` (đã khoá sha256). Không đụng file ngoài `viec/lvn-landing/`.
7. Commit, push lên `claude/project-thread-jowxv1`.
Trả lời: số test đạt, dung lượng trang (KB), hash commit, 3 dòng mô tả bố cục.
