may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl13-kiosk-ux; D:\linhx\ifagent-wt\yl13-kiosk-ux
nhan: may-3 2026-11-18T16:12:19+0700

Phiếu `yl13-kiosk-ux`: sửa trải nghiệm kiosk `/yen-lam/csmo/kiosk-lam` (1080×1920) sau khi Linh duyệt lúc 15:52 18/11. ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` (luật chung, chống chuyển nền, CẤM). Ảnh trước: `viec/yen-lam-v09/anh/` nếu có, nếu không thì tự chụp staging.
0. `git -C D:\linhx\ifagent fetch --all`; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl13-kiosk-ux -b agy/yl13-kiosk-ux origin/agy/yl10-gop`. Nối node_modules như phiếu yl10.
Chạy mọi lệnh ở tiền cảnh. Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới, chụp ảnh, push, ghi CON_LAI.
VIỆC (giữ bộ màu, kính và logo sẵn có):
1. Nghe giữa hội trường ồn: khi khách nói, hiện NGAY chữ nhận được (tạm thời rồi chốt) ở khung lời, cỡ chữ đọc được từ 1,5 m. Có nút "Nói lại" và gợi ý "Hoặc bấm Nhắn Lam để gõ". Nếu không nhận được tiếng sau 6 giây thì báo nhẹ "Lam chưa nghe rõ, anh chị nói lại gần hơn nhé".
2. Thẻ "SẮP DIỄN RA": mỗi dòng ghi giờ + TÊN PHIÊN (cắt gọn 1 dòng) + phòng, tối đa 3 dòng, lấy từ agenda.json. Thẻ diễn giả ghi thêm giờ và phòng phiên của người đó.
3. Lời chào nhắc cả hai sự kiện: "Kính chào anh chị đến VSMCamp & CSMOSummit 2026". Thân lời dùng phông thân bài sẵn có, KHÔNG serif to.
4. Mã QR sang điện thoại: hiện QR nhỏ kèm chữ "Quét để hỏi tiếp trên điện thoại" ở góc khung lời sau mỗi câu trả lời của Lam và ở màn kết quả chụp bìa. Giữ nút Mã QR.
5. Mũi tên thu gọn không được đè lên chữ lời chào: đặt lại vị trí hoặc dời chữ xuống.
6. Biển báo camera: tạo trang in A5 dọc `/yen-lam/csmo/bien-camera` (HTML, in được) ghi "Khu vực có camera AI · Camera chỉ dùng để Lam nhận biết có người đứng trước kiosk và biểu cảm, không lưu hình ảnh" (sửa câu cho đúng thực tế code, kiểm xem camera ẩn có lưu ảnh hay không). Kèm một dòng nhỏ ở chân kiosk: "Kiosk có camera AI".
Ảnh trước/sau 1080×1920: màn chờ, đang nghe (có chữ tạm), đã trả lời (có QR), kết quả chụp bìa. Tự soi 100%, chấm ≥ 8.
Test Playwright 1 tệp yl13-kiosk-ux: thẻ sắp diễn ra có tên phiên; lời chào có "VSMCamp"; sau trả lời mock có QR; chữ tạm hiện khi giả lập sự kiện nhận giọng; mũi tên không giao với khung chữ.
Cuối: push `agy/yl13-kiosk-ux`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 16:15 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
