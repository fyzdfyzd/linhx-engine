may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl13-dt-ux-sua-1; D:\linhx\ifagent-wt\yl13-dt-ux
nhan: may-3 2026-11-18T16:47:17+0700

Phiếu `yl13-dt-ux-sua-1` (LƯỢT 2: lượt 1 dừng vì agy hết hạn mức sau 3 phút; nếu worktree/nhánh đã có thì dùng lại, bỏ qua bước 0): sửa trải nghiệm điện thoại `/yen-lam/#lam` (390×844 @2x) sau khi Linh duyệt lúc 15:52 18/11. ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
0. `git -C D:\linhx\ifagent fetch --all`; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl13-dt-ux -b agy/yl13-dt-ux origin/agy/yl12-email-vao`. Nhánh nền đã có cổng email. Nối node_modules như phiếu yl10.
Chạy mọi lệnh ở tiền cảnh. Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới, chụp ảnh, push, ghi CON_LAI.
VIỆC:
1. Gộp bước vào: KHÔNG để Lam hỏi tên rồi cổng lại hỏi email. Lần tương tác đầu chỉ có một tấm: email (bắt buộc) + tên (không bắt buộc) + ô đồng ý. Lời chào đầu của Lam bỏ câu "Mình gọi bạn là gì nhỉ?" và gọi khách theo tên nếu đã có. Ô nhập chat đổi placeholder thành "Hỏi Lam về lịch, diễn giả, chỗ ngồi…".
2. Tải đầu nhanh: màn khung xám hiện nay mất 4–5 giây. Mục tiêu: lời chào và ô nhập hiện trong ≤ 1,5 giây trên 4G giả lập (Playwright throttle ~1,6 Mbps, RTT 150 ms). Cách làm: render ngay lời chào tĩnh và ô nhập từ HTML, tải phần khác sau; hoãn ảnh và JS không cần cho màn đầu; nén ảnh Lam đầu trang (WebP, ≤ 80 KB). Đo trước/sau bằng số ms, ghi vào KET-QUA.
3. Nút gửi chat dùng màu xanh chính sẵn có, không dùng cam đỏ.
Ảnh trước/sau 390×844 @2x: màn đầu ở giây thứ 1, tấm email, chat sau 1 câu. Tự soi 100%, chấm ≥ 8.
Test Playwright 1 tệp yl13-dt-ux: tin đầu không chứa "gọi bạn là gì"; chỉ hiện một tấm email; ô nhập hiện trong ≤ 1500 ms ở throttle; nút gửi không phải màu cam đỏ.
Cuối: push `agy/yl13-dt-ux`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 17:11 24p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
