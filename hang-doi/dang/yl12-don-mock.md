may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 20
theo_doi: D:\linhx\nhat-ky\yl12-don-mock; D:\linhx\ifagent-wt\yl12-don-mock
nhan: may-3 2026-11-18T15:01:15+0700

Phiếu `yl12-don-mock`: DỌN DỮ LIỆU GIẢ trước production. ĐỌC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
0. worktree `D:\linhx\ifagent-wt\yl12-don-mock` -b agy/yl12-don-mock từ origin/agy/yl10-gop.
1. Tìm mọi nguồn dữ liệu mẫu hiện lên giao diện: thông báo "MOCK-…", ảnh mẫu lặp lại trên Bảng tin (seed-staging.js, tep mẫu, bia mẫu), câu hỏi/bình luận [TEST], khách giả. Liệt kê vào KET-QUA.
2. Bảo đảm: production KHÔNG bao giờ nạp seed (chỉ khi biến môi trường staging/thu bật), có test chứng minh. Bảng tin rỗng thì hiện trạng thái rỗng đẹp ("Chưa có ảnh, hãy là người đầu tiên") thay vì ô trống.
3. Không xoá dữ liệu trên VM. Chỉ sửa code nạp/hiển thị. Ảnh 390×844 bảng tin rỗng.
Push agy/yl12-don-mock. KHÔNG deploy.

nhip: 15:28 27p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
