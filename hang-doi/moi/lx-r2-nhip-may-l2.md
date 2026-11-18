may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r2-nhip-may-l2; D:\linhx\nhat-ky\lx-r2-nhip-may-l2
phu_thuoc: lx-r1-phu-thuoc-cho-l2

Phiếu lx-r2-nhip-may-l2 (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc, lượt 1 bị runner dừng sau 30 giây vì agy để lệnh clone chạy nền rồi ngồi chờ):
- Đầu tiên: `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r2-nhip-may-l2`.
- Mọi lệnh dài ghi log ra tệp và chạy tiền cảnh, ví dụ: `git clone ... > D:\linhx\nhat-ky\lx-r2-nhip-may-l2\clone.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh: `python -m pytest runner/test_X.py -q > D:\linhx\nhat-ky\lx-r2-nhip-may-l2\t.log 2>&1`.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r2-nhip-may-l2\tien-do.log` sau mỗi bước.
1. `git -c sendpack.sideband=false clone -b lx-r1-phu-thuoc-cho-l2 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r2-nhip-may-l2` rồi `git -C D:\linhx\wt-lx-r2-nhip-may-l2 checkout -b lx-r2-nhip-may-l2`.
2. Lỗi: máy 1 runner treo đêm 17/11, không ai biết. Dòng `nhip` hiện chỉ ghi trong phiếu khi agy đang chạy; máy rảnh hay vòng chính treo thì im.
3. VIẾT TEST TRƯỚC, commit riêng, cho thấy ĐỎ: (a) vòng chính runner ghi `nhip_luc` (ISO, giờ +07) và `dang_chay: [id...]` vào `hang-doi/may/<may>.json` mỗi 5 phút kể cả khi rảnh (dùng lại `cap_nhat_ho_so_may_git`, không push dày hơn 5 phút); (b) hàm `kiem_may_cam(wt, bay_gio, nguong_phut=30)` trả danh sách máy có nhip cũ hơn ngưỡng; (c) mỗi runner khi nhận phiếu gọi hàm này: máy câm thì ghi 1 tệp `hang-doi/can-linh/may-cam-<may>.md` (không ghi trùng) và trả mọi phiếu `dang/` mà máy đó đang giữ về `moi/` (bỏ dòng `nhan`, tăng `tu_sua` 0→1).
4. Vá cho test xanh, commit "feat(nhip-may): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r2-nhip-may-l2 -c sendpack.sideband=false push origin lx-r2-nhip-may-l2`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r2-nhip-may-l2; test mới đỏ→xanh; số test chạy.
