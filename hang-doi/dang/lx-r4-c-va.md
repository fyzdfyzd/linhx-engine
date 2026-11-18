may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r4-tran-kiem-l4; D:\linhx\nhat-ky\lx-r4-tran-kiem-l4
phu_thuoc: lx-r4-b-test
nhan: may-3 2026-11-18T13:51:06+0700
moc: 99cc35716fa08a4ba33fb78de0d9e094cafe1975

Phiếu lx-r4-c-va (LAB131). Thư mục D:\linhx\wt-lx-r4-tran-kiem-l4 ở nhánh lx-r4-tran-kiem-l4 đã có commit test đỏ, KHÔNG clone lại, KHÔNG sửa tệp test.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc; lượt trước agy để lệnh chạy nền rồi ngồi chờ nên runner dừng):
- Mọi lệnh ghi log ra tệp, chạy tiền cảnh: `<lệnh> > D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\<ten>.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\tien-do.log` sau mỗi bước.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá, chạy `pytest runner` toàn bộ.
1. Vá runner/linhx_runner.py và/hoặc runner/hang_doi_git.py cho test xanh, không đổi hành vi phiếu không có `lenh_kiem`.
2. Chạy tệp test mới: phải XANH. Chạy thêm tệp test cũ của module đã sửa (từng tệp một), không đỏ thêm. Commit "fix(r4): ...".
3. `git -C D:\linhx\wt-lx-r4-tran-kiem-l4 -c sendpack.sideband=false push origin lx-r4-tran-kiem-l4:refs/heads/agy/lx-r4-tran-kiem-l4 > D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\push-c.log 2>&1` (tên agy/* để trạm đồng bộ lên GitHub).
KET-QUA: dòng đầu `dat: co|khong`; SHA đỉnh; test đỏ→xanh; số test cũ đã chạy.

nhip: 13:54 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
