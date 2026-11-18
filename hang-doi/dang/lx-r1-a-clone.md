may: may-3
loai: code
tran_phut: 10
theo_doi: D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4
nhan: may-3 2026-11-18T13:33:17+0700

Phiếu lx-r1-a-clone (LAB131, chỉ chuẩn bị thư mục, không sửa code).
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc; lượt trước agy để lệnh chạy nền rồi ngồi chờ nên runner dừng):
- Mọi lệnh ghi log ra tệp, chạy tiền cảnh: `<lệnh> > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\<ten>.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\tien-do.log` sau mỗi bước.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá, chạy `pytest runner` toàn bộ.
1. `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4`.
2. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r1-phu-thuoc-cho-l4 > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\clone.log 2>&1` (có rồi thì xoá thư mục trước).
3. `git -C D:\linhx\wt-lx-r1-phu-thuoc-cho-l4 checkout -b lx-r1-phu-thuoc-cho-l4`.
KET-QUA: dòng đầu `dat: co|khong`; SHA HEAD.
