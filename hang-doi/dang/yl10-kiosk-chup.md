may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl10-kiosk-chup; D:\linhx\ifagent-wt\yl10-kiosk-chup
nhan: may-3 2026-11-18T07:28:15+0700

Phiếu Yên Lam sửa nhanh `yl10-kiosk-chup`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `D:\linhx\nhat-ky\yl10-kiosk-chup\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào D:\linhx\ifagent). `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl10-kiosk-chup -b agy/yl10-kiosk-chup origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Kiosk: giao diện chụp ảnh đang VỠ. Đi hết nhánh chụp ở 1080×1920: nút "Chụp bìa cùng Lam" → màn đồng ý → 3-2-1 → "Lại gần chút nhé" → chờ bìa chọn 1 trong 4 track → bìa + QR → về chờ. Dùng camera giả của Playwright (`--use-fake-device-for-media-stream`, `--use-fake-ui-for-media-stream`).
Chụp từng màn trước khi sửa, tìm mọi chỗ vỡ (tràn, chồng lớp, lệch tâm, khung camera méo, nút < 44px, chữ mờ), sửa hết, chụp lại. Khung tham chiếu: `viec/yen-lam-v09/khung/` (K3, K3b, K4). Không đổi CSS kính, dùng lại class sẵn có.
Test: Playwright 1 tệp đi hết luồng chụp, kiểm không phần tử nào tràn khỏi màn, nút chính ≥ 44px.
Cuối: commit + push `agy/yl10-kiosk-chup`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 08:07 39p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
