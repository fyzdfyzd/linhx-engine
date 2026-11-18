may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r4-tran-kiem-l4; D:\linhx\nhat-ky\lx-r4-tran-kiem-l4
phu_thuoc: lx-r4-a-clone
nhan: may-3 2026-11-18T13:35:54+0700
moc: 546e9e3f7d6013c8a1d1fb56dc64fe649202fff2

Phiếu lx-r4-b-test (LAB131). Thư mục D:\linhx\wt-lx-r4-tran-kiem-l4 đã clone sẵn ở nhánh lx-r4-tran-kiem-l4, KHÔNG clone lại. CHỈ VIẾT TEST, chưa vá code.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc; lượt trước agy để lệnh chạy nền rồi ngồi chờ nên runner dừng):
- Mọi lệnh ghi log ra tệp, chạy tiền cảnh: `<lệnh> > D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\<ten>.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\tien-do.log` sau mỗi bước.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá, chạy `pytest runner` toàn bộ.
1. Viết `runner/test_tran_kiem.py`: (a) header mới `tran_kiem_phut` (mặc định 5); runner chạy `lenh_kiem` SAU khi agy thoát, trần riêng, KHÔNG tính vào `tran_phut`; quá trần kiểm → KET-QUA `loi` lý do `qua_tran_kiem`; (b) `lenh_kiem` chạy toàn bộ (`pytest` không có đường dẫn tệp và không có `-k`/`-m`) → từ chối lúc nhận phiếu, `loi` lý do `lenh_kiem_qua_rong`; `lenh_kiem` rỗng vẫn được (giữ hành vi cũ); (c) đề gửi agy có thêm dòng cố định "Không chạy bộ test đầy đủ; runner sẽ chạy lenh_kiem sau khi bạn thoát." khi phiếu có `lenh_kiem`.
2. Chạy đúng tệp test mới, cho thấy ĐỎ (ghi số failed). Commit "test(r4): ...".
3. `git -C D:\linhx\wt-lx-r4-tran-kiem-l4 -c sendpack.sideband=false push origin lx-r4-tran-kiem-l4 > D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\push-b.log 2>&1`.
KET-QUA: dòng đầu `dat: co|khong`; SHA; số test đỏ.

nhip: 13:47 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
