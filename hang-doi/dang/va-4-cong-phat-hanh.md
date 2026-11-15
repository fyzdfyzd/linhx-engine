may: may-4
loai: code
tran_phut: 40
theo_doi: D:\linhx\wt-va4
khong_tien_phut: 25
tu_sua: 1
nhan: may-4 2026-11-15T09:20:44+0700

KHÔNG chạy lệnh nền hay subagent nền: mọi lệnh tiền cảnh, làm tuần tự.
Repo: `D:\linhx\wt-va4` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine D:\linhx\wt-va4`; có rồi: `git pull`). KHÔNG sửa C:\linhx\hang-doi. Đọc trước `viec/ra-quy-trinh/SO-SANH.md` (khâu liên quan).

Vá 4, cổng phát hành (chỉ khuôn và script kiểm, KHÔNG deploy thật): `runner/cong_phat_hanh.py --base <url staging> --sha <sha>`: GET /healthz phải trả đúng BUILD_SHA; chặn nếu base trùng tên miền prod trong danh sách `--prod`; chặn nếu giờ VN > 22h hoặc < 7h; chỉ dùng GET. Thêm vào SKILL.md mục "Phát hành": phiếu deploy chỉ staging, chạy cổng này trước và sau, ghi lệnh rollback; prod luôn là CAN-LINH (Linh duyệt và chạy). Học từ AGENTS.md mục "Luật deploy" của repo ifagent (MSI đã có repo ở D:\LINHX\PRJ\IFAGENT, chỉ đọc, KHÔNG git pull hay sửa gì ở đó). Test giả lập HTTP cục bộ.
Test trong runner/ (không conftest, không mạng). `python -m pytest runner -q` đạt hết trừ test đường dẫn chỉ Windows. Cập nhật `skills/le/hang-doi-may/SKILL.md` (mục Phiếu hoặc Bài học, ngắn). `git pull --rebase`, push nhánh. Trả lời ≤1200 ký tự: làm gì, số test, hash.

nhip: 09:23 3p warning: --mode auto is not available for this account; continuing in the default mode.
