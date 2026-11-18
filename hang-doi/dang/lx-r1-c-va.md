may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r1-phu-thuoc-cho-l4; D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4
phu_thuoc: lx-r1-b-test
nhan: may-3 2026-11-18T13:51:39+0700
moc: 97e9d12ade34dfecf55c7112e9fec3c7ab52cac4

Phiếu lx-r1-c-va (LAB131). Thư mục D:\linhx\wt-lx-r1-phu-thuoc-cho-l4 ở nhánh lx-r1-phu-thuoc-cho-l4 đã có commit test đỏ, KHÔNG clone lại, KHÔNG sửa tệp test.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc; lượt trước agy để lệnh chạy nền rồi ngồi chờ nên runner dừng):
- Mọi lệnh ghi log ra tệp, chạy tiền cảnh: `<lệnh> > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\<ten>.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\tien-do.log` sau mỗi bước.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá, chạy `pytest runner` toàn bộ.
1. Vá runner/hang_doi_git.py: thay huỷ dây chuyền bằng đánh dấu `bi_chan` như test. Giữ đường huỷ tay `huy_chuoi(id)` chỉ chạy khi gọi rõ.
2. Chạy tệp test mới: phải XANH. Chạy thêm tệp test cũ của module đã sửa (từng tệp một), không đỏ thêm. Commit "fix(r1): ...".
3. `git -C D:\linhx\wt-lx-r1-phu-thuoc-cho-l4 -c sendpack.sideband=false push origin lx-r1-phu-thuoc-cho-l4:refs/heads/agy/lx-r1-phu-thuoc-cho-l4 > D:\linhx\nhat-ky\lx-r1-phu-thuoc-cho-l4\push-c.log 2>&1` (tên agy/* để trạm đồng bộ lên GitHub).
KET-QUA: dòng đầu `dat: co|khong`; SHA đỉnh; test đỏ→xanh; số test cũ đã chạy.

nhip: 13:57 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
