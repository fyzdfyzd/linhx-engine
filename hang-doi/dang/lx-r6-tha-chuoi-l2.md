may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r6-tha-chuoi-l2; D:\linhx\nhat-ky\lx-r6-tha-chuoi-l2
nhan: may-3 2026-11-18T08:05:00+0700

Phiếu lx-r6-tha-chuoi-l2 (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc, lượt 1 bị runner dừng sau 30 giây vì agy để lệnh clone chạy nền rồi ngồi chờ):
- Đầu tiên: `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r6-tha-chuoi-l2`.
- Mọi lệnh dài ghi log ra tệp và chạy tiền cảnh, ví dụ: `git clone ... > D:\linhx\nhat-ky\lx-r6-tha-chuoi-l2\clone.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh: `python -m pytest runner/test_X.py -q > D:\linhx\nhat-ky\lx-r6-tha-chuoi-l2\t.log 2>&1`.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r6-tha-chuoi-l2\tien-do.log` sau mỗi bước.
1. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r6-tha-chuoi-l2` rồi `git -C D:\linhx\wt-lx-r6-tha-chuoi-l2 checkout -b lx-r6-tha-chuoi-l2`.
2. Việc: luật "chạy phiếu thử trước mỗi chuỗi" hiện chỉ là lời dặn, Claude đã bỏ qua đêm 17/11. Viết `runner/tha_chuoi.py <thu-muc-phieu> --may <may>`: đọc mọi .md trong thư mục, tự sinh 1 phiếu ping (dùng `tao_phieu_ping`, tran_phut 5) làm gốc, chèn `phu_thuoc: <id ping>` vào mọi phiếu không có phu_thuoc, kiểm không có vòng phụ thuộc và mọi id phu_thuoc tồn tại, rồi mới ghi vào `hang-doi/moi/` + commit + push (pull --rebase tối đa 3 lần).
3. VIẾT TEST TRƯỚC (repo giả tmp_path, không mạng), commit riêng, cho thấy ĐỎ: chuỗi 3 phiếu → 4 tệp trong moi/, ping là gốc; vòng phụ thuộc hoặc id lạ → thoát mã 2, không ghi gì.
4. Viết cho test xanh, commit "feat(tha-chuoi): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r6-tha-chuoi-l2 -c sendpack.sideband=false push origin lx-r6-tha-chuoi-l2`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r6-tha-chuoi-l2; test mới đỏ→xanh; số test chạy.

nhip: 08:08 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
