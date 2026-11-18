may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r6-tha-chuoi-l3; D:\linhx\nhat-ky\lx-r6-tha-chuoi-l3
nhan: may-3 2026-11-18T15:30:49+0700
moc: 062e1f439d61fab27bd658a3d36bc6d4db58ed1e

Phiếu lx-r6-sua-1 (LAB131). Thư mục D:\linhx\wt-lx-r6-tha-chuoi-l3 ở nhánh lx-r6-tha-chuoi-l3, KHÔNG clone lại.
LUẬT CHỐNG CHUYỂN NỀN: mọi lệnh ghi log ra tệp trong thư mục nhật ký của phiếu, chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục tới khi xong, không kết thúc lượt; test chỉ chạy 1 tệp mỗi lệnh. CẤM chạy `pytest runner` toàn bộ, đụng GitHub, sửa D:\linhx\hang-doi.
Lỗi Claude soi: runner/tha_chuoi.py hàm _dam_bao_wt_hang_doi, khi repo người gọi đang ở nhánh hang-doi thì chạy `reset --hard` + `clean -fd` ngay trong repo đó → mất việc chưa commit.
1. Viết test trước (commit riêng): repo giả đang ở nhánh hang-doi có 1 tệp chưa commit → chạy tha_chuoi → tệp đó vẫn còn nguyên. Cho thấy ĐỎ.
2. Vá: luôn ghi phiếu qua worktree riêng (`_duong_dan_wt`), không bao giờ reset/clean repo người gọi. Test mới và runner/test_tha_chuoi.py XANH. Commit "fix(tha-chuoi): ...".
3. `git -C D:\linhx\wt-lx-r6-tha-chuoi-l3 -c sendpack.sideband=false push origin lx-r6-tha-chuoi-l3 > D:\linhx\nhat-ky\lx-r6-tha-chuoi-l3\push-s1.log 2>&1`.
KET-QUA: dòng đầu `dat: co|khong`; SHA; test đỏ→xanh.
