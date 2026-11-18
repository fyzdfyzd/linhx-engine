may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
theo_doi: D:\linhx\wt-lx-r2-nhip-may
phu_thuoc: lx-r1-phu-thuoc-cho

Phiếu lx-r2-nhip-may (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
1. `git -c sendpack.sideband=false clone -b lx-r1-phu-thuoc-cho git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r2-nhip-may` rồi `git -C D:\linhx\wt-lx-r2-nhip-may checkout -b lx-r2-nhip-may`.
2. Lỗi: máy 1 runner treo đêm 17/11, không ai biết. Dòng `nhip` hiện chỉ ghi trong phiếu khi agy đang chạy; máy rảnh hay vòng chính treo thì im.
3. VIẾT TEST TRƯỚC, commit riêng, cho thấy ĐỎ: (a) vòng chính runner ghi `nhip_luc` (ISO, giờ +07) và `dang_chay: [id...]` vào `hang-doi/may/<may>.json` mỗi 5 phút kể cả khi rảnh (dùng lại `cap_nhat_ho_so_may_git`, không push dày hơn 5 phút); (b) hàm `kiem_may_cam(wt, bay_gio, nguong_phut=30)` trả danh sách máy có nhip cũ hơn ngưỡng; (c) mỗi runner khi nhận phiếu gọi hàm này: máy câm thì ghi 1 tệp `hang-doi/can-linh/may-cam-<may>.md` (không ghi trùng) và trả mọi phiếu `dang/` mà máy đó đang giữ về `moi/` (bỏ dòng `nhan`, tăng `tu_sua` 0→1).
4. Vá cho test xanh, commit "feat(nhip-may): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r2-nhip-may -c sendpack.sideband=false push origin lx-r2-nhip-may`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r2-nhip-may; test mới đỏ→xanh; số test chạy.
