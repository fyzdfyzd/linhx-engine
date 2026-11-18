may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl11-tri-thuc; C:\linhx\ifagent-wt\yl11-tri-thuc
nhan: may-2 2026-11-18T13:00:49+0700

Phiếu Yên Lam `yl11-tri-thuc`: NẠP DỮ LIỆU BTC 18/11 làm tri thức cho Yên Lam (kiosk + đồng hành). ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` (luật chung, chống chuyển nền, cấm).
Chạy mọi lệnh tiền cảnh. Ghi tiến độ `C:\linhx\nhat-ky\yl11-tri-thuc\tien-do.log`. Mỗi bước xong COMMIT + PUSH. Phút 30 dừng việc mới, push, ghi CON_LAI.
0. `git -C C:\linhx\ifagent fetch --all`; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl11-tri-thuc -b agy/yl11-tri-thuc origin/agy/yl10-gop`. Nối node_modules như phiếu yl10.
1. Nguồn: thư mục Google Drive trên máy này `G:\My Drive\02_Công Việc Chung (Work & Projects)\04_DuAn_TheoNam\2026\[1021]IFAGENT_LEBROS\DATA 18_11` (Linh gửi 12:59). Liệt kê mọi tệp (tên, loại, cỡ) vào KET-QUA. Không thấy thư mục thì tìm gần đúng dưới `G:\My Drive\02_Công Việc Chung*\04_DuAn_TheoNam\2026\` (tên có dấu, khoảng trắng); vẫn không thấy thì dừng, ghi CAN-LINH.
2. Chuyển nội dung chữ sang Markdown UTF-8 không BOM (docx/pdf/xlsx/csv/md/txt; Google Docs dạng .gdoc thì mở bằng trình duyệt đã đăng nhập hoặc ghi THIEU). Lưu vào `apps/lab/demos/yen-lam/tri-thuc/nguon/data-18-11/`. Ảnh: KHÔNG commit ảnh có mặt người; ảnh khác chỉ ghi tên vào danh sách.
3. Nối vào nguồn tri thức chung đang dùng cho Lam (bản `docNguonTriThucChung` trong `apps/lab/server/v1/may-chu.js` và chỗ nạp tri thức kiosk/FAQ, xem nhánh yl10-trang-test). Dữ liệu 18/11 MỚI HƠN thì ưu tiên khi trùng (giờ, phòng, diễn giả, chương trình). Nếu có lịch/diễn giả mới khác `agenda/chuan/agenda.json`, `dien-gia.json` thì cập nhật hai tệp đó (giữ định dạng, chạy lại test khoá liên quan từng tệp) và ghi rõ thay đổi trong KET-QUA.
4. NÉN VỪA PHẢI: phần đưa vào prompt ≤ 12.000 ký tự (giờ, phòng, track, diễn giả, địa điểm, vé, check-in, tài trợ); phần còn lại tra cứu khi cần. Không bịa ngoài dữ liệu.
5. Test mới (mock Gemini): 8 câu hỏi lấy từ dữ liệu 18/11 → ngữ cảnh gửi đi chứa đúng dữ kiện; kiosk và đồng hành đọc cùng nguồn; bản nén ≤ 12.000 ký tự.
Cuối: push `agy/yl11-tri-thuc`. KHÔNG deploy. KET-QUA: dat, SHA, danh sách tệp đã nạp/THIEU, thay đổi agenda/diễn giả, test.

nhip: 13:18 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
