may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-nhip
khong_tien_phut: 25
tu_sua: 1

LƯU Ý: lần trước dừng vì agy chạy tác vụ nền (subagent/background) rồi ngồi chờ, thư mục không đổi 10 phút. KHÔNG dùng background task hay subagent nền; tự làm tuần tự. Có thể đã làm dở trong C:\linhx\wt-nhip: kiểm git status rồi làm tiếp.

KHÔNG chạy lệnh nền (background): mọi lệnh chạy tiền cảnh và chờ xong.

Bảng web và runner phải trả lời 4 câu cho Linh: mỗi máy đang làm gì, kẹt ở đâu, cần Linh thao tác gì trên máy, hỗ trợ gì.
Repo: `C:\linhx\wt-nhip` (clone nhánh claude/project-thread-jowxv1 nếu chưa có, có rồi `git pull`). KHÔNG sửa C:\linhx\hang-doi.
1. Nhịp: trong lúc agy chạy, cứ 3 phút runner ghi 1 dòng `nhip: <giờ> <phút đã chạy> <dòng stdout/stderr cuối của agy ≤120 ký tự>` vào cuối `hang-doi/dang/<id>.md` (chỉ giữ 1 dòng nhip), push nhánh hang-doi (pull --rebase, thử 3 lần, lỗi bỏ qua).
2. Cần Linh: runner thêm vào đề gửi agy câu: "Nếu gặp việc chỉ người làm được (đăng nhập, quyền Admin/UAC, captcha, cài phần mềm, duyệt), DỪNG việc đó và ghi khối `CAN-LINH: <việc>; LENH: <lệnh dán được nếu có>` trong câu trả lời." Runner thấy khối này thì ghi `hang-doi/can-linh/<id>.md` (máy, phiếu, việc, lệnh, giờ) và push.
3. Bảng `runner/bang/bang.py`: trên cùng là khối đỏ "Cần anh làm" (từ `can-linh/`, ẩn khi rỗng); dưới là mỗi máy 1 dòng: đang làm gì (phiếu + phút + dòng nhip), trạng thái (chạy / rảnh / kẹt: dừng-lỗi gần nhất kèm lý do / im lặng > 30 phút đỏ). Tối giản, đọc trong 5 giây trên điện thoại. `/api/trang-thai` thêm `can_linh`, `may[].nhip`.
3b. Hồ sơ máy: runner ghi `hang-doi/may/<ma-may>.json` lúc khởi động và mỗi 60 phút (chỉ push khi đổi): mã + tên Windows, vai trò (biến `LINHX_VAI` trong tho.env, ví dụ "Máy chính: code, điều phối"), CPU (tên, nhân/luồng), RAM tổng/trống, GPU (tên, VRAM nếu đọc được), ổ đĩa tổng/trống, agy (đường dẫn, phiên bản), Python, Chrome (có/không, tên các profile), cấu hình nhận phiếu (so_phieu, nhận bat-ky hay chỉ đích danh), số phiếu xong/lỗi 24 giờ qua. Bảng web thêm trang/tab "Máy": mỗi máy 1 thẻ hồ sơ + năng lực, thanh RAM/ổ đĩa; ổ C dưới 10 GB thì cảnh báo. Không ghi mật khẩu, token, email.
4. Test trong runner/ (không conftest, không mạng, chạy tiền cảnh); `python -m pytest runner -q` đạt hết trừ test đường dẫn chỉ Windows.
5. Cập nhật `skills/le/hang-doi-may/SKILL.md` mục Phiếu và Bài học (2-3 dòng).
`git pull --rebase`, push. Trả lời: số test, hash.
