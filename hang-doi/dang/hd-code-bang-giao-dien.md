may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-giao-dien
khong_tien_phut: 25
tu_sua: 1
phu_thuoc: nhip-can-linh-b
nhan: may-2 2026-11-15T10:21:38+0700

KHÔNG chạy lệnh nền hay subagent nền: mọi lệnh tiền cảnh, làm tuần tự.
Repo: `C:\linhx\wt-giao-dien` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-giao-dien`; có rồi: `git pull`). KHÔNG sửa C:\linhx\hang-doi. Đọc trước `viec/ra-quy-trinh/SO-SANH.md` (khâu liên quan).

Làm lại giao diện bảng theo dõi `runner/bang/` cho đẹp, hiện đại, tối giản chuẩn Apple (Linh xem trên điện thoại, đọc trong 5 giây). Giữ nguyên dữ liệu và API, chỉ đổi giao diện; Python stdlib, CSS/JS nhúng, không CDN.
- Trên cùng: một câu trạng thái lớn ("3 máy chạy, 1 cần anh") + khối "Cần anh làm" đỏ (ẩn khi rỗng), mỗi việc có nút chép lệnh.
- Thẻ máy: tên + vai trò, chấm trạng thái (xanh chạy, xám rảnh, cam kẹt, đỏ im lặng), phiếu đang làm + thanh phút/trần + dòng nhịp cuối; bấm mở chi tiết.
- Tab: Tổng quan · Phiếu (đang/chờ/xong 24h, lọc theo máy) · Máy (hồ sơ năng lực, thanh RAM/ổ).
- Phông hệ thống (-apple-system, Segoe UI, Inter), nhiều khoảng trắng, một màu nhấn, bo góc 16, bóng nhẹ, tự sáng/tối theo máy, chữ ≥ 15px trên điện thoại, không tràn ngang ở 390px.
- Tự làm mới 15 giây bằng fetch /api/trang-thai, không nhấp nháy cả trang.
Bằng chứng: chụp 390×844 và 1440×900, cả sáng và tối, lưu `viec/bang-giao-dien/anh/` (commit, mỗi ảnh < 500 KB). Test cũ của bang vẫn đạt; thêm test trang trả 200 và có các khối chính.
`python -m pytest runner -q` đạt hết trừ test đường dẫn chỉ Windows. Cài lại bảng trên máy 2 (cai-bang.ps1 hoặc khởi động lại tác vụ LINHX-Bang). `git pull --rebase`, push. Trả lời: số test, hash, đường dẫn ảnh.
