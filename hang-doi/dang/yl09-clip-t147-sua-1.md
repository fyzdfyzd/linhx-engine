may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-clip-t147; C:\linhx\ifagent-wt\yl09-clip-t147
nhan: may-2 2026-11-18T04:48:53+0700

Phiếu Yên Lam v0.9 `yl09-clip-t147` lượt 2: TIẾP phần dở trên nhánh agy/yl09-clip-t147 (worktree đã có thì vào, commit + push phần chưa commit, làm tiếp, bỏ bước 1). ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI.md` (luật 1–9). Chạy mọi lệnh tiền cảnh, KHÔNG background task, KHÔNG chạy cả bộ test lab (mỗi lệnh test ≤ 8 phút). Ghi tiến độ vào `C:\linhx\nhat-ky\yl09-clip-t147\tien-do.log` mỗi bước. Commit + push sau mỗi ý, phút 35 phải push.
1. `git -C C:\linhx\ifagent fetch --all`; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-clip-t147 -b agy/yl09-clip-t147 origin/agy/yl09-kiosk`; `git merge origin/clip-lam-t147` (14 clip Lam mới ở `assets/t147/`, webm alpha 1080×1920 + mp4 dự phòng Safari).
2. Việc: nối clip t147 vào kiosk một trang theo trạng thái: chào khi có người tới (m-vay-chao), mời chụp (m-moi-chup), lại gần (m-lai-gan), nghe/gật (m-gat-dau), suy nghĩ khi chờ trả lời (m-suy-nghi), bìa hiện ra (m-bat-ngo), chỉ QR ở K4 (m-chi-qr), chỉ widget trái/phải (m-chi-trai, m-chi-phai), lỗi/mất mạng (m-xin-loi); clip cũ t146 giữ cho chờ/nghe/nói/cảm ơn. Linh chốt 18/11: KHÔNG dùng clip đếm ngón (m-dem-321); bước 3-2-1 phát m-moi-chup và SỐ 3-2-1 do giao diện kiosk hiện thật to giữa màn (≥ 400px trên 1080×1920, dùng phông/kính sẵn có). Clip mới đưa vào bộ tải trước asset. Mọi clip bắt đầu/kết thúc ở tư thế chờ: chuyển cảnh không nháy đen.
3. Test mới: mỗi trạng thái phát đúng clip; 3-2-1 hiện số trên giao diện và không gọi m-dem-321; tải trước có đủ clip t147. Duyệt pixel theo DE-BAI luật 7: chụp 1080×1920 các khoảnh khắc mời chụp, số 2 đang đếm, bìa + chỉ QR; ảnh ghép cạnh khung K1/K3/K4 vào `bang-chung/yl09-clip-t147/`.
4. Push `agy/yl09-clip-t147`. CẤM như DE-BAI luật 5. KET-QUA theo luật 9.

nhip: 05:06 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
