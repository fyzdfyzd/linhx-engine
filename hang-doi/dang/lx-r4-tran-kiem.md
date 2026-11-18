may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
theo_doi: D:\linhx\wt-lx-r4-tran-kiem
phu_thuoc: lx-thu-5p
nhan: may-3 2026-11-18T07:12:05+0700

Phiếu lx-r4-tran-kiem (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
1. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r4-tran-kiem` rồi `git -C D:\linhx\wt-lx-r4-tran-kiem checkout -b lx-r4-tran-kiem`.
2. Lỗi: agy tự chạy cả bộ test (nhiều khi chạy nền rồi ngồi chờ) nên ăn hết trần 40 phút. Lời dặn văn xuôi không đủ, phải chặn bằng code.
3. VIẾT TEST TRƯỚC, commit riêng, cho thấy ĐỎ: (a) header mới `tran_kiem_phut` (mặc định 5); runner chạy `lenh_kiem` SAU khi agy thoát, trần riêng `tran_kiem_phut`, KHÔNG tính vào `tran_phut`; quá trần kiểm thì KET-QUA `loi` lý do `qua_tran_kiem`; (b) `lenh_kiem` rỗng hoặc chạy toàn bộ (`pytest` không có đường dẫn tệp hoặc `-k`/`-m`) thì runner từ chối ngay lúc nhận phiếu, KET-QUA `loi` lý do `lenh_kiem_qua_rong`; (c) runner tự chèn vào đầu đề gửi agy một dòng cố định: "Không chạy bộ test đầy đủ; runner sẽ chạy lenh_kiem sau khi bạn thoát."
4. Vá linhx_runner.py / hang_doi_git.py cho test xanh, commit "feat(tran-kiem): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r4-tran-kiem -c sendpack.sideband=false push origin lx-r4-tran-kiem`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r4-tran-kiem; test mới đỏ→xanh; số test chạy.
