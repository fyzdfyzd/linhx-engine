may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl14-bia-kiosk; D:\linhx\ifagent-wt\yl14-bia-kiosk
nhan: may-3 2026-11-18T17:40:16+0700

Phiếu `yl14-bia-kiosk`: GẤP, sự kiện diễn ra sáng 19/11. Đội test thật tại Ascott chiều 18/11 báo luồng bìa ở kiosk lỗi. ĐỌC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
0. `git -C D:\linhx\ifagent fetch --all`; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl14-bia-kiosk -b agy/yl14-bia-kiosk origin/agy/yl10-gop` (lấy đỉnh mới nhất). Nối node_modules như phiếu yl10.
Chạy mọi lệnh ở tiền cảnh. Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới, push, ghi CON_LAI.
VIỆC:
1. Kẹt ở bước chọn track: sau câu "Mình đã chọn mảng Toàn thể cho bìa", cả 4 thẻ track (Toàn thể/Grand Ballroom, Olive/Hồ Tây 2, Lavender/Trúc Bạch, Iris/Hồ Tây 1) đều ghi "0 phiên". Thanh dưới hiện "Bìa 20%", sau đó không chạm chọn được nữa. Tìm gốc: dữ liệu track/phiên không nối, API lỗi, hay trạng thái bị kẹt. Sửa để số phiên đúng theo agenda.json, chạm thẻ chọn được, bìa chạy tới 100%; nếu lỗi thì báo rõ và có nút Thử lại. Không được treo.
2. Bìa kết quả trên kiosk (màn "Quét để nhận bìa") đang KHÁC template tạp chí AGENTIC ME trên điện thoại. Bản điện thoại có khung chữ AGENTIC ME, logo VSMCamp/CSMO, các mục THE IDEA I CHOSE / PEOPLE WHO INSPIRED ME / MY NEXT MOVE; bản kiosk chỉ có ảnh và chữ AGENTIC ME đơn giản. Kiosk phải dùng ĐÚNG template của điện thoại, chung một nguồn template, không làm 2 bản.
3. Chọn diễn giả trên kiosk và điện thoại đang tắc, khựng. Đo thời gian từ chạm tới phản hồi, mục tiêu ≤ 150 ms. Ảnh diễn giả tải lười, dùng bản nhỏ (srcset), không tải lại cả danh sách sau mỗi lần chạm.
Test Playwright 1 tệp yl14-bia-kiosk (AI mock):
- 4 track có số phiên > 0;
- luồng bìa từ chọn track tới bìa xong không treo quá 20 giây (mock);
- bìa kiosk có đủ chữ khung template;
- chạm chọn diễn giả phản hồi ≤ 150 ms.
Ảnh trước/sau 1080×1920: màn chọn track, bìa kết quả. Cuối: push `agy/yl14-bia-kiosk`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 18:07 27p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
