may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r3-don-mo-coi-l2; D:\linhx\nhat-ky\lx-r3-don-mo-coi-l2
phu_thuoc: lx-r2-nhip-may-l2

Phiếu lx-r3-don-mo-coi-l2 (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc, lượt 1 bị runner dừng sau 30 giây vì agy để lệnh clone chạy nền rồi ngồi chờ):
- Đầu tiên: `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r3-don-mo-coi-l2`.
- Mọi lệnh dài ghi log ra tệp và chạy tiền cảnh, ví dụ: `git clone ... > D:\linhx\nhat-ky\lx-r3-don-mo-coi-l2\clone.log 2>&1`. Test chỉ chạy 1 tệp mỗi lệnh: `python -m pytest runner/test_X.py -q > D:\linhx\nhat-ky\lx-r3-don-mo-coi-l2\t.log 2>&1`.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\lx-r3-don-mo-coi-l2\tien-do.log` sau mỗi bước.
1. `git -c sendpack.sideband=false clone -b lx-r2-nhip-may-l2 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r3-don-mo-coi-l2` rồi `git -C D:\linhx\wt-lx-r3-don-mo-coi-l2 checkout -b lx-r3-don-mo-coi-l2`.
2. Lỗi: phiếu nằm `dang/` từ 15/11 (vd lx-code-cat-tran, lx-ff-gop-bang) không ai dọn. Mồ côi = phiếu `dang/` mà (a) máy giữ nó có nhip mới nhưng `dang_chay` không chứa id đó, hoặc (b) dòng `nhan` cũ hơn 3 × tran_phut.
3. VIẾT TEST TRƯỚC, commit riêng, cho thấy ĐỎ: hàm `don_mo_coi(wt, bay_gio)` chuyển phiếu mồ côi sang `xong/<id>/KET-QUA.md` trạng thái `dung` lý do `mo_coi` (giữ nguyên SHA cuối nếu có trong phiếu), không đụng phiếu đang chạy thật; runner gọi nó tối đa 1 lần / 15 phút.
4. Vá cho test xanh, commit "feat(mo-coi): ...". Dùng `dang_chay` do lx-r2-nhip-may-l2 thêm.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r3-don-mo-coi-l2 -c sendpack.sideband=false push origin lx-r3-don-mo-coi-l2`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r3-don-mo-coi-l2; test mới đỏ→xanh; số test chạy.
