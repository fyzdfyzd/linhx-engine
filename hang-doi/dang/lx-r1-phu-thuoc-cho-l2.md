may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r1-phu-thuoc-cho-l2; D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l2
nhan: may-3 2026-11-18T08:03:51+0700

Phiếu lx-r1-phu-thuoc-cho-l2 (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc, lượt 1 bị runner dừng sau 30 giây vì agy để lệnh clone chạy nền rồi ngồi chờ):
- Đầu tiên: `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l2`.
- Mọi lệnh dài ghi log ra tệp và chạy tiền cảnh, ví dụ: `git clone ... > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l2\clone.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh: `python -m pytest runner/test_X.py -q > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l2\t.log 2>&1`.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l2\tien-do.log` sau mỗi bước.
1. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r1-phu-thuoc-cho-l2` rồi `git -C D:\linhx\wt-lx-r1-phu-thuoc-cho-l2 checkout -b lx-r1-phu-thuoc-cho-l2`.
2. Lỗi: `huy_phieu_phu_thuoc_truot_trong_wt` (runner/hang_doi_git.py) huỷ dây chuyền mọi phiếu con khi một phiếu trượt, kể cả khi phiếu trượt đã push gần đủ việc (đêm 17/11 mất cả chuỗi 12 phiếu).
3. VIẾT TEST TRƯỚC, commit riêng "test(phu-thuoc-cho): ...", chạy cho thấy ĐỎ: (a) phiếu cha trượt → phiếu con ở lại `moi/`, có thêm dòng header `bi_chan: <id cha> <ly do>`, KHÔNG sinh KET-QUA huy; (b) phiếu con có `bi_chan` không được nhận; (c) khi cha (hoặc lượt `-sua-k` của cha) đạt `xong` thì runner xoá dòng `bi_chan` và con chạy được; (d) phiếu cha trượt hẳn sinh đúng 1 phiếu `hang-doi/can-linh/<id cha>-phan-loai.md` liệt kê các con bị chặn, SHA cuối cha đã push (nếu có) và 3 lựa chọn: sua / chia / huy.
4. Vá hang_doi_git.py cho test xanh. Giữ đường huỷ tay: lệnh/hàm `huy_chuoi(id)` chỉ chạy khi gọi rõ. Commit "fix(phu-thuoc-cho): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r1-phu-thuoc-cho-l2 -c sendpack.sideband=false push origin lx-r1-phu-thuoc-cho-l2`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r1-phu-thuoc-cho-l2; test mới đỏ→xanh; số test chạy.

nhip: 08:06 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
