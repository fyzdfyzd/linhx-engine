may: may-2
loai: code
tran_phut: 30

Sửa runner trong repo `C:\linhx\wt-lvn` (nhánh `claude/project-thread-jowxv1`, `git pull` trước). KHÔNG sửa C:\linhx\hang-doi (runner đang chạy).
Thêm công tắc `LINHX_NHAN_BAT_KY` (mặc định 1). Đặt 0 thì máy CHỈ nhận phiếu có `may:` đúng tên máy, bỏ qua phiếu `bat-ky`.
- runner/hang_doi_git.py: chỗ chọn phiếu (tìm "bat-ky").
- runner/cai-may.ps1 thêm cờ `-ChiDichDanh`, runner/cai_may.py tham số tương ứng: ghi `LINHX_NHAN_BAT_KY=0` vào tho.env.
- Test mới trong runner/ (không dùng conftest.py).
- Chạy `python -m pytest runner -q` Ở TIỀN CẢNH (không chạy nền, không chờ tác vụ nền), tất cả đạt.
- Chỉ đụng runner/. Commit một lần, push.
Trả lời: số test đạt, hash commit.
