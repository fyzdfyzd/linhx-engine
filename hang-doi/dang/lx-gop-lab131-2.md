may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-gop-lab131; D:\linhx\nhat-ky\lx-gop-lab131
phu_thuoc: lx-gop-lab131-1
nhan: may-3 2026-11-18T18:42:08+0700
moc: 363802129d55151d01b1bc0fc2528375905cb06e

Phiếu lx-gop-lab131-2 (LAB131). Thư mục D:\linhx\wt-lx-gop-lab131 ở nhánh lx-gop-lab131 đã gộp r5, r6, r1. KHÔNG clone lại. Gộp tiếp 2 nhánh, cùng cách như phiếu lx-gop-lab131-1:
LUẬT CHỐNG CHUYỂN NỀN: mọi lệnh ghi log ra `D:\linhx\nhat-ky\lx-gop-lab131\<ten>.log`, chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục tới khi xong, không kết thúc lượt; test chỉ chạy 1 tệp mỗi lệnh. CẤM chạy `pytest runner` toàn bộ, đụng GitHub, deploy, sửa D:\linhx\hang-doi, sửa logic ngoài phần giải xung đột.
   d. D:\linhx\wt-lx-r4-tran-kiem-l4 nhánh lx-r4-tran-kiem-l4 → test_tran_kiem.py, test_hang_doi_git.py, test_phu_thuoc_cho.py
   e. D:\linhx\wt-lx-r0-tu-clone nhánh lx-r0-tu-clone → test_tu_clone.py, test_hang_doi_git.py, test_phu_thuoc_cho.py, test_tran_kiem.py, test_bi_mat_goc.py
Cuối cùng chạy thêm từng tệp: test_chan_cho_nen.py, test_tu_cham_khoa.py, test_tha_chuoi.py, test_va5_cham_va_ngat_mach.py.
Xuất soi: `git -C D:\linhx\wt-lx-gop-lab131 show --cc <mọi SHA merge của lx-gop-lab131> > D:\linhx\nhat-ky\lx-gop-lab131\merges.patch`, chép vào bao-cao/lab131/gop/ trên nhánh hang-doi y như phiếu lx-patch-lab131 (clone hang-doi riêng, push trạm, KHÔNG GitHub).
`git -C D:\linhx\wt-lx-gop-lab131 -c sendpack.sideband=false push origin lx-gop-lab131 > D:\linhx\nhat-ky\lx-gop-lab131\push-2.log 2>&1`.
KET-QUA: dòng đầu `dat: co|khong`; SHA đỉnh lx-gop-lab131; xung đột; số test từng tệp.

nhip: 18:48 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
