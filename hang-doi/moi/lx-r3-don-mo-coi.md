may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
theo_doi: D:\linhx\wt-lx-r3-don-mo-coi
phu_thuoc: lx-r2-nhip-may

Phiếu lx-r3-don-mo-coi (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
1. `git -c sendpack.sideband=false clone -b lx-r2-nhip-may git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r3-don-mo-coi` rồi `git -C D:\linhx\wt-lx-r3-don-mo-coi checkout -b lx-r3-don-mo-coi`.
2. Lỗi: phiếu nằm `dang/` từ 15/11 (vd lx-code-cat-tran, lx-ff-gop-bang) không ai dọn. Mồ côi = phiếu `dang/` mà (a) máy giữ nó có nhip mới nhưng `dang_chay` không chứa id đó, hoặc (b) dòng `nhan` cũ hơn 3 × tran_phut.
3. VIẾT TEST TRƯỚC, commit riêng, cho thấy ĐỎ: hàm `don_mo_coi(wt, bay_gio)` chuyển phiếu mồ côi sang `xong/<id>/KET-QUA.md` trạng thái `dung` lý do `mo_coi` (giữ nguyên SHA cuối nếu có trong phiếu), không đụng phiếu đang chạy thật; runner gọi nó tối đa 1 lần / 15 phút.
4. Vá cho test xanh, commit "feat(mo-coi): ...". Dùng `dang_chay` do lx-r2-nhip-may thêm.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r3-don-mo-coi -c sendpack.sideband=false push origin lx-r3-don-mo-coi`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r3-don-mo-coi; test mới đỏ→xanh; số test chạy.
