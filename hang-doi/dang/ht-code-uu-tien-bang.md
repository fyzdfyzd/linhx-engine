may: may-3
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-ht-uu-tien
nhan: may-3 2026-11-21T22:12:18+0700

Thêm ưu tiên theo bảng việc cho runner hàng đợi. CHỈ làm trên nhánh mới, KHÔNG push vào hang-doi, main hay nhánh runner đang chạy.
1. Clone https://github.com/fyzdfyzd/linhx-engine vào C:\linhx\wt-ht-uu-tien, tạo nhánh agy/ht-uu-tien-bang từ main.
2. Đọc runner/linhx_runner.py: tìm chỗ chọn phiếu tiếp theo trong hang-doi/moi/.
3. Thêm: đọc hang-doi/bang.json (mẫu ở nhánh hang-doi); phiếu có tiền tố tên trùng 'ma' của bảng thì xếp theo uu_tien tăng dần (0 trước, 1, 2...), cùng ưu tiên giữ thứ tự cũ; phiếu không thuộc bảng nào xếp sau cùng; file thiếu/hỏng thì giữ hành vi cũ. Không đổi gì khác.
4. Viết test pytest cho hàm sắp xếp (≥ 5 ca: bảng thiếu, json hỏng, cùng ưu tiên, không thuộc bảng, ưu tiên 0). Chạy tiền cảnh tới khi đạt cùng các test runner sẵn có.
5. Push nhánh agy/ht-uu-tien-bang. KHÔNG mở PR, không merge.
KET-QUA: tên hàm, file:dòng sửa, số test đạt, sha commit.
