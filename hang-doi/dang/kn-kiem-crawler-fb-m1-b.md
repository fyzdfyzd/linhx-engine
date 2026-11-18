may: may-1
loai: khac
tran_phut: 20
khong_tien_phut: 15
tu_sua: 0
phu_thuoc: kn-kiem-crawler-web-m1-b
nhan: may-1 2026-11-18T11:50:48+0700

# kn-kiem-crawler-fb-m1-b
Lượt 2: lượt 1 kẹt không chạy. Không chạy tác vụ nền (luật 12).
Đọc và làm theo luật chung `viec/kn-thu/DE-BAI.md` (bắt buộc).

Kỹ năng: LINHX Crawler quét Facebook profile/trang công khai.
Dùng chức năng Facebook có sẵn của crawler (đọc code/README D:\LINHX_CRAWLER tìm endpoint, cookie crawler tự giữ, KHÔNG in cookie). Quét trang công khai https://www.facebook.com/VnExpress (≤ 10 bài mới nhất).
Lưu JSON (bài: thời gian, 200 ký tự đầu, link) vào xong/<id>/fb.json.
ĐẠT khi: ≥ 5 bài có nội dung + thời gian. Hỏng do checkpoint/đăng nhập → `CHUA_DANG_NHAP` + CAN-LINH ghi tài khoản FB crawler cần.
Trả: endpoint, số bài, thời gian, lỗi nếu có.

nhip: 11:52 2p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-18T11:52:42+0700] · root agent idle; waiting up to 40m0s for 1 ba
